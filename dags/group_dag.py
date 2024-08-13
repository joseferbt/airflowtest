from airflow import DAG
from airflow.operators.bash import BashOperator
from subdags.subdag_transforms import subdag_transforms
from subdags.downloads import downloads_task
from datetime import datetime

with DAG('group_dag', start_date=datetime(2022, 1, 1),
         schedule_interval='@daily', catchup=False) as dag:

    downloads = downloads_task()

    check_files = BashOperator(
        task_id='check_files',
        bash_command='sleep 10'
    )
    transform = subdag_transforms()
    downloads >> check_files >> transform