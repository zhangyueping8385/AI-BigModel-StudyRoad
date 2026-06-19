from langchain_community.llms.tongyi import Tongyi

model = Tongyi(
    model = "qwen-plus"
)

response = model.invoke("你是谁，能干嘛？？")

print(response)