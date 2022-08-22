#!/bin/bash

if [ ! -f ./.env ]; then
    echo "Creating Environment File"

    echo -e "POSTGRES_DB=DATA\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD=postgres\nPOSTGRES_HOST=database\nPOSTGRES_PORT=5432" >> .env

    echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" >> .env
fi

if [ ! -d ./logs ]; then
    echo "Creating Logs Directory For Airflow"
    mkdir ./logs
fi

if [ ! -d ./plugins ]; then
    echo "Creating Plugins Directory For Airflow"
    mkdir ./plugins
fi

sleep 1

docker network ls|grep airflow_network > /dev/null || docker network create airflow_network && echo "Created Docker Network"

sleep 1

source .env
