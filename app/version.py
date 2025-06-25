from io import open


def read_version(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "0.1.0"


""" It defines the project current version """
__version__ = read_version(".version").strip()

if __name__ == "__main__":
    print(__version__)
