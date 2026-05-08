import math
import re
from collections import Counter
from .ingest import connect

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def retrieve_documents(query: str, limit: int = 4) -> list[dict]:
    q = Counter(tokens(query))
    if not q:
        return []
    docs = []
    with connect() as conn:
        rows = conn.execute("SELECT document_id,file_name,title,body FROM documents").fetchall()
    for row in rows:
        body = row["body"] or ""
        d = Counter(tokens(row["title"] + " " + body))
        dot = sum(q[t] * d[t] for t in q)
        norm = math.sqrt(sum(v * v for v in q.values())) * math.sqrt(sum(v * v for v in d.values()))
        score = dot / norm if norm else 0
        if score:
            snippet = body[:550].replace("\n", " ")
            docs.append({"title": row["title"], "file_name": row["file_name"], "score": round(score, 3), "snippet": snippet})
    return sorted(docs, key=lambda item: item["score"], reverse=True)[:limit]


if __name__ == "__main__":
    print("Testing document retrieval...")

    query = "audience engagement trends in top cities for action and sci-fi genres in 2025"

    results = retrieve_documents(query)

    print(f"Found {len(results)} matching documents\n")

    for doc in results:
        print("=" * 50)
        print("Title:", doc["title"])
        print("File:", doc["file_name"])
        print("Score:", doc["score"])
        print("Snippet:", doc["snippet"][:200])
        print()