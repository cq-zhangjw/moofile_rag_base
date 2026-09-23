# llama-server编译部署+opencode验证记录(Ubuntu, GPU)

> 原文链接：https://blog.csdn.net/qq_36991535/article/details/164249922
> 发布时间：2026-09-01 09:56:04
> 作者：Anesthesia丶

## 背景

之前也用了 vllm 部署 qwen3.8-9b-gptq-int4 版本，其他的没什么，就是感觉显存占用太高了，常驻显存约 16g，基本上没法干其它的事儿了。

ollama 倒是方便，但是对我来讲，感觉模型的管理机制又束缚了我，毕竟我只是想找一个好一点的模型让我用起来，它想加自定义的模型相对不是那么方便。

个人倾向 llama-server 这种一行命令起服务的方式，既没有 vllm 的高显存占用，也没有多余的功能，所以倒腾了一下这个方式。需要的小伙伴可以参考。

## 操作环境

- CPU：i9 13900
- GPU: RTX 3080 20g
- OS：Ubuntu 24.04 (WSL2)
- Driver：591.86
- Model: qwen3.8-9b、mmproj-qwen3.5-9b
- Tool: Opencode

![nvidia-smi](https://p3-doubao-search-sign.byteimg.com/labis/image/52bcbabd4bc5773cf60e38c2c265bc6b~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641899&x-signature=m%2FdeAJNExcNg9QnTlEo3C2KsWXY%3D)

## 1、拉取llama-cpp最新的源码

```bash
git clone https://github.com/ggml-org/llama.cpp.git
```

或者国内用 gitcode：

```bash
git clone https://gitcode.com/GitHub_Trending/ll/llama.cpp.git
```

## 2、安装必要依赖

```bash
apt install -y git build-essential cmake libssl-dev ninja-build
```

## 3、编译源码

```bash
cd llama.cpp
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DLLAMA_BUILD_SERVER=ON -DGGML_CUDA=ON
```

正常结果参考下图：

![编译结果](https://p11-doubao-search-sign.byteimg.com/labis/image/441c75608134ddafdf01801ae01c8ba5~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641899&x-signature=upKcd4vS9wUeMRlX3%2BKjYkKPv2M%3D)

bin目录下会生成 llama-server 文件：

![bin目录](https://p11-doubao-search-sign.byteimg.com/labis/image/332da392f32a45071a2b5b10a7e689f4~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641899&x-signature=kQrQa1XV2hi6LaRUuugGNSn7%2Ff4%3D)

## 4、将 llama-server 加入环境变量

```bash
echo 'export PATH="<编译生成的bin目录>:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

比如，我这儿：

```bash
echo 'export PATH="/home/ai/projects/llama.cpp/build/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

验证输入 `which llama-server`，输出正确的路径，即配置成功。

## 5、gguf模型下载

两个地址，`hf` 会比 `modelscope` 模型全一些，下载速度也会快一点：

- https://hf-mirror.com/models?search=Qwen3.8-9B
- https://www.modelscope.cn/models?name=qwen3.8-9b&page=1&tabKey=task

当然你可以 python 安装 `huggingface` 或 `modelscope`，然后使用 cli 下载，但是不适应于单文件的下载。

这里以 `qwen3.8-9b-Q5_0.gguf` 模型举例，点击对应的下载按钮，浏览器会开始下载。

![gguf模型下载](https://p11-doubao-search-sign.byteimg.com/labis/image/8b22e026cb22dbe8a292e3ee64eee2f9~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641899&x-signature=99PJFRSs%2BNGLc9BFLdfvz13TuYc%3D)

同时为了让 qwen3.8-9b 模型拥有多模态的能力，需要搭配配套的 `mmproj` 模型。

qwen3.8-9b 目前找不到原生的，暂时使用 `mmproject-qwen3.5-9b.gguf` 模型代替。亲测可用~

![mmproj模型下载](https://p11-doubao-search-sign.byteimg.com/labis/image/7489b4dd33de8b6b19fc8614291a2efe~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641899&x-signature=5WAUQFmVkUDD1QsOnr48Z0eGk%2FA%3D)

## 6、测试

```bash
cd <gguf模型所在的目录>
llama-server -m <模型名> --mmproj <mmproj模型名> -c 131072 -ngl 999 --host 0.0.0.0 --port 8088
```

比如，我这：

```bash
cd /home/ai/models/gguf
llama-server -m Qwen3.8-9B-Q5_K_M.gguf --mmproj mmproj-Qwen3.5-9B-BF16.gguf -c 131072 -ngl 999 --host 0.0.0.0 --port 8088
```

启动成功后，大概长这样：

![启动成功](https://p26-doubao-search-sign.byteimg.com/labis/image/9a5808242cbd2177ce9ece6432be9ec8~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641899&x-signature=ZhdK1WyHWzoaTeTd9PONNTeWLZA%3D)

显存占用情况，大约在12g左右：

![显存占用](https://p3-doubao-search-sign.byteimg.com/labis/image/cc7e2066f5a84f64e36588ce70a90acc~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641899&x-signature=3uRNvmLaAyIpZbKu2i0GrHzSF3U%3D)

到这里，基本上已经成功了大半，只差简单的测试即可。

我这里使用 opencode，给了一张简单的证件照让它识别，基本没问题。

![opencode测试](https://p11-doubao-search-sign.byteimg.com/labis/image/650783d6c9706c0b43a4e3c072a8a9be~tplv-be4g95zd3a-896x896.jpeg?lk3s=0ed4045e&x-expires=1805641899&x-signature=o8%2B5Tgx77GfFAU89u1lad1xt17o%3D)
