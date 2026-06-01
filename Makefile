.PHONY: up down test-unit test-api test-integration test-workflow test-all

up:
	docker-compose up -d --build

down:
	docker-compose down

test-unit:
	pytest tests/unit -v -m unit

test-api:
	pytest tests/api -v -m api

test-integration:
	pytest tests/integration -v -m integration

test-workflow:
	pytest tests/workflow -v -m workflow

test-all:
	pytest -v --html=report.html --self-contained-html
