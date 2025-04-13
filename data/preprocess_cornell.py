import json

# File paths for TSV format
lines_path = "data/movie_lines.txt"
convos_path = "data/movie_conversations.txt"
pairs_path = "data/dialogue_pairs.json"
corpus_path = "data/corpus.txt"

# Step 1: Map line ID → text
def load_lines(path):
    id2line = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 5:
                line_id, text = parts[0], parts[4]
                id2line[line_id] = text
    return id2line

# Step 2: Load conversation line ID sequences
def load_conversations(path):
    conversations = []
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                raw_ids = ' '.join(parts[3:])  # handles all remaining parts
                # Fix spacing: ['L194' 'L195'] → ['L194','L195']
                fixed_ids = raw_ids.replace("'", "").replace("[", "").replace("]", "").split()
                line_ids = [f"L{line_num.strip()[1:]}" if not line_num.startswith("L") else line_num for line_num in fixed_ids]
                conversations.append(line_ids)
    return conversations

# Step 3: Extract prompt-response pairs
def extract_pairs(id2line, conversations):
    pairs = []
    for conv in conversations:
        for i in range(len(conv) - 1):
            q = id2line.get(conv[i], "").strip()
            a = id2line.get(conv[i + 1], "").strip()
            if q and a:
                pairs.append({"prompt": q, "response": a})
    return pairs

# Step 4: Save dialogue pairs to JSONL
def save_jsonl(pairs, path):
    with open(path, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair) + "\n")
    print(f"✅ Saved {len(pairs)} prompt-response pairs to {path}")

# Step 5: Save flat text to corpus.txt
def save_corpus(pairs, path):
    with open(path, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(pair["prompt"] + "\n")
            f.write(pair["response"] + "\n")
    print(f"✅ Saved flattened corpus to {path}")

def main():
    print("📥 Loading data...")
    id2line = load_lines(lines_path)
    conversations = load_conversations(convos_path)
    pairs = extract_pairs(id2line, conversations)

    print("💾 Saving outputs...")
    save_jsonl(pairs, pairs_path)
    save_corpus(pairs, corpus_path)

if __name__ == "__main__":
    main()
