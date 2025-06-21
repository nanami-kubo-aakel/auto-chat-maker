# コントリビューションガイド

このプロジェクトへの貢献をありがとうございます。以下のガイドラインに従って開発に参加してください。

## 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/nanami-kubo-aakel/auto-chat-maker.git
cd auto-chat-maker

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements-dev.txt

# プレコミットフックの設定
pre-commit install
```

## コーディング規約

- PEP8に準拠したコードスタイル
- 型ヒントの使用
- ドキュメント文字列の記述
- ログ出力の実装

詳細は `docs/developer-guide/` を参照してください。

## コミットメッセージのルール

### 基本フォーマット

```
[コミット種別]要約

変更した理由（内容、詳細）
```

### コミット種別（ライト版）

- **fix**: バグ修正
- **add**: 新規（ファイル）機能追加
- **update**: 機能修正（バグではない）
- **remove**: 削除（ファイル）

### 例

```
[fix]削除フラグが更新されない不具合の修正

refs #110 更新SQLの対象カラムに削除フラグが含まれていなかったため追加しました。
```

### コミット単位

- 1つのバグ修正 = 1つのコミット
- 1つの機能追加 = 1つのコミット
- 複数の変更を1つのコミットにまとめない

## プルリクエストの作成

1. 新しいブランチを作成
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 変更をコミット
   ```bash
   git add .
   git commit -m "[add]新機能の追加"
   ```

3. プルリクエストを作成
   - タイトルは変更内容を簡潔に
   - 説明には変更理由と影響範囲を記載

## テスト

```bash
# テストの実行
make test

# コード品質チェック
make lint

# コードフォーマット
make format
```

## 参考資料

- [Gitのコミットメッセージの書き方](https://qiita.com/itosho/items/9565c6ad2ffc24c09364)
- [開発者ガイド](docs/developer-guide/README.md) 