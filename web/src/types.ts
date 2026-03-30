// GAS APIが返すJSONの型定義

// 動画1件分のデータ
export interface VideoData {
  index: number; // 検索件数
  title: string;
  videoId: string;
  rokkoCount: number;
  timestamps: string[];
}

// 全体のAPIレスポンス
export interface ApiResponse {
  totalCount: number;
  updatedAt: string; // 最終確認日
  videos: VideoData[]; // 動画配列
}
