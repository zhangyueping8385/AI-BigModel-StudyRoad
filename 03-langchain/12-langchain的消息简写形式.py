from langchain_community.chat_models.tongyi import ChatTongyi

model = ChatTongyi(
    model = 'qwen-plus'
)

messages = [
    ("system","你是一个唐代诗人"),
    ("human", "帮我写一首7字唐诗"),
    ("ai",
     """
    《秋江独钓》  
    霜落寒江一钓舟，  
    孤峰倒浸碧天秋。  
    风来忽散千重浪，  
    月出徐浮万点鸥。  
    竿影摇星沉水底，  
    蓑痕带露立汀洲。  
    忽闻隔岸渔歌起，  
    半入芦花半入流。 
    """),
    ("human", "按照上方的形式，再写一首诗")
]

response = model.stream(
    input=messages
)

for chunk in response:
    print(chunk.content,end="",flush=True)