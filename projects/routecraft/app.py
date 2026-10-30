"""Trouver un chemin de coût minimal avec l’algorithme de Dijkstra."""
import argparse, heapq, json, math

def shortest(graph,start,end):
    if start not in graph or end not in graph: raise ValueError('Sommet inconnu')
    for edges in graph.values():
        for target,weight in edges.items():
            if target not in graph or not isinstance(weight,(float,int)) or not math.isfinite(weight) or weight<0: raise ValueError('Arête invalide ou poids négatif')
    distances={start:0}; previous={}; queue=[(0,start)]
    while queue:
        cost,node=heapq.heappop(queue)
        if cost!=distances[node]: continue
        if node==end:
            path=[end]
            while path[-1]!=start: path.append(previous[path[-1]])
            return {'cost':cost,'path':list(reversed(path))}
        for neighbor,weight in graph[node].items():
            candidate=cost+weight
            if candidate<distances.get(neighbor,float('inf')):
                distances[neighbor]=candidate; previous[neighbor]=node; heapq.heappush(queue,(candidate,neighbor))
    return {'cost':None,'path':[]}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('file'); p.add_argument('start'); p.add_argument('end'); a=p.parse_args()
    with open(a.file) as f: graph=json.load(f)
    print(json.dumps(shortest(graph,a.start,a.end),indent=2))
if __name__=='__main__': main()
