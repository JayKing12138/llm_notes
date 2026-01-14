import base64
import requests

# 1. 编码本地视频
def encode_video(video_path):
    with open(video_path, "rb") as video_file:
        return base64.b64encode(video_file.read()).decode('utf-8')

video_path = "67b1e1726f1836bde701039704b80c.mp4"
base64_video = encode_video(video_path)

# 2. 构造请求
url = "http://127.0.0.1:8010/v1/chat/completions"
payload = {
    "model": "Qwen3-VL-4B-Instruct",
    "messages": [
        {
            "role": "user",
            "content": [
                # 视频输入
                {
                    "type": "video_url",
                    "video_url": {
                        "url": f"data:video/mp4;base64,{base64_video}"
                    }
                },
                {"type": "text", "text": "请详细描述这段视频的内容，包括发生的动作和场景。"}
            ]
        }
    ],
    "max_tokens": 1024
}

# 3. 发送请求
response = requests.post(url, json=payload)
print(response.json()['choices'][0]['message']['content'])