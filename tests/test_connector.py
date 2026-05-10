import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from tts_plugin_edgetts.connector import EdgeTTSConnector
from tts_plugin_bridge.protocol import TTSRequest


@pytest.mark.asyncio
async def test_engine_name():
    connector = EdgeTTSConnector()
    assert connector.ENGINE_NAME == "edgetts"
    assert connector.name == "edgetts"


@pytest.mark.asyncio
async def test_supported_params():
    connector = EdgeTTSConnector()
    params = connector.get_supported_params()
    assert "voice" in params
    assert "rate" in params
    assert "pitch" in params
    assert "proxy" in params


@pytest.mark.asyncio
async def test_is_available_true():
    connector = EdgeTTSConnector()
    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_etts.list_voices = AsyncMock(
            return_value=[{"ShortName": "ja-JP-NanamiNeural"}]
        )
        result = await connector.is_available()
        assert result is True


@pytest.mark.asyncio
async def test_is_available_false():
    connector = EdgeTTSConnector()
    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_etts.list_voices = AsyncMock(side_effect=Exception("network error"))
        result = await connector.is_available()
        assert result is False


@pytest.mark.asyncio
async def test_synthesize_basic():
    connector = EdgeTTSConnector()
    req = TTSRequest(text="こんにちは")

    async def fake_stream():
        yield {"type": "audio", "data": b"\xff\xfb\x90\x00"}
        yield {
            "type": "SentenceBoundary",
            "offset": 0,
            "duration": 1000000,
            "text": "こんにちは",
        }

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        res = await connector.synthesize(req)
        assert res.success is True
        assert res.audio_data == b"\xff\xfb\x90\x00"
        assert res.metadata.get("format") == "mp3"


@pytest.mark.asyncio
async def test_speed_to_rate_conversion():
    connector = EdgeTTSConnector()
    req = TTSRequest(text="hello", speed=1.5)

    async def fake_stream():
        yield {"type": "audio", "data": b"audio"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        await connector.synthesize(req)
        mock_etts.Communicate.assert_called_once()
        call_kwargs = mock_etts.Communicate.call_args
        assert call_kwargs[1]["rate"] == "+50%"


@pytest.mark.asyncio
async def test_speed_to_rate_slow():
    connector = EdgeTTSConnector()
    req = TTSRequest(text="hello", speed=0.5)

    async def fake_stream():
        yield {"type": "audio", "data": b"audio"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        await connector.synthesize(req)
        call_kwargs = mock_etts.Communicate.call_args
        assert call_kwargs[1]["rate"] == "-50%"


@pytest.mark.asyncio
async def test_volume_to_percent():
    connector = EdgeTTSConnector()
    req = TTSRequest(text="hello", volume=2.0)

    async def fake_stream():
        yield {"type": "audio", "data": b"audio"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        await connector.synthesize(req)
        call_kwargs = mock_etts.Communicate.call_args
        assert call_kwargs[1]["volume"] == "+100%"


@pytest.mark.asyncio
async def test_model_as_voice():
    connector = EdgeTTSConnector()
    req = TTSRequest(text="hello", model="en-US-EmmaMultilingualNeural")

    async def fake_stream():
        yield {"type": "audio", "data": b"audio"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        await connector.synthesize(req)
        call_kwargs = mock_etts.Communicate.call_args
        assert call_kwargs[1]["voice"] == "en-US-EmmaMultilingualNeural"


@pytest.mark.asyncio
async def test_extra_params_override():
    connector = EdgeTTSConnector()
    req = TTSRequest(
        text="hello",
        speed=1.0,
        extra={"rate": "+100%", "pitch": "+10Hz", "proxy": "http://proxy:8080"},
    )

    async def fake_stream():
        yield {"type": "audio", "data": b"audio"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        await connector.synthesize(req)
        call_kwargs = mock_etts.Communicate.call_args
        assert call_kwargs[1]["rate"] == "+100%"
        assert call_kwargs[1]["pitch"] == "+10Hz"
        assert call_kwargs[1]["proxy"] == "http://proxy:8080"


@pytest.mark.asyncio
async def test_synthesize_error():
    connector = EdgeTTSConnector()
    req = TTSRequest(text="hello")

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(side_effect=Exception("TTS service error"))
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        res = await connector.synthesize(req)
        assert res.success is False
        assert "TTS service error" in res.error


@pytest.mark.asyncio
async def test_context_manager():
    async with EdgeTTSConnector() as connector:
        assert connector.ENGINE_NAME == "edgetts"


@pytest.mark.asyncio
async def test_default_voice():
    connector = EdgeTTSConnector()
    assert connector.voice == "ja-JP-NanamiNeural"


@pytest.mark.asyncio
async def test_custom_voice_constructor():
    connector = EdgeTTSConnector(voice="en-US-EmmaMultilingualNeural")
    assert connector.voice == "en-US-EmmaMultilingualNeural"


@pytest.mark.asyncio
async def test_synthesize_stream_yields_audio_chunks():
    connector = EdgeTTSConnector()
    req = TTSRequest(text="hello")

    async def fake_stream():
        yield {"type": "audio", "data": b"chunk1"}
        yield {
            "type": "SentenceBoundary",
            "offset": 0,
            "duration": 100,
            "text": "hello",
        }
        yield {"type": "audio", "data": b"chunk2"}
        yield {"type": "audio", "data": b"chunk3"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        chunks = []
        async for chunk in connector.synthesize_stream(req):
            chunks.append(chunk)

    assert chunks == [b"chunk1", b"chunk2", b"chunk3"]


@pytest.mark.asyncio
async def test_synthesize_stream_uses_same_params():
    connector = EdgeTTSConnector()
    req = TTSRequest(
        text="hello", speed=1.5, volume=1.2, model="en-US-EmmaMultilingualNeural"
    )

    async def fake_stream():
        yield {"type": "audio", "data": b"audio"}

    with patch("tts_plugin_edgetts.connector.edge_tts") as mock_etts:
        mock_comm = MagicMock()
        mock_comm.stream = MagicMock(return_value=fake_stream())
        mock_etts.Communicate = MagicMock(return_value=mock_comm)

        chunks = []
        async for chunk in connector.synthesize_stream(req):
            chunks.append(chunk)

        call_kwargs = mock_etts.Communicate.call_args
        assert call_kwargs[1]["voice"] == "en-US-EmmaMultilingualNeural"
        assert call_kwargs[1]["rate"] == "+50%"
        assert call_kwargs[1]["volume"] == "+20%"
