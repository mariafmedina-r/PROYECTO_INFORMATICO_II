# Design System Document: The Artisanal Connection

## 1. Overview & Creative North Star
**Creative North Star: "The Digital Estate"**

This design system is built to bridge the gap between the rugged, organic reality of coffee cultivation and the sophisticated, fast-paced world of urban consumption. We avoid the "generic marketplace" aesthetic by adopting an editorial layout style—reminiscent of high-end culinary magazines. 

The system rejects the rigid, boxy constraints of traditional web design. Instead, it utilizes **Intentional Asymmetry** and **Tonal Layering**. Hero sections should feature overlapping elements (e.g., a product image breaking the container of a text block) to create a sense of depth and movement. We are not just building an interface; we are curating an experience that feels as tactile and premium as a hand-poured brew.

---

## 2. Colors & Surface Architecture

The palette is rooted in the earth, using deep roasted tones (`primary`) and lush vegetation (`secondary`) to anchor the experience.

### The "No-Line" Rule
To maintain an organic, premium feel, **1px solid borders are strictly prohibited for sectioning.** Boundaries must be defined solely through background color shifts. 
- Use `surface-container-low` (#f4f4f0) for large structural sections.
- Use `surface` (#faf9f5) for the main canvas.
- Separation is achieved through the spacing scale (e.g., `8` or `12` tokens) rather than lines.

### Surface Hierarchy & Nesting
Think of the UI as layers of fine parchment. 
- **Base Level:** `surface`
- **Secondary Content:** `surface-container`
- **Floating/Interactive Elements:** `surface-container-lowest` (#ffffff)
By nesting a `surface-container-lowest` card inside a `surface-container-low` section, you create a natural lift that signals interactability without visual clutter.

### The "Glass & Gradient" Rule
For floating navigation or high-impact overlays, use **Glassmorphism**. Apply `surface` at 80% opacity with a `backdrop-blur` of 12px. For primary CTAs, use a subtle linear gradient from `primary` (#361f1a) to `primary_container` (#4e342e) at a 135-degree angle to add "soul" and dimension.

---

## 3. Typography: The Editorial Voice

We pair the heritage of the roast with the clarity of modern commerce.

*   **Display & Headlines (Noto Serif):** Use `display-lg` and `headline-md` to establish authority. These should feel like headers in a premium coffee journal. Letter spacing should be slightly tightened (-0.02em) for a more bespoke look.
*   **Body & Labels (Manrope):** This geometric sans-serif provides the "modern" half of the vibe. Use `body-lg` for product descriptions to ensure maximum readability.
*   **The "Hierarchy of Scale":** Create high contrast between headlines and body text. A `headline-lg` (2rem) should often sit near `label-md` (0.75rem) to create a sophisticated, asymmetrical tension.

---

## 4. Elevation & Depth

### The Layering Principle
Avoid "Drop Shadow" presets. Depth is achieved via **Tonal Stacking**.
- **Level 1:** `surface` (Base)
- **Level 2:** `surface-container-low` (Content Grouping)
- **Level 3:** `surface-container-lowest` (Interactive Card)

### Ambient Shadows
When a shadow is required (e.g., a hovering product card), use a multi-layered shadow:
- `box-shadow: 0 10px 30px rgba(54, 31, 26, 0.05), 0 4px 8px rgba(54, 31, 26, 0.03);`
The shadow color must be a tinted version of `primary` or `on-surface`, never pure black.

### The "Ghost Border" Fallback
If accessibility requires a border (e.g., a search input), use a **Ghost Border**: `outline-variant` (#d4c3bf) at 20% opacity. 

---

## 5. Components

### Buttons
- **Primary:** Gradient (`primary` to `primary_container`), `DEFAULT` (0.5rem) roundedness. Typography: `label-md` in all-caps with 0.05em tracking for a "button-as-label" aesthetic.
- **Secondary:** `surface-container-highest` background with `on_surface` text. No border.
- **Tertiary:** `on_surface` text with a subtle `primary` underline that expands on hover.

### Input Fields
- **Container-less Design:** Use a simple `outline-variant` bottom-border (2px) that transitions to `secondary` (#1b6d24) on focus. 
- **Background:** `surface-container-low`.

### Cards & Lists
- **Rule:** Forbid divider lines. 
- **Implementation:** Product lists should use the `spacing scale (5)` to separate items. Information hierarchy within a card is handled by typography weight (e.g., `title-md` for price, `body-sm` for origin).

### Custom Component: The "Origin Tag"
Used for coffee origins (e.g., "Huila, Colombia"). 
- **Style:** `secondary_container` background, `on_secondary_container` text, `full` roundedness. It should feel like a soft, organic leaf.

---

## 6. Do's and Don'ts

### Do:
*   **Use Asymmetry:** Place product images off-center within their containers to evoke an artisanal feel.
*   **Embrace White Space:** Use the `16` (5.5rem) spacing token between major homepage sections.
*   **Layer Surfaces:** Place white (`surface-container-lowest`) cards on beige (`surface-container-low`) backgrounds.

### Don't:
*   **Don't use 1px lines:** Do not use borders to separate the header from the body or sidebar from the feed. Use color shifts.
*   **Don't use pure black:** Use `primary` (#361f1a) for dark text to keep the palette warm and organic.
*   **Don't over-round:** Stick to the `DEFAULT` (0.5rem) for cards and inputs. Reserve `full` (pill-shape) only for small tags and chips.

---

## 7. Interaction States
- **Hover:** Elements should subtly lift via a shift from `surface-container` to `surface-container-lowest` rather than a heavy shadow.
- **Active:** A brief 2% scale-down to provide tactile feedback, mimicking the "press" of a physical button.
- **Success:** Use `secondary` (#1b6d24) for confirmation states, evoking the lush green of unroasted coffee cherries.