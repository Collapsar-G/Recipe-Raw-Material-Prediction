from data_processing import data_split, data_read


def get_all_ingredients(data):  # 获取数据中的全部食材
    ingredients = set()
    for d in data:
        ingredient_list = d.keys()
        for ingredient in ingredient_list:
            ingredients.add(ingredient)
    return ingredients


def get_datas():  # 调用函数读取训练数据
    datas = data_read()
    train_data = data_split(datas)
    return train_data


def embedding():  # 将训练数据转化为embedding
    return


if __name__ == '__main__':
    data = get_datas()
    ingredients = get_all_ingredients(data)
    print(len(ingredients))
