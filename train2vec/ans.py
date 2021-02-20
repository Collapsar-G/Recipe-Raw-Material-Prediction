#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/16 19:32

"""生成最后的结果"""

__author__ = 'Collapsar-G'

import math

import numpy as np
from test import data_split as test_data_split, get_data_test
from getdata import data_read as train_data_read, data_split as train_data_split
import re
from pattern3.text.en import singularize
import json

material_index = {}  # 食材的标号 例如:{eggs:0,...}
material_sum = {}  # 对应食材标号的食材质量总和
material_count = {}
material_evg = {}
material_error = []
material_th = {}


def get_material_information(data):
    index = 0
    # for recipe in data:  # 数据预处理
    # for i in range(len(data)):
    #     recipe = data[i]
    for key in data:
        recipe = data[key]
        for material in recipe:
            temp = 0
            sav = recipe[material]
            recipe[material] = recipe[material].lower()
            # print(recipe[material], material)
            if recipe[material]:
                if 'tbsp' in recipe[material]:
                    if 'honey' in material:
                        temp = float(re.sub('tbsp', '', recipe[material])) * 30
                    else:
                        temp = float(re.sub('tbsp', '', recipe[material])) * 15
                elif 'tsp' in recipe[material]:
                    temp = float(re.sub('tsp', '', recipe[material])) * 6
                elif 'tbs' in recipe[material]:
                    temp = float(re.sub('tbs', '', recipe[material])) * 15
                elif 'tablespoons' in recipe[material]:
                    temp = float(re.sub('tablespoons', '', recipe[material])) * 15
                elif 'tablespoon' in recipe[material]:
                    temp = float(re.sub('tablespoon', '', recipe[material])) * 15
                elif 'teaspoon' in recipe[material]:
                    temp = float(re.sub('teaspoon', '', recipe[material])) * 5
                elif 'dozen' in recipe[material]:
                    temp = float(re.sub('dozen', '', recipe[material])) * 12
                elif 'oz' in recipe[material]:
                    temp = float(re.sub('oz', '', recipe[material])) * 29.57
                elif 'can' in recipe[material]:
                    temp = float(re.sub('can', '', recipe[material])) * 446.25
                elif 'lbs' in recipe[material]:
                    temp = float(re.sub('lbs', '', recipe[material])) * 453.59
                elif 'lb' in recipe[material]:
                    temp = float(re.sub('lb', '', recipe[material])) * 453.59
                elif 'cups' in recipe[material]:
                    temp = float(re.sub('cups', '', recipe[material])) * 180
                elif 'cup' in recipe[material]:
                    temp = float(re.sub('cup', '', recipe[material])) * 180
                elif 'ml' in recipe[material]:
                    temp = float(re.sub('ml', '', recipe[material]))
                elif 'tbls' in recipe[material]:
                    temp = float(re.sub('tbls', '', recipe[material])) * 15
                elif 'l' in recipe[material]:
                    temp = float(re.sub('l', '', recipe[material])) * 1000
                elif 'jgger' in recipe[material]:
                    temp = float(re.sub('jgger', '', recipe[material])) * 45
                elif 'jigger' in recipe[material]:
                    temp = float(re.sub('jigger', '', recipe[material])) * 45
                elif 'g' in recipe[material]:
                    temp = float(re.sub('g', '', recipe[material]))
                elif re.search('c$', recipe[material]):
                    temp = float(re.sub('c', '', recipe[material])) * 210
                elif re.search('t$', recipe[material]):
                    if re.search('T$', sav):
                        temp = float(re.sub('T', '', sav)) * 15
                    else:
                        recipe[material] = ''
                        continue
                elif '¾' in recipe[material]:
                    temp = 0
                elif '½' in recipe[material]:
                    temp = 0
                elif '1–1' in recipe[material]:
                    temp = 0
                elif '¼' in recipe[material]:
                    temp = 0
                elif 'to6' in recipe[material]:
                    temp = 0
                elif '0ne' in recipe[material]:
                    temp = 0
                else:
                    temp = float(recipe[material])
            if recipe[material]:
                recipe[material] = temp
            if material not in material_index:
                material_index[material] = [(key, temp)]
                index += 1
                material_sum[material] = temp
                material_count[material] = 1.
            else:
                material_index[material].append((key, temp))
                material_sum[material] += temp
                material_count[material] += 1.
    for key in material_count:
        material_evg[key] = material_sum[key] / material_count[key]
        sum = 0
        for material in material_index[key]:
            sum += (material[1] - material_evg[key]) ** 2
        material_th[key] = math.sqrt(sum)
    print(index)
    return data, material_index, material_sum, material_evg, material_th, material_count


def clean_data(data, material_index, material_sum, material_evg, material_th, material_count):
    for key in material_index:
        for material in material_index[key]:
            if material[1] > 1000:
                if (material_evg[key] - material_th[key] * 3) <= material[1] <= (
                        material_evg[key] + material_th[key] * 3):
                    material_error.append(material[0])
                    material_sum[key] -= material[1]
                    material_count[key] -= 1
    for key in material_sum:
        if material_count[key] != 0:
            material_evg[key] = material_sum[key] / material_count[key]
        else:
            material_evg[key] = 0
    return material_sum, material_error

def ans_data():
    print("ans_data")
    file = open('test.txt', 'r', encoding="UTF-8-sig")
    js = file.read()
    similar_test = json.loads(js)
    print(len(similar_test.keys()))
    file.close()
    data_test, name_test, id_test = test_data_split(get_data_test())
    data_train, name_train, id_train = train_data_split(train_data_read())
    data_train, material_index, material_sum, material_evg, material_th, material_count = get_material_information(
        data_train)
    material_sum, material_error = clean_data(data_train, material_index, material_sum, material_evg, material_th,
                                              material_count)
    similar_dec = {}
    for key in similar_test:
        temp = []
        for i in range(len(similar_test[key])):
            if (similar_test[key][i][1] >= 0.9) & (similar_test[key][i][0] not in material_error):
                temp.append(similar_test[key][i][0])
        similar_dec[key] = temp
    ans = []
    for key in data_test:
        recipe = str(key) + "," + str(id_test[key])
        for ingredient in data_test[key]:
            temp = []
            flag = False
            for i in range(len(similar_dec[key])):
                if ingredient in data_train[similar_dec[key][i]].keys():
                    if data_train[similar_dec[key][i]][ingredient] != '':
                        flag = True
                        temp.append(int(data_train[similar_dec[key][i]][ingredient]))

            if flag & len(temp) != 0:

                data_test[key][ingredient] = np.mean(temp)
            # elif ingredient in material_evg.keys():
            #     data_test[key][ingredient] = material_evg[ingredient]
            else:
                try:
                    data_test[key][ingredient] = material_evg[ingredient]
                except:
                    data_test[key][ingredient] = "Null"
            recipe += ',' + str(name_test[key][ingredient]) + "#" + str(data_test[key][ingredient])

        ans.append(recipe)
    file = open('./data/recipe2.csv', 'a', encoding='utf-8')
    for i in range(len(ans)):
        s = ans[i]
        s = s + '\n'  # 去除单引号，逗号，每行末尾追加换行符
        file.write(s)
    file.close()
    print("保存文件成功")


if __name__ == "__main__":
   ans_data()