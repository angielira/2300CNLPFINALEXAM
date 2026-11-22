# HelpMate UX spec (Iris, Phase 4 step 1)

For frontend-engineer (Pixel), pyodide-engineer (Pip) and data-viz-expert (Vega). Build to the ids and classes below; `site/css/app.css` already styles them. Do not rename without telling Iris.

**File names.** `reports/plan.md` section 1 says `css/tokens.css`, `css/helpmate.css`, `css/insights.css`. This work uses `site/css/design-tokens.css` and `site/css/app.css` (insights styles are inside app.css, section 12). Atlas should update plan.md, or rename the files. Load in every page: design-tokens.css, then app.css.

## 0. Rules for every page
- `<html lang="en">`, viewport meta `width=device-width, initial-scale=1`. One `<h1>` per page, no skipped heading levels.
- Head: Nunito link tags from the comment at the top of design-tokens.css (weights 600-900).
- First element in body: `<a class="skip-link" href="#main">Skip to main content</a>`. Then header, `<main id="main" tabindex="-1">`, footer.
- No emoji. Icons are inline `<svg class="icon" aria-hidden="true" focusable="false" viewBox="0 0 24 24">` with stroke paths (use `icon--fill` for solid shapes). Icon-only buttons are not allowed: always visible text.
- Real `<button>`, `<label for>`, `<fieldset>/<legend>`. Every interactive element is at least 44x44 CSS px (the CSS enforces this; do not shrink it).
- Never show color alone. Library badge = text. Selected format = `aria-pressed` plus a check mark (CSS draws it).
- Status changes go into `aria-live="polite"` regions. Move focus only when a panel opens or closes.
- Test at 360px wide, 200% zoom, keyboard only, and `prefers-reduced-motion`.

## 1. index.html

