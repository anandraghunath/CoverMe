import torch
from model.model_def import CustomTransformer
from tokenizers import Tokenizer
import torch.nn.functional as F

# Config
MODEL_PATH = "model/checkpoints/transformer.pt"
TOKENIZER_PATH = "tokenizer/custom_tokenizer.json"
MAX_LEN = 128
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load tokenizer and model
tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
vocab_size = tokenizer.get_vocab_size()

model = CustomTransformer(vocab_size=vocab_size)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()

def generate_reply(prompt, max_new_tokens=30):
    input_ids = tokenizer.encode(prompt).ids
    input_ids = input_ids[:MAX_LEN]
    input_tensor = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0).to(DEVICE)

    for _ in range(max_new_tokens):
        with torch.no_grad():
            output = model(input_tensor)
        next_token_logits = output[0, -1, :]
        probs = F.softmax(next_token_logits, dim=-1)
        top_k = 50
        topk_probs, topk_indices = torch.topk(probs, top_k)
        next_token_id = topk_indices[torch.multinomial(topk_probs, 1).item()].item()
        if next_token_id == tokenizer.token_to_id("[SEP]"):
            break
        input_tensor = torch.cat([
            input_tensor,
            torch.tensor([[next_token_id]], dtype=torch.long).to(DEVICE)
        ], dim=1)

        if next_token_id == tokenizer.token_to_id("[SEP]"):
            break

    generated_ids = input_tensor[0].tolist()
    return tokenizer.decode(generated_ids)

# Try it
while True:
    prompt = input("\n🗣 You: ")
    if prompt.lower() in ("exit", "quit"):
        break
    response = generate_reply(prompt)
    print("🤖 AI:", response)
