from langchain_chroma import Chroma
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import CSVLoader


vector_store = InMemoryVectorStore(
    embedding=DashScopeEmbeddings()
)

"""
持久化向量存储
需要保证 langchain-chroma chromedb两个库已安装
"""
vector_store = Chroma(
    collection_name="test",   #给当前向量存储起个名字，类似于数据库名称
    embedding_function=DashScopeEmbeddings(), # 向量化函数
    persist_directory='./data/chroma_db'    # 存储路径
)

loader = CSVLoader(
    file_path="data/info.csv",
    encoding="utf-8",
    source_column="source"
)

documents = loader.load()

"""
内存向量存储
"""
# 新增向量
vector_store.add_documents(
    documents = documents,
    ids=["id"+str(i) for i in range(1,len(documents)+1)]
)

#删除向量
vector_store.delete(["id1","id2"])



#检索向量，返回类型为[Document]
result = vector_store.similarity_search(
    "Python是不是很简单呀",
    2  #检索的结果个数
)


print(result)