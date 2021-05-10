#! /bin/sh

LOG_FILE="$0.$$.log"

cat /dev/null > "$LOG_FILE" && chmod 777 "$LOG_FILE"

exec 1> "$LOG_FILE"

for filename in /data/ObeyLaw0624/*.xlsx; do
  python manage.py load --table="violation" --file="$filename"
done