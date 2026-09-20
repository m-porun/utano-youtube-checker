// タイムスタンプバッジ
// 六甲おろしを歌ったところからYouTube観れる
interface TimestampListProps {
  videoId: string;
  timestamps: string[];
}

export function toSeconds(ts: string): number {
  const parts = ts.split(":").map(Number);
  if (parts.some((part) => Number.isNaN(part))) return 0;
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  return 0;
}

export default function TimestampList({
  videoId,
  timestamps,
}: TimestampListProps) {
  if (timestamps.length === 0) return null;

  return (
    <div>
      <h3 className="mb-3 text-sm text-[#3C393E]">六甲おろしタイム</h3>
      <div className="flex flex-wrap gap-2">
        {timestamps.map((ts, i) => (
          <a
            key={i}
            href={`https://www.youtube.com/watch?v=${videoId}&t=${toSeconds(ts)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-full bg-[#BFBABA] px-3 py-1 text-sm font-medium text-[#3C393E] transition hover:bg-[#3C393E] hover:text-[#E1DCDC]"
          >
            {ts}
          </a>
        ))}
      </div>
    </div>
  );
}
