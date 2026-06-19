from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnableLambda

model = ChatTongyi(
    model = 'qwen-plus'
)
strParser = StrOutputParser()

first_prompt = PromptTemplate.from_template(
    '我邻居姓：{lastname}，刚生了{gender}，请帮忙起名字，只告诉我名字即可，不需要额外信息'
)

second_prompt = PromptTemplate.from_template(
    "姓名{name},请告诉我名字含义"
)

my_func = RunnableLambda(lambda ai_msg:{"name":ai_msg.content})

chain = first_prompt | model | my_func | second_prompt | model | strParser

res = chain.stream(
    {"lastname":"刘","gender":"女儿"}
)

for chunk in res:
    print(chunk,end="",flush=True)