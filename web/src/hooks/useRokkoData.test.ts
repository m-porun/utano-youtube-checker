import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useRokkoData } from "./useRokkoData";

const validData = {
  totalCount: 1,
  updatedAt: "2026-09-15",
  videos: [{ videoId: "abcD_efG-12", title: "title", rokkoCount: 1, timestamps: ["0:01:02"] }],
};

afterEach(() => vi.unstubAllGlobals());

describe("useRokkoData", () => {
  it("stores valid data", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(validData))));
    const { result } = renderHook(() => useRokkoData());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toEqual(validData);
  });

  it("stores an HTTP error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("", { status: 500 })),
    );
    const { result } = renderHook(() => useRokkoData());
    await waitFor(() => expect(result.current.error?.message).toBe("HTTP 500"));
  });

  it("stores an error for malformed JSON data", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}")));
    const { result } = renderHook(() => useRokkoData());
    await waitFor(() => expect(result.current.error?.message).toBe("データ形式が不正です"));
  });
});
