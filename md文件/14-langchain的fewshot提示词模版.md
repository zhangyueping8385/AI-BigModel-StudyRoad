# 14 - LangChain 的 FewShot 提示词模版

> 学习使用 FewShotPromptTemplate 创建带示例的提示词模板，提升任务效果

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 的 FewShotPromptTemplate** 创建包含示例的提示词模板，通过 Few-Shot 学习让模型更好地理解任务要求。

### 1.1 核心功能

- ✅ 使用 FewShotPromptTemplate 创建带示例的模板
- ✅ 动态注入示例数据
- ✅ 分离示例模板和整体模板
- ✅ 支持 prefix、examples、suffix 三部分

---

## 🔧 二、核心代码解析

### 2.1 导入相关类

```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.llms.tongyi import Tongyi
```

| 导入类 | 说明 |
|-------|------|
| `FewShotPromptTemplate` | 带示例的提示词模板 |
| `PromptTemplate` | 基础提示词模板（用于单个示例） |
| `Tongyi` | 通义千问 LLM 模型 |

### 2.2 准备示例数据

```python
example_data = [
    {"word": "大", "antonym": "小"},
    {"word": "快", "antonym": "慢"},
    {"word": "高", "antonym": "矮"},
]
```

**示例数据格式**：
- 是一个列表，每个元素是一个字典
- 字典的 key 对应示例模板中的变量
- 这里有两个变量：`word`（单词）和 `antonym`（反义词）

### 2.3 创建示例模板

```python
example_template = """
单词：{word}
反义词：{antonym}
"""
```

这是**单个示例的模板**，定义了每个示例怎么展示。

**填充后的效果**：
```
单词：大
反义词：小
```

### 2.4 创建示例的 PromptTemplate

```python
example_prompt = PromptTemplate(
    input_variables=["word", "antonym"],
    template=example_template
)
```

把示例模板包装成 PromptTemplate 对象。

### 2.5 创建 FewShotPromptTemplate

```python
few_shot_prompt = FewShotPromptTemplate(
    example_prompt=example_prompt,  # 单个示例的模板
    examples=example_data,           # 示例数据
    prefix="请给出下面单词的反义词：",  # 前缀（任务说明）
    suffix="单词：{input}\n反义词：",   # 后缀（实际输入）
    input_variables=["input"],       # 输入变量
)
```

**FewShotPromptTemplate 的结构**：

```
┌─────────────────────────────────┐
│  prefix（前缀）                   │  ← 任务说明、规则等
│  "请给出下面单词的反义词："        │
├─────────────────────────────────┤
│  examples（示例）                 │  ← 多个示例
│  "单词：大  反义词：小"           │
│  "单词：快  反义词：慢"           │
│  "单词：高  反义词：矮"           │
├─────────────────────────────────┤
│  suffix（后缀）                   │  ← 实际输入
│  "单词：{input}  反义词："        │
└─────────────────────────────────┘
```

### 2.6 组合成链并调用

```python
model = Tongyi(model="qwen-plus")
chain = few_shot_prompt | model

print(chain.invoke(input={"input": "胖"}))
```

**调用后的完整提示词**：

```
请给出下面单词的反义词：

单词：大
反义词：小

单词：快
反义词：慢

单词：高
反义词：矮

单词：胖
反义词：
```

模型看到这些示例后，就知道要输出"瘦"。

---

## 💡 三、关键知识点

### 3.1 什么是 Few-Shot 提示词？

**Few-Shot（少样本学习）** 就是给模型看几个示例，让它学会任务的模式，然后对新输入给出正确输出。

**为什么有效？**
- 模型能更准确地理解任务要求
- 输出格式更统一
- 效果比 Zero-Shot（零样本）好很多

### 3.2 FewShotPromptTemplate 的组成部分

| 部分 | 参数名 | 作用 |
|-----|--------|------|
| **前缀** | `prefix` | 任务说明、规则、角色设定 |
| **示例** | `examples` | 示例数据列表 |
| **示例模板** | `example_prompt` | 每个示例的展示格式 |
| **后缀** | `suffix` | 实际输入，等待模型回答 |
| **输入变量** | `input_variables` | suffix 中用到的变量名 |

### 3.3 工作流程

```
1. 渲染 prefix
2. 遍历 examples，用 example_prompt 渲染每个示例
3. 渲染 suffix（填充输入变量）
4. 拼接成完整的提示词
5. 传给模型
```

---

## 🎯 四、常见使用场景

### 4.1 文本分类

```python
example_data = [
    {"text": "今天天气真好", "category": "正面"},
    {"text": "这东西太差了", "category": "负面"},
    {"text": "今天星期三", "category": "中性"},
]

example_template = "文本：{text}\n分类：{category}"
```

### 4.2 信息抽取

