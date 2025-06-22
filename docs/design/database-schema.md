# データベーススキーマ設計書

## 概要

Auto Chat Makerシステムのデータベーススキーマ設計書です。Teamsチャット対応を基本とし、将来的なOutlookメール対応も考慮した拡張性のある設計となっています。

## データベース概要

- **データベース**: SQLite（ローカル試行版）
- **ORM**: SQLAlchemy
- **マイグレーション**: Alembic
- **文字エンコーディング**: UTF-8

## テーブル定義

### 1. users（ユーザーテーブル）

ユーザー情報を管理するテーブルです。

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**カラム詳細**:
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | UUID | PRIMARY KEY | ユーザーID（自動生成） |
| email | VARCHAR(255) | UNIQUE, NOT NULL | メールアドレス |
| name | VARCHAR(255) | NOT NULL | ユーザー名 |
| created_at | TIMESTAMP | DEFAULT | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT | 更新日時 |

**インデックス**:
- `idx_users_email` (email)

**サンプルデータ**:
```sql
INSERT INTO users (email, name) VALUES
('user1@example.com', '田中太郎'),
('user2@example.com', '佐藤花子');
```

### 2. message_types（メッセージタイプテーブル）

メッセージの種類を管理するマスターテーブルです。

```sql
CREATE TABLE message_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**カラム詳細**:
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | UUID | PRIMARY KEY | メッセージタイプID |
| type_name | VARCHAR(50) | UNIQUE, NOT NULL | タイプ名 |
| description | TEXT | | 説明 |
| is_active | BOOLEAN | DEFAULT TRUE | 有効フラグ |
| created_at | TIMESTAMP | DEFAULT | 作成日時 |

**インデックス**:
- `idx_message_types_type_name` (type_name)
- `idx_message_types_is_active` (is_active)

**サンプルデータ**:
```sql
INSERT INTO message_types (type_name, description) VALUES
('teams_chat', 'Teamsチャットメッセージ'),
('outlook_mail', 'Outlookメール（将来対応）'),
('text', 'テキストメッセージ'),
('image', '画像メッセージ'),
('file', 'ファイルメッセージ');
```

### 3. chat_messages（チャットメッセージテーブル）

Teamsチャットのメッセージ情報を管理するテーブルです。

```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    sender VARCHAR(255) NOT NULL,
    thread_id VARCHAR(255) NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    channel_id VARCHAR(255),
    team_id VARCHAR(255),
    sent_at TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**カラム詳細**:
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | UUID | PRIMARY KEY | チャットメッセージID |
| user_id | UUID | FOREIGN KEY | ユーザーID |
| message_id | VARCHAR(255) | UNIQUE, NOT NULL | TeamsメッセージID |
| content | TEXT | NOT NULL | メッセージ内容 |
| sender | VARCHAR(255) | NOT NULL | 送信者名 |
| thread_id | VARCHAR(255) | NOT NULL | スレッドID |
| message_type | VARCHAR(50) | NOT NULL | メッセージタイプ |
| channel_id | VARCHAR(255) | | TeamsチャンネルID |
| team_id | VARCHAR(255) | | TeamsチームID |
| sent_at | TIMESTAMP | | 送信日時 |
| processed_at | TIMESTAMP | | 処理日時 |
| created_at | TIMESTAMP | DEFAULT | 作成日時 |

**インデックス**:
- `idx_chat_messages_user_id` (user_id)
- `idx_chat_messages_message_id` (message_id)
- `idx_chat_messages_sent_at` (sent_at)
- `idx_chat_messages_thread_id` (thread_id)
- `idx_chat_messages_processed_at` (processed_at)
- `idx_chat_messages_channel_id` (channel_id)
- `idx_chat_messages_team_id` (team_id)

**サンプルデータ**:
```sql
INSERT INTO chat_messages (user_id, message_id, content, sender, thread_id, message_type, channel_id, team_id, sent_at) VALUES
(
    (SELECT id FROM users WHERE email = 'user1@example.com'),
    'msg_001',
    '明日の会議について確認したいのですが、何時からでしょうか？',
    '田中太郎',
    'thread_001',
    'text',
    'channel_001',
    'team_001',
    '2024-12-01 10:00:00'
);
```

### 4. reply_suggestions（返信案テーブル）

AIが生成した返信案を管理するテーブルです。

```sql
CREATE TABLE reply_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_message_id UUID NOT NULL,
    content TEXT NOT NULL,
    confidence_score DECIMAL(3,2),
    selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_message_id) REFERENCES chat_messages(id) ON DELETE CASCADE
);
```

**カラム詳細**:
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | UUID | PRIMARY KEY | 返信案ID |
| chat_message_id | UUID | FOREIGN KEY | チャットメッセージID |
| content | TEXT | NOT NULL | 返信案内容 |
| confidence_score | DECIMAL(3,2) | | 信頼度スコア（0.00-1.00） |
| selected | BOOLEAN | DEFAULT FALSE | 選択フラグ |
| created_at | TIMESTAMP | DEFAULT | 作成日時 |

**インデックス**:
- `idx_reply_suggestions_chat_message_id` (chat_message_id)
- `idx_reply_suggestions_selected` (selected)
- `idx_reply_suggestions_created_at` (created_at)
- `idx_reply_suggestions_confidence_score` (confidence_score)

