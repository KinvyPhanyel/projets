"""Analyser des dépenses CSV avec des montants décimaux exacts et des plafonds par catégorie."""
import argparse, csv, json
from decimal import Decimal, InvalidOperation

def summarize(rows, budget):
    totals={}
    for row in rows:
        amount=Decimal(row['amount'])
        if not amount.is_finite() or amount<0: raise ValueError('Montant positif fini requis')
        category=row['category'].strip()
        if not category: raise ValueError('Catégorie requise')
        totals[category]=totals.get(category,Decimal(0))+amount
    return [{'category':k,'spent':str(v),'limit':str(budget[k]) if k in budget else None,'over_budget':v>Decimal(str(budget[k])) if k in budget else False} for k,v in sorted(totals.items())]

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('file'); p.add_argument('--budgets',default='budgets.json'); a=p.parse_args()
    with open(a.budgets) as f: budgets=json.load(f)
    with open(a.file,newline='') as f: report=summarize(csv.DictReader(f),budgets)
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
