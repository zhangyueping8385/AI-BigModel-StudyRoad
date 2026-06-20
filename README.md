# LangChain 学习总笔记

> 从 API 调用到 RAG 实战，全面掌握 LangChain 核心知识体系

---

## 📚 总览

### 学习路径

```
基础篇 → LangChain核心篇 → 数据处理篇 → RAG实战篇 → Memory篇
```

### 知识体系

| 模块 | 核心内容 | 重要程度 |
|-----|---------|---------|
| **大模型 API** | OpenAI SDK、流式输出、多轮对话 | ⭐⭐⭐ |
| **提示词工程** | Few-Shot、文本分类、信息抽取、文本匹配 | ⭐⭐⭐⭐ |
| **算法基础** | 余弦相似度 | ⭐⭐⭐ |
| **LangChain 模型** | LLM、Chat Model、流式输出 | ⭐⭐⭐ |
| **提示词模板** | PromptTemplate、FewShot、ChatPromptTemplate | ⭐⭐⭐⭐ |
| **链（Chain）** | LCEL、RunnablePassthrough、多分支 | ⭐⭐⭐⭐⭐ |
| **文档加载** | CSV、JSON、TXT、PDF Loader | ⭐⭐⭐ |
| **文本分割** | RecursiveCharacterTextSplitter | ⭐⭐⭐⭐ |
| **向量存储** | InMemory、Chroma、增删查 | ⭐⭐⭐⭐⭐ |
| **RAG** | 检索增强生成、优化技巧 | ⭐⭐⭐⭐⭐ |
| **Memory** | 会话记忆、多种记忆类型 | ⭐⭐⭐⭐ |

---

# 第一篇：基础篇

## 第1章 大模型 API 调用基础

### 1.1 OpenAI SDK 基础调用

**核心代码**：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 兼容接口
)

response = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ]
)

print(response.choices[0].message.content)
```

**关键点**：
- `api_key`：API 密钥，从平台获取
- `base_url`：兼容模式的接口地址
- `model`：模型名称
- `messages`：消息列表，包含角色和内容

### 1.2 消息的三种角色

| 角色 | 说明 | 作用 |
|-----|------|------|
| `system` | 系统消息 | 设置大模型的行为、人设、规则 |
| `user` | 用户消息 | 用户的提问 |
| `assistant` | 助手消息 | 大模型的回复 |

### 1.3 响应结构

```python
response.choices[0].message.content  # 回复内容
response.choices[0].message.role     # 角色（assistant）
response.usage.prompt_tokens         # 输入 token 数
response.usage.completion_tokens     # 输出 token 数
response.usage.total_tokens          # 总 token 数
```

---

## 第2章 流式输出

### 2.1 为什么需要流式输出？

- 用户体验好：打字机效果，不用等全部生成完
- 减少等待：边生成边显示
- 适合长文本：大段文字不用等很久

### 2.2 核心代码

```python
response = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "写一篇文章"}],
    stream=True  # 开启流式输出
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**关键点**：
- `stream=True`：开启流式模式
- `delta.content`：每次返回的片段内容
- SSE（Server-Sent Events）协议：服务器推送技术

---

## 第3章 多轮对话与历史消息

### 3.1 大模型是无状态的

大模型**不会记住**之前的对话，每次调用都是独立的。要实现多轮对话，需要**手动把历史消息传进去**。

### 3.2 核心代码

```python
history = []

# 第一轮
history.append({"role": "user", "content": "你好"})
response = client.chat.completions.create(
    model="qwen-plus",
    messages=history
)
reply = response.choices[0].message.content
history.append({"role": "assistant", "content": reply})

# 第二轮
history.append({"role": "user", "content": "你叫什么名字？"})
response = client.chat.completions.create(
    model="qwen-plus",
    messages=history
)
```

### 3.3 历史消息优化策略

| 策略 | 说明 | 适用场景 |
|-----|------|---------|
| **固定窗口** | 只保留最近 N 条消息 | 简单对话 |
| **Token 限制** | 控制总 token 数不超过上限 | 长对话 |
| **摘要总结** | 把旧对话总结成一条摘要 | 超长对话 |
| **滑动窗口** | 保留最近的 N 个 token | 平衡效果 |

> 💡 面试常考：大模型是有状态还是无状态的？如何实现多轮对话？

---

## 第4章 提示词工程

### 4.1 什么是提示词工程？

通过精心设计输入提示词，让大模型更好地完成任务。

