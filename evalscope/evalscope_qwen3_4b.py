from evalscope import TaskConfig, run_task

task_cfg = TaskConfig(
    model='Qwen3-4B-eval',
    api_url='http://127.0.0.1:8000/v1/chat/completions',
    eval_type='openai_api',
    
    # 这里必须是简称，以匹配 EvalScope 的注册表
    datasets=['ceval', 'gsm8k', 'hellaswag'], 
    
    dataset_args={
        'gsm8k': {
            'dataset_id': 'gsm8k', 
            'few_shot_num': 4,
            'few_shot_random': True,
        },
        'hellaswag': {
            'dataset_id': 'hellaswag',
            'few_shot_num': 0,
        },
        'ceval': {
            # 关键：手动指定正确的 ModelScope 数据集 ID
            'dataset_id': 'ceval-exam', 
            'subset_list': ['middle_school_geography', 'middle_school_history'],
            'few_shot_num': 5,
        }
    },
    
    eval_batch_size=16, 
    limit=100, 
    
    generation_config={
        'max_tokens': 1024,
        'temperature': 0.0,
        'top_p': 1.0,
        'n': 1,
        'timeout': 60000, # 移动到这里，消除 Warning
        'stream': True,   # 移动到这里，消除 Warning
    },
    # 外部的参数已移除
)

run_task(task_cfg=task_cfg)