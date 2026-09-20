import type { CSSProperties } from "react";

const WOBBLE_REFERENCE = 70;
const BASE_DURATION = 1.12;
const FASTEST_DURATION = 0.22;

export function wobbleStyle(count: number): CSSProperties {
  const scale = Math.min(
    1,
    Math.max(0, (Math.sqrt(count) - 1) / (Math.sqrt(WOBBLE_REFERENCE) - 1)),
  );
  const duration = BASE_DURATION - (BASE_DURATION - FASTEST_DURATION) * scale;

  return {
    "--wobble-duration": `${duration.toFixed(2)}s`,
  } as CSSProperties;
}
