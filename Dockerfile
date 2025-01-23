FROM apache/airflow:2.10.4

USER root

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY setup.cfg /usr/local/airflow/setup.cfg
COPY pyproject.toml /usr/local/airflow/pyproject.toml

RUN chown -R airflow /usr/local/airflow

USER airflow

WORKDIR /usr/local/airflow
RUN pip install -e ".[dev]"