```
a.skip-link
header.site-header > .container.container--wide.site-header__inner
  a.brand[href=index.html] > img.brand__mark[src=assets/brand/helpmate-mark.svg, alt="", width=44, height=44] + span.brand__name "HelpMate"
  nav.site-nav[aria-label="Main"] > a.nav-link[aria-current=page] "Get help" + a.nav-link[href=insights.html] "Insights"
main#main.container[tabindex=-1]
  section.hero[aria-labelledby=hero-title]
    h1#hero-title.hero__title      "Hi! What's giving you trouble today?"
    p.hero__lead                   "Tell me in your own words. There are no silly questions, and I'll go one small step at a time."
    form#ask-form.ask[novalidate]
      label.ask__label[for=question]     "Type your question here"
      textarea#question.ask__input[rows=3, maxlength=300, aria-describedby="question-hint", placeholder="For example: my printer will not print"]
      p#question-hint.ask__hint          "Please don't include passwords or personal details."
      div.ask__actions
        button#ask-button.btn.btn--primary.btn--lg[type=submit]   "Help me with this"
        span.ask__count[aria-live=off]   "0 of 300"   (optional)
    div.chips[role=group, aria-labelledby=chips-title]
      p#chips-title.chips__title   "Not sure what to type? Tap one of these."
      ul.chips__list > li > button.chip[type=button]   (example question text, from examples.json when ready)
    p#engine-status.status[role=status] > span.spinner[aria-hidden] + span "Getting HelpMate ready..."  -> "HelpMate is ready." (remove spinner)
  section#results.results[aria-labelledby=results-title, hidden]     (aria-live region wrapper: div#results-live[aria-live=polite])
    h2#results-title.results__title   "Here's what I found"
    (notices, see section 3)
    article#card-category.card.card--category[aria-labelledby=card-category-title]
      header.card__head > h3#card-category-title.card__title "I think this is about" + span.badge.badge--nn
      div.card__body > p.card__big "Printer"  + div.meter > span.meter__track > span.meter__fill[style="--value:93"] + span "93% sure"
    article#card-mood.card.card--mood   (only when mood data exists)
      header.card__head > h3.card__title "How you sound" + span.badge.badge--nltk
      div.card__body > p "That sounds frustrating. Let's slow down and do this together."  (calm tone text from answers[].calm_intro)
    article#card-things.card.card--things   (only when entities found)
      header.card__head > h3.card__title "Things you mentioned" + span.badge.badge--spacy
      div.card__body > ul.tags > li.tag > span.tag__kind "Device" + span "printer"
    article#card-breakdown.card.card--breakdown   (only for example chips: examples.json)
      header.card__head > h3.card__title "How I read that question" + span.badge.badge--both
    section#answer.answer[aria-labelledby=answer-title]
      h3#answer-title.answer__title   (answers[].title)
      p.answer__summary               (answers[].summary)
      p "Topics" + ul.tags (answers[].tags) + span.badge.badge--spacy
      h4 "How would you like your help?"
      div#format-buttons.formats[role=group, aria-label="Choose how you want help"]
        button.format-btn.format-btn--see [type=button, data-format=see_it, aria-pressed=false, aria-controls=format-panel]
            svg.icon (eye) + span "See it" + span.format-btn__hint "Steps with pictures"
        button.format-btn.format-btn--hear [data-format=hear_it]  svg (speaker) "Hear it"  hint "I'll read it to you"
        button.format-btn.format-btn--try  [data-format=try_it]   svg (check-square) "Try it" hint "Tick off each step"
        button.format-btn.format-btn--read [data-format=read_it]  svg (document) "Read it" hint "A checklist to print"
        (order: see, hear, try, read; use format_rank only to mark the first as "Popular", as text, never to reorder)
      div#format-panel.format-panel[data-format=see_it, tabindex=-1, role=region, aria-label="Your help"]
        (content patterns in section 2)
      p.help-note   answers[].when_to_get_help
      div.learn-cta > p.learn-cta__text "Want to understand this better? Try the 10-step mini-course." + button#learn-open.btn.btn--secondary[aria-haspopup=dialog, aria-controls=learn-panel] "Learn more"
  section#rating.card.rating[aria-labelledby=rating-title]
    h2#rating-title.rating__title "Did this help?"
    p.rating__privacy "Please don't include personal details. Your rating helps HelpMate get better each time it is rebuilt."
    form#rating-form[name=rating, data-netlify=true, netlify-honeypot=bot-field]   (hidden inputs per plan.md section 6)
      p.honeypot > label "Don't fill this in" + input[name=bot-field, tabindex=-1, autocomplete=off]
      fieldset.stars
        legend.stars__legend "How would you rate this help?"
        div.stars__row           DOM order 5,4,3,2,1 (CSS reverses it)
          input.stars__input#star-5[type=radio, name=stars, value=5, required] + label.stars__label[for=star-5] > svg.icon(star outline) + span.visually-hidden "5 stars"
          ... down to star-1 ("1 star")
        p#stars-value.stars__value[aria-live=polite]   "" -> "4 of 5 stars"
      div.field > label.field__label[for=comment] "Anything to add? (optional)" + textarea#comment.field__input[name=comment, maxlength=500] + p.field__help "Up to 500 characters."
      button.btn.btn--primary[type=submit] "Send my rating"
    div#rating-thanks.thanks[hidden, role=status] > p "Thank you! Your rating will help the next version of HelpMate."
footer.site-footer > .container
  ul.site-footer__links > li > a "Get help", "Insights", "How HelpMate works"(optional)
  p.site-footer__note "HelpMate is a study project. It gives general self-help tips, not professional repair."
  p.site-footer__note "Made with NLTK, spaCy and a small neural network." + badges (span.badge.badge--nltk, .badge--spacy, .badge--nn)
div#panel-backdrop.panel-backdrop
aside#learn-panel.panel[role=dialog, aria-modal=true, aria-labelledby=learn-title, aria-hidden=true]   (sibling of main, last in body)
  header.panel__head > h2#learn-title.panel__title "Printer basics in 10 steps" + button#learn-close.panel__close[type=button] svg(x) + span "Close"
  div.panel__body
    div.progress > div.progress__label > span "Your progress" + span#progress-text "3 of 10 steps"
                 + div.progress__track[role=progressbar, aria-valuemin=0, aria-valuemax=10, aria-valuenow=3, aria-label="Mini-course progress"] > span.progress__fill[style="--value:30"]
    ol.dots > li > button.dot[aria-label="Step 1, done"][aria-current=step on the open step]; add .is-done when completed
    article.lesson
      p.lesson__kicker "Step 3 of 10" + span.badge.badge--spacy (tags)
      p.lesson__idea (idea)
      p.lesson__example > strong "Think of it like this" + text (example)
      fieldset.quiz > legend.quiz__q (check_question) + label.choice > input[type=radio, name=check] + span (x3)
      button.btn.btn--primary "Check my answer"
      p.quiz__feedback.is-correct   "Yes! Nicely done."  |  .is-try-again  "Not quite. Have another look at the example, then try again."
    h3 "Your badges" + ul.medals > li.medal[.is-earned] > span.medal__disc(svg) + span (badge name) + span.medal__state "Earned" | "Not yet"
    div.celebrate[hidden]  "You earned the Printer Pro badge. Well done!"
  div.panel__foot > button.btn.btn--secondary "Back" + button.btn.btn--primary "Next step"
```
Panel behavior (frontend): on open remove `aria-hidden`, add `.is-open` to `#learn-panel` and `#panel-backdrop`, add `has-panel-open` to body, move focus to `#learn-close`, trap Tab, close on Esc and backdrop click, return focus to `#learn-open`. Set `inert` on `main` and footer while open. Phone (below 896px): full-screen sheet. Desktop: 28rem slide-over from the right.