```python
example_data = [
    {"text": "张三今年30岁，是一名工程师", "name": "张三", "age": "30"},
    {"text": "李四25岁，做产品经理", "name": "李四", "age": "25"},
]
```

### 4.3 翻译

```python
example_data = [
    {"cn": "你好", "en": "Hello"},
    {"cn": "谢谢", "en": "Thank you"},
]
```

### 4.4 代码生成

```python
example_data = [
    {"input": "两数相加", "code": "def add(a, b): return a + b"},
    {"input": "两数相乘", "code": "def multiply(a, b): return a * b"},
]
```

---

## ⚠️ 五、注意事项

1. **示例要典型**：选最能代表任务的示例，覆盖各种情况
2. **格式要统一**：所有示例的输出格式要完全一致
3. **数量要适中**：2-5 个通常就够了，太多会浪费 token
4. **顺序可能影响结果**：可以试试不同的排列顺序
5. **变量名要对应**：example_data 的 key 和 example_prompt 的变量要对应
6. **处理边界情况**：考虑给一些容易混淆的示例，让模型学会区分

---

## 📝 六、进阶用法

### 6.1 动态选择示例

示例太多的时候，可以根据输入动态选择最相关的示例：

```python
from langchain_core.prompts import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import FAISS

# 用向量相似度选择最相关的示例
example_selector = SemanticSimilarityExampleSelector.from_examples(
    example_data,
    embeddings,  # 嵌入模型
    FAISS,       # 向量数据库
    k=2          # 选2个最相关的
)

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,  # 用 selector 代替 examples
    example_prompt=example_prompt,
    prefix="...",
    suffix="...",
    input_variables=["input"]
)
```

> 💡 这样可以从大量示例中自动选最相关的几个，效果更好，也更省 token。

### 6.2 查看生成的提示词

可以用 `format()` 方法查看完整的提示词，方便调试：

```python
formatted = few_shot_prompt.format(input="胖")
print(formatted)
```

### 6.3 示例的其他格式

示例不一定是问答形式，也可以是对话形式：

```python
example_template = """
用户：{question}
助手：{answer}
"""
```

---

## 🔍 七、对比：手动构建 vs 模板构建

### 手动构建（不推荐）

```python
examples = [
    ("大", "小"),
    ("快", "慢"),
    ("高", "矮"),
]

prompt_text = "请给出下面单词的反义词：\n\n"
for word, antonym in examples:
    prompt_text += f"单词：{word}\n反义词：{antonym}\n\n"
prompt_text += f"单词：{input}\n反义词："
```

**问题**：
- 代码混乱
- 难以维护
- 容易出错

### 模板构建（推荐）

```python
few_shot_prompt = FewShotPromptTemplate(
    example_prompt=example_prompt,
    examples=example_data,
    prefix="请给出下面单词的反义词：",
    suffix="单词：{input}\n反义词：",
    input_variables=["input"],
)
```

**优点**：
- 结构清晰
- 易于维护
- 可复用
- 支持高级功能（如动态选择示例）

---

## 💡 八、完整示例模板

```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.llms.tongyi import Tongyi

# 1. 准备示例数据
examples = [
    {"input": "我今天很开心", "output": "正面"},
    {"input": "这太糟糕了", "output": "负面"},
    {"input": "今天星期一", "output": "中性"},
]

# 2. 单个示例的模板
example_template = """
输入：{input}
情感：{output}
"""

example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template=example_template
)

# 3. 创建 Few-Shot 模板
few_shot_prompt = FewShotPromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
    prefix="请判断下面文本的情感倾向（正面/负面/中性）：",
    suffix="输入：{text}\n情感：",
    input_variables=["text"],
)

# 4. 组合成链
model = Tongyi(model="qwen-plus")
chain = few_shot_prompt | model

# 5. 调用
result = chain.invoke({"text": "这部电影太好看了"})
print(result)

# 6. 查看完整提示词（调试用）
print("\n--- 完整提示词 ---")
print(few_shot_prompt.format(text="这部电影太好看了"))
```

---

## 📊 九、提示词模板总结

| 模板类型 | 适用场景 | 复杂度 |
|---------|---------|--------|
| `PromptTemplate` | 简单文本生成 | ⭐ |
| `FewShotPromptTemplate` | 需要示例的任务 | ⭐⭐ |
| `ChatPromptTemplate` | 对话、多角色 | ⭐⭐ |
| `PipelinePromptTemplate` | 多步组合 | ⭐⭐⭐ |

> 💡 从简单的开始用，需要的时候再用复杂的。

---

> 💡 **学习建议**：Few-Shot 是提升大模型效果的利器，而 FewShotPromptTemplate 让这件事变得很优雅。建议把之前手动写 Few-Shot 的代码改成用模板的方式，体会结构化的好处。然后试试动态选择示例的高级用法。
