# 25 - PDFLoader 的使用

> 学习使用 LangChain 的 PyPDFLoader 加载 PDF 文件，按页或整体生成 Document 对象

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 的 PyPDFLoader** 加载 PDF 文件的方法，支持按页分割和整体加载两种模式，将 PDF 内容转换为 Document 对象。

### 1.1 核心功能

- ✅ 使用 PyPDFLoader 加载 PDF 文件
- ✅ `page` 模式：每页生成一个 Document
- ✅ `single` 模式：所有页生成一个 Document
- ✅ 自动提取 PDF 文本内容

---

## 🔧 二、核心代码解析

### 2.1 导入 PyPDFLoader

```python
from langchain_community.document_loaders import PyPDFLoader
```

从 `langchain_community.document_loaders` 模块导入 PyPDFLoader。

> 💡 PyPDFLoader 基于 PyPDF2 或 pypdf 库实现，用于解析 PDF 文件并提取文本。

### 2.2 创建 PyPDFLoader 实例

```python
loader = PyPDFLoader(
    file_path="./data/Zookeeper篇.pdf",
    mode="page"  # 默认 page，每个页面生成一个 Document 对象
                 # single 将所有页面生成一个 Document 对象
)
```

**参数说明**：

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `file_path` | str | PDF 文件路径 | 必填 |
| `mode` | str | 加载模式：`"page"` 或 `"single"` | `"page"` |

**两种模式对比**：

| 模式 | 说明 | Document 数量 |
|-----|------|--------------|
| `page` | 每页一个 Document | 等于 PDF 页数 |
| `single` | 所有页合并成一个 Document | 1个 |

### 2.3 加载 PDF

```python
docs = loader.load()
```

调用 `load()` 方法加载 PDF，返回 Document 对象列表。

### 2.4 查看加载结果

```python
print(len(docs))  # 查看 Document 个数

for doc in docs:
    print(doc)
```

---

## 💡 三、关键知识点

### 3.1 Document 对象结构

**page 模式下**，每个 Document 对应 PDF 的一页：

```python
Document(
    page_content="这是第1页的内容...",
    metadata={
        "source": "./data/Zookeeper篇.pdf",
        "page": 0  # 页码，从0开始
    }
)
```

**single 模式下**，所有页合并成一个 Document：

```python
Document(
    page_content="第1页内容\n\n第2页内容\n\n第3页内容...",
    metadata={
        "source": "./data/Zookeeper篇.pdf",
        "total_pages": 10  # 总页数
    }
)
```

**metadata 常用字段**：

| 字段 | 说明 |
|-----|------|
| `source` | PDF 文件路径 |
| `page` | 当前页码（page模式，从0开始） |
| `total_pages` | 总页数（single模式） |

### 3.2 什么时候用 page 模式？

- 想按页处理或检索
- 需要知道内容来自哪一页
- PDF 内容较多，需要分割后向量化
- 做 RAG 时，希望检索粒度更细

**典型场景**：
```
PDF（100页）
    ↓ page 模式
[页1] [页2] [页3] ... [页100]
    ↓ 向量化
存入向量库，检索时返回相关的页
```

### 3.3 什么时候用 single 模式？

- PDF 内容较少，想整体处理
- 不需要知道具体页码
- 想保留完整上下文

**典型场景**：
```
PDF（3页）
    ↓ single 模式
[完整文档]
    ↓ 直接传给大模型
一次性处理整个文档
```

> 💡 大多数 RAG 场景用 page 模式更合适，因为检索粒度更细。

### 3.4 PDF 文本提取的局限性

PyPDFLoader 只能提取**文本层**的内容，有以下限制：

| 内容类型 | 能否提取 | 说明 |
|---------|---------|------|
| 普通文本 | ✅ 可以 | 正常提取 |
| 图片中的文字 | ❌ 不行 | 需要 OCR |
| 扫描版 PDF | ❌ 不行 | 本质是图片 |
| 表格 | ⚠️ 部分 | 可能格式混乱 |
| 公式 | ⚠️ 部分 | 可能提取不完整 |
| 排版格式 | ❌ 不行 | 只能提取纯文本 |

