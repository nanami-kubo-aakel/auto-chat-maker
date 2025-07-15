# コード品質チェック・修正手順

## 概要

このドキュメントは、mypyとflake8の規約チェックを実行し、検出されたエラーを修正する手順を説明します。
開発フローに組み込む際のAIプロンプトとして使用できます。

## AIプロンプト

```
# 要件
mypy, flake8の規約がコード内で守られているか確認し、エラーを修正してください。

# タスク
1. 仮想環境を立ち上げてください
2. docs/instructions, auto-chat-maker直下の設定を確認してください
3. 実行コマンドに従って、src, test以下のコードをチェックしてください
4. flake8, mypyでエラーが出た個所を修正してください
5. push時にmypyエラーが出ないよう、バージョン統一を行ってください
6. 修正後、テストが通ることを確認してください

# 実行手順

## 1. 環境セットアップ
```bash
# 仮想環境セットアップ
make setup-venv
source venv/bin/activate
```

## 2. 設定確認
- `docs/instructions/developer-guide.md`: 開発ガイドライン
- `docs/instructions/environment-setup.md`: 環境設定ガイド
- `pyproject.toml`: mypy設定
- `.flake8`: flake8設定
- `Makefile`: 実行コマンド
- `.pre-commit-config.yaml`: pre-commit設定

## 3. 静的解析実行
```bash
# flake8チェック
flake8 src/ tests/

# mypyチェック
mypy src/
```

## 4. エラー修正

### 4.1 flake8エラー修正
- **行長超過**: 79文字制限内に分割
- **未使用インポート**: 不要なimport文を削除
- **空行エラー**: 適切な空行数に修正

### 4.2 mypyエラー修正
- **型アノテーション不足**: 関数引数・返り値に型を追加
- **Any返却エラー**: cast()で明示的型変換
- **デコレータ型エラー**: `# type: ignore[misc]`を追加
- **重複モジュール**: 不要なファイルを削除

### 4.3 バージョン統一
```bash
# requirements-dev.txtでmypyバージョンを固定
mypy==1.3.0

# ローカル環境を更新
pip install -r requirements-dev.txt
```

## 5. 最終確認
```bash
# pre-commitフック実行（push時と同じ）
pre-commit run --all-files

# テスト実行
make test
```

# 修正対象ファイル例

## 型アノテーション追加
```python
# Before
def get_logger(self, name: str):
    return structlog.get_logger(name)

# After
def get_logger(self, name: str) -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
```

## 行長修正
```python
# Before
return f"ChatMessage(id={self.id}, message_id={self.message_id}, sender={self.sender_name})"

# After
return (
    f"ChatMessage(id={self.id}, message_id={self.message_id}, "
    f"sender={self.sender_name})"
)
```

## デコレータ型エラー修正
```python
# Before
@router.get("/health")
async def health_check() -> Dict[str, Any]:

# After
@router.get("/health")  # type: ignore[misc]
async def health_check() -> Dict[str, Any]:
```

# 期待される結果

## 成功条件
- ✅ flake8: エラーゼロ
- ✅ mypy: エラーゼロ
- ✅ pre-commit: 全フック通過
- ✅ テスト: 全テスト通過
- ✅ バージョン統一: mypy 1.3.0

## 出力例
```
pre-commit run --all-files
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
check for merge conflicts................................................Passed
debug statements (python)................................................Passed
black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
mypy.....................................................................Passed

make test
==================================== 28 passed, 1 warning in 0.40s ====================================
```

# 注意事項

## バージョン管理
- mypyバージョンは1.3.0に統一
- pre-commit設定とローカル環境のバージョンを一致させる
- CI/CD環境でも同じバージョンを使用

## 修正の原則
- 既存のテストを壊さない
- 機能に影響を与えない
- 型安全性を向上させる
- 可読性を維持する

## トラブルシューティング

### 重複モジュールエラー
```
error: Duplicate module named "auto_chat_maker.api.routes"
```
**解決策**: 不要なファイル（例：`routes.py`）を削除

### デコレータ型エラー
```
error: Untyped decorator makes function "health_check" untyped
```
**解決策**: `# type: ignore[misc]`をデコレータに追加

### バージョン不一致
```
pre-commit mypy version: 1.3.0
local mypy version: 1.16.1
```
**解決策**: `requirements-dev.txt`でバージョンを固定し、再インストール

# 更新履歴

- 初版作成: 2024年12月
- 更新者: 開発チーム
- 最終更新: 2024年12月
