/**
 * @alphaforge/solar-orb-ball
 *
 * The central animated Solar Orb — extracted as a standalone, self-contained
 * React component so it can iterate on its own dev server independent of the
 * larger solar-orb-ui design system.
 *
 * Usage:
 *   import { SolarOrb } from "@alphaforge/solar-orb-ball";
 *   import "@alphaforge/solar-orb-ball/styles";
 *
 *   <SolarOrb size={260} accent="#ff8f00" />
 */

export { SolarOrb } from "./SolarOrb";
export type { SolarOrbProps, SolarOrbStarPreset } from "./SolarOrb";
