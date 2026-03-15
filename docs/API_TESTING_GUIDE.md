# API 测试指南

本文档介绍如何使用提供的 Python 脚本测试 Qwen API。

## 准备工作

1. 确保已安装 Python 3.x
2. 安装依赖库：
   ```bash
   pip install requests
   ```

## 配置 API 参数

编辑 [config.json](file:///e:/TsetRange9/Qwen3/config.json) 文件，更新以下参数：

- `api_base_url`: API 服务的基础 URL
- `api_token`: API 访问令牌
- `default_model`: 默认使用的文本模型
- `default_image_model`: 默认使用的图像模型

或者，您可以使用环境变量设置参数：

```bash
export QWEN_API_BASE="http://your-api-url:port"
export QWEN_API_TOKEN="your-token-here"
```

## 运行测试

执行以下命令运行测试脚本：

```bash
python test_api.py
```

## 支持的 API 功能

### 1. 聊天完成

兼容 OpenAI 的 [/v1/chat/completions](file:///e:/TsetRange9/Qwen3/docker-compose.yml#L3-L15) 接口，可用于文本对话。

### 2. 图像生成

兼容 OpenAI 的 [/v1/images/generations](file:///e:/TsetRange9/Qwen3/docker-compose.yml#L3-L15) 接口，根据文本提示生成图像。

### 3. 文档解读

使用 [/v1/chat/completions](file:///e:/TsetRange9/Qwen3/docker-compose.yml#L3-L15) 接口处理文档，提供文件 URL 和相关问题。

### 4. 图像解读

使用 [/v1/chat/completions](file:///e:/TsetRange9/Qwen3/docker-compose.yml#L3-L15) 接口分析图像内容。

### 5. Token 检查

使用 [/token/check](file:///e:/TsetRange9/Qwen3/docker-compose.yml#L3-L15) 接口验证认证令牌是否有效。

## 错误处理

如果遇到错误，请检查：

1. API 服务是否正在运行
2. 认证令牌是否正确
3. 网络连接是否正常
4. 请求格式是否符合 API 规范

## 注意事项

- 请勿频繁调用 token 检查接口（间隔至少10分钟）
- 在生产环境中妥善保管 API 令牌
- 根据实际需求调整请求频率，避免对 API 服务造成过大压力