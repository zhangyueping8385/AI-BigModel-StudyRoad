from langchain_community.embeddings import DashScopeEmbeddings

model = DashScopeEmbeddings()

# 单文本转向量
print(model.embed_query("你好"))
print(model.embed_documents(['你好', 'hello', '再见']))