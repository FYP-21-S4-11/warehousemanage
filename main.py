from application import app
import os

if __name__ == '__main__':
    from waitress import serve
    serve(app, debug=True, host="0.0.0.0",  port=8080)