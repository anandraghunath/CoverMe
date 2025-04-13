import torch
import torch.nn.functional as F
from model.model_def import CustomTransformer
from tokenizers import Tokenizer

# === CONFIG ===
MODEL_PATH = "model/checkpoints/transformer.pt"
TOKENIZER_PATH = "tokenizer/custom_tokenizer.json"
MAX_LEN = 128
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TOP_K = 50
MAX_GEN_TOKENS = 30

# === Load tokenizer and model ===
tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
vocab_size = tokenizer.get_vocab_size()

model = CustomTransformer(vocab_size)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()

# === Generate Function with Top-K Sampling + Stop Token ===
def generate_reply(prompt):
    input_ids = tokenizer.encode(prompt).ids[:MAX_LEN]
    input_tensor = torch.tensor([input_ids], dtype=torch.long).to(DEVICE)

    for _ in range(MAX_GEN_TOKENS):
        with torch.no_grad():
            logits = model(input_tensor)
        next_token_logits = logits[0, -1, :]  # (vocab,)
        probs = F.softmax(next_token_logits, dim=-1)

        # Top-k sampling
        topk_probs, topk_indices = torch.topk(probs, k=TOP_K)
        next_token_id = topk_indices[torch.multinomial(topk_probs, 1).item()].item()

        if next_token_id == tokenizer.token_to_id("[SEP]"):
            break

        input_tensor = torch.cat([
            input_tensor,
            torch.tensor([[next_token_id]], dtype=torch.long).to(DEVICE)
        ], dim=1)

    decoded = tokenizer.decode(input_tensor[0].tolist())
    return decoded.replace(prompt, "").strip()

# === Interactive loop ===
print("🧠 Type something (type 'exit' to quit)")
while True:
    prompt = input("🗣 You: ")
    if prompt.lower() in ("exit", "quit"):
        break
    response = generate_reply(prompt)
    print("🤖 AI:", response)
