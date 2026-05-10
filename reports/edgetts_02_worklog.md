# edgetts_02: 作業ログ 2026-05-08

## 作業概要
vox4ai リポジトリに `tts-plugin-edgetts` を新規作成し、`tts-plugin-bridge` にストリーミング再生機能を追加した。

---

## Phase 1: 調査・設計

### コードベース調査
- `tts-plugin-piperplus` — `PiperPlusConnector` (TTSConnector実装、aiohttp HTTP通信)
- `tts-plugin-bridge` — `TTSConnector` ABC / `ConnectorFactory` (entry_points発見) / `TTSSkill` (Agent向けラッパー+CLI)
- `edge-tts` v7.2.8 — `Communicate` クラスの async stream API、`list_voices()`、rate/volume/pitch パラメータ

### br (beads-rust) の試行
- `br init` → SQLite "file-backed pager not available on this platform" エラー
- Windows環境でbrが動作しないため、`reports/` ディレクトリで代替管理

### 設計書
- `reports/edgetts_01_design.md` にアーキテクチャ・パラメータマッピング・テスト方針を記載

---

## Phase 2: tts-plugin-edgetts 実装 (TDD)

### プロジェクトスケルトン
```
tts-plugin-edgetts/
├── pyproject.toml          # entry_point: tts_bridge.connectors = edgetts
├── AGENTS.md
├── README.md
├── .gitignore
├── LICENSE
├── reports/
│   └── edgetts_01_design.md
├── tests/
│   ├── test_connector.py
│   └── test_integration.py
└── tts_plugin_edgetts/
    ├── __init__.py
    └── connector.py
```

### TDD Red → Green → Refactor

**Red**: 14テストを先に記述 (importエラーで失敗確認)
**Green**: `EdgeTTSConnector` 最小実装で14/14通過
**Refactor**: `_build_params()` 抽出、ruff format適用

### EdgeTTSConnector 仕様
| パラメータ | デフォルト | 変換ロジック |
|---|---|---|
| `voice` | `ja-JP-NanamiNeural` | `TTSRequest.model` or `extra["voice"]` で上書き |
| `rate` | `+0%` | `speed` → `round((speed-1)*100)` → `±N%` |
| `volume` | `+0%` | `volume` → `round((volume-1)*100)` → `±N%` |
| `pitch` | `+0Hz` | `extra["pitch"]` で直接指定 |
| `proxy` | None | `extra["proxy"]` で指定 |

---

## Phase 3: 結合試験

`test_integration.py` で bridge 経由の動作を6テスト検証:
- `ConnectorFactory.list_available()` に "edgetts" が含まれる
- `ConnectorFactory.create("edgetts")` → `EdgeTTSConnector` インスタンス
- `TTSSkill.synthesize()` → base64音声データ返却
- speed/volume パラメータ変換の確認
- エンジン unavailable 時のエラーハンドリング
- entry_points 登録の確認

### 実発声テスト
3パターンのMP3生成 + Windowsプレーヤーで再生確認:
- edge-tts直接: 24KB
- EdgeTTSConnector経由: 28KB
- speed=1.3, volume=1.5, KeitaNeural: 14KB

---

## Phase 4: ストリーミング再生対応 (要望対応)

### 追加要件
1. bridge が ffplay を subprocess で呼んで再生
2. edgetts のストリーミング再生を活かしたパイプ渡し

### tts-plugin-bridge 変更点

**protocol.py**:
- `TTSConnector.synthesize_stream()` 追加 — デフォルト実装(一括yield)付きasync generator
- 型ヒントに `AsyncGenerator` 追加

**skill.py**:
- `TTSSkill.play()` 追加 — ストリーミング合成→ffplay stdin パイプ再生
- `shutil.which("ffplay")` で自動検索、`player` 引数で上書き可能
- `FileNotFoundError` ハンドリング追加
- CLI `play` サブコマンド追加
  ```
  tts-plugin-bridge play "こんにちは" -e edgetts
  ```

### tts-plugin-edgetts 変更点

**connector.py**:
- `_build_params()` にリファクタリング (synthesize/synthesize_stream 共用)
- `synthesize_stream()` オーバーライド — edge-ttsの `Communicate.stream()` からaudioチャンクを直接yield
- バッファなしでffplayにストリーミング

### データフロー
```
TTSSkill.play()
  → EdgeTTSConnector.synthesize_stream()
    → edge_tts.Communicate.stream()
      → MP3チャンク yield (720B/チャンク)
    → subprocess.stdin.write(chunk)
  → ffplay -nodisp -autoexit -i pipe:0
```

### ストリーミングテスト追加
- bridge: `test_play.py` 5テスト (Popenモック、ffplay不在、エンジン不可、デフォルトストリーム)
- edgetts: `test_connector.py` 2テスト追加 (チャンクyield確認、パラメータ引継ぎ)

---

## 最終テスト結果

| パッケージ | テスト数 | 結果 |
|---|---|---|
| tts-plugin-bridge | 16 | 16 passed |
| tts-plugin-edgetts | 22 | 22 passed |
| **合計** | **38** | **38 passed** |

lint: ruff check 全通過 / format: ruff format 適用済み

### 実発声確認
- `skill.play()` → ffplay経由で35チャンクストリーミング再生 OK
- CLI `tts-plugin-bridge play "..." -e edgetts` → 36チャンク再生 OK
