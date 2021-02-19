#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/16 19:32

"""永远的工具人"""

__author__ = 'Collapsar-G'

import getdata
import numpy as np
from numba import jit
import warnings
from collections import Counter
import cupy as cp

# from train import MAX_VOCAB_SIZE
# from train import EMBEDDING_SIZE
MAX_VOCAB_SIZE = 5076
EMBEDDING_SIZE = 200
warnings.filterwarnings('ignore')


def count(MAX_VOCAB_SIZE, train_data):
    text = []
    for key in train_data:
        for ingredient in train_data[key]:
            text.append(ingredient)

    ingredient_dict = dict(Counter(text).most_common(MAX_VOCAB_SIZE + 1))  # 得到食材字典表，key是食材，value是次数
    return ingredient_dict


def data2emb():
    a = 0.01
    data_emb = {}
    ingredient_emb = np.load("ingredient_emb.npy", allow_pickle=True)
    train_data, material_index, material_sum, name, id = getdata.get_data()
    ingredient_dict = count(MAX_VOCAB_SIZE, train_data)  # 得到食材字典表，key是食材，value是次数
    # print(ingredient_emb.dtype)
    # print(ingredient_emb)
    for key in train_data:
        recipe_emb = {}
        for ingredient in train_data[key]:
            emb = ingredient_emb.item().get(ingredient) * a
            recipe_emb[ingredient] = emb / (a + int(ingredient_dict[ingredient]))
        recipe = np.zeros(EMBEDDING_SIZE)
        for ingredient in recipe_emb:
            recipe = recipe + recipe_emb[ingredient]
        recipe = recipe / len(recipe_emb)
        data_emb[key] = recipe
    np.save("recipe_emb.npy", data_emb)  # 将生成的向量保存在字典文件中
    return data_emb, train_data, material_index, material_sum, name, id


@jit
def cosine_similarity(x, y, norm=False):
    """ 计算两个向量x和y的余弦相似度 """
    assert len(x) == len(y), "len(x) != len(y)"
    zero_list = [0] * len(x)
    if (x == zero_list).all() or (y == zero_list).all():
        return float(1) if (x == y).all() else float(0)

    # method 1
    res = np.array([[x[i] * y[i], x[i] * x[i], y[i] * y[i]] for i in range(len(x))])
    cos = sum(res[:, 0]) / (np.sqrt(sum(res[:, 1])) * np.sqrt(sum(res[:, 2])))

    return 0.5 * cos + 0.5 if norm else cos  # 归一化到[0, 1]区间内


def cupy_cos(a, b,norm = False):
    dot = a * b  # 对应原始相乘dot.sum(axis=1)得到内积
    a_len = cp.linalg.norm(a, axis=1)  # 向量模长
    b_len = cp.linalg.norm(b, axis=1)
    cos = dot.sum(axis=1) / (a_len * b_len)
    return 0.5 * cos + 0.5 if norm else cos  # 归一化到[0, 1]区间内


def top_n_cosine_similarity(x, des_data, n, norm=False):
    """计算des_data中和x余弦相似度最高的n个向量的"""
    similaritys = {}
    for key in des_data.keys():
        similarity = cosine_similarity(x, des_data[key], norm=norm)
        similaritys[key] = similarity
        # print(similarity)
    result = sorted(similaritys.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    n_list = []
    for i in range(n):
        n_list.append(result[i])

    return n_list


if __name__ == "__main__":
    data2emb()
    # # 声明字典
    # key_value = {2: 56, 1: 2, 5: 12, 4: 24, 6: 18, 3: 323}
    # np.save("ingredient_emb.npy", key_value)
    # key = np.load("ingredient_emb.npy", allow_pickle=True)
    # print(key)
    # # # 初始化
    # # result = sorted(key_value.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    # # n_list = []
    # # for i in range(2):
    # #     n_list.append(result[i][0])
    # # print(result, n_list)
