from langchain_community.chat_models import ChatTongyi
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


"""
用户的提问 + 向量库中检索到的参考资料
"""

model = ChatTongyi(
    model  = "qwen-plus"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "以我提供的已知参考资料为主，简清和专业的回答用户问题。参考资料：{context}"),
        ("user", "用户提问{input}")
    ]
)

vector_store = InMemoryVectorStore(embedding=DashScopeEmbeddings(model = "text-embedding-v4"))

# 向量库的数据 add_texts 传入一个list[str]
vector_store.add_texts(
    [
        "减肥就是要少吃多练",
        "在减脂期间吃东西很重要，清淡少油控制卡路里摄入并运动起来",
        "跑步是很好的运动哦"
    ]
)

input_text = "怎么减肥？"

def print_prompt(prompt):
    print(prompt.to_string())
    print("=" * 20)
    return prompt

# langchain中向量的存储对象， as_retriever 可以返回一个Runnable接口 的子类实例对象
retriever = vector_store.as_retriever(search_kwargs={"k":1})

def format_func(docs:list[Document]):
    if not docs:
        return  "无相关参考资料"

    format_str = "["
    for doc in docs:
        format_str += doc.page_content
    format_str += "]"
    return format_str

chain = {"input":RunnablePassthrough(),"context":retriever | format_func} | prompt | print_prompt | model | StrOutputParser()

res = chain.invoke(
    input_text
)

print(res)