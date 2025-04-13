import json
import torch
from torch.utils.data import Dataset, DataLoader
from model.model_def import CustomTransformer
from tokenizers import Tokenizer
import os
from tqdm import tqdm

# ====== CONFIG ======
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 5
LR = 3e-4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ====== LOAD TOKENIZER ======
tokenizer = Tokenizer.from_file("tokenizer/custom_tokenizer.json")
vocab_size = tokenizer.get_vocab_size()

# ====== CUSTOM DATASET ======
class DialogDataset(Dataset):
    def __init__(self, data_path):
        with open(data_path, 'r') as f:
            self.pairs = [json.loads(line.strip()) for line in f]

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        pair = self.pairs[idx]
        text = pair["prompt"] + " [SEP] " + pair["response"]
        tokens = tokenizer.encode(text).ids[:MAX_LEN]
        pad_len = MAX_LEN - len(tokens)
        input_ids = tokens + [0] * pad_len
        input_tensor = torch.tensor(input_ids[:-1])    # input
        target_tensor = torch.tensor(input_ids[1:])    # target is next token
        return input_tensor, target_tensor

# ====== LOAD DATA ======
dataset = DialogDataset("data/dialogue_pairs.json")
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# ====== MODEL SETUP ======
model = CustomTransformer(vocab_size=vocab_size).to(DEVICE)
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
loss_fn = torch.nn.CrossEntropyLoss()

# ====== TRAIN LOOP ======
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    loop = tqdm(loader, desc=f"Epoch {epoch+1}")
    for batch in loop:
        inputs, targets = [b.to(DEVICE) for b in batch]
        outputs = model(inputs)  # shape: (batch, seq, vocab)

        # reshape for loss: (batch
