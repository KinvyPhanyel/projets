"""Index BM25 sérialisable, filtres lexicaux ET et expressions exactes."""

from collections import Counter, defaultdict
import json
import math
import re


def tokenize(text):
    return re.findall(r"[^\W_]+", text.casefold(), re.UNICODE)


class BM25:
    def __init__(self, documents):
        if not documents or any(not isinstance(v, str) for v in documents.values()):
            raise ValueError("Documents texte requis")
        self.documents = documents
        self.tokens = {k: tokenize(v) for k, v in documents.items()}
        self.lengths = {k: len(v) for k, v in self.tokens.items()}
        self.avg = sum(self.lengths.values()) / len(documents) or 1
        self.postings = defaultdict(dict)
        for name, tokens in self.tokens.items():
            for term, count in Counter(tokens).items():
                self.postings[term][name] = count

    def search(self, query, mode="or", limit=10):
        if mode not in ("or", "and") or type(limit) is not int or limit < 1:
            raise ValueError("Mode ou limite invalides")
        phrases = re.findall(r'"([^"]+)"', query)
        terms = set(tokenize(query))
        if not terms:
            return []
        sets = [set(self.postings.get(term, {})) for term in terms]
        candidates = set.intersection(*sets) if mode == "and" else set.union(*sets)
        results = []
        n = len(self.documents)
        for name in candidates:
            tokens = self.tokens[name]
            if any(
                not any(tokens[i : i + len(p)] == p for i in range(len(tokens) - len(p) + 1))
                for p in [tokenize(x) for x in phrases]
            ):
                continue
            score = 0
            for term in terms:
                posting = self.postings.get(term, {})
                frequency = posting.get(name, 0)
                if frequency:
                    idf = math.log(1 + (n - len(posting) + 0.5) / (len(posting) + 0.5))
                    score += (
                        idf
                        * frequency
                        * 2.2
                        / (frequency + 1.2 * (0.25 + 0.75 * self.lengths[name] / self.avg))
                    )
            results.append(
                {"document": name, "score": round(score, 6), "excerpt": self.documents[name][:160]}
            )
        return sorted(results, key=lambda row: (-row["score"], row["document"]))[:limit]

    def export(self):
        return json.dumps(
            {"version": 1, "documents": self.documents}, ensure_ascii=False, sort_keys=True
        )

    @classmethod
    def restore(cls, text):
        value = json.loads(text)
        if value["version"] != 1:
            raise ValueError("Version d’index inconnue")
        return cls(value["documents"])


def run(request, db=":memory:"):
    index = BM25(request["documents"])
    restored = BM25.restore(index.export())
    return {
        "queries": [
            {"query": q["text"], "results": restored.search(q["text"], q.get("mode", "or"))}
            for q in request["queries"]
        ],
        "index": {
            "documents": len(index.documents),
            "terms": len(index.postings),
            "average_length": index.avg,
        },
    }


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="advanced-sample.json")
    parser.add_argument("--db", default=":memory:")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as file:
            scenario = json.load(file)
        print(json.dumps(run(scenario, db=args.db), indent=2, ensure_ascii=False, allow_nan=False))
    except (ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        raise SystemExit(2)
