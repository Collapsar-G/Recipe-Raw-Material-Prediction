import csv
from Embedding.config import train_data_path

def data_read():
    train_data = []
    with open(train_data_path, encoding="utf8") as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        # birth_header = next(csv_reader)  # 读取第一行每一列的标题
        for row in csv_reader:  # 将csv 文件中的数据保存到birth_data中
            train_data.append(row)

    # print(train_data)
    return train_data


def data_split(datas):
    result = []
    for data in datas:
        dst = {}
        # print(len(data))
        for index in range(2, len(data)):
            # print(index)
            dec = data[index].split('#')
            dst[dec[0]] = dec[1]
        # print(dst)
        result.append(dst)
    # print(result)
    return result


if __name__ == '__main__':
    datas = data_read()
    train_data = data_split(datas)
    print(train_data)
