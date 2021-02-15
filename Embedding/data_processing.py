import csv
from config import train_data_path
import numpy as np
import re

materials = []
NotIn = []  # 测试集中训练集中没有的
material_index = {}  # 食材的标号 例如:{eggs:0,...}
material_sum = {}  # 对应食材标号的食材质量总和


def data_read():  # 从文件中读取数据
    train_data = []
    with open(train_data_path, encoding="utf8") as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        # birth_header = next(csv_reader)  # 读取第一行每一列的标题
        for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
            train_data.append(row)
            # print(row)

    # print(train_data)
    return train_data


def data_split(datas):  # 将读取的数据处理为字典列表
    result = []
    for data in datas:
        dst = {}
        # print(len(data))
        for index in range(2, len(data)):
            # print(index)
            dec = data[index].split('#')
            if dec[0] not in materials:
                materials.append(dec[0])
            dst[dec[0]] = dec[1]
        # print(dst)
        result.append(dst)
        # print(result)
    return result


def text():
    with open('../recipe3.csv', encoding="utf8") as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        # birth_header = next(csv_reader)  # 读取第一行每一列的标题
        for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
            x = 0
            for item in row:
                x += 1
                if x <= 2:
                    continue
                dec = item.split('#')
                if dec[0] not in materials:
                    NotIn.append(dec[0])
                    # print(dec[0])


def get_material_information(data):  # 获取食材信息
    index = 0
    for recipe in data:  # 数据预处理
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
                        break
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
            # print(temp)
            if material not in material_index:
                material_index[material] = index
                index += 1
                material_sum[material] = temp
            else:
                material_sum[material] += temp
    print(material_sum)


if __name__ == '__main__':
    datas = data_read()
    train_data = data_split(datas)
    get_material_information(train_data)
