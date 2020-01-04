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

run-acceptance-tests
    docker-compose up -d test_zlo_db
    sh migrations/run.sh
    docker-compose down test_zlo_db
    docker-compose rm test_zlo_db