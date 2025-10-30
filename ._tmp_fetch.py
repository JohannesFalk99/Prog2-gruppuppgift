import urllib.request, json
url = 'http://127.0.0.1:5002/fetch_elpriser?year=2025&month=10&day=30&prisklass=SE3'
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        print('HTTP', r.status)
        data = r.read().decode('utf-8')
        j = json.loads(data)
        print('keys:', list(j.keys()))
        print('sample labels len:', len(j.get('labels') or []))
        print('sample values len:', len(j.get('values') or []))
except Exception as e:
    print('ERR', e)
