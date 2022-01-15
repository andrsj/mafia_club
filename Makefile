include .env

all: stop build up-test pause run-migrations
.PHONY: all

pause:
	sleep 3s

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
	sh src/dim_mafii/migrations/run.sh

unit-tests: 
	run-contexts src/dim_mafii/tests/unittests/

integretional-tests: 
	run-contexts src/dim_mafii/tests/integretional/

end-to-end-tests:
	run-contexts src/dim_mafii/tests/e2e/

run-all-tests:
	run-contexts src/dim_mafii/tests/unittests/
	run-contexts src/dim_mafii/tests/integretional/
	run-contexts src/dim_mafii/tests/e2e/

update-fixtures: 
	python src/dim_mafii/cli/create_fixtures_from_sheet.py --sheet ТестовийБланкНеДляПротоколуіРейтингу

blanks-check-for-errors: 
	python src/dim_mafii/cli/blanks_checker.py --month=$(month) --year=$(year)

blanks-create-or-update-players: 
	python src/dim_mafii/cli/create_or_update_players.py

blanks-get-all-nicknames:
	python src/dim_mafii/cli/get_all_nicknames_in_games.py --month=$(month) --year=$(year)

blanks-create-sheet-by-range:
	python src/dim_mafii/cli/generate_sheets.py --start=$(start) --end=$(end)

blanks-check-for-errors-by-month:
	python src/dim_mafii/cli/blanks_checker.py --month=$(month) --year=$(year)

blanks-check-for-errors-for-date:
	python src/dim_mafii/cli/blanks_checker.py --date=$(date)

blanks-check-for-errors-by-date-range:
	python src/dim_mafii/cli/blanks_checker.py --start=$(start) --end=$(end)

blanks-feel-games-month:
	python src/dim_mafii/cli/feel_games_blank_2.py --month=$(month) --year=$(year) --full

blanks-feel-games-range:
	python src/dim_mafii/cli/feel_games_blank_2.py --start=$(start) --end=$(end) --full

w_dump:
	cat $(name) | docker exec -i test_zlo_db psql -U test_zlo

r_dump:
	docker exec test_zlo_db pg_dumpall -U test_zlo > $(name)

ri_dump:
	docker exec test_zlo_db pg_dump --column-inserts --data-only test_zlo -U test_zlo > $(name)

db:
	docker exec -it test_zlo_db psql -U test_zlo
