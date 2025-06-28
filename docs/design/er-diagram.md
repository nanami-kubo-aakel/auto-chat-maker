# ER図

Auto Chat MakerシステムのER図（Entity Relationship Diagram）です。

## 概要

この図は、Auto Chat Makerシステムのデータベース設計を示しています。主要なエンティティとその関係性を表現しています。

## ER図

![ER図](https://www.plantuml.com/plantuml/png/SoWkIImgAStDuU8gBKbL2D0rKj2rKl1DpSd91m00)

## 説明

### エンティティ

1. **users（ユーザー）**
   - システムの利用者情報
   - メールアドレスと名前を管理

2. **message_types（メッセージタイプ）**
   - チャットメッセージの分類
   - システムで処理するメッセージの種類を定義

3. **chat_messages（チャットメッセージ）**
   - Teamsチャットのメッセージ情報
   - 送信者、内容、スレッド情報を管理

4. **reply_suggestions（返信案）**
   - AIが生成した返信案
   - 信頼度スコアと選択状態を管理

5. **subscriptions（サブスクリプション）**
   - Microsoft Graph APIのサブスクリプション情報
   - Webhook通知の管理

### リレーションシップ

- **users** → **chat_messages**: 1対多（1人のユーザーは複数のチャットメッセージを持つ）
- **users** → **subscriptions**: 1対多（1人のユーザーは複数のサブスクリプションを持つ）
- **message_types** → **chat_messages**: 1対多（1つのメッセージタイプは複数のチャットメッセージに適用される）
- **chat_messages** → **reply_suggestions**: 1対多（1つのチャットメッセージは複数の返信案を生成する）

### インデックス

各テーブルには適切なインデックスが設定されており、クエリパフォーマンスを最適化しています。

## PlantUMLソースコード

```plantuml
@startuml Auto Chat Maker ER Diagram

!theme plain
skinparam entity {
    BackgroundColor LightBlue
    BorderColor DarkBlue
    FontColor Black
    FontSize 12
}

skinparam relationship {
    Color DarkBlue
    FontColor DarkBlue
    FontSize 10
}

title Auto Chat Maker システム - ER図（Entity Relationship Diagram）

' エンティティ定義
entity "users" as users {
    * id : UUID (PK)
    --
    * email : VARCHAR(255) (UNIQUE)
    * name : VARCHAR(255)
    created_at : TIMESTAMP
    updated_at : TIMESTAMP
}

entity "message_types" as message_types {
    * id : UUID (PK)
    --
    * type_name : VARCHAR(50) (UNIQUE)
    description : TEXT
    is_active : BOOLEAN
    created_at : TIMESTAMP
}

entity "chat_messages" as chat_messages {
    * id : UUID (PK)
    --
    * user_id : UUID (FK)
    * message_id : VARCHAR(255) (UNIQUE)
    * content : TEXT
    * sender : VARCHAR(255)
    * thread_id : VARCHAR(255)
    * message_type : VARCHAR(50)
    sent_at : TIMESTAMP
    processed_at : TIMESTAMP
    created_at : TIMESTAMP
}

entity "reply_suggestions" as reply_suggestions {
    * id : UUID (PK)
    --
    * chat_message_id : UUID (FK)
    * content : TEXT
    confidence_score : DECIMAL(3,2)
    selected : BOOLEAN
    created_at : TIMESTAMP
}

entity "subscriptions" as subscriptions {
    * id : UUID (PK)
    --
    * user_id : UUID (FK)
    * subscription_id : VARCHAR(255)
    * resource : VARCHAR(255)
    * resource_type : VARCHAR(50)
    expires_at : TIMESTAMP
    created_at : TIMESTAMP
}

' リレーションシップ定義
users ||--o{ chat_messages : "has"
users ||--o{ subscriptions : "has"
message_types ||--o{ chat_messages : "categorizes"
chat_messages ||--o{ reply_suggestions : "generates"

' カーディナリティの説明
note right of users
  1人のユーザーは複数の
  チャットメッセージを持つ
end note

note right of chat_messages
  1つのチャットメッセージは
  複数の返信案を生成する
end note

note right of subscriptions
  1人のユーザーは複数の
  サブスクリプションを持つ
end note

note right of message_types
  1つのメッセージタイプは
  複数のチャットメッセージに
  適用される
end note

' インデックス情報
note bottom of chat_messages
  インデックス:
  - user_id (FK)
  - message_id (UNIQUE)
  - sent_at
  - thread_id
end note

note bottom of reply_suggestions
  インデックス:
  - chat_message_id (FK)
  - selected
  - created_at
end note

note bottom of subscriptions
  インデックス:
  - user_id (FK)
  - subscription_id
  - expires_at
end note

@enduml
```
