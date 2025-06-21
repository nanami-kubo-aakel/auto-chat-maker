.PHONY: help install install-dev test lint format clean docs

help:  ## このヘルプメッセージを表示
	@echo "利用可能なコマンド:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 依存関係をインストール
	pip install -r requirements.txt

install-dev:  ## 開発用依存関係をインストール
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

docs:  ## ドキュメントを生成
	cd docs && make html

setup: install-dev  ## 開発環境をセットアップ
	@echo "開発環境のセットアップが完了しました" 