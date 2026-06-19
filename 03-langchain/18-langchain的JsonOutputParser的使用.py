from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate

strParser = StrOutputParser()
jsonParser = JsonOutputParser()

model = ChatTongyi(model = "qwen-plus")

first_prompt = PromptTemplate.from_template(
"我邻居姓：{lastname}，刚生了{gender}，请帮忙起名字，并封装为JSON格式返回给我。要求key是name，value就是你起的名字，请严格遵守格式要求。"
)

second_prompt = PromptTemplate.from_template(
    "姓名{name}，请帮我解析含义"
)

chain  = first_prompt | model | jsonParser | second_prompt | model |strParser

res = chain.stream(
    {"lastname":"张","gender":"女儿"}
)

for chunck in res:
    print(chunck,end="",flush=True)