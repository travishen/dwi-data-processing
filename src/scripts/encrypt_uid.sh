#! /bin/sh

LOG_FILE="$0.$$.log"

cat /dev/null > "$LOG_FILE" && chmod 777 "$LOG_FILE"

exec 1> "$LOG_FILE"

OUTPUT_DIR="/data/Encrypted/$(date +"%d-%m-%Y")"
VIOLATION_DIR="$OUTPUT_DIR/Violation"

mkdir -p "$VIOLATION_DIR"

python manage.py encrypt --table="accident" --file="/data/Accident_0701.xlsx" --output-dir="$OUTPUT_DIR"

for filename in /data/ObeyLaw0624/*.xlsx; do
  python manage.py encrypt --table="violation" --file="$filename" --output-dir="$VIOLATION_DIR"
done