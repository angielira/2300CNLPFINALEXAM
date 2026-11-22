# NLTK in the browser

- Pyodide's package list includes nltk (3.9.4 in Pyodide 314.0.8); load it with `pyodide.loadPackage("nltk")`.
- Don't rely on `nltk.download()` in the browser: ship the data files with the site, write them into Pyodide's file system, and add the folder to `nltk.data.path`.

## Sources
- https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- https://pyodide.org/en/stable/usage/file-system.html
