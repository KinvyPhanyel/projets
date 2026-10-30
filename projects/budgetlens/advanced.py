"""Budget mensuel avec revenus, remboursements, plafonds et projection à date."""

from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
import calendar
import json


def amount(value):
    try:
        n = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("Montant numérique requis") from error
    if not n.is_finite() or n < 0 or n.as_tuple().exponent < -2:
        raise ValueError("Montant positif avec au plus deux décimales requis")
    return n


def monthly(transactions, budgets, as_of):
    today = date.fromisoformat(as_of)
    expenses = defaultdict(Decimal)
    income = Decimal(0)
    included = 0
    limits = {k: amount(v) for k, v in budgets.items()}
    for row in transactions:
        day = date.fromisoformat(row["date"])
        value = amount(row["amount"])
        kind = row["kind"]
        if kind not in ("expense", "refund", "income") or not row.get("category"):
            raise ValueError("Transaction invalide")
        if day.year != today.year or day.month != today.month or day > today:
            continue
        included += 1
        if kind == "income":
            income += value
        else:
            expenses[row["category"]] += value if kind == "expense" else -value
    days = calendar.monthrange(today.year, today.month)[1]
    report = []
    for category in sorted(set(expenses) | set(limits)):
        spent = expenses[category]
        limit = limits.get(category)
        projected = (spent * days / today.day).quantize(Decimal("0.01"))
        report.append(
            {
                "category": category,
                "net_spent": str(spent),
                "limit": str(limit) if limit is not None else None,
                "remaining": str(limit - spent) if limit is not None else None,
                "projected_month_end": str(projected),
                "over_budget": limit is not None and spent > limit,
            }
        )
    total = sum(expenses.values(), Decimal(0))
    return {
        "as_of": as_of,
        "included_transactions": included,
        "income": str(income),
        "net_expenses": str(total),
        "cash_flow": str(income - total),
        "categories": report,
        "projection_assumption": "constant average daily spending",
    }


def run(request, db=":memory:"):
    return monthly(request["transactions"], request["budgets"], request["as_of"])


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
