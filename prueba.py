import textwrap
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
with DAG(
    "tutorial",
    default_args = {
        "depends_on_past": False,
        "email": ["joseferbt@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),  # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    },
    description = "Tutorial DAG",
    schedule= timedelta(minutes=5),
    start_date= datetime(2024, 8 , 11),
    catchup = False,
    tags = ["exmaple"]
) as dag :
    t1 = BashOperator(
        task_id = "printdate",
        bash_command = "date",
    )
    t2 = BashOperator(
        task_id = "sleep",
        depends_on_past = False,
        bash_command = "sleep 5",
        retries = 3,
    )
    templeted_command = textwrap.dedent(
        """
        {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds,7) }}"
        {% endfor %}
        """
    )
    t3 = BashOperator(
        task_id = "templated",
        depends_on_past = False,
        bash_command = templeted_command,
    )
    t1.doc_md = textwrap.dedent(
        """\
    #### Task Documentation
    You can document your task using the attributes `doc_md` (markdown),
    `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
    rendered in the UI's Task Instance Details page.
    ![img](https://imgs.xkcd.com/comics/fixing_problems.png)
    **Image Credit:** Randall Munroe, [XKCD](https://xkcd.com/license.html)
    """
    )

dag.doc_md = __doc__  # providing that you have a docstring at the beginning of the DAG; OR
dag.doc_md = """
This is a documentation placed anywhere
"""
t1 >> [t2,t3]