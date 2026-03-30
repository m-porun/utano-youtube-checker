import { useCallback, useMemo, useState } from "react";
import { useRokkoData } from "./hooks/useRokkoData";
import type { VideoData } from "./types";
import IntroSequence from "./components/IntroSequence";
import RokkoCount from "./components/RokkoCount";
import VideoCard from "./components/VideoCard";

function sortVideos(videos: VideoData[]): VideoData[] {
  return [...videos].sort((a, b) => {
    if (b.rokkoCount !== a.rokkoCount) return b.rokkoCount - a.rokkoCount;
    return a.index - b.index;
  });
}

export default function App() {
  const { data, loading, error } = useRokkoData();
  const [introDone, setIntroDone] = useState(false);

  const handleIntroComplete = useCallback(() => setIntroDone(true), []);

  const sortedVideos = useMemo(() => {
    if (!data) return [];
    return sortVideos(data.videos);
  }, [data]);

  if (!introDone) {
    return (
      <IntroSequence
        isReady={!loading && !!data}
        hasError={!!error}
        onComplete={handleIntroComplete}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <RokkoCount count={data!.totalCount} updatedAt={data!.updatedAt} />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <h2 className="mb-6 text-xl font-bold text-gray-700">
          六甲おろしを歌った配信一覧
        </h2>
        <div className="flex flex-col gap-6">
          {sortedVideos.map((video) => (
            <VideoCard key={video.videoId} video={video} />
          ))}
        </div>
      </main>
      <footer className="py-8 text-center text-sm text-gray-400">
        &copy; UTANO ch. 白玖ウタノ 非公式ファンサイト
      </footer>
    </div>
  );
}
