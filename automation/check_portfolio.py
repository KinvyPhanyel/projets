"""Run representative functional checks, and export reproducible demo results."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]

def module(slug):
    spec = importlib.util.spec_from_file_location(slug, ROOT / 'projects' / slug / 'app.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def expect_error(fn):
    try:
        fn()
    except ValueError:
        return
    raise RuntimeError('Expected ValueError')

def run():
    results = {}
    events = [json.loads(line) for line in (ROOT/'projects/sentinel-log/sample.jsonl').read_text().splitlines()]
    m = module('sentinel-log'); alerts = m.detect(events)
    require(len(alerts) == 1 and alerts[0]['attempts'] == 3, 'Authentication detection')
    require(m.detect(events, 5) == [], 'Threshold behavior')
    results['sentinel-log'] = alerts
    m = module('stockpilot')
    with tempfile.TemporaryDirectory() as tmp:
        db = m.connect(str(Path(tmp)/'stock.db'))
        m.move(db,'keyboard',5); m.move(db,'keyboard',-2)
        expect_error(lambda: m.move(db,'keyboard',-4))
        quantity = db.execute('SELECT quantity FROM products').fetchone()[0]
        require(quantity == 3, 'Stock rollback')
        require(db.execute('SELECT count(*) FROM movements').fetchone()[0] == 2,'Movement audit')
        db.close()
    results['stockpilot'] = {'sku':'keyboard','quantity':quantity,'rejected_overdraft':True}
    m = module('budgetlens')
    report = m.summarize([{'category':'transport','amount':'1500.10'},{'category':'transport','amount':'1000.20'}],{'transport':2000})
    require(report[0]['spent']=='2500.30' and report[0]['over_budget'], 'Decimal budget')
    results['budgetlens'] = report
    m = module('docuindex'); found=m.search(ROOT/'projects/docuindex/documents','sécurité')
    require(len(found)==1 and found[0]['document'].endswith('security.txt'),'Search relevance')
    require(m.search(ROOT/'projects/docuindex/documents','inexistant')==[], 'No-match search')
    results['docuindex'] = [{**item,'document':Path(item['document']).name} for item in found]
    m=module('cleandata')
    import csv
    with (ROOT/'projects/cleandata/sample.csv').open() as f: clean=m.clean(csv.DictReader(f))
    require(clean['counts']=={'accepted':2,'rejected':2},'Data quarantine')
    results['cleandata']=clean
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200 if self.path=='/' else 503); self.end_headers()
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True); worker.start()
    try:
        m=module('pulsewatch'); url=f'http://127.0.0.1:{server.server_port}'
        require(m.probe(url+'/')['healthy'],'HTTP healthy service')
        require(not m.probe(url+'/failure')['healthy'],'HTTP unhealthy service')
    finally:
        server.shutdown(); server.server_close(); worker.join()
    results['pulsewatch']={'healthy_status':200,'unhealthy_status':503,'both_cases_checked':True}
    m=module('flowdag'); order=m.schedule({'report':['validate'],'extract':[],'validate':['extract']})
    require(order==['extract','validate','report'],'DAG ordering')
    expect_error(lambda: m.schedule({'a':['b'],'b':['a']}))
    results['flowdag']={'order':order,'cycle_rejected':True}
    m=module('routecraft'); graph=json.loads((ROOT/'projects/routecraft/sample.json').read_text()); route=m.shortest(graph,'campus','centre')
    require(route=={'cost':6,'path':['campus','gare','centre']},'Shortest path')
    expect_error(lambda:m.shortest({'a':{'b':-1},'b':{}},'a','b'))
    results['routecraft']=route
    m=module('sensorscope'); anomalies=m.analyze([20,21,20,22,21,85,20])
    require([r['index'] for r in anomalies['points'] if r['anomaly']]==[5],'Outlier detection')
    require(m.analyze([1,1,2])['points'][2]['anomaly'],'Zero-MAD behavior')
    results['sensorscope']=anomalies
    m=module('vaultcheck')
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'document.txt'; p.write_text('original'); before=m.manifest(tmp)
        p.write_text('changed'); after=m.manifest(tmp)
        require(before['document.txt']!=after['document.txt'],'Tamper detection')
    results['vaultcheck']={'algorithm':'SHA-256','modification_detected':True}
    return {'status':'passed','projects_checked':len(results),'results':results}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path); args=parser.parse_args()
    result=run(); text=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output: args.output.write_text(text)
    print(text, end='')
