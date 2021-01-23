import logging
import uuid
from enum import Enum

import sqlalchemy
from sqlalchemy import (
    Table, Column, Integer, 
    String, MetaData, ForeignKey,
    create_engine, text)
from airflow.models.baseoperator import BaseOperator
from airflow.hooks.mysql_hook import MySqlHook
from airflow.utils.decorators import apply_defaults


logger = logging.getLogger(__name__)

# resources
SQL_QUERY_CREATE_RESOURCE='INSERT INTO resources (url, type) values ("%s", "%s");'

# tasks
SQL_QUERY_CREATE_TASK='INSERT INTO tasks (hash, state, resource_id) VALUES ("%s", "%s", %d);'
SQL_QUERY_UPDATE_TASK_STATUE='UPDATE tasks SET state="%s" WHERE hash=%s;'
SQL_QUERY_MAX_TASK_ID='select max(id) from tasks;'

# task state
TASK_STATE_PENDING='PENDING'
TASK_STATE=[TASK_STATE_PENDING, 'RUNNING', 'SUCCESS', 'FAILED', 'TERMINATED']

TABLE_NAMES=['tasks', 'resources', 'resource_histories']


class DataAccessLayer:
    connection = None
    engine = None
    conn_string = None
    metadata = MetaData()

    def db_init(self, conn_string: str):
        self.engine = create_engine(conn_string)
        self.conn_string = conn_string

        self.tasks = Table('tasks', self.metadata, autoload=True, autoload_with=self.engine)
        self.resources = Table('resources', self.metadata, autoload=True, autoload_with=self.engine)
        self.resource_histories = Table('resource_histories', self.metadata, autoload=True, autoload_with=self.engine)

        self.metadata.create_all(self.engine) # create all tables enrolled in metadata
        self.connection = self.engine.connect()
        
        logger.info('DB setup success with sqlalchemy {version}'.format(version=sqlalchemy.__version__))

        return self

    def create_resource(self, url: str, resource_type: str):
        insert_exp = self.resources.insert().values(url=url, type=resource_type)
        try:
            result = self.connection.execute(insert_exp)
        except Exception as e:
            logger.info(f'fail to create resource {e}')

        new_resource_id = result.inserted_primary_key[0]
        logger.info('create resource with result id {rid}'.format(rid=new_resource_id))
        return new_resource_id

    def create_task(self, resource_id):
        sql = SQL_QUERY_CREATE_TASK % (uuid.uuid4(), TASK_STATE_PENDING, resource_id)
        try:
            result = self.connection.execute(text(sql))
        except Exception as err:
            logger.info(err)

        return result

    def close(self):
        self.connection.close()


def update_task(conn, hash_id, state):
    sql = SQL_QUERY_UPDATE_TASK_STATUE % (hash_id)
    try:
        result = conn.execute(text(sql))
    except Exception as err:
        logger.info(err)

def get_maxtask_id(conn):
    sql = SQL_QUERY_MAX_TASK_ID
    try:
        result = conn.execute(text(sql))
    except Exception as err:
        logger.info(err)
    row = result.fetchone()
    max_id = row[0]
    if max_id == None:
        return -1
    return max_id

def setup_db(conn_id):
    logger.info(f'mysql connection id : {conn_id}')

    # get credentials
    hook = MySqlHook(mysql_conn_id=conn_id, schema='crawler')
    uri = hook.get_uri()
    
    logger.info(f'uri {uri}')

    dal = DataAccessLayer()
    return dal.db_init(uri)