### 4.2 Few-Shot 学习（少样本学习）

给大模型几个示例，让它学习规律，然后处理新的输入。

**示例：文本分类**

```python
prompt = """
请将以下文本分类为「正面」或「负面」。

文本：这个产品质量很好，我很满意
分类：正面

文本：物流太慢了，体验很差
分类：负面

文本：客服态度不错，问题都解决了
分类：正面

文本：{text}
分类：
"""
```

### 4.3 三大经典任务

| 任务 | 说明 | 输出格式 |
|-----|------|---------|
| **文本分类** | 判断文本属于哪个类别 | 单个标签 |
| **信息抽取** | 从文本中提取指定信息 | JSON 结构化 |
| **文本匹配** | 判断两段文本意思是否相同 | 是/否 |

### 4.4 提示词设计原则

1. **明确任务**：清晰说明要做什么
2. **给出示例**：Few-Shot 效果更好
3. **指定格式**：明确输出格式（如 JSON）
4. **设定角色**：给大模型一个专业身份
5. **分步思考**：复杂任务让它一步步来

> 💡 面试常考：你知道哪些提示词技巧？Few-Shot 是什么意思？

---

## 第5章 余弦相似度算法

### 5.1 什么是余弦相似度？

衡量两个向量方向的相似程度，值越接近 1 越相似。

### 5.2 公式

```
cos(θ) = (A · B) / (|A| × |B|)
```

- 分子：两个向量的点积（对应位置相乘再相加）
- 分母：两个向量的模长相乘

### 5.3 Python 实现

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)
```

### 5.4 在文本中的应用

```
文本 → Embedding 模型 → 向量 → 计算余弦相似度 → 判断相似程度
```

**相似度范围**：[-1, 1]
- 接近 1：非常相似
- 接近 0：不相关
- 接近 -1：相反

> 💡 面试常考：余弦相似度的公式和原理？和欧氏距离的区别？

---

# 第二篇：LangChain 核心篇

## 第6章 LangChain 简介与模型调用

### 6.1 什么是 LangChain？

LangChain 是一个大模型应用开发框架，提供了很多现成的组件和工具，让你快速构建 LLM 应用。

**核心组件**：
- 模型（Models）
- 提示词模板（Prompts）
- 链（Chains）
- 文档加载器（Document Loaders）
- 向量存储（Vector Stores）
- 记忆（Memory）
- 代理（Agents）

### 6.2 LLM 模型调用

```python
from langchain_community.llms import Tongyi

llm = Tongyi(model_name="qwen-plus")
result = llm.invoke("你好")
print(result)
```

### 6.3 Chat Model 调用

```python
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage

chat = ChatTongyi(model="qwen-plus")

messages = [
    SystemMessage(content="你是一个翻译官"),
    HumanMessage(content="你好")
]

result = chat.invoke(messages)
print(result.content)
```

### 6.4 消息对象

| 类 | 对应角色 |
|----|---------|
| `SystemMessage` | system |
| `HumanMessage` | user |
| `AIMessage` | assistant |

### 6.5 消息简写形式

用元组代替消息对象，更简洁：

```python
messages = [
    ("system", "你是一个翻译官"),
    ("human", "你好")
]
```

### 6.6 流式输出

```python
for chunk in chat.stream("写一首诗"):
    print(chunk.content, end="")
```

---

## 第7章 提示词模板（PromptTemplate）

### 7.1 为什么需要模板？

- 复用：相同结构的提示词不用重复写
- 变量：动态替换内容
- 规范：统一格式

### 7.2 基础用法

```python
from langchain_core.prompts import PromptTemplate

template = "请将以下文本翻译成{language}：{text}"

prompt = PromptTemplate.from_template(template)

result = prompt.format(language="英文", text="你好")
print(result)
# 输出：请将以下文本翻译成英文：你好
```

### 7.3 模板变量

- 用 `{变量名}` 表示占位符
- `format()` 方法传入变量值
- 变量名必须和模板中的一致

---

## 第8章 聊天提示词模板（ChatPromptTemplate）

### 8.1 基础用法

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    ("human", "{question}")
])

messages = prompt.format_messages(role="翻译官", question="你好")
```

### 8.2 MessagesPlaceholder

用于插入动态数量的消息（如历史对话）：

```python
from langchain_core.prompts import MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    MessagesPlaceholder("history"),  # 占位符，传入消息列表
    ("human", "{question}")
])

messages = prompt.format_messages(
    history=[("human", "你好"), ("ai", "你好！")],
    question="你叫什么名字？"
)
```

