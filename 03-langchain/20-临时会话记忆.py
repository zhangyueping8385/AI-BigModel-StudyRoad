from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

model = ChatTongyi(
    model = 'qwen-plus'
)

# prompt = PromptTemplate.from_template(
#     "你需要根据会话历史回应永华问题，对话历史：{historychat}，用户提问{input}，请回答"
# )
prompt = ChatPromptTemplate.from_messages(
    [
        ("system","你需要根据会话历史回应用户问题。对话历史："),
        MessagesPlaceholder("chat_history"),
        ("human","请回答如下问题：{input}")
    ]
)


strParser = StrOutputParser()


# 打印消息
def print_prompt(full_prompt):
    print("="*20,full_prompt.to_string(),"="*20)
    return full_prompt

chain = prompt | print_prompt |model |strParser



store = {} #key是session，value是InMemoryCHatMessageHistory类对象
def get_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 功能：自动附加历史消息
conversation_chain = RunnableWithMessageHistory(
    chain,
    get_history, # 通过会话ID获取InMemoryCHatMessageHistory类对象
    input_messages_key="input",
    history_messages_key="chat_history"
)

if __name__ == '__main__':
    # 固定格式，添加langchain的配置，为当前程序配置所属的session_id
    session_config = {
        "configurable":{
            "session_id":"user_001"
        }
    }

    res = conversation_chain.invoke(
        {"input":"小明有3只猪"},
        session_config
    )
    print("第一次执行",res)

    res = conversation_chain.invoke(
        {"input": "小明有5只猪"},
        session_config
    )
    print("第二次执行", res)

    res = conversation_chain.invoke(
        {"input": "总共有几只猪"},
        session_config
    )
    print("第三次执行", res)