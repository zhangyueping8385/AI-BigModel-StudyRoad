from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage

model = ChatTongyi(
    model = 'qwen-plus'
)

messages = [
    SystemMessage(content="你是毛不易的师傅，擅长作词作曲"),
    HumanMessage(content="给我生成关于成长的一首流行歌")
]

response = model.stream(
    input=messages
)

for chunk in response:
    print(chunk.content,end="",flush=True)