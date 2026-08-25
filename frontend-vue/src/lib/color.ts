/** Convert a hex color (`#rgb` or `#rrggbb`) to `rgba(r, g, b, alpha)`. Passes through any
 * non-hex string unchanged (e.g. an already-`rgba(...)` value). */
export function withAlpha(color: string, alpha: number): string {
  const hex = color.trim()
  if (!hex.startsWith('#')) return hex

  let r: number
  let g: number
  let b: number
  if (hex.length === 4) {
    r = parseInt(hex[1] + hex[1], 16)
    g = parseInt(hex[2] + hex[2], 16)
    b = parseInt(hex[3] + hex[3], 16)
  } else if (hex.length === 7) {
    r = parseInt(hex.slice(1, 3), 16)
    g = parseInt(hex.slice(3, 5), 16)
    b = parseInt(hex.slice(5, 7), 16)
  } else {
    return hex
  }
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}
