import { useCallback, useMemo, useState } from "react";
import { useRokkoData } from "./hooks/useRokkoData";
import type { VideoData } from "./types";
import IntroSequence from "./components/IntroSequence";
import RokkoCount from "./components/RokkoCount";
import VideoCard from "./components/VideoCard";
import background from "./assets/background.jpg";

function sortVideos(videos: VideoData[]): VideoData[] {
  return [...videos].sort((a, b) => {
    if (b.rokkoCount !== a.rokkoCount) return b.rokkoCount - a.rokkoCount;
    if ((a.title === null) !== (b.title === null)) return a.title === null ? 1 : -1;
    return (a.title ?? "").localeCompare(b.title ?? "") || a.videoId.localeCompare(b.videoId);
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
    <div className="relative isolate min-h-screen">
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-0 bg-cover bg-center opacity-70"
        style={{ backgroundImage: `url(${background})` }}
      />
      <div
        aria-hidden="true"
        className="page-background pointer-events-none fixed inset-0 z-0 opacity-80"
      />
      <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-0 bg-[#F2E7DD]/50" />
      <div className="relative z-10">
        <RokkoCount count={data!.totalCount} updatedAt={data!.updatedAt} />
        <div className="mx-auto my-16 max-w-3xl px-4">
          <h2 className="rounded-2xl bg-[#CE2D54] px-4 py-4 text-center text-xl text-[#F2E7DD] shadow-[0_12px_32px_rgba(60,57,62,0.35)]">
            六甲おろしを歌った配信一覧
          </h2>
        </div>
        <main className="mx-auto max-w-3xl px-4 pb-8 pt-0">
          <div className="flex flex-col gap-[72px]">
            {sortedVideos.map((video) => (
              <VideoCard key={video.videoId} video={video} />
            ))}
          </div>
        </main>
        <footer className="py-8 text-center text-sm text-[#3C393E]">
          白玖ウタノ-六甲おろしカウンター
        </footer>
      </div>
    </div>
  );
}
