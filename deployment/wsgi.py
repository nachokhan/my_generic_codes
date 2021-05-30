# This file will be used for FLASK apps.
# Because Django creates its own wsgi.py file

from flask_app import app

if __name__ == '__main__':
    app.run(debug=False)
