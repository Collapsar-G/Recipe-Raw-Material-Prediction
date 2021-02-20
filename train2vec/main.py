from train import train_data
from test import test_data
from ans import ans_data


def summary():
    print("summary")
    train_data()
    test_data()
    ans_data()
    print("train2emb模型运行完成")


if __name__ == "__main__":
    summary()
