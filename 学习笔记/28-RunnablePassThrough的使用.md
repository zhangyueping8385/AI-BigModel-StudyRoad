# 28 - RunnablePassthrough 的使用

> 学习 LangChain 中 RunnablePassthrough 的用法，掌握 LCEL 链中多输入分支的构建方式

---

## 📚 一、代码概述

本代码演示了**RunnablePassthrough** 的使用，以及如何在 LCEL 链中构建多输入分支，将用户输入同时传给多个处理路径，最终合并成一个字典传给提示词模板。

这是构建 RAG 链的标准写法，也是 LCEL 最常用的模式之一。

### 1.1 核心功能

- ✅ RunnablePassthrough 直接传递输入
- ✅ as_retriever() 将向量库转成检索器
- ✅ 字典形式的多分支链
- ✅ 检索器 + 格式化函数组合
- ✅ 完整的 RAG 链构建

---

## 🔧 二、核心代码解析

### 2.1 导入相关类

```python
from langchain_core.runnables import RunnablePassthrough
```

**RunnablePassthrough** 是一个"透传"的 Runnable，它接收什么输入，就原样输出什么。

### 2.2 创建检索器

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 1})
```

**`as_retriever()` 方法**：
- 将向量存储（VectorStore）转换成检索器（Retriever）
- 检索器是 Runnable 的子类，可以直接用在 LCEL 链中
- 输入：查询字符串
- 输出：Document 对象列表

**参数**：
- `search_kwargs`：搜索参数，比如 `{"k": 1}` 表示返回最相似的 1 个结果

> 💡 为什么要用 as_retriever？因为向量库本身不是 Runnable，不能直接用 `|` 连接到链里。转成 Retriever 后就可以了。

### 2.3 格式化函数

```python
def format_func(docs: list[Document]):
    if not docs:
        return "无相关参考资料"
    format_str = "["
    for doc in docs:
        format_str += doc.page_content
    format_str += "]"
    return format_str
```

这个函数的作用：
- 接收检索器返回的 Document 列表
- 把多个文档的内容拼接成一个字符串
- 处理空结果的情况
- 返回格式化后的文本，作为提示词的 context

### 2.4 构建多分支链

```python
chain = (
    {
        "input": RunnablePassthrough(),
        "context": retriever | format_func
    }
    | prompt
    | print_prompt
    | model
    | StrOutputParser()
)
```

这是最关键的部分！让我们拆解一下：

**字典形式的输入**：
```python
{
    "input": RunnablePassthrough(),    # 分支1：直接透传用户输入
    "context": retriever | format_func  # 分支2：检索 + 格式化
}
```

**执行流程**：

```
用户输入 "怎么减肥？"
    ├─→ RunnablePassthrough() ──→ "怎么减肥？"
    │                              ↓
    │                           "input" 的值
    │
    └─→ retriever ──→ [Document] ──→ format_func ──→ "[减肥就是要少吃多练...]"
                                                                 ↓
                                                             "context" 的值
                                    ↓
                          合并成字典
                          {
                              "input": "怎么减肥？",
                              "context": "[减肥就是要少吃多练...]"
                          }
                                    ↓
                                  prompt
                                    ↓
                                  model
                                    ↓
                            StrOutputParser
                                    ↓
                               回答字符串
```

> 💡 字典中的每个值都是一个 Runnable（或可以转成 Runnable 的东西），它们会**并行执行**，然后把结果合并成一个字典传给下一个环节。

### 2.5 调用链

```python
res = chain.invoke(input_text)
print(res)
```

直接传入用户输入字符串即可，不需要手动构建字典。

---

## 💡 三、关键知识点

### 3.1 什么是 RunnablePassthrough？

**RunnablePassthrough** 是一个最简单的 Runnable，它的作用就是：**输入什么，输出什么**。

```python
from langchain_core.runnables import RunnablePassthrough

passthrough = RunnablePassthrough()

result = passthrough.invoke("hello")
print(result)  # 输出: hello
```

就像一根"直通管道"，不做任何处理，直接把输入传下去。

### 3.2 为什么需要 RunnablePassthrough？

在 LCEL 中，当你需要构建多分支链时，有些分支需要对输入做处理，有些分支只需要把输入原样传下去。

**举个例子**：

```
输入 "问题"
    ├─→ 直接传给提示词的 {question} 变量
    └─→ 先检索，再传给提示词的 {context} 变量
