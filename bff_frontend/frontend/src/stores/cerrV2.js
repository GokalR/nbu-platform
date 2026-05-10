/** Pinia store for the cerr-v2 service. Caches API responses so back-navigation
 *  is instant and reduces R2 round-trips. */
import { defineStore } from 'pinia'
import {
  listRegions, getRegionOverview, listRegionDistricts,
  getDistrictOverview, getDistrictMacro, listDistrictMahallas, getDistrictGeo,
  getMahallaOverview,
  getCountryGeo, getRegionDistrictsGeo, getRaqamlarda, getCountryRankings,
  getCountryAggregate,
} from '@/services/cerrApi.js'

export const useCerrV2Store = defineStore('cerrV2', {
  state: () => ({
    regions: null,                         // Array<{code, name, mahalla_count, districts_count}>
    regionOverview: {},                    // {[code]: overview}
    regionDistricts: {},                   // {[code]: Array<district>}
    districtOverview: {},                  // {[code]: overview}
    districtMacro: {},                     // {[code]: macro}
    districtMahallas: {},                  // {[code]: Array<mahalla summary>}
    districtGeo: {},                       // {[code]: GeoJSON FC}
    mahallaOverview: {},                   // {[stir]: overview}
    countryGeo: null,                      // GeoJSON FC
    regionGeo: {},                         // {[code]: districts FC}
    raqamlarda: {},                        // {[scope]: record} where scope = "national" | "<code>"
    countryRankings: null,                 // [{code, name, score, rank, district_count, mahalla_count, districts:[]}]
    countryAggregate: null,                // {regions, totals, tier_counts} — one-shot country page payload
    loading: false,
    error: null,
  }),
  actions: {
    async loadRegions() {
      if (this.regions) return this.regions
      this.regions = await listRegions()
      return this.regions
    },
    async loadCountryGeo() {
      if (this.countryGeo) return this.countryGeo
      this.countryGeo = await getCountryGeo()
      return this.countryGeo
    },
    async loadRegionOverview(code) {
      if (!this.regionOverview[code]) this.regionOverview[code] = await getRegionOverview(code)
      return this.regionOverview[code]
    },
    async loadRegionDistricts(code) {
      if (!this.regionDistricts[code]) this.regionDistricts[code] = await listRegionDistricts(code)
      return this.regionDistricts[code]
    },
    async loadRegionGeo(code) {
      if (!this.regionGeo[code]) this.regionGeo[code] = await getRegionDistrictsGeo(code)
      return this.regionGeo[code]
    },
    async loadDistrictOverview(code) {
      if (!this.districtOverview[code]) this.districtOverview[code] = await getDistrictOverview(code)
      return this.districtOverview[code]
    },
    async loadDistrictMacro(code) {
      if (this.districtMacro[code] === undefined)
        this.districtMacro[code] = await getDistrictMacro(code)
      return this.districtMacro[code]
    },
    async loadDistrictMahallas(code) {
      if (!this.districtMahallas[code])
        this.districtMahallas[code] = await listDistrictMahallas(code, { sort: 'rating_asc', limit: 2000 })
      return this.districtMahallas[code]
    },
    async loadDistrictGeo(code) {
      if (this.districtGeo[code] === undefined) this.districtGeo[code] = await getDistrictGeo(code)
      return this.districtGeo[code]
    },
    async loadMahallaOverview(stir) {
      if (!this.mahallaOverview[stir]) this.mahallaOverview[stir] = await getMahallaOverview(stir)
      return this.mahallaOverview[stir]
    },
    async loadRaqamlarda(scope) {
      if (this.raqamlarda[scope] === undefined) {
        try {
          this.raqamlarda[scope] = await getRaqamlarda(scope)
        } catch {
          this.raqamlarda[scope] = null
        }
      }
      return this.raqamlarda[scope]
    },
    async loadCountryRankings() {
      if (this.countryRankings) return this.countryRankings
      try {
        this.countryRankings = await getCountryRankings()
      } catch {
        this.countryRankings = []
      }
      return this.countryRankings
    },
    /** Single-fetch country page payload. Hydrates `regions`, `regionOverview`
     *  (population KPI only) and `countryRankings` so the country page doesn't
     *  need to fan out to 14 region overviews. */
    async loadCountryAggregate() {
      if (this.countryAggregate) return this.countryAggregate
      try {
        const agg = await getCountryAggregate()
        this.countryAggregate = agg
        // Hydrate `regions` so existing getters / pages keep working.
        if (!this.regions) {
          this.regions = agg.regions.map((r) => ({
            code: r.code,
            name: r.name,
            mahalla_count: r.mahalla_count,
            districts_count: r.districts_count,
          }))
        }
        // Synthesise minimal regionOverview entries (just population) so
        // CountryView's `regionsEnriched` resolves without 14 extra fetches.
        for (const r of agg.regions) {
          if (!this.regionOverview[r.code] && r.population != null) {
            this.regionOverview[r.code] = {
              kpis: [{ key: 'population', value: r.population }],
            }
          }
        }
        // Materialise countryRankings in the legacy shape too.
        if (!this.countryRankings) {
          this.countryRankings = agg.regions
            .filter((r) => r.has_cerr)
            .map((r) => ({
              code: r.code,
              name: r.name,
              score: r.score,
              rank: r.rank,
              district_count: r.districts_count,
              mahalla_count: r.mahalla_count,
            }))
            .sort((a, b) => a.rank - b.rank)
        }
        return agg
      } catch {
        this.countryAggregate = null
        return null
      }
    },
  },
  getters: {
    regionByCode: (s) => (code) => (s.regions || []).find((r) => r.code === Number(code)) || null,
    districtByCode: (s) => (code) => {
      for (const list of Object.values(s.regionDistricts)) {
        const d = (list || []).find((dd) => dd.code === Number(code))
        if (d) return d
      }
      return null
    },
  },
})
