# Calling Pyodide from the page

- `const pyodide = await loadPyodide();` then `await pyodide.loadPackage([...])`.
- Only the standard library is available until packages are loaded.
- Use `pyodide.runPython` / `runPythonAsync` and `pyodide.globals` to pass values.

## Sources
- https://pyodide.org/en/stable/usage/loading-packages.html
