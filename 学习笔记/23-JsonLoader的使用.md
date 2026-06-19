# 23 - JSONLoader 的使用

> 学习使用 LangChain 的 JSONLoader 加载 JSON 文件，通过 jq_schema 提取指定字段内容

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 的 JSONLoader** 加载 JSON 文件的方法，支持普通 JSON 和 JSON Lines 两种格式，通过 jq_schema 灵活提取需要的字段。

### 1.1 核心功能

- ✅ 使用 JSONLoader 加载 JSON 文件
- ✅ 通过 jq_schema 提取指定字段
- ✅ 支持普通 JSON 格式
- ✅ 支持 JSON Lines 格式（每行一个 JSON 对象）

---

## 🔧 二、核心代码解析

### 2.1 导入 JSONLoader

```python
from langchain_community.document_loaders import JSONLoader
```

从 `langchain_community.document_loaders` 模块导入 JSONLoader。

### 2.2 加载普通 JSON 文件

#### 示例 JSON 文件（stus.json）

```json
{
  "name": "周杰轮",
  "age": 11,
  "hobby": [
    "唱",
    "跳",
    "RAP"
  ],
  "other": {
    "addr": "深圳",
    "tel": "12332112321"
  }
}
```

#### 加载代码

```python
loader = JSONLoader(
    file_path="./data/stus.json",
    jq_schema='.other.addr'  # 获取到深圳
)
document = loader.load()
print(document)
```

**参数说明**：

| 参数 | 类型 | 说明 |
|-----|------|------|
| `file_path` | str | JSON 文件路径 |
| `jq_schema` | str | jq 表达式，用于提取指定字段 |

**jq_schema 语法**：
- `.` 表示根对象
- `.字段名` 表示取某个字段
- 支持嵌套：`.other.addr` 表示取 other 对象下的 addr 字段

**提取结果**：
- `jq_schema='.other.addr'` → 提取到 `"深圳"`
- `jq_schema='.name'` → 提取到 `"周杰轮"`
- `jq_schema='.hobby'` → 提取到 `["唱", "跳", "RAP"]`

### 2.3 加载 JSON Lines 文件

#### 示例 JSON Lines 文件（stu_json_lines.json）

```json
{"name":"周杰轮","age":11,"gender":"男"}
{"name":"蔡依临","age": 12,"gender":"女"}
{"name":"王力鸿","age":11,"gender":"男"}
```

> 💡 JSON Lines 格式：每行是一个独立的 JSON 对象，也叫 NDJSON（Newline Delimited JSON）。

#### 加载代码

```python
loader_jsonline = JSONLoader(
    file_path="./data/stu_json_lines.json",
    jq_schema=".name",
    text_content=False,
    json_lines=True
)
document_jsonline = loader_jsonline.load()
print(document_jsonline)
```

**新增参数**：

| 参数 | 类型 | 说明 |
|-----|------|------|
| `json_lines` | bool | 是否为 JSON Lines 格式，默认 False |
| `text_content` | bool | 是否将提取结果视为纯文本，默认 True |

**text_content 的作用**：
- `True`（默认）：提取的内容会被当作纯文本，直接作为 page_content
- `False`：提取的内容会被序列化为 JSON 字符串，适合提取对象或数组时使用

---

## 💡 三、关键知识点

### 3.1 jq_schema 是什么？

**jq** 是一个轻量级的命令行 JSON 处理工具，`jq_schema` 就是使用 jq 的语法来从 JSON 中提取数据。

**常用 jq 语法**：

| 表达式 | 含义 | 示例结果 |
|-------|------|---------|
| `.` | 整个对象 | `{...}` |
| `.name` | 取 name 字段 | `"张三"` |
| `.other.addr` | 嵌套取字段 | `"深圳"` |
| `.hobby[]` | 遍历数组 | 每个元素单独输出 |
| `.hobby[0]` | 取数组第一个元素 | `"唱"` |
| `.name, .age` | 取多个字段 | `"张三"` 和 `20` |
| `{name: .name, age: .age}` | 构造新对象 | `{"name": "张三", "age": 20}` |

### 3.2 普通 JSON vs JSON Lines

