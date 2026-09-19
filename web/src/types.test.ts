import { describe, expect, it } from "vitest";
import { isApiResponse } from "./types";

describe("isApiResponse", () => {
  it("accepts the public JSON schema", () => {
    expect(isApiResponse({ totalCount: 1, updatedAt: "2026-09-15", videos: [{ videoId: "abcD_efG-12", title: null, rokkoCount: 1, timestamps: ["0:01:02"] }] })).toBe(true);
  });

  it("rejects missing or incorrectly typed fields", () => {
    expect(isApiResponse({ totalCount: "1", videos: [] })).toBe(false);
  });

  it.each([
    { totalCount: 1, updatedAt: "2026-09-15", videos: {} },
    { totalCount: 1, updatedAt: "2026-09-15", videos: [{ videoId: "x", title: 1, rokkoCount: 1, timestamps: [] }] },
    { totalCount: 1, updatedAt: "2026-09-15", videos: [{ videoId: "x", title: null, rokkoCount: 1, timestamps: [1] }] },
    { totalCount: 1, updatedAt: "2026-09-15", videos: [{ videoId: "x", title: null, rokkoCount: "1", timestamps: [] }] },
  ])("rejects malformed video values", (value) => {
    expect(isApiResponse(value)).toBe(false);
  });
});
