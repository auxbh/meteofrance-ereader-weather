import os
import json
import platform
import binascii
import time

from threading import RLock
from geopy import geocoders

import logging

logger = logging.getLogger()


class WeatherUtils:
    __lock = RLock()
    __zip_mapping = {}
    __city_mapping = {}
    __french_days = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]

    @staticmethod
    def get_direction(bearing):
        coords = {
            "N": [0, 22.5],
            "NE": [22.5, 67.5],
            "E": [67.5, 112.5],
            "SE": [112.5, 157.5],
            "S": [157.5, 202.5],
            "SW": [202.5, 247.5],
            "W": [247.5, 292.5],
            "NW": [292.5, 337.5],
            "N": [337.5, 360],
        }
        for k, v in coords.items():
            if bearing >= v[0] and bearing < v[1]:
                return k
        return ""

    @staticmethod
    def get_direction_fr(bearing):
        direction = WeatherUtils.get_direction(bearing)
        return {
            "W": "O",
            "NW": "NO",
            "SW": "SO",
        }.get(direction, direction)

    @staticmethod
    def get_am_pm_hour_str(timestamp):
        if platform.system() == "Windows":
            return timestamp.strftime("%#I %p")
        else:
            return timestamp.strftime("%-I %p")

    @staticmethod
    def get_24h_hour_str(timestamp):
        return timestamp.strftime("%Hh")

    @staticmethod
    def get_french_day_str(timestamp):
        if hasattr(timestamp, "weekday"):
            weekday = timestamp.weekday()
        else:
            weekday = (
                timestamp.tm_wday
                if hasattr(timestamp, "tm_wday")
                else int(time.strftime("%w", timestamp)) - 1
            )
        return WeatherUtils.__french_days[weekday]

    @staticmethod
    def apply_timezone_env():
        if "TZ" in os.environ and hasattr(time, "tzset"):
            time.tzset()

    @staticmethod
    def get_localtime():
        WeatherUtils.apply_timezone_env()
        return time.localtime()

    @staticmethod
    def load_api_dump(url):
        if "DEBUG_API" in os.environ:
            url_hash = binascii.crc32(url.encode("utf8"))
            debug_json = f"/tmp/{url_hash}.json"
            if os.path.exists(debug_json):
                with open(debug_json, encoding="utf-8") as r:
                    return json.load(r)

    @staticmethod
    def save_api_dump(url, r):
        if "DEBUG_API" in os.environ or os.path.exists("/tmp/dump-api.flag"):
            url_hash = binascii.crc32(url.encode("utf8"))
            debug_json = f"/tmp/{url_hash}.json"
            with open(debug_json, "w", encoding="utf-8") as w:
                w.write(r.text)

    @staticmethod
    def get_gps_coordinates(zip_code):
        try:
            WeatherUtils.__lock.acquire()
            if zip_code in WeatherUtils.__zip_mapping:
                return WeatherUtils.__zip_mapping[zip_code]

            # geopy cannot specify zip code explicitly, so not accurate
            geolocator = geocoders.Nominatim(user_agent="Nook-Weather")
            location = geolocator.geocode({"country": "us", "postalcode": zip_code})
            coordinates = f"{location.latitude},{location.longitude}"
            WeatherUtils.__zip_mapping[zip_code] = coordinates
            return coordinates
        except Exception as e:
            logger.error("Failed to get gps coordinates from zip %s: %s", zip_code, e)
            return None
        finally:
            WeatherUtils.__lock.release()
