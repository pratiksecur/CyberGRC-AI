import api from "./axios";

/*
 * The list endpoints return at most one page per request (500 rows by
 * default) and report the full row count in the X-Total-Count header.
 *
 * getAllPages follows the pages until every row has been fetched, so a list
 * is never silently cut short when the data grows beyond one page.
 */

const PAGE_SIZE = 500;

// Safety stop in case the server never reports that it is finished.
const MAX_PAGES = 200;

export async function getAllPages<T>(
  path: string
): Promise<T[]> {
  const items: T[] = [];

  let offset = 0;

  for (let page = 0; page < MAX_PAGES; page += 1) {
    const response = await api.get<T[]>(path, {
      params: {
        limit: PAGE_SIZE,
        offset,
      },
    });

    items.push(...response.data);

    offset += response.data.length;

    const total = Number(
      response.headers["x-total-count"]
    );

    // No more rows, no total reported, or everything has been fetched.
    if (
      response.data.length === 0 ||
      !Number.isFinite(total) ||
      offset >= total
    ) {
      break;
    }
  }

  return items;
}
