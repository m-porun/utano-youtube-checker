// ビルド時に生成した静的 JSON を取得するカスタムフック
import { useEffect, useState } from "react";
import { isApiResponse, type ApiResponse } from "../types";

export function useRokkoData() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/rokko.json`, { cache: "no-cache" })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json: unknown) => {
        if (!isApiResponse(json)) throw new Error("データ形式が不正です");
        setData(json);
      })
      .catch((err: unknown) =>
        setError(err instanceof Error ? err : new Error(String(err))),
      )
      .finally(() => setLoading(false));
  }, []);

  // data(取得データ), loading(読み込み中かどうか), error(エラーがあればErrorオブジェクト)
  return { data, loading, error };
}
