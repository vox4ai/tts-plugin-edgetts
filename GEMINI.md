# tts-plugin-edgetts

[edge-tts](https://github.com/rany2/edge-tts) (Microsoft Edge TTS) を `tts-plugin-bridge` で利用するためのプラグインです。

## 🛠 概要
- **役割**: Microsoft Edge TTS サービスを使用して、API キー不要で多言語音声合成を行う。
- **主要機能**:
    - クラウドベースの音声合成（ローカルサーバー不要）。
    - ストリーミング再生（`ffplay` がある場合）またはローカル再生（`paplay`/`aplay`）。
    - 多言語・多声種への対応。

## ⚙️ 前提条件
- インターネット接続。
- 再生用コマンド (`ffplay`, `paplay`, `aplay` のいずれか) が PATH に存在すること。

## 🚀 開発・実行
- **パッケージ管理**: `uv`
- **テスト**: `pytest`

## 🔗 関連リポジトリ
- `repos/tts-plugin-bridge`: コアフレームワーク
