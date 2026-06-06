import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from tts_plugin_bridge import ConnectorFactory
from vox4ai_skill_lib import TTSSkill
from tts_plugin_edgetts.connector import EdgeTTSConnector


@pytest.fixture(autouse=True)
def register_edgetts():
    ConnectorFactory._discovered = True
    ConnectorFactory._registry["edgetts"] = EdgeTTSConnector
    yield
    ConnectorFactory._registry.pop("edgetts", None)


@pytest.mark.asyncio
async def test_factory_discovers_edgetts():
    engines = ConnectorFactory.list_available()
    assert "edgetts" in engines


@pytest.mark.asyncio
async def test_factory_creates_edgetts():
    connector = ConnectorFactory.create("edgetts")
    assert isinstance(connector, EdgeTTSConnector)
    assert connector.name == "edgetts"


@pytest.mark.asyncio
async def test_skill_synthesize_with_edgetts():
    async def fake_stream():
        yield {"type": "audio", "data": b"\xff\xfb\x90\x00mp3data"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_etts.list_voices = AsyncMock(
            return_value=[{"ShortName": "ja-JP-NanamiNeural"}]
        )
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        async with TTSSkill(default_engine="edgetts") as skill:
            result = await skill.synthesize(text="こんにちは、世界")

    assert result.status == "ok"
    assert result.engine == "edgetts"
    assert result.audio_base64 is not None


@pytest.mark.asyncio
async def test_skill_synthesize_with_voice_param():
    async def fake_stream():
        yield {"type": "audio", "data": b"audio"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_etts.list_voices = AsyncMock(
            return_value=[{"ShortName": "ja-JP-NanamiNeural"}]
        )
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        async with TTSSkill(default_engine="edgetts") as skill:
            result = await skill.synthesize(
                text="Hello",
                speed=1.5,
                volume=1.2,
            )

    assert result.status == "ok"
    call_kwargs = mock_etts.Communicate.call_args
    assert call_kwargs[1]["rate"] == "+50%"
    assert call_kwargs[1]["volume"] == "+20%"


@pytest.mark.asyncio
async def test_skill_unavailable_edgetts():
    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_etts.list_voices = AsyncMock(side_effect=Exception("network error"))

        async with TTSSkill(default_engine="edgetts") as skill:
            result = await skill.synthesize(text="test")

    assert result.status == "error"
    assert "not reachable" in result.message


@pytest.mark.asyncio
async def test_connector_entry_point():
    import importlib.metadata

    eps = importlib.metadata.entry_points(group="tts_bridge.connectors")
    edgetts_eps = [ep for ep in eps if ep.name == "edgetts"]
    assert len(edgetts_eps) > 0, (
        "edgetts entry point not found in tts_bridge.connectors"
    )

    cls = edgetts_eps[0].load()
    assert issubclass(cls, EdgeTTSConnector)
