import json
import os
from typing import Sequence
from langchain_community.chat_models import ChatTongyi
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableWithMessageHistory, RunnableConfig
# 自定义基于文件的会话历史记录类
class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, store_path: str = "./chat_history"):
        self.session_id = session_id  # 会话id作为文件名
        self.store_path = store_path  # 存储目录
        self.file_path = os.path.join(self.store_path, self.session_id)
        # 确保目录存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    def add_message(self, message: BaseMessage) -> None:
        # 单条消息添加接口，内部调用批量添加接口
        self.add_messages([message])
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # 1. 读取现有消息
        all_messages = list(self.messages)
        # 2. 追加新消息
        all_messages.extend(messages)
        # 3. 序列化并写入文件
        # 注意：这里采用覆盖写入模式，适用于中小规模历史记录
        new_messages = [message_to_dict(msg) for msg in all_messages]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f)
    @property
    def messages(self) -> list[BaseMessage]:
        """从文件读取并反序列化消息"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages = json.load(f)
                return messages_from_dict(messages)
        except FileNotFoundError:
            # 文件不存在时返回空列表
            return []
    def clear(self):
        """清空会话记录"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
# --- 以下链的定义与临时记忆部分基本一致 ---
model = ChatTongyi(model="qwen-plus")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你需要根据历史对话回复用户问题"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "请回复如下问题{input}"),
    ]
)
def print_prompt(prompt_value):
    """打印调试信息，显示完整的 Prompt 结构"""
    print("\n" + "=" * 30 + " PROMPT DEBUG " + "=" * 30)
    for msg in prompt_value.messages:
        print(f"[{msg.type.upper()}]: {msg.content}")
    print("=" * 74 + "\n")
    return prompt_value
base_chain = prompt | RunnableLambda(print_prompt) | model | StrOutputParser()
def get_chat_history(session_id: str) -> BaseChatMessageHistory:
    """
    关键变化：这里返回的是 FileChatMessageHistory 实例
    不同的 session_id 对应不同的物理文件
    """
    return FileChatMessageHistory(session_id)
# 创建带有持久化记忆功能的链
conversation_chain = RunnableWithMessageHistory(
    base_chain,
    get_chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)
if __name__ == "__main__":
    session_config: RunnableConfig = {
        "configurable": {"session_id": "user_001"}
    }
    questions = [
        # "小明有1只猫",
        # "小明有4只狗",
        "宠物总数是多少"
    ]
    for q in questions:
        print(f"\nUser: {q}")
        response = conversation_chain.invoke(
            {"input": q},
            config=session_config
        )
        print(f"AI: {response}")