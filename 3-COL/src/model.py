import torch
import torch.nn.functional as F
from torch.nn import Linear
from torch_geometric import edge_index
from torch_geometric.nn import GCNConv, global_add_pool

class GNNModel(torch.nn.Module):
    def __init__(self):
        super(GNNModel, self).__init__()
        # punto di partenza
        dim_input = 1
        dim_hidden = 64 # numero arbitrario di neuroni
        # creazione dei layer di comunicazione
        self.conv_one = GCNConv(in_channels=dim_input, out_channels=dim_hidden)
        self.conv_two = GCNConv(in_channels=dim_hidden, out_channels=dim_hidden)
        self.conv_three = GCNConv(in_channels=dim_hidden, out_channels=dim_hidden)
        self.conv_four = GCNConv(in_channels=dim_hidden, out_channels=dim_hidden)
        # creazione del layer di classificazione
        self.classifier = Linear(in_features=dim_hidden, out_features=1)

    def forward(self, data):
        x = data.x
        edge_index = data.edge_index
        batch = data.batch

        x = self.conv_one(x, edge_index)
        x = self.conv_two(x, edge_index)
        x = self.conv_three(x, edge_index)
        x = self.conv_four(x, edge_index)
        x = global_add_pool(x, batch)

        x = self.classifier(x)

        return x