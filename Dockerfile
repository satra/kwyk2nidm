FROM continuumio/miniconda3:4.7.12-alpine

WORKDIR /opt/kwyk2nidm
COPY . .

RUN /opt/conda/bin/pip install .

WORKDIR /data

ENTRYPOINT ["/opt/conda/bin/kwyk2nidm"]