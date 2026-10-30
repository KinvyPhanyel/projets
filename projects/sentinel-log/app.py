"""Détecter les échecs de connexion répétés dans des journaux JSONL."""
import argparse, collections, datetime, json

def detect(events, threshold=3, window=300):
    buckets=collections.defaultdict(collections.deque)
    alerts=[]
    for event in sorted(events, key=lambda x: datetime.datetime.fromisoformat(x['timestamp'].replace('Z','+00:00')).timestamp()):
        if event.get('status') != 'failed': continue
        stamp=datetime.datetime.fromisoformat(event['timestamp'].replace('Z','+00:00')).timestamp()
        key=(event['ip'],event.get('user','unknown'))
        queue=buckets[key]
        while queue and stamp-queue[0]>window: queue.popleft()
        queue.append(stamp)
        if len(queue)==threshold:
            alerts.append({'ip':key[0],'user':key[1],'attempts':len(queue),'timestamp':event['timestamp'],'rule':'repeated_auth_failure'})
    return alerts

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('file'); p.add_argument('--threshold',type=int,default=3); p.add_argument('--window',type=int,default=300); a=p.parse_args()
    if a.threshold<1 or a.window<1: p.error('threshold et window doivent être positifs')
    with open(a.file) as f: events=[json.loads(line) for line in f if line.strip()]
    print(json.dumps(detect(events,a.threshold,a.window),indent=2))
if __name__=='__main__': main()
