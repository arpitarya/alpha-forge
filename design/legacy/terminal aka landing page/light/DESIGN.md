# Design System Specification: Kinetic Precision

## 1. Overview & Creative North Star: "The Solar Terminal"
The Creative North Star for this design system is **"The Solar Terminal."** This is not a standard SaaS dashboard; it is a high-performance instrument. It blends the brutalist efficiency of a command-line interface with the premium finish of high-end aerospace instrumentation.

To break the "template" look, we reject traditional structural containers. We favor **intentional asymmetry**—where data-heavy modules are balanced by expansive, breathing negative space. Layouts should feel kinetic, as if the data is live and flowing, anchored by a rigid, 0px-radius geometry that communicates absolute precision and "Zero-Latency" reliability.

---

## 2. Color & Atmospheric Theory
The palette is built on the high-contrast tension between deep obsidian voids and incandescent amber energy.

### The "No-Line" Rule
**Prohibit 1px solid borders for sectioning.** Boundaries must be defined solely through background color shifts or tonal transitions. To separate a sidebar from a main feed, transition from `surface` (#0e0e0e) to `surface-container-low` (#131313). Structure is felt, not seen.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers of tinted glass. 
*   **Base:** `surface` (#0e0e0e)
*   **De-emphasized Zones:** `surface-container-lowest` (#000000) for deep-set code blocks or terminal inputs.
*   **Interactive Layers:** `surface-container` (#1a1a1a) for standard cards.
*   **Elevated Focus:** `surface-bright` (#2c2c2c) for active state containers.

### The "Glass & Gradient" Rule
To inject "soul" into the machine, use **Signature Textures**:
*   **Amber Bloom:** Apply a subtle `primary` radial gradient (opacity 5-10%) behind key data visualizations to simulate a phosphor-glow effect.
*   **Kinetic CTAs:** Main actions should use a linear gradient from `primary` (#ffa44f) to `primary-container` (#ff8f00) at a 45-degree angle to create a sense of forward motion.

---

## 3. Typography: Space Grotesk
Space Grotesk’s monospaced influence provides a futuristic, tech-forward aesthetic while maintaining high legibility.

*   **The Power Scale:** Use `display-lg` (3.5rem) for hero data points, set with a `-0.04em` letter-spacing to give it an aggressive, editorial punch.
*   **The Terminal Label:** Use `label-sm` (0.6875rem) in ALL CAPS with `+0.1em` letter-spacing for metadata. This mimics technical schematics.
*   **Hierarchy:** `headline-md` should be used sparingly to anchor sections, while `body-md` handles the heavy lifting of high-density data layouts.

---

## 4. Elevation & Depth: Tonal Layering
We do not use drop shadows to indicate "height." We use light.

*   **The Layering Principle:** Stacking is achieved through the `surface-container` tiers. A `surface-container-high` module sitting on a `surface` background creates a natural, sharp lift.
*   **Ambient Glows:** Instead of a grey shadow, use a soft `primary` tinted glow for "Active" states. A `blur: 24px` / `opacity: 12%` amber shadow creates a "powered-on" effect.
*   **The Ghost Border:** If a separator is required for accessibility, use `outline-variant` (#484847) at **15% opacity**. It should be a mere suggestion of a line.
*   **Glassmorphism:** For floating overlays (modals/tooltips), use `surface-container` with an `80% opacity` and a `blur: 12px`. This ensures the high-density data beneath remains a visible texture, maintaining the "Terminal" feel.

---

## 5. Components

### The Hard-Edge Constraint
**The Roundedness Scale is set to 0px across all tokens.** This is non-negotiable. Buttons, cards, and inputs must be perfectly rectangular to maintain the "Forge" brand personality.

*   **Buttons:** 
    *   *Primary:* `primary_container` background, `on_primary_container` text. High-energy, bold.
    *   *Secondary:* `outline` ghost border (20% opacity), `primary` text.
    *   *Tertiary:* `on_surface_variant` text, no background. 
*   **Input Fields:** Use `surface_container_highest` as the fill. The "Active" state is marked by a 2px bottom-bar of `primary`—avoid full-box outlines.
*   **Data Chips:** Small, rectangular tags using `secondary_container` with `on_secondary_container` text. They should look like physical labels on a machine.
*   **Cards:** Forbid divider lines. Use `spacing: 24px` (vertical white space) or a shift to `surface_container_low` to separate content blocks.
*   **High-Density Modules:** Use `body-sm` for data tables to maximize information density, using `surface-container-lowest` for alternating row backgrounds.

---

## 6. Do’s and Don’ts

### Do:
*   **Embrace the Dark:** Use the `background` (#0e0e0e) as a canvas for the amber "light" to shine.
*   **Use Asymmetry:** Align text to the left but place key metrics on a strict right-hand grid to create visual tension.
*   **Optimize for Light Mode:** In Light Mode, ensure the `warm white` surface uses `surface-container` tiers that are subtle (e.g., 2-3% contrast shifts) to maintain a premium paper-like feel.

### Don't:
*   **No Rounding:** Never use `border-radius`. It softens the "Precision" message.
*   **No Standard Shadows:** Avoid the "fuzzy grey" shadow of generic UI kits. If it doesn't glow, it doesn't float.
*   **No Crowding:** Even in "high-density" layouts, use the `surface` tokens to create "voids" that let the eye rest.
*   **No Default Borders:** Never use `outline` at 100% opacity. It creates "visual noise" that kills the kinetic minimalist aesthetic.