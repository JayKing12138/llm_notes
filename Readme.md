# LLM Notes

在较为有限的条件（NVIDIA GeForce RTX 3060 × 2，CUDA Version: 12.8）下实现单机多卡下的部署、推理、微调、评估、个性化项目的实现等。

unsloth、Llama-Factory等可以使用docker拉取到本地，但是选择使用pypi等自己构建基本环境，熟悉具体流程、解决构建环境时发生的各种依赖矛盾等问题。

使用**modelsscope**、**hugging face**。

对于使用Qwen、Llama等大模型进行LoRA或GRPO等参数高效微调，可直接选用Unsloth、Llama-Factory、Swift等高层框架。若涉及更复杂的模型结构修改或定制化训练需求，则需依赖TRL、PEFT、Transformers等底层库进行深度开发。

## 环境设置

![Alt text](IMAGES/image.png)

## 推理

## 评估

### evalscope


## 部署

### vllm 

[`vllm/start_vllm_server.md`](vllm/start_vllm_server.md)

### open-webui

# 微调

### unsloth

### Llama Factory

### Swift


### Colossal-AI

### TRL

# AI Agent