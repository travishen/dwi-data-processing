#! /bin/sh

LOG_FILE="$0.$$.log"

cat /dev/null > "$LOG_FILE" && chmod 777 "$LOG_FILE"

exec 1> "$LOG_FILE"

python manage.py load --table="country_town" --file="/data/02_old_r.xlsx"