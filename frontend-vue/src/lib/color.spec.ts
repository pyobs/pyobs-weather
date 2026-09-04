import { describe, it, expect } from 'vitest'
import { adaptToSurface, withAlpha } from './color'

describe('withAlpha', () => {
  it('converts a 6-digit hex color to rgba', () => {
    expect(withAlpha('#ff0000', 0.5)).toBe('rgba(255, 0, 0, 0.5)')
  })
  it('converts a 3-digit hex color to rgba', () => {
    expect(withAlpha('#f00', 0.1)).toBe('rgba(255, 0, 0, 0.1)')
  })
  it('overrides the alpha of an existing rgba() value', () => {
    expect(withAlpha('rgba(0, 0, 0, 0.1)', 0.5)).toBe('rgba(0, 0, 0, 0.5)')
  })
  it('applies alpha to an rgb() value', () => {
    expect(withAlpha('rgb(10, 20, 30)', 0.4)).toBe('rgba(10, 20, 30, 0.4)')
  })
  it('passes genuinely unparseable strings through unchanged', () => {
    expect(withAlpha('red', 0.5)).toBe('red')
  })
})

describe('adaptToSurface', () => {
  const lightSurface = '#ffffff'
  const darkSurface = '#1a1d21'

  it('leaves a color unchanged when it already clears the contrast threshold', () => {
    expect(adaptToSurface('#ff0000', lightSurface)).toBe('rgb(255, 0, 0)')
  })

  it('lightens a black default so it is visible on a dark surface', () => {
    const adapted = adaptToSurface('rgba(0, 0, 0, 0.1)', darkSurface)
    expect(adapted).not.toBe('rgb(0, 0, 0)')
    const [, r, g, b] = adapted.match(/rgb\((\d+), (\d+), (\d+)\)/)!.map(Number)
    expect(r).toBeGreaterThan(100)
    expect(r).toBe(g)
    expect(g).toBe(b)
  })

  it('darkens a near-white color so it is visible on a light surface', () => {
    const adapted = adaptToSurface('#fefefe', lightSurface)
    const [, r] = adapted.match(/rgb\((\d+), (\d+), (\d+)\)/)!.map(Number)
    expect(r).toBeLessThan(150)
  })

  it('preserves hue while adjusting lightness', () => {
    const adapted = adaptToSurface('#001a00', darkSurface) // very dark green
    const [, r, g, b] = adapted.match(/rgb\((\d+), (\d+), (\d+)\)/)!.map(Number)
    expect(g).toBeGreaterThan(r)
    expect(g).toBeGreaterThan(b)
  })

  it('returns the input unchanged when either color is unparseable', () => {
    expect(adaptToSurface('red', darkSurface)).toBe('red')
  })
})
