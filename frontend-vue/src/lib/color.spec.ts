import { describe, it, expect } from 'vitest'
import { withAlpha } from './color'

describe('withAlpha', () => {
  it('converts a 6-digit hex color to rgba', () => {
    expect(withAlpha('#ff0000', 0.5)).toBe('rgba(255, 0, 0, 0.5)')
  })
  it('converts a 3-digit hex color to rgba', () => {
    expect(withAlpha('#f00', 0.1)).toBe('rgba(255, 0, 0, 0.1)')
  })
  it('passes non-hex strings through unchanged', () => {
    expect(withAlpha('rgba(0, 0, 0, 0.1)', 0.5)).toBe('rgba(0, 0, 0, 0.1)')
  })
})
