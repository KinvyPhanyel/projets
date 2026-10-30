"""Indexer des documents locaux et classer les résultats avec un score TF-IDF."""

import argparse, collections, json, math, re
from pathlib import Path


def tokens(text):
    return re.findall(r"[^\W_]+", text.lower(), re.UNICODE)


def search(directory, query, limit=5):
    docs = {
        str(p): collections.Counter(tokens(p.read_text(encoding="utf-8")))
        for p in sorted(Path(directory).rglob("*.txt"))
        if p.is_file() and not p.is_symlink()
    }
    if not docs:
        return []
    terms = set(tokens(query))
    result = []
    for name, counts in docs.items():
        size = sum(counts.values()) or 1
        score = 0
        for term in terms:
            df = sum(term in d for d in docs.values())
            score += counts[term] / size * (math.log((1 + len(docs)) / (1 + df)) + 1)
        if score > 0:
            result.append({"document": name, "score": round(score, 6)})
    return sorted(result, key=lambda r: (-r["score"], r["document"]))[:limit]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=5)
    a = p.parse_args()
    if a.limit < 1:
        p.error("limit doit être positif")
    print(json.dumps(search(a.directory, a.query, a.limit), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
