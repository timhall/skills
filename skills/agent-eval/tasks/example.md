example: `paginate` drops the last page when the list length is an exact multiple of the page size

## Problem

`paginate(items, size)` in `src/paginate.js` computes the page count as
`Math.floor(items.length / size)`. When `items.length` is an exact multiple of `size`, that rounds
down one page short, so the final page of items is silently dropped from the result.

## Fix

Use `Math.ceil` when computing the page count, and add a test in `test/paginate.test.js` that pins
the exact-multiple boundary (e.g. 10 items, page size 5, expect 2 pages).
