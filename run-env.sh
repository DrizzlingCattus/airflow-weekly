#!/bin/bash

ENV_FILE=.env

source $ENV_FILE
export $(cut -d= -f1 $ENV_FILE)

# Global variables
AIRFLOW_HOME="/usr/local/airflow"
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=True
FERNET_KEY="46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho="
# encrypted data cannot be decrypted with new fernet key
#FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; FERNET_KEY = Fernet.generate_key().decode(); print(FERNET_KEY)")
AIRFLOW__CORE__FERNET_KEY="$FERNET_KEY"
PYTHONPATH=$AIRFLOW_HOME:$PYTHONPATH
# dialect+driver://username:password@host:port/database
AIRFLOW__CORE__SQL_ALCHEMY_CONN="mysql+mysqldb://${DB_USER}:${DB_PASSWORD}@${DB_HOSTNAME}:${DB_PORT}/${DB_DATABASE_NAME}${DB_EXTRAS}"

export \
  AIRFLOW_HOME \
  AIRFLOW__CORE__EXECUTOR \
  AIRFLOW__CORE__LOAD_EXAMPLES \
  FERNET_KEY \
  AIRFLOW__CORE__FERNET_KEY \
  PYTHONPATH \
  AIRFLOW__CORE__SQL_ALCHEMY_CONN \
  AIRFLOW_CONN_SERVICE_DB

cat docker-compose.yaml | envsubst | docker-compose -f - up -d --force-recreate
