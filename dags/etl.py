import os

from functools import wraps

import pandas as pd

from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect


args = {"owner": "Airflow", "start_date": days_ago(1)}

dag = DAG(dag_id="etl", default_args=args, schedule_interval=None)

DATASET_URL = "https://gist.githubusercontent.com/JoeLeavitt/f9d1e14e87f2ca41609b0af63fbab7af/raw/9fedfd46068bdf6ee62731da4cf08c56df7c4866/DATA.csv"


CONFIG = dotenv_values(".env")
if not CONFIG:
    CONFIG = os.environ


def logger(fn):
    from datetime import datetime, timezone

    @wraps(fn)
    def inner(*args, **kwargs):
        called_at = datetime.now(timezone.utc)
        print(f">>> Running {fn.__name__!r} function. Logged at {called_at}")
        to_execute = fn(*args, **kwargs)
        print(f">>> Function: {fn.__name__!r} executed. Logged at {called_at}")
        return to_execute

    return inner


@logger
def connect_db():
    print("Connecting to DB")
    connection_uri = "postgresql+psycopg2://{}:{}@{}:{}".format(
        CONFIG["POSTGRES_USER"],
        CONFIG["POSTGRES_PASSWORD"],
        CONFIG["POSTGRES_HOST"],
        CONFIG["POSTGRES_PORT"],
    )

    engine = create_engine(connection_uri, pool_pre_ping=True)
    engine.connect()
    return engine


@logger
def extract(dataset_url):
    print(f"Reading dataset from {dataset_url}")
    df = pd.read_csv(dataset_url)
    return df


@logger
def transform(df):
    pass

@logger
def check_table_exists(table_name, engine):
    if table_name in inspect(engine).get_table_names():
        print(f"{table_name!r} exists in the DB!")
    else:
        print(f"{table_name} does not exist in the DB!")


@logger
def load_to_db(df, table_name, engine):
    print(f"Loading dataframe to DB on table: {table_name}")
    df.to_sql(table_name, engine, if_exists="replace")


@logger
def etl():
    db_engine = connect_db()

    raw_df = extract(DATASET_URL)
    raw_table_name = "raw_DATA"

    clean_df = transform(raw_df)
    clean_table_name = "clean_DATA"

    load_to_db(raw_df, raw_table_name, db_engine)
    load_to_db(clean_df, clean_table_name, db_engine)


@logger
def tables_exists():
    db_engine = connect_db()
    print("Checking if tables exists")
    check_table_exists("raw_DATA", db_engine)
    check_table_exists("clean_DATA", db_engine)

    db_engine.dispose()


with dag:
    run_etl_task = PythonOperator(task_id="run_etl_task", python_callable=etl)
    run_tables_exists_task = PythonOperator(
        task_id="run_tables_exists_task", python_callable=tables_exists)

    run_etl_task >> run_tables_exists_task
