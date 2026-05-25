# meteofrance-ereader-weather

A lightweight weather server for e-readers such as the Kindle that uses [Météo-France](https://meteofrance.com/)'s API

This repository is based on https://github.com/gadget1999/rpi-docker/tree/master/nook-weather

The icons are provided by Météo-France

<img src=".github/img/ereader_image.png" height="300px">

## Features

- Serves weather information to e-reader-friendly displays
- Uses `GPS_COORDINATES` for location
- Easy Docker deployment

## Environment variables

- `GPS_COORDINATES`: latitude,longitude (default: `48.862137,2.346131`; Paris)
- `EREADER_WIDTH`: output image width in pixels (default: `758`)
- `EREADER_HEIGHT`: output image height in pixels (default: `1024`)

## Endpoints

- `http://<ip>/forecast`: HTML weather forecast page
- `http://<ip>/ereader_image`: generated image for e-reader display

## Run with Docker

With Docker run

```sh
docker run -d -p 8080:8080 \
  -e GPS_COORDINATES=48.862137,2.3461315 \
  -e EREADER_WIDTH=758 \
  -e EREADER_HEIGHT=1024 \
  ghcr.io/auxbh/meteofrance-ereader-weather:main
```

With Docker compose

```sh
services:
  nmeteofrance-ereader-weather:
    image: ghcr.io/auxbh/meteofrance-ereader-weather:main
    container_name: meteofrance-ereader-weather
    restart: unless-stopped

    environment:
      GPS_COORDINATES: 48.862137,2.3461315
      EREADER_WIDTH: 758
      EREADER_HEIGHT: 1024

    ports:
      - "8080:8080"
```

## Local build for developping

Build with Docker

```sh
docker build -t meteofrance-ereader-weather .
```

Run the image
```sh
docker run -d -p 8080:8080 \
  -e GPS_COORDINATES=48.862137,2.3461315 \
  meteofrance-ereader-weather
```
