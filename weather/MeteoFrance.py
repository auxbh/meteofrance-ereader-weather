from meteofrance_api import MeteoFranceClient

from .utils import WeatherUtils


DESC_ICON_MAP = [
    (["orage", "tonnerre"], "thunderstorm"),
    (["grele", "grêle"], "hail"),
    (["neige", "verglas"], "snow"),
    (["pluie", "averse", "bruine"], "rain"),
    (["brouillard", "brume"], "fog"),
    (["eclaircie", "éclaircie", "variable"], "sunny-intervals"),
    (["voilé"], "hazy"),
    (["peu nuageux"], "partly-cloudy"),
    (["couvert", "nuageux", "nuage"], "cloudy"),
    (["clair", "soleil", "ensoleille"], "clear"),
]


class MeteoFranceAPI:
    @property
    def name(self):
        return "Meteo-France"

    def __init__(self):
        self.__client = MeteoFranceClient()

    def __nested_value(self, data, *keys, default=None):
        value = data
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        return value

    def __temperature(self, data, *keys, default=0):
        value = self.__nested_value(data, *keys, default=default)
        if value is None:
            value = default
        return int(round(float(value)))

    def __forecast_time(self, forecast, timestamp):
        return forecast.timestamp_to_locale_time(timestamp)

    def __weather(self, item, item_time=None):
        weather = item.get("weather") or item.get("weather12H") or {}
        desc = (
            weather.get("desc")
            or weather.get("description")
            or item.get("desc")
            or "Inconnu"
        )
        return desc, self.__icon(desc, weather.get("icon"), item_time)

    def __is_daytime(self, item_time):
        if not item_time:
            return True
        return item_time.hour >= 6 and item_time.hour < 21

    def __icon(self, desc, icon_id=None, item_time=None):
        text = f"{desc or ''} {icon_id or ''}".lower()
        for keywords, icon in DESC_ICON_MAP:
            if any(keyword in text for keyword in keywords):
                if icon == "clear":
                    return (
                        "clear-day" if self.__is_daytime(item_time) else "clear-night"
                    )
                if icon == "partly-cloudy":
                    return (
                        "partly-cloudy-day"
                        if self.__is_daytime(item_time)
                        else "partly-cloudy-night"
                    )
                return icon
        return "unknown"

    def forecast(self, lat, lon):
        forecast = self.__client.get_forecast(float(lat), float(lon), language="fr")
        observation = self.__client.get_observation(float(lat), float(lon), language="fr")
        current = forecast.current_forecast or forecast.nearest_forecast
        today = forecast.today_forecast or forecast.daily_forecast[0]
        current_time = self.__forecast_time(
            forecast, current.get("dt", forecast.updated_on)
        )
        cond, icon = self.__weather(current, current_time)

        temp = int(round(float(observation.temperature)))
        feels = self.__temperature(current, "T", "windchill", default=temp)
        wind_speed = self.__temperature(current, "wind", "speed")
        wind_dir = WeatherUtils.get_direction_fr(
            int(
                round(
                    float(self.__nested_value(current, "wind", "direction", default=0))
                )
            )
        )
        humidity = self.__temperature(current, "humidity", default=0)

        result = {}
        result["now"] = {
            "api_provider": self.name,
            "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "temp": temp,
            "high": self.__temperature(today, "T", "max", default=temp),
            "low": self.__temperature(today, "T", "min", default=temp),
            "cond": cond,
            "icon": icon,
            "summary": f"Vent {wind_speed} km/h {wind_dir}, ressenti {feels}°, humidité {humidity}%",
        }

        result["hourly"] = []
        for i in [1, 3, 5, 8, 11, 14]:
            if i >= len(forecast.forecast):
                continue
            item = forecast.forecast[i]
            item_time = self.__forecast_time(forecast, item["dt"])
            cond_h, icon_h = self.__weather(item, item_time)
            result["hourly"].append(
                {
                    "time": WeatherUtils.get_24h_hour_str(item_time),
                    "temp": self.__temperature(item, "T", "value"),
                    "cond": cond_h,
                    "icon": icon_h,
                }
            )

        result["daily"] = []
        for item in forecast.daily_forecast[1:7]:
            item_time = self.__forecast_time(forecast, item["dt"])
            cond_d, icon_d = self.__weather(item)
            result["daily"].append(
                {
                    "day": WeatherUtils.get_french_day_str(item_time),
                    "date": item_time.strftime("%d/%m"),
                    "high": self.__temperature(item, "T", "max"),
                    "low": self.__temperature(item, "T", "min"),
                    "cond": cond_d,
                    "icon": icon_d,
                }
            )

        result["location"] = forecast.position.get("name")
        return result
