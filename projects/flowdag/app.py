"""Calculer l’ordre d’exécution d’un graphe de tâches et détecter les cycles."""
import argparse, heapq, json

def schedule(graph):
    nodes=set(graph)
    if any(not isinstance(deps,list) for deps in graph.values()): raise ValueError('Les dépendances doivent être des listes')
    unknown={d for deps in graph.values() for d in deps}-nodes
    if unknown: raise ValueError('Tâches inconnues: '+', '.join(sorted(unknown)))
    remaining={n:set(deps) for n,deps in graph.items()}; ready=[n for n,deps in remaining.items() if not deps]; heapq.heapify(ready); result=[]
    while ready:
        n=heapq.heappop(ready); result.append(n)
        for other,deps in remaining.items():
            if n in deps:
                deps.remove(n)
                if not deps: heapq.heappush(ready,other)
    if len(result)!=len(nodes): raise ValueError('Cycle détecté dans le graphe')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('file'); a=p.parse_args()
    with open(a.file) as f: graph=json.load(f)
    print(json.dumps({'order':schedule(graph)},indent=2))
if __name__=='__main__': main()
