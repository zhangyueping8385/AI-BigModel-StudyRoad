from langchain_core.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi

prompt = PromptTemplate.from_template(
    "我的邻居姓{lastname}，刚生了{gender}，你帮我起个名字，简单回答。"
)

model = Tongyi(
    model = "qwen-plus"
)

chain  = prompt | model

response = chain.stream(
    input={"lastname":"张","gender":"女生"},
)

for chunk in response:
    print(chunk,end="",flush=True)