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


def render_file(text_file, output_file, **kargs):
    texto = render_text(text_file, **kargs)

    with open(output_file, "w") as f:
        f.write(texto)
