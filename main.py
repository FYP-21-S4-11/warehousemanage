from application import app
import os

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))