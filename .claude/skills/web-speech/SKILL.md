---
name: web-speech
description: "Read HelpMate steps aloud with the browser's Web Speech API (speechSynthesis). Use for the Hear it format."
---

# web-speech

Used by: instructional-designer, frontend-engineer

## Recipe
```js
const synth = window.speechSynthesis;
function speak(text) {
  synth.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "en-US"; u.rate = 0.95;
  synth.speak(u);
}
// Play / Pause / Stop -> speak(), synth.pause(), synth.resume(), synth.cancel()
```
- Voices load asynchronously: refresh the list on `voiceschanged`.
- Always keep the text on screen too.