## 2. Format panel content (`#format-panel`, set `data-format`)
- **See it:** `h4.format-panel__title`, optional `p.format-panel__intro` (calm_intro), `ol.steps > li.step > span.step__num + div > p.step__label + p.step__detail (+ img.step__image with alt)`. Source: `see_it.steps`.
- **Hear it:** `div.hear-controls` with `button.btn` "Read it to me" (svg play), `button.btn.btn--secondary` "Pause", "Stop". `p.hear-note` "Your device's voice will read each step. The words stay on screen too." `ol.script > li.script__line` (`.is-speaking` on the line being read; set `aria-current="true"` too). If `speechSynthesis` is missing: replace the controls with a `.notice.notice--info` "Your browser can't read aloud. The steps below are the same words."
- **Try it:** `ul.check-list > li > label.check > input.check__box[type=checkbox, id=try_it step id] + span.check__text`. Above it a `.progress` bar "2 of 6 done". When all ticked: `p.try-done` "All done! Well done. If it still isn't working, see the note below."
- **Read it:** `h4.print-title.print-only` (read_it.print_title) is printed; `ul.read-list > li.read-list__item`; `div.format-actions > button.btn.btn--secondary "Print this checklist"` (calls `window.print()`). Print CSS shows only the panel.
- Always start a panel with its own label so people know which format they are in. Switching format keeps the user's place and moves focus to `#format-panel` (tabindex=-1).

## 3. Result states (use `.notice`, always icon + words)
| State | Markup | Copy |
|---|---|---|
| Loading engine | `#engine-status` with `.spinner` | "Getting HelpMate ready. This can take a few seconds the first time." |
| Thinking | `.skeleton` blocks inside `#results` | "Thinking about your question..." |
| Ready | `#engine-status` text | "HelpMate is ready." |
| Unsure (confidence below `min_confidence` or no known words) | `.notice.notice--unsure` + chips of the 8 categories as `button.chip` | "I'm not sure yet. Which of these is closest to your problem?" |
| Frustrated (`mood.frustrated`) | `.notice.notice--calm` + badge NLTK | "That sounds frustrating, and that's okay. We'll take it one small step at a time." |
| Empty question | `.field__error` under textarea, `aria-invalid=true` | "Please type a few words about your problem first." |
| Browser engine failed | `.notice.notice--error` + fallback card badge spaCy | "The smart helper couldn't start, so I matched your words instead. The answer may be less exact." |
| Data not built yet | `.notice.notice--info` | "HelpMate's answers aren't ready yet. Please try again in a minute." |
| Rating sent / failed | `.thanks` / `.notice--error` | "Thank you!" / "That didn't send. Your rating is still here, so you can try again." |

## 4. Badges (plan.md section 7; text is always inside the pill)
`<span class="badge badge--nltk" title="Made by NLTK in your browser">NLTK</span>` and the same with `--spacy` ("Made by spaCy when the site was built"), `--nn` text "Neural network" ("Made by HelpMate's neural network in your browser"), `--both` text "NLTK + spaCy". Because `title` is not reachable by keyboard or touch, also repeat the meaning in a `.visually-hidden` span: `<span class="visually-hidden">, made by NLTK in your browser</span>`. Optional small `svg.icon` before the text.

