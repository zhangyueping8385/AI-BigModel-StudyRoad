from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system","你是一个唐朝诗人，会作诗"),
        MessagesPlaceholder("history"),
        ("human","请再来一首唐诗")
    ]
)

history_data = [
    ("human","你来写一个唐诗"),
    ("ai","床前明月光，疑是地上霜，举头望明月，低头思故乡"),
    ("system","好诗好诗，再来一首"),
    ("ai","锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦")
]

prompt_text = chat_prompt_template.invoke({"history":history_data}).to_string()
print(prompt_text)

model = ChatTongyi(
    model="qwen-plus"
)

res = model.invoke(prompt_text).content

print(res)