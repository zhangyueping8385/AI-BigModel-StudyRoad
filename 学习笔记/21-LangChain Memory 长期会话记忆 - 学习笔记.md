# LangChain Memory 长期会话记忆 - 学习笔记

> 基于 `FileChatMessageHistory` 实现的持久化会话记忆方案

---

## 📚 一、概述

### 1.1 什么是会话记忆？

在大语言模型（LLM）应用中，**会话记忆（Memory）** 是指系统能够记住之前的对话内容，并基于历史上下文进行回复的能力。

| 记忆类型 | 特点 | 适用场景 |
|---------|------|---------|
| **短期记忆** | 仅存在于内存中，程序重启即丢失 | 单次对话、临时会话 |
| **长期记忆** | 持久化存储（文件/数据库），重启后可恢复 | 用户会话保存、多轮对话续接 |

### 1.2 本代码实现了什么？

本代码通过自定义 `FileChatMessageHistory` 类，实现了**基于文件的长期会话记忆**：

- ✅ 会话历史以 JSON 格式存储在本地文件
- ✅ 不同 `session_id` 对应不同物理文件，实现多会话隔离
- ✅ 程序重启后可恢复历史对话
- ✅ 完全兼容 LangChain 的 `RunnableWithMessageHistory` 接口

---

## 🏗️ 二、整体架构

### 2.1 核心组件关系图

```
┌─────────────────────────────────────────────────────────┐
│                     用户调用                              │
│         conversation_chain.invoke(...)                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│           RunnableWithMessageHistory                     │
│  （自动管理记忆的读取与写入）                              │
└─────────┬───────────────────────────┬───────────────────┘
          │                           │
          ▼                           ▼
┌──────────────────┐      ┌──────────────────────────┐
│  读取历史消息     │      │   base_chain 处理链       │
│  (get_chat_history)│     │  Prompt → Model → Output │
└────────┬─────────┘      └────────────┬─────────────┘
         │                             │
         ▼                             ▼
┌──────────────────┐      ┌──────────────────────────┐
│ FileChatMessage-  │      │   生成回复后自动追加      │
│ History (文件存储) │◄─────┤   到历史记录中           │
└──────────────────┘      └──────────────────────────┘
```

### 2.2 数据流向

```
用户输入
    ↓
[读取历史消息] ← 从 JSON 文件加载
    ↓
[拼接 Prompt] ← System + History + Human
    ↓
[LLM 生成回复]
    ↓
[写入历史消息] → 追加到 JSON 文件
    ↓
返回回复给用户
```

---

## 🔧 三、核心代码解析

### 3.1 导入依赖

```python
import json
import os
from typing import Sequence

# LangChain 核心模块
from langchain_community.chat_models import ChatTongyi
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableWithMessageHistory, RunnableConfig
```

**关键导入说明：**

| 导入项 | 作用 |
|-------|------|
| `BaseChatMessageHistory` | 会话历史基类，自定义记忆必须继承它 |
| `message_to_dict` / `messages_from_dict` | 消息对象与字典的双向序列化 |
| `RunnableWithMessageHistory` | 自动管理记忆的包装器 |
| `MessagesPlaceholder` | Prompt 模板中的历史消息占位符 |

---

### 3.2 FileChatMessageHistory 类

这是本代码的**核心**，实现了基于文件的持久化记忆。

#### 3.2.1 类定义与初始化

```python
class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, store_path: str = "./chat_history"):
        self.session_id = session_id          # 会话id作为文件名
        self.store_path = store_path          # 存储目录
        self.file_path = os.path.join(self.store_path, self.session_id)
        # 确保目录存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
```

**设计要点：**
- 继承 `BaseChatMessageHistory` 抽象基类
- `session_id` 作为文件名，实现多会话隔离
- 自动创建存储目录，避免路径不存在报错

#### 3.2.2 添加消息（写入）

```python
def add_message(self, message: BaseMessage) -> None:
    # 单条消息添加接口，内部调用批量添加接口
    self.add_messages([message])

def add_messages(self, messages: Sequence[BaseMessage]) -> None:
    # 1. 读取现有消息
    all_messages = list(self.messages)
    # 2. 追加新消息
    all_messages.extend(messages)
    # 3. 序列化并写入文件
    new_messages = [message_to_dict(msg) for msg in all_messages]
    with open(self.file_path, "w", encoding="utf-8") as f:
        json.dump(new_messages, f)
```

**写入流程：**

| 步骤 | 操作 | 说明 |
|-----|------|------|
| 1 | 读取现有消息 | 调用 `self.messages` 属性读取文件 |
| 2 | 追加新消息 | 将新消息合并到列表中 |
| 3 | 序列化 | `message_to_dict()` 将消息对象转为字典 |
| 4 | 写入文件 | 覆盖写入整个 JSON 文件 |

