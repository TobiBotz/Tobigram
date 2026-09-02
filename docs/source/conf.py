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
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
]

autodoc_mock_imports = [
    "warpcrypto",
    "tgcrypto",
    "cryptg",
    "pysocks",
    "uvloop",
]

autosummary_generate = True

napoleon_use_rtype = False
napoleon_use_param = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "_includes", "Thumbs.db", ".DS_Store", "telegram/base", "telegram/functions", "telegram/types"]

html_theme = "furo"
html_title = "wzgram"
html_baseurl = "https://wzgram.com/"
html_logo = "../../assets/svg/wzgram-icon.svg"
html_favicon = "../../assets/favicon.svg"
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_default_options = {
    "member-order": "bysource",
}

suppress_warnings = ["image.not_readable"]