**サンプルデータ**:
```sql
INSERT INTO reply_suggestions (chat_message_id, content, confidence_score) VALUES
(
    (SELECT id FROM chat_messages WHERE message_id = 'msg_001'),
    '明日の会議は14:00から予定しています。',
    0.95
),
(
    (SELECT id FROM chat_messages WHERE message_id = 'msg_001'),
    '会議の時間について確認いたします。明日14:00からでよろしいでしょうか？',
    0.88
),
(
    (SELECT id FROM chat_messages WHERE message_id = 'msg_001'),
    '明日の会議時間は14:00-15:00の予定です。',
    0.92
);
```

### 5. subscriptions（サブスクリプションテーブル）

Microsoft Graph APIのWebhookサブスクリプション情報を管理するテーブルです。

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    subscription_id VARCHAR(255) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    webhook_url VARCHAR(500),
    change_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**カラム詳細**:
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | UUID | PRIMARY KEY | サブスクリプションID |
| user_id | UUID | FOREIGN KEY | ユーザーID |
| subscription_id | VARCHAR(255) | NOT NULL | Microsoft GraphサブスクリプションID |
| resource | VARCHAR(255) | NOT NULL | リソースURL |
| resource_type | VARCHAR(50) | NOT NULL | リソースタイプ |
| expires_at | TIMESTAMP | NOT NULL | 有効期限 |
| webhook_url | VARCHAR(500) | | Webhook通知先URL |
| change_type | VARCHAR(50) | | 変更タイプ（created, updated, deleted） |
| is_active | BOOLEAN | DEFAULT TRUE | 有効フラグ |
| created_at | TIMESTAMP | DEFAULT | 作成日時 |

**インデックス**:
- `idx_subscriptions_user_id` (user_id)
- `idx_subscriptions_subscription_id` (subscription_id)
- `idx_subscriptions_expires_at` (expires_at)
- `idx_subscriptions_resource_type` (resource_type)
- `idx_subscriptions_is_active` (is_active)

**サンプルデータ**:
```sql
INSERT INTO subscriptions (user_id, subscription_id, resource, resource_type, expires_at, webhook_url, change_type) VALUES
(
    (SELECT id FROM users WHERE email = 'user1@example.com'),
    'sub_001',
    'https://graph.microsoft.com/v1.0/teams/team-id/channels/channel-id/messages',
    'teams_chat',
    '2024-12-02 10:00:00',
    'https://your-app.ngrok.io/api/webhook/microsoft-graph',
    'created'
);
```

## リレーションシップ

### 1対多の関係
- **users** → **chat_messages**: 1人のユーザーは複数のチャットメッセージを持つ
- **users** → **subscriptions**: 1人のユーザーは複数のサブスクリプションを持つ
- **chat_messages** → **reply_suggestions**: 1つのチャットメッセージは複数の返信案を生成する

### 多対多の関係
- **message_types** ↔ **chat_messages**: 1つのメッセージタイプは複数のチャットメッセージに適用される

## 制約

### 外部キー制約
- `chat_messages.user_id` → `users.id`
- `reply_suggestions.chat_message_id` → `chat_messages.id`
- `subscriptions.user_id` → `users.id`

### 一意制約
- `users.email`: メールアドレスの重複禁止
- `chat_messages.message_id`: TeamsメッセージIDの重複禁止
- `message_types.type_name`: メッセージタイプ名の重複禁止

### チェック制約
- `reply_suggestions.confidence_score`: 0.00以上1.00以下
- `message_types.is_active`: TRUE/FALSEのみ

## パフォーマンス最適化

### インデックス戦略
1. **主キーインデックス**: 全テーブルに自動作成
2. **外部キーインデックス**: 結合クエリの高速化
3. **検索インデックス**: 頻繁に検索されるカラム
4. **複合インデックス**: 複数条件での検索最適化

### 推奨クエリパターン
```sql
-- ユーザーのチャットメッセージ一覧取得
SELECT cm.*, rs.content as reply_content, rs.confidence_score
FROM chat_messages cm
LEFT JOIN reply_suggestions rs ON cm.id = rs.chat_message_id
WHERE cm.user_id = ? AND cm.sent_at >= ?
ORDER BY cm.sent_at DESC;

-- 未処理のチャットメッセージ取得
SELECT * FROM chat_messages
WHERE processed_at IS NULL
ORDER BY sent_at ASC;

-- 期限切れサブスクリプション取得
SELECT * FROM subscriptions
WHERE expires_at < NOW()
AND resource_type = 'teams_chat';
```

## データ整合性

### 削除時の動作
- **CASCADE**: 親レコード削除時に子レコードも削除
- **RESTRICT**: 子レコードが存在する場合は削除禁止

### 更新時の動作
- **CASCADE**: 親レコード更新時に子レコードも更新
- **SET NULL**: 親レコード削除時に子レコードをNULLに設定

## 拡張性設計

### 将来的なメール対応
```sql
-- メールメッセージテーブル（将来追加）
CREATE TABLE mail_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    subject VARCHAR(500),
    content TEXT NOT NULL,
    sender VARCHAR(255) NOT NULL,
    recipients TEXT,
    sent_at TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### プラグイン固有テーブル
```sql
-- Teamsチャット固有情報テーブル
CREATE TABLE teams_chat_extensions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_message_id UUID NOT NULL,
    channel_id VARCHAR(255),
    team_id VARCHAR(255),
    reply_to_message_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_message_id) REFERENCES chat_messages(id) ON DELETE CASCADE
);
```

## 更新履歴

- 初版作成: 2024年12月
- Teams対応化: 2024年12月 - Teamsチャットベースに変更
- 拡張性設計追加: 2024年12月 - 将来的なメール対応を考慮
- 最終更新: 2024年12月
- 更新者: 開発チーム
