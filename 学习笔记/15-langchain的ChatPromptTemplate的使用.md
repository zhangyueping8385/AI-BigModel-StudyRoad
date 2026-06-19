# 15 - LangChain 的 ChatPromptTemplate 的使用

> 学习使用 ChatPromptTemplate 创建对话式提示词模板，支持多角色消息和历史消息占位

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 的 ChatPromptTemplate** 创建对话式提示词模板，支持 system、human、ai 等多角色消息，还支持历史消息占位符，是构建对话应用的重要工具。

### 1.1 核心功能

- ✅ 使用 ChatPromptTemplate 创建对话模板
- ✅ 支持 system、human、ai 等多角色
- ✅ 使用 MessagesPlaceholder 占位历史消息
- ✅ 模板 + 模型组成链

---

## 🔧 二、核心代码解析

### 2.1 导入相关类

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
```

| 导入类 | 说明 |
|-------|------|
| `ChatPromptTemplate` | 对话提示词模板 |
| `MessagesPlaceholder` | 消息占位符（用于历史消息） |
| `ChatTongyi` | 通义千问聊天模型 |

### 2.2 创建对话模板

```python
chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一位资深的美容顾问，可以根据用户的肤质推荐护肤品。"),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])
```

**模板结构**：

```
┌─────────────────────────────────┐
│  system 消息                     │  ← 角色设定
│  "你是一位资深的美容顾问..."     │
├─────────────────────────────────┤
│  MessagesPlaceholder("history")  │  ← 历史消息占位符
│  （运行时替换为实际的对话历史）   │
├─────────────────────────────────┤
│  human 消息                      │  ← 当前问题
│  "{question}"                    │
└─────────────────────────────────┘
```

**模板中的消息类型**：

| 类型 | 写法 | 说明 |
|-----|------|------|
| system | `("system", "内容")` | 系统设定 |
| human | `("human", "内容")` | 用户消息 |
| ai | `("ai", "内容")` | AI 回复 |
| 占位符 | `MessagesPlaceholder("变量名")` | 历史消息占位 |

### 2.3 准备历史数据

```python
history_data = [
    ("human", "你好，我是干性皮肤"),
    ("ai", "你好，干性皮肤需要注意保湿，建议使用滋润型的护肤品。")
]
```

历史消息用元组列表的形式，和之前学的消息简写形式一样。

### 2.4 调用模板

```python
prompt_text = chat_prompt_template.invoke({
    "history": history_data,
    "question": "我应该用什么类型的洗面奶？"
}).to_string()

print(prompt_text)
```

**执行流程**：

1. 把 `history` 变量替换为 `history_data` 中的消息列表
2. 把 `question` 变量替换为实际问题
3. 生成完整的消息列表
4. 用 `.to_string()` 转成字符串方便查看

**填充后的完整提示词**：

```
System: 你是一位资深的美容顾问，可以根据用户的肤质推荐护肤品。

Human: 你好，我是干性皮肤
AI: 你好，干性皮肤需要注意保湿，建议使用滋润型的护肤品。

Human: 我应该用什么类型的洗面奶？
```

### 2.5 组合成链并调用模型

```python
model = ChatTongyi(model="qwen-plus")
chain = chat_prompt_template | model

response = model.invoke(prompt_text)
print(response.content)
```

> 💡 这里代码里用了 `model.invoke(prompt_text)`，但更标准的用法是 `chain.invoke({...})`，直接传字典给链。

**标准链式调用写法**：

```python
chain = chat_prompt_template | model

result = chain.invoke({
    "history": history_data,
    "question": "我应该用什么类型的洗面奶？"
})
print(result.content)
```

---

## 💡 三、关键知识点

### 3.1 ChatPromptTemplate vs PromptTemplate

| 对比项 | PromptTemplate | ChatPromptTemplate |
|-------|---------------|-------------------|
| **输出** | 字符串 | 消息列表（List[BaseMessage]） |
| **角色支持** | 不直接支持 | 原生支持 system/human/ai |
| **历史消息** | 需要手动拼接 | 支持 MessagesPlaceholder |
| **适用模型** | LLM | Chat Model |
| **使用场景** | 简单文本生成 | 对话、多轮交互 |

> 💡 简单说：PromptTemplate 输出"一段文字"，ChatPromptTemplate 输出"一组消息"。

### 3.2 MessagesPlaceholder 的作用

`MessagesPlaceholder` 是一个特殊的占位符，用于在模板中预留一个位置，运行时填充一组消息。

**为什么需要它？**

因为历史消息的数量是不固定的——可能有 2 条，也可能有 20 条。用普通的变量占位符没法处理这种动态数量的消息。

**使用方式**：

```python
# 模板中定义占位符
ChatPromptTemplate.from_messages([
    ("system", "..."),
    MessagesPlaceholder("chat_history"),  # 这里会填充一组消息
    ("human", "{question}")
])