> 💡 如果是扫描版 PDF（图片 PDF），需要用 OCR 工具先识别文字，再用 LangChain 处理。

---

## 🎯 四、常见使用模式

### 4.1 按页加载（默认）

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("document.pdf")
docs = loader.load()

print(f"PDF 共 {len(docs)} 页")
print(f"第1页内容：\n{docs[0].page_content[:200]}...")
```

### 4.2 整体加载

```python
loader = PyPDFLoader(
    file_path="document.pdf",
    mode="single"
)
docs = loader.load()

print(f"共 {len(docs)} 个文档")
print(f"总字数：{len(docs[0].page_content)}")
```

### 4.3 加载后再分割

通常 PDF 一页内容还是太长，加载后还需要用文本分割器再切分：

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 加载 PDF（按页）
loader = PyPDFLoader("document.pdf")
docs = loader.load()

# 2. 进一步分割成更小的块
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
split_docs = splitter.split_documents(docs)

print(f"原始页数：{len(docs)}")
print(f"分割后块数：{len(split_docs)}")
```

### 4.4 提取特定页

```python
loader = PyPDFLoader("document.pdf")
docs = loader.load()

# 只取前 5 页
first_5_pages = docs[:5]

# 只取第 10 页（注意从0开始）
page_10 = docs[9]

# 取指定范围的页
pages_5_to_10 = docs[4:10]
```

### 4.5 加载多个 PDF

```python
from langchain_community.document_loaders import DirectoryLoader

# 加载目录下所有 PDF
loader = DirectoryLoader(
    path="./pdfs/",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader
)
docs = loader.load()
```

---

## ⚠️ 五、注意事项

1. **页码从 0 开始**：metadata 中的 page 字段从 0 开始计数，不是从 1 开始
2. **扫描版 PDF 不行**：PyPDFLoader 只能提取文本，扫描版（图片）PDF 需要 OCR
3. **格式会丢失**：提取的是纯文本，排版、字体、颜色等格式信息都会丢失
4. **表格可能乱**：PDF 中的表格提取后可能格式混乱，需要额外处理
5. **加密 PDF 打不开**：加密的 PDF 需要先解密才能加载
6. **大文件用懒加载**：超大 PDF 可以用 lazy_load() 逐页加载，节省内存

---

## 📝 六、其他 PDF 加载器

LangChain 有多种 PDF 加载器，各有特点：

| 加载器 | 特点 | 适用场景 |
|-------|------|---------|
| `PyPDFLoader` | 轻量、快速、基于 pypdf | 普通文本 PDF |
| `PDFMinerLoader` | 提取更准确，支持布局 | 需要保留布局信息 |
| `PyMuPDFLoader` | 速度快，支持图片提取 | 高性能需求 |
| `UnstructuredPDFLoader` | 功能强大，支持多种元素 | 复杂 PDF 结构 |
| `MathpixPDFLoader` | 支持公式识别 | 学术论文、数学公式 |
| `AmazonTextractPDFLoader` | AWS OCR 服务 | 扫描版 PDF |

> 💡 简单场景用 PyPDFLoader 就够了，复杂场景再考虑其他加载器。

---

## 🔍 七、完整 RAG 流程示例

PyPDFLoader 常用于构建知识库，配合向量数据库做 RAG：

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import TongyiEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 1. 加载 PDF
print("=== 1. 加载 PDF ===")
loader = PyPDFLoader("./data/Zookeeper篇.pdf")
docs = loader.load()
print(f"加载了 {len(docs)} 页")

# 2. 文本分割
print("\n=== 2. 文本分割 ===")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
split_docs = splitter.split_documents(docs)
print(f"分割成 {len(split_docs)} 个块")

# 3. 向量化并存入向量库
print("\n=== 3. 构建向量库 ===")
embeddings = TongyiEmbeddings()
db = FAISS.from_documents(split_docs, embeddings)
print("向量库构建完成")