> 💡 MessagesPlaceholder 是实现多轮对话的关键，经常和 Memory 一起使用。

### 8.3 Few-Shot 提示词模板

```python
from langchain_core.prompts import FewShotPromptTemplate

examples = [
    {"input": "你好", "output": "Hello"},
    {"input": "谢谢", "output": "Thank you"},
]

example_prompt = PromptTemplate.from_template(
    "输入：{input}\n输出：{output}"
)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="请翻译以下中文为英文：",
    suffix="输入：{text}\n输出：",
    input_variables=["text"]
)
```

---

## 第9章 链（Chain）与 LCEL

### 9.1 什么是 LCEL？

**LCEL（LangChain Expression Language）** 是 LangChain 的表达式语言，用管道符 `|` 把各个组件连接起来，形成一条链。

### 9.2 基础链

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | model | StrOutputParser()

result = chain.invoke({"question": "你好"})
```

**执行流程**：

```
输入字典 → prompt（生成提示词）→ model（调用大模型）→ StrOutputParser（提取文本）→ 输出
```

### 9.3 为什么用 LCEL？

- 简洁：一行代码搞定
- 统一接口：所有组件都支持 invoke、stream、batch
- 易于组合：像搭积木一样组合
- 支持流式：整条链都支持流式输出

### 9.4 常用接口

| 方法 | 说明 |
|-----|------|
| `invoke(input)` | 执行一次，返回完整结果 |
| `stream(input)` | 流式执行，逐块返回 |
| `batch(inputs)` | 批量执行多个输入 |

---

## 第10章 RunnablePassthrough 与多分支链

### 10.1 RunnablePassthrough

透传输入，不做任何处理。

```python
from langchain_core.runnables import RunnablePassthrough

passthrough = RunnablePassthrough()
result = passthrough.invoke("hello")
# 输出：hello
```

### 10.2 字典形式的多分支链

字典中的每个 value 都是一个 Runnable，**并行执行**，结果合并成字典。

```python
chain = {
    "question": RunnablePassthrough(),
    "context": retriever | format_func
} | prompt | model
```

**执行流程**：

```
输入 "问题"
    ├─→ RunnablePassthrough() ──→ "问题"  (question 的值)
    └─→ retriever ──→ format_func ──→ "上下文"  (context 的值)
                                    ↓
                          合并成字典
                          {"question": "问题", "context": "上下文"}
                                    ↓
                                  prompt
                                    ↓
                                  model
```

### 10.3 itemgetter 提取字段

当输入是字典时，用 `itemgetter` 提取指定字段：

```python
from operator import itemgetter

chain = {
    "context": itemgetter("question") | retriever,
    "question": itemgetter("question"),
    "language": itemgetter("language")
} | prompt | model
```

### 10.4 标准 RAG 链写法（必须记住）

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

answer = rag_chain.invoke("什么是 RAG？")
```

> 💡 面试必背：标准 RAG 链的写法。

---

# 第三篇：数据处理篇

## 第11章 文档加载器（Document Loader）

### 11.1 Document 对象

所有加载器都返回 `Document` 对象：

```python
Document(
    page_content="文本内容",
    metadata={"source": "文件名", "page": 0}
)
```

| 属性 | 说明 |
|-----|------|
| `page_content` | 文档的文本内容 |
| `metadata` | 元数据（来源、页码等） |

### 11.2 统一接口

所有 Loader 都有相同的接口：
- `load()`：加载所有文档，返回列表
- `lazy_load()`：懒加载，逐个返回（适合大文件）

### 11.3 常用加载器

#### CSVLoader

```python
from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(
    file_path="data.csv",
    encoding="utf-8",
    source_column="name"  # 用哪一列作为 source
)
docs = loader.load()
```

**特点**：每行一个 Document

#### JSONLoader

```python
from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="data.json",
    jq_schema=".[]",
    text_content=False
)
docs = loader.load()
```

**jq_schema**：指定提取路径，如 `.[]` 表示数组的每个元素

#### TextLoader

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("data.txt", encoding="utf-8")
docs = loader.load()
```

**特点**：整个文件一个 Document，通常需要配合文本分割器使用

#### PyPDFLoader

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(
    file_path="doc.pdf",
    mode="page"  # page：每页一个；single：整体一个
)
docs = loader.load()
```

**两种模式**：

