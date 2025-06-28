.PHONY: help install install-dev test lint format clean docs venv setup setup-venv docs-install docs-serve docs-build docs-deploy docs-clean

help:  ## このヘルプメッセージを表示
	@echo "利用可能なコマンド:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv:  ## 仮想環境を作成
	python -m venv venv
	@echo "仮想環境を作成しました。有効化するには: source venv/bin/activate"

setup-venv: venv  ## 仮想環境を作成し、依存関係をインストール
	@echo "仮想環境を作成し、依存関係をインストールしています..."
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r requirements-dev.txt
	venv/bin/pre-commit install
	@echo "仮想環境のセットアップが完了しました。有効化するには: source venv/bin/activate"

install:  ## 依存関係をインストール（仮想環境が有効な場合）
	pip install -r requirements.txt

install-dev:  ## 開発用依存関係をインストール（仮想環境が有効な場合）
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## テストを実行
	pytest

test-cov:  ## カバレッジ付きでテストを実行
	pytest --cov=src/auto_chat_maker --cov-report=html --cov-report=term-missing

lint:  ## コード品質チェックを実行
	flake8 src/ tests/
	mypy src/
	pylint src/

format:  ## コードフォーマットを実行
	black src/ tests/
	isort src/ tests/

format-check:  ## コードフォーマットチェックを実行
	black --check src/ tests/
	isort --check-only src/ tests/

clean:  ## 一時ファイルを削除
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-venv:  ## 仮想環境を削除
	rm -rf venv/

docs:  ## ドキュメントを生成
	cd docs && make html

setup: install-dev  ## 開発環境をセットアップ（既存の仮想環境が有効な場合）
	@echo "開発環境のセットアップが完了しました"

check-venv:  ## 仮想環境が有効かチェック
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "警告: 仮想環境が有効になっていません。"; \
		echo "仮想環境を作成するには: make setup-venv"; \
		echo "既存の仮想環境を有効化するには: source venv/bin/activate"; \
		exit 1; \
	else \
		echo "仮想環境が有効です: $$VIRTUAL_ENV"; \
	fi

# MkDocs関連のターゲット

# MkDocsの依存関係をインストール
docs-install:
	pip install -r requirements-docs.txt

# ローカルでドキュメントを確認
docs-serve:
	mkdocs serve

# ドキュメントをビルド
docs-build:
	mkdocs build

# GitHub Pagesにデプロイ
docs-deploy:
	mkdocs gh-deploy

# ドキュメントのクリーンアップ
docs-clean:
	rm -rf site/
