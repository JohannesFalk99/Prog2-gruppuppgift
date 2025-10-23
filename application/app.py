#App.py for flask
#__init__.py
from flask import Flask, render_template
from endpoints import route_blueprint

app = Flask(__name__)
app.register_blueprint(route_blueprint)

@app.route('/')
def index():
    return render_template('index.html')

# Map /index and /index.html to the existing index view
app.add_url_rule('/index', endpoint='index', view_func=index)
app.add_url_rule('/index.html', endpoint='index', view_func=index)

#map error pages
app.add_url_rule('/404', endpoint='not_found', view_func=lambda: render_template('404.html'), methods=['GET'])

@app.route('/401')
def unauthorized():
    return render_template('401.html'), 401

@app.route('/500')
def server_error():
    return render_template('500.html'), 500

#tables

@app.route('/tables')
def tables():
    return render_template('tables.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    