// イントロ演出
// 5秒ずつ2つのメッセージをフェードイン・フェードアウトで表示
import { useEffect, useState } from "react";

type Phase = 0 | 1 | 2;

interface IntroSequenceProps {
  /** 10秒経過時にデータ取得が完了しているか */
  isReady: boolean;
  /** データ取得に失敗したか */
  hasError: boolean;
  /** イントロ終了時に呼ばれるコールバック */
  onComplete: () => void;
}

export default function IntroSequence({
  isReady,
  hasError,
  onComplete,
}: IntroSequenceProps) {
  // phase 0: 「これまでにウタノンが歌った六甲おろし…」
  // phase 1: 「その数は…」
  // phase 2: 完了判定
  const [phase, setPhase] = useState<Phase>(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // phase 0 開始: フェードイン
    const fadeInTimer = setTimeout(() => setVisible(true), 100);

    // phase 0 → フェードアウト（3秒後）
    const fadeOut0 = setTimeout(() => setVisible(false), 3000);

    // phase 1 開始（5秒後）
    const phase1Start = setTimeout(() => {
      setPhase(1);
      setVisible(true);
    }, 5000);

    // phase 1 → フェードアウト（8秒後）
    const fadeOut1 = setTimeout(() => setVisible(false), 8000);

    // phase 2: 完了判定（10秒後）
    const phase2Start = setTimeout(() => setPhase(2), 10000);

    return () => {
      clearTimeout(fadeInTimer);
      clearTimeout(fadeOut0);
      clearTimeout(phase1Start);
      clearTimeout(fadeOut1);
      clearTimeout(phase2Start);
    };
  }, []);

  // phase 2 に到達したら判定
  useEffect(() => {
    if (phase !== 2) return;
    if (isReady && !hasError) {
      onComplete();
    }
  }, [phase, isReady, hasError, onComplete]);

  if (phase === 2 && (hasError || !isReady)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-amber-50 px-4">
        <p className="text-center text-lg text-gray-600">
          ごめんね、時間を置いてからもう一度見に来てね
        </p>
      </div>
    );
  }

  const messages = [
    "これまでにウタノンが歌った六甲おろし…",
    "その数は…",
  ];

  return (
    <div className="flex min-h-screen items-center justify-center bg-amber-50 px-4">
      <p
        className={`text-center text-2xl font-bold text-gray-700 transition-opacity duration-2000 ${
          visible ? "opacity-100" : "opacity-0"
        }`}
      >
        {messages[phase === 2 ? 1 : phase]}
      </p>
    </div>
  );
}
