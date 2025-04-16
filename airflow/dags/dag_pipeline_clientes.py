from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import boto3

# Função para rodar os crawlers após o job Glue
def start_glue_crawlers():
    glue_client = boto3.client('glue', region_name='us-east-1')
    crawlers = ['etlproj-bronze-crawler', 'etlproj-silver-crawler']
    for crawler in crawlers:
        glue_client.start_crawler(Name=crawler)
        print(f"Crawler iniciado: {crawler}")

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'retries': 0
}

with DAG(
    dag_id='pipeline_clientes',
    default_args=default_args,
    max_active_runs=1,
    schedule_interval=None,
    description='Executa o ETL para o pipeline de clientes ',
    tags=["etl", "clientes"]
) as dag:

    iniciar_glue_pipeline_clientes = GlueJobOperator(
        task_id='iniciar_job_glue_clientes',
        job_name='pipeline_clientes',
        region_name='us-east-1',
        wait_for_completion=True,
        dag=dag
    )

    iniciar_crawlers = PythonOperator(
        task_id='iniciar_crawlers',
        python_callable=start_glue_crawlers
    )

    iniciar_glue_pipeline_dataquality = GlueJobOperator(
        task_id='iniciar_job_glue_dataquality',
        job_name='dataquality',
        region_name='us-east-1',
        wait_for_completion=True,
        dag=dag
    )

    iniciar_glue_pipeline_clientes >> iniciar_crawlers >> iniciar_glue_pipeline_dataquality