// 動画カード
// 配信タイトル・歌った回数
import type { VideoData } from "../types";
import TimestampList, { toSeconds } from "./TimestampList";

interface VideoCardProps {
  video: VideoData;
}

export default function VideoCard({ video }: VideoCardProps) {
  return (
    <article className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <div className="p-4 sm:p-6">
        <div className="mb-3 flex items-start justify-between gap-3">
          <h2 className="text-base font-bold leading-snug text-gray-800 sm:text-lg">
            {video.title}
          </h2>
          <span className="shrink-0 rounded-full bg-amber-500 px-3 py-1 text-sm font-bold text-white">
            {video.rokkoCount}回
          </span>
        </div>
        <div className="mb-4">
          <TimestampList videoId={video.videoId} timestamps={video.timestamps} />
        </div>
      </div>
      <div className="aspect-video w-full">
        <iframe
          src={`https://www.youtube.com/embed/${video.videoId}${video.timestamps.length > 0 ? `?start=${toSeconds(video.timestamps[0])}` : ""}`}
          title={video.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          loading="lazy"
          className="h-full w-full"
        />
      </div>
    </article>
  );
}
