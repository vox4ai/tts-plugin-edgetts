from typing import AsyncGenerator, Optional

import edge_tts
from tts_plugin_bridge.protocol import TTSConnector, TTSRequest, TTSResponse


class EdgeTTSConnector(TTSConnector):
    ENGINE_NAME = "edgetts"
    SUPPORTED_PARAMS = ["voice", "rate", "pitch", "proxy"]

    def __init__(
        self,
        voice: str = "ja-JP-NanamiNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        proxy: Optional[str] = None,
    ):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.proxy = proxy

    @staticmethod
    def _speed_to_rate(speed: float) -> str:
        percent = round((speed - 1.0) * 100)
        return f"{percent:+d}%"

    @staticmethod
    def _volume_to_percent(volume: float) -> str:
        percent = round((volume - 1.0) * 100)
        return f"{percent:+d}%"

    def _build_params(self, req: TTSRequest) -> dict:
        voice = req.extra.get("voice") or req.model or self.voice
        rate = req.extra.get("rate") or self._speed_to_rate(req.speed)
        pitch = req.extra.get("pitch") or self.pitch
        volume = self._volume_to_percent(req.volume) if req.volume else "+0%"
        proxy = req.extra.get("proxy") or self.proxy
        return {
            "voice": voice,
            "rate": rate,
            "pitch": pitch,
            "volume": volume,
            "proxy": proxy,
        }

    async def synthesize(self, req: TTSRequest) -> TTSResponse:
        try:
            params = self._build_params(req)
            communicate = edge_tts.Communicate(req.text, **params)

            audio_chunks: list[bytes] = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])

            if not audio_chunks:
                return TTSResponse.fail("No audio data received from edge-tts")

            audio_data = b"".join(audio_chunks)
            return TTSResponse.ok(audio_data=audio_data, metadata={"format": "mp3"})
        except Exception as e:
            return TTSResponse.fail(f"{type(e).__name__}: {e}")

    async def synthesize_stream(self, req: TTSRequest) -> AsyncGenerator[bytes, None]:
        params = self._build_params(req)
        communicate = edge_tts.Communicate(req.text, **params)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    async def is_available(self) -> bool:
        try:
            await edge_tts.list_voices()
            return True
        except Exception:
            return False

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
