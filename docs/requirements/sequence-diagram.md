# シーケンス図

Auto Chat Makerシステムのシーケンス図です。

## 概要

この図は、Auto Chat Makerシステムの主要な処理フローの時系列での動作を示しています。

## シーケンス図

![シーケンス図](https://www.plantuml.com/plantuml/png/SoWkIImgAStDuU8gBKbL2D0rKj2rKl1DpSd91m00)

## 説明

### 主要フロー

1. **Teamsチャット検知・返信案生成フロー**
   - Microsoft Graph APIからのWebhook通知を受信
   - チャットメッセージ情報を取得・記録
   - AIサービスによる返信必要性判定
   - 返信が必要な場合、返信案を生成・通知

2. **返信案選択・確定フロー**
   - ユーザーによる返信案の選択・編集
   - 確定された返信内容の保存

3. **Teamsチャット返信実行フロー**
   - MCPサーバー経由でのTeamsチャット返信
   - 送信履歴の記録

### 参加者

- **エンドユーザー**: システムの利用者
- **Microsoft Graph API**: Teamsチャットとの連携
- **Auto Chat Maker**: メインシステム
- **MCPサーバー**: チャット送信の実行
- **AIサービス**: 返信判定・生成
- **通知サービス**: ユーザー通知
- **データベース**: データ保存・管理

### 拡張予定

将来的なOutlookメール対応では、同じAI判定・生成ロジックを再利用し、MCPサーバー経由でメール送信を実行する予定です。

## PlantUMLソースコード

```plantuml
@startuml Auto Chat Maker Sequence Diagram

!theme plain
skinparam sequence {
    ArrowColor DarkBlue
    ActorBorderColor DarkBlue
    LifeLineBorderColor DarkBlue
    ParticipantBorderColor DarkBlue
    ParticipantBackgroundColor LightBlue
}

title Auto Chat Maker - Teamsチャット自動検知・返信案生成シーケンス図

actor "エンドユーザー" as User
participant "Microsoft Graph API" as GraphAPI
participant "Auto Chat Maker" as System
participant "MCPサーバー" as MCPServer
participant "AIサービス" as AIService
participant "通知サービス" as NotificationService
participant "データベース" as DB

== Teamsチャット検知・返信案生成フロー ==

GraphAPI -> System: Webhook通知 (新着チャットメッセージ)
activate System

System -> DB: チャットメッセージ情報をログに記録
activate DB
DB --> System: 記録完了
deactivate DB

System -> MCPServer: チャットメッセージ情報取得要求
activate MCPServer
MCPServer --> System: チャットメッセージ本文・送信者・スレッド情報
deactivate MCPServer

System -> AIService: 返信必要性判定要求
activate AIService
AIService -> AIService: チャットメッセージ内容を分析
AIService --> System: 返信必要判定結果
deactivate AIService

alt 返信が必要な場合
    System -> AIService: 返信案生成要求
    activate AIService
    AIService -> AIService: 3件の返信案を生成
    AIService --> System: 返信案リスト
    deactivate AIService

    System -> NotificationService: ユーザー通知要求
    activate NotificationService
    NotificationService -> User: 通知送信
    NotificationService --> System: 通知完了
    deactivate NotificationService

    System -> DB: 返信案を保存
    activate DB
    DB --> System: 保存完了
    deactivate DB

    System -> User: 返信案選択UI表示
else 返信が不要な場合
    System -> DB: 処理結果をログに記録
    activate DB
    DB --> System: 記録完了
    deactivate DB
end

deactivate System

== 返信案選択・確定フロー ==

User -> System: 返信案選択
activate System

System -> DB: 保存された返信案を取得
activate DB
DB --> System: 返信案データ
deactivate DB

System -> User: 返信案一覧表示

alt 返信案を編集する場合
    User -> System: 返信案編集
    System -> User: テキストエディタ表示
    User -> System: 編集内容送信
else 返信案をそのまま使用する場合
    User -> System: 返信案選択
end

System -> DB: 確定された返信内容を保存
activate DB
DB --> System: 保存完了
deactivate DB

deactivate System

== Teamsチャット返信実行フロー ==

User -> System: 返信実行指示
activate System

System -> DB: 確定された返信内容を取得
activate DB
DB --> System: 返信内容
deactivate DB

System -> MCPServer: チャット返信要求
activate MCPServer
MCPServer -> GraphAPI: Teamsチャット返信メッセージ送信
activate GraphAPI
GraphAPI --> MCPServer: 送信結果
deactivate GraphAPI
MCPServer --> System: 送信完了
deactivate MCPServer

System -> DB: 送信履歴を記録
activate DB
DB --> System: 記録完了
deactivate DB

System -> User: 送信完了通知
deactivate System

== 将来的なメール対応フロー（拡張予定） ==

note over System, DB
将来的なOutlookメール対応時は、
同じAI判定・生成ロジックを再利用し、
MCPサーバー経由でメール送信を実行
end note

@enduml
```
