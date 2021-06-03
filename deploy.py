##################################
# Deploy an app to DonWeb server #
##################################

import os
import sys
import shutil
from utils.generics import render_file

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
    print("\t- Remember to have installed gunicorn inside your virtual environment")
    print("\t- Remember to have installed SuperVisor")
    print("\t- Remember to have installed nginx")
    print("\t- Please check that port " + params["ext_port"] + " is open")
    print("\t- Please check that port " + params["ext_port"] + " is not being used for another app")
    print("\t- Please check that port " + params["int_port"] + " is not being used for another app")
    print("\nThanks for playing around with me. Sometimes I feel so alone :D\n")


def generate_deploy_file(file_name):
    parameters = {}
    print("You may need to answer some questions:")
    parameters["framework"] = input("- What is the framework of your pp? [django|flask]: ")
    parameters["app_name"] = input("- What is the name of your app? (no spaces): ")
    parameters["base_dir"] = input("- What is the base directory for your app (/ at the end): ")
    parameters["int_port"] = input("- Which internal port you want to use for your app: ")
    parameters["ext_port"] = input("- Which external port you want to use for your app: ")
    parameters["workers"] = input("- How many workers do you want to assign the supervisor: ")

    if parameters["framework"] == "flask":
        parameters["app_module"] = input("- What is the name of the app modulo (only Flask): ")
        parameters["app_object_name"] = input("- What is the name of the App object (only Flask): ")

    texto = "##########################################\n"
    texto += "# Deployment File for " + parameters['app_name'] + "\n"
    texto += "##########################################\n\n"

    for key in parameters.keys():
        texto += key + " : " + parameters[key] + '\n'

    texto += "\n\n#################\n#END OF CONFIG FILE\n#################"

    with open(file_name, "w") as f:
        f.write(texto)


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
            key, value = line.split(":", 1) or None
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


def undeploy(file_name):

    app_name = None

    with open(file_name, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if ':' in line and line[0] != '#':
            key, value = line.split(":", 1)
            if key.strip() == "app_name":
                app_name = value.strip()

    if not app_name:
        print("\nThere is no APP_NAME in deploy file. Nothing to undeploy\n")
        exit(1)

    nginx_file = "/etc/nginx/sites-available/" + app_name
    nginx_link = "/etc/nginx/sites-enabled/" + app_name
    supervisor_file = "/etc/supervisor/conf.d/" + app_name + ".conf"

    print("\nRemoving NGINX config file...", end="", flush=True),
    os.system("sudo rm " + nginx_file)
    print("\t[DONE!]")

    print("\nRemoving NGINX config link...", end="", flush=True),
    os.system("sudo rm " + nginx_link)
    print("\t[DONE!]")

    print("\nRemoving SuperVisor config file...", end="", flush=True),
    os.system("sudo rm " + supervisor_file)
    print("\t[DONE!]")

    print("\nRestarting services...", end="", flush=True),
    os.system("sudo systemctl restart nginx.service")
    os.system("sudo nginx -t")
    os.system("sudo supervisorctl reread")
    os.system("sudo supervisorctl update")
    print("\t[DONE!]")


if __name__ == "__main__":

    deploy_file = None

    welcome()

    if len(sys.argv) != 3:
        print("Incorrect number of parameters. Use:")
        print("\nsudo python deploy.sh:")
        print("\t-w <deploy_config_file> ---> to generate a deploy-file for a project")
        print("\t-f <deploy_config_file> ---> to deploy a project from deploy-file")        
        print("\t-u <deploy_config_file> ---> to un-deploy a project (rollback a deployment)")
        print("\n\n")
        exit(2)

    option = sys.argv[1]
    deploy_file = sys.argv[2]

    if option == '-w':
        print("\nGENERATE DEPLOY FILE\n")
        generate_deploy_file(deploy_file)
        print("\nDEPLOY FILE WAS GENERATED")
        exit()
    elif option == '-u':
        print("\nUNDEPLOY PROJECT\n")
        check_if_sudo_mode()
        undeploy(deploy_file)
        print("\nUndeployment finished!")
        exit()

    print("Checking sudo privileges...", end="", flush=True)
    check_if_sudo_mode()
    print("\t\t[DONE!]")

    print("Reading parameters file...", end="", flush=True)
    params = file_input(deploy_file)
    print("\t\t[DONE!]")

    # Check ports redundancy
    if params["int_port"] == params["ext_port"]:
        print("\tWARNING!! Your internal port and external port are the same.\n")
        input("Enter to continue, Ctrl+c to exit... ")

    # FILES
    app_name = params['app_name']
    folder = "deploy_" + app_name + "/"

    # NGINX FILES
    nginx_folder = folder + "nginx/"
    nginx_conf_file = nginx_folder + app_name
    final_nginx_conf_file = "/etc/nginx/sites-available/" + app_name
    final_nginx_conf_file_link = "/etc/nginx/sites-enabled/" + app_name


    # SUPERVISOR FILES
    supervisor_folder = folder + "supervisor/"
    supervisor_conf_file = supervisor_folder + app_name + ".conf"
    final_supervisor_conf_file = "/etc/supervisor/conf.d/" + app_name + ".conf"

    # OTHER FILES
    wsgi_conf_file = folder + "/wsgi.py"
    final_wsgi_conf_file = params["base_dir"] + app_name + "/wsgi.py"

    try:

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
            if os.path.isfile(final_wsgi_conf_file):
                os.remove(final_wsgi_conf_file)
            shutil.copyfile(wsgi_conf_file, final_wsgi_conf_file)
            print("\t\t[DONE!]")

        print("Restarting services...\n", end="", flush=True),
        os.system("sudo systemctl restart nginx.service")
        os.system("sudo nginx -t")
        os.system("sudo supervisorctl reread")
        os.system("sudo supervisorctl update")
        os.system("sudo supervisorctl restart " + app_name)
        print("\t[DONE!]")

    except Exception as e:
        print("\n\n-----------------------\nAn error ocurred:")
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
        print("-----------------------")
        print("\n\n UNDEPLOYING (Rollback).....", end="", flush=True)
        undeploy(deploy_file)
        print("[DONE!]")
    finally:
        say_bye()
