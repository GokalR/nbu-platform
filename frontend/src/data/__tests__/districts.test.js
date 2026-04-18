import { describe, it, expect } from 'vitest'
import { districts, districtByKey, tools } from '../districts'

describe('districts data', () => {
  it('has exactly 19 entries (4 cities + 15 districts)', () => {
    expect(districts).toHaveLength(19)
  })

  it('each district has required keys: key, kind, population, area, status', () => {
    const requiredKeys = ['key', 'kind', 'population', 'area', 'status']
    for (const d of districts) {
      for (const k of requiredKeys) {
        expect(d).toHaveProperty(k)
      }
    }
  })

  it('kind is either "city" or "district" for every entry', () => {
    for (const d of districts) {
      expect(['city', 'district']).toContain(d.kind)
    }
  })

  it('contains exactly 4 cities', () => {
    const cities = districts.filter((d) => d.kind === 'city')
    expect(cities).toHaveLength(4)
  })

  it('contains exactly 15 districts', () => {
    const dists = districts.filter((d) => d.kind === 'district')
    expect(dists).toHaveLength(15)
  })

  it('districtByKey maps correctly for "fargona_city"', () => {
    const entry = districtByKey['fargona_city']
    expect(entry).toBeDefined()
    expect(entry.key).toBe('fargona_city')
    expect(entry.kind).toBe('city')
    expect(entry.population).toBe(335.1)
  })

  it('districtByKey has an entry for every district key', () => {
    for (const d of districts) {
      expect(districtByKey[d.key]).toBe(d)
    }
  })
})

describe('tools data', () => {
  it('tools array has entries', () => {
    expect(tools.length).toBeGreaterThan(0)
  })

  it('each tool has required keys: key, icon, accent, to or comingSoon', () => {
    for (const t of tools) {
      expect(t).toHaveProperty('key')
      expect(t).toHaveProperty('icon')
      expect(t).toHaveProperty('accent')
      // Each tool should have either a route or be marked as comingSoon
      const hasRoute = 'to' in t
      const isComingSoon = 'comingSoon' in t
      expect(hasRoute || isComingSoon).toBe(true)
    }
  })
})
