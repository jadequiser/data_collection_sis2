from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)


from src.scraper import run_scraper
from src.cleaner import run_cleaner
from src.loader import run_loader

default_args = {
    'owner': 'ganiya',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'airbnb_project_dag',
    default_args=default_args,
    description='Pipeline: Scrape Airbnb -> Clean -> Load DB',
    schedule='@daily',  
    start_date=datetime(2023, 12, 1),
    catchup=False,
    tags=['project'],
) as dag:

    t1_scrape = PythonOperator(
        task_id='scrape_data',
        python_callable=run_scraper
    )

    t2_clean = PythonOperator(
        task_id='clean_data',
        python_callable=run_cleaner
    )

    t3_load = PythonOperator(
        task_id='load_to_sqlite',
        python_callable=run_loader
    )

    t1_scrape >> t2_clean >> t3_load