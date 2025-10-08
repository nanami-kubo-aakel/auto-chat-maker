# Netlifyセットアップ手順

このファイルは、Auto Chat MakerのドキュメントをNetlifyで公開するための実行手順です。

## ステップ1: GitHubへプッシュ

変更をGitHubにプッシュします：

```bash
git push origin main
```

認証が求められた場合：
- Username: あなたのGitHubユーザー名
- Password: GitHubのPersonal Access Token（パスワードではありません）

Personal Access Tokenの作成方法：
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "Generate new token (classic)"
3. Note: "Auto Chat Maker deployment"
4. Expiration: 適切な期限を選択
5. Scopes: `repo` にチェック
6. "Generate token" をクリック
7. 表示されたトークンをコピー（一度しか表示されません）

## ステップ2: GitHub OAuth アプリケーションの作成

### 2-1. GitHub Settings にアクセス

1. GitHubにログイン: https://github.com
2. 右上のプロフィールアイコンをクリック → **Settings**
3. 左メニュー下部の **Developer settings** をクリック
4. **OAuth Apps** → **New OAuth App** をクリック

### 2-2. OAuth アプリケーションの設定

以下の情報を入力します：

| フィールド | 値 |
|----------|-----|
| Application name | `Auto Chat Maker CMS` |
| Homepage URL | `https://YOUR-SITE-NAME.netlify.app` ※後で更新 |
| Application description | `CMS for Auto Chat Maker documentation` |
| Authorization callback URL | `https://api.netlify.com/auth/done` |

**Register application** をクリックします。

### 2-3. 認証情報の保存

作成後、以下の情報が表示されます：

- **Client ID**: コピーして安全な場所に保存
- **Client Secret**: **Generate a new client secret** をクリックして生成し、コピーして保存

⚠️ **重要**: Client Secretは一度しか表示されないため、必ず安全な場所に保存してください。

## ステップ3: Netlifyサイトの作成

### 3-1. Netlifyにログイン

1. Netlifyにアクセス: https://www.netlify.com/
2. **Sign up** または **Log in** をクリック
3. **GitHub** でログインすることを推奨

### 3-2. 新しいサイトを作成

1. ダッシュボードで **Add new site** → **Import an existing project** をクリック
2. **Deploy with GitHub** を選択
3. GitHubアカウントへのアクセスを承認（必要な場合）
4. リポジトリ一覧から `nanami-kubo-aakel/auto-chat-maker` を選択
   - 表示されない場合は、"Configure Netlify on GitHub" をクリックしてリポジトリへのアクセスを許可
5. ビルド設定を確認：
   - **Branch to deploy**: `main`
   - **Build command**: `pip install -r requirements-docs.txt && mkdocs build`
   - **Publish directory**: `site`
   - ※ `netlify.toml` があるため、自動的に設定されます
6. **Deploy site** をクリック

### 3-3. デプロイの確認

1. デプロイが開始されます（数分かかります）
2. ビルドログを確認して、エラーがないことを確認
3. デプロイが完了すると、ランダムなURL（例: `https://random-name-123456.netlify.app`）が割り当てられます

### 3-4. サイト名の変更（オプション）

1. **Site settings** をクリック
2. **Site details** セクションの **Change site name** をクリック
3. わかりやすい名前に変更（例: `auto-chat-maker-docs`）
4. **Save** をクリック
5. 新しいURL: `https://auto-chat-maker-docs.netlify.app`

**このURLをメモしてください**（次のステップで使用します）

## ステップ4: GitHub OAuth認証の設定

### 4-1. NetlifyでOAuth設定

1. Netlifyサイトの **Site settings** に移動
2. 左メニューの **Site configuration** → **Access & security** → **OAuth** をクリック
3. **Install provider** または **Install authentication provider** をクリック
4. **GitHub** を選択
5. ステップ2で保存したGitHub OAuthの認証情報を入力：
   - **Client ID**: GitHub OAuthアプリのClient ID
   - **Client Secret**: GitHub OAuthアプリのClient Secret
6. **Install** をクリック

### 4-2. GitHub OAuth アプリのHomepage URLを更新

1. GitHubの **Settings** → **Developer settings** → **OAuth Apps** に戻る
2. 作成した `Auto Chat Maker CMS` アプリを選択
3. **Homepage URL** を実際のNetlify URL（例: `https://auto-chat-maker-docs.netlify.app`）に更新
4. **Update application** をクリック

## ステップ5: CMS管理画面へのアクセス

### 5-1. 管理画面にログイン

1. ブラウザで Netlify URL + `/admin/` にアクセス
   - 例: `https://auto-chat-maker-docs.netlify.app/admin/`
2. **Login with GitHub** をクリック
3. GitHubアカウントでログイン
4. リポジトリへのアクセスを承認（初回のみ）

### 5-2. ドキュメントの編集テスト

1. 左メニューから任意のコレクション（例: 要件定義）を選択
2. ファイルを選択して編集
3. **Save** をクリック（下書き保存）
4. **Publish** → **Publish now** をクリック
5. GitHubリポジトリを確認して、コミットが作成されていることを確認
6. 数分後にNetlifyが自動的に再ビルドし、変更が反映される

## ✅ セットアップ完了

以下が正常に動作していれば、セットアップ完了です：

- [ ] GitHubへのプッシュが完了
- [ ] GitHub OAuthアプリが作成済み
- [ ] NetlifyでサイトがデプロイされDocumentationが閲覧可能
- [ ] CMS管理画面（`/admin/`）にアクセス可能
- [ ] GitHub OAuthでログイン可能
- [ ] CMSからドキュメントを編集し、GitHubにコミット可能
- [ ] 編集後、自動的にNetlifyが再ビルド・デプロイ

## トラブルシューティング

### ログインできない

- GitHub OAuth アプリの **Authorization callback URL** が `https://api.netlify.com/auth/done` になっているか確認
- NetlifyのOAuth設定でClient IDとClient Secretが正しいか確認

### ビルドが失敗する

- Netlifyのデプロイログを確認
- Python 3.11が使用されているか確認
- `requirements-docs.txt` のパッケージがすべてインストールされているか確認

### CMSで編集が保存できない

- GitHubリポジトリへの書き込み権限があるか確認
- GitHub OAuthアプリの認証スコープが正しいか確認

## サイトURL

セットアップ完了後のURL：

- **ドキュメントサイト**: `https://YOUR-SITE-NAME.netlify.app/`
- **CMS管理画面**: `https://YOUR-SITE-NAME.netlify.app/admin/`

---

詳細なドキュメントは `docs/instructions/decap-cms-setup.md` を参照してください。
