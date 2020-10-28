from datetime import timedelta, date

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.models.baseoperator import BaseOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.mysql_hook import MySqlHook
from airflow.utils.dates import days_ago
from airflow.utils.decorators import apply_defaults
import requests

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

dag = DAG(
    'crawler',
    default_args=default_args,
    description='A simple crawler',
    schedule_interval='@once',
)

def print_date(**kwargs):
    today = date.today()
    #kwargs['task_instance'].xcom_push(key='print', value='asdf')
    return today
    

starter = DummyOperator(
    task_id='starting',
    dag=dag,
)

t1 = PythonOperator(
    task_id='print_date',
    python_callable=print_date,
    # kwargs로 넘겨줌. task_instance도 포함.
    provide_context=True,
    dag=dag,
)

t2 = BashOperator(
    task_id='sleep',
    depends_on_past=False,
    bash_command='sleep 5',
    retries=3,
    dag=dag,
)

def test_hackernews(**kwargs):
    #today = kwargs['task_instance'].xcom_pull(task_ids='print_date')
    url = 'https://hacker-news.firebaseio.com/v0/item/8863.json?print=pretty'
    response = requests.get(url)
    body = response.json()
    print('hacker news', body)

t3 = PythonOperator(
    task_id='test_hackernews_api',
    python_callable=test_hackernews,
    provide_context=True,
    dag=dag,
)

class HelloDBOperator(BaseOperator):

    # default 값을 인자 넣어줌
    @apply_defaults
    def __init__(
        self,
        name: str,
        mysql_conn_id: str, # airflow's connection id
        database: str,
        *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self.mysql_conn_id = mysql_conn_id
        self.database = database

    def execute(self, context):
        hook = MySqlHook(mysql_conn_id=self.mysql_conn_id,
                         schema=self.database)
        sql = "select event from log"
        result = hook.get_first(sql)
        print(result)
        return 'ok' 

t4 = HelloDBOperator(
    task_id='mysql_conn_test',
    name='mysql_conn_test',
    mysql_conn_id='airflow_db',
    database='airflow',
    dag=dag)

starter >> t1 >> [t2, t3, t4]


