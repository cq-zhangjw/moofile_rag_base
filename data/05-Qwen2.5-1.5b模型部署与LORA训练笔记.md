# Qwen2.5-1.5b 模型部署与LORA训练笔记

> 原文链接：https://blog.csdn.net/qq_36991535/article/details/160481241
> 发布时间：2026-04-24 21:41:31
> 作者：Anesthesia丶

这两天心血来潮，想了解一下小模型的部署与训练的过程，刚好家里有张 3080 魔改 20g 可以试试水，于是说干就干~ 在这里简单记录以下相关的笔记。

## 一、VLLM 环境构筑

本来是想用现成的镜像的，但是国内 docker 受限，以下镜像源又找不到适合我的 GPU 版本，主要是有些带 cuda 版本，有些又不带 cuda 版本，带 cuda 版本的只能找到 cuda13.0，我的驱动最高支持 cuda 12.6，实在是不想折腾驱动，所以决定自己搭。

参考镜像站：
- https://1ms.run/search
- https://docker.aityp.com/

所幸还不是特别麻烦，我是基于我自己已经折腾过的环境继续造的，基本上没费啥事儿。

现有环境：

- 硬件: i9 13900 + Nvidia 3080 20g
- 系统环境：ubuntu24.04 + Driver Version: 560.94
- 基础环境：docker + ubuntu24.04 + cuda12.6 + python3.12.3 + pyTorch2.7.1，且预装了很多常用的依赖包

在这个环境的基础上，只需要做两件事：

### 1. 升级 torch 版本至 2.10.0

主要是发现安装 `vllm==0.19.1` 时会安装这个版本的 torch。因为是纯环境构筑，没有什么版本的特别要求，不如反过来适配 `vllm`。

```bash
pip install torch==2.10.0 torchvision torchaudio -f https://mirrors.aliyun.com/pytorch-wheels/cu126/
python -c "import torch; print(torch.version.cuda); print(torch.cuda.is_available())"
```

### 2. 安装 vllm 版本至 0.19.1

```bash
python -m pip install vllm==0.19.1
```

然后，你可以执行以下命令成功启动 `qwen2.5-1.5b-instruct` 模型。

当然模型需要提前执行以下命令进行下载：

```bash
pip install modelscope
modelscope download Qwen/Qwen2.5-1.5B-Instruct --local_dir qwen2.5-1.5b-Instruct
```

启动服务：

```bash
python3.12 -m vllm.entrypoints.openai.api_server \
  --model qwen2.5-1.5b-Instruct \
  --served-model-name qwen2.5-1.5b-instruct \
  --dtype auto \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --trust-remote-code \
  --host 0.0.0.0 \
  --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --api-key xxx
```

这里有两个注意点：

- 如果你需要开启模型的工具能力，需要指定 `--enable-auto-tool-choice` 和 `--tool-call-parser qwen3_coder` 参数。
- `--api-key` 参数一定要指定，不然请求的时候死活过不去~

测试参考代码：

```python
import requests

url = "http://192.168.3.28:8088/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer xxx"
}
data = {
    "model": "qwen2.5-1.5b-instruct",
    "messages": [
        {"role": "user", "content": "写一个Python的斐波那契数列"}
    ],
    "temperature": 0.2,
    "stream": False
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code, response.text)
```

至此，第一步完活。

## 二、训练环境准备

有了第一步的环境打底，这个就顺畅多了，基本没什么问题，执行以下命令即可。

```bash
pip install -r requirements.txt
```

`requirements.txt`：

```
transformers
datasets
peft
bitsandbytes
accelerate
huggingface-hub
sentencepiece
```

### 训练数据示例

`training_data.jsonl`（温柔人设对话示例）：

```jsonl
{"messages": [{"role": "user", "content": "我今天心情特别差，什么事都不顺心。"}, {"role": "assistant", "content": "抱抱你呀，辛苦啦🥺 生活偶尔就是会有一段乱糟糟的低谷期，不是你不够好，只是当下刚好有点累啦。慢慢来没关系，累了就好好歇一歇，我一直都在这里陪着你呀。"}]}
{"messages": [{"role": "system", "content": "你是一位温柔知性、善解人意的女生，说话语气柔软、耐心体贴，擅长安慰、开导、鼓励别人，永远传递温暖、包容与正能量，情商很高，懂得共情与换位思考。"}, {"role": "user", "content": "感觉自己好没用，什么都做不好。"}, {"role": "assistant", "content": "不许这么否定自己呀。每个人都有暂时做不好、会笨拙的时候，这一点都不代表你差劲。你已经在很努力地撑住一切，就已经非常了不起啦。给自己多一点时间和宽容，你真的比自己想象里优秀很多✨"}]}
```

> 注：原博客中有 15 条完整的温柔人设对话训练样本，此处仅展示格式示例。

