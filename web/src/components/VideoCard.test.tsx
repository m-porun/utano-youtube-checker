import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { VideoData } from "../types";
import VideoCard from "./VideoCard";

const validVideo: VideoData = {
  title: "六甲おろし歌唱回",
  videoId: "abcD_efG-12",
  rokkoCount: 1,
  timestamps: ["01:02:03"],
};

describe("VideoCard", () => {
  it.each(["short-id", "abcD_efG!12"])("renders nothing for invalid video ID %s", (videoId) => {
    const { container } = render(<VideoCard video={{ ...validVideo, videoId }} />);

    expect(container.innerHTML).toBe("");
  });

  it("uses a start timestamp in the YouTube embed URL", () => {
    render(<VideoCard video={validVideo} />);

    expect(screen.getByTitle("六甲おろし歌唱回").getAttribute("src")).toBe(
      "https://www.youtube.com/embed/abcD_efG-12?start=3723",
    );
  });

  it("shows a fallback for a missing title", () => {
    render(<VideoCard video={{ ...validVideo, title: null }} />);

    expect(screen.getAllByText("タイトルを取得できませんでした")).not.toHaveLength(0);
  });

  it("orders the title, embedded video, and timestamps in the card", () => {
    const { container } = render(<VideoCard video={validVideo} />);

    const title = container.querySelector("h2")!;
    const iframe = container.querySelector("iframe")!;
    const timestamp = container.querySelector("a")!;

    expect(title.compareDocumentPosition(iframe)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
    expect(iframe.compareDocumentPosition(timestamp)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });
});