```

第二个分支需要 `retriever | format_func` 来处理。

第一个分支呢？什么都不用做，直接传下去就行。这时候就用 `RunnablePassthrough()`。

```python
{
    "question": RunnablePassthrough(),  # 直接透传
    "context": retriever | format_func   # 处理后再传
}
```

> 💡 简单理解：RunnablePassthrough 就是"什么都不做，直接传"的占位符。

### 3.3 字典形式的链（并行执行）

在 LCEL 中，当你用一个字典作为链的一部分时：

```python
{
    "key1": runnable1,
    "key2": runnable2,
    "key3": runnable3
}
```

**特点**：
1. 每个 value 都是一个 Runnable
2. 所有 Runnable **并行执行**
3. 输入会同时传给每个 Runnable
4. 执行完成后，结果合并成一个字典
5. 这个字典作为下一个环节的输入

**示意图**：

```
           输入
            │
     ┌──────┼──────┐
     ↓      ↓      ↓
  run1    run2    run3
     ↓      ↓      ↓
  val1    val2    val3
     └──────┼──────┘
            ↓
    {k1:v1, k2:v2, k3:v3}
            ↓
         下一个环节
```

### 3.4 普通函数也能放进链里

注意代码中的 `format_func` 是一个普通的 Python 函数，但可以直接用 `|` 连接：

```python
retriever | format_func
```

这是因为 LangChain 会自动把普通函数包装成 RunnableLambda。

**两种写法等价**：

```python
# 写法1：直接用函数
retriever | format_func

# 写法2：显式包装
from langchain_core.runnables import RunnableLambda
retriever | RunnableLambda(format_func)
```

> 💡 只要函数接收一个参数、返回一个值，就可以直接放进链里。

---

## 🎯 四、常见使用模式

### 4.1 最简 RAG 链（标准写法）

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 检索器
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 格式化函数
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# 使用
answer = rag_chain.invoke("什么是 RAG？")
```

> 💡 这是 LangChain 官方推荐的 RAG 写法，记住这个模板。

### 4.2 多输入分支

```python
# 三个分支并行处理
chain = (
    {
        "user_input": RunnablePassthrough(),
        "translation": translate_runnable,
        "summary": summary_runnable
    }
    | final_prompt
    | model
)
```

### 4.3 嵌套字典链

```python
chain = (
    {
        "question": RunnablePassthrough(),
        "context": {
            "docs": retriever,
            "count": lambda docs: len(docs)
        } | format_context
    }
    | prompt
    | model
)
```

### 4.4 用 itemgetter 提取字段

有时候输入已经是字典了，需要提取某个字段：

```python
from operator import itemgetter

# 输入是 {"question": "...", "language": "..."}
chain = (
    {
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question"),
        "language": itemgetter("language")
    }
    | prompt
    | model
)
```

> 💡 `itemgetter("key")` 的作用就是从字典中取出指定 key 的值，相当于 `lambda x: x["key"]`。

### 4.5 带历史对话的 RAG

```python
chain = (
    {
        "context": itemgetter("question") | retriever | format_docs,
        "history": itemgetter("history"),
        "question": itemgetter("question")
    }
    | prompt
    | model
)

# 调用时传字典
answer = chain.invoke({
    "question": "什么是向量数据库？",
    "history": [("你好", "你好！有什么可以帮你的？")]
})
```

---

## ⚠️ 五、注意事项

1. **字典中的 key 要和提示词变量对应**：字典的 key 必须和 PromptTemplate 中的变量名一致，否则会报错
2. **所有分支接收相同的输入**：字典形式的链中，每个 Runnable 接收的输入都是一样的
3. **并行执行**：多个分支是并行执行的，不是顺序执行
4. **普通函数会自动包装**：普通 Python 函数可以直接用 `|` 连接，LangChain 会自动转成 RunnableLambda
5. **RunnablePassthrough 不能省**：在字典分支中，如果某个分支需要直接透传输入，必须写 `RunnablePassthrough()`，不能空着不写
6. **函数只能接收一个参数**：放进链里的函数只能接收一个参数，如果需要多个参数，要传字典进去

---

## 📝 六、Runnable 家族成员

LangChain 中有很多 Runnable 的子类，各有各的用途：

| Runnable | 作用 | 说明 |
|---------|------|------|
| `RunnablePassthrough` | 透传 | 输入什么输出什么 |
| `RunnableLambda` | 函数包装 | 把普通函数转成 Runnable |
| `RunnableParallel` | 并行执行 | 就是字典形式的链 |
| `RunnableSequence` | 顺序执行 | 就是用 `|` 连接的链 |
| `RunnableBranch` | 条件分支 | 根据条件选择不同路径 |
| `RunnableWithFallbacks` | 降级备用 | 失败了用备用方案 |

