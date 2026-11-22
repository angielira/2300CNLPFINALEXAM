# Web Speech API (speech synthesis)

- `window.speechSynthesis`: `speak(utterance)`, `pause()`, `resume()`, `cancel()`, `getVoices()`; properties `speaking`, `pending`, `paused`.
- `SpeechSynthesisUtterance` properties: `text`, `voice`, `lang`, `rate`, `pitch`, `volume`.
- Voices load asynchronously: listen for `voiceschanged`.
- Baseline widely available since 2018; voices depend on the device.

## Sources
- https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis
- https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance
