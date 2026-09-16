# goit-pythonweb-hw-06

База даних PostgreSQL через SQLAlchemy + Alembic: студенти, групи,
викладачі, предмети та оцінки. Запити — у `my_select.py`
(`select_1` ... `select_10`).

## Запуск

Потрібні Docker і [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env          # 1. налаштування підключення
docker compose up -d --wait   # 2. Postgres у контейнері, до статусу healthy
uv sync                       # 3. залежності
uv run alembic upgrade head   # 4. створити таблиці (міграція)
uv run python seed.py         # 5. наповнити випадковими даними
uv run python my_select.py    # 6. виконати всі 10 вибірок
```

Значення в `.env.example` робочі, міняти нічого не потрібно.

Прибрати за собою: `docker compose down -v`.

## Якщо щось не так

**Некоректне кодування виводу (Windows).** Запускати з `PYTHONUTF8=1`:

```powershell
$env:PYTHONUTF8=1; uv run python my_select.py
```

**`database "HW_06" does not exist` після зміни `.env`.** `POSTGRES_USER`,
`POSTGRES_PASSWORD` і `POSTGRES_DB` застосовуються лише при першій
ініціалізації бази. Щоб зміни підхопились, базу треба перестворити:

```bash
docker compose down -v && docker compose up -d --wait
uv run alembic upgrade head && uv run python seed.py
```
