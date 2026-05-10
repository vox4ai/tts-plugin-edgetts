# edgetts_01: tts-plugin-edgetts 設計

## 概要
Microsoft Edge TTS サービスを利用するプラグイン。
`edge-tts` Python パッケージを内部で呼び出し、`tts-plugin-bridge` の `TTSConnector` に準拠する。

## アーキテクチャ

```
tts-plugin-bridge (TTSSkill / ConnectorFactory)
        │
        ▼ entry_point: tts_bridge.connectors = edgetts
tts-plugin-edgetts (EdgeTTSConnector)
        │
        ▼
    edge-tts (Communicate / list_voices)
        │
        ▼
    Microsoft Edge TTS WebSocket API
```

## ディレクトリ構成
```
tts-plugin-edgetts/
├── pyproject.toml
├── AGENTS.md
├── reports/
├── tests/
│   └── test_connector.py
└── tts_plugin_edgetts/
    ├── __init__.py
    └── connector.py
```

## EdgeTTSConnector 仕様

### クラス定義
```python
class EdgeTTSConnector(TTSConnector):
    ENGINE_NAME = "edgetts"
    SUPPORTED_PARAMS = ["voice", "rate", "pitch", "proxy"]
```

### コンストラクタ
- `voice: str` — デフォルト `"ja-JP-NanamiNeural"`
- `rate: str` — デフォルト `"+0%"` (形式: `[+-]N%`)
- `pitch: str` — デフォルト `"+0Hz"` (形式: `[+-]NHz`)
- `proxy: Optional[str]` — デフォルト `None`

### TTSRequest マッピング
| TTSRequest フィールド | EdgeTTS パラメータ | 変換ロジック |
|---|---|---|
| `text` | `Communicate(text=...)` | そのまま |
| `speed` | `rate` | `speed` → パーセント形式 (1.0→"+0%", 1.5→"+50%", 0.5→"-50%") |
| `volume` | `volume` | `volume` → パーセント形式 (1.0→"+0%", 2.0→"+100%") |
| `pitch` | `pitch` | そのまま (Hz形式の文字列を想定) |
| `model` | `voice` | `model` を voice 名として使用 |
| `extra["voice"]` | `voice` | voice の直接指定 |
| `extra["rate"]` | `rate` | rate の直接指定 (直接指定優先) |
| `extra["pitch"]` | `pitch` | pitch の直接指定 (直接指定優先) |
| `extra["proxy"]` | `proxy` | proxy URL |

### synthesize() フロー
1. TTSRequest からパラメータを変換
2. `edge_tts.Communicate(text, voice, rate=, volume=, pitch=)` を生成
3. `stream()` で音声チャンクを収集 (MP3)
4. 全チャンクを結合して `TTSResponse.ok(audio_data=mp3_bytes)` を返す

### is_available() フロー
1. `edge_tts.list_voices()` を呼び出し
2. 例外なくレスポンスが返れば `True`、例外なら `False`

### 出力フォーマット
- edge-tts は MP3 (24kHz, 48kbps, mono) を出力
- `TTSRequest.output_format` が "wav" の場合、`pydub` なしでは変換不可
- 初期実装では MP3 のまま返却 (metadata に format="mp3" を記録)

## 依存関係
- `tts-plugin-bridge` (path dependency)
- `edge-tts>=7.0`
- `aiohttp` (edge-tts 経由)

## テスト方針 (TDD / t_wada)
1. **Red**: 失敗するテストを先に書く
2. **Green**: テストを通す最小実装
3. **Refactor**: リファクタリング

### テストケース
- test_connector_is_available_true
- test_connector_is_available_false
- test_connector_synthesize_basic
- test_connector_speed_to_rate_conversion
- test_connector_volume_to_percent
- test_connector_model_as_voice
- test_connector_extra_params_override
- test_connector_error_handling
- test_connector_context_manager