| 模式 | 说明 | Document 数量 |
|-----|------|--------------|
| `page` | 每页一个 Document | 等于页数 |
| `single` | 所有页合并成一个 | 1个 |

**注意**：PyPDFLoader 只能提取文本层，扫描版 PDF（图片）需要 OCR

> 💡 面试常考：你用过哪些文档加载器？Document 对象有什么属性？

---

## 第12章 文本分割器（Text Splitter）

### 12.1 为什么需要分割？

- 文档太长，超过大模型上下文窗口
- 向量化时，太长的向量效果不好
- RAG 检索时，粒度太粗找不到精准内容

### 12.2 RecursiveCharacterTextSplitter

最常用的文本分割器，按优先级尝试不同分隔符：

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每块大小（字符数）
    chunk_overlap=50,    # 重叠字符数
    separators=["\n\n", "\n", "。", " ", ""]  # 分隔符优先级
)

split_docs = splitter.split_documents(docs)
```

### 12.3 关键参数

| 参数 | 说明 | 建议值 |
|-----|------|--------|
| `chunk_size` | 每块的大小 | 500-1000 |
| `chunk_overlap` | 块之间的重叠 | chunk_size 的 10% |
| `separators` | 分隔符列表（按优先级） | 默认即可 |

### 12.4 重叠（Overlap）的作用

- 防止语义被切断
- 保持上下文连贯性
- 提高检索准确率

```
块1：[这是第一段。这是第二段的前半部分]
块2：      [这是第二段的后半部分。这是第三段]
```

> 💡 面试常考：为什么要做文本分割？chunk_size 和 chunk_overlap 怎么设置？

---

## 第13章 向量存储（Vector Store）

### 13.1 什么是向量存储？

专门用来存储和检索向量的数据库，支持相似度搜索。

**工作原理**：

```
文档 → Embedding → 向量 → 存入向量库
问题 → Embedding → 向量 → 相似度搜索 → 返回最相似的文档
```

### 13.2 InMemoryVectorStore（内存存储）

```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import DashScopeEmbeddings

vector_store = InMemoryVectorStore(
    embedding=DashScopeEmbeddings()
)
```

**特点**：
- ✅ 速度快
- ✅ 无需安装
- ❌ 程序退出数据丢失
- 适合：开发测试、临时使用

### 13.3 Chroma（持久化存储）

```python
from langchain_chroma import Chroma

vector_store = Chroma(
    collection_name="my_collection",
    embedding_function=DashScopeEmbeddings(),
    persist_directory="./chroma_db"
)
```

**特点**：
- ✅ 数据持久化，下次启动还在
- ✅ 本地部署，简单易用
- 需要安装：`langchain-chroma`、`chromadb`
- 适合：生产环境、长期使用

> ⚠️ 注意：Chroma 的参数名是 `embedding_function`，InMemory 是 `embedding`

### 13.4 基本操作

#### 添加

```python
# 添加文本
vector_store.add_texts(["文本1", "文本2"])

# 添加 Document
vector_store.add_documents(docs, ids=["id1", "id2"])
```

#### 删除

```python
vector_store.delete(["id1", "id2"])
```

#### 查询

```python
# 相似度搜索
results = vector_store.similarity_search("查询文本", k=3)

# 带分数的搜索
results = vector_store.similarity_search_with_score("查询", k=3)
```

### 13.5 as_retriever()

把向量库转成检索器（Retriever），可以直接用在 LCEL 链中：

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
```

**输入**：字符串
**输出**：Document 列表

### 13.6 其他向量数据库

| 数据库 | 特点 | 适用场景 |
|-------|------|---------|
| InMemory | 内存、无需安装 | 开发测试 |
| Chroma | 轻量、本地 | 中小项目 |
| FAISS | Facebook 开源、速度快 | 高性能 |
| Milvus | 分布式、功能强 | 大规模生产 |
| Pinecone | 云服务、托管 | 不想运维 |

> 💡 面试常考：你用过哪些向量数据库？Chroma 和 FAISS 的区别？

---

# 第四篇：RAG 实战篇

## 第14章 RAG 原理与实现

### 14.1 什么是 RAG？

**RAG（Retrieval-Augmented Generation，检索增强生成）** 是一种让大模型基于外部知识回答问题的技术。

### 14.2 为什么需要 RAG？

| 问题 | RAG 解决方案 |
|-----|-------------|
| 知识过时 | 从最新文档中检索 |
| 私有知识 | 接入企业内部文档 |
| 幻觉问题 | 基于事实回答 |
| 数据安全 | 不用把数据喂给模型训练 |