> ⚠️ **注意**：这里采用**覆盖写入**模式，适用于中小规模历史记录。如果历史消息非常大，频繁全量写入会有性能问题。

#### 3.2.3 读取消息（读取）

```python
@property
def messages(self) -> list[BaseMessage]:
    """从文件读取并反序列化消息"""
    try:
        with open(self.file_path, "r", encoding="utf-8") as f:
            messages = json.load(f)
            return messages_from_dict(messages)
    except FileNotFoundError:
        # 文件不存在时返回空列表
        return []
```

**关键设计：**
- 使用 `@property` 装饰器，像访问属性一样调用
- `messages_from_dict()` 将字典反序列化为消息对象
- 文件不存在时返回空列表，优雅处理首次对话

#### 3.2.4 清空会话

```python
def clear(self):
    """清空会话记录"""
    with open(self.file_path, "w", encoding="utf-8") as f:
        json.dump([], f)
```

直接写入空数组，实现清空功能。

---

### 3.3 构建处理链（Chain）

#### 3.3.1 模型与 Prompt

```python
model = ChatTongyi(model="qwen-plus")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你需要根据历史对话回复用户问题"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "请回复如下问题{input}"),
    ]
)
```

**Prompt 结构说明：**

```
┌─────────────────────────────────────┐
│  SYSTEM: 你需要根据历史对话回复用户问题  │  ← 系统提示
├─────────────────────────────────────┤
│  [chat_history 占位符]               │  ← 历史消息会插入这里
├─────────────────────────────────────┤
│  HUMAN: 请回复如下问题{input}         │  ← 用户当前输入
└─────────────────────────────────────┘
```

#### 3.3.2 调试函数

```python
def print_prompt(prompt_value):
    """打印调试信息，显示完整的 Prompt 结构"""
    print("\n" + "=" * 30 + " PROMPT DEBUG " + "=" * 30)
    for msg in prompt_value.messages:
        print(f"[{msg.type.upper()}]: {msg.content}")
    print("=" * 74 + "\n")
    return prompt_value
```

**作用**：在 Prompt 传入模型前打印完整内容，方便调试。通过 `RunnableLambda` 包装后插入到链中。

#### 3.3.3 基础链

```python
base_chain = prompt | RunnableLambda(print_prompt) | model | StrOutputParser()
```

**链的组成：**

```
prompt → print_prompt(调试) → model(LLM) → StrOutputParser(提取文本)
```

使用 LangChain 的 `|` 运算符（管道符）串联各个组件。

---

### 3.4 记忆包装器

#### 3.4.1 获取会话历史的函数

```python
def get_chat_history(session_id: str) -> BaseChatMessageHistory:
    """
    关键变化：这里返回的是 FileChatMessageHistory 实例
    不同的 session_id 对应不同的物理文件
    """
    return FileChatMessageHistory(session_id)
```

这是一个**工厂函数**，根据 `session_id` 返回对应的记忆实例。

#### 3.4.2 创建带记忆的链

```python
conversation_chain = RunnableWithMessageHistory(
    base_chain,
    get_chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)
```

**参数说明：**

| 参数 | 说明 |
|-----|------|
| `base_chain` | 基础处理链 |
| `get_chat_history` | 获取记忆实例的函数 |
| `input_messages_key` | 用户输入在参数字典中的 key |
| `history_messages_key` | 历史消息在 Prompt 模板中的占位符变量名 |

---

### 3.5 使用示例

```python
if __name__ == "__main__":
    session_config: RunnableConfig = {
        "configurable": {"session_id": "user_001"}
    }
    
    questions = [
        # "小明有1只猫",
        # "小明有4只狗",
        "宠物总数是多少"
    ]
    
    for q in questions:
        print(f"\nUser: {q}")
        response = conversation_chain.invoke(
            {"input": q},
            config=session_config
        )
        print(f"AI: {response}")
```

**使用步骤：**

1. 配置 `session_id`，标识唯一会话
2. 调用 `conversation_chain.invoke()` 传入问题
3. 系统自动读取历史 → 生成回复 → 保存历史

---

## 📁 四、文件存储格式

### 4.1 存储结构

```
./chat_history/
├── user_001          # 会话1的历史文件
├── user_002          # 会话2的历史文件
└── ...
```

### 4.2 JSON 文件内容示例

```json
[
  {
    "type": "human",
    "data": {
      "content": "小明有1只猫",
      "additional_kwargs": {},
      "response_metadata": {}
    }
  },
  {
    "type": "ai",
    "data": {
      "content": "好的，我知道了，小明有1只猫。",
      "additional_kwargs": {},
      "response_metadata": {}
    }
  }
]
```

每条消息包含：
- `type`：消息类型（human/ai/system）
- `data.content`：消息内容
- `additional_kwargs`：额外参数
- `response_metadata`：响应元数据

