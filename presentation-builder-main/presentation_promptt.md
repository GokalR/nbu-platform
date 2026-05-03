# Prompt for Claude Code: AI в работе — Занятие 1 (v6 — Production)

## Project Overview

Generate an HTML presentation for a **2.5-hour workshop** titled:
**"AI в работе: возможности, ограничения и принципы использования"** (Занятие 1)

**Audience:** Senior management of a bank. Sophisticated, busy, risk-aware. Most have tried ChatGPT casually but aren't power users. Appropriately skeptical of hype, appropriately concerned about regulatory and operational risk.

**Total slides: 44**

**Total run time: ~150 minutes (2.5 hours), with built-in flex if running long.**

---

## Tone — Senior Advisor

The presenter is a senior internal expert briefing peers — like a CRO or senior director with 15 years of relevant experience addressing fellow executives. Professional and human. Doesn't lecture, doesn't apologize, doesn't oversell.

Concrete rules:

- **«Вы» is allowed on slides, but only when it earns its place.** «Если вы это отправили — вы это написали» — yes, this is the principle. «Что вы получите за эти 2.5 часа» — no, this is sales register. Use «вы» where it makes the line land harder; replace with a noun phrase otherwise.
- **Conversational connectives are fine in moderation.** «При этом», «как правило», «в большинстве случаев» — yes. «Если коротко», «давайте посмотрим», «представьте себе» — no.
- **No anthropomorphism.** «Модель оценивает», not «AI знает». «Генерирует», not «думает». Even when warm, stay technically honest about what the model is.
- **No rhetorical structures or pattern tics.** No triple negations («не коллега, не партнёр, не советник»). No «не магия и не угроза». No «это не одно и то же». No «действительно» as a defensive intensifier.
- **No moralizing.** Don't tell the audience what's important. Don't congratulate yourself on insights. Let the slide do its work.
- **Slides don't narrate themselves.** No subtitles like «То же самое, но рядом — чтобы разница читалась мгновенно».
- **Speaker notes coach the presenter.** Directive: «дайте 30 секунд паузы», «не комментируйте», «подача без драматизации».
- **Two protected dry-wit moments**: slide 32's «Регулятор не примет аргумент 'это нам ChatGPT написал'» and slide 13's barely-visible «парусник» bar at 0.0001%. Don't add more, don't comment on these in the room.
- **Russian for slide content.** Speaker notes can mix registers but stay primarily Russian.

---

## Design Tokens

```css
:root {
  /* Backgrounds */
  --bg-primary: #0d0d10;
  --bg-elevated: #16161a;
  --bg-input: #1c1c20;

  /* Text */
  --text-primary: #f4f4f5;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;

  /* Accent — graphite-gold */
  --accent: #c9a96e;
  --accent-soft: rgba(201, 169, 110, 0.15);
  --accent-line: rgba(201, 169, 110, 0.4);

  /* Muted warning */
  --warning: #a87878;
  --warning-soft: rgba(168, 120, 120, 0.18);

  /* Borders */
  --border-subtle: rgba(244, 244, 245, 0.08);
  --border-strong: rgba(244, 244, 245, 0.18);

  /* Typography */
  --font-serif: 'Source Serif Pro', 'PT Serif', Georgia, serif;
  --font-sans: 'Inter', 'IBM Plex Sans', system-ui, sans-serif;
  --font-mono: 'IBM Plex Mono', 'JetBrains Mono', monospace;

  /* Spacing scale */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;

  /* Slide layout */
  --slide-width: 1920px;
  --slide-height: 1080px;
  --slide-padding: 96px;
  --content-max-width: 1400px;
}
```

**Typography scale:**
- `--text-display`: 96px serif italic — title slide, big takeaways
- `--text-h1`: 64px serif italic — section openings
- `--text-h2`: 44px serif — slide titles
- `--text-h3`: 28px sans-serif semibold — card titles, subheaders
- `--text-body`: 22px sans-serif regular — default body
- `--text-small`: 18px sans-serif — captions, secondary
- `--text-caption`: 14px sans-serif uppercase tracking-wide — labels, eyebrows

**Font loading:**
- All `@font-face` declarations must use `font-display: swap` to avoid blocking render
- System fallbacks: Georgia (serif), Arial (sans), Courier New (mono)

---

## Responsive Behavior

Slides are designed at 1920×1080. On smaller viewports:

- Container element gets `transform: scale(N)` where N = min(viewportWidth/1920, viewportHeight/1080)
- `transform-origin: center center`
- Body has `overflow: hidden; background: var(--bg-primary)`
- The scaled slide is centered with letterboxing (top/bottom or left/right) using flexbox `align-items: center; justify-content: center`
- This must work on a 13" laptop (1440×900) and a typical conference projector (1280×720) without breaking layout

---

## Reusable Component Patterns

### Pattern A — Card

```
- Background: var(--bg-elevated)
- Border: 1px solid var(--border-subtle)
- Border-radius: 12px
- Padding: var(--space-6) (24px)
- On accent emphasis: border becomes 1px solid var(--accent-line)
```

### Pattern B — Two-column comparison

```
- Display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-8) (32px)
- Each column: vertical stack with header at top
- Headers: --text-caption style, uppercase, secondary color, with thin accent underline (2px, 24px width, accent color)
- Optional center divider: vertical line, var(--border-subtle), 1px wide
```

### Pattern C — Numbered Card

```
- Same as Pattern A
- Number top-left: large (--text-h1 size, 64px), serif italic, var(--accent) color
- Title below number: --text-h3, primary color
- Description (if any): --text-body, secondary color, max 2 lines
```

### Pattern D — Slide Title Block

```
- Eyebrow line above title: --text-caption, secondary color, 24px width accent line below it
- Title: --text-h2, serif, near-white
- Optional subtitle: --text-small, muted color
- Top of slide, left-aligned, 96px from top edge
```

### Pattern E — Process Step

```
- Horizontal layout
- Each step is a card (Pattern A)
- Steps connected by chevron arrows: 32px wide line, var(--border-strong) color
- Step number above title: --text-caption, accent color (e.g. "ШАГ 1")
- Step title: --text-h3
- Step description: --text-small, secondary color
```

### Pattern F — Demo / Example Two-Column

```
- 40/60 split: prompt on left (40%), output/screenshot on right (60%)
- Prompt container: var(--bg-input), 12px radius, padding 24px, font-mono 18px, with small "ЗАПРОС" label above
- Output container: same styling, with "РЕЗУЛЬТАТ" label
- Screenshot placeholders: dashed 1.5px border var(--border-subtle), centered text in --text-muted
```

### Slide chrome (every slide)

```
- Bottom-left: section name, --text-caption, secondary
- Bottom-right: slide number "11 / 44", --text-caption, secondary
- Top-right: thin progress bar, 200px wide, 2px tall, accent fills as deck progresses
- All chrome 32px from edges, opacity 0.5
```

---

## Time Budget

| Section | Slides | Time |
|---|---|---|
| 0. Opening | 1–3 | 7 min |
| 1. What is AI / GenAI | 4–10 | 18 min |
| 2. How AI works / why it errs | 11–18 | 25 min |
| Break | 19 | 10 min |
| 3. Where AI helps | 20–24 | 18 min |
| 4. Risks | 25–29 | 18 min |
| 5. Responsibility | 30–32 | 10 min |
| 6. Principles | 33–38 | 14 min |
| 7. Diagnostic | 39–41 | 25 min |
| 8. Wrap-up | 42–44 | 5 min |
| **Total** | | **150 min** |

**Slide 30 (assistant analogy) was removed in v6** — the workflow on slide 31 (now 31) makes the same point. Section 5 compressed from 4 to 3 slides.

**Sections 1, 3, 4, 6 each trimmed by 2 minutes** to give the diagnostic exercise its full 25 minutes without overrun.

If the session is running long when reaching Section 7, **the diagnostic exercise is non-negotiable**. Cut Section 6 (principles) presentation time first — the 5 principles can be covered in 8 minutes if needed.

---

## Slide-by-Slide Specification

---

### SECTION 0 — OPENING (Slides 1–3, ~7 min)

#### Slide 1 — Title

**Content:**
- Eyebrow: «Программа курса»
- Lesson marker: «Занятие 1»
- Title: «AI в работе: возможности, ограничения и принципы использования»
- Subtitle: «Вводное занятие. Общий язык и рамка для следующих занятий.»

**Visualization:**

Layout: Centered vertically and horizontally on slide. Max width: 1100px. Vertical stack, gap 32px between elements.

Components:
- Eyebrow text "ПРОГРАММА КУРСА" — --text-caption, --text-muted, letterspacing 0.15em
- Below eyebrow: thin horizontal line, 80px wide, 2px tall, --accent color, 24px gap above and below
- "Занятие 1" — --text-h3, serif italic, --text-secondary
- Title — --text-display (96px), serif italic, --text-primary, line-height 1.15, max 3 lines
- Subtitle — --text-h3, sans-serif regular, --text-secondary

All text left-aligned within the centered block. No icons.

Animation: Fade in from opacity 0 to 1 over 600ms, staggered 100ms per element top-to-bottom.

**Speaker note:** «Два с половиной часа. Не про промптинг — про устройство инструмента, его область применимости и его ограничения. Это рамка для следующих занятий.»

---

