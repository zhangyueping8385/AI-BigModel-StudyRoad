from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


loader = TextLoader(
    file_path="./data/文件24data.txt",
    encoding="utf-8"
)

docs = loader.load()

spliter = RecursiveCharacterTextSplitter(
    chunk_size=500, #分段的最大字符数
    chunk_overlap=50, # 分段之间允许的重叠字符数
    separators=["。", "？", "！", "；", "，", "：", "（", "）", "“", "”", "《", "》", "【", "】", "——", "…",".","?","!",";"], # 文本分隔的依据符号
    length_function=len
)

split_docs = spliter.split_documents(docs)
print(len(split_docs))  # 查看Document对象个数

for split_doc in split_docs:
    print("="*20)
    print(split_doc)
    print("="*20)
