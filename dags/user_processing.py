from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.postgres.operators.postgres import PostgresOperator


with DAG(
        'user_processing',
        start_date=datetime(2024, 1, 1),
        schedule_interval='@daily',
        catchup=False) as dag:

    create_Table = PostgresOperator(
        task_id='create_Table',
        postgres_conn_id='postgres',
        sql='''
        create table if not exists users(
        firstname text not null,
        lastname text not null,
        country text not null,
        username text not null,
        password text not null,
        email text not null,
        );
        '''
    )