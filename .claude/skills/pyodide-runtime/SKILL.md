---
name: pyodide-runtime
description: "Load Pyodide, packages and data files in the browser and call Python from JavaScript. Use for the live Ask HelpMate box."
---

# pyodide-runtime

Used by: frontend-engineer, pyodide-engineer

## Recipe
```js
const pyodide = await loadPyodide();                 // from the jsDelivr CDN script tag
await pyodide.loadPackage(["nltk", "numpy"]);       // official Pyodide packages
// ship NLTK data with the site, then write it into the virtual FS
const files = await (await fetch("data/nltk_manifest.json")).json();
for (const f of files) {
  const buf = new Uint8Array(await (await fetch("nltk_data/" + f)).arrayBuffer());
  pyodide.FS.mkdirTree("/nltk_data/" + f.split("/").slice(0, -1).join("/"));
  pyodide.FS.writeFile("/nltk_data/" + f, buf);
}
pyodide.runPython("import nltk; nltk.data.path.insert(0, '/nltk_data')");
```
- Only the standard library is available until packages are loaded.
- MEMFS is cleared on reload; the browser cache makes later loads faster.
- Consider a Web Worker so the page stays responsive.
