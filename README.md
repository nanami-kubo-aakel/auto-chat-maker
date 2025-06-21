# Auto Chat Maker

## 概要
このプロジェクトは自動チャットメーカーソフトウェアです。

## セットアップ

### 必要な環境
- Python 3.8以上
- pip

### インストール手順
```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt

# 開発用依存関係のインストール
pip install -r requirements-dev.txt
```

### 開発環境のセットアップ
```bash
# コードフォーマッターの設定
pre-commit install
```

## 開発ガイドライン
- PEP8に準拠したコードスタイル
- 型ヒントの使用
- ドキュメント文字列の記述
- ログ出力の実装

## 開発コマンド

Makefileを使用して開発作業を効率化できます：

```bash
# 利用可能なコマンドを表示
make help

# 開発環境のセットアップ
make setup

# テストの実行
make test

# カバレッジ付きでテストを実行
make test-cov

# コード品質チェック
make lint

# コードフォーマット
make format

# コードフォーマットチェック
make format-check

# 一時ファイルの削除
make clean

# ドキュメント生成
make docs
```

## プロジェクト構造
```
auto_chat_maker/
├── src/
│   └── auto_chat_maker/
│       ├── __init__.py
│       ├── core/
│       ├── utils/
│       └── config/
├── tests/
└── docs/
```

## コントリビューション

プロジェクトへの貢献を歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ドキュメント

- [要件定義](docs/requirements/)
- [設計書](docs/design/)
- [仕様書](docs/specification/)
- [開発者ガイド](docs/developer-guide/) 