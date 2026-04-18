import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock the api service that rsApi imports
vi.mock('@/services/api', () => ({ BACKEND_URL: '' }))

// By default, VITE_API_URL is not set, so BASE will be '' and isConfigured() returns false.
// We import rsApi after the mock is in place.
const { rsApi } = await import('../rsApi')

describe('rsApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  describe('isConfigured()', () => {
    it('returns false when VITE_API_URL is empty', () => {
      expect(rsApi.isConfigured()).toBe(false)
    })
  })

  describe('when not configured, all methods return { ok: false, reason: "no-backend" }', () => {
    const noBackend = { ok: false, reason: 'no-backend' }

    it('createSubmission returns no-backend', async () => {
      const result = await rsApi.createSubmission({ district: 'test' })
      expect(result).toEqual(noBackend)
    })

    it('getSubmission returns no-backend', async () => {
      const result = await rsApi.getSubmission('abc-123')
      expect(result).toEqual(noBackend)
    })

    it('uploadExcel returns no-backend', async () => {
      const fakeFile = new File(['data'], 'test.xlsx')
      const result = await rsApi.uploadExcel('sub-1', 'budget', fakeFile)
      expect(result).toEqual(noBackend)
    })

    it('health returns no-backend', async () => {
      const result = await rsApi.health()
      expect(result).toEqual(noBackend)
    })

    it('listUploads returns no-backend', async () => {
      const result = await rsApi.listUploads('sub-1')
      expect(result).toEqual(noBackend)
    })

    it('runAnalysis returns no-backend', async () => {
      const result = await rsApi.runAnalysis('sub-1')
      expect(result).toEqual(noBackend)
    })

    it('latestAnalysis returns no-backend', async () => {
      const result = await rsApi.latestAnalysis('sub-1')
      expect(result).toEqual(noBackend)
    })
  })

  describe('baseUrl()', () => {
    it('returns empty string when not configured', () => {
      expect(rsApi.baseUrl()).toBe('')
    })
  })
})
