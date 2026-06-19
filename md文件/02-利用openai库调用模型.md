# 02 - 利用 OpenAI 库调用模型

> 学习使用 OpenAI SDK 进行标准的对话式调用，掌握 messages 消息结构

---

## 📚 一、代码概述

本代码演示了**标准的 OpenAI 对话调用方式**，展示了如何通过 `messages` 数组构建多角色对话，是大模型应用开发的基础。

### 1.1 核心功能

- ✅ 使用环境变量配置 API Key（更安全）
- ✅ 构建包含 system、user、assistant 三种角色的对话
- ✅ 获取并打印 AI 回复内容

---

## 🔧 二、核心代码解析

### 2.1 初始化客户端

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
)
```

**改进点**：使用 `os.getenv("OPENAI_API_KEY")` 从环境变量读取 API Key，而不是硬编码。

> 💡 **设置环境变量的方法**：
> - Windows: `set OPENAI_API_KEY=sk-xxx`
> - Mac/Linux: `export OPENAI_API_KEY=sk-xxx`
> - Python 项目中推荐使用 `python-dotenv` 库加载 `.env` 文件

### 2.2 构建对话消息

```python
response = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {'role':'system','content':'你是一个Python编程专家，并且不说废话简单回答'},
        {'role':'assistant','content':'好的，我是编程专家，并且话不多，你要问什么？'},
        {'role':'user','content':'输出1-10的数字，使用python代码'},
    ]
)
```

**messages 数组结构详解：**

```
┌─────────────────────────────────────────┐
│  [0] system: 设定AI身份和行为规则        │  ← 系统提示
├─────────────────────────────────────────┤
│  [1] assistant: AI的历史回复             │  ← 历史对话
├─────────────────────────────────────────┤
│  [2] user: 用户的当前问题                │  ← 当前输入
└─────────────────────────────────────────┘
```

**三种角色的作用：**

| 角色 | 作用 | 是否必须 |
|-----|------|---------|
| `system` | 设定 AI 的人设、行为规范、输出格式等 | 可选但推荐 |
| `user` | 用户的提问或输入 | 必须 |
| `assistant` | AI 的历史回复，用于上下文连贯 | 可选（多轮对话需要） |

### 2.3 获取回复内容

```python
print(response.choices[0].message.content)
```

**返回对象的访问路径：**

```
response
  └── choices (列表)
        └── [0] (第一个选择)
              └── message
                    └── content (回复文本)
```

> 💡 为什么是 `choices[0]`？
> 
> 因为大模型可以一次生成多个候选回复（通过 `n` 参数控制），默认生成 1 个，所以取第 0 个。

---

## 💡 三、关键知识点

### 3.1 System Prompt 的重要性

`system` 角色的提示词是**控制 AI 行为的关键**，可以用来：

| 用途 | 示例 |
|-----|------|
| **设定身份** | "你是一个Python编程专家" |
| **设定风格** | "回答言简意赅，不说废话" |
| **设定格式** | "输出JSON格式" |
| **设定约束** | "只回答技术问题，拒绝其他话题" |

### 3.2 对话的工作原理

大模型本身是**无状态**的，每次调用都是独立的。所谓"对话"，其实是：

```
每次调用都把完整的历史对话一起发给模型
模型根据全部上下文生成下一句回复
```

**示意图：**

```
第1次调用：  [system, user问题1] → AI回复1
第2次调用：  [system, user问题1, AI回复1, user问题2] → AI回复2
第3次调用：  [system, user问题1, AI回复1, user问题2, AI回复2, user问题3] → AI回复3
...
```

> ⚠️ 这就是为什么对话越长，消耗的 token 越多——因为每次都要把全部历史重新发送一遍。

### 3.3 为什么要有 assistant 历史消息？

在示例中，我们手动加了一条 `assistant` 消息：
```python
{'role':'assistant','content':'好的，我是编程专家，并且话不多，你要问什么？'}
```

**作用：**
1. **模拟历史对话**：让模型觉得这是对话的延续
2. **引导回答风格**：通过示例回复来引导模型的回答方式
3. **Few-shot 学习**：给模型看几个例子，它就能学会模式

---

## 🎯 四、常见使用模式

### 4.1 单轮问答（最简单）

```python
messages = [
    {"role": "user", "content": "什么是Python？"}
]
```

### 4.2 带人设的问答

```python
messages = [
    {"role": "system", "content": "你是一个幽默的老师"},
    {"role": "user", "content": "什么是Python？"}
]
```

### 4.3 多轮对话

```python
messages = [
    {"role": "system", "content": "你是一个编程助手"},
    {"role": "user", "content": "怎么定义变量？"},
    {"role": "assistant", "content": "用 = 号，比如 x = 1"},
    {"role": "user", "content": "那怎么定义列表？"}  # 继续追问
]
```

---

## ⚠️ 五、注意事项

1. **消息顺序很重要**：必须按时间顺序排列，user 和 assistant 交替出现
2. **不要漏掉历史**：每次新的提问都要带上之前的所有对话历史
3. **注意 token 限制**：对话太长会超出模型的上下文窗口，需要截断或摘要
4. **system 放最前面**：系统提示词通常放在 messages 数组的第一个位置

---

## 📝 六、完整示例模板

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 对话历史（实际项目中可以用列表维护）
messages = [
    {"role": "system", "content": "你是一个 helpful 的助手"},
]

# 模拟多轮对话
while True:
    user_input = input("你: ")
    if user_input == "退出":
        break
    
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=messages
    )
    
    reply = response.choices[0].message.content
    print(f"AI: {reply}")
    
    # 把AI回复也加入历史
    messages.append({"role": "assistant", "content": reply})
```

---

> 💡 **学习建议**：理解 messages 数组的结构是掌握大模型开发的关键。试着自己写一个简单的命令行聊天程序，体会多轮对话的实现方式。
