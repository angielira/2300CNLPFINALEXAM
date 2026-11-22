# Loading packages in Pyodide

- Only the standard library is available at start.
- `pyodide.loadPackage(["nltk", "numpy"])` (JS, low overhead) or `micropip.install()` (Python, PyPI pure-Python wheels and Pyodide-built wheels).
- Loading an official package also loads its dependencies.
- Pyodide itself loads from jsDelivr (e.g. `.../pyodide/v314.0.8/full/pyodide.js`); remote wheel servers need CORS.

## Sources
- https://pyodide.org/en/stable/usage/loading-packages.html
