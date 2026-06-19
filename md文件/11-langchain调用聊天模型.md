# 11 - LangChain 调用聊天模型

> 学习使用 LangChain 的 Chat Model 进行对话，了解消息对象的使用

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 的聊天模型（Chat Model）**进行对话的方法，使用消息对象（SystemMessage、HumanMessage、AIMessage）来构建多角色对话。

### 1.1 核心功能

- ✅ 使用 ChatTongyi 聊天模型
- ✅ 使用消息对象构建对话
- ✅ 支持 System、Human、AI 三种角色
- ✅ 流式输出

---

## 🔧 二、核心代码解析

### 2.1 导入相关类

```python
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
```

**导入的类说明**：

| 类 | 说明 | 对应角色 |
|----|------|---------|
| `ChatTongyi` | 通义千问聊天模型类 | - |
| `SystemMessage` | 系统消息 | system |
| `HumanMessage` | 人类消息 | user |
| `AIMessage` | AI 消息 | assistant |

### 2.2 初始化模型

```python
model = ChatTongyi(
    model = "qwen-plus"
)
```

和 LLM 的初始化类似，但用的是 `ChatTongyi` 而不是 `Tongyi`。

### 2.3 构建消息列表

```python
messages = [
    SystemMessage(content="你是一名Python编程专家，回答言简意赅"),
    HumanMessage(content="输出1-10的数字，使用python代码")
]
```

**消息列表的结构**：

```
[
  SystemMessage: 设定AI的角色和行为
  HumanMessage:  用户的输入/问题
  AIMessage:     AI的回复（如果有历史）
  HumanMessage:  下一个用户问题
  ...
]
```

### 2.4 流式调用

```python
response = model.stream(input=messages)
for i in response:
    print(i.content, end="", flush=True)
```

**Chat Model 的 stream 返回的是消息对象**，需要用 `.content` 获取文本内容。

---

## 💡 三、关键知识点

### 3.1 LLM vs Chat Model

| 对比项 | LLM（Tongyi） | Chat Model（ChatTongyi） |
|-------|---------------|-------------------------|
| **输入** | 字符串 | 消息列表 |
| **输出** | 字符串 | 消息对象（AIMessage） |
| **角色支持** | 不直接支持 | 支持 system/user/assistant |
| **对话能力** | 需要手动拼接 | 原生支持多轮对话 |
| **适用场景** | 文本补全、生成 | 对话、聊天、多轮交互 |

**输入输出对比**：

```python
# LLM：字符串进，字符串出
result = llm.invoke("你好")
# result 是字符串："你好！有什么可以帮你的？"

# Chat Model：消息列表进，消息对象出
result = chat_model.invoke([HumanMessage(content="你好")])
# result 是 AIMessage 对象
# result.content 是字符串："你好！有什么可以帮你的？"
```

### 3.2 消息类型详解

| 消息类型 | 类名 | 作用 | 示例 |
|---------|------|------|------|
| **系统消息** | `SystemMessage` | 设定 AI 的角色、行为、规则 | "你是一个编程专家" |
| **人类消息** | `HumanMessage` | 用户的输入、问题 | "帮我写个排序函数" |
| **AI 消息** | `AIMessage` | AI 的回复 | "好的，这是排序函数..." |
| **函数消息** | `FunctionMessage` | 函数调用的返回结果 | - |
| **工具消息** | `ToolMessage` | 工具调用的返回结果 | - |

### 3.3 消息对象的属性

```python
msg = HumanMessage(content="你好")

print(msg.content)   # 消息内容："你好"
print(msg.type)      # 消息类型："human"
print(msg.role)      # 角色："user"（有些模型用 role）
```

> 💡 不同类型的消息对象，type 属性不同：
> - SystemMessage → "system"
> - HumanMessage → "human"
> - AIMessage → "ai"

---

## 🎯 四、多轮对话实现

### 4.1 手动维护消息列表

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 初始化消息列表
messages = [
    SystemMessage(content="你是一个 helpful 的助手")
]

# 第一轮
messages.append(HumanMessage(content="我有2只猫"))
response = model.invoke(messages)
messages.append(response)  # 把 AI 回复加入列表

