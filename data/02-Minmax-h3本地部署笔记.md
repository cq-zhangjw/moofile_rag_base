# Minmax h3 本地部署笔记

> 原文链接：https://blog.csdn.net/qq_36991535/article/details/163713487
> 发布时间：2026-08-13 21:43:48
> 作者：Anesthesia丶

之前尝试过部署 wan-2.2 和 LTX 2.3，但是 Wan2.2 没有声音，LTX 没有倒腾成功，总以为是硬件的问题，一度没什么热情。随着 Minimax h3 的开源，据说效果堪比 seedance，而且直出音视频不用后期配音，那我高低得再玩一下子。于是，有了今天这篇笔记。

## 硬件环境

- CPU：i9 13900
- GPU: RTX 3080 20g 魔改
- 主板：
- 内存：ddr4 3200 64g
- 硬盘：Nvme 4.0 固态 4T

## 软件环境

- OS: windows 11
- 驱动：Nvidia-smi 591.86, cuda version 13.1
- Python: 3.10.11
- Torch: torch2.10.0+cu128
- ComfyUI: v0.31.1
- 整合包：ComfyUI-aki-v1.4（绘世启动器2.9.1）
- llama_cpp_python: 0.3.40+cu128

必要的软件会放到最后，需要的小伙伴可以自取。

## 环境构筑

### 1、python 安装

过程不再啰嗦，可以从以下国内镜像地址下载 python 3.10.11 的版本并安装即可。

※ 记得勾选加入环境变量

https://mirrors.aliyun.com/python-release/windows/

然后，设置国内镜像源：

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn
```

### 2、驱动检查

cmd 输入 `nvidia-smi` 确认 `cuda version > 12.8`，如果不满足条件，从官网下载驱动并更新。

### 3、ComfyUI环境构筑

#### 1）整合包（不含模型和插件）

已整理好，可以从 CSDN 资源进行下载：
https://download.csdn.net/download/qq_36991535/93270735

#### 2）custom nodes

需要安装以下自定义节点：

- **XB_ToolBox**: https://github.com/wjluoxiao/XB_ToolBox
- **rgthree-comfy**: https://github.com/rgthree/rgthree-comfy
- **ComfyUI-VideoHelperSuite**: https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
- **ComfyUI-MiniMax-H3-Turbo**: https://github.com/larryvrh/ComfyUI-MiniMax-H3-Turbo
- **ComfyUI-Custom-Scripts**: https://github.com/pythongosssss/ComfyUI-Custom-Scripts

如果没法访问 github，可以搜索国内的 gitee 码云平台，一般都会被复刻过去。

或者可以从 CSDN 资源下载，已经打包好了插件：
https://download.csdn.net/download/qq_36991535/93270738

解压后将内容直接放到 `ComfyUI-aki-v1.4/custom_nodes` 目录下即可。

#### 3）启动与版本切换

启动 `A绘世启动器.exe`，使用版本管理切换 comfyui 版本 > 0.30.0。

等待切换成功后，使用一键启动功能，会自动安装必要的依赖。

不出意外，会出现意外，启动时你会遇到以下这个错误：

```
File "E:\my_projects\ComfyUI-one-click\ComfyUI-aki-v1.4\python\lib\site-packages\torch\_library\infer_schema.py", line 58, in error_fn
raise ValueError(
ValueError: infer_schema(func): Parameter kernel_size has unsupported type list[int].
```

**这是因为 torch 版本过低导致的**，据官方 issue，最新的 comfyui 需要搭配 torch > 2.7 的版本。所以你需要升级 torch 到最新版本。

打开高级选项，从右上角的【启动命令提示符】进入控制台，执行以下命令升级 `torch` 到最新版（使用国内镜像源提速），`xformers` 可能会出现不匹配的问题，需要同步升级：

```bash
pip install -U torch==2.10.0 torchvision torchaudio --index-url https://mirrors.nju.edu.cn/pytorch/whl/cu128
pip install -U xformers --index-url https://mirrors.nju.edu.cn/pytorch/whl/cu128
```

到这里为止，如果正常，此时重新一键启动，会正常进入页面。

你可以尝试加载工作流，大家复制保存成JSON文件，然后使用 comfyui 进行加载即可。

大家也可以从以下网盘获取完整的资源，教程 B站搜索 `机智罗_LX` 讲解相当到位：

https://pan.quark.cn/s/66bca11146b8#/list/share/ea0525dd9cf8463eae93009457b62553

工作流文件名：`59-MiniMax-H3 图片-视频-音频-多参生视频 切换工作流-Lora加速.json`

> 注：完整工作流 JSON 文件较长（约 50KB），原博客中有完整内容，此处略去。可从上述网盘链接获取。

但是加载后你会发现，画面最终会缺少一些节点组件。除此之外，你还需要安装 llama_cpp_python，俗称轮子。

执行以下命令进行安装（同样需要进入高级选项的控制台）：

文件可以从这下载：
https://download.csdn.net/download/qq_36991535/93270740

```bash
pip install llama_cpp_python-0.3.40+cu128-cp310-cp310-win_amd64.whl
```

最后重启 comfyui，刷新浏览器，你会发现一切都似乎 OK 了，只需下载必要的模型即可。

## 模型下载

### 1）目录存放结构

```
diffusion_models/
├── minimax_h3_fl2va_pruned_int8_convrot.safetensors
├── minimax_h3_fl2va_int8_convrot.safetensors
├── minimax_h3_ref2va_int8_convrot.safetensors
└── minimax_h3_ref2va_pruned_int8_convrot.safetensors

loras/
├── minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors
├── minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy_resized_avg_rank_21_bf16.safetensors
└── minimax_h3_turbo_4step_ema_ckpt850.safetensors

vae/
├── minimax_h3_audio_vae_fp32.safetensors
└── minimax_h3_video_vae_fp16.safetensors

text_encoders/
└── qwen3vl_32b_minimax_h3_int8_convrot.safetensors
```

### 2）下载地址

对号下载即可：

- https://hf-mirror.com/lightx2v/Minimax-h3-Turbo/tree/main
- https://hf-mirror.com/Kijai/MiniMax-H3_comfy/tree/main/loras
- https://hf-mirror.com/Comfy-Org/MiniMax-H3/tree/main

最后按照上面的目录结构放置，刷新浏览器即可。

## 测试运行

到目前为止应该一切都搞定了，只差运行测试效果。

没法贴视频。贴个图意思一下~

不会写提示词，直接借鉴了这个网站上的：
https://tryminimax.asia/zh/minimax-h3-prompts

最后的结果，感觉还像那么回事。

- 4步加速lora，8步生成
- 9:16 480p
- 生成时间在 20-30分钟左右。
