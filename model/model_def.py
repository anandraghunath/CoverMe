import torch
import torch.nn as nn

class CustomTransformer(nn.Module):
    def __init__(self, vocab_size, emb_size=256, n_heads=4, n_layers=4, max_len=128):
        super().__init__()

        self.token_emb = nn.Embedding(vocab_size, emb_size)
        self.pos_emb = nn.Parameter(torch.randn(1, max_len, emb_size))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=emb_size,
            nhead=n_heads,
            dim_feedforward=1024,
            dropout=0.1,
            activation='relu'
        )

        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.fc_out = nn.Linear(emb_size, vocab_size)

    def forward(self, x):
        # x shape: (batch_size, seq_len)
        seq_len = x.size(1)

        # Embed tokens and add positional embeddings
        x = self.token_emb(x) + self.pos_emb[:, :seq_len]

        # Transformer expects (seq_len, batch_size, emb_size)
        x = x.transpose(0, 1)

        # Run through transformer encoder
        x = self.transformer(x)

        # Transpose back and run through output layer
        x = x.transpose(0, 1)  # (batch_size, seq_len, emb_size)
        return self.fc_out(x)
