# memory.py
import os, json, time
from typing import List, Dict

CONV_DIR = "conversations"
os.makedirs(CONV_DIR, exist_ok=True)

def conv_path(conv_id: str) -> str:
    return os.path.join(CONV_DIR, f"{conv_id}.json")

def load_conversation(conv_id: str) -> Dict:
    path = conv_path(conv_id)
    if not os.path.exists(path):
        return {"id": conv_id, "messages": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_message(conv_id: str, user_q: str, assistant_a: str, docs: List[Dict]):
    conv = load_conversation(conv_id)
    conv["messages"].append({
        "time": int(time.time()),
        "user": user_q,
        "assistant": assistant_a,
        "docs": docs
    })
    with open(conv_path(conv_id), "w", encoding="utf-8") as f:
        json.dump(conv, f, ensure_ascii=False, indent=2)

def list_conversations() -> List[str]:
    return [os.path.splitext(f)[0] for f in os.listdir(CONV_DIR) if f.endswith(".json")]
