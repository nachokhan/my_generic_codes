##################################
# Deploy an app to DonWeb server #
##################################

import os
from utils.gernerics import render_file

NGINX_TEMPLATE_FILE = "deployment/nginx"

required_parameters = [
    "framework"  # [flask | django]
    "app_name",
    "base_dir",
    "int_port",
    "ext_port",
    "workers",
]

optional_parameters = []


def welcome():
    print("\n--------------------------------------------------\n"
        "Welcome to NADS: Nacho Automatic Deplyment System\n"
        "--------------------------------------------------\n")


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
        print("\nERROR!: You must run this script with 'sudo' access. Exiting... \n")
        exit()


if __name__ == "__main__":
    print("Holis")
    # params = file_input("clicknic.par")

    # check_if_sudo_mode()
    # rendered_nginx_file = render_file(
    #     NGINX_TEMPLATE_FILE,
    #     app_name=params["app_name"],
    #     base_dir=params["base_dir"],
    #     internal_port=params["int_port"],
    #     external_port=params["ext_port"],
    #     workers=params["workers"],
    # )
