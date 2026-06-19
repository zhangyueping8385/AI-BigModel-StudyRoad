import numpy as np

"""
计算两个向量的点积
两个向量对的之相乘纸之和
"""
def get_dot(vec_a,vec_b):
    if len(vec_a) != len(vec_b):
        print("两个向量纬度不一样！")

    sum_dot = 0
    for a,b in zip(vec_a,vec_b):
        sum_dot += (a * b)
    return sum_dot

"""
计算向量的模
某向量对每个数字平方开根号
"""

def get_norm(vec_a):
    sum_norm  = 0
    for i in vec_a:
        sum_norm += (i * i)
    return np.sqrt(sum_norm)

"""
计算余弦相似度
两个向量的点积 / 两个向量的模长的乘积
"""
def cosine_similarity(vec_a,vec_b):
    return get_dot(vec_a,vec_b) / (get_norm(vec_a) * get_norm(vec_b))


if __name__ == '__main__':
    vec_a = [0.5, 0.5]
    vec_b = [0.7, 0.7]
    vec_c = [0.7, 0.5]
    vec_d = [-0.6, -0.5]

    print(cosine_similarity(vec_a, vec_b))
    print(cosine_similarity(vec_a, vec_c))
    print(cosine_similarity(vec_a, vec_d))
