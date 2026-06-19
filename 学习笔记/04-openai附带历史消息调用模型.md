# 04 - OpenAI 附带历史消息调用模型

> 学习如何通过传递历史消息实现多轮对话，让模型记住上下文

---

## 📚 一、代码概述

本代码演示了**多轮对话的实现方式**——通过在 messages 数组中携带历史对话，让模型能够记住之前说过的话，实现有记忆的对话。

### 1.1 核心功能

- ✅ 携带多轮历史消息调用模型
- ✅ 模型基于上下文回答问题
- ✅ 流式输出展示回复

---

## 🔧 二、核心代码解析

### 2.1 构建带历史的消息列表

```python
response = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {'role':'system','content':'你是一个百事通，回答言简意赅'},
        {'role': 'user', 'content': '我有2只猫'},
        {'role':'assistant','content':'好的'},
        {'role': 'user', 'content': '我有5只狗'},
        {'role': 'assistant', 'content': '好的'},
        {'role': 'user', 'content': '我有几只宠物'}
    ],
    stream=True
)
```

**对话历史结构：**

```
┌─────────────────────────────────────┐
│  system: 你是一个百事通，回答言简意赅   │  ← 系统设定
├─────────────────────────────────────┤
│  user: 我有2只猫                     │  ← 第1轮用户输入
├─────────────────────────────────────┤
│  assistant: 好的                     │  ← 第1轮AI回复
├─────────────────────────────────────┤
│  user: 我有5只狗                     │  ← 第2轮用户输入
├─────────────────────────────────────┤
│  assistant: 好的                     │  ← 第2轮AI回复
├─────────────────────────────────────┤
│  user: 我有几只宠物                   │  ← 第3轮用户输入（当前问题）
└─────────────────────────────────────┘
```

模型看到完整的对话历史后，就能算出：2只猫 + 5只狗 = 7只宠物。

### 2.2 流式输出

```python
for chunk in response:
    print(chunk.choices[0].delta.content,
          end=" ",
          flush=True
    )
```

和上一节的流式输出用法一致。

---

## 💡 三、关键知识点

### 3.1 大模型是"无状态"的

这是最重要的概念！

```
❌ 错误理解：模型有记忆，能记住你说过的话
✅ 正确理解：模型每次调用都是独立的，所谓"记忆"是我们把历史消息塞进去的
```

**每次调用都要带上完整历史**：

```
第1次调用：[system, user:我有2只猫] → AI:好的
第2次调用：[system, user:我有2只猫, AI:好的, user:我有5只狗] → AI:好的
第3次调用：[system, user:我有2只猫, AI:好的, user:我有5只狗, AI:好的, user:我有几只宠物] → AI:7只
```

> 💡 这就像每次考试都把课本带进去——模型本身不记得，是你把"课本"（历史消息）递给它看。

### 3.2 为什么需要 assistant 消息？

对话必须是 **user 和 assistant 交替出现** 的：

```
✅ 正确：user → assistant → user → assistant
❌ 错误：user → user → user （连续两个user）
```

**原因**：模型是按照"对话模式"训练的，它期望看到一问一答的结构。如果格式不对，模型可能会困惑或输出异常。

### 3.3 历史消息的作用

| 作用 | 说明 |
|-----|------|
| **上下文理解** | 模型知道之前聊了什么，能理解指代（如"它"、"那个"） |
| **保持人设一致** | 模型的回答风格、语气保持连贯 |
| **信息累积** | 之前提到的信息（如"我有2只猫"）可以被后续问题引用 |
| **引导回答** | 通过历史对话引导模型按特定方式回答 |

---

## 🎯 四、多轮对话的实现方式

### 4.1 用列表维护历史

```python
# 初始化对话历史
messages = [
    {"role": "system", "content": "你是一个 helpful 的助手"}
]

# 用户提问
user_input = "我有2只猫"
messages.append({"role": "user", "content": user_input})

# 调用模型
response = client.chat.completions.create(
    model="qwen-plus",
    messages=messages
)
reply = response.choices[0].message.content

# 把AI回复也加入历史
messages.append({"role": "assistant", "content": reply})

# 下一轮对话...
user_input2 = "我有5只狗"
messages.append({"role": "user", "content": user_input2})
# ...继续调用
```

### 4.2 完整的对话循环

```python
messages = [
    {"role": "system", "content": "你是一个 helpful 的助手"}
]

while True:
    user_input = input("你: ")
    if user_input == "退出":
        break
    
    # 添加用户消息
    messages.append({"role": "user", "content": user_input})
    
    # 调用模型
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=messages
    )
    reply = response.choices[0].message.content
    
    print(f"AI: {reply}")
    
    # 添加AI回复
    messages.append({"role": "assistant", "content": reply})
```

---

## ⚠️ 五、注意事项

### 5.1 Token 消耗问题

对话越长，消耗的 token 越多：

```
第1轮：100 tokens
第2轮：200 tokens
第3轮：300 tokens
...
第100轮：10000+ tokens
```

**解决方案：**
- 滑动窗口：只保留最近 N 条消息
- 摘要记忆：用模型对历史对话做摘要
- 定期清空：不重要的对话可以重置

### 5.2 上下文窗口限制

每个模型都有最大上下文长度（如 4K、8K、32K、128K tokens），超出会报错。

> 💡 就像一张纸有字数限制，写满了就写不下了。

### 5.3 消息格式要正确

- user 和 assistant 必须交替出现
- 通常以 user 消息结尾（当前问题）
- system 消息一般放在最前面
- 不要有连续的相同角色

---

## 📝 六、实际应用场景

### 6.1 客服机器人

用户可以追问之前的问题，机器人记得上下文。

### 6.2 代码助手

用户："帮我写个排序函数"
AI：[给出代码]
用户："改成降序"
AI：[修改代码] ← 知道"改成"指的是刚才的代码

### 6.3 角色扮演

设定角色后，整个对话过程中保持人设一致。

---

## 🔍 七、进阶：记忆优化策略

| 策略 | 原理 | 适用场景 |
|-----|------|---------|
| **滑动窗口** | 只保留最近 N 条消息 | 简单对话 |
| **摘要记忆** | 定期用模型总结历史对话 | 长对话 |
| **向量检索** | 从历史中检索相关片段 | 知识库问答 |
| **混合记忆** | 短期+长期结合 | 复杂应用 |

这些高级策略在 LangChain 等框架中有现成实现。

---

> 💡 **学习建议**：动手写一个简单的命令行聊天机器人，体会多轮对话的实现。然后试试聊很长时间，看看 token 消耗和模型表现，理解上下文窗口的概念。
