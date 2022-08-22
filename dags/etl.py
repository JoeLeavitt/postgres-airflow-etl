import os
import pandas as pd

from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect
from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

CONFIG = dotenv_values(".env")
if not CONFIG:
    CONFIG = os.environ

DATASET_URL = "https://gist.githubusercontent.com/JoeLeavitt/f9d1e14e87f2ca41609b0af63fbab7af/raw/9fedfd46068bdf6ee62731da4cf08c56df7c4866/DATA.csv"

default_args = {
    "owner": "Airflow",
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    "start_date": days_ago(1)
}

def start_connection():
    print("Starting connection to Postgres Database")

    connection_uri = "postgresql+psycopg2://{}:{}@{}:{}".format(
        CONFIG["POSTGRES_USER"],
        CONFIG["POSTGRES_PASSWORD"],
        CONFIG["POSTGRES_HOST"],
        CONFIG["POSTGRES_PORT"],
    )

    engine = create_engine(connection_uri, pool_pre_ping=True)

    engine.connect()

    return engine

def extract(dataset_url):
    print(f"Querying data from {dataset_url}")

    df = pd.read_csv(dataset_url)

    return df

def transform(df):
    print("Performing simple transforms on the data")

    email_idx = df.columns.get_loc("email")
    email_domains = []

    # Cleanup Data
    df = df.drop_duplicates()

    for email in df['email']:
        slice_at = email.index('@') + 1
        email_domains.append(email[slice_at:])

    # Add Column For Email Domain
    df.insert(email_idx+1, "email_domain", email_domains, allow_duplicates=True)

    return df

def load(df, table_name, engine):
    print("Loading data into Postgres database (DATA table)")

    df.to_sql(table_name, engine, if_exists="replace")

def etl():
    engine = start_connection()

    # Extract
    raw_df = extract(DATASET_URL)

    # Transform
    transformed_df = transform(raw_df)

    # Load
    load(transformed_df, "DATA", engine)

    engine.dispose()

def check_table():
    engine = start_connection()

    print("Checking table in Postgres Database")

    if "DATA" in inspect(engine).get_table_names():
        print(f"SUCCESS! DATA table found in the Postgres database")

        engine.dispose()

        return True
    else:
        print(f"FAILURE! DATA table was not created")

        engine.dispose()

        return False

with DAG(dag_id="etl_pipeline", max_active_runs=1, default_args=default_args, catchup=False, schedule_interval=None) as dag:
    t1 = PythonOperator(task_id="etl_task", python_callable=etl)
    t2 = PythonOperator(task_id="check_table_task", python_callable=check_table)
    t3 = DummyOperator(task_id="generate_analytics_task")

    t1 >> t2 >> t3
