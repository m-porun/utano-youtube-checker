export interface VideoData {
  title: string | null;
  videoId: string;
  rokkoCount: number;
  timestamps: string[];
}

export interface ApiResponse {
  totalCount: number;
  updatedAt: string; // 最終確認日
  videos: VideoData[]; // 動画配列
}

export function isApiResponse(value: unknown): value is ApiResponse {
  if (!value || typeof value !== "object") return false;
  const data = value as Record<string, unknown>;
  return typeof data.totalCount === "number" && typeof data.updatedAt === "string" && Array.isArray(data.videos) && data.videos.every((video) => {
    if (!video || typeof video !== "object") return false;
    const item = video as Record<string, unknown>;
    return typeof item.videoId === "string" && (typeof item.title === "string" || item.title === null) && typeof item.rokkoCount === "number" && Array.isArray(item.timestamps) && item.timestamps.every((timestamp) => typeof timestamp === "string");
  });
}
