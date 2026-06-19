from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi


parser = StrOutputParser()
model = ChatTongyi(
    model="qwen-plus"
)
prompt = PromptTemplate.from_template(
    "姓氏{lastname}，性别{gender}，直接给出合适名字，只输出名字，不要多余话语、不要提问。"
)

chain = prompt | model | parser | model | parser

res = chain.invoke(input={"lastname":"张","gender":"女"})
print(res)