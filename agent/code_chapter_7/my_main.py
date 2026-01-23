# my_main.py
from dotenv import load_dotenv
from my_llm import MyLLM # 注意：这里导入我们自己的类

# 加载环境变量
load_dotenv(dotenv_path="/home/crq/llm_scripts/langchain/.env")

# 实例化我们重写的客户端，并指定provider
llm = MyLLM(provider="modelscope") 

# 准备消息
messages = [{"role": "user", "content": "你好，请介绍一下你自己。"}]

# 发起调用，think等方法都已从父类继承，无需重写
response_stream = llm.think(messages)

# 在 Python 中，yield 构成的生成器（Generator）是惰性执行的。
# 当你调用 response_stream = llm.think(messages) 时，函数体代码并不会立即执行。
# 只有当你开始遍历（例如 for _ in response_stream）时，think 内部的代码才会开始跑。
for _ in response_stream:
    # 仅仅是迭代，不做额外打印
    pass

# HelloAgentsLLM.think也输出，原代码也输出，重复输出。
# # 打印响应
# print("ModelScope Response:")
# for chunk in response_stream:
#     # chunk 已经是文本片段，可以直接使用
#     print(chunk, end="", flush=True)