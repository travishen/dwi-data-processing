#! /bin/sh

LOG_FILE="$0.$$.log"

cat /dev/null > "$LOG_FILE" && chmod 777 "$LOG_FILE"

exec 1> "$LOG_FILE"

python << END
from app.database import utils
with utils.session_scope() as s:
  s.execute("TRUNCATE TABLE divorce;")
  s.execute("TRUNCATE TABLE old;")
  s.execute("TRUNCATE TABLE indigenous;")
  s.execute("TRUNCATE TABLE education;")
  s.execute("TRUNCATE TABLE income_mid;")
  s.execute("TRUNCATE TABLE income_avg;")
END

python manage.py load --table="divorce" --file="/data/01_divorce_r.xlsx"
python manage.py load --table="old" --file="/data/02_old_r.xlsx"
python manage.py load --table="indigenous" --file="/data/03_Indgnus_r.xlsx"
python manage.py load --table="education" --file="/data/04_highedu_r.xlsx"
python manage.py load --table="income_mid" --file="/data/05_income_r.xlsx"
python manage.py load --table="income_avg" --file="/data/05_income_r.xlsx" --sheet=1
