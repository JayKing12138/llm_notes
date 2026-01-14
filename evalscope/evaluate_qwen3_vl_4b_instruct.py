import json
import requests
import base64
import re

# 1. 配置信息
JSON_PATH = '/home/crq/.cache/modelscope/hub/datasets/tany0699/beans3/beans_val_vl.json'
API_URL = 'http://127.0.0.1:8010/v1/chat/completions'
# MODEL_NAME = 'Qwen3-VL-4B-Instruct' 
MODEL_NAME = 'Qwen3-VL-4B-Instruct-lora-beans3' 

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def run_eval():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 分类统计字典
    # 格式: {类别名: [正确数, 总数]}
    stats = {
        "健康": [0, 0],
        "菜豆锈病": [0, 0],
        "角斑病": [0, 0]
    }
    
    total_data = len(data)

    print(f"🚀 开始全量评测 | 样本总数: {total_data}")
    print("-" * 85)
    print(f"{'ID':<5} | {'预期病害 (Target)':<15} | {'模型输出 (Model)':<20} | {'结果'}")
    print("-" * 85)

    for i, item in enumerate(data):
        # 1. 提取参考答案
        ref_text = item['conversations'][1]['value']
        target_match = re.search(r'诊断结果为：(.+?)。', ref_text)
        target_disease = target_match.group(1) if target_match else ref_text
        
        # 更新该类别的总计数
        if target_disease in stats:
            stats[target_disease][1] += 1
        
        # 2. 构造 Prompt
        user_prompt = item['conversations'][0]['value']
        system_instr = "\n要求：仅输出病名（健康、菜豆锈病、角斑病中的一个），禁止输出任何标点或废话。"
        full_prompt = user_prompt + system_instr
        
        image_path = item['images'][0]

        try:
            # 3. API 请求
            base64_image = encode_image(image_path)
            payload = {
                "model": MODEL_NAME,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                "temperature": 0.0,
                "max_tokens": 15
            }

            response = requests.post(API_URL, json=payload, timeout=30)
            res_json = response.json()
            
            model_raw = res_json['choices'][0]['message']['content'].strip()
            # 清洗输出
            model_clean = model_raw.replace("诊断结果为：", "").replace("。", "").strip()

            # 4. 判定
            is_correct = (target_disease == model_clean)
            if is_correct:
                stats[target_disease][0] += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            print(f"{i:<5} | {target_disease:<15} | {model_clean:<20} | {status}")
            
        except Exception as e:
            print(f"{i:<5} | {target_disease:<15} | 错误: {str(e)[:15]} | ⚠️")

    # 5. 分类总结输出
    print("\n" + "="*45)
    print(f"{'病害类别':<12} | {'正确/总数':<12} | {'准确率'}")
    print("-" * 45)
    
    grand_correct = 0
    grand_total = 0
    
    for category, (correct, total) in stats.items():
        acc = (correct / total * 100) if total > 0 else 0
        print(f"{category:<14} | {correct:>3}/{total:<7} | {acc:>6.2f}%")
        grand_correct += correct
        grand_total += total

    print("-" * 45)
    overall_acc = (grand_correct / grand_total * 100) if grand_total > 0 else 0
    print(f"{'总计':<14} | {grand_correct:>3}/{grand_total:<7} | {overall_acc:>6.2f}%")
    print("="*45)

if __name__ == '__main__':
    run_eval()