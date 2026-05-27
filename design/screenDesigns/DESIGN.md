---
name: Zomato AI Sushi
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#5b403f'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f0f1f1'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#006e26'
  on-secondary: '#ffffff'
  secondary-container: '#8af793'
  on-secondary-container: '#007328'
  tertiary: '#7c5400'
  on-tertiary: '#ffffff'
  tertiary-container: '#9d6b00'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#8dfa96'
  secondary-fixed-dim: '#71dd7c'
  on-secondary-fixed: '#002106'
  on-secondary-fixed-variant: '#00531b'
  tertiary-fixed: '#ffddaf'
  tertiary-fixed-dim: '#ffba43'
  on-tertiary-fixed: '#281800'
  on-tertiary-fixed-variant: '#614000'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
  deep-charcoal: '#1C1C1C'
  cool-gray: '#696969'
  border-light: '#E8E8E8'
  surface-white: '#FFFFFF'
  ai-tint: rgba(226, 55, 68, 0.05)
typography:
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.04em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  ai-verdict:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-max: 1200px
  gutter: 1.5rem
  stack-gap: 1rem
  section-gap: 2.5rem
  touch-target: 3rem
---

## Brand & Style

The brand personality is authoritative yet approachable, combining the established reliability of Zomato's extensive food database with the cutting-edge precision of AI-driven curation. It is designed to feel like a high-end digital concierge—efficient, clean, and deeply personalized.

The design style is **Corporate / Modern** with a strong emphasis on **Minimalism**. It utilizes a "Sushi-style" aesthetic: clean white surfaces, precise alignment, and generous whitespace to ensure the user's focus remains entirely on the culinary recommendations. The interface is center-focused and intentional, stripping away sidebar distractions to create a premium, utility-first experience.

**Key visual principles:**
- **Grid Layout:** Content is housed within a wide-screen grid (max-width 1200px) featuring a compact top filter bar and a multi-column cards grid for recommendations.
- **Clarity over Clutter:** Use of subtle thin borders and soft shadows instead of heavy gradients or complex background patterns.
- **Action-Oriented:** Zomato Red is reserved strictly for primary actions, critical UI markers (like rank), and brand identity.

## Colors

The palette is anchored by the iconic **Zomato Red**, used strategically to guide the eye toward primary CTAs and ranking indicators. **Zomato Green** is utilized exclusively for high-performance metrics (ratings 4.0+) and positive confirmations, while **Zomato Gold** serves as the universal signifier for star ratings and quality highlights.

The background is a soft, near-white neutral (`#FCFCFC`) to reduce eye strain and provide better contrast for the pure white (`#FFFFFF`) component cards. Text hierarchy is maintained through **Deep Charcoal** for high-legibility headings and **Cool Gray** for supporting metadata and secondary labels.

## Typography

The design system exclusively uses **Plus Jakarta Sans** to convey a modern, welcoming, yet professional tone. The typographic hierarchy is built on extreme weight contrast—using Extra Bold (`800`) for main titles with tight letter-spacing to create a "blocky," authoritative look, while maintaining open and airy line heights for body content to ensure scannability.

On mobile devices, headings scale down to prevent awkward text wrapping, while body sizes remain consistent to maintain a minimum 44px vertical rhythm for touch targets.

## Layout & Spacing

The layout follows a **Fixed Grid** model centered on the viewport. The primary content wrapper is constrained to a maximum width of `1200px` (lg) to accommodate a multi-column restaurant grid.

**Key Layout Rules:**
- **Vertical Rhythm:** Elements are stacked vertically with a consistent `1rem` gap between related cards and a `2.5rem` gap between major sections (Form vs. Results).
- **Mobile First:** On viewports smaller than `640px`, horizontal padding reduces from `1.5rem` to `1rem`, and two-column grids (like sliders) reflow into a single-column stack.
- **Safe Areas:** All interactive elements (pills, inputs, buttons) must maintain a minimum height of `48px` to comply with touch-target accessibility standards.

## Elevation & Depth

This design system utilizes a **Low-contrast Outline** approach combined with **Soft Ambient Shadows** to create a sense of organized layering without looking heavy.

- **Surface Levels:** The base page sits at the lowest level (`#FCFCFC`). Interactive cards and panels sit on the first elevated tier (`#FFFFFF`).
- **Shadow Profile:** Shadows are extremely diffused with low opacity—`0px 2px 8px rgba(28, 28, 28, 0.08)`. This creates a subtle "lift" that distinguishes cards from the background without creating harsh edges.
- **Borders:** Every card and input uses a thin, `1px` border in `#E8E8E8`. This provides structural definition even when the shadow is subtle.
- **Interactive States:** On hover, restaurant cards should transition to a slightly higher elevation (`-4px` Y-axis translation) with a slightly more pronounced shadow to indicate clickability.

## Shapes

The shape language is defined by **Rounded-XL (12px)** corners for all primary containers, including preference forms and restaurant cards. This softness balances the "corporate" typography, making the tool feel more accessible and "food-friendly."

- **Primary Cards:** 12px (`rounded-xl`).
- **Secondary Badges/Pills:** 8px (`rounded-lg`) for rank badges and 6px (`rounded-md`) for cuisine tags.
- **Interactive Pills:** Fully rounded (pill-shaped) for budget selection and toggle states.

## Components

### Buttons & Inputs
- **Primary Action:** Solid Zomato Red background with white text, 12px rounded corners, and a full-width block display.
- **Segmented Control (Budget):** Pill-style buttons in a row. The active state features a 2px Zomato Red border and a soft red background tint (`#E23744` at 5% opacity).
- **Input Fields:** Pure white background, 1px `#E8E8E8` border, with a Zomato Red focus ring.

### Cards
- **Form Card:** A single, large white container with the standard 12px radius and soft shadow. 
- **Restaurant Card:** Features a flex-row header for the rank badge and name. Includes a nested **AI Verdict Box** at the bottom with a 2px left-border accent in Zomato Red and an italicized font style to distinguish AI-generated content from static data.

### Badges & Indicators
- **Rank Badge:** Solid Zomato Red block with white Extra Bold text.
- **Rating Pill:** Dynamic coloring—Zomato Green for ≥ 4.0, Zomato Gold for < 4.0.
- **Cuisine Tags:** Small, subtle gray tags (`#F8F8F8`) to provide information without competing with the primary card content.

### Feedback Systems
- **AI Summary Banner:** Uses a soft Zomato Red tint background (`#E23744` at 5% opacity) and a thick 4px left-border to highlight the "AI Verdict" at the top of the results.
- **Loading Skeleton:** Pulsing gray blocks (`animate-pulse`) that mirror the layout of the restaurant cards to maintain visual stability during generation.