# Stock Trading Agent Makefile
# Provides convenient commands for building and running the trading system

.PHONY: help build start stop restart logs test backtest docker-test status cleanup install

# Default target
help:
	@echo "Stock Trading Agent - Available Commands"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make build       - Build Docker image"
	@echo "  make start       - Start the application"
	@echo "  make stop        - Stop the application"
	@echo "  make restart     - Restart the application"
	@echo "  make logs        - View application logs"
	@echo "  make test        - Run tests in Docker"
	@echo "  make backtest    - Run backtesting in Docker"
	@echo "  make docker-test - Run Docker environment test"
	@echo "  make status      - Show application status"
	@echo "  make cleanup     - Clean up Docker resources"
	@echo ""
	@echo "Local Commands:"
	@echo "  make install     - Install dependencies locally"
	@echo "  make local-test  - Run tests locally"
	@echo "  make local-app   - Run web interface locally"
	@echo ""

# Docker commands
build:
	./docker-run.sh build

start:
	./docker-run.sh start

stop:
	./docker-run.sh stop

restart:
	./docker-run.sh restart

logs:
	./docker-run.sh logs

test:
	./docker-run.sh test

backtest:
	./docker-run.sh backtest

docker-test:
	./docker-run.sh docker-test

status:
	./docker-run.sh status

cleanup:
	./docker-run.sh cleanup

# Local commands
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

local-test:
	@echo "Running tests locally..."
	python test_system.py

local-app:
	@echo "Starting web interface locally..."
	streamlit run app.py

# Development commands
dev-setup: install
	@echo "Setting up development environment..."
	mkdir -p data logs
	@echo "Development environment ready!"

# Quick start
quick-start: build start
	@echo "Application started! Access at http://localhost:8501"

# Full test suite
test-all: local-test
	@echo "Running Docker tests..."
	./docker-run.sh docker-test
	@echo "All tests completed!" 