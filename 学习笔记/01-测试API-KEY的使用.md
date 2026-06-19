# 01 - 测试 API-KEY 的使用

> 学习如何配置并验证 API Key，确保能正常调用大模型接口

---

## 📚 一、代码概述

本代码演示了**最基础的大模型调用方式**，用于验证 API Key 是否配置正确，是所有后续开发的第一步。

### 1.1 核心功能

- ✅ 使用 OpenAI 兼容 SDK 调用通义千问模型
- ✅ 直接在代码中配置 API Key
- ✅ 验证接口连通性与返回结果

---

## 🔧 二、核心代码解析

### 2.1 导入与初始化

```python
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key="sk-84d7e5ef9b684f918cc343b6a54b7c45",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
```

**关键参数说明：**

| 参数 | 说明 |
|-----|------|
| `api_key` | API 密钥，用于身份认证和计费 |
| `base_url` | 模型服务的接口地址 |

> 💡 **为什么 base_url 是阿里云的地址？**
> 
> 这里使用的是**阿里云百炼平台**的通义千问模型，但通过 OpenAI 兼容接口调用。这样做的好处是：代码写法与 OpenAI 完全一致，只需切换 `base_url` 即可更换模型供应商。

### 2.2 发起调用

```python
completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？你能做什么？？"},
    ]
)
```

**调用参数：**

| 参数 | 说明 |
|-----|------|
| `model` | 指定使用的模型名称，这里是 `qwen-plus` |
| `messages` | 对话消息列表，是一个数组 |

**messages 中的角色（role）：**

| 角色 | 作用 |
|-----|------|
| `system` | 系统提示词，设定 AI 的身份和行为规则 |
| `user` | 用户输入的内容 |
| `assistant` | AI 的回复内容（历史对话中使用） |

### 2.3 输出结果

```python
print(completion.model_dump_json())
```

使用 `model_dump_json()` 方法将返回对象序列化为 JSON 字符串，方便查看完整的返回结构。

---

## 💡 三、关键知识点

### 3.1 API Key 的两种配置方式

| 方式 | 代码示例 | 适用场景 |
|-----|---------|---------|
| **硬编码** | `api_key="sk-xxx"` | 快速测试、学习 demo |
| **环境变量** | `api_key=os.getenv("OPENAI_API_KEY")` | 生产环境、项目开发 |

> ⚠️ **安全提醒**：生产环境中**绝对不要**把 API Key 直接写在代码里！一旦泄露可能导致高额费用。推荐使用环境变量或配置文件。

### 3.2 OpenAI 兼容接口

很多大模型服务商都提供了 **OpenAI 兼容接口**，这意味着：

```
同样的代码，只改 base_url 和 api_key，就能切换不同的大模型
```

**常见的兼容接口供应商：**
- 阿里云百炼（通义千问）
- 百度文心一言
- 月之暗面（Kimi）
- DeepSeek
- 智谱 AI

---

## 🎯 四、返回结果结构

调用成功后，返回的 JSON 大致结构如下：

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "qwen-plus",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "我是通义千问，一个AI助手..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 100,
    "total_tokens": 120
  }
}
```

**关键字段：**

| 字段 | 说明 |
|-----|------|
| `choices[0].message.content` | AI 的回复内容 |
| `usage.total_tokens` | 本次调用消耗的 token 总数（用于计费） |
| `finish_reason` | 结束原因，`stop` 表示正常结束 |

---

## ⚠️ 五、常见问题

**Q1: 调用报错 "Invalid API Key" 怎么办？**
> 检查 API Key 是否正确复制，注意不要有多余空格。确认 Key 对应的账户是否有余额。

**Q2: 报错 "Connection Error" 怎么办？**
> 检查网络连接，确认 `base_url` 地址正确。国内网络可能需要特殊配置。

**Q3: 怎么获取 API Key？**
> 去阿里云百炼平台注册账号，在控制台创建 API Key 即可。

---

## 📝 六、快速测试模板

```python
from openai import OpenAI

client = OpenAI(
    api_key="你的API_KEY",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 最简单的测试
response = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

---

> 💡 **学习建议**：这是入门第一步，确保能跑通后再继续学习更复杂的用法。建议把 API Key 配置到环境变量中，养成好习惯。
