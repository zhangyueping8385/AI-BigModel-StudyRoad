# 16 - LangChain 的 Chain 基础使用

> 学习使用 LCEL（LangChain Expression Language）构建链，掌握管道符组合组件的方法

---

## 📚 一、代码概述

本代码演示了**LangChain 中 Chain（链）的基础使用**，通过 `|` 管道符将提示词模板和模型组合成一条链，实现端到端的调用。

### 1.1 核心功能

- ✅ 使用 LCEL 管道语法构建链
- ✅ 提示词模板 + 模型组合
- ✅ 链的流式输出
- ✅ 历史消息传递

---

## 🔧 二、核心代码解析

### 2.1 导入相关类

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
```

### 2.2 创建对话模板

```python
chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一位资深的美容顾问，可以根据用户的肤质推荐护肤品。"),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])
```

和上一节一样，创建一个带历史消息占位符的对话模板。

### 2.3 初始化模型

```python
model = ChatTongyi(model="qwen-plus")
```

### 2.4 组合成链（核心）

```python
chain = chat_prompt_template | model
```

**这就是 LCEL 的核心**——用 `|` 管道符把多个组件连接起来。

**链的执行流程**：

```
输入（字典）
    ↓
chat_prompt_template（填充模板，生成消息列表）
    ↓
model（调用模型，生成回复）
    ↓
输出（AIMessage 对象）
```

> 💡 就像流水线一样，前一个组件的输出是后一个组件的输入。

### 2.5 准备历史数据

```python
history_data = [
    ("human", "你好，我是干性皮肤"),
    ("ai", "你好，干性皮肤需要注意保湿，建议使用滋润型的护肤品。")
]
```

### 2.6 流式调用链

```python
response = chain.stream({
    "history": history_data,
    "question": "我应该用什么类型的洗面奶？"
})

for i in response:
    print(i.content, end="", flush=True)
```

**调用方式**：
- 输入是一个字典，包含模板需要的所有变量
- 输出是流式的，逐块返回

---

## 💡 三、关键知识点

### 3.1 什么是 LCEL？

**LCEL（LangChain Expression Language）** 是 LangChain 的表达式语言，核心就是用 `|` 管道符组合各种 Runnable 组件。

**为什么叫"链"（Chain）？**

因为多个组件串在一起，就像一条链条：

```
组件A → 组件B → 组件C → ...
```

每个环节处理完传给下一个环节。

### 3.2 链的特点

| 特点 | 说明 |
|-----|------|
| **统一接口** | 所有组件都是 Runnable，都有 invoke/stream/batch 方法 |
| **灵活组合** | 可以像搭积木一样自由组合 |
| **流式支持** | 整条链都支持流式输出 |
| **异步支持** | 整条链都支持异步调用 |
| **易于调试** | 可以单独测试每个环节 |

### 3.3 链的输入输出

**输入**：
- 字典形式，包含所有需要的变量
- key 是变量名，value 是变量值

**输出**：
- 取决于最后一个组件是什么
- 如果最后是模型，输出就是消息对象或字符串

**示例**：

```python
# 链的组成
chain = prompt | model

# 输入：字典
input_data = {"name": "张三", "question": "你好"}

# 输出：AIMessage 对象（因为最后是 Chat Model）
output = chain.invoke(input_data)
print(output.content)  # 获取文本内容
```

---

## 🎯 四、常见链的组合方式

### 4.1 最简单的链：提示词 + 模型

```python
chain = prompt | model
```

最常用的组合，用于基本的对话和生成任务。

### 4.2 带输出解析的链

```python
chain = prompt | model | output_parser
```

在模型后面加一个解析器，把输出转换成想要的格式（如 JSON、列表等）。

### 4.3 多步链

```python
chain = step1 | step2 | step3 | model
```

多个处理步骤串联，每一步处理后传给下一步。

### 4.4 分支链

```python
# 更复杂的结构，有分支和合并
# （需要用 RunnableParallel 等高级组件）
```

---

## ⚠️ 五、注意事项

1. **输入必须是字典**：链的输入必须是字典，不能直接传字符串（除非第一个组件接受字符串）
2. **变量名要对应**：字典的 key 要和模板中的变量名完全一致
3. **组件类型要匹配**：前一个组件的输出类型要和后一个组件的输入类型匹配
4. **流式输出的类型**：链的流式输出类型取决于最后一个组件
5. **错误处理**：链中任何一个环节出错，整个链都会报错

---

## 📝 六、进阶：更多 Runnable 组件

### 6.1 RunnableLambda（自定义函数）

可以把普通函数包装成 Runnable，加入链中：

```python
from langchain_core.runnables import RunnableLambda

