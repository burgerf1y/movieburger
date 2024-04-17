import torch
import torch.nn as nn
import torch.nn.functional as f

class DNN(torch.nn.Module):
    def __init__(self, hidden_size=500, dropout=0):
        super(DNN, self).__init__()
        self.fc1 = nn.Linear(250,hidden_size)
        self.fc2 = nn.Linear(hidden_size,hidden_size)
        self.fc3 = nn.Linear(hidden_size,250)
        self.dropout = nn.Dropout(dropout, inplace=False)
    
    def forward(self, x):
        x = self.fc1(self.dropout(x))
        x = f.leaky_relu(x)
        x = self.fc2(self.dropout(x))
        x = f.leaky_relu(x)
        x = self.fc3(self.dropout(x))
        return x