from langchain_core.prompts import FewShotPromptTemplate,PromptTemplate
from langchain_community.llms import Tongyi
# 示例的模版
example_template = PromptTemplate.from_template("单词{word}，反义词{antonym}")

# 示例的数据,要求list套dict
example_data = [
    {"word":"大","antonym":"小"},
    {"word": "上", "antonym": "下"},
]

fewshot_template = FewShotPromptTemplate(
    example_prompt=example_template, #示例数据的模板
    prefix="严格按照示例格式，只给出语义直接对立的单字反义词，不要多余解释",  # 示例之前的提示词
    examples=example_data,  #示例数据
    suffix = "请给出{input_word}的反义词，仅输出单个汉字",   # 示例之后的提示词
    input_variables=["input_word"]  # 声明在前缀或后缀中需要注入的变量名

)

prompt_text = fewshot_template.invoke(input={"input_word":"左"}).to_string()

model = Tongyi(
    model = "qwen-plus"
)

print(model.invoke(input=prompt_text))
