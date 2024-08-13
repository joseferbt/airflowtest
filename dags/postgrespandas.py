from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd
import re

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 13),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'postgres_csv_etl',
    default_args=default_args,
    description='ETL job to extract from Postgres and CSV, transform, and load to Postgres',
    schedule_interval=timedelta(days=1),
)

def extract_from_postgres(**kwargs):
    source_hook = PostgresHook(postgres_conn_id='source_postgres_conn')
    df = source_hook.get_pandas_df(sql="SELECT * FROM source_table")
    kwargs['ti'].xcom_push(key='postgres_data', value=df.to_dict())

def extract_from_csv(**kwargs):
    df = pd.read_csv('path/to/your/file.csv')
    kwargs['ti'].xcom_push(key='csv_data', value=df.to_dict())

    def transform_data(**kwargs):
        ti = kwargs['ti']
    postgres_data = pd.DataFrame(ti.xcom_pull(key='postgres_data', task_ids='extract_postgres'))
    csv_data = pd.DataFrame(ti.xcom_pull(key='csv_data', task_ids='extract_csv'))

    # Combine data
    combined_data = pd.concat([postgres_data, csv_data], ignore_index=True)

    # Text normalization
    combined_data['text_column'] = combined_data['text_column'].str.lower()

    # Clean data
    combined_data['text_column'] = combined_data['text_column'].apply(lambda x: re.sub(r'[^\w\s]', '', x))

    # Remove duplicates
    combined_data.drop_duplicates(inplace=True)

    # Handle missing values
    combined_data.fillna('Unknown', inplace=True)

    kwargs['ti'].xcom_push(key='transformed_data', value=combined_data.to_dict())

    def load_to_postgres(**kwargs):
        ti = kwargs['ti']
    transformed_data = pd.DataFrame(ti.xcom_pull(key='transformed_data', task_ids='transform_data'))

    target_hook = PostgresHook(postgres_conn_id='target_postgres_conn')
    target_hook.insert_rows(
        table='target_table',
        rows=transformed_data.values.tolist(),
        target_fields=transformed_data.columns.tolist()
    )