import requests
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime

# Kết nối tới Cassandra
auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
cluster = Cluster(['127.0.0.1'], port=9042, auth_provider=auth_provider)
session = cluster.connect()

# Tạo keyspace và bảng (nếu chưa có)
session.execute("""
CREATE KEYSPACE IF NOT EXISTS mykeyspace
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }
""")
session.set_keyspace('mykeyspace')

session.execute("""
CREATE TABLE IF NOT EXISTS web_data (
    id text PRIMARY KEY,
    title text,
    url text,
    content text,
    tstamp timestamp,
    anchor list<text>,
    digest text,
    boost float,
    version bigint
)
""")

# Lấy dữ liệu từ Solr API
solr_url = 'http://localhost:8983/solr/nutch/select?q=*:*&q.op=OR&indent=true&wt=json&start=0&rows=10'
response = requests.get(solr_url)
data = response.json()

# Chèn dữ liệu vào Cassandra
insert_query = session.prepare("""
INSERT INTO web_data (id, title, url, content, tstamp, anchor, digest, boost, version)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""")

for doc in data['response']['docs']:
    tstamp = datetime.strptime(doc['tstamp'], '%Y-%m-%dT%H:%M:%S.%fZ') if 'tstamp' in doc else None
    session.execute(insert_query, (
        doc['id'],
        doc.get('title', ''),
        doc.get('url', ''),
        doc.get('content', ''),
        tstamp,
        doc.get('anchor', []),
        doc.get('digest', ''),
        doc.get('boost', 0.0),
        doc.get('_version_', 0)
    ))

print("Dữ liệu đã được chèn vào Cassandra thành công.")
