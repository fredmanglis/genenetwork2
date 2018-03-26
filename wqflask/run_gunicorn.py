# Run with gunicorn, see ./bin/genenetwork2 for an example
#
# Run standalone with
#
#   ./bin/genenetwork2 ./etc/default_settings.py -c run_gunicorn.py

# from flask import Flask
# application = Flask(__name__)

print("Starting up Gunicorn process")

from .wqflask import app

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'

@app.route("/gunicorn")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
