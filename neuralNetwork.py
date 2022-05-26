import random

import matplotlib
import numpy as np
import pandas as pd
import torch
from scipy.stats import pearsonr
from sklearn.model_selection import KFold
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from convert import convertTrainFile
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

from torch import nn
import torch.nn.functional as f



class MLP(nn.Module):

    def __init__(self, in_dim, out_dim):
        super(MLP, self).__init__()
        self.module = nn.Sequential(
            nn.Linear(in_dim,64),
            nn.ReLU(inplace=True),
            nn.Linear(64, out_dim),
        )


    def forward(self, x):
        out = self.module(x)
        out = torch.sigmoid(out)
        return out

def findTrainFeatureMaxMin():
    data = convertTrainFile('files/20220518-126sample31feature.xlsx')

    features = data.columns.values[:-2]

    x_train = []
    for i in range(len(features)):
        x_train.append(data[features[i]].values)

    x_train = np.array(x_train).T

    return x_train.max(axis=0),x_train.min(axis=0)

if  __name__== '__main__':
    matplotlib.rc('font', family='Microsoft YaHei')
    data = convertTrainFile('files/20220518-126sample31feature.xlsx')

    print(data.columns.values)

    features = data.columns.values[:-2]
    print(features)

    count = 0
    selected_features = []
    corrs = []

    for i in range(len(features)):
        x = data[features[i]].values
        y = data['Target'].values
        corr, p = pearsonr(x, y)
        if abs(corr) >= 0:
            corrs.append(corr)
            selected_features.append(features[i])
            count += 1
        else:
            print(corr)
    print(len(selected_features))


    # for feature in data.columns.values[:-2]:
    #     if feature not in selected_features:
    #         del data[feature]

    x_train = []
    for i in range(len(selected_features)):
        x_train.append(data[selected_features[i]].values)

    x_train = np.array(x_train).T

    # X = x_train

    max,min = findTrainFeatureMaxMin()

    X_std = (x_train - min) / (max - min)
    X = X_std * (1 - 0) + 0

    Y1 = np.array(data['Target_Volume'].values)
    Y2 = np.array(data['Target'].values)
    Y = np.vstack((Y1,Y2)).T



    # k-fold test
    # kf = KFold(n_splits=126,shuffle=True)
    # model_best = None
    # best_test_r2 = -np.inf
    # y_test_list = []
    # prediction_test_list  = []
    # train_r2_list = []
    # for train_index, test_index in kf.split(X):
    #     # print("TRAIN:", train_index, "TEST:", test_index)
    #     x_train, x_test = X[train_index], X[test_index]
    #     y_train, y_test = Y[train_index], Y[test_index]
    #
    #     x_train = torch.Tensor(x_train).to(device)
    #     y_train = torch.Tensor(y_train).view(y_train.shape[0], 1).to(device)
    #     x_test = torch.Tensor(x_test).to(device)
    #     y_test = torch.Tensor(y_test).view(y_test.shape[0], 1).to(device)
    #
    #     in_dim = x_train.shape[1]
    #     out_dim = y_train.shape[1]
    #
    #     model = MLP(in_dim=in_dim, out_dim=out_dim).to(device)
    #     loss_fn = nn.MSELoss()
    #     optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    #
    #     epochs = 2000
    #     with tqdm(range(epochs), unit='epoch', total=epochs, desc='Epoch iteration') as epoch:
    #         for ep in epoch:
    #             model.train()
    #             batch_size = 125
    #             step_num = len(x_train) // batch_size
    #             with tqdm(range(step_num),
    #                       unit=' samples',
    #                       total=step_num,
    #                       leave=True,
    #                       desc='Sample Iteration') as tepoch:
    #                 for step in tepoch:
    #                     try:
    #                         x_batch = x_train[step * batch_size:(step * batch_size) + batch_size]
    #                         y_batch = y_train[step * batch_size:(step * batch_size) + batch_size]
    #                     except:
    #                         x_batch = x_train[step * batch_size:]
    #                         y_batch = y_train[step * batch_size:]
    #                     output = model(x_batch)
    #                     loss = loss_fn(output, y_batch)
    #                     optimizer.zero_grad()
    #                     loss.backward()
    #                     optimizer.step()
    #
    #     prediction_test = model(x_test)
    #     prediction_train = model(x_train)
    #
    #
    #     train_r2_list.append(r2_score(y_train.cpu().detach().numpy(),prediction_train.cpu().detach().numpy()))
    #     y_test_list.append(y_test.cpu().detach().numpy()[0])
    #     prediction_test_list.append(prediction_test.cpu().detach().numpy()[0])
    # print(y_test_list)
    # print(prediction_test_list)
    # print('test r2: ',r2_score(y_test_list, prediction_test_list))
    # print('train r2: ',train_r2_list)
    # # print(best_test_r2)
    # quit()
    seed = random.randint(1,1000)
    # seed = 213
    torch.cuda.manual_seed(seed)

    # target1
    x_train,x_test,y_train,y_test = train_test_split(X,Y1,test_size=0.35,random_state=seed)

    x_train = torch.Tensor(x_train).to(device)
    y_train = torch.Tensor(y_train).view(y_train.shape[0],1).to(device)
    x_dev = torch.Tensor(x_test[:20,:]).to(device)
    y_dev = torch.Tensor(y_test[:20]).view(y_test[:20].shape[0],1).to(device)
    x_test1 = torch.Tensor(x_test[20:, :]).to(device)
    y_test1 = torch.Tensor(y_test[20:]).view(y_test[20:].shape[0], 1).to(device)


    in_dim = x_train.shape[1]
    out_dim = y_train.shape[1]

    model = MLP(in_dim=in_dim,out_dim=out_dim).to(device)
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(),lr = 0.0001)
    best_r2_target1 = -np.inf
    best_epoch_target1 = None
    epochs = 30000
    with tqdm(range(epochs),unit= 'epoch',total=epochs,desc='Epoch iteration') as epoch:
        for ep in epoch:
            model.train()
            batch_size = 81
            step_num = len(x_train) // batch_size
            with tqdm(range(step_num),
                      unit=' samples',
                      total=step_num,
                      leave=True,
                      desc='Sample Iteration') as tepoch:
                for step in tepoch:
                    try:
                        x_batch = x_train[step * batch_size:(step * batch_size) + batch_size]
                        y_batch = y_train[step * batch_size:(step * batch_size) + batch_size]
                    except:
                        x_batch = x_train[step * batch_size:]
                        y_batch = y_train[step * batch_size:]
                    output = model(x_batch)
                    loss = loss_fn(output,y_batch)


                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

            model.eval()
            y_hat = model(x_dev)
            test_r2 = r2_score(y_dev.cpu().detach().numpy(), y_hat.cpu().detach().numpy())
            if test_r2 > best_r2_target1:
                best_r2_target1 = test_r2
                best_epoch_target1 = ep+1
                torch.save({'MLP':model.state_dict()},f'checkpoints/best_model_target1.pt')







    # target2
    x_train, x_test, y_train, y_test = train_test_split(X, Y2, test_size=0.35, random_state=seed)

    x_train = torch.Tensor(x_train).to(device)
    y_train = torch.Tensor(y_train).view(y_train.shape[0],1).to(device)
    x_dev = torch.Tensor(x_test[:20,:]).to(device)
    y_dev = torch.Tensor(y_test[:20]).view(y_test[:20].shape[0],1).to(device)
    x_test2 = torch.Tensor(x_test[20:, :]).to(device)
    y_test2 = torch.Tensor(y_test[20:]).view(y_test[20:].shape[0], 1).to(device)

    in_dim = x_train.shape[1]
    out_dim = y_train.shape[1]

    model = MLP(in_dim=in_dim, out_dim=out_dim).to(device)
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    best_r2_target2 = -np.inf
    best_epoch_target2 = None
    epochs = 20000
    with tqdm(range(epochs), unit='epoch', total=epochs, desc='Epoch iteration') as epoch:
        for ep in epoch:
            model.train()
            batch_size = 81
            step_num = len(x_train) // batch_size
            with tqdm(range(step_num),
                      unit=' samples',
                      total=step_num,
                      leave=True,
                      desc='Sample Iteration') as tepoch:
                for step in tepoch:
                    try:
                        x_batch = x_train[step * batch_size:(step * batch_size) + batch_size]
                        y_batch = y_train[step * batch_size:(step * batch_size) + batch_size]
                    except:
                        x_batch = x_train[step * batch_size:]
                        y_batch = y_train[step * batch_size:]
                    output = model(x_batch)
                    loss = loss_fn(output, y_batch)

                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

            model.eval()
            y_hat = model(x_dev)
            test_r2 = r2_score(y_dev.cpu().detach().numpy(), y_hat.cpu().detach().numpy())
            if test_r2 > best_r2_target2:
                best_r2_target2 = test_r2
                best_epoch_target2 = ep+1
                torch.save({'MLP': model.state_dict()}, f'checkpoints/best_model_target2.pt')


    print('best dev r2 for target1: ',best_r2_target1)
    print('best epoch for target1: ',best_epoch_target1)
    print('best dev r2 for target2: ', best_r2_target2)
    print('best epoch for target2: ',best_epoch_target2)
    print('random seed: ',seed)

    model1 = MLP(in_dim=in_dim, out_dim=out_dim).to(device)
    checkpoint = torch.load(f'checkpoints/best_model_target1.pt', map_location=device)
    model1.load_state_dict(checkpoint['MLP'])

    model2 = MLP(in_dim=in_dim, out_dim=out_dim).to(device)
    checkpoint = torch.load(f'checkpoints/best_model_target2.pt', map_location=device)
    model2.load_state_dict(checkpoint['MLP'])

    model1.eval()
    model2.eval()
    y_hat1 = model1(x_test1)
    y_hat2 = model2(x_test2)

    print('best test r2 for target1: ', r2_score(y_test1.cpu().detach().numpy(), y_hat1.cpu().detach().numpy()))
    print('best test r2 for target2: ', r2_score(y_test2.cpu().detach().numpy(), y_hat2.cpu().detach().numpy()))







