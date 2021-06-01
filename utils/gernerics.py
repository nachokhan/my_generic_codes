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


def render_file(text_file, **kargs):
    texto = render_text(text_file, kargs)

    app_name = kargs["app_name"]

    file = text_file.split("/")[-1]
    extension = file.split(".", 1)[1]

    print(f"File: {file}")
    print(f"extension: {extension}")

    file_name = app_name

    if extension:
        file_name += "." + extension

    print(f"File_nameeee: {file_name}")

    with open(file_name, "w") as f:
        f.write(texto)
