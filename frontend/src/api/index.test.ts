import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

type Api = typeof import("./index");

// Re-import for each test so the module-level memo caches start empty.
async function freshApi(): Promise<Api> {
  vi.resetModules();
  return (await import("./index")) as Api;
}

function mockFetchOnce(body: unknown, init: Partial<Response> = {}): void {
  const response = {
    ok: true,
    status: 200,
    statusText: "OK",
    json: async () => body,
    ...init,
  } as Response;
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => response),
  );
}

describe("api", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetches companies.json under the Vite base URL", async () => {
    const fetchSpy = vi.fn<typeof fetch>(
      async () => ({ ok: true, json: async () => ({ companies: [] }) }) as Response,
    );
    vi.stubGlobal("fetch", fetchSpy);

    const api = await freshApi();
    await api.loadCompanies();

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const requestedUrl = fetchSpy.mock.calls[0][0] as string;
    expect(requestedUrl.endsWith("/data/companies.json")).toBe(true);
  });

  it("memoises loadCompanies so repeated calls share one fetch", async () => {
    const fetchSpy = vi.fn<typeof fetch>(
      async () => ({ ok: true, json: async () => ({ companies: [] }) }) as Response,
    );
    vi.stubGlobal("fetch", fetchSpy);

    const api = await freshApi();
    const [a, b] = await Promise.all([api.loadCompanies(), api.loadCompanies()]);

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(a).toBe(b);
  });

  it("caches loadChangeDetail per id", async () => {
    const fetchSpy = vi.fn<typeof fetch>(
      async () => ({ ok: true, json: async () => ({ id: "x" }) }) as Response,
    );
    vi.stubGlobal("fetch", fetchSpy);

    const api = await freshApi();
    await api.loadChangeDetail("abc");
    await api.loadChangeDetail("abc");
    await api.loadChangeDetail("def");

    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });

  it("URL-encodes change ids so slashes don't escape the data directory", async () => {
    const fetchSpy = vi.fn<typeof fetch>(
      async () => ({ ok: true, json: async () => ({}) }) as Response,
    );
    vi.stubGlobal("fetch", fetchSpy);

    const api = await freshApi();
    await api.loadChangeDetail("weird/id with space");

    const requestedUrl = fetchSpy.mock.calls[0][0] as string;
    expect(requestedUrl).toContain("/data/changes/weird%2Fid%20with%20space.json");
  });

  it("throws a descriptive error on a non-OK response", async () => {
    mockFetchOnce(null, {
      ok: false,
      status: 404,
      statusText: "Not Found",
    } as Partial<Response>);

    const api = await freshApi();
    await expect(api.loadCompanies()).rejects.toThrow(/404 Not Found/);
  });
});
