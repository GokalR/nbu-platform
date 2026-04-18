import { describe, it, expect } from 'vitest'
import { formatDuration } from '../formatDuration'

describe('formatDuration', () => {
  it('returns empty string for 0', () => {
    expect(formatDuration(0)).toBe('')
  })

  it('returns empty string for null', () => {
    expect(formatDuration(null)).toBe('')
  })

  it('returns empty string for undefined', () => {
    expect(formatDuration(undefined)).toBe('')
  })

  it('formats 90 seconds as "1:30"', () => {
    expect(formatDuration(90)).toBe('1:30')
  })

  it('formats 65 seconds as "1:05"', () => {
    expect(formatDuration(65)).toBe('1:05')
  })

  it('formats 3600 seconds as "60:00"', () => {
    expect(formatDuration(3600)).toBe('60:00')
  })

  it('zero-pads single digit seconds (61 → "1:01")', () => {
    expect(formatDuration(61)).toBe('1:01')
  })
})
