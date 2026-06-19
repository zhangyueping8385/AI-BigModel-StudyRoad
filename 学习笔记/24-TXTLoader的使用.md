# 24 - TXTLoader 的使用

> 学习使用 LangChain 的 TextLoader 加载文本文件，并使用文本分割器将长文本切分成小块

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 的 TextLoader** 加载纯文本文件，并使用 **RecursiveCharacterTextSplitter** 将长文本分割成多个小块，方便后续向量化和检索。

### 1.1 核心功能

- ✅ 使用 TextLoader 加载 TXT 文件
- ✅ 使用 RecursiveCharacterTextSplitter 分割文本
- ✅ 自定义分割大小、重叠字符、分隔符
- ✅ 将长文档切分成多个 Document 对象

---

## 🔧 二、核心代码解析

### 2.1 导入相关类

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

| 导入类 | 说明 |
|-------|------|
| `TextLoader` | 文本文件加载器 |
| `RecursiveCharacterTextSplitter` | 递归字符文本分割器 |

### 2.2 创建 TextLoader 并加载

```python
loader = TextLoader(
    file_path="./data/文件24data.txt",
    encoding="utf-8"
)
docs = loader.load()
```

**参数说明**：

| 参数 | 类型 | 说明 |
|-----|------|------|
| `file_path` | str | TXT 文件路径 |
| `encoding` | str | 文件编码，默认 None |

**加载结果**：
- 返回一个 Document 对象的列表
- 整个文件内容作为一个 Document 的 page_content
- 如果文件很大，这一个 Document 会非常长

### 2.3 创建文本分割器

```python
spliter = RecursiveCharacterTextSplitter(
    chunk_size=500,              # 每段的最大字符数
    chunk_overlap=50,            # 段与段之间的重叠字符数
    separators=["。", "？", "！", "；", "，", "：", "（", "）", "“", "”", "《", "》", "【", "】", "——", "…",".","?","!",";"],
    length_function=len          # 计算长度的函数
)
```

**参数详解**：

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `chunk_size` | int | 每个文本块的最大字符数 | 4000 |
| `chunk_overlap` | int | 相邻块之间的重叠字符数 | 200 |
| `separators` | list | 分隔符列表，按优先级排序 | `["\n\n", "\n", " ", ""]` |
| `length_function` | function | 计算文本长度的函数 | `len` |

### 2.4 分割文档

```python
split_docs = spliter.split_documents(docs)
```

**输入**：Document 列表（可能只有一个大文档）
**输出**：分割后的 Document 列表（多个小文档）

### 2.5 查看分割结果

```python
print(len(split_docs))  # 查看分割后的 Document 个数

for split_doc in split_docs:
    print("="*20)
    print(split_doc)
    print("="*20)
```

---

## 💡 三、关键知识点

### 3.1 为什么要分割文本？

大模型和向量数据库都有** token 限制**，太长的文本处理不了：

| 问题 | 说明 |
|-----|------|
| **Token 限制** | 大模型有上下文窗口限制，太长的文本塞不下 |
| **检索精度** | 整段文本向量化后，检索时不够精准 |
| **响应速度** | 文本太长，处理和生成都慢 |
| **成本问题** | Token 是计费的，太长会浪费 |

**解决方案**：把长文本切成小块（chunk），每块单独处理。

```
长文本（10000字）
    ↓ 分割
[块1（500字）] [块2（500字）] [块3（500字）] ...
    ↓ 向量化
[向量1] [向量2] [向量3] ...
    ↓ 检索
找到最相关的几块，拼起来给大模型
```

### 3.2 RecursiveCharacterTextSplitter 的工作原理

**递归字符分割**是最常用的分割方式，它会**按优先级依次尝试**不同的分隔符：

```
1. 先用第一个分隔符（如 "。"）尝试分割
2. 如果分割后还是太大，用下一个分隔符（如 "，"）
3. 继续递归，直到每块都小于 chunk_size
4. 保证尽量在语义完整的地方分割
```

**分隔符优先级**：
- 优先用句号、问号等句子结束符（保证语义完整）
- 不行再用逗号、分号等
- 最后实在不行就按字符硬切

> 💡 这样做的好处是：尽量在句子、段落边界分割，保持语义完整性，而不是把一句话从中间切断。

### 3.3 chunk_overlap（重叠）的作用

相邻的文本块之间保留一些重叠字符，避免上下文断裂：

```
块1：这是第一段话。内容很丰富，
块2：内容很丰富，涉及很多方面。
        ↑ 重叠部分（chunk_overlap）
```

**为什么需要重叠？**
- 防止关键信息被切断在两个块中间
- 保持上下文的连贯性
- 提高检索的准确率

> 💡 重叠大小一般设为 chunk_size 的 10%-20% 比较合适。

### 3.4 分割后的 Document

分割后的每个小块都是一个独立的 Document 对象：

```python
Document(
    page_content="这是第一块文本内容...",
    metadata={
        "source": "./data/文件24data.txt",
        "start_index": 0  # 起始位置（有些分割器会有）
    }
)
```

---

## 🎯 四、常见使用模式

### 4.1 基本用法

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 加载文本
loader = TextLoader("data.txt", encoding="utf-8")
docs = loader.load()

# 2. 分割文本
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
split_docs = splitter.split_documents(docs)

print(f"分割前：{len(docs)} 个文档")
print(f"分割后：{len(split_docs)} 个文档")
```

### 4.2 中文文本分割

中文没有空格分词，需要专门设置中文分隔符：

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=[
        "\n\n",  # 段落
        "\n",    # 换行
        "。",    # 句号
        "！",    # 感叹号
        "？",    # 问号
        "；",    # 分号
        "，",    # 逗号
        " ",     # 空格
        "",      # 字符（最后手段）
    ]
)
```

