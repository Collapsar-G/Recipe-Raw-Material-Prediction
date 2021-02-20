#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/16 19:32

"""词谱预测文件"""

__author__ = 'Collapsar-G'

import json

import numpy as np
from numba import jit
import warnings
from collections import Counter
import csv
import re
from pattern3.text.en import singularize
from utils import count, top_n_cosine_similarity

from sklearn.metrics.pairwise import cosine_similarity, paired_distances

MAX_VOCAB_SIZE = 5076
EMBEDDING_SIZE = 200
warnings.filterwarnings('ignore')
test_data_path = "./data/recipe3.csv"
materials = []


def get_data_test():
    train_data = []
    with open(test_data_path, encoding="utf8") as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
            train_data.append(row)
    return train_data


def data_split(datas):  # 将读取的数据处理为字典列表
    result = {}
    id = {}
    name = {}
    t = {}
    for i in range(len(datas)):

        data = datas[i]
        recipe = {}
        # for data in datas:
        dst = {}
        # print(len(data))
        ingredient = {}
        for index in range(2, len(data)):
            # print(index)
            dec = data[index].split('#')
            a = dec[0]
            b= a 
            b = singularize(b)
            temp = dec[0].lower()
            temp = re.sub('fresh|frozen|large|small|chunks', '', temp)  # 去掉部分无关紧要形容词

            temp = singularize(temp)
            if temp not in materials:
                materials.append(temp)
            dst[temp] = dec[1]
            ingredient[dec[0]] = temp
            if a != b:
                t[a] = b
                t[b] = a
        # print(dst)
        result[data[0]] = dst
        name[data[0]] = ingredient
        id[data[0]] = data[1]
        # print(result)

    return result, name, id, t


def test_emb(data):
    a = 0.01
    data_emb = {}
    ingredient_emb = np.load("ingredient_emb.npy", allow_pickle=True)
    ingredient_dict = count(MAX_VOCAB_SIZE, data)  # 得到食材字典表，key是食材，value是次数
    for key in data:
        recipe_emb = {}
        for ingredient in data[key]:
            try:
                emb = ingredient_emb.item().get(ingredient) * a
                recipe_emb[ingredient] = emb / (a + int(ingredient_dict[ingredient]))
            except:
                continue
        recipe = np.zeros(EMBEDDING_SIZE)
        for ingredient in recipe_emb:
            recipe = recipe + recipe_emb[ingredient]
        recipe = recipe / len(recipe_emb)
        data_emb[key] = recipe
    # np.save("recipe_emb_test.npy", data_emb)  # 将生成的向量保存在字典文件中
    return data_emb


def test_data():
    print("test_data")
    result, name, id, t = data_split(get_data_test())
    data_emb = test_emb(result)
    recipe_emb = np.load("recipe_emb.npy", allow_pickle=True)
    print(recipe_emb)
    emb_recipe = recipe_emb.item()
    similarly = {}
    for key in data_emb:
        similarly[key] = top_n_cosine_similarity(data_emb[key], emb_recipe, 30, norm=True)
        # print(similarly[key])
    # np.save("similarly.npy", similarly)
    # similar = np.load("./similarly.npy", allow_pickle=True)
    # similar_test = similar.item()
    js = json.dumps(similarly)
    file = open('test.txt', 'w', encoding="UTF-8-sig")  # 用pandas读写会产生无用的转义字符引起报错，所以采用json读写
    file.write(js)
    file.close()


if __name__ == "__main__":
    test_data()
