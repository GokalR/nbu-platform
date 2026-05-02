/**
 * Pick the right Golden Mart schema based on level.
 * Used by both the admin form and the public detail view so they
 * stay aligned to the same auto-generated schema.
 */
import { CITY_SECTIONS,    CITY_TABS,    tabSections as citySections    } from './citySchema.js'
import { REGION_SECTIONS,  REGION_TABS,  tabSections as regionSections  } from './regionSchema.js'
import { COUNTRY_SECTIONS, COUNTRY_TABS, tabSections as countrySections } from './countrySchema.js'

export function schemaForLevel(level) {
  if (level === 'country') {
    return { sections: COUNTRY_SECTIONS, tabs: COUNTRY_TABS, tabSections: countrySections }
  }
  if (level === 'region') {
    return { sections: REGION_SECTIONS,  tabs: REGION_TABS,  tabSections: regionSections  }
  }
  return { sections: CITY_SECTIONS, tabs: CITY_TABS, tabSections: citySections }
}

export function totalFieldsForLevel(level) {
  return schemaForLevel(level).sections.reduce((n, s) => n + s.attrs.length, 0)
}
