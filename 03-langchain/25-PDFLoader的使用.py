from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(
    file_path="./data/Zookeeper篇.pdf",
    mode="page"  #默认page，每个页面生成一个Document对象，singgle将所有页面生成一个Document对象
)

docs = loader.load()
print(len(docs))
for doc in docs:
    print(doc)