| Library | Look | Contrast |
|---|---|---|
| NLTK | gold fill, navy text, navy border | 11.08 |
| spaCy | magenta fill, white text | 7.13 |
| Neural network | navy fill, white text | 15.97 |
| NLTK + spaCy | white fill, navy text and border, two dots | 15.97 |

## 5. insights.html (Vega)
```
header.site-header (same as index; "Insights" has aria-current=page)
main#main.container.container--wide[tabindex=-1]
  div.page-head > h1 "What people ask HelpMate" + p.page-head__lead "These charts update each time HelpMate is rebuilt. Each one says which tool made it."
  div#insights-status.status[role=status]             loading text, or .notice.notice--info "No ratings yet. Be the first to rate an answer." (.empty-state for empty charts)
  section.stat-grid[aria-label="Key numbers"] > div.stat > span.stat__value "412" + span.stat__label "questions studied"   (4 stats; each can carry a badge in its label)
  div.insights-grid
    section.card.chart-card[aria-labelledby=chart-words-title]      (add .chart-card--wide for full width)
      header.card__head > h2#chart-words-title.card__title "Most common words" + span.badge.badge--nltk
      figure.chart > (svg role=img aria-labelledby=title+desc, OR ul.bar-list > li.bar-row > span.bar__label + span.bar__track > span.bar__fill[style="--value:80"] + span.bar__value) + figcaption.chart__caption (one-sentence takeaway)
      ul.legend (only when color means something; swatches `.legend__swatch--1..5`, label text always present)
      details.chart-table > summary "Show this as a table" + div.table-wrap > table.data-table > caption, thead th[scope=col], tbody th[scope=row] + td.num
    sections: #chart-words (NLTK), #chart-phrases (NLTK), #chart-categories (Neural network: share by category), #chart-ratings (NLTK: stars and sentiment by week), #chart-formats (NLTK: format ranking), #chart-quality (three sub-cards: Neural network accuracy + confusion matrix, NLTK frustration precision/recall, spaCy entity precision/recall, each with its own badge)
    section.card.chart-card > "Where HelpMate gets it wrong" list of misclassified examples (honest errors), badge per list
```
Charts: use `--chart-1..5` (all at least 3:1 on white); add direct value labels, not only color; keep each text at 14px or larger; every chart has a `details.chart-table`. Chart text uses `.chart svg text` styling. Confusion matrix: show numbers inside cells and use a navy ramp, not red/green.

## 6. Microcopy and tone
Warm, short sentences, grade 6-8 reading level, never blame the user, explain a term once ("A router is the box that gives you Wi-Fi."). Say "I" for HelpMate sparingly; prefer "we" when doing steps.
- Hero: "Hi! What's giving you trouble today?"
- Button: "Help me with this" (not "Submit").
- Success: "Nice work. That's one step done."
- Gentle fail: "That's okay. Let's try once more."
- Format hints: See it "Steps with pictures", Hear it "I'll read it to you", Try it "Tick off each step", Read it "A checklist to print".
- Footer disclaimer: "HelpMate is a study project. It gives general self-help tips, not professional repair."
- Avoid: "invalid", "error code 500", "failed", "you must", "simply", "just".

## 7. How Iris checked
- Contrast pairs in `site/css/design-tokens.css` header; `tests/test_contrast.py` recomputes each pair from the token values with the WCAG formula (QA should run `pytest tests/test_contrast.py`). I had no shell in this session, so the ratios in the comment were worked out by hand and the test has not been run yet.
- Finding: the brand note says coral `#E04E2C` is safe text on cream. It is about 3.77:1, which fails 4.5:1 for normal text. Use `--coral-ink #C2410C` (4.91:1) for coral text. Also blue `#2F7BF5` (3.78) and purple `#8A5CF6` (4.03) fail for small text, and bright coral and teal fail even 3:1 on cream, so brights are used only as decoration paired with text. Atlas/Forge: update `knowledge/ux-accessibility-designer/brand.md` and the brand-system skill.
- Targets: all `.btn`, `.chip`, `.format-btn`, `.nav-link`, `.dot`, `.choice`, `.check`, `.stars__label`, `.panel__close`, `summary` have min size 44px or more in CSS.
- Not checked yet (needs the HTML): real rendering at 360px, tab order, screen reader names, print preview. Quinn should run an axe or Playwright check at 360px once index.html exists.
