#!/usr/bin/env bash

# Imports
#. $(dirname "$0")/wait-for-it.sh

# Global variables
: "${AIRFLOW_HOME="/usr/local/airflow"}"
: "${AIRFLOW__CORE__EXECUTOR:=LocalExecutor}"
: "${AIRFLOW__CORE__LOAD_EXAMPLES=True}"

export \
  AIRFLOW_HOME \
  AIRFLOW__CORE__EXECUTOR \
  AIRFLOW__CORE__LOAD_EXAMPLES \
  #AIRFLOW__CORE__FERNET_KEY \

# Install custom python package if requirements.txt is present
if [ -e "/requirements.txt" ]; then
  $(command -v pip) install --user -r /requirements.txt
fi

# Setup mysql connection
if [ -z "$AIRFLOW__CORE__SQL_ALCHEMY_CONN" ]; then
  #: "${DB_HOST:="mysql"}"
  #: "${DB_PORT:="5432"}"
  #: "${DB_USER:="airflow"}"
  #: "${DB_PASSWORD:="airflow"}"
  #: "${DB_DATABASE_NAME:="airflow"}"
  #: "${DB_EXTRAS:-""}"

  # dialect+driver://username:password@host:port/database
  AIRFLOW__CORE__SQL_ALCHEMY_CONN="mysql+mysqldb://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_DATABASE_NAME}${DB_EXTRAS}"
  export AIRFLOW__CORE__SQL_ALCHEMY_CONN

  . $(dirname "$0")/wait-for-it.sh "${DB_HOST}:${DB_PORT}" -- echo "Mysql connection success!"
fi

# need to use getopts or smt
airflow initdb
airflow scheduler &
exec airflow webserver -p 8080
