/* HelpMate brain worker (Pip). Classic Web Worker: runs Pyodide (NLTK + NumPy) off the main thread.
   Messages in:  {id, type: "init"} | {id, type: "analyze", text}
   Messages out: {id, ok: true, result} | {id, ok: false, error: "plain message"} | {type: "progress", text}
   Everything here is browser-only; Python runs inside Pyodide. spaCy is never used. */
"use strict";

var PYODIDE_VERSION = "v314.0.8";
var PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/" + PYODIDE_VERSION + "/full/pyodide.js";
var SITE_ROOT = new URL("../", self.location.href);   // worker lives in site/js/

var pyodide = null;
var initPromise = null;

/* PY_GLUE is the exact Python the worker runs. tests/test_brain_python_path.py extracts it
   from this file between the markers and runs it, so keep the markers. */
// PY_GLUE_START
var PY_GLUE = [
  "import json, sys",
  "if '/py' not in sys.path:",
  "    sys.path.insert(0, '/py')",
  "from nlp import classifier",
  "_MODEL = json.loads(_model_json)",
  "_NLTK_OK = False",
  "try:",
  "    from nlp import nltk_features",
  "    nltk_features.use_data_dir('/nltk_data')",
  "    _NLTK_OK = True",
  "except Exception:",
  "    nltk_features = None",
  "def helpmate_analyze(text):",
  "    r = classifier.predict_numpy(_MODEL, text)",
  "    mood = {'compound': 0.0, 'frustrated': False, 'reasons': []}",
  "    mood_ok = False",
  "    if _NLTK_OK:",
  "        try:",
  "            m = nltk_features.frustration(text)",
  "            mood = {'compound': float(m['compound']), 'frustrated': bool(m['frustrated']), 'reasons': list(m['reasons'])}",
  "            mood_ok = True",
  "        except Exception:",
  "            pass",
  "    return json.dumps({",
  "        'category': r['category'], 'confidence': float(r['confidence']),",
  "        'probabilities': {k: float(v) for k, v in r['probabilities'].items()},",
  "        'unsure': bool(r['unsure']), 'known_terms': int(r['known_terms']),",
  "        'mood': mood, 'mood_ok': mood_ok,",
  "        'tokenizer': _MODEL.get('tokenizer'),",
  "    })",
  ""
].join("\n");
// PY_GLUE_END

function say(text) { self.postMessage({ type: "progress", text: text }); }

async function fetchOk(url, as) {
  var res = await fetch(url);
  if (!res.ok) { throw new Error("Could not download " + url.pathname.split("/").pop() + " (" + res.status + ")"); }
  return as === "json" ? res.json() : as === "text" ? res.text() : new Uint8Array(await res.arrayBuffer());
}

function writeFile(path, data) {
  var dir = path.split("/").slice(0, -1).join("/");
  if (dir) { pyodide.FS.mkdirTree(dir); }
  pyodide.FS.writeFile(path, data);
}

async function init() {
  if (typeof loadPyodide !== "function") {
    importScripts(PYODIDE_URL);                       // defines loadPyodide
  }
  say("Starting the Python engine...");
  pyodide = await loadPyodide();
  say("Loading the language tools...");
  var pkgs = pyodide.loadPackage(["nltk", "numpy"]);

  var manifestP = fetchOk(new URL("data/nltk_manifest.json", SITE_ROOT), "json");
  var modelP = fetchOk(new URL("data/model.json", SITE_ROOT), "text");
  var manifest = await manifestP;
  var modelText = await modelP;
  await pkgs;

  var dataBase = new URL(manifest.base_url || "nltk_data/", SITE_ROOT);
  var dataRoot = manifest.fs_root || "/nltk_data";
  var pyBase = new URL(manifest.python_base_url || "py/", SITE_ROOT);

  // Python modules first (small), then the NLTK data files. Fetch in parallel.
  var jobs = [];
  (manifest.python_files || []).forEach(function (f) {
    jobs.push(fetchOk(new URL(f, pyBase), "bytes").then(function (b) { writeFile("/py/" + f, b); }));
  });
  (manifest.items || []).forEach(function (f) {
    jobs.push(fetchOk(new URL(f, dataBase), "bytes").then(function (b) { writeFile(dataRoot + "/" + f, b); }));
  });
  await Promise.all(jobs);

  pyodide.globals.set("_model_json", modelText);
  pyodide.runPython(PY_GLUE);
  pyodide.globals.delete("_model_json");

  // Warm-up call: loads stopwords and the VADER lexicon now, and surfaces problems at start-up.
  JSON.parse(pyodide.globals.get("helpmate_analyze")("my printer is not working"));
}

function analyze(text) {
  var fn = pyodide.globals.get("helpmate_analyze");
  var raw;
  try { raw = fn(String(text || "")); } finally { if (fn && fn.destroy) { fn.destroy(); } }
  var r = JSON.parse(raw);
  var both = r.mood_ok;
  return {
    category: r.category,
    confidence: r.confidence,
    probabilities: r.probabilities,
    unsure: r.unsure,
    mood: r.mood,
    library: both ? "Neural network + NLTK" : "Neural network"
  };
}

function messageOf(e) {
  var m = (e && e.message) ? String(e.message) : String(e);
  return m.split("\n").filter(Boolean).pop() || "Something went wrong in the browser engine.";
}

self.onmessage = async function (ev) {
  var msg = ev.data || {};
  try {
    if (msg.type === "init") {
      if (!initPromise) { initPromise = init(); }
      await initPromise;
      self.postMessage({ id: msg.id, ok: true, result: true });
    } else if (msg.type === "analyze") {
      if (!initPromise) { throw new Error("The engine has not started yet."); }
      await initPromise;
      self.postMessage({ id: msg.id, ok: true, result: analyze(msg.text) });
    } else {
      throw new Error("Unknown request.");
    }
  } catch (e) {
    if (msg.type === "init") { initPromise = null; }
    self.postMessage({ id: msg.id, ok: false, error: messageOf(e) });
  }
};