### 14.3 RAG 完整流程

```
┌──────────── 数据准备（离线） ────────────┐
│  文档 → 分割 → 向量化 → 存入向量库          │
└─────────────────────────────────────────┘
                    ↓
┌──────────── 问答阶段（在线） ────────────┐
│  用户提问 → 向量化 → 相似度搜索 → Top K    │
│                    ↓                      │
│  构建提示词（问题 + 检索到的上下文）        │
│                    ↓                      │
│  大模型生成回答 → 返回给用户                │
└─────────────────────────────────────────┘
```

### 14.4 标准 RAG 代码（必须掌握）

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ========== 1. 数据准备 ==========
# 加载文档
loader = TextLoader("knowledge.txt", encoding="utf-8")
docs = loader.load()

# 分割文本
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
split_docs = splitter.split_documents(docs)

# 存入向量库
embeddings = DashScopeEmbeddings()
vector_store = Chroma(
    collection_name="knowledge",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
vector_store.add_documents(split_docs)

# ========== 2. 构建 RAG 链 ==========
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

prompt = ChatPromptTemplate.from_template("""
你是一个专业的知识助手。请根据以下参考资料回答问题。

要求：
1. 只能使用参考资料中的信息
2. 如果参考资料中没有答案，请回答"根据现有资料无法回答"
3. 回答要简洁准确

参考资料：
{context}

用户问题：{question}

回答：
""")

model = ChatTongyi(model="qwen-plus")

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# ========== 3. 提问 ==========
answer = rag_chain.invoke("什么是 RAG？")
print(answer)
```

### 14.5 RAG 提示词要点

1. **角色设定**：告诉模型它的身份
2. **使用规则**：只能用参考资料，不知道就说不知道
3. **参考资料**：检索到的上下文
4. **用户问题**：用户的提问

> 💡 面试必背：RAG 的完整流程？如何实现一个 RAG 系统？

---

## 第15章 RAG 优化技巧

### 15.1 检索优化

| 技巧 | 说明 | 效果 |
|-----|------|------|
| **更好的 Embedding** | 用更强的向量模型 | 提升检索准确率 |
| **调整 chunk 大小** | 找到最合适的粒度 | 平衡精度和召回 |
| **增加 overlap** | 块之间多重叠一些 | 减少语义断裂 |
| **重排序（Rerank）** | 粗筛后再精排 | 提升 Top K 质量 |
| **多查询检索** | 把问题改写成多个查询 | 增加召回率 |
| **混合检索** | 向量 + 关键词 | 结合两者优势 |

### 15.2 生成优化

| 技巧 | 说明 |
|-----|------|
| **更好的提示词** | 明确规则、减少幻觉 |
| **引用来源** | 要求标注答案来源 |
| **分步思考** | 让模型先分析再回答 |
| **多轮验证** | 让模型自己检查答案 |

### 15.3 重排序（Rerank）

```
检索 10 个候选 → 重排序模型 → 选出 Top 3 → 传给大模型
```

**为什么需要重排序？**
- 向量检索是粗筛，速度快但精度一般
- 重排序模型更精确，但速度慢
- 结合两者：先快后精

### 15.4 多查询检索（Multi-Query）

```
用户问题 → 大模型改写成 3 个不同角度的查询 → 每个都检索 → 合并去重
```

**作用**：从多个角度检索，增加召回率

### 15.5 上下文压缩

检索到的文档可能很长，只提取和问题相关的片段：

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(model)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_store.as_retriever()
)
```

> 💡 面试常考：RAG 有哪些优化方法？如何提升 RAG 的准确率？

---

# 第五篇：Memory 记忆篇

## 第16章 会话记忆

### 16.1 为什么需要 Memory？

大模型是无状态的，每次对话都要把历史传进去。Memory 帮你自动管理历史消息。

### 16.2 ConversationBufferMemory

最简单的记忆，保存完整对话历史：

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
memory.save_context({"input": "你好"}, {"output": "你好！"})
memory.save_context({"input": "你叫什么？"}, {"output": "我叫小助手"})

history = memory.load_memory_variables({})
print(history["history"])
```

### 16.3 其他记忆类型

| 类型 | 说明 | 适用场景 |
|-----|------|---------|
| `ConversationBufferMemory` | 完整保存所有对话 | 短对话 |
| `ConversationBufferWindowMemory` | 只保留最近 K 轮 | 长对话 |
| `ConversationSummaryMemory` | 把历史总结成摘要 | 超长对话 |
| `ConversationTokenBufferMemory` | 按 token 数限制 | 精确控制长度 |

### 16.4 Memory + Chain

```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=model,
    memory=memory
)

