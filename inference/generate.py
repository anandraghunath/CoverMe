import torch
import torch.nn.functional as F
from model.model_def import CustomTransformer
from tokenizers import Tokenizer
from collections import Counter

# === CONFIG ===
MODEL_PATH = "model/checkpoints/transformer.pt"
TOKENIZER_PATH = "tokenizer/custom_tokenizer.json"
MAX_LEN = 128
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TOP_K = 50
MAX_GEN_TOKENS = 30
REPEAT_PENALTY = 0.7  # reduce likelihood of repeated tokens

# === LOAD MODEL & TOKENIZER ===
tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
vocab_size = tokenizer.get_vocab_size()

model = CustomTransformer(vocab_size)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()

def generate_reply(prompt):
    input_ids = tokenizer.encode(prompt).ids[:MAX_LEN]
    generated_ids = input_ids.copy()

    input_tensor = torch.tensor([input_ids], dtype=torch.long).to(DEVICE)

    for _ in range(MAX_GEN_TOKENS):
        with torch.no_grad():
            logits = model(input_tensor)[0, -1, :]

        # Apply repetition penalty
        for token_id in Counter(generated_ids):
            logits[token_id] *= REPEAT_PENALTY

        probs = F.softmax(logits, dim=-1)
        topk_probs, topk_indices = torch.topk(probs, k=TOP_K)
        next_token_id = topk_indices[torch.multinomial(topk_probs, 1).item()].item()

        if next_token_id == tokenizer.token_to_id("[SEP]"):
            break

        generated_ids.append(next_token_id)
        input_tensor = torch.cat([
            input_tensor,
            torch.tensor([[next_token_id]], dtype=torch.long).to(DEVICE)
        ], dim=1)

    response = tokenizer.decode(generated_ids)
    return response.replace(prompt, "").strip()

# === CHAT LOOP ===
print("🧠 Type something (type 'exit' to quit)")
while True:
    prompt = input("🗣 You: ")
    if prompt.lower() in ("exit", "quit"):
        break
    response = generate_reply(prompt)
    print("🤖 AI:", response)
