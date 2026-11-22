# The four formats

| Format | Delivery | Tech |
|---|---|---|
| See it | Numbered, color-coded steps + simple diagrams | HTML/CSS/SVG |
| Hear it | Steps read aloud | Web Speech API `speechSynthesis` |
| Try it | Click-through practice with checkboxes | HTML + localStorage |
| Read it | Printable checklist | HTML + print CSS |

- Speech: `SpeechSynthesisUtterance` with `text`, `lang`, `rate`, `pitch`, `volume`; voices load asynchronously.
- Keep on-screen text for every format.

## Sources
- https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis
- docs/05-learning-formats.md (this repo)
