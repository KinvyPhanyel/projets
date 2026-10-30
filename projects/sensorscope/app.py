"""Détecter des anomalies par médiane et écart absolu médian dans une série de capteurs."""
import argparse, csv, json, math, statistics

def analyze(values,threshold=3.5):
    if len(values)<3 or any(not math.isfinite(x) for x in values): raise ValueError('Au moins trois valeurs finies requises')
    median=statistics.median(values); mad=statistics.median(abs(x-median) for x in values)
    points=[]
    for index,value in enumerate(values):
        score=0.67448975*abs(value-median)/mad if mad else None
        anomalous=score>threshold if score is not None else value!=median
        points.append({'index':index,'value':value,'score':round(score,4) if score is not None else None,'anomaly':anomalous})
    return {'median':median,'mad':mad,'zero_mad_policy':'flag values different from median','points':points}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('file'); p.add_argument('--threshold',type=float,default=3.5); a=p.parse_args()
    if not math.isfinite(a.threshold) or a.threshold<=0: p.error('Seuil positif fini requis')
    with open(a.file,newline='') as f: values=[float(r['value']) for r in csv.DictReader(f)]
    print(json.dumps(analyze(values,a.threshold),indent=2))
if __name__=='__main__': main()
