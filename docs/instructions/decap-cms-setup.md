# DeCap CMS セットアップガイド

## 概要

このガイドでは、Auto Chat MakerプロジェクトのドキュメントをDeCap CMSとNetlify経由で公開し、Web UIから編集できるようにする手順を説明します。

## 前提条件

- GitHubアカウント
- Netlifyアカウント（無料プラン可）
- このリポジトリへの管理者権限

## セットアップ手順

### 1. GitHubリポジトリの確認

プロジェクトがGitHubリポジトリにプッシュされていることを確認してください。

```bash
git remote -v
```

### 2. GitHub OAuth アプリケーションの作成

#### 2.1 GitHub Settings にアクセス

1. GitHubにログイン
2. 右上のプロフィールアイコンをクリック → **Settings**
3. 左メニューの **Developer settings** をクリック
4. **OAuth Apps** → **New OAuth App** をクリック

#### 2.2 OAuth アプリケーションの設定

以下の情報を入力します：

- **Application name**: `Auto Chat Maker CMS`（任意の名前）
- **Homepage URL**: `https://YOUR-SITE-NAME.netlify.app`（後でNetlifyから取得）
- **Application description**: `CMS for Auto Chat Maker documentation`（任意）
- **Authorization callback URL**: `https://api.netlify.com/auth/done`

**Register application** をクリックします。

#### 2.3 認証情報の保存

作成後、以下の情報が表示されます：

- **Client ID**: 後で使用するのでコピーして保存
- **Client Secret**: **Generate a new client secret** をクリックして生成し、コピーして保存

⚠️ **重要**: Client Secretは一度しか表示されないため、必ず安全な場所に保存してください。

### 3. Netlifyサイトの作成

#### 3.1 Netlifyにログイン

[Netlify](https://www.netlify.com/)にアクセスしてログインします（GitHubアカウントでログイン可能）。

#### 3.2 新しいサイトを作成

1. ダッシュボードで **Add new site** → **Import an existing project** をクリック
2. **GitHub** を選択
3. リポジトリ一覧から `auto_chat_maker` を選択
4. ビルド設定は自動的に検出されます（`netlify.toml`を使用）
   - Build command: `pip install -r requirements-docs.txt && mkdocs build`
   - Publish directory: `site`
5. **Deploy site** をクリック

#### 3.3 サイト名の設定（オプション）

1. デプロイが完了したら、**Site settings** をクリック
2. **Change site name** でわかりやすい名前に変更
   - 例: `auto-chat-maker-docs`
3. サイトURLが `https://auto-chat-maker-docs.netlify.app` のようになります

### 4. GitHub OAuth 認証の設定

#### 4.1 NetlifyでOAuth設定

1. Netlifyサイトの **Site settings** に移動
2. 左メニューの **Access control** → **OAuth** をクリック
3. **Install provider** から **GitHub** を選択
4. 先ほど保存したGitHub OAuthの認証情報を入力：
   - **Client ID**: GitHub OAuthアプリのClient ID
   - **Client Secret**: GitHub OAuthアプリのClient Secret
5. **Install** をクリック

#### 4.2 Homepage URLの更新

GitHub OAuth アプリの設定を更新します：

1. GitHubの **Developer settings** → **OAuth Apps** に戻る
2. 作成したアプリを選択
3. **Homepage URL** を実際のNetlify URL（例: `https://auto-chat-maker-docs.netlify.app`）に更新
4. **Update application** をクリック

### 5. config.ymlの更新

`docs/admin/config.yml` を開き、リポジトリ情報を更新します：

```yaml
backend:
  name: github
  repo: YOUR_GITHUB_USERNAME/auto_chat_maker  # 実際のユーザー名とリポジトリ名
  branch: main  # デフォルトブランチ名（mainまたはmaster）
```

変更をコミットしてプッシュします：

```bash
git add docs/admin/config.yml
git commit -m "Update DeCap CMS repository configuration"
git push origin main
```

Netlifyが自動的に再ビルド・デプロイします。

### 6. CMS管理画面へのアクセス

#### 6.1 管理画面にログイン

1. ブラウザで `https://YOUR-SITE-NAME.netlify.app/admin/` にアクセス
2. **Login with GitHub** をクリック
3. GitHubアカウントでログイン
4. リポジトリへのアクセスを承認

#### 6.2 ドキュメントの編集

- 左メニューから編集したいコレクション（要件定義、設計書など）を選択
- ファイルを選択して編集
- **Publish** をクリックすると、GitHubリポジトリにコミットされます
- Netlifyが自動的に再ビルドし、変更が反映されます

## ワークフロー

### 通常の編集フロー

1. CMS管理画面で編集 → **Publish** をクリック
2. 変更がGitHubにコミットされる
3. Netlifyが自動的にビルド・デプロイ
4. 数分後にサイトに変更が反映される

### ローカルでの編集フロー

従来通り、ローカルでMarkdownファイルを編集し、`git push`することも可能です。

```bash
# ローカルで編集
vim docs/requirements/functional-requirements.md

# コミット
git add .
git commit -m "Update functional requirements"
git push origin main
```

## トラブルシューティング

### ログインできない

- GitHub OAuth アプリの **Authorization callback URL** が `https://api.netlify.com/auth/done` になっているか確認
- NetlifyのOAuth設定でClient IDとClient Secretが正しいか確認

### 編集が反映されない

- Netlifyのデプロイログを確認（**Deploys** タブ）
- ビルドエラーがある場合は、`requirements-docs.txt` に必要なパッケージが含まれているか確認

### CMSで特定のファイルが表示されない

- `docs/admin/config.yml` の `collections` 設定を確認
- ファイルが正しいフォルダ構造に配置されているか確認

## 参考リンク

- [DeCap CMS公式ドキュメント](https://decapcms.org/docs/)
- [Netlify公式ドキュメント](https://docs.netlify.com/)
- [MkDocs公式ドキュメント](https://www.mkdocs.org/)
- [GitHub OAuth Apps ドキュメント](https://docs.github.com/en/developers/apps/building-oauth-apps)

## セキュリティに関する注意事項

- Client Secretは絶対に公開リポジトリにコミットしないでください
- CMSへのアクセスはGitHub OAuthで制限されるため、リポジトリへのアクセス権を持つユーザーのみが編集可能です
- 本番環境では、編集権限を持つユーザーを適切に管理してください