conversation.predict(input="你好")
conversation.predict(input="你叫什么名字？")
```

> 💡 面试常考：LangChain 的 Memory 有什么用？你知道哪些 Memory 类型？

---

# 第六篇：面试高频问题

## 基础概念题

### Q1：什么是 LangChain？它有哪些核心组件？

**答**：
LangChain 是一个大模型应用开发框架，提供了丰富的组件和工具，帮助开发者快速构建 LLM 应用。

核心组件包括：
- **Models**：大模型封装（LLM、Chat Model）
- **Prompts**：提示词模板
- **Chains**：链，把多个组件串起来
- **Document Loaders**：文档加载器
- **Text Splitters**：文本分割器
- **Vector Stores**：向量存储
- **Memory**：会话记忆
- **Agents**：代理

### Q2：大模型是有状态的还是无状态的？如何实现多轮对话？

**答**：
大模型是**无状态**的，每次调用都是独立的，不会记住之前的对话。

实现多轮对话的方法：
1. 手动维护历史消息列表
2. 每次调用时把完整历史传进去
3. 用户消息和助手回复都要加入历史
4. 历史太长时需要做截断或摘要

### Q3：什么是 RAG？它解决了什么问题？

**答**：
RAG（Retrieval-Augmented Generation，检索增强生成）是一种让大模型基于外部知识回答问题的技术。

解决的问题：
1. **知识过时**：大模型训练数据有截止日期，RAG 可以检索最新文档
2. **私有知识**：大模型不知道企业内部数据，RAG 可以接入
3. **幻觉问题**：基于检索到的事实回答，减少胡说八道
4. **数据安全**：不用把私有数据喂给模型训练

### Q4：RAG 的完整流程是什么？

**答**：
分为两个阶段：

**数据准备阶段（离线）**：
1. 加载文档（Document Loader）
2. 文本分割（Text Splitter）
3. 向量化（Embedding）
4. 存入向量库（Vector Store）

**问答阶段（在线）**：
1. 用户提问
2. 问题向量化
3. 相似度搜索，找到最相关的 Top K 文档
4. 把问题和检索到的上下文组装成提示词
5. 大模型基于提示词生成回答
6. 返回给用户

### Q5：什么是向量数据库？为什么不用普通数据库？

**答**：
向量数据库是专门用来存储和检索向量的数据库。

和普通数据库的区别：
- 普通数据库：精确匹配（=、LIKE），存的是结构化数据
- 向量数据库：相似度搜索，存的是高维向量

为什么需要向量数据库：
1. **语义搜索**：能找到意思相近的，不只是关键词匹配
2. **检索速度**：专门优化了相似度计算，大数据量也很快
3. **专门功能**：内置了各种相似度算法、索引优化

---

## 技术细节题

### Q6：什么是余弦相似度？公式是什么？

**答**：
余弦相似度是衡量两个向量方向相似程度的指标，值越接近 1 越相似。

公式：
```
cos(θ) = (A · B) / (|A| × |B|)
```

- 分子：两个向量的点积（对应位置相乘再相加）
- 分母：两个向量的模长相乘

取值范围：[-1, 1]
- 接近 1：方向相同，非常相似
- 接近 0：方向垂直，不相关
- 接近 -1：方向相反，语义相反

### Q7：文本分割为什么要设置 chunk_overlap？

**答**：
chunk_overlap 是两个相邻文本块之间的重叠部分。

作用：
1. **防止语义断裂**：如果一块的结尾和下一块的开头说的是同一件事，没有重叠可能会被切断，导致语义不完整
2. **保持上下文**：重叠部分提供了上下文，让每块都有完整的语义
3. **提高检索准确率**：检索时更容易匹配到相关内容

一般设置为 chunk_size 的 10% 左右。

### Q8：LangChain 的 LCEL 是什么？有什么优势？

**答**：
LCEL（LangChain Expression Language）是 LangChain 的表达式语言，用管道符 `|` 把组件连接成链。

优势：
1. **简洁**：代码更简洁易读
2. **统一接口**：所有组件都支持 invoke、stream、batch
3. **流式支持**：整条链都支持流式输出
4. **易于组合**：像搭积木一样灵活组合
5. **易于调试**：每个环节都可以单独测试

示例：
```python
chain = prompt | model | StrOutputParser()
```

### Q9：RunnablePassthrough 是什么？有什么用？

**答**：
RunnablePassthrough 是一个"透传"的 Runnable，输入什么就输出什么，不做任何处理。

作用：
在构建多分支链时，有些分支需要对输入做处理，有些分支只需要把输入原样传下去。这时候就用 RunnablePassthrough 作为占位符。

示例：
```python
chain = {
    "question": RunnablePassthrough(),  # 直接透传
    "context": retriever | format_func   # 处理后再传
} | prompt | model
```

### Q10：Chroma 和 InMemoryVectorStore 的区别？

**答**：

| 对比项 | InMemoryVectorStore | Chroma |
|-------|---------------------|--------|
| 存储位置 | 内存 | 磁盘 |
| 持久化 | 程序退出就没了 | 永久保存 |
| 速度 | 极快 | 快 |
| 安装依赖 | 不需要 | 需要安装 chromadb |
| 适用场景 | 开发测试、临时数据 | 生产环境、长期使用 |

---

## 实战应用题

### Q11：如何实现一个简单的 RAG 系统？

**答**：
核心步骤：

1. **准备数据**：用 DocumentLoader 加载文档
2. **文本分割**：用 TextSplitter 切成小块
3. **向量化存储**：用 Embedding 模型转成向量，存入 VectorStore
4. **构建检索器**：as_retriever() 转成检索器
5. **构建提示词**：把检索到的上下文和问题组合起来
6. **构建 RAG 链**：用 LCEL 把检索器、提示词、模型串起来
7. **问答**：调用链获取回答

核心代码：
```python
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

