from tokenizers import Tokenizer, models, trainers, pre_tokenizers
import os

# File paths
corpus_path = "data/corpus.txt"
save_dir = "tokenizer"
vocab_size = 8000

# Step 1: Initialize a WordPiece tokenizer
tokenizer = Tokenizer(models.WordPiece(unk_token="[UNK]"))
tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()

# Step 2: Set up the trainer
trainer = trainers.WordPieceTrainer(
    vocab_size=vocab_size,
    special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
)

# Step 3: Train tokenizer
tokenizer.train([corpus_path], trainer)

# Step 4: Save tokenizer
os.makedirs(save_dir, exist_ok=True)
tokenizer.save(os.path.join(save_dir, "custom_tokenizer.json"))

print(f"✅ Tokenizer trained and saved to {save_dir}/custom_tokenizer.json")
