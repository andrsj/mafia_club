include .env

.PHONY: stop up build run-migrations

stop:
	docker-compose down

build:
	docker-compose build

up:
	docker-compose up -d test_zlo_db

run-migrations:
	docker-compose up -d test_zlo_db
	sh migrations/run.sh