### Q12：RAG 效果不好怎么优化？

**答**：
可以从检索和生成两个方面优化：

**检索优化**：
1. 换更好的 Embedding 模型
2. 调整 chunk_size 和 chunk_overlap
3. 增加检索数量 k 值
4. 加重排序（Rerank），先粗筛再精排
5. 多查询检索（Multi-Query），从多个角度检索
6. 混合检索，向量检索 + 关键词检索结合

**生成优化**：
1. 优化提示词，明确规则
2. 要求模型引用来源
3. 加入"不知道就说不知道"的约束
4. 让模型分步思考

### Q13：如何处理长对话的历史消息？

**答**：
几种策略：

1. **固定窗口**：只保留最近 N 轮对话，简单但会丢失早期信息
2. **Token 限制**：控制总 token 数不超过模型上限，比固定窗口更精确
3. **摘要记忆**：把旧的对话总结成摘要，保留关键信息，节省 token
4. **滑动窗口**：保留最近的 N 个 token，平衡效果和成本

一般来说，短对话用固定窗口，长对话用摘要记忆。

### Q14：你知道哪些文档加载器？各有什么特点？

**答**：

- **CSVLoader**：加载 CSV 文件，每行一个 Document，适合表格数据
- **JSONLoader**：加载 JSON 文件，用 jq_schema 指定提取路径，适合结构化数据
- **TextLoader**：加载纯文本，整个文件一个 Document，适合文章、日志
- **PyPDFLoader**：加载 PDF，支持按页或整体模式，适合论文、文档
- **DirectoryLoader**：批量加载目录下的多个文件

所有加载器都返回 Document 对象，有统一的 load() 和 lazy_load() 接口。

### Q15：Few-Shot 是什么？和 Zero-Shot、One-Shot 的区别？

**答**：

- **Zero-Shot**：不给示例，直接让模型做任务，效果最差
- **One-Shot**：给一个示例，让模型学习规律
- **Few-Shot**：给多个示例，效果更好，是最常用的

示例越多，模型越容易理解任务要求，输出质量越高。但示例太多会增加 token 成本，需要平衡效果和成本。

---

# 第七篇：实战代码模板

## 模板 1：基础对话

```python
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage

model = ChatTongyi(model="qwen-plus")

messages = [
    SystemMessage(content="你是一个专业的助手"),
    HumanMessage(content="你好")
]

result = model.invoke(messages)
print(result.content)
```

## 模板 2：流式输出

```python
for chunk in model.stream("写一首关于春天的诗"):
    print(chunk.content, end="")
```

## 模板 3：提示词模板 + 链

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    ("human", "{question}")
])

chain = prompt | model | StrOutputParser()