# 第二轮
messages.append(HumanMessage(content="我有5只狗"))
response = model.invoke(messages)
messages.append(response)

# 第三轮
messages.append(HumanMessage(content="我一共有几只宠物？"))
response = model.invoke(messages)
print(response.content)
```

### 4.2 流式多轮对话

```python
messages = [
    SystemMessage(content="你是一个 helpful 的助手")
]

while True:
    user_input = input("你: ")
    if user_input == "退出":
        break
    
    messages.append(HumanMessage(content=user_input))
    
    print("AI: ", end="", flush=True)
    full_response = ""
    for chunk in model.stream(messages):
        full_response += chunk.content
        print(chunk.content, end="", flush=True)
    print()
    
    messages.append(AIMessage(content=full_response))
```

---

## ⚠️ 五、注意事项

1. **输入是消息列表**：Chat Model 的输入必须是消息对象的列表，不能直接传字符串
2. **输出是消息对象**：invoke 返回的是 AIMessage，需要 `.content` 获取文本
3. **流式输出也是消息对象**：stream 返回的每一块也是消息对象，需要 `.content`
4. **消息顺序要正确**：Human 和 AI 消息要交替出现，通常以 Human 结尾
5. **System 消息放最前面**：系统消息一般放在消息列表的最开头

---

## 📝 六、消息简写形式

LangChain 还支持用元组的简写形式来表示消息，更简洁：

```python
# 完整写法
messages = [
    SystemMessage(content="你是一个助手"),
    HumanMessage(content="你好"),
    AIMessage(content="你好！")
]

# 简写写法（元组形式）
messages = [
    ("system", "你是一个助手"),
    ("human", "你好"),
    ("ai", "你好！")
]
```

**简写对应关系**：

| 元组形式 | 对应类 |
|---------|--------|
| `("system", "...")` | `SystemMessage` |
| `("human", "...")` | `HumanMessage` |
| `("ai", "...")` | `AIMessage` |

> 💡 简写形式在提示词模板中用得很多，下一节会详细学习。

---

## 🔍 七、Chat Model 的其他方法

### 7.1 invoke（普通调用）

```python
result = model.invoke([HumanMessage(content="你好")])
print(result.content)
```

### 7.2 stream（流式调用）

```python
for chunk in model.stream([HumanMessage(content="你好")]):
    print(chunk.content, end="")
```

### 7.3 batch（批量调用）

```python
results = model.batch([
    [HumanMessage(content="你好")],
    [HumanMessage(content="介绍一下Python")]
])
for r in results:
    print(r.content)
```

### 7.4 异步方法

```python
# 异步调用
result = await model.ainvoke([HumanMessage(content="你好")])

# 异步流式
async for chunk in model.astream([HumanMessage(content="你好")]):
    print(chunk.content, end="")
```

---

## 💡 八、快速上手模板

```python
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 1. 初始化模型
model = ChatTongyi(model="qwen-plus")

# 2. 构建消息
messages = [
    SystemMessage(content="你是一个Python编程专家，回答简洁明了"),
    HumanMessage(content="用Python写一个快速排序")
]

# 3. 普通调用
response = model.invoke(messages)
print("普通调用结果：")
print(response.content)

# 4. 流式调用
print("\n流式输出：")
for chunk in model.stream(messages):
    print(chunk.content, end="", flush=True)
```

---

## 📊 九、LLM 和 Chat Model 怎么选？

| 场景 | 推荐使用 | 原因 |
|-----|---------|------|
| 简单文本生成 | LLM 或 Chat Model | 都可以，Chat Model 效果通常更好 |
| 对话/聊天 | Chat Model | 原生支持多角色消息 |
| 提示词模板 | Chat Model | 配合 ChatPromptTemplate 更好用 |
| 老项目兼容 | LLM | 历史代码可能用 LLM |
| 新开发项目 | Chat Model | 现在主流都用 Chat Model |

> 💡 建议：新项目直接用 Chat Model，效果更好，功能更全。LLM 更多是为了兼容旧代码。

---

> 💡 **学习建议**：Chat Model 是 LangChain 的主流用法。建议从一开始就用 Chat Model 而不是 LLM，这样后续学习提示词模板、链、记忆等组件时会更顺畅。
