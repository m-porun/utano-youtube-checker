import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "./App";

vi.mock("./hooks/useRokkoData", () => ({
  useRokkoData: () => ({
    data: { totalCount: 1, updatedAt: "2026-09-19", videos: [] },
    loading: false,
    error: null,
  }),
}));

vi.mock("./components/IntroSequence", () => ({
  default: ({ onComplete }: { onComplete: () => void }) => (
    <button type="button" onClick={onComplete}>
      イントロを完了する
    </button>
  ),
}));

describe("App", () => {
  it("shows the updated footer text", () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "イントロを完了する" }));

    expect(screen.getByText("白玖ウタノ-六甲おろしカウンター")).toBeTruthy();
  });
});
