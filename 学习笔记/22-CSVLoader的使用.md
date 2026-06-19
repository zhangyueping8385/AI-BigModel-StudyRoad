# 22 - CSVLoader 的使用

> 学习使用 LangChain 的 CSVLoader 加载 CSV 文件，将表格数据转换为 Document 对象

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 的 CSVLoader** 加载 CSV 文件的方法，支持批量加载和懒加载两种方式，将 CSV 中的每一行数据转换为一个 Document 对象。

### 1.1 核心功能

- ✅ 使用 CSVLoader 加载 CSV 文件
- ✅ 自定义分隔符和引号字符
- ✅ 批量加载（load）
- ✅ 懒加载（lazy_load）

---

## 🔧 二、核心代码解析

### 2.1 导入 CSVLoader

```python
from langchain_community.document_loaders import CSVLoader
```

从 `langchain_community.document_loaders` 模块导入 CSVLoader。

> 💡 LangChain 有很多种 Document Loader，用于加载不同格式的文件（PDF、Word、CSV、JSON 等），CSVLoader 是其中之一。

### 2.2 创建 CSVLoader 实例

```python
loader = CSVLoader(
    file_path="./data/stu.csv",      # CSV 文件路径
    csv_args={
        "delimiter": ",",            # 分隔符，默认是逗号
        "quotechar": '"',            # 引号字符，用于包围包含分隔符的文本
    },
    encoding="utf-8"                 # 文件编码
)
```

**参数说明**：

| 参数 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| `file_path` | str | CSV 文件的路径 | 必填 |
| `csv_args` | dict | 传递给 Python csv 模块的参数 | `{}` |
| `encoding` | str | 文件编码格式 | `None`（使用系统默认） |

**csv_args 常用参数**：

| 参数 | 说明 | 示例 |
|-----|------|------|
| `delimiter` | 字段分隔符 | `","`、`";"`、`"\t"` |
| `quotechar` | 引用字符 | `'"'`、`"'"` |
| `escapechar` | 转义字符 | `"\\"` |
| `lineterminator` | 行终止符 | `"\n"` |

### 2.3 批量加载（load）

```python
documents = loader.load()
for document in documents:
    print(document)
```

**特点**：
- 一次性加载所有数据到内存
- 返回一个 Document 对象的列表
- 适合小文件

**返回值**：`List[Document]`，每个 Document 代表 CSV 中的一行。

### 2.4 懒加载（lazy_load）

```python
for document in loader.lazy_load():
    print(document)
```

**特点**：
- 逐行加载，每次只加载一行到内存
- 返回一个迭代器（generator）
- 适合大文件，节省内存

> 💡 懒加载就像"随用随取"，而批量加载是"一次性全拿过来"。大文件用懒加载更省内存。

---

## 💡 三、关键知识点

### 3.1 Document 对象

CSVLoader 加载后，每一行数据会变成一个 Document 对象：

```python
Document(
    page_content="列名1: 值1\n列名2: 值2\n列名3: 值3",  # 文本内容
    metadata={"source": "./data/stu.csv", "row": 0}      # 元数据
)
```

**Document 的两个核心属性**：

| 属性 | 类型 | 说明 |
|-----|------|------|
| `page_content` | str | 文档的文本内容 |
| `metadata` | dict | 文档的元数据（来源、行号等） |

**CSV 行如何转成 page_content**：

假设 CSV 内容是：
```csv
name,age,city
张三,20,北京
李四,25,上海
```

加载后第一行的 page_content 是：
```
name: 张三
age: 20
city: 北京
```

> 💡 每一行会被格式化成"列名: 值"的形式，每行一个键值对。

### 3.2 批量加载 vs 懒加载

| 对比项 | load（批量） | lazy_load（懒加载） |
|-------|-------------|-------------------|
| **返回类型** | 列表（List） | 迭代器（Generator） |
| **内存占用** | 一次性全部加载 | 逐行加载，占用少 |
| **访问速度** | 快（已在内存） | 稍慢（需要逐行读取） |
| **可重复遍历** | 可以多次遍历 | 只能遍历一次 |
| **适用场景** | 小文件、需要随机访问 | 大文件、流式处理 |

**代码对比**：

```python
# 批量加载
docs = loader.load()  # 全部加载完
print(len(docs))      # 可以知道总数
print(docs[0])        # 可以随机访问

# 懒加载
docs = loader.lazy_load()  # 返回迭代器
for doc in docs:           # 只能顺序遍历
    print(doc)
```

### 3.3 CSV 文件格式

CSV（Comma-Separated Values）是一种常见的表格数据格式：

```csv
姓名,年龄,城市
张三,20,北京
李四,25,上海
"王,五",30,"广州,深圳"
```

**注意点**：
- 第一行通常是表头（列名）
- 字段之间用分隔符隔开（默认逗号）
- 如果字段内容包含分隔符，需要用引号包围

---

## 🎯 四、常见使用模式

### 4.1 基本加载

```python
from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(file_path="data.csv")
documents = loader.load()

print(f"共加载了 {len(documents)} 条数据")
print(f"第一条内容：\n{documents[0].page_content}")
```

### 4.2 加载 TSV 文件（制表符分隔）

```python
loader = CSVLoader(
    file_path="data.tsv",
    csv_args={"delimiter": "\t"}
)
```

### 4.3 加载分号分隔的 CSV

```python
loader = CSVLoader(
    file_path="data.csv",
    csv_args={"delimiter": ";"}
)
```

