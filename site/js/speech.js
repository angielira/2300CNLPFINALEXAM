// Hear it: window.speechSynthesis with Play / Pause / Stop. The text always stays on screen too.
export const speechSupported = () => typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;

let voices = [];
if (speechSupported()) {
  const refresh = () => { voices = window.speechSynthesis.getVoices(); };
  refresh();
  window.speechSynthesis.addEventListener?.("voiceschanged", refresh);
}
function pickVoice() {
  return voices.find((v) => v.lang && v.lang.toLowerCase().startsWith("en-us")) || voices.find((v) => v.lang && v.lang.toLowerCase().startsWith("en")) || null;
}

export function createSpeaker(lines, { onLine = () => {}, onState = () => {} } = {}) {
  const synth = window.speechSynthesis;
  let token = 0, state = "stopped";
  const set = (s) => { state = s; onState(s); };

  function speakFrom(i, t) {
    if (t !== token) return;
    if (i >= lines.length) { onLine(-1); set("stopped"); return; }
    onLine(i);
    const u = new SpeechSynthesisUtterance(lines[i]);
    u.lang = "en-US"; u.rate = 0.95;
    const v = pickVoice(); if (v) u.voice = v;
    u.onend = () => speakFrom(i + 1, t);
    u.onerror = (e) => { if (t === token && e.error !== "canceled" && e.error !== "interrupted") { onLine(-1); set("stopped"); } };
    synth.speak(u);
  }
  return {
    play() {
      if (state === "paused") { synth.resume(); set("playing"); return; }
      synth.cancel(); token++; set("playing"); speakFrom(0, token);
    },
    pause() { if (state === "playing") { synth.pause(); set("paused"); } },
    stop() { token++; synth.cancel(); onLine(-1); set("stopped"); },
    get state() { return state; },
  };
}
export function stopAllSpeech() { if (speechSupported()) { try { window.speechSynthesis.cancel(); } catch { /* ignore */ } } }
window.addEventListener("pagehide", stopAllSpeech);
