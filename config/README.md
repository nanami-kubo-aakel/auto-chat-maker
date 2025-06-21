# 設定ファイル

このディレクトリには、アプリケーションの設定ファイルが含まれています。

## 構成

- `default.yaml` - デフォルト設定
- `development.yaml` - 開発環境用設定
- `production.yaml` - 本番環境用設定
- `test.yaml` - テスト環境用設定

## 使用方法

環境変数 `APP_ENV` を設定することで、適切な設定ファイルが読み込まれます。

```bash
export APP_ENV=development
python -m auto_chat_maker
``` 