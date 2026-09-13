import test from 'node:test'
import assert from 'node:assert/strict'
import { collectPages } from '../src/utils/pagination.js'

test('selector includes mouse 501 and preserves filters on every page', async () => {
  const calls = []
  const items = Array.from({ length: 501 }, (_, id) => ({ id }))
  const result = await collectPages(async params => {
    calls.push(params)
    return { total: 501, items: items.slice((params.page - 1) * 500, params.page * 500) }
  }, { room: '测试鼠房', in_cage: true })
  assert.equal(result.length, 501)
  assert.equal(result.at(-1).id, 500)
  assert.deepEqual(calls.map(p => [p.page, p.room, p.in_cage]), [[1, '测试鼠房', true], [2, '测试鼠房', true]])
})
test('failed later page rejects instead of returning partial options', async () => {
  await assert.rejects(collectPages(async ({ page }) => {
    if (page === 2) throw new Error('offline')
    return { total: 501, items: Array.from({ length: 500 }, (_, id) => ({ id })) }
  }), /offline/)
})
test('empty and repeated pages do not loop forever', async () => {
  assert.deepEqual(await collectPages(async () => ({ total: 0, items: [] })), [])
  await assert.rejects(collectPages(async () => ({ total: 5, items: [{ id: 1 }] })), /Incomplete/)
})
