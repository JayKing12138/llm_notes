# [单机多卡训练](https://llamafactory.readthedocs.io/zh-cn/latest/advanced/distributed.html#id14)

# Qwen3_4b_instruct_2507



## NativeDDP分布式训练

#### lora微调 学习 弱智吧：



```bash
FORCE_TORCHRUN=1 CUDA_VISIBLE_DEVICES=0,3 NPROC_PER_NODE=2 llamafactory-cli train \
    examples/train_lora/qwen3_lora_sft_ddp_ruozhiba.yaml
```

在`LLaMA-Factory/data/dataset_info.json`里添加数据,例如：
```json
  "agri_wiki_qa": {
  "file_name": "/home/crq/.cache/modelscope/hub/datasets/chal1ce/Agricultrue_Wiki_QA_110K/agriculture_wiki_qa_full.csv",
  "columns": {
    "prompt": "question",
    "response": "answer",
    "history": "thinking"
  }
},
  "ruozhiba_gpt4": {
    "file_name": "/home/crq/.cache/modelscope/hub/datasets/hfl/ruozhiba_gpt4/ruozhiba_qa2449_gpt4o.json",
    "columns": {
      "prompt": "instruction",
      "query": "input",
      "response": "output"
    }
  }
```

NativeDDP，训练3个epoch，结果保存在`LLaMA-Factory/saves/Qwen3-4B-Instruct-2507/lora/sft`

#### lora微调 学习 农学知识：

```bash
FORCE_TORCHRUN=1 CUDA_VISIBLE_DEVICES=0,3 NPROC_PER_NODE=2 llamafactory-cli train \
    examples/train_lora/qwen3_lora_sft_ddp_agri_wiki_qa.yaml
```

NativeDDP，训练50个epoch，结果保存在`LLaMA-Factory/saves/Qwen3-4B-Instruct-2507/lora/sft_agri`

tensorboard文件保存在: LLaMA-Factory/saves/Qwen3-4B-Instruct-2507/lora/sft_agri/runs/Jan08_02-43-26_ubun下

### lora微调 学习 gsm8k_zh 

```bash
FORCE_TORCHRUN=1 CUDA_VISIBLE_DEVICES=0,3 NPROC_PER_NODE=2 llamafactory-cli train \
    examples/train_lora/qwen3_lora_sft_ddp_gsm8k_zh.yaml
```

NativeDDP，训练15.88个epoch，结果保存在`LLaMA-Factory/saves/Qwen3-4B-Instruct-2507/lora/sft_gsm8k_zh`

保存了两组checkpoint，一组step=500，另一组1000.


## DeepSpeed分布式训练


```bash
conda activate llamafdeepspeed

export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

deepspeed --include localhost:0,3 src/train.py \
    --deepspeed examples/deepspeed/ds_z2_config.json \
    --stage sft \
    --do_train \
    --model_name_or_path /home/crq/.cache/modelscope/hub/models/Qwen/Qwen3-4B-Instruct-2507 \
    --dataset gsm8k_zh \
    --template qwen \
    --finetuning_type lora \
    --output_dir saves/Qwen3-4B/ds_z2/gsm8k_zh \
    --overwrite_cache \
    --overwrite_output_dir \
    --cutoff_len 1024 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 8 \
    --lr_scheduler_type cosine \
    --logging_steps 5 \
    --save_steps 100 \
    --learning_rate 5e-5 \
    --num_train_epochs 3.0 \
    --plot_loss \
    --bf16 true
```



# Qwen3_vl_4b_instruct

- 先下载数据集豆类叶片病变分类数据集tany0699/beans3,训练/测试
```bash
python3 -c "from modelscope.msdatasets import MsDataset; \
ds = MsDataset.load('beans3', namespace='tany0699', split='train', \
download_mode='force_redownload', cache_dir='/home/crq/datasets/beans3')"

python3 -c "from modelscope.msdatasets import MsDataset; \
ds = MsDataset.load('beans3', namespace='tany0699', split='validation', \
download_mode='force_redownload', cache_dir='/home/crq/datasets/beans3')"
```

- 对Qwen3_vl_4b_instruct，选取豆类叶片病变分类数据集tany0699/beans3，进行微调
- 首先进行适配llama factory的转换, 见`convert.py`（训练集和测试集分别转换成两个）。
- 然后修改`/home/crq/LLaMA-Factory/data/dataset_info.json`，添加beans_train_vl和beans_val_vl；
- 然后开始lora微调

### 使用DeepSpeed

```bash
conda activate llamafds
cd ~/LLaMA-Factory/

# 环境变量设置（确保 DeepSpeed 正常工作）
export CUDA_HOME=$CONDA_PREFIX
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib:$LD_LIBRARY_PATH

# 启动微调
deepspeed --include localhost:0,3 src/train.py \
    --deepspeed examples/deepspeed/ds_z2_config.json \
    --stage sft \
    --do_train \
    --model_name_or_path /home/crq/.cache/modelscope/hub/models/Qwen/Qwen3-VL-4B-Instruct \
    --dataset beans_train_vl \
    --template qwen3_vl_nothink \
    --finetuning_type lora \
    --lora_target all \
    --output_dir saves/Qwen3-VL-4B/lora/beans_sft \
    --overwrite_cache \+
    --overwrite_output_dir \
    --cutoff_len 2048 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 8 \
    --lr_scheduler_type cosine \
    --logging_steps 5 \
    --save_steps 100 \
    --learning_rate 1e-4 \
    --num_train_epochs 5.0 \
    --plot_loss \
    --bf16 true
```

### 使用FSDP （使用0.6B）

根据需要修改`examples/accelerate/fsdp_config.yaml`以及 `examples/extras/fsdp_qlora/qwen3_lora_sft.yaml`，文件然后运行以下命令即可启动 FSDP+QLoRA 微调：

不使用量化的话：注释掉examples/extras/fsdp_qlora/qwen3_lora_sft.yaml的quantization_bit: 4

使用的话需要安装`bitsandbytes`

```bash
conda activate llamafds

bash examples/extras/fsdp_qlora/train.sh
```



### Megatron ❓

