# 5. Learning styles and how HelpMate offers formats responsibly

## What the research says

- "Learning styles" (such as VARK: visual, auditory, reading/writing, kinesthetic) is the idea that people learn best when teaching matches their preferred mode. The key claim is the **meshing hypothesis**. ([Pashler et al., 2008](https://doi.org/10.1111/j.1539-6053.2009.01038.x))
- Pashler, McDaniel, Rohrer and Bjork found plenty of evidence that people *have preferences* about how information is presented, but virtually no evidence that matching instruction to those preferences improves learning.
- Later reviews agree: studies that tested meshing properly found very small, non-significant effects, and it is widely described as a neuromyth. ([Aslaksen & Lorås, 2018](https://doi.org/10.3389/fpsyg.2018.01538); [review, 2023](https://doi.org/10.3389/feduc.2023.1147498))

## HelpMate's design decision

HelpMate **lets users choose** a format; it never diagnoses a "style" or locks anyone into one.

| Button | What it shows | Why it helps everyone |
|---|---|---|
| See it (blue) | Color-coded numbered steps, simple diagrams, screenshots | Pictures of where to click reduce search time |
| Hear it (coral) | Steps read aloud with the browser's Web Speech API (`speechSynthesis`) | Hands and eyes stay on the device; helps low-vision and low-literacy users |
| Try it (teal) | Click-through practice with checkboxes | Doing the steps builds confidence (practice and retrieval are well supported) |
| Read it (purple) | Plain-language printable checklist | Easy to follow away from the screen |

Users can switch formats at any time, and combining words with pictures is encouraged.

## The 10-step mini-course ("Learn more")

- Optional side panel tied to the question's category.
- 10 short steps, each with one idea, one example and one quick check question (microlearning plus retrieval practice).
- Progress bar and badges saved in the browser's `localStorage` (no accounts needed).

## Accessibility (WCAG 2.2)

- Text contrast at least 4.5:1; buttons at least 44×44 px; plain words, no jargon.
- Every format has a text alternative; "Hear it" never replaces on-screen text.

## Sources
- Pashler et al., 2008, *Learning Styles: Concepts and Evidence*: https://doi.org/10.1111/j.1539-6053.2009.01038.x
- Aslaksen & Lorås, 2018: https://doi.org/10.3389/fpsyg.2018.01538
- Persistence of matching learning styles (2023): https://doi.org/10.3389/feduc.2023.1147498
- Web Speech API (MDN): https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
