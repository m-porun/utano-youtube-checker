// 動画カード
// 配信タイトル・歌った回数
import type { VideoData } from "../types";
import { wobbleStyle } from "./wobble";
import TimestampList, { toSeconds } from "./TimestampList";

interface VideoCardProps {
  video: VideoData;
}

export default function VideoCard({ video }: VideoCardProps) {
  // videoId は YouTube の仕様上 [A-Za-z0-9_-]{11} であることをバリデーション
  const safeVideoId = /^[A-Za-z0-9_-]{11}$/.test(video.videoId)
    ? video.videoId
    : "";

  if (!safeVideoId) return null;

  return (
    <article className="glass-card relative overflow-visible">
      <span
        className="heart-wobble absolute -right-3 -top-4 z-10 inline-flex h-[69px] w-24 items-center justify-center"
        style={wobbleStyle(video.rokkoCount)}
      >
        <svg viewBox="0 0 496 359" aria-hidden="true" className="absolute inset-0 h-full w-full">
          <path
            d="M247.698 72.3805C287.183 15.3272 317.758 3.82722 360.924 0.327238C427.733 -5.08969 504.643 57.3272 494.486 144.327C475.452 307.37 287.743 292.34 247.698 358.328V72.3805Z"
            fill="#3C393E"
          />
          <path
            d="M247.698 72.3805C208.212 15.3272 177.637 3.82722 134.471 0.327238C67.6623 -5.08969 -9.24763 57.3272 0.908873 144.327C19.9433 307.37 207.652 292.34 247.698 358.328V72.3805Z"
            fill="#3C393E"
          />
        </svg>
        <span className="relative -translate-y-[2px] text-2xl text-[#E1DCDC]">
          {video.rokkoCount}回
        </span>
      </span>
      <div className="px-4 pb-4 pt-6 sm:px-6 sm:pb-6 sm:pt-8">
        <h2 className="mb-4 pr-24 text-base leading-snug text-[#CE2D54] sm:text-lg">
          {video.title ?? "タイトルを取得できませんでした"}
        </h2>
      </div>
      <div className="mx-auto aspect-video w-[90%] overflow-hidden rounded-xl shadow-[0_10px_14px_-4px_rgba(60,57,62,0.6)]">
        <iframe
          src={`https://www.youtube.com/embed/${safeVideoId}${video.timestamps.length > 0 ? `?start=${toSeconds(video.timestamps[0])}` : ""}`}
          title={video.title ?? "タイトルを取得できませんでした"}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          loading="lazy"
          className="h-full w-full"
        />
      </div>
      <div className="px-4 pb-6 pt-6 sm:px-6 sm:pb-8 sm:pt-8">
        <TimestampList videoId={safeVideoId} timestamps={video.timestamps} />
      </div>
    </article>
  );
}
