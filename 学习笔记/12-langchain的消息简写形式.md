# 12 - LangChain 的消息简写形式

> 学习使用元组形式的消息简写，更简洁地构建对话消息

---

## 📚 一、代码概述

本代码演示了**使用元组形式的消息简写**来构建对话，不需要导入消息类，直接用 `("role", "content")` 的格式即可。

### 1.1 核心功能

- ✅ 使用元组简写形式表示消息
- ✅ 无需导入 SystemMessage、HumanMessage 等类
- ✅ 支持 system、human、ai 三种角色
- ✅ 可用于 Few-Shot 示例构建

---

## 🔧 二、核心代码解析

### 2.1 导入模型

```python
from langchain_community.chat_models.tongyi import ChatTongyi
```

只需要导入模型类，不需要导入各种消息类。

### 2.2 用元组构建消息列表

```python
messages = [
    ("system", "你是一名唐诗大家，回答言简意赅，我给你上句，你接下句"),
    ("human", "床前明月光"),
    ("ai", "疑是地上霜"),
    ("human", "举头望明月"),
    ("ai", "低头思故乡"),
    ("human", "白日依山尽")
]
```

**元组格式**：

```python
("角色", "内容")
```

**角色对应关系**：

| 元组形式 | 完整写法 | 说明 |
|---------|---------|------|
| `("system", "...")` | `SystemMessage(content="...")` | 系统设定 |
| `("human", "...")` | `HumanMessage(content="...")` | 用户消息 |
| `("ai", "...")` | `AIMessage(content="...")` | AI 回复 |

### 2.3 流式调用

```python
model = ChatTongyi(model="qwen-plus")

response = model.stream(input=messages)
for i in response:
    print(i.content, end="", flush=True)
```

调用方式和之前一样，模型会自动把元组转换成对应的消息对象。

---

## 💡 三、关键知识点

### 3.1 完整写法 vs 简写形式

| 对比项 | 完整写法 | 简写写法 |
|-------|---------|---------|
| **导入** | 需要导入消息类 | 不需要 |
| **代码量** | 较多 | 较少 |
| **可读性** | 明确 | 简洁 |
| **灵活性** | 高（可设置更多属性） | 低（只能设置 content） |
| **适用场景** | 需要高级属性时 | 简单对话、提示词模板 |

**代码对比**：

```python
# 完整写法
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="你是一个助手"),
    HumanMessage(content="你好"),
    AIMessage(content="你好！")
]

# 简写写法
messages = [
    ("system", "你是一个助手"),
    ("human", "你好"),
    ("ai", "你好！")
]
```

### 3.2 简写形式的原理

LangChain 内部有一个 `_convert_to_message` 的转换逻辑，会自动把元组转换成对应的消息对象：

```python
# 伪代码：LangChain 内部的转换逻辑
def convert_to_message(msg):
    if isinstance(msg, tuple):
        role, content = msg
        if role == "system":
            return SystemMessage(content=content)
        elif role == "human":
            return HumanMessage(content=content)
        elif role == "ai":
            return AIMessage(content=content)
    return msg  # 已经是消息对象就直接返回
```

所以你传元组进去，模型会自动帮你转换成消息对象。

### 3.3 什么时候用简写？

| 场景 | 推荐写法 | 原因 |
|-----|---------|------|
| 简单对话 | 简写 | 代码简洁 |
| 提示词模板 | 简写 | 模板里用简写更清晰 |
| Few-Shot 示例 | 简写 | 示例多的时候写起来快 |
| 需要设置 name 等属性 | 完整写法 | 简写不支持额外属性 |
| 需要消息 id 等元数据 | 完整写法 | 简写只有 content |

> 💡 大多数情况下用简写就够了，代码更简洁。只有需要设置消息的高级属性时才用完整写法。

---

## 🎯 四、常见使用模式

### 4.1 简单对话

```python
messages = [
    ("system", "你是一个 helpful 的助手"),
    ("human", "你好，介绍一下你自己")
]
```

### 4.2 Few-Shot 示例

