# 09 - LangChain 访问通义千问大模型

> 学习使用 LangChain 框架调用通义千问大模型，了解 LLM 组件的基本用法

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 框架调用通义千问大模型**的最简单方式，是 LangChain 入门的第一步。

### 1.1 核心功能

- ✅ 使用 LangChain 的 LLM 组件
- ✅ 调用通义千问（qwen-plus）模型
- ✅ 最简单的 invoke 调用方式

### 1.2 为什么用 LangChain？

LangChain 是一个大模型应用开发框架，它的优势是：

| 优势 | 说明 |
|-----|------|
| **统一接口** | 不同大模型用同样的调用方式 |
| **组件丰富** | 提示词模板、记忆、链、代理等 |
| **易于扩展** | 可以方便地组合各种组件 |
| **生态完善** | 集成了大量第三方工具和服务 |

---

## 🔧 二、核心代码解析

### 2.1 导入模型类

```python
from langchain_community.llms.tongyi import Tongyi
```

**导入路径说明**：

| 路径部分 | 说明 |
|---------|------|
| `langchain_community` | LangChain 社区贡献的集成包 |
| `llms` | 大语言模型（LLM）模块 |
| `tongyi` | 通义千问的具体实现 |
| `Tongyi` | 模型类名 |

> 💡 LangChain 把模型分为两类：
> - **LLM**：文本补全模型（输入一段文本，输出续写）
> - **Chat Model**：对话模型（输入消息列表，输出回复）
> 
> 这里用的是 LLM 类。

### 2.2 初始化模型

```python
model = Tongyi(
    model = "qwen-plus"
)
```

**初始化参数**：

| 参数 | 说明 | 示例 |
|-----|------|------|
| `model` | 模型名称 | `"qwen-plus"` |

**常见的通义千问模型**：

| 模型名 | 说明 |
|-------|------|
| `qwen-turbo` | 快速版，性价比高 |
| `qwen-plus` | 增强版，效果更好 |
| `qwen-max` | 最强版，能力最强 |

> 💡 API Key 怎么配置？
> 
> LangChain 会自动从环境变量 `DASHSCOPE_API_KEY` 中读取 API Key。也可以在初始化时传入 `dashscope_api_key` 参数。

### 2.3 调用模型

```python
response = model.invoke("你是谁，能干嘛？？")
print(response)
```

**invoke 方法**：

- 输入：字符串（提示词）
- 输出：字符串（模型回复）

这是最简单的调用方式，直接传一个字符串进去，得到一个字符串回复。

---

## 💡 三、关键知识点

### 3.1 LangChain 的模型分类

LangChain 中有两种主要的模型接口：

| 类型 | 类名 | 输入 | 输出 | 适用场景 |
|-----|------|------|------|---------|
| **LLM** | `Tongyi` / `OpenAI` | 字符串 | 字符串 | 文本补全、生成 |
| **Chat Model** | `ChatTongyi` / `ChatOpenAI` | 消息列表 | 消息对象 | 对话、聊天 |

**区别**：
- LLM 是"文本进，文本出"，比较简单
- Chat Model 是"消息列表进，消息出"，支持多角色对话

### 3.2 invoke 方法

`invoke()` 是 LangChain 中最基本的调用方法：

```python
# 输入一个值，输出一个值
result = model.invoke(input)
```

这是所有 Runnable 组件的统一接口，包括模型、提示词模板、链等等。

> 💡 LangChain 的核心设计理念是"一切都是 Runnable"，所有组件都有相同的调用接口（invoke、stream、batch 等），可以像搭积木一样组合。

### 3.3 LangChain 的版本变化

LangChain 经历了比较大的架构调整：

| 版本 | 特点 |
|-----|------|
| 旧版（0.0.x） | 所有东西都在 langchain 包里 |
| 新版（0.1+） | 拆分成 langchain、langchain-core、langchain-community 等包 |

**导入路径的变化**：
```python
# 旧版
from langchain.llms import Tongyi

# 新版
from langchain_community.llms import Tongyi
# 或
from langchain_community.llms.tongyi import Tongyi
```

---

## 🎯 四、LLM 的其他调用方式

### 4.1 批量调用 batch

```python
# 一次调用多个提示词
results = model.batch(["你好", "介绍一下Python"])
for r in results:
    print(r)
```

### 4.2 流式输出 stream

```python
# 流式输出，逐块返回
for chunk in model.stream("写一首关于春天的诗"):
    print(chunk, end="", flush=True)
```

### 4.3 异步调用 ainvoke

```python
# 异步调用，适合并发场景
result = await model.ainvoke("你好")
```

---

## ⚠️ 五、注意事项

1. **API Key 配置**：确保环境变量 `DASHSCOPE_API_KEY` 已设置，或者在初始化时传入
2. **模型名称正确**：不同供应商的模型名不一样，注意拼写
3. **LLM vs Chat Model**：根据需求选择合适的接口类型，对话场景推荐用 Chat Model
4. **导入路径**：注意 LangChain 版本，不同版本导入路径可能不同
5. **异常处理**：实际项目中要处理网络异常、超时、限流等情况

---

## 📝 六、常见模型对比

| 供应商 | LLM 类 | Chat Model 类 | 环境变量 |
|-------|--------|--------------|---------|
| **通义千问** | `Tongyi` | `ChatTongyi` | `DASHSCOPE_API_KEY` |
| **OpenAI** | `OpenAI` | `ChatOpenAI` | `OPENAI_API_KEY` |
| **文心一言** | `Ernie` | `ChatErnie` | `ERNIE_API_KEY` |
| **智谱 AI** | `ZhipuAI` | `ChatZhipuAI` | `ZHIPUAI_API_KEY` |

> 💡 虽然供应商不同，但使用方式基本一样。这就是 LangChain "统一接口"的好处——换模型只需要改初始化的代码。

---

## 🔍 七、LangChain 核心概念

### 7.1 Runnable 协议

LangChain 的核心抽象是 **Runnable**，所有组件都实现了这个接口：

| 方法 | 作用 |
|-----|------|
| `invoke()` | 同步调用，输入一个，输出一个 |
| `stream()` | 流式输出，逐块返回 |
| `batch()` | 批量调用，输入多个，输出多个 |
| `ainvoke()` | 异步版本的 invoke |
| `astream()` | 异步版本的 stream |
| `abatch()` | 异步版本的 batch |

### 7.2 链式调用

Runnable 之间可以用 `|` 运算符连接，形成链（Chain）：

```python
chain = prompt | model | output_parser
```

这是 LangChain 最强大的特性之一，后面会详细学习。

---

## 💡 八、快速上手模板

```python
from langchain_community.llms.tongyi import Tongyi

# 1. 初始化模型
model = Tongyi(model="qwen-plus")

# 2. 普通调用
response = model.invoke("你好，请介绍一下你自己")
print(response)

# 3. 流式调用
print("\n--- 流式输出 ---")
for chunk in model.stream("写一首短诗"):
    print(chunk, end="", flush=True)
```

---

> 💡 **学习建议**：这是 LangChain 的入门第一步。先确保能跑通基本调用，然后再学习提示词模板、记忆、链等更高级的功能。试着换几个不同的模型（如果有 API Key 的话），体会统一接口的便利。
