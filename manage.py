from application.func.kvs.kvs import Kvs
from application import app

if __name__ == '__main__':
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=True)
