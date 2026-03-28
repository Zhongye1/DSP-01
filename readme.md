## 数据结构习题集整理：

使用 `pdflatex` 命令将.tex文件编译为PDF文档：

```
pdflatex 数据结构2009-题库.tex
```

### 2. 使用LaTeX编辑器

- TeXstudio
- TeXmaker
- Overleaf（在线编辑器）
- WinEdt
- VSCode配合LaTeX Workshop插件

### 转换为Word文档

```bash
pandoc 数据结构2009-题库.tex -o 数据结构2009-题库.docx
```

或使用脚本

```bash
python convert_latex_to_word.py
```

## Workspace

Workspace目录包含了一系列用于处理数据结构试题的工具和API接口，主要包括以下几个部分：

1. **PDF处理** ([ans408ocr.py](file:///e:/TsetRange9/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84/workspace/ans408ocr.py))
    - 用于解析PDF格式的试卷并按年份分类试题
    - 集成了MinerU API进行OCR识别和内容提取
    - 提取文件名中的年份信息并自动分类

2. **试题转换模块** ([convert_to_questions.py](file:///e:/TsetRange9/%E6%8D%AE%E7%BB%93%E6%9E%84/workspace/convert_to_questions.py))
    - 将提取的试题内容按照教材章节进行分类
    - 支持连接本地LLM服务（如Ollama）或自定义API进行智能分类
    - 根据章节关键词映射，自动将题目归类到对应章节（如线性表、栈和队列、树与二叉树等）

### 部署配置

- **Docker Compose**: 使用[docker-compose.yml](file:///e:/TsetRange9/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84/workspace/docker-compose.yml)文件进行容器化部署
- **环境变量**: 配置了Asia/Shanghai时区，端口映射到8000
- **配置文件**: [config.json](file:///e:/TsetRange9/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84/workspace/config.json)中保存API基本配置信息

### 数据存储

- 结果文件夹：存储各年份的content_list.json、model.json等处理结果
- 按年份分类存储，便于管理不同年份的数据

### API接口

工作区提供兼容OpenAI的接口，支持以下功能：

- `/v1/chat/completions`: 对话补全接口
- `/v1/images/generations`: AI绘图接口
- 文档解读和图像解析功能
- token存活检测功能

### 环境依赖

- Python运行环境
- LLM服务（如Ollama或其他API服务）
- Docker和Docker Compose（用于容器化部署）
