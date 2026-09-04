import { cssVar } from './color'

/** Chart.js chrome colors (grid/ticks/legend/tooltip) for the currently active theme, read live
 * off the `--pyobs-surface-*` tokens so they stay in sync with `style.css` without duplicating
 * the palette here. Call fresh on every (re)render — cheap `getComputedStyle` reads, no caching. */
export function chartChromeColors() {
  const text = cssVar('--pyobs-surface-text', '#212529')
  const muted = cssVar('--pyobs-surface-text-muted', '#6c757d')
  const border = cssVar('--pyobs-surface-border', '#dee2e6')
  const hoverBg = cssVar('--pyobs-surface-hover-bg', '#e9ecef')

  return {
    text,
    muted,
    grid: border,
    tooltip: { backgroundColor: hoverBg, titleColor: text, bodyColor: text, borderColor: border, borderWidth: 1 },
  }
}
