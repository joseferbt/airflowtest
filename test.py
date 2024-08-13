from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
with DAG(
        'postgres_etl',
        start_date=datetime(2023, 1, 1),
        schedule_interval='@daily',
        catchup=False
) as dag:
    def extract_data(**kwargs):
        df = pd.read_csv('your_data.csv')
        return df.to_dict('records')

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data
    )

    def transform_data(**kwargs):
        data = kwargs['ti'].xcom_pull(task_ids='extract_data')
        # Perform transformations on the data
        # For example:
        for row in data:
        # Modify row as needed
        return data

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )
    def load_data(**kwargs):
        data = kwargs['ti'].xcom_pull(task_ids='transform_data')
        conn = psycopg2.connect(
            dbname="your_database",
            user="your_user",
            password="your_password",
            host="your_host",
            port="your_port"
        )
        cur = conn.cursor()
        # Insert data into PostgreSQL table
        for row in data:
            # Construct SQL INSERT statement
            cur.execute(insert_sql, row)
        conn.commit()
        cur.close()
        conn.close()

    load_task = PostgresOperator(
        task_id='load_data',
        postgres_conn_id='your_postgres_conn',
        sql="INSERT INTO your_table (column1, column2, ...) VALUES (%s, %s, ...)",
        parameters=data
    )
    extract_task >> transform_task >> load_task
