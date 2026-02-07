ARG PG_VERSION=16
FROM timescale/timescaledb:latest-pg${PG_VERSION}

USER root

# Install pgvector dependencies and extension
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    postgresql-server-dev-${PG_VERSION} \
    dumb-init && \
    cd /tmp && \
    git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    cd .. && \
    rm -rf pgvector && \
    apt-get remove -y git build-essential postgresql-server-dev-${PG_VERSION} && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER postgres
