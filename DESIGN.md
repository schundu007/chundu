---
name: Sudhakar Chundu Portfolio
description: Staff DevOps/SRE portfolio — precision instrumentation for FAANG-level hiring
colors:
  zinc-black: "#09090b"
  zinc-surface: "#18181b"
  zinc-panel: "#27272a"
  chalk-white: "#fafafa"
  zinc-mist: "#a1a1aa"
  zinc-fog: "#71717a"
  alert-lime: "#E0FF4F"
  alert-lime-deep: "#c8e63d"
  warm-ivory: "#FEFDFB"
  warm-ivory-secondary: "#F9F8F4"
typography:
  display:
    fontFamily: "Sora, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "clamp(2.25rem, 5vw, 3.5rem)"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Sora, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "clamp(1.75rem, 3vw, 2.5rem)"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Sora, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "clamp(1.125rem, 1.5vw, 1.35rem)"
    fontWeight: 600
    lineHeight: 1.35
  body:
    fontFamily: "Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "JetBrains Mono, Fira Code, monospace"
    fontSize: "0.75rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.12em"
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  full: "9999px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "32px"
  xl: "48px"
  2xl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.alert-lime}"
    textColor: "{colors.zinc-black}"
    rounded: "{rounded.md}"
    padding: "0.75rem 1.5rem"
    typography: "{typography.body}"
  button-primary-hover:
    backgroundColor: "{colors.alert-lime-deep}"
    textColor: "{colors.zinc-black}"
  button-secondary:
    backgroundColor: "{colors.zinc-panel}"
    textColor: "{colors.chalk-white}"
    rounded: "{rounded.md}"
    padding: "0.75rem 1.5rem"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.chalk-white}"
    rounded: "{rounded.md}"
    padding: "0.75rem 1.5rem"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.zinc-mist}"
    rounded: "{rounded.md}"
    padding: "0.5rem 1rem"
  tag-chip:
    backgroundColor: "{colors.zinc-panel}"
    textColor: "{colors.zinc-mist}"
    rounded: "{rounded.full}"
    padding: "0.35rem 0.85rem"
---

# Design System: Sudhakar Chundu Portfolio

## 1. Overview

**Creative North Star: "The Signal Board"**

This is a precision instrumentation aesthetic, not a marketing aesthetic. The design operates the way a well-configured monitoring system does: information surfaces exactly when it's needed, hierarchy communicates priority at a glance, and the accent color carries one meaning only — a live indicator, not decoration. Every layout decision is defensible as a structural choice.

The surface is almost entirely Zinc Black and zinc neutrals. A single Alert Lime occupies less than 8% of any screen — used on CTAs, active states, date chips, and hover indicators. That rarity is the mechanism. When recruiter eyes land on the lime, it marks exactly what matters: a call to action, a live system, a highlight worth reading.

This system explicitly rejects generic developer portfolio templates (same hero + skills grid + contact form, repeated endlessly), agency-portfolio scroll-jacking and particle flair, and dark-SaaS clichés like purple-to-pink gradients, neon glassmorphism cards, and hero-metric stat blocks.

