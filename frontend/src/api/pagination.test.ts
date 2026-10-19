import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./axios", () => ({
  default: { get: vi.fn() },
}));

import api from "./axios";
import { getAllPages } from "./pagination";

const get = vi.mocked(api.get);

function page(count: number, total?: number) {
  return {
    data: Array.from({ length: count }, (_, index) => ({ id: index })),
    headers: total === undefined ? {} : { "x-total-count": String(total) },
  } as never;
}

describe("getAllPages", () => {
  beforeEach(() => {
    get.mockReset();
  });

  it("returns a single page in one request", async () => {
    get.mockResolvedValueOnce(page(2, 2));

    const items = await getAllPages("/risks/");

    expect(items).toHaveLength(2);
    expect(get).toHaveBeenCalledTimes(1);
    expect(get).toHaveBeenCalledWith("/risks/", {
      params: { limit: 500, offset: 0 },
    });
  });

  it("keeps fetching until every row has arrived", async () => {
    get
      .mockResolvedValueOnce(page(500, 1200))
      .mockResolvedValueOnce(page(500, 1200))
      .mockResolvedValueOnce(page(200, 1200));

    const items = await getAllPages("/risks/");

    expect(items).toHaveLength(1200);
    expect(get).toHaveBeenCalledTimes(3);

    const offsets = get.mock.calls.map(
      (call) =>
        (call[1] as { params: { offset: number } }).params.offset
    );

    expect(offsets).toEqual([0, 500, 1000]);
  });

  it("stops after one page when the server reports no total", async () => {
    get.mockResolvedValueOnce(page(3));

    const items = await getAllPages("/risks/");

    expect(items).toHaveLength(3);
    expect(get).toHaveBeenCalledTimes(1);
  });

  it("stops on an empty page even if the total says more", async () => {
    get
      .mockResolvedValueOnce(page(500, 900))
      .mockResolvedValueOnce(page(0, 900));

    const items = await getAllPages("/risks/");

    expect(items).toHaveLength(500);
    expect(get).toHaveBeenCalledTimes(2);
  });

  it("returns an empty list when there is nothing", async () => {
    get.mockResolvedValueOnce(page(0, 0));

    expect(await getAllPages("/risks/")).toEqual([]);
  });
});
