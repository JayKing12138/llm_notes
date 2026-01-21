import asyncio
import os
import json
import sys
import requests
from typing import Optional
from contextlib import AsyncExitStack

from openai import OpenAI  
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 加载 .env 文件
load_dotenv()

class MCPClient:
    def __init__(self):
        """初始化 MCP 客户端"""
        self.exit_stack = AsyncExitStack()
        self.openai_api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = os.getenv("BASE_URL") 
        self.model = os.getenv("MODEL")
        if not self.openai_api_key:
            raise ValueError("❌ 未找到 DASHSCOPE_API_KEY，请在 .env 文件中设置")
        self.client = OpenAI(api_key=self.openai_api_key, base_url=self.base_url)
        self.session: Optional[ClientSession] = None

    async def connect_to_server(self, server_script_path: str):
        """连接到 MCP 服务器并列出可用工具"""
        if not server_script_path.endswith(('.py', '.js')):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")

        command = "python" if server_script_path.endswith('.py') else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\n已连接到服务器，支持以下工具:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """
        使用大模型处理查询并调用 MCP 工具（适配 Qwen/DashScope）
        """
        messages = [{"role": "user", "content": query}]
        
        # 获取工具列表
        response = await self.session.list_tools()
        tools = response.tools

        # 构造 functions 列表（Qwen 更兼容此格式）
        functions = []
        for tool in tools:
            functions.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema  # 注意：这里用 parameters，不是 input_schema
            })

        # 第一次调用：带 functions
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=functions,  # ⚠️ 关键：用 functions 而不是 tools
            function_call="auto"
        )

        message = response.choices[0].message

        # 如果模型决定调用函数
        if hasattr(message, 'function_call') and message.function_call:
            func_call = message.function_call
            tool_name = func_call.name
            tool_args = json.loads(func_call.arguments)

            print(f"\n\n[Calling tool {tool_name} with args {tool_args}]\n\n")

            # 调用 MCP 工具
            result = await self.session.call_tool(tool_name, tool_args)
            
            # 在调用工具后立即打印原始结果
            tool_result = result.content[0].text
            print(f"\n🔧 工具返回原始内容:\n{tool_result}\n")
            
            
            tool_result = result.content[0].text

            # 构建消息历史：用户 -> 助手（调用函数） -> 函数结果
            messages.append(message)  # 助手的消息（含 function_call）
            messages.append({
                "role": "function",
                "name": tool_name,
                "content": tool_result
            })

            # 第二次调用：传入函数结果
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions  # 保持一致
            )
            final_message = final_response.choices[0].message
            return final_message.content or ""

        # 如果模型不调用函数，直接返回
        return message.content or ""

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n🤖 MCP 客户端已启动！输入 'quit' 退出")
        while True:
            try:
                query = input("\n你: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print(f"\n🤖 OpenAI: {response}")
            except Exception as e:
                print(f"\n⚠️ 发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())