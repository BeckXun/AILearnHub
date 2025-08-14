# AI Learning Hub - AI学习项目集

这是一个包含多个 AI 相关学习项目的代码库，涵盖了 Agent 系统、MCP 协议、RAG 系统等前沿技术的实践示例。

## 项目结构

### 🤖 Agent 系统学习

#### 1. Agent的概念、原理与构建模式
- **路径**: `agent-concepts-and-patterns/`
- **描述**: Agent 基础概念学习和实践，包含一个完整的贪吃蛇游戏 Agent 示例
- **特色**: 通过游戏场景深入理解 Agent 的工作原理

#### 2. A2A协议深度解析(1)
- **路径**: `a2a-protocol-deep-dive-1/`
- **描述**: Agent-to-Agent 协议学习第一部分，包含天气查询 Agent
- **功能**: 演示基础的 A2A 通信机制

#### 3. A2A协议深度解析(2)
- **路径**: `a2a-protocol-deep-dive-2/`
- **描述**: A2A 协议学习进阶部分，包含机票查询和天气查询两个 Agent
- **功能**: 展示复杂的多 Agent 协作场景

### 🔗 MCP 协议学习

#### 4. MCP 与 Function Calling 到底什么关系
- **路径**: `mcp-and-function-calling/MarkChat/`
- **描述**: 深入理解 Model Context Protocol (MCP) 与函数调用的关系
- **应用**: MarkChat - 一个基于 MCP 的聊天应用

#### 5. MCP终极指南-进阶篇
- **路径**: `mcp-ultimate-guide-advanced/`
- **描述**: MCP 协议的进阶学习，包含实际的天气服务 MCP 实现

#### 6. MCP终极指南-番外篇
- **路径**: `mcp-ultimate-guide-extras/`
- **描述**: MCP 学习的扩展资料，包含各种系统提示词模板
- **资源**: Cline 系统提示词、ReAct 系统提示词等

### 🔍 RAG 系统构建

#### 7. 使用Python构建RAG系统
- **路径**: `python-rag-system/rag/`
- **描述**: 从零开始构建检索增强生成 (RAG) 系统
- **技术栈**: Sentence Transformers, ChromaDB, Google Gemini API

## 环境要求

### 基础环境
- **Python**: 3.8+
- **包管理器**: [uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Jupyter**: 用于 RAG 系统学习 (可选)

### API 密钥配置

大部分项目需要 AI 服务的 API 密钥，请在对应项目目录下创建 `.env` 文件：

#### OpenRouter API (Agent 项目)
```bash
# .env
OPENROUTER_API_KEY=sk-xxx
```

#### Google Gemini API (RAG 项目)
```bash
# .env
GEMINI_API_KEY=xxx
```

获取 API 密钥：
- [OpenRouter](https://openrouter.ai/)
- [Google AI Studio](https://aistudio.google.com/apikey)

## 快速开始

### 1. 运行 Agent 贪吃蛇游戏
```bash
cd "agent-concepts-and-patterns"
# 创建 .env 文件并配置 OPENROUTER_API_KEY
uv run agent.py snake
```

### 2. 启动 MarkChat 聊天应用
```bash
cd "mcp-and-function-calling/MarkChat"
# 创建 .env 文件并配置 OPENROUTER_API_KEY
uv run start.py
# 访问 http://localhost:5000
```

### 3. 学习 RAG 系统构建
```bash
cd "python-rag-system/rag"
# 创建 .env 文件并配置 GEMINI_API_KEY
uv add sentence_transformers chromadb google-genai python-dotenv
uv run --with jupyter jupyter lab
```

### 4. 启动天气 Agent 服务
```bash
cd "a2a-protocol-deep-dive-1/weather"
uv run .
```

## 学习路径建议

### 入门路径
1. **Agent 概念学习** → `agent-concepts-and-patterns/`
2. **简单 A2A 通信** → `a2a-protocol-deep-dive-1/`
3. **RAG 系统基础** → `python-rag-system/`

### 进阶路径
1. **复杂 Agent 协作** → `a2a-protocol-deep-dive-2/`
2. **MCP 协议深入** → `mcp-ultimate-guide-advanced/`
3. **实际应用开发** → `mcp-and-function-calling/`

### 高级路径
1. **系统提示词工程** → `mcp-ultimate-guide-extras/`
2. **多 Agent 系统设计**
3. **生产级 AI 应用开发**

## 技术栈

- **AI 框架**: 自定义 Agent 框架
- **语言模型**: 通过 OpenRouter 访问各种 LLM
- **向量数据库**: ChromaDB
- **嵌入模型**: Sentence Transformers
- **Web 框架**: Flask (MarkChat)
- **前端**: HTML/CSS/JavaScript
- **包管理**: uv

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个学习资源库！

## 许可证

本项目仅用于学习和研究目的。

---

**开始你的 AI 学习之旅吧！** 🚀
