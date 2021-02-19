from __future__ import print_function
from torch.autograd import Variable

import torch
x = Variable(torch.ones(2, 2), requires_grad = True)
y = x + 2
print(y.grad)

# y 是作为一个操作的结果创建的因此y有一个creator
z = y * y * 3
out = z.mean()
print(z)
# 现在我们来使用反向传播
out.backward()

# out.backward()和操作out.backward(torch.Tensor([1.0]))是等价的
# 在此处输出 d(out)/dx
print(x.grad)