"""Classifieur binaire entièrement local ; apprentissage sans fuite de validation."""

import math
import random


def sigmoid(z):
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    e = math.exp(z)
    return e / (1 + e)


class Logistic:
    def __init__(self, learning_rate=0.1, epochs=500, l2=0.01):
        if (
            not math.isfinite(learning_rate)
            or learning_rate <= 0
            or type(epochs) is not int
            or epochs < 1
            or epochs > 100000
            or not math.isfinite(l2)
            or l2 < 0
        ):
            raise ValueError("Hyperparamètres invalides")
        self.rate = learning_rate
        self.epochs = epochs
        self.l2 = l2

    def fit(self, x, y):
        if not x or len(x) != len(y) or not x[0] or set(y) != {0, 1}:
            raise ValueError("Deux classes et des observations requises")
        width = len(x[0])
        if any(len(row) != width or any(not math.isfinite(v) for v in row) for row in x):
            raise ValueError("Matrice invalide")
        self.mean = [sum(row[j] for row in x) / len(x) for j in range(width)]
        self.scale = [
            math.sqrt(sum((row[j] - self.mean[j]) ** 2 for row in x) / len(x)) or 1
            for j in range(width)
        ]
        z = [[(v - self.mean[j]) / self.scale[j] for j, v in enumerate(row)] for row in x]
        self.weights = [0.0] * width
        self.bias = 0.0
        for _ in range(self.epochs):
            residual = [
                sigmoid(sum(w * v for w, v in zip(self.weights, row)) + self.bias) - label
                for row, label in zip(z, y)
            ]
            for j in range(width):
                gradient = (
                    sum(e * row[j] for e, row in zip(residual, z)) / len(x)
                    + self.l2 * self.weights[j]
                )
                self.weights[j] -= self.rate * gradient
            self.bias -= self.rate * sum(residual) / len(x)
        return self

    def predict_proba(self, x):
        if not hasattr(self, "weights"):
            raise ValueError("Modèle non entraîné")
        result = []
        for row in x:
            if len(row) != len(self.weights) or any(not math.isfinite(v) for v in row):
                raise ValueError("Observation invalide")
            result.append(
                sigmoid(
                    self.bias
                    + sum(
                        w * (v - m) / s
                        for w, v, m, s in zip(self.weights, row, self.mean, self.scale)
                    )
                )
            )
        return result

    def export(self):
        return {"mean": self.mean, "scale": self.scale, "weights": self.weights, "bias": self.bias}


def split(x, y, fraction=0.25, seed=42):
    if not 0 < fraction < 1 or len(x) != len(y) or set(y) != {0, 1}:
        raise ValueError("Séparation invalide")
    rng = random.Random(seed)
    train = []
    test = []
    for label in (0, 1):
        group = [i for i, value in enumerate(y) if value == label]
        if len(group) < 2:
            raise ValueError("Deux exemples par classe au minimum")
        rng.shuffle(group)
        count = max(1, min(len(group) - 1, round(len(group) * fraction)))
        test.extend(group[:count])
        train.extend(group[count:])
    return (
        [x[i] for i in train],
        [y[i] for i in train],
        [x[i] for i in test],
        [y[i] for i in test],
    )


def metrics(y, probabilities):
    if not y or len(y) != len(probabilities):
        raise ValueError("Métriques sans données")
    predicted = [int(p >= 0.5) for p in probabilities]
    tp = sum(a == b == 1 for a, b in zip(y, predicted))
    tn = sum(a == b == 0 for a, b in zip(y, predicted))
    fp = sum(a == 0 and b == 1 for a, b in zip(y, predicted))
    fn = sum(a == 1 and b == 0 for a, b in zip(y, predicted))
    loss = -sum(
        a * math.log(max(1e-15, p)) + (1 - a) * math.log(max(1e-15, 1 - p))
        for a, p in zip(y, probabilities)
    ) / len(y)
    return {
        "accuracy": (tp + tn) / len(y),
        "precision": tp / (tp + fp) if tp + fp else 0,
        "recall": tp / (tp + fn) if tp + fn else 0,
        "log_loss": loss,
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "samples": len(y),
    }


def run(request, db=":memory:"):
    x = request["x"]
    y = request["y"]
    train_x, train_y, test_x, test_y = split(
        x, y, request.get("test_fraction", 0.25), request.get("seed", 42)
    )
    model = Logistic(**request.get("parameters", {})).fit(train_x, train_y)
    probabilities = model.predict_proba(test_x)
    return {
        "train_samples": len(train_y),
        "test": metrics(test_y, probabilities),
        "model": model.export(),
        "probabilities": probabilities,
        "labels": test_y,
    }
