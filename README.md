# Інтерфейс для введення ігор

## [Copy of spreadsheet](https://docs.google.com/spreadsheets/d/1TSmU7pTWiW-TxgCs0RWqbOdI5VhRVC5Wtde2KQ79-xU/edit#gid=1765678933)

### Перший запуск роботи інтерфейсу
0. `$: python3 -m venv <env>; source <env>/bin/activate` (Virtual Environment)
1. `$: pip install -r requirements.txt; pip install -e src` (Встановлення локальних і трьохсторонніх бібліотек)
2. Записати **credentials** для GoogleAPI в `src/dim_mafii/credentials/***.json`
3. `$: make up-test` (Запуск бази (Не дивуємося що це тестова база))
4. `$: make run-migrations` (Запуск міграцій тестової бази даних)
5. `$: docker exec -it test_zlo_db psql -U test_zlo` (Прямий доступ до БД, можна і через локальний клієнт `psql`)
6. `make blanks-create-or-update-players` (Записати гравців в БД з бланку гравців)
7. Done, можна продовжувати роботу з скриптами (Всі скрипти в директорії `src/dim_mafii/cli`)

### CLI scripts які записані в `makefile`
- `make update-fixtures` - Оновити фікстури для unit-tests
- `make blanks-check-for-errors month=** year=**` - Перевірити бланк на місяць і рік (Alias для `by-month`):\
Рік - чотирьохзначне число (`year=2021`)\
Місяць - україньска назва (Для прикладу: `month=Січень`)
- `make blanks-create-or-update-players` - записати (оновити) таблицю з гравцями
- `make blanks-create-sheet-by-range start=** end=**` - створити бланки від початкової дати до кінцевої\
Дата вказується в тому форматі, яка зазначена в конфігурації (`src/dim_mafii/domain/config.py`)\
Для прикладу: `start=01_01_1999` якщо `DATE_FORMAT = "%d_%m_%Y"`
- `make blanks-check-for-errors-by-month month=** year=**` - Перевірити бланки в межі одного місяця
- `make blanks-check-for-errors-for-date date=**` - Перевірити бланки за датою
- `make blanks-check-for-errors-by-date-range` - Перевірити бланки в межах дат
- *`make blanks-feel-games-month month=** year=**` - Записати ігри в базу в межах одного місяця
- *`make blanks-feel-games-range start=** end=**` - Записати ігри в базу в межах двох дат  

---

*(Need to fix: поправити перевірку і змінити або правило перевірки клубу гри, або назви клубів)

### Скрипти, що НЕ записані в `makefile`
- *`cli/calculate_mmr.py` - Стара версія скрипта обрахування MMR (Можливо ще знадобиться, але малоймовірно)
- `cli/calculate_mme2.py` - Обрахувати рейтинг MMR в csv file, що в ньому вказаний\
(Невеличке уточнення, деякі змінні поки що ЗАХАРДКОДЖЕННІ (`start, end, clubname, filename`)\
`clubname` - фільтрація ігор по клубах (Рейтингова|Школа), \
`filename` - назва CSV file\
`start | end` - початкова і кінцева дата фільтрації ЗАПИСАНИХ ігор)
- *`cli/calculate_rating.py` - Статистика ігор - [Spreadsheet](https://docs.google.com/spreadsheets/d/1xmkkaNULRmD6pJeB6kdz_SPEOi76DrIFirP4fou1k5Y/edit#gid=1696394479)
- *`cli/feel_games_and_houses.py` - Дуже старий скрипт запису ігор для старого формату бланків
- *`cli/fix_name_club.py` - Зміна назви клубів (Не актуальний, так як назви клубів записані в міграціях)
- *`cli/generate_statistic` - Стара версія статистики (Не актуально)
- *`cli/get_all_nicknames_in_games.py` - Отримати список всіх гравців, що ГРАЛИ в іграх в конкретному місяці - [Spreadsheet](https://docs.google.com/spreadsheets/d/1LlgeZ8AmgRIV-WN9qjwT-q3k4FtwoVKigy5islO6BjA/edit#gid=1773681275)
- *`cli/list_last_year_players.py` - Отримати список гравців, які грали в ігри на протязі останнього року
- `cli/save_players_to_json.py` - Зберегти гравців в `dim_mafii/tests/fixtures/players.json`
- `cli/setup_end_for_test.py` - Тимчасовий код для використання тестової бази
- `cli/show_game.py` - Демонстрація усієї гри в консоль

---

*(Вже не актуально або це був тимчасовий скрипт, можливо потім буде використовуватися)

