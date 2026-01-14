# think_inference.py
from modelscope import AutoModelForCausalLM, AutoTokenizer

model_dir = "/home/crq/.cache/modelscope/hub/models/Qwen/Qwen3-4B-Thinking-2507"
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    device_map="cuda:0",
    trust_remote_code=True
).eval()

# 启用think模式
response, history = model.chat(
    tokenizer,
    "我是秦始皇",
    history=None,
    think=True  # 关键参数
)
print(response)