include .env

.PHONY: stop up build run-migrations

stop:
	docker-compose down

build:
	docker-compose build

up-test:
	docker-compose up -d test_zlo_db

up-prod:
	docker-compose up -d zlodb

run-migrations:
	docker-compose up -d test_zlo_db
	sh src/zlo/migrations/run.sh

unit-tests:
	run-contexts src/zlo/tests/unittests/

integretional-tests:
	run-contexts src/zlo/tests/integretional/

run-all-tests:
	run-contexts src/zlo/tests/unittests/
	run-contexts src/zlo/tests/integretional/

update-fixtures:
	python src/zlo/cli/create_fixtures_from_sheet.py --sheet ТестовийБланкНеДляПротоколуІРейтингу

blanks-check-for-errors:
	python src/zlo/cli/blanks_checker.py --month=$(month) --year=$(year)

blanks-create-or-update-players:
	python src/zlo/cli/create_or_update_players.py

blanks-feel-games:
	python ~/guiding/src/zlo/cli/feel_games_blank_2.py --month=$(month) --year=$(year)