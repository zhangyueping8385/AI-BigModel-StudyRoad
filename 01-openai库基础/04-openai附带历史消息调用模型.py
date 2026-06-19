import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
)

response = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {'role':'system','content':'你是一个百事通，回答言简意赅'},
        {'role': 'user', 'content': '我有2只猫'},
        {'role':'assistant','content':'好的'},
        {'role': 'user', 'content': '我有5只狗'},
        {'role': 'assistant', 'content': '好的'},
        {'role': 'user', 'content': '我有几只宠物'}
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content,
          end=" ",  # 每一段之间以空格分隔
          flush=True  # 立刻刷新缓存区
    )
