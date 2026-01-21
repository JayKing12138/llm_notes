# MCP client入门
## uv的安装

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
安装完成后，重启终端，确保 uv 命令可用。


## 创建项目目录并设置环境
```bash
# 创建项目目录
uv init mcp-client
cd mcp-client

# 创建虚拟环境
uv venv
# 激活虚拟环境
source .venv/bin/activate

# 安装 MCP SDK
uv add mcp openai python-dotenv

```


## 接入大模型，配置.env文件：

### 接入openai的话：
```bash
BASE_URL="https://api.chatanywhere.tech"
MODEL=gpt-5-nano
OPENAI_API_KEY=XXX
```

### 接入dashscope的话：
```bash
BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL=qwen3-max
DASHSCOPE_API_KEY=XXX
```

### 接入本地vllm启动的模型的话：
```bash
BASE_URL=http://localhost:8010/v1
MODEL=Qwen3-VL-4B-Instruct-lora-beans3
```

## client.py
在mcp-client文件夹里添加client.py。通过
```bash
uv run client.py
```
即可运行MCP client客户端了。

# MCP天气查询服务器server与使用

## 1. MCP服务器概念介绍
根据MCP协议定义，Server可以提供三种类型的标准能力，Resources、Tools、Prompts，每个Server可同时提供者三种类型能力或其中一种。
- **Resources**资源，类似于文件数据读取，可以是文件资源或是API响应返回的内容。
- **Tools**工具，第三方服务、功能函数，通过此可控制LLM可调用哪些函数。
- **Prompts**提示词，为用户预先定义好的完成特定任务的模板。

## 2. MCP服务器通讯机制
根据 MCP 的规范，当前支持两种传输方式：标准输入输出（stdio）和基于 HTTP 的服务器推送事件（SSE）。

| **维度**       | **stdio（标准输入输出）**                     | **HTTP + SSE（服务器推送事件）**             |
|----------------|---------------------------------------------|--------------------------------------------|
| **使用场景**   | 本地通信（客户端与服务端在同一机器）          | 远程通信（跨网络部署）                      |
| **通信方式**   | 通过 stdin/stdout 传递 JSON-RPC 消息         | 通过 HTTP 长连接 + SSE 流式推送 JSON-RPC 消息 |
| **特点**       | 低延迟、无网络开销、简单高效                  | 支持实时流式响应，适合 Web 和分布式环境      |


## 3. [天气查询服务器Server与Client创建流程](https://kq4b3vgg5b.feishu.cn/wiki/HhPmwc7TSikFpSkpUFDcGZ8PnCf)

```bash
# 创建项目目录
uv init weather
cd weather

# 创建虚拟环境
uv venv
# 激活虚拟环境
source .venv/bin/activate

uv add mcp openai python-dotenv httpx requests

uv add pandas openpyxl 
```

在weather文件夹中，添加server.py和client.py。

在server.py中，选择高德天气而不是openweather。
```bash
# 启动项目：
uv run client.py server.py
```
qwen3-max成功实现。

## 4. [MCP Inspector功能介绍](https://kq4b3vgg5b.feishu.cn/wiki/HhPmwc7TSikFpSkpUFDcGZ8PnCf)