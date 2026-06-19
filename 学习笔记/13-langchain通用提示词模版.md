# 13 - LangChain 通用提示词模版

> 学习使用 PromptTemplate 创建可复用的提示词模板，通过变量占位符动态生成提示词

---

## 📚 一、代码概述

本代码演示了**使用 LangChain 的 PromptTemplate** 创建可复用的提示词模板，通过变量占位符实现提示词的动态生成，并使用 LCEL 管道符组合成链。

### 1.1 核心功能

- ✅ 使用 PromptTemplate 创建提示词模板
- ✅ 使用 `{变量名}` 作为占位符
- ✅ 通过 `from_template` 快速创建
- ✅ 使用 `|` 管道符组合链（LCEL）

---

## 🔧 二、核心代码解析

### 2.1 导入相关类

```python
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi
```

| 导入类 | 说明 |
|-------|------|
| `PromptTemplate` | 提示词模板类 |
| `Tongyi` | 通义千问 LLM 模型 |

### 2.2 创建提示词模板

```python
prompt = PromptTemplate.from_template("我的邻居姓{lastname}，刚生了{gender}孩子，帮我起{number}个名字")
```

**模板语法**：

- 使用 `{变量名}` 作为占位符
- 变量名可以自定义，只要前后一致就行
- 调用时传入对应的值

**模板中的变量**：

| 变量 | 说明 | 示例值 |
|-----|------|--------|
| `{lastname}` | 姓氏 | "张" |
| `{gender}` | 性别 | "女生" |
| `{number}` | 数量 | "3" |

### 2.3 初始化模型

```python
model = Tongyi(model="qwen-plus")
```

### 2.4 组合成链

```python
chain = prompt | model
```

**LCEL（LangChain Expression Language）管道语法**：

使用 `|` 运算符把多个组件连接起来，形成一条链。

```
输入 → prompt（填充模板） → model（调用模型） → 输出
```

> 💡 这就像 Unix 的管道命令 `cat file.txt | grep "hello"`，前一个的输出是后一个的输入。

### 2.5 流式调用

```python
response = chain.stream(input={"lastname": "张", "gender": "女生", "number": "3"})
for i in response:
    print(i, end="", flush=True)
```

**调用方式**：

- 传入一个字典，key 是变量名，value 是变量值
- 链会自动把值填充到模板里，然后调用模型

**执行流程**：

```
1. 传入 {"lastname": "张", "gender": "女生", "number": "3"}
2. prompt 填充模板 → "我的邻居姓张，刚生了女孩子，帮我起3个名字"
3. model 调用模型 → 生成回复
4. 返回结果
```

---

## 💡 三、关键知识点

### 3.1 为什么要用提示词模板？

| 好处 | 说明 |
|-----|------|
| **复用性** | 同一个模板可以用不同的参数调用多次 |
| **可维护性** | 修改提示词只需要改模板，不用改业务代码 |
| **可读性** | 模板和逻辑分离，代码更清晰 |
| **易于测试** | 可以单独测试模板的效果 |

**不用模板的写法（不推荐）**：
```python
lastname = "张"
gender = "女生"
number = "3"
prompt_text = f"我的邻居姓{lastname}，刚生了{gender}孩子，帮我起{number}个名字"
response = model.invoke(prompt_text)
```

**用模板的写法（推荐）**：
```python
prompt = PromptTemplate.from_template("我的邻居姓{lastname}，刚生了{gender}孩子，帮我起{number}个名字")
chain = prompt | model
response = chain.invoke({"lastname": "张", "gender": "女生", "number": "3"})
```

> 💡 看起来模板写法代码更多，但当提示词很复杂、有很多变量时，模板的优势就体现出来了。

### 3.2 PromptTemplate 的创建方式

#### 方式一：from_template（最常用）

```python
prompt = PromptTemplate.from_template("你是一个{role}，请回答{question}")
```

简单直接，一行搞定。

#### 方式二：构造函数

```python
prompt = PromptTemplate(
    template="你是一个{role}，请回答{question}",
    input_variables=["role", "question"]
)
```

可以显式指定输入变量。

#### 方式三：从文件加载

```python
prompt = PromptTemplate.from_file("prompt_template.txt")
```

模板存在文件里，代码更干净。

### 3.3 模板格式化

可以用 `format()` 方法查看填充后的完整提示词：

