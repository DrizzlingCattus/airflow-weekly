import json
import logging
import requests

from datetime import timedelta, date

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from crawler_app.settings import (
    PROJECT_NAME, 
    DB_DATABASE,
    HACKERNEWS_DB_CONNECTION_ID)
from crawler_app.db import (
    get_maxtask_id,
    setup_db)
from crawler_app.request import get_maxitem_num, get_item_info


MAX_PROCESS_NUM = 10

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

logger = logging.getLogger(__name__)

dag = DAG(
    f'{PROJECT_NAME}.task_factory',
    default_args=default_args,
    description='A simple crawler',
    schedule_interval='@once',
)

def print_date(**kwargs):
    today = date.today()
    logger.info(f'{PROJECT_NAME} DAG start running at {today}.')
    #kwargs['task_instance'].xcom_push(key='print', value='asdf')
    return today

t1 = PythonOperator(
    task_id='print_date',
    python_callable=print_date,
    # kwargs로 넘겨줌. task_instance도 포함.
    provide_context=True,
    dag=dag,
)

def watch_hackernews_items(conn_id):
    max_num = get_maxitem_num()

    dal = setup_db(conn_id)
    conn = dal.connection

    curr_num = get_maxtask_id(conn) + 1

    logger.info(f'max item: {max_num} & curr item: {curr_num}')

    if max_num <= curr_num:
        return True 

    for i in range(MAX_PROCESS_NUM):
        info = get_item_info(curr_num + i)

        logger.info('info is {info}'.format(info=json.dumps(info)))

        if info is None:
            continue

        resource_id = dal.create_resource(url=info['url'], resource_type=info['type'])
        dal.create_task(resource_id)
    dal.close()

    return True

t2 = PythonOperator(
    task_id='watch_hackernews_items',
    python_callable=watch_hackernews_items,
    op_kwargs={
        'conn_id': HACKERNEWS_DB_CONNECTION_ID,
    },
    dag=dag,
)

t1 >> t2