| 对比项 | 普通 JSON | JSON Lines |
|-------|----------|-----------|
| **格式** | 一个完整的 JSON 对象/数组 | 每行一个 JSON 对象 |
| **文件扩展名** | `.json` | `.jsonl` 或 `.json` |
| **加载方式** | 一次性加载整个文件 | 逐行加载 |
| **适用场景** | 配置文件、小数据 | 日志、大数据集 |
| **内存占用** | 大（全部加载） | 小（逐行处理） |

**普通 JSON 示例**：
```json
[
  {"name": "张三", "age": 20},
  {"name": "李四", "age": 25}
]
```

**JSON Lines 示例**：
```json
{"name": "张三", "age": 20}
{"name": "李四", "age": 25}
```

### 3.3 Document 对象结构

JSONLoader 加载后返回 Document 对象：

```python
Document(
    page_content="深圳",  # jq_schema 提取的内容
    metadata={
        "source": "./data/stus.json",
        "seq_num": 1
    }
)
```

- `page_content`：jq_schema 提取到的内容
- `metadata`：元数据，包含文件路径和序号

---

## 🎯 四、常见使用模式

### 4.1 提取单个字段

```python
# 提取 name 字段
loader = JSONLoader(
    file_path="data.json",
    jq_schema=".name"
)
docs = loader.load()
# page_content 就是 name 的值
```

### 4.2 提取嵌套字段

```python
# 提取嵌套的 addr 字段
loader = JSONLoader(
    file_path="data.json",
    jq_schema=".contact.address"
)
```

### 4.3 提取数组中的每个元素

```python
# JSON 内容：{"items": ["a", "b", "c"]}
loader = JSONLoader(
    file_path="data.json",
    jq_schema=".items[]"  # [] 表示遍历数组
)
docs = loader.load()
# 会生成 3 个 Document，分别对应 "a"、"b"、"c"
```

### 4.4 提取数组中对象的某个字段

```python
# JSON 内容：{"users": [{"name": "张三"}, {"name": "李四"}]}
loader = JSONLoader(
    file_path="data.json",
    jq_schema=".users[].name"
)
docs = loader.load()
# 生成 2 个 Document，分别是 "张三" 和 "李四"
```

### 4.5 加载 JSON Lines 文件

```python
loader = JSONLoader(
    file_path="data.jsonl",
    jq_schema=".content",
    json_lines=True
)
docs = loader.load()
# 每行生成一个 Document
```

### 4.6 提取整个对象（text_content=False）

```python
# 提取整个对象，保持 JSON 格式
loader = JSONLoader(
    file_path="data.json",
    jq_schema=".",
    text_content=False  # 序列化为 JSON 字符串
)
docs = loader.load()
# page_content 是完整的 JSON 字符串
```

---

## ⚠️ 五、注意事项

1. **jq_schema 语法要正确**：jq 语法写错会导致提取失败，建议先测试 jq 表达式
2. **json_lines 参数要匹配**：JSON Lines 格式必须设置 `json_lines=True`，否则会报错
3. **编码问题**：如果文件是 GBK 编码，可能需要转码，JSONLoader 默认按 UTF-8 读取
4. **提取数组时用 []**：要遍历数组生成多个 Document，jq_schema 末尾要加 `[]`
5. **text_content 的选择**：提取的是字符串用 True，提取的是对象或数组用 False
6. **大文件用 JSON Lines**：数据量大时建议用 JSON Lines 格式，更省内存

---

## 📝 六、进阶用法

### 6.1 复杂的 jq 表达式

```python
# 提取多个字段并组合
loader = JSONLoader(
    file_path="data.json",
    jq_schema='"姓名：\(.name)\n年龄：\(.age)"'  # 字符串插值
)
```

### 6.2 条件过滤

```python
# 只提取 age > 18 的用户的 name
loader = JSONLoader(
    file_path="data.jsonl",
    jq_schema='select(.age > 18) | .name',
    json_lines=True
)
```

### 6.3 自定义 metadata

```python
docs = loader.load()
for i, doc in enumerate(docs):
    doc.metadata["id"] = i
    doc.metadata["type"] = "json"
```

