include .env

.PHONY: stop up build run-migrations

stop:
	docker-compose down

build:
	docker-compose build

up:
	docker-compose up -d zlodb

run-migrations:
	docker-compose up -d zlodb
	sh migrations/run.sh