#### Slide 2 — О чём это занятие

**Content:**
- Title: «О чём это занятие»
- 4 outcomes:
  1. **Как это устроено** — Принцип работы и природа ошибок
  2. **Карта применимости** — Где AI помогает, где создаёт риски
  3. **Пять принципов** — Рабочие правила использования
  4. **Диагностика** — Текущее использование AI участниками

**Visualization:**

Layout: Title block at top using Pattern D. Below: 2×2 grid of cards, gap 24px both directions. Grid container max-width: 1200px, centered. Each card aspect ratio approximately 1.4:1.

Components per card:
- Pattern C (Numbered Card)
- Number 01-04 (leading zero) in top-left, --text-h1 serif italic accent
- Below number, gap 24px: card title in --text-h3
- Below title: description in --text-body --text-secondary
- No icons

Animation: Cards fade-in stagger left-to-right, top-to-bottom, 100ms apart, 400ms each.

---

#### Slide 3 — Рамка

**Content:**
- Eyebrow: «Рамка»
- Central line: «AI — инструмент с измеримыми свойствами и понятными границами.»
- Subtitle: «Сегодня — про эти свойства и эти границы.»

**Visualization:**

Layout: Vertical center of slide. Single column, centered text, max-width 1000px.

Components:
- Eyebrow at top: --text-caption uppercase, --text-muted, 32px gap below
- Main statement: --text-h1 (64px) serif italic, --text-primary, line-height 1.3
- Subtitle: --text-h3 sans regular, --text-secondary, 32px gap above

No background, no border. Pure typography.

**Speaker note:** «Тон занятия — нейтральный. Без оптимистического и без тревожного шума. Если в зале начнётся дискуссия про 'заменит ли AI людей' — мягко возвращайте к предметному уровню.»

---

### SECTION 1 — WHAT IS AI / GENERATIVE AI (Slides 4–10, ~18 min)

#### Slide 4 — Три вещи, которые называют AI

**Content:**
- Title: «Три вещи, которые называют AI»
- Subtitle: «Все три встречаются в банке каждый день. Все три называют 'AI'. При этом устроены по-разному.»
- Three cards:
  1. **Антифрод-системы** — отслеживают подозрительные транзакции (тип: ML)
  2. **Биометрия в приложении банка** — узнают клиента по лицу или голосу (тип: CV)
  3. **ChatGPT, Claude, Gemini** — отвечают на вопросы и пишут тексты (тип: GenAI)
- Bottom callout: «Сегодня говорим о третьем типе. Контраст с первым удобен — на нём разница видна сразу.»

**Visualization:**

Layout: Title block (Pattern D). Subtitle below title in --text-h3 secondary. Three cards in horizontal row, equal width, gap 24px. Bottom callout: full-width block, 80px below cards.

Each card:
- Pattern A with extra padding (32px)
- Top: small icon, 32×32px, line-art, 1.5px stroke, --accent
  - Card 1: stylized shield with checkmark inside
  - Card 2: face outline with brackets [ ]
  - Card 3: speech bubble with three dots
- Middle: --text-h3 title
- Bottom: --text-small description, --text-secondary
- Right side small label: "ML" / "CV" / "GenAI" in --text-caption --accent

Bottom callout:
- Full-width within content area
- Background: --bg-elevated
- Padding: 24px 32px
- Border-left: 3px solid --accent
- Text: --text-body, primary, italic

**Speaker note:** «Антифрод выбран не случайно. Знаком аудитории. Работает в производственной среде много лет. И — главное — даёт чистый контраст с GenAI по всем ключевым параметрам: задача, данные, тип ответа, валидация. Следующие два слайда раскрывают этот контраст подробно.»

---

#### Slide 5 — Как работает классический AI: пример антифрода

**Content:**
- Title: «Как работает классический AI: пример антифрода»
- Subtitle: «Узкая задача. Размеченные данные. Бинарный ответ.»
- Process diagram showing antifraud pipeline.
- Caption: «Одна задача. Один тип ответа. Точность измерима. Поведение предсказуемо.»

**Visualization:**

Layout: Title block at top. Below: large process diagram, full content width, ~600px tall. Bottom: 2-line caption.

Diagram has 4 stages, left to right.

**Stage 1 — Транзакции:**
- Stack of 4 transaction "cards" on the left, slightly fanned (rotation 0°, -2°, -4°, -6°)
- Each card: 140×80px rectangle, --bg-elevated, with text inside in --text-small --text-secondary: «сумма», «получатель», «время», «локация»
- Stack visually flows toward Stage 2
- Label below: «Поток транзакций — каждая со своими признаками»

**Stage 2 — Модель:**
- Centered rectangle, 280×200px, --bg-elevated, --accent border (1.5px)
- Inside: simplified neural-net visualization
  - 3 columns of dots at x positions: 70, 140, 210 (relative to box origin)
  - 4 rows of dots at y positions: 50, 90, 130, 170
  - Total 12 dots, each 8px diameter, --accent fill
  - Connections: every dot in column 1 connects to every dot in column 2 (16 lines); every dot in column 2 connects to every dot in column 3 (16 lines)
  - Connection lines: 1px stroke, --border-subtle
- Label inside box top: «Обученный классификатор» (--text-small --text-primary, position 16px from top)
- Below box: caption «Обучен на исторических размеченных данных банка»

