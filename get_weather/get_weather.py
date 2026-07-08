import requests

from chapter02chat.model import QWEATHER_API_KEY


# ===================== 2. 天气 API 接入层 =====================
# 优先级: wttr.in（免Key） > 和风天气（需Key+订阅）

def _kmh_to_beaufort(kmh: int) -> int:
    """风速 km/h 转蒲福风级"""
    if kmh < 1:
        return 0
    elif kmh <= 5:
        return 1
    elif kmh <= 11:
        return 2
    elif kmh <= 19:
        return 3
    elif kmh <= 28:
        return 4
    elif kmh <= 38:
        return 5
    elif kmh <= 49:
        return 6
    elif kmh <= 61:
        return 7
    elif kmh <= 74:
        return 8
    elif kmh <= 88:
        return 9
    elif kmh <= 102:
        return 10
    elif kmh <= 117:
        return 11
    else:
        return 12


def _fetch_weather_wttr(city: str) -> str | None:
    """
    wttr.in 免费天气 API — 无需注册，无需 API Key
    文档: https://github.com/chubin/wttr.in
    """
    url = "https://wttr.in/" + city
    params = {"format": "j1"}

    try:
        resp = requests.get(url, params=params, timeout=10,
                           headers={"Accept-Language": "zh-CN"})
        data = resp.json()
        current = data.get("current_condition", [{}])[0]
        if not current:
            return None

        windspeed_kmh = int(current.get("windspeedKmph", 0))
        wind_scale = _kmh_to_beaufort(windspeed_kmh)

        wind_dir_map = {
            "N": "北", "NNE": "北东北", "NE": "东北", "ENE": "东东北",
            "E": "东", "ESE": "东东南", "SE": "东南", "SSE": "南东南",
            "S": "南", "SSW": "南西南", "SW": "西南", "WSW": "西西南",
            "W": "西", "WNW": "西西北", "NW": "西北", "NNW": "北西北",
        }
        wind_dir_en = current.get("winddir16Point", "")
        wind_dir = wind_dir_map.get(wind_dir_en, wind_dir_en)

        weather_desc_list = current.get('lang_zh', [])
        if weather_desc_list:
            weather_desc = weather_desc_list[0].get('value', '')
        else:
            weather_desc = current.get('weatherDesc', [{}])[0].get('value', '未知')

        return (
            f"{city}当前天气：{weather_desc}，"
            f"气温 {current.get('temp_C', '?')}°C，"
            f"体感温度 {current.get('FeelsLikeC', '?')}°C，"
            f"{wind_dir}风 {wind_scale}级（{windspeed_kmh}km/h），"
            f"相对湿度 {current.get('humidity', '?')}%，"
            f"能见度 {current.get('visibility', '?')}km，"
            f"气压 {current.get('pressure', '?')}hPa，"
            f"云量 {current.get('cloudcover', '?')}%"
        )
    except (requests.RequestException, KeyError, ValueError):
        return None


def _fetch_weather_qweather(city: str) -> str | None:
    """
    和风天气 API — 数据更丰富，需注册Key并在控制台订阅API服务
    注册地址: https://dev.qweather.com/
    """
    if not QWEATHER_API_KEY:
        return None

    try:
        # 步骤1：城市名 → LocationID
        url_city = "https://geoapi.qweather.com/v2/city/lookup"
        resp = requests.get(
            url_city,
            params={"location": city, "key": QWEATHER_API_KEY, "number": 1},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") != "200" or not data.get("location"):
            return None
        city_id = data["location"][0]["id"]

        # 步骤2：LocationID → 实时天气
        url_now = "https://devapi.qweather.com/v7/weather/now"
        resp2 = requests.get(
            url_now,
            params={"location": city_id, "key": QWEATHER_API_KEY},
            timeout=10,
        )
        data2 = resp2.json()
        if data2.get("code") != "200" or not data2.get("now"):
            return None
        now = data2["now"]

        wind_dir_map = {
            "N": "北", "S": "南", "E": "东", "W": "西",
            "NE": "东北", "NW": "西北", "SE": "东南", "SW": "西南",
        }
        wind_dir = wind_dir_map.get(now.get("windDir", ""), now.get("windDir", "未知"))

        return (
            f"{city}当前天气：{now.get('text', '未知')}，"
            f"气温 {now.get('temp', '?')}°C，"
            f"体感温度 {now.get('feelsLike', '?')}°C，"
            f"{wind_dir}风 {now.get('windScale', '?')}级，"
            f"相对湿度 {now.get('humidity', '?')}%，"
            f"能见度 {now.get('vis', '?')}km，"
            f"气压 {now.get('pressure', '?')}hPa"
        )
    except requests.RequestException:
        return None


# ===================== 工具定义 =====================
from langchain_core.tools import tool


def _get_mock_weather(city: str) -> str:
    """离线兜底 — 模拟天气数据"""
    weather_data = {
        "杭州": "晴天，气温 25°C ~ 32°C，东南风 3级，湿度 65%",
        "北京": "多云，气温 18°C ~ 28°C，北风 2级，湿度 40%",
        "上海": "阴转小雨，气温 22°C ~ 29°C，东风 4级，湿度 75%",
        "深圳": "雷阵雨，气温 26°C ~ 33°C，南风 3级，湿度 80%",
        "广州": "晴转多云，气温 27°C ~ 34°C，西南风 2级，湿度 70%",
        "成都": "阴天，气温 20°C ~ 27°C，无持续风向 1级，湿度 72%",
    }
    return weather_data.get(city, f"{city}：晴间多云，气温 20°C ~ 30°C，微风，湿度 55%")


@tool(description="根据城市名称查询当日天气的工具")
def get_weather(city: str) -> str:
    """
    天气查询工具，输入城市名称（如"杭州"、"北京"），返回该城市实时天气。

    数据来源优先级: wttr.in(免费免Key) > 和风天气(需Key) > 模拟数据(兜底)
    """
    # 策略1：wttr.in 免费 API（无需任何配置）
    result = _fetch_weather_wttr(city)
    if result:
        return result

    # 策略2：和风天气（数据更丰富，需Key+订阅）
    result = _fetch_weather_qweather(city)
    if result:
        return result

    # 策略3：模拟数据兜底（保证永远不返回 None）
    return _get_mock_weather(city)
