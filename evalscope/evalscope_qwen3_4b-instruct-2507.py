from evalscope import TaskConfig, run_task

# 定义 JSON 的绝对路径
JSON_PATH = '/home/crq/.cache/modelscope/hub/datasets/tany0699/beans3/beans_val_vl.json'

task_cfg = TaskConfig(
    model='Qwen3-VL-4B-Instruct',
    api_url='http://127.0.0.1:8010/v1/chat/completions',
    eval_type='openai_api',
    
    datasets=['general_vqa'], 
    
    dataset_args={
        'general_vqa': {
            # 关键：直接用路径作为 ID，强制本地化
            'dataset_id': JSON_PATH,
            
            # 这里的 formatting 和 columns 是为了让适配器读懂你的 from/value 格式
            'formatting': 'sharegpt',
            'columns': {
                'messages': 'conversations',
                'images': 'images',
                'role': 'from',
                'content': 'value'
            },
            
            # 强制指定 split，本地加载通常被归为 train
            'eval_split': 'train'
        }
    },
    
    limit=10, 
    eval_batch_size=1, 
    
    generation_config={
        'max_tokens': 512,
        'temperature': 0.0,
        'timeout': 60000,
    },
)

run_task(task_cfg=task_cfg)