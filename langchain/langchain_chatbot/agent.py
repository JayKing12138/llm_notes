import os
from dotenv import load_dotenv 
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
import json
import pandas as pd
import requests


# 加载环境变量
load_dotenv(override=True)
GAODE_API_KEY = os.getenv("GAODE_API_KEY")

model = ChatTongyi(model="qwen3-max")

web_search = TavilySearchResults(max_results=2)


@tool
def get_weather(loc):
    """
    根据城市名称查询高德即时天气
    :param loc: 城市名称，例如 "北京市"、"东城区" 或 "天津市"
    """
    # --- Step 1. 获取城市的 adcode ---
    try:
        # 读取同级目录下的 Excel 文件
        df = pd.read_excel('./AMap_adcode_citycode.xlsx')
        
        # 在“中文名”列中查找匹配的行，并获取对应的 adcode
        # 使用 loc[0] 确保只取第一个匹配结果
        match = df[df['中文名'] == loc]
        
        if match.empty:
            return json.dumps({"status": "0", "info": f"未在对照表中找到城市: {loc}"}, ensure_ascii=False)
        
        adcode = str(match.iloc[0]['adcode'])
    except Exception as e:
        return json.dumps({"status": "0", "info": f"读取编码表失败: {str(e)}"}, ensure_ascii=False)

    # --- Step 2. 构建请求 ---
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    # --- Step 3. 设置查询参数 ---
    params = {
        "key": GAODE_API_KEY,               
        "city": adcode,
        "extensions": "base"  # base:实况天气; all:预报天气
    }

    # --- Step 4. 发送请求并解析 ---
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # 使用 indent 使返回的 JSON 字符串更美观
        return json.dumps(data, indent=4, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "0", "info": f"API请求失败: {str(e)}"}, ensure_ascii=False)

tools = [web_search, get_weather]

# 创建模型
prompt = """
你是一名乐于助人的智能助手，擅长根据用户的问题选择合适的工具来查询信息并回答。

当用户的问题涉及**天气信息**时，你应优先调用`get_weather`工具，查询用户指定城市的实时天气，并在回答中总结查询结果。

当用户的问题涉及**新闻、事件、实时动态**时，你应优先调用`web_search`工具，检索相关的最新信息，并在回答中简要概述。

如果问题既包含天气又包含新闻，请先使用`get_weather`查询天气，再使用`web_search`查询新闻，最后将结果合并后回复用户。

所有回答应使用**简体中文**，条理清晰、简洁友好。
"""



 
agent = create_agent(
    model=model,
    tools=[web_search, get_weather],
    system_prompt=prompt
)