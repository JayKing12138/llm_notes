import os
import json
import pandas as pd
from typing import Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

# 初始化 MCP 服务器
mcp = FastMCP("GaodeWeatherServer")

# 高德 API 配置
GAODE_API_KEY = os.getenv("GAODE_API_KEY")
if not GAODE_API_KEY:
    raise ValueError("请在 .env 文件中设置 GAODE_API_KEY")

# 城市编码表路径（与脚本同目录）
ADCODE_FILE = "./AMap_adcode_citycode.xlsx"

def get_adcode(city_name: str) -> str | None:
    """根据中文城市名查找对应的 adcode"""
    try:
        df = pd.read_excel(ADCODE_FILE)
        match = df[df['中文名'] == city_name]
        if not match.empty:
            return str(match.iloc[0]['adcode'])
        return None
    except Exception as e:
        return None

async def fetch_weather(city: str) -> dict[str, Any]:
    """
    使用高德 API 获取实况天气
    :param city: 中文城市名，如 "北京市"、"茌平区"
    :return: 天气数据字典或错误信息
    """
    # 1. 获取 adcode
    adcode = get_adcode(city)
    if not adcode:
        return {"error": f"未找到城市 '{city}' 的行政区划编码，请检查名称或编码表"}

    # 2. 构造请求
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": GAODE_API_KEY,
        "city": adcode,
        "extensions": "base"
    }

    try:
        import requests
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "1":
            return {"error": f"高德 API 错误: {data.get('info', '未知错误')}"}

        live = data.get("lives", [{}])[0]
        if not live:
            return {"error": "未获取到实况天气数据"}

        return {
            "province": live.get("province", ""),
            "city": live.get("city", city),
            "weather": live.get("weather", "未知"),
            "temperature": live.get("temperature", "N/A"),
            "winddirection": live.get("winddirection", "无"),
            "windpower": live.get("windpower", "≤3"),
            "humidity": live.get("humidity", "N/A"),
            "reporttime": live.get("reporttime", "")
        }
    except Exception as e:
        return {"error": f"请求失败: {str(e)}"}

def format_weather(data: dict[str, Any]) -> str:
    """将高德天气数据格式化为易读文本"""
    if "error" in data:
        return f"⚠️ {data['error']}"

    return (
        f"🌍 {data['province']} {data['city']}\n"
        f"🌡 温度: {data['temperature']}°C\n"
        f"💧 湿度: {data['humidity']}%\n"
        f"🌬 风向: {data['winddirection']}风\n"
        f"💨 风力: {data['windpower']}级\n"
        f"🌤 天气: {data['weather']}\n"
        f"🕒 更新时间: {data['reporttime']}\n"
    )

@mcp.tool()
async def query_weather(city: str) -> str:  # 统一改为city
    """
    获取指定城市的实况天气。注意：必须通过参数 'city' 传入中文城市名，例如 {"city": "北京市"}。
    不要使用 'location'、'place' 或其他字段名。
    """
    data = await fetch_weather(city)
    return format_weather(data)

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')