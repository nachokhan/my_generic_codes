# This file will be used for FLASK apps.
# Because Django creates its own wsgi.py file

from {{app_module}} import {{app_object_name}}

if __name__ == '__main__':
    {{app_object_name}}.run(debug=False)
