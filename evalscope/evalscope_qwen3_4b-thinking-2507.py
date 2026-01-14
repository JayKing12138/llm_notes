from evalscope.run import run_task
from evalscope.config import TaskConfig
from evalscope.collections import CollectionSchema, DatasetInfo

# 1. 定义评测集合
schema = CollectionSchema(name='Qwen3_Hard_Collection', datasets=[
    CollectionSchema(name='English_General', datasets=[
        DatasetInfo(name='mmlu_pro', weight=1, args={'few_shot_num': 0}),
        DatasetInfo(name='ifeval', weight=1, args={'few_shot_num': 0}),
    ]),
    CollectionSchema(name='Chinese_General', datasets=[
        DatasetInfo(name='ceval', weight=1, args={
            'dataset_id': 'ceval-exam', 
            'few_shot_num': 5
        }),
        DatasetInfo(name='cmmlu', weight=1, args={'few_shot_num': 5}),
    ]),
    CollectionSchema(name='Code_Logic', datasets=[
        DatasetInfo(name='live_code_bench', weight=1, args={
            'few_shot_num': 0, 
            'subset_list': ['v5_v6'], 
            'extra_params': {'start_date': '2025-01-01', 'end_date': '2025-04-30'}
        }),
    ]),
    CollectionSchema(name='Math_Science_Hard', datasets=[
        DatasetInfo(name='math_500', weight=1, args={'few_shot_num': 0}),
        DatasetInfo(name='aime24', weight=1, args={'few_shot_num': 0}),
        DatasetInfo(name='gpqa_diamond', weight=1, args={'few_shot_num': 0})
    ])
])

# 2. 手动展平数据集列表 (替换掉报错的 flatten_datasets)
all_dataset_infos = []
for sub_collection in schema.datasets:
    if isinstance(sub_collection, CollectionSchema):
        all_dataset_infos.extend(sub_collection.datasets)
    else:
        all_dataset_infos.append(sub_collection)

target_datasets = [ds.name for ds in all_dataset_infos]
dataset_args_map = {ds.name: ds.args for ds in all_dataset_infos}

# 3. 构造 TaskConfig
task_cfg = TaskConfig(
    model='Qwen3-4B-Thinking-2507-eval',
    api_url='http://127.0.0.1:8000/v1/chat/completions',
    eval_type='openai_api',
    
    datasets=target_datasets,
    dataset_args=dataset_args_map,
    
    eval_batch_size=8,      
    limit=100,               
    
    generation_config={
        'max_tokens': 2048,  
        'temperature': 0.0,
        'top_p': 1.0,
        'timeout': 300000,   
        'stream': True,
    }
)

# 4. 执行任务
if __name__ == '__main__':
    run_task(task_cfg=task_cfg)