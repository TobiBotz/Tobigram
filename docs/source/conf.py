import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

with open(os.path.join(os.path.dirname(__file__), "../../pyrogram/__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"')
            break

project = "Tobigram"
copyright = "2017-present Dan, TobiBotz "
author = "Dan, TobiBotz "
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
    "python_socks",
    "uvloop",
]

autosummary_generate = True

napoleon_use_rtype = False
napoleon_use_param = False

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "_includes",
    "Thumbs.db",
    ".DS_Store",
]

html_theme = "furo"
html_title = "Tobigram"
html_baseurl = "https://docs.tobigram.com/"
html_logo = "_static/pyrogram.png"
html_favicon = "_static/pyrogram-icon.png"
html_show_sourcelink = False
html_copy_source = False
html_static_path = ["_static"]
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#404040",
        "color-brand-content": "#93774b",
        "color-brand-visited": "#93774b",
        "color-link": "#93774b",
        "color-link--hover": "#bf431d",
        "color-link--visited": "#93774b",
        "color-highlighted-background": "#e4e0d7",
    },
    "dark_css_variables": {
        "color-brand-primary": "#bfbcb9",
        "color-brand-content": "#b7a280",
        "color-brand-visited": "#b7a280",
        "color-link": "#b7a280",
        "color-link--hover": "#e85823",
        "color-link--visited": "#b7a280",
        "color-highlighted-background": "#323232",
    },
}

html_css_files = [
    "css/all.min.css",
    "css/custom.css",
]
html_js_files = [
    "js/sidebar.js",
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
