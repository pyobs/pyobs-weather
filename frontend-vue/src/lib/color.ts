/** Minimal RGB triple, channels in `[0, 255]`. */
interface Rgb {
  r: number
  g: number
  b: number
}

/** Parses a `#rgb`, `#rrggbb`, `rgb(...)` or `rgba(...)` string into its RGB channels. Returns
 * `null` for anything else (named colors, `hsl()`, malformed input) — callers fall back to
 * passing the original string through unchanged. */
function parseColor(color: string): Rgb | null {
  const s = color.trim()

  if (s.startsWith('#')) {
    const hex = s.slice(1)
    if (hex.length === 3) {
      return {
        r: parseInt(hex[0] + hex[0], 16),
        g: parseInt(hex[1] + hex[1], 16),
        b: parseInt(hex[2] + hex[2], 16),
      }
    }
    if (hex.length === 6) {
      return {
        r: parseInt(hex.slice(0, 2), 16),
        g: parseInt(hex.slice(2, 4), 16),
        b: parseInt(hex.slice(4, 6), 16),
      }
    }
    return null
  }

  const m = s.match(/^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*[\d.]+\s*)?\)$/i)
  if (m) return { r: Number(m[1]), g: Number(m[2]), b: Number(m[3]) }

  return null
}

interface Hsl {
  h: number
  s: number
  l: number
}

function rgbToHsl({ r, g, b }: Rgb): Hsl {
  const rn = r / 255
  const gn = g / 255
  const bn = b / 255
  const max = Math.max(rn, gn, bn)
  const min = Math.min(rn, gn, bn)
  const l = (max + min) / 2
  const d = max - min

  if (d === 0) return { h: 0, s: 0, l }

  const s = d / (1 - Math.abs(2 * l - 1))
  let h: number
  switch (max) {
    case rn:
      h = ((gn - bn) / d) % 6
      break
    case gn:
      h = (bn - rn) / d + 2
      break
    default:
      h = (rn - gn) / d + 4
  }
  h *= 60
  if (h < 0) h += 360
  return { h, s, l }
}

function hslToRgb({ h, s, l }: Hsl): Rgb {
  const c = (1 - Math.abs(2 * l - 1)) * s
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1))
  const m = l - c / 2
  let r = 0
  let g = 0
  let b = 0
  if (h < 60) [r, g, b] = [c, x, 0]
  else if (h < 120) [r, g, b] = [x, c, 0]
  else if (h < 180) [r, g, b] = [0, c, x]
  else if (h < 240) [r, g, b] = [0, x, c]
  else if (h < 300) [r, g, b] = [x, 0, c]
  else [r, g, b] = [c, 0, x]
  return {
    r: Math.round((r + m) * 255),
    g: Math.round((g + m) * 255),
    b: Math.round((b + m) * 255),
  }
}

/** WCAG relative luminance, https://www.w3.org/TR/WCAG21/#dfn-relative-luminance */
function relativeLuminance({ r, g, b }: Rgb): number {
  const lin = (channel: number) => {
    const v = channel / 255
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
  }
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
}

/** WCAG contrast ratio between two colors, in `[1, 21]`. */
function contrastRatio(a: Rgb, b: Rgb): number {
  const la = relativeLuminance(a)
  const lb = relativeLuminance(b)
  const lighter = Math.max(la, lb)
  const darker = Math.min(la, lb)
  return (lighter + 0.05) / (darker + 0.05)
}

/** WCAG 1.4.11 minimum for graphical objects/UI components (non-text). */
const MIN_CONTRAST = 3
const LIGHTNESS_STEP = 0.02

/** Adapts `color` to stay legible against `surfaceColor` (a `--pyobs-surface-bg` value):
 * keeps hue and saturation, and clamps lightness towards white (on a dark surface) or black
 * (on a light surface) until the pair clears `MIN_CONTRAST`. Returns `color` unchanged if either
 * value can't be parsed, or if it already clears the contrast threshold. */
export function adaptToSurface(color: string, surfaceColor: string): string {
  const rgb = parseColor(color)
  const surface = parseColor(surfaceColor)
  if (!rgb || !surface) return color

  const hsl = rgbToHsl(rgb)
  const step = relativeLuminance(surface) < 0.5 ? LIGHTNESS_STEP : -LIGHTNESS_STEP

  let l = hsl.l
  let candidate = rgb
  for (let i = 0; i < 49 && contrastRatio(candidate, surface) < MIN_CONTRAST; i++) {
    const next = l + step
    if (next < 0.02 || next > 0.98) break
    l = next
    candidate = hslToRgb({ ...hsl, l })
  }

  return `rgb(${candidate.r}, ${candidate.g}, ${candidate.b})`
}

/** Reads a `--pyobs-*` custom property off the root element, e.g. `--pyobs-surface-bg`. */
export function cssVar(name: string, fallback: string): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return value || fallback
}

/** Rewrites `color` (hex or `rgb(a)`) to `rgba(r, g, b, alpha)`. Passes through anything else
 * (named colors, already-unparseable strings) unchanged. */
export function withAlpha(color: string, alpha: number): string {
  const rgb = parseColor(color)
  if (!rgb) return color
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`
}