**Stage 3 — Решение:**
- Two output paths splitting from model
- Top path (angled up): «Норма» — green-tinted soft outline (#7d9b7d at 30% opacity), checkmark icon
- Bottom path (angled down): «Подозрение» — --warning soft outline, flag icon

**Stage 4 — Действие:**
- Top: «Пропустить» — --text-secondary
- Bottom: «Заблокировать → проверка» — --warning

Connecting elements: thin chevron arrows between stages, --border-strong, 1.5px. Animated dots flowing along arrows on entry (subtle, 1px dots moving slowly).

Caption styling: --text-body italic, --text-secondary

Animation: Stages reveal left-to-right, 300ms each. After all stages visible, "flowing dots" animation starts and loops slowly.

**Speaker note:** «Обратите внимание на свойства: обучение на собственных данных банка, одна задача, для каждой транзакции есть правильный ответ, точность можно измерить и валидировать. Все эти свойства теряются, когда переходим к GenAI.»

---

#### Slide 6 — Как работает Generative AI

**Content:**
- Title: «Как работает Generative AI»
- Subtitle: «Универсальная задача. Публичные данные. Текст за текстом.»
- Process diagram.
- Caption: «Множество задач. Вариативные ответы. Точность не всегда измерима. Поведение нестабильно.»

**Visualization:**

Layout mirrors Slide 5 (intentional, for comparison): title block, big diagram, caption.

4 stages, left to right:

**Stage 1 — Запрос:**
- Single large speech-bubble shape, --bg-input background, 280×140px
- Inside, --font-mono 16px --text-secondary: «Напиши письмо клиенту…»
- Label below: «Один запрос на естественном языке»

**Stage 2 — LLM:**
- Centered rectangle, 280×200px, --bg-elevated, --accent border (1.5px)
- Inside: 5 mini horizontal bars representing word probabilities
  - Bars at y positions: 50, 80, 110, 140, 170
  - Bars start at x=40, decreasing in length: 200px, 160px, 120px, 90px, 60px
  - All bars height 16px, border-radius 2px right side only
  - Top bar in --accent; bars 2-5 in --text-muted
- Label inside box top: «LLM (например, GPT-4)» (--text-small --text-primary, 16px from top)
- Below box: caption «Обучен на больших публичных корпусах текста»

**Stage 3 — Генерация:**
- Sequence of 5 word tokens being generated one by one
- Tokens as small rounded rectangles in a row, 16px gap between each
- Token text: «Уважаемый» → «Иван» → «Иванович» → «,» → «...»
- Each token: padding 8px 12px, --bg-elevated, border-radius 6px, --text-small --text-primary
- Above tokens: small annotation "слово за словом" --text-caption --text-muted
- Circular arrow icon (◞↺ style) to the left of the sequence, 24px, --accent
- Below tokens: «каждое слово — отдельное предсказание» --text-caption --text-muted

**Stage 4 — Результат:**
- Document-shape rectangle, 220×280px, --bg-elevated
- Inside: 8 horizontal lines suggesting text (varying widths to look natural: 180, 200, 160, 190, 180, 150, 170, 140)
- Lines: 4px tall, --text-muted opacity 0.4, 16px gap between
- Top of document: small label «Готовый текст» --text-caption --text-secondary

Connecting elements: same arrow style as Slide 5, animated dots.

Animation: Same 300ms-per-stage stagger as Slide 5. Stage 3 (generation loop) has tokens appearing one-by-one with 200ms delay, simulating real-time generation.

**Speaker note:** «Сравните со слайдом 5: универсальная задача вместо одной, публичные данные вместо собственных, генерация слово за словом без проверки итога. Последний пункт — главный источник ошибок, к которым перейдём в разделе 2.»

---

#### Slide 7 — Сравнение по ключевым параметрам

**Content:**
- Title: «Сравнение по ключевым параметрам»
- Comparison table.

**Visualization:**

Layout: Title block at top. Below: comparison table using Pattern B. Each column has header row, then 5 comparison rows.

Column headers:
- Left: «КЛАССИЧЕСКИЙ AI» — --text-caption uppercase, with subtitle «(антифрод, биометрия)» in --text-muted below
- Right: «GENERATIVE AI» — --text-caption uppercase --accent, with subtitle «(ChatGPT, Claude)» in --text-muted below
- Each header has thin accent line below (left: secondary color, right: --accent), 60px wide, 2px tall

5 comparison rows:

| Аспект | Классический AI | Generative AI |
|---|---|---|
| Задача | Одна, узкая | Универсальная |
| Данные обучения | Размечены банком | Публичный интернет |
| Тип ответа | Категория или число | Текст любой длины |
| Точность | Измеряется и валидируется | Сложно валидировать |
| Поведение | Предсказуемо | Вариативно |

Row styling:
- Horizontal flex with 3 elements: aspect label (left, fixed width 200px, --text-caption secondary), classical column, GenAI column
- Row separator: 1px --border-subtle
- Row padding: 16px vertical
- Aspect labels right-aligned
- Cell text: --text-body
- Right column (GenAI) cells have very subtle --accent-soft background tint

Animation: Rows fade in top-to-bottom, 80ms stagger.

**Speaker note:** «Дайте таблице 20–30 секунд молчания. Аудитория считывает её сама. Не комментируйте каждую строку — слайд сам справляется.»

---

#### Slide 8 — Где Generative AI находится в общей структуре

**Content:**
- Title: «Где Generative AI находится в общей структуре»
- Subtitle: «Когда сегодня в новостях говорят 'AI' — как правило, имеется в виду внутренний круг: Generative AI / LLMs.»
- Right-side callouts (4 entries):
  - **AI** (внешний круг) — «Любые системы, имитирующие интеллектуальное поведение. Очень широкая категория.»
  - **Machine Learning** — «Системы, обучающиеся на данных. Сюда входят антифрод, скоринг, рекомендательные системы.»
  - **Deep Learning** — «ML на нейронных сетях с большим числом слоёв. Биометрия, распознавание речи.»
  - **Generative AI / LLMs** — «Подкласс Deep Learning, обученный генерировать текст, изображения, код. ChatGPT, Claude, Midjourney.»

**Visualization:**

Layout: Title block at top. Subtitle below. Center-left: large nested-circles diagram. Right side: callout text explaining each layer.

Build as inline SVG, viewBox 0 0 800 900 (extra height for top label). All circles centered at (400, 460).

Four concentric circles:
- Outer: radius 360, stroke 1.5px --border-strong, no fill
- Circle 2: radius 280, stroke 1.5px --border-strong, no fill
- Circle 3: radius 200, stroke 1.5px --border-strong, no fill
- Innermost: radius 120, stroke 2px --accent, fill --accent-soft

Labels — placed INSIDE each band (between rings), at the top portion:
- "AI" label: positioned at (400, 90), inside the band between outer edge and circle 2
- "Machine Learning" label: positioned at (400, 200), inside band between circle 2 and circle 3
- "Deep Learning" label: positioned at (400, 290), inside band between circle 3 and innermost
- "Generative AI / LLMs" label: positioned at (400, 460), centered inside the innermost circle

Label font: --text-h3 for outer 3, --text-h3 bold for innermost. Outer 3 labels: --text-secondary. Innermost label: --text-primary.

Subtle dots inside outer rings (decorative): 12 small dots (4px) randomly distributed in band between circles 1 and 2; 8 dots between 2 and 3; 4 dots between 3 and innermost. All dots --text-muted, opacity 0.3.

Right-side callout text (positioned to the right of SVG, vertical stack, gap 32px between entries):
- Each entry: small colored bullet (matching that layer), label in --text-h3, 1-line description in --text-small --text-secondary
- Spacing 32px between entries

Animation: Circles draw on entry, outer to inner, 250ms each. Innermost circle gets subtle pulse on completion (one-time, 800ms scale 1 → 1.05 → 1).

**Speaker note:** «Антифрод и биометрия — в средних слоях. ChatGPT — во внутреннем. Регуляторные документы про 'AI' часто адресуют разные слои этой схемы — полезно сразу смотреть, к какому слою применима норма.»

---

#### Slide 9 — Карта основных инструментов

**Content:**
- Title: «Карта основных инструментов»
- Subtitle: «Цель слайда — ориентация в рынке. Не рекомендация к использованию.»
- 5 categories:
  - **ТЕКСТ:** ChatGPT, Claude, Gemini, DeepSeek
  - **ИЗОБРАЖЕНИЯ:** Midjourney, DALL·E
  - **ВИДЕО:** Sora, Veo, Runway
  - **КОД:** GitHub Copilot, Cursor
  - **ГОЛОС:** ElevenLabs

**Visualization:**

Layout: Title block at top. Below: 5 columns by category, each a vertical stack.

Each column:
- Header: category name in --text-caption uppercase, --accent
- Below header: vertical stack of 2-4 tool name cards

Tool cards:
- Small Pattern A cards, padding 16px, just the tool name
- --text-body, primary
- Width: column width
- Gap between cards: 8px

Column gap: 24px. Container max-width: 1400px.

**Speaker note:** «Слайд проходится быстро (1–2 минуты). Цель — узнаваемость названий. Если кто-то спросит про конкретный инструмент — короткий ответ и движение дальше. Один важный момент, который полезно упомянуть в речи: версии моделей быстро меняются (GPT-4, GPT-4o, GPT-4.5), и поведение от версии к версии может заметно отличаться. Это отдельный операционный риск — то, что работало в пилоте, может вести себя иначе через три месяца.»

---

#### Slide 10 — Section transition

**Content:**
- Single line: «Раздел 2. Как это устроено и почему ошибается.»

**Visualization:**

Layout: Vertically and horizontally centered. Single line of text, max-width 900px.

Components:
- Text: --text-h1 serif italic, --text-primary
- Above: thin accent line, 80px wide, 2px tall, --accent, 48px gap below
- Below: «2 из 8» in --text-caption --text-muted

Animation: Line draws first (300ms), then text fades in (500ms), then "2 из 8" fades in (300ms).

---

### SECTION 2 — HOW AI WORKS / WHY IT ERRS (Slides 11–18, ~25 min) — THE CORE

#### Slide 11 — Главный образ раздела

**Content:**
- Eyebrow: «Главный образ раздела»
- Central line: «По сути — это очень мощное автодополнение.»
- Subtitle: «Из этого свойства вытекают и сильные стороны, и ограничения.»

**Visualization:**

Layout: Vertically centered, single column, max-width 1100px. Three text elements stacked.

Components:
- Eyebrow: --text-caption uppercase, --text-muted, with 60px wide --accent line below it (gap 16px)
- Main: --text-display (96px) serif italic, --text-primary, line-height 1.2
  - Heavier weight on "очень мощное автодополнение"
- Subtitle: --text-h3 sans regular, --text-secondary, 32px gap above

Animation: Eyebrow + line fade in first (400ms). Main: words fade in left-to-right in groups of 2-3, 80ms apart. Subtitle fades in last.

**Speaker note:** «Подача спокойная и уверенная. Не оправдывайтесь за простоту модели — она объясняет большую часть наблюдаемого поведения LLM. Дайте слайду 30 секунд, прежде чем переходить к деталям.»

---

#### Slide 12 — Автодополнение, которое все знают

**Content:**
- Title: «Автодополнение, которое все знают»
- Phone mockup with autocomplete
- Right-side text:
  - Para 1: «Телефон предсказывает следующее слово на основе ваших прошлых сообщений.»
  - Para 2: «ChatGPT работает по тому же принципу — но обучен не на личных сообщениях, а на большой части публичного интернета.»

**Visualization:**

Layout: Title block at top. Below: phone mockup centered, ~400×800px. Right side of phone: explanatory text.

Phone body:
- Rounded rectangle 380×780px
- Background: var(--bg-elevated)
- Border: 2px var(--border-strong)
- Border-radius: 48px
- Inner screen: 340×680px, top inset 60px, --bg-primary background, border-radius 32px

Inside screen, top to bottom:
- Status bar (8% screen height): mock time "9:41", small icons
- Chat area (60% screen height): 2 message bubbles
  - Bubble 1 (incoming, left): light gray, «Когда встречаемся?»
  - Bubble 2 (outgoing, right, accent-tinted): typing in progress «Я сегодня иду на|» (cursor blinking)
- Autocomplete suggestion bar: three rounded suggestion pills horizontally
  - «встречу» — center pill highlighted with --accent border
  - «обед» — left pill, neutral
  - «совещание» — right pill, neutral
  - Pill styling: 8px padding, 16px horizontal, --bg-elevated background
- Keyboard mock (bottom 30%): simplified rows of small rounded keys

Right-side text: --text-body, --text-primary

Animation: Phone slides in from left. After phone in place: cursor blinks. Autocomplete pills appear one by one, accent pill last with subtle scale-up.

---

#### Slide 13 — Как модель выбирает следующее слово

**Content:**
- Title: «Как модель выбирает следующее слово»
- Sentence with blank: «Совет директоров утвердил ___»
- Bar chart of probabilities
- Caption: «Модель оценивает вероятность каждого слова и выбирает наиболее вероятное. Дальше — то же самое для следующего слова, и так до конца ответа.»

**Visualization:**

Layout: Title block at top. Center: sentence in large type. Below: horizontal bar chart, max-width 800px, centered.

Sentence display:
- --text-h2 serif, --text-primary
- Blank "___" rendered as styled box: 200px wide, --bg-input background, --accent dashed border (1px), inline-block
- Container: --bg-elevated, padding 24px 32px, border-radius 12px, max-width 700px, centered

Bar chart structure:
- Total chart container width: 800px
- Each row contains: word label (160px wide, right-aligned, --text-body, primary, 16px gap on right) + bar area (480px wide, fixed) + percentage label (auto-width, 16px gap on left, --text-h3)
- Bars drawn relative to a reference width of 480px (this represents 22% of available space — i.e., the longest bar uses 480px and shorter bars scale proportionally)

Bars (5 rows):
1. «бюджет» — 22% — bar width: 480px (full reference, longest) — color: --accent
2. «стратегию» — 18% — bar width: 393px (= 480 × 18/22) — color: --text-secondary
3. «решение» — 15% — bar width: 327px — color: --text-secondary
4. «отчёт» — 12% — bar width: 262px — color: --text-secondary
5. «парусник» — 0.0001% — bar width: 1px (intentionally barely visible) — color: --text-muted

Each bar:
- Height: 40px
- Border-radius: 4px right side only (bars start at left edge of bar area)
- Subtle gradient: solid at left end, slight transparency at right
- Word label always at left, percentage label always immediately right of bar

Caption: --text-small, --text-secondary, italic, max-width 700px, centered, 32px gap above.

Animation: Bars grow left-to-right on entry. Stagger top-to-bottom, 80ms apart. Each bar grows over 600ms, ease-out. The "парусник" row label and 0.0001% percentage appear normally, but the bar itself is so thin it almost reads as a dot — the visual punchline.

**Speaker note:** «Не комментируйте 'парусник' с 0.0001%. Если кто-то заметит сам — короткая улыбка достаточна, и движение дальше.»

---

#### Slide 14 — На каких данных модель обучена

**Content:**
- Title: «На каких данных модель обучена»
- Caption: «Большая часть публичного интернета. Но не банковские данные, не клиентские документы, не внутренние процессы.»

**Visualization:**

Layout: Title block at top. Center: data-flow diagram, ~900×500px. 6 source nodes around a central LLM node.

Build as SVG, viewBox 0 0 900 500.

Central LLM node:
- Position: (450, 250)
- Rounded rectangle: 200×100px, centered on position
- Background: --bg-elevated
- Border: 2px --accent
- Inside: «LLM» — --text-h2 serif italic, --accent

Source nodes (6 around center, radius ~280px):
- Top-left (225°): «Wikipedia»
- Top (270°): «Книги»
- Top-right (315°): «Новости»
- Bottom-right (45°): «GitHub»
- Bottom (90°): «Документация»
- Bottom-left (135°): «Форумы»

Each source node:
- Pattern A card style, 160×60px
- --text-body, --text-secondary
- Small leading icon (16px), --accent, line-art

Connecting lines (6, source to LLM):
- 1px stroke
- Gradient: --text-muted (source) to --accent (LLM)
- 3 small flowing dots (4px, --accent), animating from source toward LLM

Caption below diagram (centered, 32px gap):
- --text-small, --text-secondary

Important addition for banker context — small inset block below caption, max-width 700px, --bg-elevated, padding 16px 24px, border-left 3px --warning:
- Text: «Модель не имеет доступа к внутренним системам банка, политикам, продуктам, клиентским данным. Всё, что она 'знает' о банке — публично известное на момент обучения.»
- --text-small --text-secondary

Animation: Sources appear first (fade in together). Lines draw source-to-LLM (300ms each, simultaneous). LLM node fades in last. Inset block fades in after diagram. Then flowing dots loop continuously (4-second loop).

**Speaker note:** «Ключевое наблюдение: модель не хранит факты в виде базы данных — она усреднила статистические закономерности языка. Отсюда два следствия: модель отвечает, даже когда не знает, и эти ответы статистически правдоподобны. Следующие три слайда — конкретные демонстрации.»

---

#### Slide 15 — Пример 1: подсчёт букв

**Content:**
- Title: «Пример 1: подсчёт букв»
- Запрос: «Сколько букв 'о' в слове 'корпоративного'?»
- Screenshot placeholder
- Caption: «Правильный ответ — 4. Типичные ответы модели — 3, 5 или 6. Задача архитектурно сложна для LLM, несмотря на тривиальность для человека.»

**Visualization:**

Pattern F (Demo Two-Column).

Layout: Title block at top. Below: 40/60 split. Caption at bottom, full width.

Left column (40%):
- "ЗАПРОС" label at top (--text-caption, --accent)
- Prompt box: --bg-input, padding 24px, border-radius 12px, font-mono 18px

Right column (60%):
- "РЕЗУЛЬТАТ" label at top (--text-caption, --accent)
- Screenshot placeholder: rectangle 16:9, dashed 1.5px --border-subtle, rounded 12px, --bg-input background
- Inside placeholder: «[SCREENSHOT: ChatGPT даёт неправильный ответ для слова 'корпоративного']» in --text-muted

Below placeholder, overlay annotation:
- Small (--warning) circle with X, top-right of where wrong answer would be
- Annotation in --warning: «Неверно. Правильный ответ — 4.»

Caption: --text-body italic, --text-secondary. Max-width 1000px, centered.

**Speaker note:** «Слово 'корпоративного' содержит 4 буквы 'о' — позиции 2, 7, 10, 12. Прогоните этот запрос вживую за день до занятия — модели иногда обновляются и угадывают. Если демо не сработает, есть запасные слова: 'голословно' (4 о), 'осторожно' (4 о), 'добровольно' (4 о). На самом занятии — не предлагайте аудитории считать буквы вместе с вами, это ловушка для слайда. Просто покажите скриншот неправильного ответа модели и идите дальше.»

---

#### Slide 16 — Пример 2: фабрикация источников

**Content:**
- Title: «Пример 2: фабрикация источников»
- Запрос: «Назови три исследования о связи между корпоративной культурой и операционным риском в банках, с авторами и годами»
- Screenshot placeholder
- Caption: «Авторы выглядят правдоподобно. Журналы существуют. Исследований — нет.»

**Visualization:**

Same as Slide 15 (Pattern F). Three small (--warning) line markers indicating where each fabricated citation would be in the screenshot.

**Speaker note:** «Термин — 'галлюцинация'. Подача без драматизации: модель не обманывает, она просто генерирует статистически правдоподобный текст. Для банковского контекста это критично — фабрикация источников встречается в юридических меморандумах, кредитных решениях, регуляторных справках.»

---

#### Slide 17 — Пример 3: арифметика

**Content:**
- Title: «Пример 3: арифметика»
- Запрос: «Сколько будет 847593 × 392847?»
- Screenshot placeholder
- Caption: «Правильный ответ проверяется калькулятором за две секунды. Модель ошибается стабильно.»

**Visualization:**

Same as Slide 15 (Pattern F).

Below screenshot, comparison row:
- Two cells side by side, 16px gap
- Cell 1: «AI: [число из скриншота]» in --warning, --text-body, --bg-input bg, padding 12px
- Cell 2: «Калькулятор: 332 974 367 271» in --accent, --text-body, --bg-input bg, padding 12px

**Speaker note:** «Правильный ответ: 847593 × 392847 = 332 974 367 271. Прогоните демо заранее на той версии модели, на которой будете показывать. Современные модели иногда подключают калькулятор как внешний инструмент — если демо отказывается ошибаться, попросите 'считать в уме, без инструментов', либо возьмите умножение посложнее (например, 847593 × 392847 × 17).»

---

#### Slide 18 — Главный вывод раздела

**Content:**
- Central line: «AI выдаёт текст, который звучит убедительно. Это не то же самое, что текст, который верен.»
- Subtitle: «Модель не проверяет, знает ли она ответ. Эта проверка — на стороне человека.»

**Visualization:**

Layout: Vertically centered. Single block, max-width 1300px.

Components:
- Main line: --text-display (96px) serif italic, line-height 1.2
- Two-color contrast: «звучит убедительно» in --text-secondary; «верен» in --accent
- Subtitle below, 48px gap: --text-h3 sans regular, --text-secondary, italic

Animation: Main line fades in word by word, 100ms apart. Contrasting words fade in last with subtle emphasis (slight scale-up to 1.02 then back). Subtitle fades in 800ms after main line completes.

**Speaker note:** «Это ключевой тезис занятия. Дайте 5–10 секунд паузы после произнесения. Не комментируйте дополнительно — слайд работает сам.»

---

### BREAK (Slide 19, 10 min)

#### Slide 19 — Перерыв

**Content:**
- «Перерыв»
- «10 минут»

**Visualization:**

Layout: Vertically and horizontally centered.

Components:
- «Перерыв» — --text-display (96px) serif italic, --text-primary
- «10 минут» — --text-h2 sans, --text-secondary, 24px gap above, italic
- Optional countdown timer below, --text-h3, --accent, monospace

Animation: Subtle fade-in. If countdown enabled, ticks down silently.

---

### SECTION 3 — WHERE AI HELPS (Slides 20–24, ~18 min)

#### Slide 20 — Карта применимости

**Content:**
- Title: «Карта применимости»
- 2×2 matrix showing where AI works and where it doesn't.

**Visualization:**

Layout: Title block at top. Center: 2×2 matrix, square, 600×600px, centered.

Build as SVG/HTML grid.

Matrix container: 600×600px, transparent background. Grid lines: 1.5px --border-strong, dividing into 4 quadrants. Outer border: 1.5px --border-strong.

Axes:
- X-axis label below: «Цена ошибки» — --text-caption, secondary
  - End-labels: «низкая» (left) and «высокая» (right) in --text-small --text-muted
- Y-axis label rotated 90° on left: «Возможность проверить» — --text-caption, secondary
  - End-labels: «легко» (bottom) and «сложно» (top), --text-small --text-muted

Quadrant content (each ~290×290px, padding 24px):

Top-left (high verifiability, low cost):
- Label: «УВЕРЕННОЕ ПРИМЕНЕНИЕ» (--text-caption --accent)
- Examples: «Драфтинг писем», «Суммаризация», «Перевод»
- Background: --accent-soft

Top-right (high verifiability, high cost):
- Label: «С КОНТРОЛЕМ» (--text-caption secondary)
- Examples: «Расчёты с проверкой», «Код с тестами», «Юридические формулировки»
- Background: subtle --bg-elevated tint

Bottom-left (low verifiability, low cost):
- Label: «ДОПУСТИМО» (--text-caption secondary)
- Examples: «Брейншторм», «Поиск идей», «Набросок направления»
- Background: subtle --bg-elevated tint

Bottom-right (low verifiability, high cost):
- Label: «ПОВЫШЕННЫЙ РИСК» (--text-caption --warning)
- Examples: «Юридические заключения», «Медицинские оценки», «Финансовые рекомендации»
- Background: --warning-soft

Quadrant typography: label at top, gap 16px, examples as vertical bullet list, --text-small, --text-secondary.

Animation: Matrix structure draws first (axes, then dividers). Quadrant backgrounds fade in. Quadrant content fades in last, all together.

**Speaker note:** «Это рабочий инструмент, не теоретическая модель. Полезно держать в голове перед каждой задачей: где она на этой карте? Три секунды размышления — иногда часы сэкономлены.»

---

#### Slide 21 — Где AI помогает

**Content:**
- Title: «Где AI помогает»
- 7 use cases:
  1. **Черновики** — Письма, презентации, меморандумы
  2. **Суммаризация** — Документы, протоколы, отчёты
  3. **Перевод** — Языки, регистры, стили
  4. **Поиск идей** — Варианты названий, формулировок, гипотез
  5. **Объяснение** — Адаптация сложного материала под аудиторию
  6. **Структурирование** — Превращение разрозненных заметок в связный документ
  7. **Код и формулы** — В том числе для тех, кто не пишет код профессионально

**Visualization:**

Layout: Title block at top. Below: 4+3 grid (4 top, 3 bottom centered). Card width ~300px, gap 24px.

Each card:
- Pattern A
- Top: small icon (32×32px line-art, --accent)
- Title: --text-h3, --text-primary
- Description: --text-small, --text-secondary, 1-2 lines

Icons:
1. pencil
2. stacked-pages-collapsing
3. arrow-between-languages
4. lightbulb
5. question-with-answer
6. structured-blocks
7. code-brackets

Animation: Cards fade in one by one, left to right, top to bottom, 60ms stagger.

---

#### Slide 22 — Пример: черновик письма клиенту

**Content:**
- Title: «Пример: черновик письма клиенту»
- Запрос: «Подготовь черновик письма клиенту private banking. Сообщаем о задержке исполнения операции на 2 рабочих дня в связи с дополнительной проверкой. Тон — корректный, без избыточных извинений, без юридического жаргона. Длина — 5–6 предложений. Закончи указанием контактного лица.»
- Result (sample email):

> Уважаемый Сергей Александрович,
>
> Уведомляем о задержке исполнения операции по вашему счёту на два рабочих дня. Задержка связана с дополнительными процедурами проверки, предусмотренными внутренним регламентом банка.
>
> Средства зарезервированы и будут зачислены не позднее 14 ноября. Никаких действий с вашей стороны не требуется.
>
> Если потребуется уточнение по статусу операции, свяжитесь со мной напрямую: Анна Петрова, персональный менеджер, +7 495 XXX-XX-XX.
>
> С уважением,
> Анна Петрова

- Bottom annotation: «Черновик за 5 секунд. Дальше — обычный процесс: правки, проверка комплаенс, отправка.»

**Visualization:**

Pattern F, but 50/50 split (result is text not screenshot).

Left column (Prompt):
- "ЗАПРОС" label
- --bg-input, font-mono 16px (smaller since prompt is long), padding 24px
- Highlighted phrases in --accent: «private banking», «корректный», «5–6 предложений», «контактного лица»

Right column (Result):
- "РЕЗУЛЬТАТ" label
- --bg-elevated, --text-body 18px, padding 24px
- The sample email above, formatted with paragraph breaks

Bottom (full width, 32px below):
- --text-small italic, --text-muted

---

#### Slide 23 — Пример: суммаризация

**Content:**
- Title: «Пример: суммаризация»
- Output bullets (concrete, not placeholders):
  1. Чистая прибыль за квартал — 4,2 млрд ₽ (+12% к прошлому кварталу)
  2. Главный драйвер — рост в розничном сегменте, особенно ипотека
  3. Основной риск — концентрация портфеля на 3 крупнейших корпоративных клиентах
  4. Рекомендация — диверсификация корп. портфеля в течение 6 месяцев
  5. Открытый вопрос — влияние новой ставки ЦБ на спрос в Q4
- Caption: «Один из пунктов оказался выводом, которого в исходном тексте не было. Удалил при проверке. Это нормальный режим работы с AI, а не аномалия.»

**Visualization:**

Layout: Title block at top. Center: side-by-side input → output, with arrow. 40% / 20% (arrow zone) / 40%.

Left side — Input:
- Stylized "thick document" graphic
- Stack of 14 horizontal lines suggesting text
- Container: 320×400px, --bg-elevated, padding 24px
- Top: «АНАЛИТИЧЕСКИЙ ОТЧЁТ» --text-caption --text-muted
- Bottom: «14 страниц» --text-small --text-secondary

Center — Arrow zone (240px wide):
- Large rightward arrow, --accent, 1.5px stroke
- Above: «AI обрабатывает» --text-caption --text-muted
- Below: «8 секунд» --text-small --accent

Right side — Output:
- Container: 320×400px (auto-height if needed up to 480px), --bg-elevated, padding 24px
- Top: «КЛЮЧЕВЫЕ ВЫВОДЫ» --text-caption --accent
- 5 bullets from content above, --text-small primary, line-height 1.4
- Each bullet has subtle "•" marker in --accent

Caption below (full width, 48px gap): --text-small italic, --text-muted, max-width 900px, centered.

---

#### Slide 24 — Пример: заметки → документ

**Content:**
- Title: «Пример: заметки → документ»

Left side input — chaotic notes (varying indentation, mixed bullet styles):
- «- решили по бюджету Q3»
- «    нужно ИТ согласие»
- «* кто отвечает за поставщика?»
- «дедлайн 15-е»
- «поменять процесс согласования (!)»
- «- юр.отдел согласует к среде»
- «открытый: лимиты по клиентам?»

Right side output — structured protocol:

**РЕШЕНИЯ**
- Бюджет Q3 утверждён в текущей редакции
- Процесс согласования подлежит пересмотру

**ДЕЙСТВИЯ**
- Получить согласование ИТ — отв. И. Иванов, до среды
- Юр. отдел согласует — отв. М. Сидорова, до среды

**ОТКРЫТЫЕ ВОПРОСЫ**
- Лимиты по клиентам — требуется отдельная встреча

**СРОКИ**
- Поставщик: ответственный определяется до 15-го числа

**Visualization:**

Layout: Title block at top. Center: 50/50 side-by-side with arrow.

Left side — Chaotic notes:
- Container: 380×400px, --bg-elevated, padding 24px
- Header: «ЗАМЕТКИ СО ВСТРЕЧИ» --text-caption --text-muted
- Use --text-small --text-secondary for content
- Visual cues of mess: varying left-padding (0px, 24px, 16px, 0px, 0px, 0px, 0px), mixed bullet styles (-, *, none), some with "(!)" and "?"

Center arrow zone (~120px wide, similar style to Slide 23).

Right side — Structured:
- Container: 380×400px, --bg-elevated, padding 24px
- Header: «СТРУКТУРИРОВАННЫЙ ПРОТОКОЛ» --text-caption --accent
- 4 sections with --text-caption --accent headers, then --text-small primary bullets
- Section gap: 16px
- Bullet indent: 16px

---

### SECTION 4 — RISKS (Slides 25–29, ~18 min)

#### Slide 25 — Где AI создаёт риски

**Content:**
- Title: «Где AI создаёт риски»
- Same matrix from Slide 20, danger quadrant emphasized
- Updated examples in danger quadrant:
  - «Юридические заключения без проверки юристом»
  - «Финансовые расчёты без верификации»
  - «Медицинские оценки»
  - «Решения по конкретным клиентам или сотрудникам»
  - «Регуляторная отчётность»

**Visualization:**

Identical to Slide 20 matrix. Differences:
- Bottom-right quadrant: --warning-soft 35% opacity (was 18%)
- Bottom-right border: 2px --warning
- Other 3 quadrants: backgrounds reduced to 5% opacity

Animation: Matrix appears as in Slide 20. Bottom-right quadrant border pulses once (1px → 3px → 2px) over 600ms. Examples fade in one by one, 100ms stagger.

---

#### Slide 26 — Уверенность модели не равна её компетентности

**Content:**
- Title: «Уверенность модели не равна её компетентности»
- Line chart.

**Visualization:**

Layout: Title block at top. Center: line chart, 800×500px.

Build as SVG, viewBox 0 0 800 500.

Axes:
- X: bottom, label «Сложность задачи» (--text-caption secondary)
- Y: left, label «Уровень (компетентность / уверенность)» (--text-caption secondary, rotated 90°)
- Both axes: 1px --border-strong
- 4 vertical grid lines (--border-subtle, 1px)
- 5 horizontal grid lines (0%, 25%, 50%, 75%, 100%)

Three lines:

Line 1 — Человек (combined):
- Path: (40, 60) → (760, 380), step-like descent through 5 points
- Stroke: 2.5px --text-secondary, solid
- 5px dots at data points

Line 2 — AI компетентность:
- Path: same descent as human
- Stroke: 2px --text-muted, dashed (4-4)

Line 3 — AI уверенность (key surprise):
- Path: stays flat at y=80
- Slight wave to suggest noise but staying high
- Stroke: 2.5px --accent, solid

Legend (top-right of chart):
- 3 entries with line samples:
  - «Человек: уверенность ≈ компетентность» (--text-secondary)
  - «AI: компетентность» (dashed --text-muted)
  - «AI: уверенность» (--accent, solid)
- --text-small

Annotations:
- "Человек: уверенность снижается вместе с компетентностью" — pointing to bottom of human line
- "AI: уверенность не зависит от компетентности" — pointing to top-right of AI confidence line, --accent

Animation: Axes draw first. Human line draws left-to-right (800ms). AI competence line draws (800ms). AI confidence line draws (1000ms). Annotations fade in last.

**Speaker note:** «Этот разрыв между уверенностью и компетентностью — главный источник операционного риска при работе с LLM. Подача без драматизации — это просто свойство модели, его нужно учитывать.»

---

#### Slide 27 — Где AI стабильно ошибается

**Content:**
- Title: «Где AI стабильно ошибается»
- 6 cards (was 5 — added bias/fairness, critical for banking):
  1. **Свежие факты** — События после даты обучения модели
  2. **Точные цифры** — Арифметика без внешних инструментов
  3. **Узкоспециальные знания** — Локальные регуляции, узкая нормативная база
  4. **Источники и цитаты** — Фабрикация при сохранении уверенного тона
  5. **Сведения о людях** — Вымышленные биографические данные
  6. **Системные смещения** — Предвзятость по полу, возрасту, языку — унаследована из обучающих данных

**Visualization:**

Layout: Title block at top. Below: 6 cards in 3+3 grid (was 5 cards in row — restructured for the added 6th card).

Each card:
- Pattern A
- Top: number "01"–"06" in --text-h2 serif italic --accent
- Title: --text-h3 primary
- Description: --text-small secondary, 2 lines

Card 6 has additional small footnote in --text-caption --text-muted: «Особо чувствительно в кредитных решениях, HR-процессах, клиентском скоринге.»

**Speaker note:** «Шестой пункт — про bias — для банка особенно важен. Если AI используется в скоринге, HR-процессах, клиентских коммуникациях, унаследованные смещения превращаются в регуляторный и репутационный риск напрямую. Это отдельная область, к которой нужен системный подход — не просто 'проверить ответ'.»

---

#### Slide 28 — Что происходит с данными, которые попадают в AI

**Content:**
- Title: «Что происходит с данными, которые попадают в AI»
- 4-step flow:
  1. **Ваш текст** — Ввод данных в публичный чат — выглядит как локальная сессия
  2. **Серверы провайдера** — OpenAI / Anthropic / Google — текст уходит туда
  3. **Может использоваться для обучения** — В публичных версиях — как правило. В корпоративных — обычно нет.
  4. **Может проявиться в чужих ответах** — Редкий, но задокументированный сценарий
- Caption: «Простое правило: если эти данные нельзя отправить внешнему получателю по обычной почте — в публичный AI-инструмент их тоже нельзя.»

**Visualization:**

Pattern E (Process Step), 4 steps.

Layout: Title block at top. Center: 4-step horizontal flow, full content width.

Each step:
- "ШАГ 1-4" eyebrow, --text-caption --accent
- Title (--text-h3)
- Description (--text-small --text-secondary)
- Icon

Step icons:
1. keyboard or chat-bubble outline
2. cloud
3. stacked-circles
4. discreet warning triangle, --warning color

Connecting arrows: chevron arrows, --border-strong, with subtle dot animation.

Caption below diagram (48px gap):
- --text-body italic, --accent, max-width 1100px, centered, with subtle accent border-left at 3px

Animation: Steps appear left-to-right, 200ms stagger. After all visible, dots flow along arrows in continuous loop.

**Speaker note:** «Это касается публичных версий. Корпоративные подписки (ChatGPT Enterprise, Claude for Work и аналоги), как правило, не используют пользовательские данные для дообучения. Но это нужно проверять в условиях договора, а не предполагать. Также полезно упомянуть — для финансовой отрасли есть отдельный регуляторный пласт: требования по защите банковской тайны, локализации данных, согласованию работы с зарубежными вендорами. Эти требования не отменяются тем, что 'мы используем Enterprise-версию'.»

---

#### Slide 29 — Несколько публичных случаев

**Content:**
- Title: «Несколько публичных случаев»
- 3 cases:

**Visualization:**

Layout: Title block at top. Below: 3 stacked cards, full content width, gap 16px.

Each card:
- Pattern A, padding 32px
- Inside: horizontal split — date+entity on left (30%), description on right (70%)
- Left:
  - Date in --text-caption uppercase --accent
  - Entity in --text-h3
- Right:
  - Description in --text-body, --text-secondary
- Subtle bottom-border: 1px --accent-line

Cards:

Card 1:
- 2023, Нью-Йорк / Юристы Mata v. Avianca
- «Адвокаты подали в суд документ с цитатами на несуществующие судебные решения, сгенерированные ChatGPT. Суд оштрафовал двух адвокатов и фирму на $5 000 каждого. Дисциплинарное разбирательство в коллегии.»

Card 2:
- 2024 / Air Canada
- «Чат-бот авиакомпании ввёл клиента в заблуждение по условиям тарифа на похоронные перелёты — клиент полагался на ответ бота, бронируя перелёт. Авиакомпания заявила, что не отвечает за ответы своего AI. Tribunal обязал выплатить компенсацию.»

Card 3:
- 2023 / Samsung
- «Инженеры вставили в ChatGPT внутренний код для отладки. Часть кода — конфиденциальная. Компания ввела внутренний запрет на использование публичных AI-инструментов с рабочих устройств.»

Animation: Cards fade in top-to-bottom, 150ms stagger.

**Speaker note:** «Это публичные случаи. Аналогичные инциденты регулярно проходят через департаменты операционного риска — просто не попадают в новости. Подача без сенсационности. Если в зале спросят про российские кейсы — публичных пока мало, но в банковской среде уже есть прецеденты по утечкам через AI-ассистентов в IT-отделах. Имена не назывем, отвечаем общим тезисом: 'аналогичные ситуации обсуждаются на уровне регулятора и операционного риска'.»

---

### SECTION 5 — RESPONSIBILITY (Slides 30–32, ~10 min)

*Note: v6 removes the standalone "junior assistant analogy" slide that was previously slide 30. The workflow on slide 30 (formerly 31) makes the same point with more substance.*

#### Slide 30 — Корректный рабочий процесс

**Content:**
- Title: «Корректный рабочий процесс»
- Subtitle: «Аналогия — AI как младший ассистент: готовит черновик. Решения и подпись — за человеком.»
- 4 steps:
  1. **AI готовит** — Черновик, вариант, заготовка
  2. **Человек проверяет** — Факты, цифры, формулировки, регуляторный контекст
  3. **Человек принимает решение** — Принять, доработать, отклонить
  4. **Человек несёт ответственность** — За результат и его последствия

**Visualization:**

Layout: Title block at top (with subtitle below title in --text-h3 secondary). Below: 4-step horizontal flow (Pattern E). Last step visually emphasized.

Each step: number ("01"-"04"), title, description.

Step 4 visual emphasis: --accent border (2px), scale 1.05, --accent-soft tint background.

Connecting arrows: standard. Arrow before step 4 thicker and --accent.

Animation: Cards appear left-to-right (250ms stagger). Final card snaps into place with subtle scale.

---

#### Slide 31 — Кто отвечает за ошибку AI

**Content:**
- Title: «Кто отвечает за ошибку AI»
- Central answer: «Тот, кто использовал AI и подписал результат.»
- Below: «Не вендор, не модель, не 'AI вообще'. Сотрудник и организация.»
- Small note: «Регулятор не примет аргумент 'это нам ChatGPT написал'.»

**Visualization:**

Layout: Title block at top. Vertical center: text-only composition, max-width 1100px.

Components:
- Title (eyebrow size, secondary)
- Main answer: --text-display (96px) serif italic, --text-primary
- Single observational sentence: --text-h3 --text-secondary, 32px gap
- Small note (32px gap): --text-small italic --text-muted

Animation: Main answer fades in. Sentence appears. Small note fades in last.

---

#### Slide 32 — Принцип ответственности

**Content:**
- Central line: «Если вы это отправили — вы это написали.»
- Subtitle: «Не имеет значения, что черновик готовил AI. Подпись определяет авторство.»

**Visualization:**

Layout: Vertically centered. Single block, max-width 1300px.

Components:
- Main: --text-display (96px) serif italic, --text-primary
  - Em-dash gets --text-muted (read as pause)
- Subtitle: --text-h3 sans regular, --text-secondary, italic, 48px gap above

Below subtitle (small, optional, 80px gap):
- Tiny line in --text-caption --text-muted: «Раздел 5 — ответственность»

This is a "weighty" slide — extra padding, lots of whitespace.

Animation: Main fade in, then barely-perceptible scale-up from 0.98 to 1 (700ms). Subtitle fades in 600ms after.

**Speaker note:** «Это операциональный тест для процесса работы с AI. Если в любой точке принцип 'отправил = написал' выполняется без оговорок — процесс выстроен корректно.»

---

### SECTION 6 — PRINCIPLES (Slides 33–38, ~14 min)

#### Slide 33 — Пять рабочих принципов

**Content:**
- Title: «Пять рабочих принципов»
- 5 principles:
  1. Контекст важнее команды
  2. Проверять — раньше, чем доверять
  3. Никаких чувствительных данных
  4. AI — для черновиков, не для финалов
  5. Не можете проверить — не используйте

**Visualization:**

Layout: Title block at top. Below: 5 cards, 3+2 arrangement (3 top, 2 bottom centered).

Each card: Pattern C numbered card, title-only:
- Number 01-05, --text-display (96px) serif italic --accent
- Title below number, --text-h3 --text-primary

Animation: Cards fade in numerically, 150ms apart.

---

#### Slide 34 — Принцип 1: Контекст важнее команды

**Content:**
- Title: «Принцип 1: Контекст важнее команды»
- Two-column:
  - **МАЛО КОНТЕКСТА:** «Напиши служебную записку про оптимизацию процесса.»
  - **ДОСТАТОЧНО КОНТЕКСТА:** «Я — руководитель департамента. Записка для члена правления, который не погружён в детали. Тон — деловой, без жаргона. Контекст: текущий процесс согласования занимает 14 дней, цель — сократить до 5. Длина — одна страница. Закончи тремя вариантами решения с оценкой рисков каждого.»

**Visualization:**

Layout: Title block at top. Below: Pattern B (Two-column).

Left column:
- Header: «МАЛО КОНТЕКСТА» --text-caption --text-muted, with --text-secondary underline (60px, 2px)
- Below: prompt box, --bg-input, font-mono 16px, padding 24px

Right column:
- Header: «ДОСТАТОЧНО КОНТЕКСТА» --text-caption --accent, with --accent underline
- Below: prompt box, --bg-input, font-mono 16px, padding 24px
- Highlighted phrases in --accent: «руководитель департамента», «член правления», «деловой, без жаргона», «14 дней... 5», «одна страница», «тремя вариантами»
- Below prompt, annotation row: «РОЛЬ — АУДИТОРИЯ — ТОН — КОНТЕКСТ — ФОРМАТ — ЦЕЛЬ»
  - Small tags, --text-caption, --accent, with thin lines from each phrase to its label

Animation: Both prompts appear. Highlights and annotation labels appear last, 300ms stagger.

---

#### Slide 35 — Принцип 2: Проверять до того, как доверять

**Content:**
- Title: «Принцип 2: Проверять до того, как доверять»
- 4 checklist items:
  - Цифры и даты — проверить вручную или через первоисточник
  - Цитаты, ссылки, нормативные акты — найти оригинал
  - Юридические, медицинские, финансовые утверждения — спросить эксперта
  - Имена, должности, биографические данные — сверить с открытыми источниками

**Visualization:**

Layout: Title block at top. Below: vertical checklist, max-width 900px, centered.

Each item:
- Horizontal flex, gap 24px
- Left: checkmark icon, 24×24px, SVG: circle with checkmark
  - Circle: 1.5px --accent stroke
  - Checkmark: --accent
- Right: --text-body --text-primary

Item spacing: 24px. Item background: subtle --bg-elevated, padding 16px, border-radius 8px.

Animation: Items fade in top-to-bottom. Each checkmark draws (stroke animation, 400ms).

---

#### Slide 36 — Принцип 3: Никаких чувствительных данных

**Content:**
- Title: «Принцип 3: Никаких чувствительных данных»
- List header: «НЕ ПЕРЕДАЁМ В ПУБЛИЧНЫЕ AI-ИНСТРУМЕНТЫ»
- 5 items:
  - Персональные данные клиентов (ФИО, паспорт, ИНН, счета)
  - Внутренние документы — кредитные меморандумы, материалы комитетов
  - Финансовая отчётность до публикации
  - Внутренние коммерческие переписки и стратегические документы
  - Исходный код банковских систем
- Callout:
  - Eyebrow: «ПРОСТАЯ ПРОВЕРКА»
  - Main: «Отправил бы я эти данные внешнему получателю по обычной почте?»
  - Below: «Если ответ — нет, в AI-инструмент тоже не отправляю.»

**Visualization:**

Layout: Title block at top. Below: list (60% width) + callout box (40% width), side by side.

Left (list):
- Header: --text-caption --warning
- 5 items, each with X icon (--warning, 1.5px stroke)

Right (callout):
- --bg-elevated background
- Border-left: 3px --accent
- Padding: 32px
- Eyebrow --text-caption
- Main --text-h3 italic --text-primary
- Below --text-small --text-secondary

Animation: List items appear top-to-bottom. Callout fades in last.

---

#### Slide 37 — Принцип 4: AI готовит черновик, финал — за человеком

**Content:**
- Title: «Принцип 4: AI готовит черновик, финал — за человеком»
- Central insight: «AI делает 80% работы за 20% времени. Последние 20% — самые важные — за человеком.»
- 80/20 visualization
- "ЧТО ВХОДИТ В ПОСЛЕДНИЕ 20%":
  - Проверка фактов
  - Точность формулировок
  - Тон под получателя
  - Регуляторный контекст
  - Репутационные нюансы

**Visualization:**

Layout: Title block at top. Center: 80/20 horizontal bar, full width 900px. Below: explanation of 20%.

Bar container: 900×80px, --bg-elevated, border-radius 12px, overflow hidden.
- Left segment (80%): width 720px, --bg-input background, label «AI: 80% объёма за 20% времени» --text-small --text-secondary, centered
- Right segment (20%): width 180px, --accent-soft background, --accent 2px border, label «Человек: критические 20%» --text-small --accent semibold, centered

Right segment visually emphasized (border, slight scale-up to 1.02 on entry).

Below bar (48px gap):
- Title: --text-caption --accent
- 5 items as small horizontal pills:
  - Each pill: --bg-elevated, padding 8px 16px, border-radius 24px, --text-small primary

Animation: Bar fills left-to-right (1000ms). 20% segment "claims" itself (scale 1 → 1.05 → 1.02, 300ms after fill). Pills appear after, 80ms stagger.

---

#### Slide 38 — Принцип 5: Не можете проверить — не используйте

**Content:**
- Title: «Принцип 5: Не можете проверить — не используйте»
- 3 items:
  - Не разбираетесь в теме — не сможете отличить точное от выдуманного
  - Нет времени проверить — не используйте AI для этой задачи
  - Узкоспециальная область — AI скорее ошибётся, а вы скорее не заметите
- Final statement: «Иногда правильное решение — не использовать AI вовсе.»

**Visualization:**

Layout: Title block at top. Below: 3-item list (centered, max-width 900px). Bottom: final statement.

List items:
- Each with small "→" arrow (--accent), then text in --text-body --text-primary
- Spacing 24px between

Below list (64px gap), takeaway:
- Container: full content width, --bg-elevated, padding 32px, border-left 3px --accent
- Text: --text-h2 serif italic --text-primary

Animation: List items fade in top-to-bottom. Takeaway block slides in from below, 400ms after list completes.

---

### SECTION 7 — DIAGNOSTIC (Slides 39–41, ~25 min)

#### Slide 39 — Где вы сейчас в работе с AI

**Content:**
- Eyebrow: «Практическая часть»
- Main: «Где вы сейчас в работе с AI»
- Subtitle: «Личная диагностика — 25 минут»
- Format: 3 phases timeline.

**Visualization:**

Layout: Vertically centered. Top: text block. Below: 3-stage timeline.

Text block (centered):
- Eyebrow: --text-caption --accent
- Main: --text-display serif italic primary
- Subtitle: --text-h3 secondary

Below (80px gap), 3 stages in row, connected by lines:

Stage 1:
- Icon: single person silhouette
- Title: «Индивидуально»
- Time: «5 минут»
- Description: «Запишите ответы на 4 вопроса»

Stage 2:
- Icon: two people facing each other
- Title: «В парах»
- Time: «10 минут»
- Description: «Обмен ответами»

Stage 3:
- Icon: circle of people
- Title: «Общий круг»
- Time: «10 минут»
- Description: «Обсуждение результатов»

Each stage card uses Pattern A. Connecting lines with arrowheads.

Animation: Text block fades in. Stages appear left-to-right, 200ms stagger.

---

#### Slide 40 — Запишите ответы на четыре вопроса

**Content:**
- Title: «Запишите ответы на четыре вопроса»
- 4 questions:

**Visualization:**

Layout: Title block at top. Below: 4 questions in 2×2 grid, generous spacing.

Each card:
- Pattern A, padding 40px
- Number 01-04 in top-left, --text-display serif italic --accent
- Question in --text-h3 --text-primary
- Subtitle in --text-small --text-secondary

Cards:

01. «Где я уже использую AI в работе?»
    Subtitle: «Задачи, инструменты, частота»

02. «Где я сознательно его избегаю — и почему?»
    Subtitle: «Причины: недоверие, непонимание, риск, привычка»

03. «Когда AI меня подводил?»
    Subtitle: «Что произошло, какой вывод сделал»

04. «Какую одну задачу попробую с AI на этой неделе?»
    Subtitle: «Конкретная задача с планом проверки»

Optional decorative element: subtle "notebook page" feel — very faint horizontal lines across cards in --border-subtle.

Animation: Cards fade in clockwise from top-left.

**Speaker note:** «Раздайте бумажные формы либо попросите открыть заметки в устройстве. Письменный формат критичен — устные ответы дают существенно меньшую глубину анализа. Подчеркните, что записи остаются у участников.»

---

#### Slide 41 — Поделитесь и обсудим

**Content:**
- Title: «Поделитесь и обсудим»
- Two cards:
  - **В ПАРАХ — 10 МИНУТ** / «Поделитесь ответами» / «Обмен ответами в парах. Особое внимание — случаям, когда AI давал некорректный результат.»
  - **ОБЩИМ КРУГОМ — 10 МИНУТ** / «Что увидели вместе» / «Повторяющиеся паттерны. Доминирующие риски. Кандидаты на пилотирование.»
- Discussion prompts:
  - Структура использования: кто, где, в каких задачах
  - Структура избегания: причины и обоснования
  - Системные риски: что требует внимания на уровне процессов банка

**Visualization:**

Layout: Title block at top. Below: two-stage layout (50/50). Bottom: discussion prompts.

Two-stage cards (Pattern A):
- Header (--text-caption --accent), Title (--text-h2), Description, 48px icon

Bottom (32px gap), discussion prompts:
- Header: «ВОПРОСЫ ДЛЯ ОБЩЕГО ОБСУЖДЕНИЯ» --text-caption --accent
- 3 prompts as Pattern A cards in row

---

### SECTION 8 — WRAP-UP (Slides 42–44, ~5 min)

#### Slide 42 — Главное за сегодня

**Content:**
- Title: «Главное за сегодня»
- 5 takeaways:
  1. AI — мощное автодополнение. Уверенный тон не означает корректный ответ.
  2. Сильные стороны: черновики, суммаризация, структурирование. Слабые: факты, расчёты, источники.
  3. Чувствительные данные не передаются. Проверка: можно ли отправить эти данные внешнему получателю по почте.
  4. Проверка — на человеке. Подпись — ваша. Регулятор не примет «AI написал».
  5. Пять принципов: контекст, проверка, безопасность, черновики, проверяемость.

**Visualization:**

Layout: Title block at top. Below: 5 numbered takeaways, vertical list, max-width 1100px.

Each row:
- Horizontal flex, gap 24px
- Left: large number (01-05), --text-h1 serif italic --accent, fixed width 80px
- Middle: small section-recap icon (24px, --accent)
- Right: takeaway text, --text-body --text-primary

Item spacing: 32px. Each row subtle bottom border --border-subtle.

Animation: Rows fade in top-to-bottom, 100ms stagger.

---

#### Slide 43 — Что дальше

**Content:**
- Eyebrow: «Что дальше»
- Lesson 2 title: «Занятие 2: [тема следующего занятия — заполнить]»
- Teaser: «На следующей встрече — формулирование запросов и границы того, что решается техникой.»

**Visualization:**

Layout: Vertically centered. Single column, max-width 1100px, generous spacing.

Components:
- Eyebrow: --text-caption --text-muted
- Lesson 2 title: --text-h1 serif italic primary (PLACEHOLDER)
- Teaser: --text-h3 secondary, 32px gap above

Animation: Subtle staggered fade-in from top.

---

#### Slide 44 — Спасибо

**Content:**
- Single line: «Спасибо за внимание.»

**Visualization:**

Layout: Vertically and horizontally centered. Single line.

Components:
- Text: --text-display (96px) serif italic, --text-primary
- Above: thin accent line, 80px wide, 2px tall, --accent, 64px gap below

Animation: Subtle fade-in over 800ms.

---

## Implementation Notes for Claude Code

**Tech stack:**
- Single `index.html` file with embedded CSS and JS
- All visualizations as inline SVG — no external image dependencies
- Slide framework: Reveal.js with custom theme OR custom solution with CSS scroll-snap + keyboard handlers (arrows + space forward, shift+arrow back, esc overview, F fullscreen)

**Fonts (Google Fonts) — with `font-display: swap`:**
- Source Serif Pro (regular, italic, bold-italic) — Cyrillic support
- Inter (regular, semibold) — Cyrillic support
- IBM Plex Mono (regular) — for prompt boxes
- Fallbacks defined in font stack

**Animation principles:**
- All transitions use ease-out cubic-bezier(0.16, 1, 0.3, 1)
- Stagger delays: 80ms small items, 200ms major elements
- No bouncing, no flashy effects, no parallax
- Slide transitions: cross-fade, 400ms
- Respect `prefers-reduced-motion`: disable all decorative animations

**Interactions:**
- Slides 15, 16, 17 (demos): clicking screenshot placeholder reveals hidden state — overlay stylized "✗" + text "Неверно"
- Slide 8 (nested circles): hover on each circle highlights and shows tooltip with description

**Accessibility:**
- Adequate contrast (#f4f4f5 on #0d0d10 ratio ~16:1)
- Full keyboard navigation
- ARIA labels on all SVG visualizations
- Focus indicators visible

**Print stylesheet (PDF export):**
- Each slide as one A4 landscape page
- Background dark preserved (use `print-color-adjust: exact`)
- All animations disabled (`* { animation: none !important; transition: none !important; }`)
- Slide chrome (page numbers, progress bar) simplified
- Demo screenshot placeholders remain visible
- Allow user to print/save-as-PDF from browser standard interface

**Output structure:**
```
/output
  index.html        ← single self-contained file
  /screenshots      ← empty folder for demo screenshots
    slide-15.png
    slide-16.png
    slide-17.png
  README.md         ← run instructions, placeholder fill guide, pre-session checklist
```

**Manual placeholders to fill after generation:**
- Slides 15, 16, 17 — actual screenshots from running demos
- Slide 43 — title of Lesson 2

---

## Pre-Session Checklist (include in README)

**Day before the session:**

- [ ] Run all three demos on the same model/version that will be shown live
  - Slide 15: «Сколько букв 'о' в слове 'корпоративного'?» — confirm model gives wrong answer
  - Slide 16: «Назови три исследования о связи между корпоративной культурой и операционным риском в банках» — confirm fabrication
  - Slide 17: «Сколько будет 847593 × 392847?» — confirm wrong answer (correct answer: 332 974 367 271)
- [ ] Take screenshots of each failure and place in `/screenshots/` folder
- [ ] If a demo unexpectedly succeeds, use a backup:
  - Letter count: try «голословно», «осторожно», «добровольно» (all have 4 о)
  - Math: try a longer multiplication, or add «без использования инструментов»
  - Citations: try a more obscure topic
- [ ] Fill in slide 43 — title of upcoming Занятие 2
- [ ] Test the deck in fullscreen on the actual presentation device
- [ ] Test the deck with the actual conference projector resolution if possible

**Day of the session:**

- [ ] Open the deck in browser, verify fonts loaded, verify all slides render
- [ ] Verify screenshots show correctly on slides 15, 16, 17
- [ ] Print/save as PDF as backup if browser fails
- [ ] Have water, paper handouts of the diagnostic exercise (slide 40), pens
- [ ] Have a separate browser tab open with the live AI model in case any participant asks "but does it really do that?" — prepared to demo on demand

**During the session:**

- [ ] If a participant tries the demo on their own device and gets a different result — acknowledge it, note that model versions differ, and emphasize that the *pattern* (confident wrong answers) is the point, not any specific instance
- [ ] If running long: trim Section 6 (principles) presentation — the slides can be flipped through quickly and the principles work as a handout. Never trim Section 7 (diagnostic).

---

## Three Filters for Every Line

Before any line ships, it passes:

1. **Could a senior internal expert say this to fellow executives without the room shifting uncomfortably?** If too cold → warm slightly. If too cheerful → cut warmth.
2. **Does it lecture, narrate, or moralize?** If yes, cut.
3. **Does «вы» actually do work, or is it just being friendly?** If just friendly, replace with a noun phrase. If it makes the line land harder — keep it.

The deck should read like a senior advisor briefing peers — professional, honest, occasionally warm where the moment earns it. Quiet authority. Not a sales pitch, not a McKinsey audit, not a workshop.
