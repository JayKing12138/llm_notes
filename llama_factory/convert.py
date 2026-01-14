import json
import os

# 路径请根据你刚才 ls 看到的结果确认
# source_dir = "/home/crq/datasets/beans3/tany0699/beans3/master/data_files/extracted/116c5530c83594a3cd5bc9d81f42fb04340a4f722afefb288efba73bf10ebf4b/train"
source_dir = "/home/crq/datasets/beans3/tany0699/beans3/master/data_files/extracted/116c5530c83594a3cd5bc9d81f42fb04340a4f722afefb288efba73bf10ebf4b/val"
# final_json_path = "/home/crq/.cache/modelscope/hub/datasets/tany0699/beans3/beans_train_vl.json"
final_json_path = "/home/crq/.cache/modelscope/hub/datasets/tany0699/beans3/beans_val_vl.json"

class_map = {
    "angular_leaf_spot": "角斑病",
    "bean_rust": "菜豆锈病",
    "healthy": "健康"
}

data_list = []

for label_dir in ["angular_leaf_spot", "bean_rust", "healthy"]:
    label_path = os.path.join(source_dir, label_dir)
    if os.path.exists(label_path):
        label_zh = class_map[label_dir]
        files = [f for f in os.listdir(label_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for img_name in files:
            abs_path = os.path.abspath(os.path.join(label_path, img_name))
            # 这里的格式改动：<image> 后面紧跟内容，不加多余的 \n
            data_list.append({
                "conversations": [  # 尝试使用 conversations 键名，兼容性更广
                    {
                        "from": "human",
                        "value": "<image>这张图片里的豆子叶片健康吗？是什么病害？"
                    },
                    {
                        "from": "gpt",
                        "value": f"诊断结果为：{label_zh}。"
                    }
                ],
                "images": [abs_path]
            })

with open(final_json_path, 'w', encoding='utf-8') as f:
    json.dump(data_list, f, ensure_ascii=False, indent=2)

print(f"成功转换到: {final_json_path}")