import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

with open(os.path.join(os.path.dirname(__file__), "../../pyrogram/__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"')
            break

project = "wzgram"
copyright = "2017-present Dan, rjriajul"
author = "Dan, rjriajul"
release = version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "_includes", "Thumbs.db", ".DS_Store", "telegram/base", "telegram/functions", "telegram/types"]

html_theme = "furo"
html_title = "wzgram"
html_baseurl = "https://rjriajul.github.io/wzgram/"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_default_options = {
    "member-order": "bysource",
}
