# postgres-airflow-etl
Provisions a PostgreSQL database and a simple Airflow environment for ETL pipelines

### Create .env file
```
cat << EOF > .env
POSTGRES_DB=winequality
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=database
POSTGRES_PORT=5432
EOF
```

### Install yq
https://mikefarah.gitbook.io/yq/v/v3.x/

Mac/Linux: ```brew install yq@3```

Windows: ```choco install yq```

### Create docker network
```
source .env
NETWORK_NAME=$(yq eval '.networks' postgres-docker-compose.yaml | cut -f 1 -d':')
docker network create $NETWORK_NAME
```

### Start external Postgres DB
```
docker-compose -f ./postgres-docker-compose.yaml up -d
```

### Retrieve Jupyter url with access token
```
docker logs $(docker ps -q --filter "ancestor=jupyter/minimal-notebook") 2>&1 | grep 'http://127.0.0.1' | tail -1
```

### Setup Airflow
```
mkdir ./logs ./plugins
chmod -R 777 ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
```

### Intialize Airflow Metadata Database
```
docker-compose -f airflow-docker-compose.yaml up airflow-init
```

### Start All Airflow Services
```
docker-compose -f airflow-docker-compose.yaml up -d
```

###
Webserver available at: ```http://localhost:8080```

### Shut Everything Down
```
docker-compose -f airflow-docker-compose.yaml down
docker-compose -f postgres-docker-compose.yaml down
```
