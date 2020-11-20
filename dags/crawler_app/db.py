from sqlalchemy import create_engine, text
from airflow.models.baseoperator import BaseOperator
from airflow.hooks.mysql_hook import MySqlHook
from airflow.utils.decorators import apply_defaults




def setup_db(conn_id, schema):

    print('input', conn_id, schema)
    hook = MySqlHook(mysql_conn_id=conn_id, schema=schema)
    uri = hook.get_uri()
    print('uri', uri)

