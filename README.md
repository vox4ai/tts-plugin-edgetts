# tts-plugin-edgetts

<p align="center">
  <img src="https://via.placeholder.com/1200x400/1a1a1a/ffffff?text=tts-plugin-edgetts" alt="tts-plugin-edgetts Banner" width="1200">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/pypi-latest-blue.svg" alt="PyPI version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-yellow.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/maintained%3F-yes-brightgreen.svg" alt="Maintained">
</p>

<p align="center">
  <a href="https://github.com/vox4ai/tts-plugin-edgetts">Website</a> •
  <a href="https://github.com/vox4ai/tts-plugin-edgetts/issues">Report Bug</a> •
  <a href="https://github.com/vox4ai/tts-plugin-edgetts/contributing">Contributing</a>
</p>

---

## 🚀 Overview

[edge-tts](https://github.com/rany2/edge-tts) (Microsoft Edge TTS) を `tts-plugin-bridge` で利用するためのプラグインです。
APIキー不要で多言語対応のTTSが利用できます。

## 📦 インストール

```bash
uv add tts-plugin-bridge tts-plugin-edgetts
```

## ⚙️ 前提条件

- インターネット接続 (Microsoft Edge TTSサービスにアクセス)
- ローカルサーバー不要
- 再生には [ffplay](https://ffmpeg.org/ffplay.html) または `paplay` / `aplay` がPATHに存在すること
  - ffplay がある場合: ストリーミング再生（受信しながら即時再生）
  - ffplay がない場合: 全取得後に paplay / aplay で再生

## 🛠 Usage

### 🧩 Python API

```python
from tts_plugin_bridge import TTSSkill

async with TTSSkill(default_engine="edgetts") as skill:
    # save / synthesize — ファイル保存やBase64取得用
    res = await skill.save(
        text="こんにちは、エッジティーティーエスのテストです。",
        speed=1.2,
        model="ja-JP-KeitaNeural",
    )

    # say / play — 直接再生（ffplayストリーミング → paplay/aplay）
    res = await skill.say(
        text="ストリーミングで即時再生します。",
        speed=1.0,
    )
```

### 🎤 CLI（vox4ai 推奨）

```bash
# 直接再生（自動ストリーミング）
vox4ai say "こんにちは" -e edgetts

# 男性声で再生
vox4ai say "こんにちは" -e edgetts --model ja-JP-KeitaNeural

# ファイル保存（MP3）
vox4ai save "こんにちは" -e edgetts -o output.mp3

# 環境診断
vox4ai --doctor
```

### ⌨️ CLI（tts-plugin-bridge 後方互換）

```bash
tts-plugin-bridge synthesize "こんにちは" -e edgetts -o output.mp3
tts-plugin-bridge play "こんにちは" -e edgetts
tts-plugin-bridge play "こんにちは" -e edgetts --model ja-JP-KeitaNeural
```

## 🔧 サポートパラメータ

| パラメータ | 型 | 説明 |
|---|---|---|
| `speed` | float | 話速 (1.0=標準, >1.0=速い) → edge-tts `rate` に自動変換 |
| `volume` | float | 音量倍率 → edge-tts `volume` に自動変換 |
| `model` | str | 音声名 (例: `ja-JP-KeitaNeural`) → edge-tts `voice` にマッピング |
| `extra.pitch` | str | ピッチ (例: `+5Hz`, `-10Hz`) |
| `extra.rate` | str | 話速の直接指定 (例: `+50%`, `-20%`)。speed変換より優先 |
| `extra.volume` | str | 音量の直接指定 (例: `+100%`)。volume変換より優先 |
| `extra.voice` | str | 音声名の直接指定。modelより優先 |
| `extra.proxy` | str | プロキシURL |

### 🗣️ 主な音声一覧

| 音声名 | 性別 | 言語 |
|---|---|---|
| `ja-JP-NanamiNeural` | 女性 | 日本語 (デフォルト) |
| `ja-JP-KeitaNeural` | 男性 | 日本語 |
| `en-US-EmmaMultilingualNeural` | 女性 | 英語 (多言語対応) |
| `en-US-AndrewNeural` | 男性 | 英語 |

全音声一覧: `uv run edge-tts --list-voices`

### 📁 出力フォーマット

MP3 (24kHz, 48kbps, mono)

## 🔍 検証環境

- **OS**: Windows 11 + WSL2 (Ubuntu)
- **確認日**: 2026-05-09
- **依存**: edge-tts v7.2.8, bridge / vox4ai CLI
- **確認内容**:
  - `vox4ai say` によるストリーミング再生（ffplay 経由）
  - `vox4ai save` による MP3 ファイル保存
  - `vox4ai --doctor` 環境診断
  - `tts-plugin-bridge` CLI 後方互換維持
  - 全ユニットテスト 22件 パス

## 📜 ライセンス

MIT License
