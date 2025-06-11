.PHONY: help install install-dev test lint format clean build upload docs
.DEFAULT_GOAL := help

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## 安装包
	pip install -e .

install-dev: ## 安装开发依赖
	pip install -e .[dev,test,gui]
	pre-commit install

test: ## 运行测试
	pytest

test-cov: ## 运行测试并生成覆盖率报告
	pytest --cov=yoloobb_converter --cov-report=html --cov-report=term

lint: ## 代码检查
	flake8 yoloobb_converter/
	mypy yoloobb_converter/

format: ## 格式化代码
	black yoloobb_converter/ tests/
	isort yoloobb_converter/ tests/

format-check: ## 检查代码格式
	black --check yoloobb_converter/ tests/
	isort --check-only yoloobb_converter/ tests/

clean: ## 清理构建文件
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## 构建包
	python -m build

upload-test: build ## 上传到测试PyPI
	python -m twine upload --repository testpypi dist/*

upload: build ## 上传到PyPI
	python -m twine upload dist/*

docs: ## 生成文档
	@echo "正在生成文档..."
	@echo "项目文档位于 README.md"

gui: ## 启动GUI
	python -m yoloobb_converter.gui.main_window

cli: ## 启动CLI
	python -m yoloobb_converter.cli.main

demo: ## 运行演示
	@echo "启动GUI演示..."
	$(MAKE) gui

check: format-check lint test ## 运行所有检查

setup-dev: install-dev ## 设置开发环境
	@echo "开发环境设置完成！"
	@echo "可用命令："
	@echo "  make test     - 运行测试"
	@echo "  make lint     - 代码检查"
	@echo "  make format   - 格式化代码"
	@echo "  make gui      - 启动GUI"
	@echo "  make cli      - 启动CLI" 