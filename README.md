# postgres-airflow-etl
Provisions a PostgreSQL database and a simple Airflow environment for ETL pipelines

## Setup
To run this project, you should have Docker installed on your system and access to
`bash`.

_Note: The Airflow environment is memory-intensive; please ensure that you run the
containers on a system with at least 16GB of RAM. This system was successfully tested on
macOS and Windows systems with 16GB of memory. Also, Windows systems automatically manage
the amount of resources given to Docker. If using a different type of system, please check your
Docker resource settings to ensure that the requisite amount of memory is allocated; in my testing on an Intel-based macOS system, I had to allow Docker to utilize 15GB of memory._

Before running the pipeline, you'll need to set up a few environment variables and export them into your shell. Here is an example of
what's required:
```sh
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=...
POSTGRES_PORT=...
AIRFLOW_UID=...
AIRFLOW_GID=...
```

You'll also need to create directories for logs and plugins for Airflow to properly work. Finally,
a docker network needs to be created to function as a bridge between the external Postgres and
the Airflow system. A convenience script has been created to automate this entire process; it can
be found in `setup.sh`.

Run the script using the following command:
```sh
bash setup.sh
```

To setup the external Postgres database, run the following command:
```sh
docker-compose -f postgres-docker-compose.yaml up -d
```

After that, the Airflow metadata database needs to be initialized:
```sh
docker-compose -f airflow-docker-compose.yaml up airflow-init
```

Finally, you can start all of the Airflow services by running the following command:
```sh
docker-compose -f airflow-docker-compose.yaml up -d
```

## Running the Pipeline
Before running the pipeline wait until all the Airflow containers are in a healthy state, you can check this by
running `docker ps` and looking at the STATUS column. All columns should read "healthy".

To run the pipeline, you'll need to log in to the Airflow interface by navigating to
http://localhost:8080. The username is `airflow` and the password is `airflow`. You
should see a list with one DAG called `etl_pipeline`. This pipeline pulls the
provided data from an external source, applies several transformations, and finally loads it into the external Postgres database as a single table. In its initial state,
the DAG will be off. To turn it on, click the toggle switch to unpause the DAG. 

The DAG is now ready to be manually executed. To do so, click the play button on the
end of the row and choose "Trigger DAG". The task is now running, and you can refresh 
the page to see an indication of its progress. Wait about 10 seconds (in my testing, 
the DAG finished nearly instantly) and refresh the page. Click the green outlined circle in 
the `Runs` column and select the graph view of the DAG. You can also click each node 
in the DAG to view the task logs and details.

During my testing, I created a Jupyter notebook. If you would like to view the
notebook files, they are provided under the `notebooks` directory.

## Removal
It's good practice to remove unused Docker containers and networks as the images
may take up a lot of space over time. To remove containers and networks that are
unreferenced by other parts of the project, you can run `docker system prune`. If
you want to remove _all_ unused containers and networks, you can run `docker system prune --all`; Docker will show you the following prompt to ensure that you understand the functionality of the `--all` flag.
```sh
WARNING! This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all images without at least one container associated to them
  - all build cache
```

A full removal of all associated components of this project would look like the following:
```sh
docker-compose -f airflow-docker-compose.yaml down --volumes --rmi all
docker-compose -f postgres-docker-compose.yaml down --volumes --rmi all
docker system prune --all
```
