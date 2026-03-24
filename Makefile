.PHONY: install dev ui test coverage lint clean help setup start

help:
	@echo "可用命令:"
	@echo "  make install    - 安装依赖"
	@echo "  make start      - 同时启动后端和前端（推荐）"
	@echo "  make dev        - 开发模式启动 FastAPI 后端"
	@echo "  make ui         - 启动 Streamlit 前端"
	@echo "  make test       - 运行测试"
	@echo "  make coverage   - 运行覆盖率报告"
	@echo "  make lint       - 代码检查"
	@echo "  make clean      - 清理缓存"
	@echo "  make setup      - 初始化数据目录"

install:
	pip install -r requirements.txt

start:
	@echo "启动 FastAPI 后端 (http://localhost:8000)..."
	@echo "启动 Streamlit 前端 (http://localhost:8501)..."
	@echo ""
	@echo "API 文档: http://localhost:8000/docs"
	@echo "Web UI:   http://localhost:8501"
	@echo ""
	@echo "按 Ctrl+C 停止所有服务"
	@echo ""
	make dev & make ui

dev:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

ui:
	streamlit run ui/app.py --server.fileWatcherType poll --server.port 8501

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	ruff check src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .ruff_cache

setup:
	python scripts/setup.py
