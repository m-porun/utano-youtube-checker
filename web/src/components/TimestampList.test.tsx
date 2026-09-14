import { describe, expect, it } from "vitest";
import { toSeconds } from "./TimestampList";

describe("toSeconds", () => {
  it("converts h:mm:ss to seconds", () => {
    expect(toSeconds("1:02:03")).toBe(3723);
  });

  it("converts mm:ss to seconds", () => {
    expect(toSeconds("02:03")).toBe(123);
  });

  it.each(["abc", "1:2:3:4", "aa:bb"])("returns 0 for invalid timestamp %s", (timestamp) => {
    expect(toSeconds(timestamp)).toBe(0);
  });
});