**Key Characteristics:**
- Near-achromatic dark base: three zinc steps (#09090b → #18181b → #27272a) carry all depth
- Single functional accent: Alert Lime is a status indicator, not a design flourish
- Typographic hierarchy does the heavy lifting: scale ratios exceed 1.3× between steps
- Shadows respond to interaction: flat at rest, ambient depth on hover
- Monospace as a semantic signal: JetBrains Mono appears only on labels, dates, and code — meaning "technical fact"

## 2. Colors

One base, one accent. The Zinc Black family supplies all neutral depth; Alert Lime supplies all energy.

### Primary
- **Alert Lime** (`#E0FF4F`): The single functional accent. Used on primary CTAs, active nav indicators, date chips, tag hover states, and interactive focus rings. Rarity is the rule: ≤8% of any given screen surface. In light mode, shifts to `#84cc16` (lime-500) for sufficient contrast on Warm Ivory.
- **Alert Lime Deep** (`#c8e63d`): Hover-state darkening of the primary accent only. Never used at rest.

### Neutral
- **Zinc Black** (`#09090b`): Page background in dark mode. The foundation.
- **Zinc Surface** (`#18181b`): Card backgrounds, the nav backdrop. One step above the page floor.
- **Zinc Panel** (`#27272a`): Tertiary surfaces, hover states, tag backgrounds. Second step above.
- **Chalk White** (`#fafafa`): Primary text on dark surfaces. Near-white, not pure white.
- **Zinc Mist** (`#a1a1aa`): Secondary text, nav link default state, supporting copy.
- **Zinc Fog** (`#71717a`): Muted text, placeholders, metadata. Minimum use for anything that needs to be read.
- **Warm Ivory** (`#FEFDFB`): Light mode page background. Warm-tinted, not clinical white.
- **Warm Ivory Secondary** (`#F9F8F4`): Light mode secondary surfaces and card backgrounds.

### Named Rules
**The One Signal Rule.** Alert Lime appears on ≤8% of any screen. It marks CTAs, active states, and date chips only. A second lime element in the same viewport dilutes the signal; rewrite the layout before adding more lime.

**The No-Pure-White Rule.** Neither pure white (`#ffffff`) nor pure black (`#000000`) appears anywhere. Zinc Black (`#09090b`) and Chalk White (`#fafafa`) are the extremes.

## 3. Typography

**Display Font:** Sora (with -apple-system, BlinkMacSystemFont fallback)
**Body Font:** Plus Jakarta Sans (with -apple-system, BlinkMacSystemFont, Segoe UI fallback)
**Code/Label Font:** JetBrains Mono (with Fira Code fallback)

**Character:** Sora is geometric and direct — it reads as technical authority without feeling corporate. Plus Jakarta Sans humanizes the body copy, keeping paragraph text readable and warm. JetBrains Mono is deployed as a semantic signal: its presence means "this is a fact, not prose."

### Hierarchy
- **Display** (weight 800, clamp 2.25rem–3.5rem, line-height 1.2, letter-spacing -0.03em): Hero headlines and section hero titles only. Sora. Tightly tracked to read as a single unit.
- **Headline** (weight 700, clamp 1.75rem–2.5rem, line-height 1.25, letter-spacing -0.025em): Section headings. Sora. Strong weight contrast against body.
- **Title** (weight 600, clamp 1.125rem–1.35rem, line-height 1.35): Card headings, subsection labels in prose. Sora.
- **Body** (weight 400, 1rem/16px, line-height 1.7): All paragraph copy. Plus Jakarta Sans. Cap line length at 65ch.
- **Label** (weight 700, 0.75rem, letter-spacing 0.12em, uppercase): Section tags, date chips, technology tags. JetBrains Mono. This is the "status indicator" style — monospace makes it read as metadata, not copy.

### Named Rules
**The Mono Semantic Rule.** JetBrains Mono means: date, tag, code, or technical metadata. It never appears in running prose or headings. Using it for decorative purposes breaks the reader's expectation.

**The Tight Headlines Rule.** Display and Headline weights use negative letter-spacing (-0.025em to -0.03em). This tightening is intentional and structural — wide-tracked headlines at large scale read as undecided, not refined.

## 4. Elevation

This system uses ambient diffuse shadows on interactive elements, not tonal layering alone. Surfaces are flat at rest; depth appears as a direct response to hover or focus — the shadow is a state indicator, not a style choice. The three zinc steps (#09090b → #18181b → #27272a) handle the at-rest separation between page, card, and panel.

### Shadow Vocabulary
- **Ambient low** (`0 1px 3px rgba(0,0,0,0.3)`): Barely-there depth signal on static cards.
- **Ambient mid** (`0 4px 16px rgba(0,0,0,0.4)`): Default card shadow. Visible but not assertive.
- **Ambient lift** (`0 8px 32px rgba(0,0,0,0.5)`): Card hover state. Communicates interactivity.
- **Ambient high** (`0 16px 48px rgba(0,0,0,0.6)`): Modal or floating overlay depth.
- **Lime glow** (`0 4px 16px rgba(224,255,79,0.3)`): Primary button hover only. The sole colored shadow in the system; reinforces the button's signal role.

### Named Rules
**The Responsive Depth Rule.** Shadows are not decoration — they are state feedback. At rest: ambient-low or ambient-mid. On hover: ambient-lift. On press/active: ambient-low (depth collapses, surface compresses). Never apply ambient-high to anything that isn't floating above the page.

**The One Glow Rule.** The lime glow appears only on `.btn-primary:hover`. Nowhere else. A second lime glow on the same screen creates visual competition with the primary CTA.

## 5. Components

### Buttons

Tactile and direct. Primary button is the only element in the system that inverts the palette — lime fill on zinc-black text — making it the most visually distinct object on any page.

- **Shape:** Gently rounded corners (12px / `radius-md`)
- **Primary** (`.btn-primary`): Alert Lime (`#E0FF4F`) fill, Zinc Black (`#09090b`) text, weight 700, 0.75rem 1.5rem padding. Hover: lifts 2px (`translateY(-2px)`), darkens to `#d4f038`, lime glow shadow.
- **Secondary** (`.btn-secondary`): Zinc Panel fill, Chalk White text, no border. Hover: Zinc Panel hover tint, text shifts to Alert Lime.
- **Outline** (`.btn-outline`): Transparent fill, 2px solid Zinc Fog border. Hover: border and text shift to Alert Lime, `rgba(224,255,79,0.05)` fill tint.
- **Ghost** (`.btn-ghost`): Transparent, Zinc Mist text, reduced padding. Hover: Alert Lime text, same fill tint.
- **Sign-in pill** (`.btn-signin`): Alert Lime fill, Zinc Black text, fully rounded (`radius-full`). Reserved for auth only.

### Cards

Flat at rest, lifted on hover. Cards are used when content items need visual separation — not as a default layout wrapper.

- **Corner Style:** Broadly rounded (16px / `radius-lg`)
- **Background:** Zinc Surface (`#18181b`), one step above the page floor
- **Shadow Strategy:** Ambient-mid at rest (`shadow-md`). Ambient-lift on hover (`shadow-lg`) with 4px upward translate.
- **Border:** None in dark mode. 1px `#e8e7e2` in light mode for definition on Warm Ivory.
- **Internal Padding:** 1.75rem on all sides

### Tags / Chips

Monospace, muted, clearly metadata.

- **Style:** Zinc Panel background, Zinc Mist text, radius-full, JetBrains Mono 0.8rem weight 500
- **Hover:** Alert Lime text, `rgba(224,255,79,0.08)` background tint
- **Date chips:** Alert Lime text, `rgba(224,255,79,0.08)` background, Mono — the one chip variant that uses the accent at rest

### Navigation

72px height, frosted zinc backdrop at 90% opacity. Links default to Zinc Mist; active state and hover use a 2px Alert Lime underline indicator that grows from center.

- **Style:** `rgba(9,9,11,0.9)` background, no border
- **Links:** Plus Jakarta Sans 0.875rem weight 500, Zinc Mist at rest, Chalk White on hover, 2px Alert Lime underline that expands from center on hover/active
- **Social icons:** Zinc Mist at rest, Alert Lime on hover, `rgba(224,255,79,0.05)` background tint
- **Mobile:** Hamburger menu; full-width panel slides in. Same color logic applies.

### Neural Network Background

Signature component: a canvas-rendered ambient particle network occupies the full viewport at z-index -1. Particles and connecting lines use Alert Lime at very low opacity (≤4%). Responds to mouse movement. Opacity reduces at mobile breakpoints for performance. Disable with `prefers-reduced-motion`.

## 6. Do's and Don'ts

### Do:
- **Do** use Alert Lime (`#E0FF4F`) exclusively for interactive state signals: CTAs, active nav underlines, date chips, hover text shifts. One signal per screen is the target.
- **Do** use JetBrains Mono only for metadata: dates, technology tags, code snippets. Mono appearance means "technical fact."
- **Do** let tonal zinc steps carry all at-rest depth. #09090b → #18181b → #27272a is the elevation story before any shadow is added.
- **Do** apply negative letter-spacing to Display and Headline: `-0.03em` at Display, `-0.025em` at Headline. This is structural, not decorative.
- **Do** cap body line length at 65ch. Long paragraphs on full-width layouts are an accessibility and readability failure.
- **Do** respect `prefers-reduced-motion` for the neural network background and all scroll-triggered entrance animations.
- **Do** scale shadows with interaction state: ambient-mid at rest, ambient-lift on hover, lime glow only on `.btn-primary`.
- **Do** use evidence-first copy: company names, years, outcomes, metrics. Never adjectives without a number behind them.

### Don't:
- **Don't** use generic Bootstrap-style template layouts: same hero + skills grid + contact form repeated section by section. This is the explicitly named anti-reference. Rewrite with distinct section treatments.
- **Don't** use gradient text (`background-clip: text` with a gradient). Prohibited. Use a single solid color.
- **Don't** add a second accent color. The entire system has one accent. Introducing blue, purple, or any hue alongside lime is not a "color palette" — it's a broken signal.
- **Don't** use glassmorphism decoratively: backdrop-filter + semi-transparent cards as a visual style. If blur appears, it must serve a functional purpose (modal overlay, nav transparency over content).
- **Don't** use purple-to-pink gradients, neon glows, or dark-SaaS hero metric cards. These are the named anti-references from PRODUCT.md. They read as template, not craft.
- **Don't** use `border-left` greater than 1px as a colored accent stripe on cards or list items. Rewrite with full borders, background tints, or leading monospace labels.
- **Don't** add shadows or glows at rest to non-interactive elements. Shadows are state feedback, not decoration. A shadow on a static text block is a lie about affordance.
- **Don't** use the lime accent on more than one element per visible viewport block. Rarity is the mechanism.
