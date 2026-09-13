/** Collect a paginated selector without silently presenting an incomplete list. */
export async function collectPages(fetchPage, params = {}) {
  const rows = new Map()
  for (let page = 1; ; page += 1) {
    const result = await fetchPage({ ...params, page, page_size: 500 })
    if (!Array.isArray(result.items) || !Number.isInteger(result.total) || result.total < 0) {
      throw new Error('Invalid paginated response')
    }
    const previousSize = rows.size
    for (const row of result.items) rows.set(row.id, row)
    if (rows.size >= result.total) return [...rows.values()]
    if (!result.items.length || rows.size === previousSize) {
      throw new Error('Incomplete paginated response; please refresh')
    }
  }
}
