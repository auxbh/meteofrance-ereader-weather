#!/usr/bin/env python

import time
from threading import RLock

from .MeteoFrance import MeteoFranceAPI

import logging

logger = logging.getLogger()


class WeatherForecast:
    __api_provider = None
    __lock = RLock()
    __last_request_time = {}
    __last_forecast_data = {}

    @staticmethod
    def init():
        WeatherForecast.__api_provider = MeteoFranceAPI()

    @staticmethod
    def get_forecast(lat, lon):
        try:
            WeatherForecast.__lock.acquire()
            request_key = f"{lat},{lon}"
            last_request_time = (
                WeatherForecast.__last_request_time[request_key]
                if request_key in WeatherForecast.__last_request_time
                else time.localtime(0)
            )
            timestamp = time.localtime()
            if time.mktime(timestamp) - time.mktime(last_request_time) < 60:
                if request_key in WeatherForecast.__last_forecast_data:
                    return WeatherForecast.__last_forecast_data[request_key]

            if not WeatherForecast.__api_provider:
                WeatherForecast.init()

            data = None
            try:
                data = WeatherForecast.__api_provider.forecast(lat, lon)
            except Exception as e:
                logger.error(
                    "%s API failed: %s",
                    WeatherForecast.__api_provider.name,
                    e,
                )

            if data:
                WeatherForecast.__last_forecast_data[request_key] = data
                WeatherForecast.__last_request_time[request_key] = timestamp
                logger.info(
                    "%s: %s, %s°",
                    data["now"]["api_provider"],
                    data["now"]["cond"],
                    data["now"]["temp"],
                )
                return data
            else:
                if request_key in WeatherForecast.__last_forecast_data:
                    # return last good cache if failed, add an indicator too
                    WeatherForecast.__last_forecast_data[request_key]["now"]["api_provider"] += "*"
                    return WeatherForecast.__last_forecast_data[request_key]

                # otherwise throw exception
                raise Exception("Meteo-France API failed.")
        finally:
            WeatherForecast.__lock.release()
