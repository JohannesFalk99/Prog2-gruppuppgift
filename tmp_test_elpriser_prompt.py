from application.app import app
c = app.test_client()
r = c.get('/elpriser')
print('status', r.status_code)
print('has_prompt', 'Vi använder cookies'.encode('utf-8') in r.data)
