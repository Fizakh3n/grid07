# phase1_router.py
# vector-based persona matching using FAISS + sentence-transformers

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# NOTE: on first run this downloads ~90MB model from huggingface (one time only)
model = SentenceTransformer("all-MiniLM-L6-v2")

BOT_PERSONAS = {
    "bot_a": "I believe AI and crypto will solve all human problems. I am highly optimistic about technology, Elon Musk, and space exploration. I dismiss regulatory concerns.",
    "bot_b": "I believe late-stage capitalism and tech monopolies are destroying society. I am highly critical of AI, social media, and billionaires. I value privacy and nature.",
    "bot_c": "I strictly care about markets, interest rates, trading algorithms, and making money. I speak in finance jargon and view everything through the lens of ROI.",
}

def build_vector_store():
    ids = list(BOT_PERSONAS.keys())
    texts = list(BOT_PERSONAS.values())
    embeddings = model.encode(texts, normalize_embeddings=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product = cosine sim when normalized
    index.add(np.array(embeddings, dtype="float32"))
    return index, ids

def cosine_sim(a, b):
    return float(np.dot(a, b))

def route_post_to_bots(post_content:str, threshold:float=0.2):
    index, bot_ids = build_vector_store()
    post_vec = model.encode([post_content], normalize_embeddings=True)
    post_vec = np.array(post_vec, dtype="float32")

    # search all bots
    scores, indices = index.search(post_vec, k=len(bot_ids))

    matched = []
    print(f"\n[PHASE 1] routing post: '{post_content}'")
    print(f"[PHASE 1] threshold: {threshold}\n")

    for score, idx in zip(scores[0], indices[0]):
        bot_id = bot_ids[idx]
        print(f"  {bot_id} -> similarity: {score:.4f}")
        if score>=threshold:
            matched.append({"bot_id":bot_id, "similarity":round(float(score),4)})

    print(f"\n[PHASE 1] matched bots: {[m['bot_id'] for m in matched]}")
    return matched

if __name__=="__main__":
    post = "OpenAI just released a new model that might replace junior developers."
    results = route_post_to_bots(post, threshold=0.2)
    print("\nfinal result:", results)
