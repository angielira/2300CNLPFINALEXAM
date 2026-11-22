/* HelpMate brain (Pip). Main-thread side of the Pyodide worker.
   import { ready, analyze, onProgress } from "./brain.js";
   ready()   -> Promise<void>; rejects with an Error (plain message) if the engine cannot start.
   analyze() -> Promise<{category, confidence, probabilities, unsure,
                         mood:{compound, frustrated, reasons}, library}>
   library is "Neural network + NLTK" (category by the neural network, mood by NLTK VADER),
   or "Neural network" if the mood step was not available.
   If this rejects, app.js should fall back to the spaCy category_hint and show the "engine failed" notice. */

var LOAD_TIMEOUT_MS = 45000;
var ANALYZE_TIMEOUT_MS = 15000;

var worker = null;
var readyPromise = null;
var nextId = 1;
var pending = new Map();      // id -> {resolve, reject, timer}
var progressHandlers = [];

export function onProgress(fn) { progressHandlers.push(fn); }

function failAll(err) {
  pending.forEach(function (p) { clearTimeout(p.timer); p.reject(err); });
  pending.clear();
}

function stop(err) {
  if (worker) { worker.terminate(); worker = null; }
  readyPromise = null;
  failAll(err);
}

function send(message, timeoutMs, timeoutText) {
  return new Promise(function (resolve, reject) {
    if (!worker) { reject(new Error("The browser engine is not running.")); return; }
    var id = nextId++;
    var timer = setTimeout(function () {
      pending.delete(id);
      reject(new Error(timeoutText));
      if (message.type === "init") { stop(new Error(timeoutText)); }   // a stuck load is not recoverable
    }, timeoutMs);
    pending.set(id, { resolve: resolve, reject: reject, timer: timer });
    worker.postMessage(Object.assign({ id: id }, message));
  });
}

function start() {
  if (typeof Worker === "undefined") {
    return Promise.reject(new Error("This browser cannot run the smart helper."));
  }
  try {
    worker = new Worker(new URL("./brain-worker.js", import.meta.url));   // classic worker
  } catch (e) {
    return Promise.reject(new Error("The smart helper could not start."));
  }
  worker.onmessage = function (ev) {
    var d = ev.data || {};
    if (d.type === "progress") { progressHandlers.forEach(function (f) { try { f(d.text); } catch (e) { /* ignore */ } }); return; }
    var p = pending.get(d.id);
    if (!p) { return; }
    pending.delete(d.id);
    clearTimeout(p.timer);
    if (d.ok) { p.resolve(d.result); } else { p.reject(new Error(d.error || "The smart helper had a problem.")); }
  };
  worker.onerror = function (ev) {
    stop(new Error("The smart helper stopped unexpectedly" + (ev && ev.message ? ": " + ev.message : ".")));
  };
  return send({ type: "init" }, LOAD_TIMEOUT_MS,
    "The smart helper took too long to start.").then(function () { return undefined; });
}

export function ready() {
  if (!readyPromise) {
    var p = start();
    readyPromise = p;
    p.catch(function () {            // allow a clean retry later
      if (readyPromise === p) { stop(new Error("The smart helper is not running.")); }
    });
  }
  return readyPromise;
}

export function analyze(text) {
  return ready().then(function () {
    return send({ type: "analyze", text: String(text == null ? "" : text) }, ANALYZE_TIMEOUT_MS,
      "The smart helper took too long to answer.");
  });
}
