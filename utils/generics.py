import os


def render_text(text_file, **kargs):

    text = [""]
    new_text = ""
    dictionary = {}

    # Rebuild dictionary with "formed" keys: "{{_key_}}""
    for key in kargs.keys():
        formed_key = "{{" + key + "}}"
        dictionary[formed_key] = kargs[key]

    # read file to render
    if text_file is not None:
        with open(text_file, "r") as f:
            text = f.readlines()

    # replace coincidences
    for line in text:
        for key in dictionary.keys():
            line = line.replace(key, dictionary[key])
        new_text += line

    return new_text


# Renders a file replacing {variables} for it values
def render_file(text_file, output_file, **kargs):
    texto = render_text(text_file, **kargs)

    with open(output_file, "w") as f:
        f.write(texto)


# Gets a list of the "static" fodlers in a project
def get_static_folders(base_dir):
    list_of_static_dirs = []
    list = [x[0] for x in os.walk(base_dir)]
    for el in list:
        if 'env/' not in el:
            if el.split("/")[-1] == "static":
                list_of_static_dirs.append(el)
    return list_of_static_dirs


# Get relative static path
def get_relative_folder(base_dir, folder):
    count = len(base_dir)
    relative = folder[count-1:]
    return relative


if __name__ == "__main__":
    base = "/home/nacho/dev/restoreserva/"
    list = get_static_folders(base)
    for dir in list:
        print(dir + " ---> " + get_relative_folder(base, dir))
