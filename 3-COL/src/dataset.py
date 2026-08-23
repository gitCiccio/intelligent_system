import torch
from torch_geometric.data import Data
from pathlib import Path
from loggers import setup_logger

logger = setup_logger(name="DatasetBuilder")


def convert_and_save_dataset(raw_dataset, save_path="data/3col_dataset.pt"):
    """
    Traduce i grafi raw in Tensori per PyTorch Geometric e li salva su disco.
    """
    pyg_data_list = []

    for item in raw_dataset:
        num_nodes = item['num_nodes']
        edges = item['edges']
        label = item['label']


        # 1. Creare la matrice 'edge_index'.
        # PyG li vuole come due liste separate (lista dei nodi di partenza, lista dei nodi di arrivo).
        source_nodes = []
        target_nodes = []
        for u, v in edges:
            # u -> v
            source_nodes.append(u)
            target_nodes.append(v)
            # v -> u
            source_nodes.append(v)
            target_nodes.append(u)

        # Devi convertire 'edges' in un torch.tensor di tipo long (torch.long)
        edge_index = torch.tensor([source_nodes, target_nodes], dtype=torch.long)

        # 2. Creare le 'Node Features' (x).
        x = torch.ones((num_nodes, 1), dtype=torch.float)

        # 3. Creare la 'Label' (y).
        y = torch.tensor([label], dtype=torch.float)

        # 4. Creare l'oggetto Data:
        data = Data(x = x, edge_index = edge_index, y = y)

        # 5. Aggiungerlo alla lista pyg_data_list
        pyg_data_list.append(data)


    # Salvare su disco.
    # Assicurati che la cartella padre di save_path esista (come abbiamo fatto nel logger)
    log_path = Path(save_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Usa torch.save(pyg_data_list, save_path)
    torch.save(pyg_data_list, save_path)
    logger.info(f"Dataset convertito e salvato in {save_path} con {len(pyg_data_list)} grafi.")