---

## 💡 五、关键知识点总结

### 5.1 必须实现的接口

自定义 `BaseChatMessageHistory` 子类时，必须实现以下方法：

| 方法/属性 | 类型 | 作用 |
|----------|------|------|
| `messages` | property | 获取所有历史消息 |
| `add_message()` | 方法 | 添加单条消息 |
| `add_messages()` | 方法 | 添加多条消息 |
| `clear()` | 方法 | 清空历史 |

### 5.2 RunnableWithMessageHistory 工作原理

```
调用 invoke(input, config)
        │
        ├─► 从 config 中提取 session_id
        │
        ├─► 调用 get_chat_history(session_id) 获取记忆对象
        │
        ├─► 读取 messages，注入到 Prompt 的 chat_history 位置
        │
        ├─► 执行 base_chain，得到回复
        │
        └─► 将用户输入和AI回复都 add_messages 到记忆中
```

### 5.3 消息序列化机制

LangChain 提供了标准的消息序列化工具：

```python
# 消息对象 → 字典（用于存储）
message_to_dict(message)

# 字典列表 → 消息对象列表（用于读取）
messages_from_dict(messages_list)
```

这使得我们可以轻松将消息保存到文件、数据库等任何存储介质。

---

## ⚖️ 六、优缺点分析

### 6.1 优点

| 优点 | 说明 |
|-----|------|
| ✅ **实现简单** | 几十行代码即可完成 |
| ✅ **持久化存储** | 程序重启不丢失 |
| ✅ **多会话隔离** | session_id 对应不同文件 |
| ✅ **标准兼容** | 完全兼容 LangChain 接口 |
| ✅ **易于调试** | JSON 文件可读可编辑 |

### 6.2 缺点

| 缺点 | 说明 | 改进方向 |
|-----|------|---------|
| ❌ **全量写入** | 每次追加都重写整个文件 | 改用追加写入或数据库 |
| ❌ **并发不安全** | 多进程同时写可能损坏文件 | 加文件锁或用数据库 |
| ❌ **查询效率低** | 不能按条件检索历史消息 | 改用数据库存储 |
| ❌ **无过期机制** | 历史消息会无限增长 | 添加截断或TTL机制 |

---

## 🚀 七、扩展思路

### 7.1 其他存储方案

| 存储方式 | 适用场景 | 优点 |
|---------|---------|------|
| **文件 (JSON)** | 小型应用、调试 | 简单、直观 |
| **SQLite** | 中小型应用 | 支持查询、事务 |
| **Redis** | 高并发、需要TTL | 性能好、自动过期 |
| **PostgreSQL** | 生产级应用 | 强大的查询能力 |
| **向量数据库** | 需要语义检索 | 支持相似度搜索 |

### 7.2 记忆优化策略

1. **滑动窗口记忆**：只保留最近 N 条消息
2. **摘要记忆**：对历史对话进行摘要，节省 token
3. **混合记忆**：短期记忆 + 长期记忆结合
4. **知识库检索**：从历史中检索相关片段

### 7.3 生产环境建议

- 使用数据库（如 Redis、PostgreSQL）替代文件存储
- 添加会话过期清理机制
- 实现记忆的加密存储（涉及隐私数据）
- 添加记忆的导入导出功能

---

## 📝 八、快速上手模板

```python
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from typing import Sequence

class MyCustomHistory(BaseChatMessageHistory):
    """自定义记忆类模板"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        # 初始化你的存储连接
    
    @property
    def messages(self) -> list[BaseMessage]:
        # 从你的存储中读取并反序列化消息
        pass
    
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # 将消息序列化后存入你的存储
        pass
    
    def clear(self) -> None:
        # 清空当前会话的消息
        pass
```

---

## 🎯 九、常见问题

**Q1: 为什么不直接用列表存内存里？**
> 因为程序重启后数据就丢了。文件存储可以实现真正的"长期记忆"。

**Q2: session_id 有什么用？**
> 用来区分不同用户或不同对话。每个 session_id 对应独立的历史记录，互不干扰。

**Q3: 历史消息太多会不会爆 token？**
> 会的。实际项目中通常会配合滑动窗口、摘要等策略，控制传给模型的历史消息长度。

**Q4: FileChatMessageHistory 和 RedisChatMessageHistory 有什么区别？**
> 存储介质不同。文件版适合开发调试，Redis 版适合生产环境，性能更好、支持过期。

---

## 📚 十、参考资料

- LangChain 官方文档：[Chat Message History](https://python.langchain.com/docs/modules/memory/chat_message_histories/)
- LangChain 官方文档：[RunnableWithMessageHistory](https://python.langchain.com/docs/expression_language/how_to/message_history/)

---

> 💡 **学习建议**：先跑通文件版，理解记忆机制后，再尝试用 Redis 或数据库实现自己的记忆存储。
