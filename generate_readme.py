import sys
import io
from src.version import __version__

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TEMPLATE_PATH = "./resources/README_template.md"
OUTPUT_PATH = "README.md"


def build_readme():
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = f.read()

        readme = template.replace("{{version}}", __version__)

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(readme)

        print(f"\U00002705 README.md generado con versión {__version__}")

    except FileNotFoundError:
        print(f"\U0001F6AB Archivo de plantilla no encontrado: {TEMPLATE_PATH}")
    except Exception as e:
        print(f"\u26a0️ Error al generar el README: {e}")


if __name__ == "__main__":
    build_readme()
