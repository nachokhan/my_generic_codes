##################################
# Deploy an app to DonWeb server #
##################################

import os
import shutil
from utils.gernerics import render_file

NGINX_TEMPLATE_FILE = "deployment/nginx"
SUPERVISOR_FLASK_TEMPLATE_FILE = "deployment/flask_supervisor.conf"
SUPERVISOR_DJANGO_TEMPLATE_FILE = "deployment/django_supervisor.conf"
WSGI_FLASK_TEMPLATE_FILE = "deployment/wsgi.py"

required_parameters = [
    "framework",
    "app_name",
    "base_dir",
    "int_port",
    "ext_port",
    "workers",
]

optional_parameters = [
    "app_object_name",
    "app_module"
]


def welcome():
    print("\n--------------------------------------------------\n"
        "Welcome to NADS: Nacho Automatic Deplyment System\n"
        "--------------------------------------------------\n")


def say_bye():
    print("\nDon't go! I'd like to give you some tips....")
    print("\t- Please check that port " + params["ext_port"] + " is open")
    print("\t- Remember to restart nginx:")
    print("\t\t 1) sudo systemctl restart nginx.system")
    print("\t- Remember to update&restart supervisor:")
    print("\t\t 1) sudo supervisorctl reread")
    print("\t\t 2) sudo supervisorctl update")
    print("\t\t 3) sudo supervisorctl restart all")
    print("\nThanks for playing around with me. Sometimes I feel so alone :D\n")


def console_input():
    parameters = {}
    print("First step consist in asking some questions:")
    parameters["framework"] = input("- What is the framework of your pp? [django|flask]: ")
    parameters["app_name"] = input("- What is the name of your app? (no spaces): ")
    parameters["base_dir"] = input("- What is the base directory for your app (/ at the end): ")
    parameters["int_port"] = input("- Which internal port you want to use for your app: ")
    parameters["ext_port"] = input("- Which external port you want to use for your app: ")
    parameters["workers"] = input("- How many workers do you want to assign the supervisor: ")

    return parameters


def file_input(file_name):
    parameters = {}
    with open(file_name, "r") as f:
        lines = f.readlines()

    for line in lines:
        # clean line
        line = line.strip()

        # ignore if its a comment
        if line and line[0] == "#":
            continue
        elif line:
            # take tje key:value pair
            key, value = line.split(":") or None
            key = key.strip()
            value = value.strip()

            # check they belong to the required and optional paramters
            # (avoid save unused parameters)
            if key and value:
                if key in required_parameters or key in optional_parameters:
                    parameters[key] = value

    # if some required parameters isnt thhere... then nerror
    for param in required_parameters:
        if param not in parameters:
            raise KeyError(f"{param} not detected in {file_name}")

    return parameters


def check_if_sudo_mode():
    if os.geteuid() != 0:
        print("\nERROR!: You must run this script with 'sudo' access. Exiting...\n")
        exit()


if __name__ == "__main__":

    welcome()

    print("Checking sudo privileges...", end="", flush=True)
    # check_if_sudo_mode()
    print("\t\t[DONE!]")

    print("Reading parameters file...", end="", flush=True)
    params = file_input("flaskapp.par")
    print("\t\t[DONE!]")

    # FILES
    app_name = params['app_name']
    folder = "deploy_" + app_name + "/"

    # NGINX FILES
    nginx_folder = folder + "nginx/"
    nginx_conf_file = nginx_folder + "nginx"
    final_nginx_conf_file = "/etc/nginx/sites-available/nginx"
    final_nginx_conf_file_link = "/etc/nginx/sites-enabled"
    final_nginx_conf_file = "AAAA/nginx"
    final_nginx_conf_file_link = "AAAA/link/nginx"

    # SUPERVISOR FILES
    supervisor_folder = folder + "supervisor/"
    supervisor_conf_file = supervisor_folder + app_name + ".conf"
    final_supervisor_conf_file = "/etc/supervisor/conf.d/" + app_name + ".conf"
    final_supervisor_conf_file = "AAAA/" + app_name + ".conf"

    # OTHER FILES
    wsgi_conf_file = folder + "/wsgi.py"
    final_wsgi_conf_file = params["base_dir"] + "/wsgi.py"
    final_wsgi_conf_file = "AAAA" + "/wsgi.py"

    print("Creating project folders...", end="", flush=True)
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)
    os.mkdir(nginx_folder)
    os.mkdir(supervisor_folder)
    print("\t\t[DONE!]")

    print("Creating NGINX config file...", end="", flush=True),
    render_file(
        NGINX_TEMPLATE_FILE,
        output_file=nginx_conf_file,
        app_name=params["app_name"],
        app_base_dir=params["base_dir"],
        internal_port=params["int_port"],
        external_port=params["ext_port"],
    )
    print("\t\t[DONE!]")

    # Check which file to use depending on the framework
    supervisor_file = None
    if params["framework"] == "django":
        supervisor_file = SUPERVISOR_DJANGO_TEMPLATE_FILE
    elif params["framework"] == "flask":
        supervisor_file = SUPERVISOR_FLASK_TEMPLATE_FILE

    if not supervisor_file:
        raise RuntimeError("The specified framework is not correct or no framework was specified")

    print("Creating SuperVisor config file...", end="", flush=True),
    render_file(
        supervisor_file,
        output_file=supervisor_conf_file,
        app_name=params["app_name"],
        app_base_dir=params["base_dir"],
        internal_port=params["int_port"],
        external_port=params["ext_port"],
        workers_count=params["workers"],
    )
    print("\t[DONE!]")

    if params["framework"] == "flask":
        print("Creating Flask WSGI file...", end="", flush=True),
        render_file(
            WSGI_FLASK_TEMPLATE_FILE,
            output_file=wsgi_conf_file,
            app_name=params["app_name"],
            app_module=params["app_module"],
            app_object_name=params["app_object_name"],
        )
        print("\t\t[DONE!]")

    print("Copying NGINX config file...", end="", flush=True),
    shutil.copyfile(nginx_conf_file, final_nginx_conf_file)
    print("\t\t[DONE!]")

    print("Linking NGINX config file...", end="", flush=True),
    os.symlink(final_nginx_conf_file, final_nginx_conf_file_link)
    print("\t\t[DONE!]")

    print("Copying SuperVisor config file...", end="", flush=True),
    shutil.copyfile(supervisor_conf_file, final_supervisor_conf_file)
    print("\t[DONE!]")

    if params["framework"] == "flask":
        print("Copying WSGI config file...", end="", flush=True),
        shutil.copyfile(wsgi_conf_file, final_wsgi_conf_file)
        print("\t\t[DONE!]")

    say_bye()