# 调用时传入消息列表
chain.invoke({
    "chat_history": [
        ("human", "你好"),
        ("ai", "你好！"),
        ("human", "你叫什么？"),
        ("ai", "我叫小明。"),
    ],
    "question": "你多大了？"
})
```

### 3.3 from_messages 方法

`ChatPromptTemplate.from_messages()` 是最常用的创建方式，接受一个消息列表：

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),      # 元组形式
    MessagesPlaceholder("history"),  # 占位符
    ("human", "{question}")          # 带变量的元组
])
```

**支持的消息格式**：

| 格式 | 示例 | 说明 |
|-----|------|------|
| 元组 | `("system", "...")` | 最常用，简洁 |
| 消息对象 | `SystemMessage(content="...")` | 完整写法 |
| 占位符 | `MessagesPlaceholder("name")` | 历史消息占位 |
| 字符串模板 | `("human", "{text}")` | 带变量的消息 |

---

## 🎯 四、常见使用模式

### 4.1 简单对话模板

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个 helpful 的助手"),
    ("human", "{question}")
])
```

### 4.2 带历史的对话模板

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个编程专家"),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])
```

### 4.3 Few-Shot 对话模板

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个翻译官"),
    ("human", "你好"),
    ("ai", "Hello"),
    ("human", "谢谢"),
    ("ai", "Thank you"),
    ("human", "{text}")
])
```

### 4.4 带变量的 system 消息

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，回答要{style}"),
    ("human", "{question}")
])
```

---

## ⚠️ 五、注意事项

1. **消息列表格式要对**：from_messages 接受的是列表，每个元素是消息或占位符
2. **占位符变量名要对应**：MessagesPlaceholder("name") 中的 name 和调用时的 key 要一致
3. **历史消息是列表**：传给占位符的必须是消息列表（或元组列表），不能是字符串
4. **变量名不能冲突**：普通变量和占位符变量不要重名
5. **输出是消息列表**：ChatPromptTemplate 的输出是消息列表，不是字符串，可以用 `.to_string()` 转成字符串查看

---

## 📝 六、进阶用法

### 6.1 查看模板的输入变量

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])

print(prompt.input_variables)
# 输出：['role', 'history', 'question']
```

### 6.2 部分填充变量

```python
# 预填充 role，只留 question 作为输入
partial_prompt = prompt.partial(role="编程专家")

chain = partial_prompt | model
result = chain.invoke({"question": "什么是Python"})
```

### 6.3 流式输出

链也支持流式输出：

```python
chain = chat_prompt_template | model

for chunk in chain.stream({
    "history": history_data,
    "question": "我应该用什么类型的洗面奶？"
}):
    print(chunk.content, end="", flush=True)
```

---

## 🔍 七、完整对话示例

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi

# 1. 创建模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个 helpful 的助手，回答简洁明了"),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])

# 2. 初始化模型
model = ChatTongyi(model="qwen-plus")

# 3. 组合成链
chain = prompt | model

# 4. 多轮对话
history = []

# 第一轮
result = chain.invoke({
    "history": history,
    "question": "你好，我叫张三"
})
print(f"AI: {result.content}")

# 把第一轮加入历史
history.append(("human", "你好，我叫张三"))
history.append(("ai", result.content))

# 第二轮
result = chain.invoke({
    "history": history,
    "question": "我叫什么名字？"
})
print(f"AI: {result.content}")
# 模型会回答"张三"，因为历史里有
```

---

## 💡 八、快速上手模板

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi

# 1. 创建对话模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，回答要{style}"),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])

# 2. 初始化模型
model = ChatTongyi(model="qwen-plus")

# 3. 组合成链
chain = prompt | model

# 4. 调用
result = chain.invoke({
    "role": "编程老师",
    "style": "幽默风趣",
    "history": [],
    "question": "什么是递归"
})
print(result.content)

# 5. 流式调用
print("\n--- 流式输出 ---")
for chunk in chain.stream({
    "role": "编程老师",
    "style": "幽默风趣",
    "history": [],
    "question": "什么是递归"
}):
    print(chunk.content, end="", flush=True)
```

---

## 📊 九、提示词模板家族

| 模板类型 | 输出 | 适用场景 |
|---------|------|---------|
| `PromptTemplate` | 字符串 | 简单文本生成 |
| `FewShotPromptTemplate` | 字符串 | 带示例的文本生成 |
| `ChatPromptTemplate` | 消息列表 | 对话、多角色 |
| `FewShotChatMessagePromptTemplate` | 消息列表 | 带示例的对话 |

> 💡 建议：和 Chat Model 配合使用时，优先用 ChatPromptTemplate。

---

> 💡 **学习建议**：ChatPromptTemplate 是构建对话应用的核心组件，一定要掌握。特别是 MessagesPlaceholder 的用法，它是实现多轮对话记忆的关键。试着用它写一个简单的聊天机器人，体会历史消息是怎么传递的。
