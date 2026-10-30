"""Gérer un stock SQLite avec journal de mouvements et prévention des sorties impossibles."""
import argparse, json, sqlite3

def connect(path):
    db=sqlite3.connect(path)
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript("CREATE TABLE IF NOT EXISTS products(sku TEXT PRIMARY KEY, quantity INTEGER NOT NULL CHECK(quantity>=0)); CREATE TABLE IF NOT EXISTS movements(id INTEGER PRIMARY KEY, sku TEXT REFERENCES products(sku), delta INTEGER NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP);")
    return db

def move(db,sku,delta):
    if not sku.strip() or delta==0: raise ValueError('SKU requis et mouvement non nul')
    with db:
        db.execute('INSERT OR IGNORE INTO products VALUES (?,0)',(sku,))
        current=db.execute('SELECT quantity FROM products WHERE sku=?',(sku,)).fetchone()[0]
        if current+delta<0: raise ValueError('Stock insuffisant')
        db.execute('UPDATE products SET quantity=quantity+? WHERE sku=?',(delta,sku))
        db.execute('INSERT INTO movements(sku,delta) VALUES (?,?)',(sku,delta))

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--db',default='stock.db'); sub=p.add_subparsers(dest='command',required=True)
    m=sub.add_parser('move'); m.add_argument('sku'); m.add_argument('delta',type=int); sub.add_parser('list'); a=p.parse_args()
    with connect(a.db) as db:
        if a.command=='move': move(db,a.sku,a.delta)
        print(json.dumps([dict(zip(['sku','quantity'],r)) for r in db.execute('SELECT sku,quantity FROM products ORDER BY sku')],indent=2))
if __name__=='__main__': main()
