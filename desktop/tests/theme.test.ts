import assert from "node:assert/strict";
import { afterEach, beforeEach, describe, it } from "node:test";

describe("theme", () => {
  const storage = new Map<string, string>();
  const doc = { dataset: {} as DOMStringMap };

  beforeEach(async () => {
    storage.clear();
    doc.dataset = {};
    globalThis.localStorage = {
      getItem: (k) => storage.get(k) ?? null,
      setItem: (k, v) => {
        storage.set(k, v);
      },
      removeItem: (k) => {
        storage.delete(k);
      },
    } as Storage;
    globalThis.document = { documentElement: doc } as Document;
  });

  afterEach(() => {
    delete (globalThis as { localStorage?: Storage }).localStorage;
    delete (globalThis as { document?: Document }).document;
  });

  it("defaults to dark and persists light", async () => {
    const { readTheme, writeTheme, applyDocumentTheme } = await import("../src/theme.ts");
    assert.equal(readTheme(), "dark");
    writeTheme("light");
    assert.equal(readTheme(), "light");
    assert.equal(doc.dataset.theme, "light");
    writeTheme("dark");
    assert.equal(readTheme(), "dark");
    assert.equal(doc.dataset.theme, undefined);
    applyDocumentTheme("light");
    assert.equal(doc.dataset.theme, "light");
  });
});
