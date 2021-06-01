# This file will be used for FLASK apps.
# Because Django creates its own wsgi.py file

from {{app_module}} import {{app_object_name}} as application

if __name__ == '__main__':
    application.run(debug=False)
