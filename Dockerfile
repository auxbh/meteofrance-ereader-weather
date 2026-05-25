FROM python:3.12-slim

LABEL Description="A lightweight weather server for e-readers such as the Kindle that uses Méteo-France's API"

COPY requirements.txt /
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libcairo2 \
      libcairo2-dev \
      libffi-dev \
      libgdk-pixbuf-2.0-0 \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      fonts-dejavu-core && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential libcairo2-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY *.py /
COPY weather /weather
COPY static /static
COPY templates /templates

ENV GPS_COORDINATES=48.862137,2.346131
ENV CITY_NAME=
ENV BIND_PORT=8080
ENV TZ=Europe/Paris
ENV EREADER_WIDTH=758
ENV EREADER_HEIGHT=1024

CMD ["python", "/server.py"]
