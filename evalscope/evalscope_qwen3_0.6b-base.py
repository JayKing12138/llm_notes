from evalscope import TaskConfig, run_task

task_cfg = TaskConfig(
    # 必须与 vLLM 启动时的 served_model_name 保持一致
    model='/home/crq/.cache/modelscope/hub/models/Qwen/Qwen3-0.6B-Base',
    
    # vLLM 默认端口
    api_url='http://127.0.0.1:8000/v1/chat/completions',
    
    eval_type='openai_api',
    
    # 这里的列表项要作为 dataset_args 的 Key
    datasets=[
        'gsm8k', 
    ],
    
    dataset_args={
        'gsm8k': {
            
            'dataset_id': 'gsm8k', 
            
            # 0.6B 比较弱，建议设置 few_shot_num=4 
            # 给模型 4 个例子参考，它会表现得比 0-shot 好很多
            'few_shot_num': 4,
            'few_shot_random': True,
            
            # Base 模型可以去掉这个 filter
            # 'filters': {'remove_until': '</think>'} 
        }
    },
    
    eval_batch_size=32, 
    
    generation_config={
        'max_tokens': 1024,  # GSM8K 题目较短，1024 足够
        'temperature': 0.0,  # 评测数学时，通常建议设为 0 以保证结果可复现
        'top_p': 1.0,
        'n': 1,
    },
    timeout=60000,
    stream=True,
    limit=100,  # 测试100条数据
)

run_task(task_cfg=task_cfg)