### 6.4 结合 jq 工具

可以先在命令行用 jq 工具测试表达式，确认正确后再写到代码里：

```bash
# 命令行测试 jq 表达式
cat data.json | jq '.other.addr'
```

### 6.5 加载多个 JSON 文件

```python
from langchain_community.document_loaders import DirectoryLoader

loader = DirectoryLoader(
    path="./data/",
    glob="**/*.json",
    loader_cls=JSONLoader,
    loader_kwargs={"jq_schema": ".content"}
)
docs = loader.load()
```

---

## 🔍 七、JSONLoader vs CSVLoader

| 对比项 | JSONLoader | CSVLoader |
|-------|-----------|-----------|
| **数据格式** | JSON（结构化） | CSV（表格） |
| **嵌套支持** | 支持嵌套对象和数组 | 不支持嵌套 |
| **提取方式** | jq_schema（灵活） | 按列提取 |
| **适用场景** | API数据、配置文件 | 表格数据、导出数据 |
| **复杂度** | 稍高（需要学jq） | 简单 |

> 💡 简单表格用 CSVLoader，复杂嵌套结构用 JSONLoader。

---

## 💡 八、完整示例模板

```python
from langchain_community.document_loaders import JSONLoader

# ========== 示例 1：普通 JSON 文件 ==========
print("=== 普通 JSON 文件 ===")

# 假设有一个 data.json 文件：
# {
#   "name": "张三",
#   "age": 25,
#   "address": {
#       "city": "北京",
#       "street": "长安街"
#   },
#   "hobbies": ["读书", "游泳", "编程"]
# }

# 提取单个字段
loader1 = JSONLoader(
    file_path="./data/data.json",
    jq_schema=".name"
)
docs = loader1.load()
print(f"提取 name：{docs[0].page_content}")

# 提取嵌套字段
loader2 = JSONLoader(
    file_path="./data/data.json",
    jq_schema=".address.city"
)
docs = loader2.load()
print(f"提取 city：{docs[0].page_content}")

# 提取数组（每个元素一个 Document）
loader3 = JSONLoader(
    file_path="./data/data.json",
    jq_schema=".hobbies[]"
)
docs = loader3.load()
print(f"提取 hobbies，共 {len(docs)} 个：")
for doc in docs:
    print(f"  - {doc.page_content}")

# ========== 示例 2：JSON Lines 文件 ==========
print("\n=== JSON Lines 文件 ===")

# 假设有一个 data.jsonl 文件：
# {"id": 1, "title": "文章1", "content": "内容1"}
# {"id": 2, "title": "文章2", "content": "内容2"}

loader4 = JSONLoader(
    file_path="./data/data.jsonl",
    jq_schema=".title",
    json_lines=True
)
docs = loader4.load()
print(f"提取所有 title，共 {len(docs)} 个：")
for doc in docs:
    print(f"  - {doc.page_content}")

# ========== 示例 3：提取整个对象 ==========
print("\n=== 提取整个对象 ===")

loader5 = JSONLoader(
    file_path="./data/data.json",
    jq_schema=".",
    text_content=False  # 保持 JSON 格式
)
docs = loader5.load()
print(f"完整 JSON：{docs[0].page_content[:100]}...")
```

---

## 📊 九、JSONLoader 使用场景

| 场景 | 说明 |
|-----|------|
| **API 数据处理** | 加载 API 返回的 JSON 数据 |
| **配置文件加载** | 加载 JSON 格式的配置文件 |
| **日志分析** | 加载 JSON 格式的日志文件（JSON Lines） |
| **知识库构建** | 把 JSON 格式的文档加载到向量库 |
| **数据转换** | 把 JSON 数据转换成 Document 供 LangChain 使用 |

---

> 💡 **学习建议**：JSONLoader 的核心是 jq_schema，掌握 jq 语法是关键。建议先学几个常用的 jq 表达式，能应对大部分场景。如果 JSON 结构很复杂，可以先用 jq 命令行工具调试好表达式，再写到代码里。JSON Lines 格式在大数据场景下非常有用，值得了解一下。