result = chain.invoke({
    "role": "翻译官",
    "question": "你好"
})
```

## 模板 4：文本分割

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

split_docs = splitter.split_documents(docs)
```

## 模板 5：向量库操作

```python
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

# 创建
vector_store = Chroma(
    collection_name="my_collection",
    embedding_function=DashScopeEmbeddings(),
    persist_directory="./chroma_db"
)

# 添加
vector_store.add_documents(docs, ids=["id1", "id2"])

# 搜索
results = vector_store.similarity_search("查询", k=3)

# 删除
vector_store.delete(["id1"])
```

## 模板 6：标准 RAG 链（最重要）

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 检索器
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 格式化函数
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 提示词
prompt = ChatPromptTemplate.from_template("""
请根据以下参考资料回答问题。
如果没有答案，请回答"根据现有资料无法回答"。

参考资料：
{context}

问题：{question}

回答：
""")

# RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# 使用
answer = rag_chain.invoke("你的问题")
```

## 模板 7：多输入 + itemgetter

```python
from operator import itemgetter

chain = (
    {
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question"),
        "language": itemgetter("language")
    }
    | prompt
    | model
    | StrOutputParser()
)

result = chain.invoke({
    "question": "什么是 RAG？",
    "language": "英文"
})
```

## 模板 8：带记忆的对话

```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=model,
    memory=memory
)

# 多轮对话
conversation.predict(input="你好")
conversation.predict(input="你叫什么名字？")
conversation.predict(input="你能做什么？")
```

---

# 第八篇：学习路线与建议

## 学习路线

```
第1阶段：基础
├── 大模型 API 调用
├── 流式输出
├── 多轮对话
└── 提示词工程

第2阶段：LangChain 核心
├── 模型调用（LLM / Chat Model）
├── 提示词模板
├── 链（LCEL）
└── RunnablePassthrough / 多分支

第3阶段：数据处理
├── 文档加载器
├── 文本分割器
└── 向量存储

第4阶段：RAG 实战
├── RAG 基础实现
├── RAG 优化技巧
└── 项目实战

第5阶段：进阶
├── Memory 记忆
├── Agents 代理
└── 工具调用
```

## 学习建议

### 1. 动手实践最重要
- 每学一个知识点，都要写代码跑一遍
- 不要只看不练，大模型开发是实践出来的
- 试着用自己的文档做一个 RAG 问答系统

### 2. 理解原理，不只是调 API
- 知道每个组件是干什么的，为什么需要它
- 理解 RAG 的完整流程，每个环节的作用
- 遇到问题知道从哪里排查

### 3. 重点掌握 RAG
- RAG 是目前大模型落地最主要的方式
- 面试必问，工作必用
- 从基础实现到优化技巧，都要掌握

### 4. 记住标准代码模板
- 标准 RAG 链的写法
- 提示词模板的写法
- 向量库的基本操作
- 这些是日常开发中用得最多的

### 5. 关注效果评估
- RAG 效果好不好，怎么评估？
- 检索准确率、回答准确率、幻觉率
- 学会用数据驱动优化

---

## 常用速查表

### LCEL 常用写法

| 写法 | 含义 |
|-----|------|
| `a \| b` | 顺序执行 |
| `{"k": runnable}` | 并行执行，合并成字典 |
| `RunnablePassthrough()` | 透传输入 |
| `itemgetter("key")` | 从字典取字段 |
| `StrOutputParser()` | 提取字符串输出 |

### Vector Store 操作

| 操作 | 方法 |
|-----|------|
| 添加文本 | `add_texts(texts)` |
| 添加文档 | `add_documents(docs, ids=...)` |
| 删除 | `delete(ids)` |
| 搜索 | `similarity_search(query, k)` |
| 带分搜索 | `similarity_search_with_score(query, k)` |
| 转检索器 | `as_retriever(search_kwargs={"k": 3})` |

### Document Loader 对比

| 加载器 | 文件格式 | 特点 |
|-------|---------|------|
| CSVLoader | CSV | 每行一个 Document |
| JSONLoader | JSON | jq_schema 提取 |
| TextLoader | TXT | 整个文件一个 |
| PyPDFLoader | PDF | 按页 / 整体模式 |

---

> 💡 **总结**：LangChain 的核心是"组合"——把模型、提示词、检索、记忆等组件像搭积木一样组合起来，构建复杂的大模型应用。RAG 是目前最主流、最实用的应用场景，一定要重点掌握。