def process_input(input_dict):
    """自定义处理函数"""
    input_dict["question"] = input_dict["question"].upper()
    return input_dict

chain = RunnableLambda(process_input) | prompt | model
```

### 6.2 RunnableParallel（并行执行）

多个分支并行执行，然后合并结果：

```python
from langchain_core.runnables import RunnableParallel

chain = RunnableParallel({
    "summary": summary_prompt | model,
    "translation": translate_prompt | model
})
```

### 6.3 RunnablePassthrough（透传）

把输入原样传递下去，常用于并行分支中：

```python
from langchain_core.runnables import RunnablePassthrough

chain = RunnablePassthrough() | prompt | model
# 等价于 prompt | model
```

---

## 🔍 七、链的方法

所有链都支持以下方法：

| 方法 | 作用 | 输入 | 输出 |
|-----|------|------|------|
| `invoke()` | 同步调用 | 1个输入 | 1个输出 |
| `stream()` | 流式输出 | 1个输入 | 多块输出 |
| `batch()` | 批量调用 | 多个输入 | 多个输出 |
| `ainvoke()` | 异步调用 | 1个输入 | 1个输出 |
| `astream()` | 异步流式 | 1个输入 | 多块输出 |
| `abatch()` | 异步批量 | 多个输入 | 多个输出 |

> 💡 因为链本身也是 Runnable，所以它和其他组件有完全相同的接口。

---

## 💡 八、完整示例模板

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi

# 1. 创建提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，回答要{style}"),
    MessagesPlaceholder("history"),
    ("human", "{question}")
])

# 2. 初始化模型
model = ChatTongyi(model="qwen-plus")

# 3. 组合成链
chain = prompt | model

# 4. 普通调用
result = chain.invoke({
    "role": "编程老师",
    "style": "幽默风趣",
    "history": [],
    "question": "什么是递归"
})
print("普通调用结果：")
print(result.content)

# 5. 流式调用
print("\n流式输出：")
for chunk in chain.stream({
    "role": "编程老师",
    "style": "幽默风趣",
    "history": [],
    "question": "什么是递归"
}):
    print(chunk.content, end="", flush=True)

# 6. 批量调用
print("\n\n批量调用：")
results = chain.batch([
    {"role": "老师", "style": "简洁", "history": [], "question": "什么是Python"},
    {"role": "老师", "style": "简洁", "history": [], "question": "什么是Java"},
])
for i, r in enumerate(results):
    print(f"结果{i+1}: {r.content[:50]}...")
```

---

## 📊 九、LangChain 核心概念总结

| 概念 | 作用 | 类比 |
|-----|------|------|
| **Model（模型）** | 核心 AI 能力 | 发动机 |
| **Prompt Template（提示词模板）** | 格式化输入 | 模具 |
| **Chain（链）** | 组合组件 | 流水线 |
| **Runnable（可运行）** | 统一接口 | 标准零件 |
| **Memory（记忆）** | 保存对话历史 | 笔记本 |
| **Agent（代理）** | 自主决策和行动 | 员工 |
| **Tool（工具）** | 外部能力扩展 | 工具箱 |

> 💡 学习路线：模型 → 提示词模板 → 链 → 记忆 → 代理/工具。先把基础的链掌握好，再学更复杂的。

---

## 🔗 十、链的调试技巧

### 10.1 单独测试每个环节

```python
# 测试提示词模板
formatted = prompt.invoke({"question": "你好"})
print(formatted.to_string())

# 测试模型
result = model.invoke([("human", "你好")])
print(result.content)
```

### 10.2 查看中间结果

可以在链中间插入一个打印函数来调试：

```python
from langchain_core.runnables import RunnableLambda

def debug_print(x):
    print(f"调试信息: {x}")
    return x

chain = prompt | RunnableLambda(debug_print) | model
```

### 10.3 使用 LangSmith

LangSmith 是 LangChain 的官方调试平台，可以可视化地查看链的每一步执行情况。

---

> 💡 **学习建议**：链（Chain）是 LangChain 的核心概念之一，也是最常用的。一定要把 LCEL 管道语法练熟，这是后续学习更复杂应用的基础。试着把之前写的各种提示词模板都用链的方式组合起来，体会"搭积木"的感觉。
