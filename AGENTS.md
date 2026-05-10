# tts-plugin-edgetts

**Plugin for Microsoft Edge TTS (edge-tts backend)**

## KEY FILES
| File | Role |
|------|------|
| `tts_plugin_edgetts/connector.py` | EdgeTTSConnector implementation |

## ENTRY POINT
```python
# pyproject.toml
[project.entry-points."tts_bridge.connectors"]
edgetts = "tts_plugin_edgetts.connector:EdgeTTSConnector"
```

## USAGE
```bash
tts-plugin-bridge synthesize "こんにちは" -e edgetts
tts-plugin-bridge synthesize "Hello" -e edgetts --pitch +5Hz
```

## CONVENTIONS
- Depends on: `tts-plugin-bridge` (core), `edge-tts` (TTS engine)
- Uses `edge_tts.Communicate` async API
- Inherits `TTSConnector` ABC
- Output format: MP3 (24kHz, 48kbps, mono)
