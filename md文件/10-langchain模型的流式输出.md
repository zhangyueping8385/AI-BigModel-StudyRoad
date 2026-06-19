# 10 - LangChain 模型的流式输出

> 学习在 LangChain 中使用流式输出，实现打字机效果

---

## 📚 一、代码概述

本代码演示了**在 LangChain 中使用流式输出**的方法，通过 `stream()` 方法逐块获取模型回复，实现打字机效果。

### 1.1 核心功能

- ✅ 使用 LangChain 的 stream 方法
- ✅ 逐块接收模型输出
- ✅ 实现流式展示效果

---

## 🔧 二、核心代码解析

### 2.1 导入与初始化

```python
from langchain_community.llms.tongyi import Tongyi

model = Tongyi(
    model = "qwen-plus"
)
```

和上一节一样，初始化 Tongyi 模型。

### 2.2 流式调用

```python
response = model.stream("你是谁，能写什么代码？")
for i in response:
    print(i, end="", flush=True)
```

**stream 方法的特点：**

- 返回一个**迭代器**（generator）
- 通过 `for` 循环逐块获取内容
- 每一块是一小段文本（字符串）

**参数说明：**

| print 参数 | 作用 |
|-----------|------|
| `end=""` | 不换行，让输出连在一起 |
| `flush=True` | 立即刷新缓冲区，实时显示 |

---

## 💡 三、关键知识点

### 3.1 invoke vs stream

| 对比项 | invoke | stream |
|-------|--------|--------|
| **返回类型** | 字符串 | 迭代器（逐块返回） |
| **等待时间** | 等全部生成完才返回 | 第一个字很快就出来 |
| **使用方式** | 直接赋值 | for 循环遍历 |
| **用户体验** | 长时间等待 | 打字机效果 |
| **适用场景** | 后台处理、短文本 | 前端展示、长文本 |

**效果对比：**

```
invoke:
[等待5秒...] "你好，我是..." （突然一整段出来）

stream:
[0.5秒] "你"
[0.1秒] "好"
[0.1秒] "，"
[0.1秒] "我"
...  一个字一个字蹦出来
```

### 3.2 LangChain 中的流式输出

LangChain 的所有 Runnable 组件都支持流式输出：

```python
# 模型流式输出
for chunk in model.stream("你好"):
    print(chunk, end="")

# 链也支持流式输出
for chunk in chain.stream({"input": "你好"}):
    print(chunk, end="")
```

> 💡 这就是 Runnable 接口的好处——所有组件都有相同的方法，包括 stream。

### 3.3 流式输出的原理

大模型生成文本是**逐个 token 生成**的：

```
生成 token 1 → 生成 token 2 → 生成 token 3 → ...
     ↓              ↓              ↓
   立刻返回        立刻返回        立刻返回
```

流式输出就是把每个 token 生成后**立即返回**，而不是等全部生成完再返回。

底层基于 **SSE（Server-Sent Events）** 协议，服务器向客户端单向推送数据。

---

## 🎯 四、常见使用模式

### 4.1 简单流式打印

```python
for chunk in model.stream("写一首诗"):
    print(chunk, end="", flush=True)
print()  # 最后换行
```

### 4.2 收集完整内容

有时候需要一边流式展示，一边保存完整内容：

```python
full_text = ""
for chunk in model.stream("写一首诗"):
    full_text += chunk
    print(chunk, end="", flush=True)

print(f"\n\n完整内容：{full_text}")
```

### 4.3 流式 + 回调函数

可以用回调函数处理每一块内容：

```python
def process_chunk(chunk):
    # 自定义处理逻辑，比如发送到前端
    print(chunk, end="", flush=True)

for chunk in model.stream("写一首诗"):
    process_chunk(chunk)
```

---

## ⚠️ 五、注意事项

1. **flush=True 很重要**：Python 的 print 默认有缓冲区，不加 flush 可能会攒到缓冲区满了才显示，失去流式效果
2. **end="" 不要忘**：默认 end="\n" 会每块换一行，效果很奇怪
3. **最后要换行**：流式输出结束后，记得 print() 换个行，否则后续输出会接在后面
4. **块的大小不固定**：每一块的长度不一定一样，可能是一个字，也可能是几个字
5. **错误处理**：流式输出过程中如果出错，处理方式和普通调用不同，需要在循环中捕获异常

---

## 📝 六、Chat Model 的流式输出

Chat Model 的流式输出稍微不同，返回的是消息对象而不是字符串：

```python
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage

model = ChatTongyi(model="qwen-plus")

for chunk in model.stream([HumanMessage(content="你好")]):
    print(chunk.content, end="", flush=True)
```

**区别**：
- LLM 的 stream 返回字符串
- Chat Model 的 stream 返回消息对象，需要 `.content` 获取文本

---

## 🔍 七、进阶：流式输出的应用场景

### 7.1 聊天机器人界面

最常见的应用，类似 ChatGPT 的打字效果，提升用户体验。

### 7.2 实时预览

用户可以边看边判断是否需要停止生成，节省时间和 token。

### 7.3 长文本生成

生成文章、代码等长内容时，用户不用等太久就能看到开头。

### 7.4 流式处理

有些场景下可以边生成边处理，比如：
- 实时翻译（生成一句翻译一句）
- 实时摘要（生成一段摘要一段）
- 流式写入数据库

---

## 💡 八、完整示例模板

```python
from langchain_community.llms.tongyi import Tongyi

def stream_chat(prompt):
    """流式对话函数，返回完整内容"""
    model = Tongyi(model="qwen-plus")
    
    full_response = ""
    print("AI: ", end="", flush=True)
    
    for chunk in model.stream(prompt):
        full_response += chunk
        print(chunk, end="", flush=True)
    
    print()  # 结束换行
    return full_response

# 使用
result = stream_chat("介绍一下Python")
print(f"\n生成完成，共 {len(result)} 字")
```

---

## 📊 九、invoke / stream / batch 对比

| 方法 | 输入 | 输出 | 特点 | 适用场景 |
|-----|------|------|------|---------|
| `invoke` | 1个 | 1个 | 一次性返回 | 简单调用、后台处理 |
| `stream` | 1个 | 多块 | 流式返回 | 前端展示、长文本 |
| `batch` | 多个 | 多个 | 批量处理 | 批量生成、并发 |

> 💡 这三个方法是 LangChain Runnable 的标准接口，所有组件都支持。

---

> 💡 **学习建议**：流式输出是提升用户体验的重要手段。建议在前端展示时都使用流式输出，后台处理时可以用普通的 invoke。试着对比两种方式的响应速度和体验差异。
