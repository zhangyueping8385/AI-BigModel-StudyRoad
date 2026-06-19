from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(
    file_path="./data/stu.csv",
    csv_args={
        "delimiter":",",
        "quotechar":'"', # 指定带有分隔符文本的引号包围是单引号还是双引号
    },
    encoding="utf-8"
)


"""
两种加载方式都是为了得到Document对象
"""
# 批量加载
documents = loader.load()
for document in documents:
    print(document)

# 懒加载
for document in loader.lazy_load():
    print(document)