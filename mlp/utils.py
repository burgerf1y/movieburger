from torch.utils.data import Dataset, DataLoader
import random
import csv
import torch
import tqdm, itertools
import numpy as np
from torch.cuda.amp import autocast
from torch.nn import MarginRankingLoss
import wandb

class RtDataset(Dataset):
    def __init__(self, rows):
        super(RtDataset,self).__init__()
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        with open('user_rating.csv', encoding = 'utf-8') as csvfile:
            reader = csv.reader(csvfile)
            #res = list(islice(reader, index - 1, index))[1:]
            for row_num, row in enumerate(reader):
                if row_num == index:
                    res = row[1:]
            res = [float(i) for i in res]
            return torch.tensor(res)

def randhandlerating(labels, device):
    avai_indices = torch.nonzero(labels > 0)
    avg = torch.mean(labels[avai_indices])
    random_indices = torch.randperm(avai_indices.size(0))
    sel_indices = avai_indices[random_indices[:avai_indices.size(0)//2]]
    x = torch.empty(250).to(device=device)
    for i in range(250):
        if i in sel_indices:
            x[i] = random.uniform(-0.2, 0.2)
        elif i in avai_indices:
            x[i] = labels[i] - avg
        else:
            x[i] = random.uniform(-0.6, -0.2)
    return x, sel_indices

class ModifiedMarginRankingLoss(torch.nn.Module):
    def __init__(self, device, margin=0.1):
        super(ModifiedMarginRankingLoss, self).__init__()
        self.device = device
        self.margin = margin

    def forward(self, scores, labels, mask):
        loss = torch.zeros(1).to(device=self.device)
        for _i, _j in itertools.combinations(list(range((mask.size(0)))),2):
            i, j = mask[_i], mask[_j]
            if labels[i]-labels[j] == 0:
                continue
            loss_fn = MarginRankingLoss(margin=self.margin*abs((labels[i]-labels[j]).item()))
            sign = torch.tensor([1] if labels[i]>labels[j] else [-1])
            loss += loss_fn(scores[i], scores[j], sign.to(device=self.device))
        return loss*2/(mask.size(0)*(mask.size(0)-1))

def train_model(model, batchSize, trainset, valset, optimizer, scheduler, num_epochs, device, loss_fn):
    train_loader = DataLoader(dataset=trainset, batch_size=batchSize, shuffle=True)
    val_loader = DataLoader(dataset=valset, batch_size=batchSize, shuffle=True)

    train_losses = []
    val_losses = []    

    for epoch in range(0, num_epochs):
        cum_loss = 0.0
        model.train()
        torch.enable_grad()
        for (i, (labels)) in enumerate(tqdm.tqdm(train_loader)):
            labels = labels[0].to(device=device)
            x, mask = randhandlerating(labels, device)
            
            with autocast():
                scores = model(labels)
                loss = loss_fn(scores, labels, mask)
                cum_loss += loss.cpu().detach().item()

            if loss > 0:
                optimizer.zero_grad()
                loss.backward()
                model.float()
                optimizer.step()

            if (((i+1)/round(len(trainset), -2))*100)%10==0 or (i+1)==len(train_loader):
                mystr = "Train-epoch "+ str(epoch) + ", Avg-Loss: "+ str(round(cum_loss/((i+1)*batchSize), 4))
                print(mystr)
                wandb.log({"train-loss": round(cum_loss/((i+1)*batchSize), 4)})
                train_losses.append(round(cum_loss/(i+1), 4))

        cum_loss = 0.0
        model.eval()

        for (i, (labels)) in enumerate(tqdm.tqdm(val_loader)):
            labels = labels[0].to(device=device)
            x, mask = randhandlerating(labels, device)

            with autocast():
                with torch.no_grad():
                    scores = model(x)
                    loss = loss_fn(scores, labels, mask)
                    cum_loss += loss.cpu().detach().item()

        scheduler.step(cum_loss/(i+1))
        val_losses.append(round(cum_loss/(i+1), 4))

        mystr = "Valid-epoch "+ str(epoch) + ", Avg-Loss: "+ str(round(cum_loss/((i+1)*batchSize), 4))
        print(mystr)
        wandb.log({"valid-loss": round(cum_loss/((i+1)*batchSize), 4)})
        if optimizer.param_groups[0]['lr']<1e-7:
            break
    
    return train_losses, val_losses

def evaluate_model(model, test_set, loss_fn, gpu=0):
    cum_loss = 0.0
    best_predict = 0

    model.eval()

    test_loader = DataLoader(dataset=test_set, batch_size=1)

    for (i, (labels)) in enumerate(tqdm.tqdm(test_loader, leave=False)):
        labels = labels[0].to(device=gpu)
        x, mask = randhandlerating(labels, gpu)
        with autocast():
            with torch.no_grad():
                scores = model(x)
                loss = loss_fn(scores, labels, mask)
                cum_loss += loss.cpu().detach().item()
        cur_max, max_index = float('-inf'), -1
        for i in range(250):
            if scores[i] > cur_max and i in mask:
                cur_max, max_index = scores[i], i
        if labels[max_index] == 5:
            best_predict += 1
        
    res = np.array([round(cum_loss/(i+1), 4), round(best_predict/(i+1), 4)], dtype=object)
    return res