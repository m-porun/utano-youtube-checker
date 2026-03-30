// GAS APIデータ取得用カスタムフック
import { useEffect, useState } from "react";
import type { ApiResponse } from "../types";

const GAS_URL = import.meta.env.VITE_GAS_URL as string;

export function useRokkoData() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(GAS_URL)
      .then((res) => res.json())
      .then((json: ApiResponse) => setData(json))
      .catch((err: unknown) =>
        setError(err instanceof Error ? err : new Error(String(err))),
      )
      .finally(() => setLoading(false));
  }, []);

  // data(取得データ), loading(読み込み中かどうか), error(エラーがあればErrorオブジェクト)
  return { data, loading, error };
}
