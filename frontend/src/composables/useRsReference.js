import { computed, ref, watch } from 'vue'
import { rsApi } from '@/services/rsApi'

/**
 * Fetches Regional Strategist reference data (city KPIs, districts,
 * enterprises, credit products) for the resolved pilot city.
 *
 * Returns reactive refs that populate as calls come back. When the
 * backend is unreachable or the city is not a pilot, refs stay null —
 * callers should render no-data banners instead of falling back.
 *
 *   const { city, districts, enterprises, products, loading, isPilot,
 *           hasCoverage } = useRsReference({ cityId, sector })
 */
export function useRsReference({ cityId, sector }) {
  const city = ref(null)
  const districts = ref([])
  const enterprises = ref([])
  const products = ref([])
  const loading = ref(false)
  const error = ref(null)

  const isPilot = computed(() => cityId.value === 'fergana' || cityId.value === 'margilan')

  async function load() {
    const id = cityId.value
    const sec = sector.value
    if (!id) {
      city.value = null
      districts.value = []
      enterprises.value = []
      return
    }
    loading.value = true
    error.value = null
    try {
      const [cityRes, districtsRes, enterprisesRes] = await Promise.all([
        rsApi.getCity(id),
        isPilot.value ? rsApi.getCityDistricts(id) : Promise.resolve({ ok: true, data: [] }),
        isPilot.value && sec
          ? rsApi.getCityEnterprises(id, sec)
          : Promise.resolve({ ok: true, data: [] }),
      ])
      city.value = cityRes.ok ? cityRes.data : null
      districts.value = districtsRes.ok ? districtsRes.data : []
      enterprises.value = enterprisesRes.ok ? enterprisesRes.data : []
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  async function loadProducts() {
    const res = await rsApi.getCreditProducts()
    products.value = res.ok ? res.data : []
  }

  // Re-fetch whenever the resolved city or sector changes
  watch([cityId, sector], load, { immediate: true })
  loadProducts()

  const hasCityData = computed(() => !!city.value)
  const hasDistrictData = computed(() => (districts.value || []).length > 0)
  const hasEnterpriseData = computed(() => (enterprises.value || []).length > 0)
  const hasCoverage = computed(() => isPilot.value && hasCityData.value)

  return {
    city,
    districts,
    enterprises,
    products,
    loading,
    error,
    isPilot,
    hasCityData,
    hasDistrictData,
    hasEnterpriseData,
    hasCoverage,
  }
}