### 4.4 懒加载处理大文件

```python
# 逐行处理，不占太多内存
count = 0
for doc in loader.lazy_load():
    # 处理每一行
    process(doc)
    count += 1
    if count % 1000 == 0:
        print(f"已处理 {count} 行")
```

### 4.5 提取特定列

```python
# 只提取 name 和 age 列
for doc in loader.lazy_load():
    content = doc.page_content
    # 解析内容，提取需要的字段
    lines = content.split("\n")
    data = {}
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            data[key] = value
    print(f"姓名：{data.get('name')}, 年龄：{data.get('age')}")
```

---

## ⚠️ 五、注意事项

1. **文件路径要正确**：确保 file_path 指向的文件存在，相对路径是相对于当前工作目录
2. **编码要匹配**：如果 CSV 文件是 GBK 编码，要设置 `encoding="gbk"`，否则会乱码
3. **表头问题**：CSVLoader 默认第一行是表头，如果没有表头，需要特殊处理
4. **空行处理**：CSV 中的空行会被忽略或产生空 Document
5. **大文件用懒加载**：文件很大时一定要用 lazy_load，不然会占满内存
6. **分隔符要正确**：如果分隔符设置错了，会导致数据解析混乱

---

## 📝 六、进阶用法

### 6.1 指定列作为 page_content

默认情况下，所有列都会拼接到 page_content 中。可以指定只使用某一列：

```python
loader = CSVLoader(
    file_path="data.csv",
    source_column="description"  # 用 description 列作为内容
)
```

> 💡 这样 page_content 就只包含 description 列的内容，其他列会放到 metadata 里。

### 6.2 自定义 metadata

可以通过继承或包装的方式，给 Document 添加自定义元数据：

```python
documents = loader.load()
for i, doc in enumerate(documents):
    doc.metadata["index"] = i
    doc.metadata["source_type"] = "csv"
```

### 6.3 结合向量数据库

CSVLoader 常和向量数据库配合使用，做 RAG（检索增强生成）：

```python
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import TongyiEmbeddings

# 1. 加载 CSV 数据
loader = CSVLoader(file_path="products.csv")
documents = loader.load()

# 2. 创建向量数据库
embeddings = TongyiEmbeddings()
db = FAISS.from_documents(documents, embeddings)

# 3. 相似度搜索
results = db.similarity_search("性价比高的手机")
```

### 6.4 加载多个 CSV 文件

```python
from langchain_community.document_loaders import DirectoryLoader

# 加载目录下所有 CSV 文件
loader = DirectoryLoader(
    path="./data/",
    glob="**/*.csv",
    loader_cls=CSVLoader
)
documents = loader.load()
```

---

## 🔍 七、Document Loader 家族

LangChain 支持很多种文件加载器：

| 加载器 | 用途 |
|-------|------|
| `CSVLoader` | 加载 CSV 文件 |
| `TextLoader` | 加载纯文本文件 |
| `PyPDFLoader` | 加载 PDF 文件 |
| `Docx2txtLoader` | 加载 Word 文档 |
| `JSONLoader` | 加载 JSON 文件 |
| `UnstructuredHTMLLoader` | 加载 HTML 文件 |
| `MarkdownLoader` | 加载 Markdown 文件 |
| `DirectoryLoader` | 加载整个目录的文件 |

> 💡 所有 Loader 的用法都差不多：创建 loader → 调用 load() 或 lazy_load() → 得到 Document 列表。

---

## 💡 八、完整示例模板

```python
from langchain_community.document_loaders import CSVLoader

# 1. 创建加载器
loader = CSVLoader(
    file_path="./data/students.csv",
    csv_args={
        "delimiter": ",",
        "quotechar": '"',
    },
    encoding="utf-8"
)

# 2. 批量加载（小文件）
print("=== 批量加载 ===")
documents = loader.load()
print(f"共加载 {len(documents)} 条记录")
print(f"\n第一条记录：")
print(documents[0].page_content)
print(f"\n元数据：{documents[0].metadata}")

# 3. 懒加载（大文件）
print("\n=== 懒加载 ===")
count = 0
for doc in loader.lazy_load():
    count += 1
    if count <= 3:  # 只打印前3条
        print(f"\n第 {count} 条：")
        print(doc.page_content[:50] + "...")
print(f"\n总共 {count} 条记录")

# 4. 解析数据
print("\n=== 解析数据 ===")
for doc in documents[:2]:
    lines = doc.page_content.split("\n")
    data = {}
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            data[key] = value
    print(f"姓名：{data.get('name')}, 年龄：{data.get('age')}")
```

---

## 📊 九、CSVLoader 使用场景

| 场景 | 说明 |
|-----|------|
| **知识库构建** | 把产品信息、FAQ 等 CSV 数据加载到向量库做 RAG |
| **数据分析** | 加载 CSV 数据，用大模型进行分析和问答 |
| **数据迁移** | 把 CSV 数据转换成 Document 格式，供其他 LangChain 组件使用 |
| **批量处理** | 对 CSV 中的每一行数据调用大模型处理 |

---

> 💡 **学习建议**：CSVLoader 是 LangChain 文档加载器中最简单的一个，也是最常用的之一。掌握它的用法后，学习其他加载器（如 PDFLoader、DocxLoader）就会很容易，因为接口都是统一的。建议配合向量数据库和 RAG 一起学习，体会完整的应用流程。