> 💡 分隔符的顺序很重要，排在前面的优先级高。

### 4.3 按 token 分割

有时候按字符数分割不够准确，可以按 token 数分割：

```python
import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")

def tiktoken_len(text):
    tokens = tokenizer.encode(text)
    return len(tokens)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # 现在是 token 数，不是字符数
    chunk_overlap=50,
    length_function=tiktoken_len  # 用 token 计数
)
```

> 💡 大模型的限制是按 token 算的，用 token 数分割更准确。

### 4.4 分割字符串

也可以直接分割字符串，不经过 Document：

```python
text = "很长的文本..."

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=10
)

chunks = splitter.split_text(text)
# 返回字符串列表
```

---

## ⚠️ 五、注意事项

1. **chunk_size 要合适**：太小会碎得太厉害，太大会放不下，一般 500-2000 字符比较常用
2. **chunk_overlap 不要太大**：重叠太大会导致冗余太多，一般是 chunk_size 的 10%-20%
3. **分隔符顺序很重要**：优先级高的分隔符放前面，尽量在语义完整的地方分割
4. **中文要单独设置分隔符**：默认分隔符主要是针对英文的，中文要自己加
5. **编码要正确**：TXT 文件编码多样（UTF-8、GBK 等），要设置对，否则会乱码
6. **分割后 metadata 会保留**：每个小块的 metadata 会继承原文档的 metadata

---

## 📝 六、其他文本分割器

### 6.1 CharacterTextSplitter

最简单的分割器，只按一个分隔符分割：

```python
from langchain_text_splitters import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator="\n\n",  # 只按空行分割
    chunk_size=500,
    chunk_overlap=50
)
```

> 💡 比较粗暴，不如递归分割好用。

### 6.2 TokenTextSplitter

按 token 数分割：

```python
from langchain_text_splitters import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

### 6.3 MarkdownTextSplitter

专门用于 Markdown 文档，按标题、段落等结构分割：

```python
from langchain_text_splitters import MarkdownTextSplitter

splitter = MarkdownTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

### 6.4 PythonCodeTextSplitter

专门用于 Python 代码，按函数、类等结构分割：

```python
from langchain_text_splitters import PythonCodeTextSplitter

splitter = PythonCodeTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

> 💡 不同类型的文本有专门的分割器，效果更好。

---

## 🔍 七、完整流程：加载 → 分割 → 向量化

TextLoader 和文本分割器通常配合向量数据库使用，这是 RAG 的标准流程：

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import TongyiEmbeddings

# 1. 加载文本
loader = TextLoader("article.txt", encoding="utf-8")
docs = loader.load()

# 2. 分割文本
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
)
split_docs = splitter.split_documents(docs)

# 3. 向量化并存入向量库
embeddings = TongyiEmbeddings()
db = FAISS.from_documents(split_docs, embeddings)

# 4. 相似度搜索
results = db.similarity_search("什么是LangChain？", k=3)

# 5. 把搜索结果拼给大模型
context = "\n\n".join([doc.page_content for doc in results])
prompt = f"根据以下内容回答问题：\n{context}\n\n问题：什么是LangChain？"
```

---

## 💡 八、完整示例模板

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 加载文本文件
print("=== 加载文本 ===")
loader = TextLoader(
    file_path="./data/sample.txt",
    encoding="utf-8"
)
docs = loader.load()
print(f"加载了 {len(docs)} 个文档")
print(f"总字符数：{len(docs[0].page_content)}")

# 2. 创建文本分割器
print("\n=== 创建分割器 ===")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,       # 每块最大 300 字符
    chunk_overlap=30,     # 重叠 30 字符
    separators=[           # 中文分隔符优先级
        "\n\n",
        "\n",
        "。",
        "！",
        "？",
        "；",
        "，",
        " ",
        ""
    ],
    length_function=len
)

# 3. 分割文档
print("\n=== 分割文档 ===")
split_docs = splitter.split_documents(docs)
print(f"分割成了 {len(split_docs)} 个小块")

# 4. 查看每块内容
print("\n=== 分割结果 ===")
for i, doc in enumerate(split_docs):
    print(f"\n--- 第 {i+1} 块（{len(doc.page_content)} 字）---")
    print(doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content)

# 5. 直接分割字符串
print("\n=== 直接分割字符串 ===")
text = "这是一段很长的文本..." * 10
chunks = splitter.split_text(text)
print(f"分割成 {len(chunks)} 块")
```

---

## 📊 九、TextLoader + 文本分割 总结

| 组件 | 作用 | 关键参数 |
|-----|------|---------|
| `TextLoader` | 加载 TXT 文件 | file_path, encoding |
| `RecursiveCharacterTextSplitter` | 递归分割文本 | chunk_size, chunk_overlap, separators |

**典型应用流程**：

```
TXT 文件 → TextLoader → Document（大）
                           ↓
              RecursiveCharacterTextSplitter
                           ↓
                    Document 列表（小）
                           ↓
                    Embeddings 向量化
                           ↓
                    存入向量数据库
                           ↓
                    相似度检索 + LLM
```

---

> 💡 **学习建议**：文本加载和分割是 RAG（检索增强生成）的第一步，也是非常重要的一步。分割的质量直接影响后续的检索效果。建议多试试不同的 chunk_size 和分隔符，找到最适合自己数据的参数。配合向量数据库一起学习，能体会完整的应用流程。
