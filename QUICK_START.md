# LLM Guard API 离线部署 - 快速开始

## 什么是离线部署？

离线部署确保：
- ✓ 所有 HuggingFace 模型在构建时下载
- ✓ 模型缓存集成到 Docker 镜像中
- ✓ 容器运行时无需网络连接
- ✓ HuggingFace 自动以离线模式运行

## 快速开始

### 第 1 步：获取 HuggingFace Token

访问 https://huggingface.co/settings/tokens，创建一个 token。

### 第 2 步：预下载模型（可选但推荐）

在构建 Docker 之前，本地验证和缓存所有模型：

```bash
# 安装 huggingface-hub（如果尚未安装）
pip install huggingface-hub

# 下载所有模型到本地缓存
python download_models.py
```

### 第 3 步：构建离线镜像

```bash
export HF_TOKEN=your_token_here
./build_offline.sh
```

或手动构建：

```bash
docker build \
    --secret HF_TOKEN=your_token_here \
    -f llm_guard_api/Dockerfile \
    -t llm-guard-api:latest \
    .
```

### 第 4 步：运行容器

```bash
docker run -p 8000:8000 llm-guard-api:latest
```

## 验证安装

### 1. 检查模型缓存

在本地验证模型：

```bash
python llm_guard_api/verify_models.py
```

在 Docker 中验证模型：

```bash
docker run llm-guard-api:latest python verify_models.py
```

### 2. 测试 API

```bash
curl -X POST http://localhost:8000/scan/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "test prompt",
    "risk_threshold": 0.5
  }'
```

## 模型列表

### 已配置的扫描器（共 5 个）

#### Input Scanners (3个)
- **BanTopics**: 禁止特定主题 (violence, crime, etc.)
- **PromptInjection**: 检测提示注入攻击
- **Toxicity**: 检测有毒内容

#### Output Scanners (5个)
- **BanCode**: 禁止代码输出
- **BanTopics**: 禁止特定主题
- **Gibberish**: 检测无意义文本
- **Toxicity**: 检测有毒内容
- **EmotionDetection**: 检测特定情绪

### 已下载的模型 (10个)

PyTorch 版本：
- MoritzLaurer/deberta-v3-base-zeroshot-v2.0
- protectai/deberta-v3-small-prompt-injection-v2
- unitary/unbiased-toxic-roberta
- vishnun/codenlbert-tiny
- madhurjindal/autonlp-Gibberish-Detector-492513457
- SamLowe/roberta-base-go_emotions
- BAAI/bge-small-zh-v1.5

ONNX 版本（加速推理）：
- ProtectAI/unbiased-toxic-roberta-onnx
- protectai/vishnun-codenlbert-tiny-onnx
- SamLowe/roberta-base-go_emotions-onnx

## 文件说明

### 新增/修改的文件

| 文件 | 说明 |
|------|------|
| `build_offline.sh` | 构建离线镜像的脚本 |
| `download_models.py` | 下载模型到本地缓存 |
| `llm_guard_api/verify_models.py` | 验证模型下载完整性 |
| `llm_guard_api/Dockerfile` | 更新的 Dockerfile（包含模型下载和验证） |
| `llm_guard_api/entrypoint.sh` | 启用离线模式的启动脚本 |
| `llm_guard_api/app/scanner.py` | 添加离线模式支持 |
| `OFFLINE_DEPLOYMENT.md` | 详细的离线部署文档 |

## 故障排除

### 问题：HF_TOKEN 无效

**解决方案**：
1. 检查 token 是否正确
2. token 必须有读权限

### 问题：模型下载超时

**解决方案**：
1. 确保网络稳定
2. 使用断点续传：`huggingface-cli download <model> --resume-download`

### 问题：Docker 构建失败

**解决方案**：
1. 检查 HF_TOKEN 是否设置：`echo $HF_TOKEN`
2. 查看构建日志：`docker build ... 2>&1 | tee build.log`
3. 确保有足够磁盘空间（至少 5GB）

### 问题：运行时模型加载失败

**解决方案**：
1. 检查离线模式是否启用：`docker run <image> env | grep HF_`
2. 验证模型缓存：`docker run <image> ls -la /home/user/.cache/huggingface/hub/`

## 环境变量

### 构建时
- `HF_TOKEN`：HuggingFace 认证 token

### 运行时（自动设置）
- `HF_HUB_OFFLINE=1`：禁用 HF Hub 在线访问
- `TRANSFORMERS_OFFLINE=1`：禁用 Transformers 在线访问
- `HF_DATASETS_OFFLINE=1`：禁用 Datasets 在线访问

### 可选配置
- `LOG_LEVEL`：日志级别（DEBUG/INFO/WARNING/ERROR）
- `LAZY_LOAD`：延迟加载模型（true/false）
- `SCAN_FAIL_FAST`：快速失败模式（true/false）

## 镜像大小参考

- 基础镜像：~160MB
- Python 依赖：~800MB
- HuggingFace 模型：~3.4GB
- **总大小：~4.5GB**

## 更新配置

如需添加新的扫描器：

1. 编辑 `llm_guard_api/config/scanners.yml`
2. 更新 `llm_guard_api/verify_models.py` 中的 `SCANNER_MODELS`
3. 更新 `Dockerfile` 中的模型列表
4. 更新 `download_models.py`
5. 重新构建镜像

## 安全最佳实践

1. **HF_TOKEN 安全**：
   - 仅在构建时使用（不会保存在镜像中）
   - 使用 Docker secrets：`--secret HF_TOKEN=xxx`

2. **网络隔离**：
   - 运行在离线环境中时无需网络
   - 所有模型都在镜像中缓存

3. **镜像签名**：
   - 构建后可对镜像进行签名和验证
   - 在生产环境中部署前扫描漏洞

## 相关文档

- [详细部署指南](OFFLINE_DEPLOYMENT.md)
- [原始模型优化说明](MODEL_OPTIMIZATION.md)
- [LLM Guard 官方文档](https://llm-guard.com/)
- [HuggingFace 离线模式文档](https://huggingface.co/docs/hub/en/security-tokens)

## 支持和帮助

- 检查构建日志：`docker build ... 2>&1 | tee build.log`
- 验证模型：`python llm_guard_api/verify_models.py`
- 查看容器日志：`docker logs <container-id>`
