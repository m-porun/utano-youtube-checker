import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TimestampList, { toSeconds } from "./TimestampList";

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

describe("TimestampList", () => {
  it("shows a heading when timestamps are available", () => {
    render(<TimestampList videoId="abcD_efG-12" timestamps={["01:02:03"]} />);

    expect(screen.getByText("六甲おろしタイム")).toBeTruthy();
  });

  it("does not show a heading when timestamps are unavailable", () => {
    const { container } = render(<TimestampList videoId="abcD_efG-12" timestamps={[]} />);

    expect(container.querySelector("h3")).toBeNull();
  });
});