```python
messages = [
    ("system", "你是一个翻译官，把中文翻译成英文"),
    ("human", "你好"),
    ("ai", "Hello"),
    ("human", "谢谢"),
    ("ai", "Thank you"),
    ("human", "再见"),
    ("ai", "Goodbye"),
    ("human", "早上好")  # 等待模型回答
]
```

### 4.3 多轮对话历史

```python
messages = [
    ("system", "你是一个数学老师"),
    ("human", "1+1等于几？"),
    ("ai", "等于2"),
    ("human", "那2+2呢？"),
    ("ai", "等于4"),
    ("human", "再乘以3呢？")
]
```

---

## ⚠️ 五、注意事项

1. **元组格式要正确**：必须是 `(角色, 内容)` 的二元组，角色只能是 "system"、"human"、"ai"
2. **只能设置 content**：简写形式只能设置消息内容，不能设置 name、id 等其他属性
3. **角色拼写要对**：注意是 "human" 不是 "user"，是 "ai" 不是 "assistant"
4. **顺序要正确**：human 和 ai 要交替出现，通常以 human 结尾
5. **不是所有地方都支持**：大多数 LangChain 组件都支持简写，但某些特殊场景可能需要完整写法

---

## 📝 六、角色名对照表

| 元组角色 | 消息类 | OpenAI API 角色 | 说明 |
|---------|--------|----------------|------|
| `"system"` | `SystemMessage` | `system` | 系统设定 |
| `"human"` | `HumanMessage` | `user` | 用户消息 |
| `"ai"` | `AIMessage` | `assistant` | AI 回复 |

> 💡 注意：元组里用 "human" 和 "ai"，而 OpenAI API 里用 "user" 和 "assistant"。LangChain 做了一层转换。

---

## 🔍 七、进阶：消息的其他形式

除了元组简写，LangChain 还支持其他消息表示方式：

### 7.1 字典形式

```python
messages = [
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"}
]
```

> 这种格式和 OpenAI API 的格式一致。

### 7.2 字符串形式

对于 LLM（非 Chat Model），直接传字符串就行：

```python
result = llm.invoke("你好")
```

### 7.3 混合使用

也可以混合使用不同形式：

```python
messages = [
    SystemMessage(content="你是一个助手"),  # 完整写法
    ("human", "你好"),                       # 元组简写
    {"role": "assistant", "content": "你好"} # 字典形式
]
```

> 💡 LangChain 会自动把各种形式转换成统一的消息对象，非常灵活。

---

## 💡 八、完整示例模板

```python
from langchain_community.chat_models.tongyi import ChatTongyi

# 1. 初始化模型
model = ChatTongyi(model="qwen-plus")

# 2. 用简写形式构建 Few-Shot 示例
messages = [
    ("system", "你是一个反义词专家，我给你一个词，你告诉我它的反义词"),
    ("human", "大"),
    ("ai", "小"),
    ("human", "高"),
    ("ai", "矮"),
    ("human", "胖"),
    ("ai", "瘦"),
    ("human", "快乐")  # 等待模型回答
]

# 3. 流式调用
print("AI: ", end="", flush=True)
for chunk in model.stream(messages):
    print(chunk.content, end="", flush=True)
print()
```

---

## 📊 九、三种消息形式对比

| 形式 | 示例 | 优点 | 缺点 |
|-----|------|------|------|
| **消息对象** | `HumanMessage(content="...")` | 功能最全、最明确 | 代码长、需要导入 |
| **元组简写** | `("human", "...")` | 简洁、无需导入 | 只能设置 content |
| **字典形式** | `{"role": "user", "content": "..."}` | 和 API 格式一致 | 写法稍长 |

> 💡 推荐：日常开发用元组简写，最简洁；需要高级属性时用消息对象；和 OpenAI 格式对齐时用字典。

---

> 💡 **学习建议**：消息简写是 LangChain 中非常实用的语法糖，能让代码简洁很多。建议从一开始就习惯用简写形式，特别是在写提示词模板的时候，会清晰很多。