```python
prompt = PromptTemplate.from_template("你是一个{role}，请回答{question}")

# 格式化模板
formatted = prompt.format(role="编程专家", question="什么是Python")
print(formatted)
# 输出："你是一个编程专家，请回答什么是Python"
```

> 💡 调试的时候很有用，可以看看模板填充对不对。

### 3.4 LCEL 管道语法

`|` 是 LangChain 的管道运算符，可以把多个 Runnable 组件串起来：

```python
# 单个组件
result = model.invoke("你好")

# 多个组件用管道连接
chain = prompt | model
result = chain.invoke({"name": "张三"})
```

**管道的特点**：

- 前一个组件的输出是后一个组件的输入
- 所有组件都必须是 Runnable
- 链本身也是 Runnable，支持 invoke、stream、batch 等方法

---

## 🎯 四、常见使用模式

### 4.1 简单模板

```python
prompt = PromptTemplate.from_template("用一句话解释{concept}")
chain = prompt | model

result = chain.invoke({"concept": "机器学习"})
print(result)
```

### 4.2 多变量模板

```python
prompt = PromptTemplate.from_template(
    "你是一个{profession}，请用{style}的风格，写一段关于{topic}的话"
)
chain = prompt | model

result = chain.invoke({
    "profession": "诗人",
    "style": "豪放",
    "topic": "春天"
})
```

### 4.3 带系统提示的模板

```python
prompt = PromptTemplate.from_template("""
你是一个{role}，回答问题时要遵循以下原则：
1. 回答要简洁
2. 用例子说明
3. 最后总结要点

问题：{question}
""")
```

---

## ⚠️ 五、注意事项

1. **变量名要一致**：模板中的 `{变量名}` 和调用时的字典 key 要完全一致
2. **变量要用大括号**：是 `{name}` 不是 `$name` 或 `{{name}}`
3. **输入是字典**：链的输入必须是字典，不能直接传字符串
4. **模板中要显示大括号**：如果模板本身需要显示 `{`，要用 `{{` 转义
5. **变量顺序不重要**：字典是无序的，只要 key 对就行

---

## 📝 六、进阶：模板的其他功能

### 6.1 部分变量预填充（partial）

```python
prompt = PromptTemplate.from_template("你是一个{role}，请回答{question}")

# 预填充 role，只留 question 作为输入
partial_prompt = prompt.partial(role="编程专家")

# 调用时只需要传 question
chain = partial_prompt | model
result = chain.invoke({"question": "什么是Python"})
```

### 6.2 查看模板变量

```python
prompt = PromptTemplate.from_template("你是一个{role}，请回答{question}")

print(prompt.input_variables)
# 输出：['role', 'question']
```

### 6.3 模板验证

```python
# 验证模板中的变量是否都在 input_variables 中
prompt = PromptTemplate(
    template="你是一个{role}，请回答{question}",
    input_variables=["role", "question"],
    validate_template=True
)
```

---

## 🔍 七、PromptTemplate vs ChatPromptTemplate

| 对比项 | PromptTemplate | ChatPromptTemplate |
|-------|---------------|-------------------|
| **输出** | 字符串 | 消息列表 |
| **适用模型** | LLM | Chat Model |
| **角色支持** | 不直接支持 | 支持 system/human/ai |
| **复杂度** | 简单 | 稍复杂 |
| **使用场景** | 简单文本生成 | 对话、多角色 |

> 💡 简单场景用 PromptTemplate，对话场景用 ChatPromptTemplate。下一节会学 ChatPromptTemplate。

---

## 💡 八、完整示例模板

```python
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi

# 1. 创建提示词模板
prompt = PromptTemplate.from_template("""
你是一个{role}，请用{style}的风格回答以下问题。
要求：
- 回答简洁明了
- 用例子说明
- 最后总结要点

问题：{question}
""")

# 2. 初始化模型
model = Tongyi(model="qwen-plus")

# 3. 组合成链
chain = prompt | model

# 4. 调用
result = chain.invoke({
    "role": "编程老师",
    "style": "幽默",
    "question": "什么是递归"
})
print(result)

# 5. 流式调用
print("\n--- 流式输出 ---")
for chunk in chain.stream({
    "role": "编程老师",
    "style": "幽默",
    "question": "什么是递归"
}):
    print(chunk, end="", flush=True)
```

---

> 💡 **学习建议**：提示词模板是 LangChain 最基础也最常用的组件之一。建议养成使用模板的习惯，不要把提示词硬编码在代码里。试着把之前写的提示词改造成模板形式，体会复用的好处。
