#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/16 19:32

"""模型训练文件"""

__author__ = 'Collapsar-G'

import scipy

from getdata import get_data
import warnings

from utils import data2emb, cosine_similarity, top_n_cosine_similarity
import numpy as np
from numba import jit

warnings.filterwarnings('ignore')
# context = 5
# n = 300

# @jit
# def similaritys_all(vec_list):
#     similaritys = {}
#     for key in vec_list:
#         topn = top_n_cosine_similarity(vec_list[key], vec_list, context + 1, True)
#         similaritys[key] = topn
#         print(topn)
#     return similaritys
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as tud

from collections import Counter
import numpy as np
import random

random.seed(1)
np.random.seed(1)
torch.manual_seed(1)

C = 3  # context window
K = 15  # number of negative samples
epochs = 2
MAX_VOCAB_SIZE = 5076
EMBEDDING_SIZE = 200
batch_size = 32
lr = 0.2

train_data, material_index, material_sum, name, id = get_data()
text = []
for key in train_data:
    for ingredient in train_data[key]:
        text.append(ingredient)

ingredient_dict = dict(Counter(text).most_common(MAX_VOCAB_SIZE + 1))  # 得到食材字典表，key是食材，value是次数

ingredient2idx = {ingredient: i for i, ingredient in enumerate(ingredient_dict.keys())}
idx2ingredient = {i: ingredient for i, ingredient in enumerate(ingredient_dict.keys())}
ingredient_counts = np.array([count for count in ingredient_dict.values()], dtype=np.float32)
ingredient_freqs = ingredient_counts / np.sum(ingredient_counts)
ingredient_freqs = ingredient_freqs ** (3. / 4.)


class IngredientEmbeddingDataset(tud.Dataset):
    def __init__(self, text, ingredient2idx, ingredient_freqs):
        ''' text: a list of ingredients, all text from the training dataset
            ingredient2idx: the dictionary from ingredient to index
            ingredient_freqs: the frequency of each ingredient
        '''
        super(IngredientEmbeddingDataset, self).__init__()  # #通过父类初始化模型，然后重写两个方法
        self.text_encoded = [ingredient2idx.get(ingredient) for ingredient in text]  # 把食材数字化表示。
        self.text_encoded = torch.LongTensor(self.text_encoded)  # nn.Embedding需要传入LongTensor类型
        self.ingredient2idx = ingredient2idx
        self.ingredient_freqs = torch.Tensor(ingredient_freqs)

    def __len__(self):
        return len(self.text_encoded)  # 返回所有食材的总数，即item的总数

    def __getitem__(self, idx):
        """ 这个function返回以下数据用于训练
            - 中心词
            - 这个食材附近的positive ingredient
            - 随机采样的K个食材作为negative ingredient
        """
        center_ingredients = self.text_encoded[idx]  # 取得中心词
        pos_indices = list(range(idx - C, idx)) + list(range(idx + 1, idx + C + 1))  # 先取得中心左右各C个词的索引
        pos_indices = [i % len(self.text_encoded) for i in pos_indices]  # 为了避免索引越界，所以进行取余处理
        pos_ingredients = self.text_encoded[pos_indices]  # tensor(list)

        neg_ingredients = torch.multinomial(self.ingredient_freqs, K * pos_ingredients.shape[0], True)
        # torch.multinomial作用是对self.ingredient_freqs做K * pos_ingredients.shape[0]次取值，输出的是self.ingredient_freqs对应的下标
        # 取样方式采用有放回的采样，并且self.ingredient_freqs数值越大，取样概率越大
        # 每采样一个正确的食材(positive ingredient)，就采样K个错误的食材(negative ingredient)，pos_ingredients.shape[0]是正确食材数量

        # while 循环是为了保证 neg_ingredients中不能包含背景词
        while len(set(pos_indices) & set(neg_ingredients)) > 0:
            neg_ingredients = torch.multinomial(self.ingredient_freqs, K * pos_ingredients.shape[0], True)

        return center_ingredients, pos_ingredients, neg_ingredients


dataset = IngredientEmbeddingDataset(text, ingredient2idx, ingredient_freqs)
dataloader = tud.DataLoader(dataset, batch_size, shuffle=True)


class EmbeddingModel(nn.Module):
    def __init__(self, vocab_size, embed_size):
        super(EmbeddingModel, self).__init__()

        self.vocab_size = vocab_size
        self.embed_size = embed_size

        self.in_embed = nn.Embedding(self.vocab_size, self.embed_size)
        self.out_embed = nn.Embedding(self.vocab_size, self.embed_size)

    def forward(self, input_labels, pos_labels, neg_labels):
        ''' input_labels: center ingredients, [batch_size]
            pos_labels: positive ingredients, [batch_size, (window_size * 2)]
            neg_labels：negative ingredients, [batch_size, (window_size * 2 * K)]

            return: loss, [batch_size]
        '''
        input_embedding = self.in_embed(input_labels)  # [batch_size, embed_size]
        pos_embedding = self.out_embed(pos_labels)  # [batch_size, (window * 2), embed_size]
        neg_embedding = self.out_embed(neg_labels)  # [batch_size, (window * 2 * K), embed_size]

        input_embedding = input_embedding.unsqueeze(2)  # [batch_size, embed_size, 1]

        pos_dot = torch.bmm(pos_embedding, input_embedding)  # [batch_size, (window * 2), 1]
        pos_dot = pos_dot.squeeze(2)  # [batch_size, (window * 2)]

        neg_dot = torch.bmm(neg_embedding, -input_embedding)  # [batch_size, (window * 2 * K), 1]
        neg_dot = neg_dot.squeeze(2)  # batch_size, (window * 2 * K)]

        log_pos = F.logsigmoid(pos_dot).sum(1)  # .sum()结果只为一个数，.sum(1)结果是一维的张量
        log_neg = F.logsigmoid(neg_dot).sum(1)

        loss = log_pos + log_neg

        return -loss

    def input_embedding(self):
        return self.in_embed.weight.detach().cpu().numpy()


model = EmbeddingModel(MAX_VOCAB_SIZE, EMBEDDING_SIZE)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

model.to(device)
for e in range(3):
    for i, (input_labels, pos_labels, neg_labels) in enumerate(dataloader):
        input_labels = input_labels.long().to(device)
        pos_labels = pos_labels.long().to(device)
        neg_labels = neg_labels.long().to(device)

        optimizer.zero_grad()
        loss = model(input_labels, pos_labels, neg_labels).mean()
        loss.backward()

        optimizer.step()

        if i % 100 == 0:
            print('epoch', e, 'iteration', i, loss.item())

embedding_weights = model.input_embedding()
torch.save(model.state_dict(), "embedding-{}.th".format(EMBEDDING_SIZE))


def find_nearest(word):
    index = ingredient2idx[word]
    embedding = embedding_weights[index]
    # cos_dis = np.array([scipy.spatial.distance.cosine(e, embedding) for e in embedding_weights])
    return embedding


result_dict = {}
for key in ingredient_dict.keys():
    result_dict[key] = find_nearest(key)
    np.save("ingredient_emb.npy", result_dict)  # 将生成的向量保存在字典文件中
