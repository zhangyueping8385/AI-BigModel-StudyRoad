from langchain_community.llms.tongyi import Tongyi

model = Tongyi(
    model = "qwen-plus"
)

response = model.stream("你是谁，能写什么代码？")

for i in response:
    print(i,end="",flush=True)