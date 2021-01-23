from data_processing import data_split, data_read


def get_all_ingredients(data):
    ingredients = set()
    for d in data:
        ingredient_list = d.keys()
        for ingredient in ingredient_list:
            ingredients.add(ingredient)
    return ingredients


def datas2emb():
    datas = data_read()
    train_data = data_split(datas)
    return train_data


def embedding():
    return


if __name__ == '__main__':
    data = datas2emb()
    ingredients = get_all_ingredients(data)
    print(len(ingredients))
