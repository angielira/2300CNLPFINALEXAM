# Pyodide file system

- Default MEMFS is in-memory and lost on reload.
- `pyodide.FS.writeFile(path, data)`, `pyodide.FS.readFile(path)`, `pyodide.FS.mkdirTree(dir)`.
- IDBFS can persist files across reloads (`pyodide.FS.mount(pyodide.FS.filesystems.IDBFS, {}, dir)` + `syncfs`).

## Sources
- https://pyodide.org/en/stable/usage/file-system.html
