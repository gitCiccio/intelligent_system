import os
import random as rnd
import torch
from torch_geometric.loader import DataLoader
from torch.nn import BCEWithLogitsLoss
from torch.optim import Adam

# Import dai tuoi moduli interni
from src.generator import generate_safe_graph, is_3_color
from src.dataset import convert_and_save_dataset
from src.model import GNNModel


def main():
    print("🚀 Avvio della pipeline per la 3-colorabilità...")

    # 1. Generazione del dataset grezzo usando le funzioni di generator.py
    print("Generazione dei grafi con generator.py...")
    raw_dataset = []
    num_samples = 50

    for _ in range(num_samples):
        g_type = rnd.choice(['regular', 'erdos_renyi'])
        n_nodes = rnd.randint(10, 20)

        graph = generate_safe_graph(g_type, n_nodes)
        if graph is not None:
            try:
                is_col = is_3_color(graph)
                label = 1 if is_col else 0

                raw_dataset.append({
                    'num_nodes': graph.number_of_nodes(),
                    'edges': list(graph.edges()),
                    'label': label
                })
            except Exception:
                continue

    print(f"Generati {len(raw_dataset)} grafi validi.")

    # 2. Conversione e salvataggio tramite dataset.py
    dataset_path = "data/3col_dataset.pt"
    print(f"Conversione e salvataggio dei dati in {dataset_path}...")
    convert_and_save_dataset(raw_dataset, save_path=dataset_path)

    # 3. Caricamento del dataset e creazione del DataLoader
    print("Caricamento del dataset PyG e creazione del DataLoader...")
    pyg_data_list = torch.load(dataset_path, weights_only=False)
    loader = DataLoader(pyg_data_list, batch_size=16, shuffle=True)

    # 4. Inizializzazione di Modello, Loss e Optimizer
    print("Inizializzazione della rete GNN e dei parametri di training...")
    model = GNNModel()
    criterion = BCEWithLogitsLoss()
    optimizer = Adam(model.parameters(), lr=0.01)

    # 5. Training Loop corretto nelle dimensioni
    model.train()
    epochs = 50

    print(f"Inizio dell'addestramento per {epochs} epoche...")
    for epoch in range(epochs):
        for batch_data in loader:
            prediction = model(batch_data)

            # CORRETTO: Adattiamo la forma della previsione a quella dell'etichetta y
            loss = criterion(prediction.view_as(batch_data.y), batch_data.y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoca {epoch + 1}/{epochs} - Loss: {loss.item():.4f}")

    print("Pipeline completata con successo! 🎉")


if __name__ == "__main__":
    main()