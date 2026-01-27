# 离线部署指南

## 概述

此配置使 LLM Guard API 能够在完全离线的环境中运行，所有 HuggingFace 模型都在构建时下载并缓存在 Docker 镜像中。

## 配置的扫描器和模型

### Input Scanners
| 扫描器 | 模型 | 大小 |
|--------|------|------|
| BanTopics | MoritzLaurer/deberta-v3-base-zeroshot-v2.0 | ~370MB |
| PromptInjection | protectai/deberta-v3-small-prompt-injection-v2 | ~270MB |
| Toxicity | unitary/unbiased-toxic-roberta | ~500MB |

### Output Scanners
| 扫描器 | 模型 | 大小 |
|--------|------|------|
| BanCode | vishnun/codenlbert-tiny | ~150MB |
| BanTopics | MoritzLaurer/deberta-v3-base-zeroshot-v2.0 | ~370MB |
| Gibberish | madhurjindal/autonlp-Gibberish-Detector-492513457 | ~250MB |
| Toxicity | unitary/unbiased-toxic-roberta | ~500MB |
| EmotionDetection | SamLowe/roberta-base-go_emotions | ~430MB |
| Relevance | BAAI/bge-small-zh-v1.5 | ~430MB |

**总大小**: ~3.4GB（包括ONNX版本）

## 构建离线镜像

### 1. 使用构建脚本（推荐）

```bash
export HF_TOKEN=your_huggingface_token_here
./build_offline.sh
```

或自定义镜像名称和Dockerfile：

```bash
export HF_TOKEN=your_huggingface_token_here
export DOCKER_IMAGE=my-llm-guard:v1.0
export DOCKERFILE=./llm_guard_api/Dockerfile
./build_offline.sh
```

### 2. 手动构建

```bash
docker build \
    --secret HF_TOKEN=your_huggingface_token_here \
    -f llm_guard_api/Dockerfile \
    -t llm-guard-api:latest \
    .
```

## 构建过程

1. **模型下载**：在构建时从 HuggingFace 下载所有配置中使用的模型
2. **模型验证**：使用 `verify_models.py` 验证所有模型是否正确下载
3. **缓存集成**：模型缓存被集成到 Docker 镜像中，路径为 `/home/user/.cache/huggingface/`

## 运行离线容器

### 基本运行

```bash
docker run -p 8000:8000 llm-guard-api:latest
```

### 使用环境变量

```bash
docker run \
    -p 8000:8000 \
    -e LOG_LEVEL=DEBUG \
    -e LAZY_LOAD=true \
    llm-guard-api:latest
```

### 离线模式环境变量

这些变量在 `entrypoint.sh` 中自动设置：

```bash
export HF_DATASETS_OFFLINE=1        # 禁用 HF datasets 在线访问
export TRANSFORMERS_OFFLINE=1       # 禁用 transformers 在线访问
export HF_HUB_OFFLINE=1             # 禁用 HF hub 在线访问
```

## 验证模型

在容器外验证已下载的模型：

```bash
python llm_guard_api/verify_models.py
```

输出示例：

```
INFO:__main__:Checking models in: /home/user/.cache/huggingface
INFO:__main__:Using ONNX models: True
✓ BanTopics: MoritzLaurer/deberta-v3-base-zeroshot-v2.0
✓ PromptInjection: protectai/deberta-v3-small-prompt-injection-v2
✓ Toxicity: unitary/unbiased-toxic-roberta
✓ BanCode: vishnun/codenlbert-tiny
✓ Gibberish: madhurjindal/autonlp-Gibberish-Detector-492513457
✓ EmotionDetection: SamLowe/roberta-base-go_emotions
✓ Relevance: BAAI/bge-small-zh-v1.5

======================================================================
MODEL VERIFICATION REPORT
======================================================================
Total models: 14
Cached models: 14
Missing models: 0
✓ All required models are cached and ready for offline use!
```

## Docker 镜像大小

- **基础镜像**: Python 3.12 slim (~160MB)
- **依赖包**: pip 包依赖 (~800MB)
- **模型缓存**: HuggingFace 模型 (~3.4GB)
- **总大小**: 约 4.5GB

## 离线工作原理

1. **构建时**：
   - 使用 HuggingFace CLI 下载所有模型
   - 验证模型下载完成
   - 模型缓存集成到镜像

2. **运行时**：
   - 启用 HuggingFace 离线模式
   - 所有模型加载来自本地缓存
   - 不尝试网络连接

## 故障排除

### 构建失败：模型下载超时

如果构建因为模型下载超时失败，可以：

1. 确保网络连接稳定
2. 增加下载超时时间
3. 手动下载模型后使用 `--cache-dir` 指定缓存目录

```bash
mkdir -p ~/.cache/huggingface
huggingface-cli download MoritzLaurer/deberta-v3-base-zeroshot-v2.0 \
    --cache-dir ~/.cache/huggingface \
    --resume-download
```

### 运行时找不到模型

如果容器运行时找不到模型：

1. 检查 HF_HUB_OFFLINE 环境变量是否已设置
2. 检查缓存目录权限：

```bash
docker run -it llm-guard-api:latest ls -la /home/user/.cache/huggingface/hub/
```

## 更新配置

如果需要添加或更改扫描器：

1. 更新 `llm_guard_api/config/scanners.yml`
2. 更新 `llm_guard_api/verify_models.py` 中的 `SCANNER_MODELS` 字典
3. 更新 Dockerfile 中的模型下载列表
4. 重新构建镜像

## 安全考虑

- 模型缓存在镜像中，确保只在受信任的网络中共享镜像
- HuggingFace token 仅在构建时使用，不存储在最终镜像中
- 离线模式防止意外的网络连接

## 参考资源

- [HuggingFace Hub 离线模式](https://huggingface.co/docs/hub/en/security-tokens)
- [Transformers 离线使用](https://huggingface.co/docs/transformers/installation#offline-mode)
- [LLM Guard 文档](https://llm-guard.com/)
