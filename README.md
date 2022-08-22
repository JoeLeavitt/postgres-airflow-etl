# postgres-airflow-etl
Provisions a PostgreSQL database and a simple Airflow environment for ETL pipelines

### Setup Postgres and Airflow environment
```
bash setup.sh
```

### Give Airflow Full Access To Airflow Specific Directories
```
chmod -R 777 ./dags ./logs ./plugins
```

### Start External Postgres Database
```
docker-compose -f postgres-docker-compose.yaml up -d
```

### Intialize Airflow Metadata Database
```
docker-compose -f airflow-docker-compose.yaml up airflow-init
```

### Start All Airflow Services
```
docker-compose -f airflow-docker-compose.yaml up -d
```

### Wait For All Services To Be In A Healthy State
```docker ps```

Webserver available at: ```http://localhost:8080```

### Shut Everything Down
```
docker-compose -f airflow-docker-compose.yaml down
docker-compose -f postgres-docker-compose.yaml down
```

### Full Removal
```
docker-compose -f airflow-docker-compose.yaml down --volumes --rmi all
docker-compose -f postgres-docker-compose.yaml down --volumes --rmi all
docker network rm etl_network
docker system prune -a
```

### Retrieve Jupyter URL With Access Token
```
docker logs $(docker ps -q --filter "ancestor=jupyter/minimal-notebook") 2>&1 | grep 'http://127.0.0.1' | tail -1
```