> 💡 你写的 `{"a": run1, "b": run2}` 本质上就是 `RunnableParallel` 的简写。

---

## 🔍 七、完整示例

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatTongyi

model = ChatTongyi(model="qwen-plus")

# ========== 示例 1：RunnablePassthrough 基础用法 ==========
print("=== 示例 1：RunnablePassthrough 基础 ===")

passthrough = RunnablePassthrough()
result = passthrough.invoke("hello world")
print(f"输入: hello world")
print(f"输出: {result}")

# ========== 示例 2：字典并行执行 ==========
print("\n=== 示例 2：字典并行执行 ===")

# 定义几个简单的 Runnable
def add_one(x):
    return x + 1

def multiply_two(x):
    return x * 2

def to_string(x):
    return f"数字是{x}"

# 并行执行三个分支
chain = {
    "original": RunnablePassthrough(),
    "plus_one": RunnableLambda(add_one),
    "times_two": RunnableLambda(multiply_two),
    "string": RunnableLambda(to_string)
}

result = chain.invoke(5)
print(f"输入: 5")
print(f"输出: {result}")

# ========== 示例 3：RAG 链（标准写法） ==========
print("\n=== 示例 3：RAG 链 ===")

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import DashScopeEmbeddings

# 准备向量库
vector_store = InMemoryVectorStore(embedding=DashScopeEmbeddings())
vector_store.add_texts([
    "LangChain 是一个大模型应用开发框架",
    "RAG 是检索增强生成技术",
    "向量数据库用于存储和检索向量"
])

# 检索器
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# 格式化函数
def format_docs(docs):
    return "\n\n".join(f"- {doc.page_content}" for doc in docs)

# 提示词模板
prompt = ChatPromptTemplate.from_template("""
请根据以下参考资料回答问题。

参考资料：
{context}

问题：{question}

回答：
""")

# 构建 RAG 链
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | model
    | StrOutputParser()
)

# 测试
question = "什么是 RAG？"
answer = rag_chain.invoke(question)
print(f"问：{question}")
print(f"答：{answer}")

# ========== 示例 4：多输入 + itemgetter ==========
print("\n=== 示例 4：多输入 + itemgetter ===")

from operator import itemgetter

prompt2 = ChatPromptTemplate.from_template("""
请用{language}回答以下问题。

参考资料：
{context}

问题：{question}
""")

chain2 = (
    {
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question"),
        "language": itemgetter("language")
    }
    | prompt2
    | model
    | StrOutputParser()
)

result2 = chain2.invoke({
    "question": "什么是 LangChain？",
    "language": "英文"
})
print(f"问（英文）：What is LangChain?")
print(f"答：{result2}")
```

---

## 📊 八、LCEL 常用写法总结

| 写法 | 含义 | 示例 |
|-----|------|------|
| `a \| b` | 顺序执行，a 的输出给 b | `prompt \| model` |
| `{"k": runnable}` | 并行执行，结果合并成字典 | `{"q": itemgetter("q"), "c": retriever}` |
| `RunnablePassthrough()` | 透传输入 | `{"q": RunnablePassthrough()}` |
| `RunnableLambda(func)` | 函数转 Runnable | `RunnableLambda(format_docs)` |
| `itemgetter("key")` | 从字典取字段 | `itemgetter("question")` |
| `StrOutputParser()` | 提取字符串输出 | `model \| StrOutputParser()` |

---

## 🔗 九、知识串联

| 前面学过的 | 和 RunnablePassthrough 的关系 |
|-----------|-----------------------------|
| **Chain（第16篇）** | RunnablePassthrough 是 LCEL 链的组成部分 |
| **向量存储（第26篇）** | as_retriever() 把向量库转成 Runnable |
| **RAG（第27篇）** | RunnablePassthrough 是构建 RAG 链的关键 |
| **提示词模板** | 字典的 key 要和模板变量对应 |

> 💡 学会了 RunnablePassthrough 和字典形式的链，你就能构建各种复杂的多分支链了。

---

> 💡 **学习建议**：RunnablePassthrough 看起来简单，但它是构建复杂 LCEL 链的基础。建议把 RAG 链的标准写法记下来，这是最常用的模式。可以试着构建一些多分支的链，比如同时做翻译、摘要、分类，体会并行执行的效果。