# 4. 创建检索器
retriever = db.as_retriever(search_kwargs={"k": 3})

# 5. 构建 RAG 链
print("\n=== 4. 构建 RAG 链 ===")
prompt = ChatPromptTemplate.from_template("""
请根据以下上下文回答问题。如果上下文中没有答案，请说"我不知道"。

上下文：{context}

问题：{question}
""")

model = ChatTongyi(model="qwen-plus")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
)

# 6. 提问
print("\n=== 5. 提问 ===")
question = "Zookeeper 是什么？"
result = rag_chain.invoke(question)
print(f"问：{question}")
print(f"答：{result.content}")
```

---

## 💡 八、完整示例模板

```python
from langchain_community.document_loaders import PyPDFLoader

# ========== 示例 1：page 模式（默认） ==========
print("=== page 模式 ===")

loader_page = PyPDFLoader(
    file_path="./data/sample.pdf",
    mode="page"
)
docs_page = loader_page.load()

print(f"共 {len(docs_page)} 页")
print(f"\n第 1 页内容（前200字）：")
print(docs_page[0].page_content[:200] + "...")
print(f"\n第 1 页元数据：{docs_page[0].metadata}")

# ========== 示例 2：single 模式 ==========
print("\n=== single 模式 ===")

loader_single = PyPDFLoader(
    file_path="./data/sample.pdf",
    mode="single"
)
docs_single = loader_single.load()

print(f"共 {len(docs_single)} 个文档")
print(f"总字数：{len(docs_single[0].page_content)}")
print(f"元数据：{docs_single[0].metadata}")

# ========== 示例 3：懒加载（大文件） ==========
print("\n=== 懒加载 ===")

loader_lazy = PyPDFLoader("./data/large.pdf")
count = 0
for doc in loader_lazy.lazy_load():
    count += 1
    if count <= 3:  # 只打印前3页
        print(f"\n第 {count} 页：{doc.page_content[:50]}...")
print(f"\n总共 {count} 页")

# ========== 示例 4：结合文本分割器 ==========
print("\n=== 结合文本分割器 ===")

from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyPDFLoader("./data/sample.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=30
)
split_docs = splitter.split_documents(docs)

print(f"原始页数：{len(docs)}")
print(f"分割后块数：{len(split_docs)}")
print(f"\n第 1 块内容：")
print(split_docs[0].page_content)
```

---

## 📊 九、PDFLoader 使用场景

| 场景 | 说明 |
|-----|------|
| **知识库构建** | 把 PDF 文档加载到向量库，做 RAG 问答 |
| **文档摘要** | 加载 PDF 后让大模型生成摘要 |
| **信息抽取** | 从 PDF 中提取指定信息（如表格、关键字段） |
| **文档问答** | 基于 PDF 内容进行问答 |
| **批量处理** | 批量处理多个 PDF 文档 |

---

## 🔗 十、三种 Loader 对比总结

| 加载器 | 文件格式 | 特点 | 典型应用 |
|-------|---------|------|---------|
| `CSVLoader` | CSV | 表格数据，每行一个 Document | 产品数据、FAQ |
| `JSONLoader` | JSON | 结构化数据，jq_schema 提取 | API 数据、配置文件 |
| `TextLoader` | TXT | 纯文本，需配合分割器 | 文章、日志 |
| `PyPDFLoader` | PDF | 按页加载，支持两种模式 | 论文、文档、书籍 |

> 💡 这四种 Loader 都是 Document Loader 家族的成员，接口统一（load/lazy_load），学会一个就能举一反三。

---

> 💡 **学习建议**：PyPDFLoader 是最常用的 PDF 加载器，简单易用。但要注意它只能提取文本层的内容，扫描版 PDF 需要用 OCR。建议把 PDFLoader 和文本分割器、向量数据库结合起来学习，完整走一遍 RAG 流程，体会每个环节的作用。
