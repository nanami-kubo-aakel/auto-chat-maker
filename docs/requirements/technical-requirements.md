# 技術要件

## 技術構成

| レイヤー          | 技術/ツール                     | 説明                     |
| ------------- | -------------------------- | ---------------------- |
| フロントエンド       | React / Next.js / Web通知API | ユーザーの返信選択UI、通知表示など     |
| バックエンド        | Node.js + Express          | Webhook受信・MCP制御・AI接続   |
| MCP通信         | `ms-365-mcp-server`        | Outlookへのメール取得／送信処理を担当 |
| AIエンジン        | Claude（Anthropic API）      | 返信要否判断・返信文案作成          |
| Microsoft API | Microsoft Graph API        | メール・スレッド・サブスクリプション管理   |

## 外部システム連携要件

* Microsoft Graph APIとの連携
* MCPサーバー（`ms-365-mcp-server`）との連携
* Claude API（Anthropic）との連携

## 更新履歴

- 初版作成: 2024年12月
- 最終更新: 2024年12月
- 更新者: 開発チーム 