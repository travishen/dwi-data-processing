#! /bin/sh

LOG_FILE="$0.$$.log"

cat /dev/null > "$LOG_FILE" && chmod 777 "$LOG_FILE"

exec 1> "$LOG_FILE"

python manage.py load --table="accident" --file="/data/Accident_0701.xlsx"