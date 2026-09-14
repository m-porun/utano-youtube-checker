import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { VideoData } from "../types";
import VideoCard from "./VideoCard";

const validVideo: VideoData = {
  index: 1,
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

    expect(screen.getByTitle(validVideo.title).getAttribute("src")).toBe(
      "https://www.youtube.com/embed/abcD_efG-12?start=3723",
    );
  });
});
