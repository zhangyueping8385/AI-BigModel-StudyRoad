from langchain_community.document_loaders import JSONLoader

"""
{
  "name": "周杰轮",
  "age": 11,
  "hobby": [
    "唱",
    "跳",
    "RAP"
  ],
  "other": {
    "addr": "深圳",
    "tel": "12332112321"
  }
}
"""
loader = JSONLoader(
    file_path="./data/stus.json",
    jq_schema='.other.addr'  # 获取到深圳
)

document = loader.load()
print(document)


"""
{"name":"周杰轮","age":11,"gender":"男"}
{"name":"蔡依临","age": 12,"gender":"女"}
{"name":"王力鸿","age":11,"gender":"男"}
"""

loader_jsonline = JSONLoader(
    file_path="./data/stu_json_lines.json",
    jq_schema=".name",
    text_content=False,
    json_lines=True
)

document_jsonline = loader_jsonline.load()
print(document_jsonline)