### 训练代码

```python
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model

# ====================== 基础配置 ======================
MODEL_NAME = "/mnt/e/models/llm/qwen2.5-1.5b-instruct"  # 纯基座模型
DATA_PATH = "data/train_converter.jsonl"
OUTPUT_DIR = "output/checkpoints"
DEVICE = "cuda"

# ====================== LoRA ======================
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# ====================== 加载模型 & 分词器 ======================
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ====================== 格式化对话 + labels ======================
def format_and_tokenize(examples):
    conversations = []
    for messages in examples["messages"]:
        text = ""
        for msg in messages:
            text += f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>\n"

        tokenized = tokenizer(
            text,
            max_length=1024,
            truncation=True,
            padding="max_length",
        )
        tokenized["labels"] = tokenized["input_ids"].copy()
        conversations.append(tokenized)

    return {
        "input_ids": [x["input_ids"] for x in conversations],
        "attention_mask": [x["attention_mask"] for x in conversations],
        "labels": [x["labels"] for x in conversations],
    }

# ====================== 加载数据 ======================
dataset = load_dataset("json", data_files=DATA_PATH, split="train")
dataset = dataset.map(
    format_and_tokenize,
    batched=True,
    remove_columns=["messages"]
)

# ====================== 训练参数 ======================
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=1.5e-4,
    num_train_epochs=3,
    logging_steps=5,
    save_strategy="epoch",
    bf16=True,
    fp16=False,
    optim="paged_adamw_8bit",
    report_to="none",
    save_total_limit=2,
)

# ====================== 训练 ======================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
)
trainer.train()
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print("训练完成！LoRA 保存至：", OUTPUT_DIR)
```

### 推理测试代码（加载基座 + LoRA）

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

BASE_MODEL_PATH = "/mnt/e/models/llm/qwen2.5-1.5b-instruct"
LORA_WEIGHT_PATH = "./output/checkpoints"

# 加载基座
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

# 挂载训练好的 LoRA
model = PeftModel.from_pretrained(base_model, LORA_WEIGHT_PATH)
model = model.eval()

SYSTEM_PROMPT = "你是一位温柔知性、善解人意的女生，说话语气柔软、耐心体贴，擅长安慰、开导、鼓励别人，永远传递温暖、包容与正能量，情商很高，懂得共情与换位思考。"

def chat(user_input):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id
        )
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return full_text.split("assistant\n")[-1].strip()

if __name__ == "__main__":
    print("模型加载完成，开始聊天吧！输入 exit 退出")
    while True:
        user_q = input("\n你：")
        if user_q.lower() in ["exit", "quit"]:
            break
        res = chat(user_q)
        print(f"AI：{res}")
```

### 合并 LoRA 到基座模型

将 LoRA 合并到 `qwen2.5-1.5b-instruct`，然后就可以使用 vllm 部署新训练的模型了：

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL_PATH = "/mnt/e/models/llm/qwen2.5-1.5b"
LORA_PATH = "./output/checkpoints/checkpoint-68538"
SAVE_PATH = "./output/checkpoints/qwen2.5-1.5b-lora-merged"

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

model = PeftModel.from_pretrained(base_model, LORA_PATH)

print("开始合并 LoRA → 完整模型...")
model = model.merge_and_unload()

model.save_pretrained(SAVE_PATH, safe_serialization=True)
tokenizer.save_pretrained(SAVE_PATH)
print(f"合并完成！模型已保存到：\n{SAVE_PATH}")
```

## 三、正式训练

正式训练之前需要准备一些你需要让大模型学习的数据，俗称训练数据，并且人工校对，并按照上述示例格式进行整理。

直接从魔搭找了一个开源数据集，效果不会很好，只是为了做实验嘛~

https://www.modelscope.cn/datasets/qiaojiedongfeng/qiaojiedongfeng/file/view/master/train.jsonl?id=27628&status=2

整整 10 万+ 条。

基座模型没有使用 `qwen2.5-1.5b-instruct`，而是不带 instruct 的 base 版本，也就是预训练模型。它只有海量的知识，不知道怎么组织语言，基本上是没法直接使用的状态。

妄想通过这 10w+ 数据让其拥有对话能力，然后自定义 NSFW 规则，懂得都懂，然想的太简单了~

`10w+` 数据，在现有配置上，跑了 `36小时`，完成度 `70%`，`2.1` 个 epoch。

从结果看，还是有一定的效果的：

- 训练过的数据基本上能回答对
- 关键是并不是原样输出，是有自己的调整在里面的

## 四、写在最后

以上就是本次的一个探索，至少整个流程基本上算是了解了。由于缺乏专业的知识、设备以及合理的数据，普通人要做这件事还是要花费不少的时间和精力的，感叹科研人员的无私奉献~

道阻且长，愿我们都能保持这份热爱，学到老活到老！~
