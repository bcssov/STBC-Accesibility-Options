import nt
import string_extensions
import string

autoloadModule = "Custom.EarlyLoad.Autoload."
autoloadPath = string_extensions.strip(string.replace("scripts\\" + autoloadModule, ".", "\\"), "\\")


def Load():
    files = nt.listdir(autoloadPath)
    files.sort()

    processed = []

    for file in files:
        values = string.split(file, ".")
        if len(values) < 2:
            continue

        extension = string.lower(values[-1])
        fileName = string.join(values[:-1], ".")
        if string.lower(fileName) == "__init__":
            continue

        if (extension == "py" or extension == "pyc") and fileName not in processed:
            processed.append(fileName)
            # noinspection PyBroadException
            try:
                # Just load
                __import__(autoloadModule + fileName)
            except:
                continue
