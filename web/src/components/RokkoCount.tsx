interface RokkoCountProps {
  count: number;
  updatedAt: string;
}

export default function RokkoCount({ count, updatedAt }: RokkoCountProps) {
  return (
    <section className="flex min-h-[60vh] flex-col items-center justify-center bg-gradient-to-b from-amber-50 to-white px-4 text-center">
      <p className="mb-2 text-lg font-medium text-amber-700">
        白玖ウタノの
      </p>
      <h1 className="mb-4 text-2xl font-bold text-gray-800 sm:text-3xl">
        六甲おろし歌唱回数
      </h1>
      <p className="text-8xl font-black tabular-nums text-amber-600 sm:text-9xl">
        {count}
      </p>
      <p className="mt-2 text-lg text-gray-500">回</p>
      <p className="mt-6 text-sm text-gray-400">
        最終更新: {updatedAt}
      </p>
    </section>
  );
}
