from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import boto3

# Função para iniciar o job Glue
def start_glue_job(job_name):
    glue_client = boto3.client('glue', region_name='us-east-1')
    response = glue_client.start_job_run(JobName=job_name)
    print(f"Job iniciado com ID: {response['JobRunId']}")

# Função para rodar crawlers após o job
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
    description='Executa o ETL para o pipeline de clientes',
    tags=["etl", "clientes"]
) as dag:

    iniciar_glue_pipeline_clientes = PythonOperator(
        task_id='iniciar_job_glue',
        python_callable=start_glue_job,
        op_args=['pipeline_clientes']
    )

    iniciar_crawlers = PythonOperator(
        task_id='iniciar_crawlers',
        python_callable=start_glue_crawlers
    )

    iniciar_glue_pipeline_dataquality = PythonOperator(
        task_id='iniciar_job_glue_dataquality',
        python_callable=start_glue_job,
        op_args=['dataquality']
    )

    # Ordem de execução: primeiro o Glue Job, depois os Crawlers, depois o job de Data Quality
    iniciar_glue_pipeline_clientes >> iniciar_crawlers >> iniciar_glue_pipeline_dataquality