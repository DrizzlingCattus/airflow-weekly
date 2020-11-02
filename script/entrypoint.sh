#!/usr/bin/env bash

# Imports
#. $(dirname "$0")/wait-for-it.sh

# Install custom python package if requirements.txt is present
if [ -e "/requirements.txt" ]; then
  $(command -v pip) install --user -r /requirements.txt
fi

TRY_LOOP="20"
wait_for_port() {
  local name="$1" host="$2" port="$3"
  local j=0
  while ! nc -z "$host" "$port" >/dev/null 2>&1 < /dev/null; do
    j=$((j+1))
    if [ $j -ge $TRY_LOOP ]; then
      echo >&2 "$(date) - $host:$port still not reachable, giving up"
      exit 1
    fi
    echo "$(date) - waiting for $name... $j/$TRY_LOOP"
    sleep 5
  done
}

# Setup mysql connection
if [ -n "$AIRFLOW__CORE__SQL_ALCHEMY_CONN" ]; then
  echo "Starting to wait for it"
  wait_for_port "MariaDB" "${DB_HOSTNAME}" "${DB_PORT}"
fi

case "$1" in
  local)
    echo "Local mode start!"
    airflow initdb
    airflow scheduler &
    exec airflow webserver -p 8080
    ;;
  *)
    echo "Not valid option"
    ;;
esac
