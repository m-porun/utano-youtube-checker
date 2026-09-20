import { wobbleStyle } from "./wobble";
import heroImage from "../assets/hero.png";

interface RokkoCountProps {
  count: number;
  updatedAt: string;
}

export default function RokkoCount({ count, updatedAt }: RokkoCountProps) {
  return (
    <section className="relative flex min-h-[60vh] flex-col items-center justify-center overflow-hidden px-4 py-8 text-center shadow-[0_8px_16px_rgba(0,0,0,0.45)]">
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-[#E1DCDC] bg-cover bg-center"
        style={{ backgroundImage: `url(${heroImage})` }}
      />
      <div className="relative flex flex-col items-center">
        <div aria-label="白玖ウタノ" className="relative mb-4 inline-block max-w-full">
          <span className="bg-[linear-gradient(180deg,#CE2D54_0%,#CE2D54_70%,#500F14_100%)] bg-clip-text text-5xl leading-none text-transparent sm:text-6xl">
            白玖ウタノ
          </span>
          <span aria-hidden="true" className="absolute bottom-0 right-0 text-sm text-[#CE2D54]">
            の
          </span>
        </div>
        <h1 className="mb-4 text-2xl text-[#3C393E] sm:text-3xl">
          六甲おろし歌唱回数
        </h1>
        <div className="heart-wobble relative h-[174px] w-[240px]" style={wobbleStyle(count)}>
          <svg viewBox="0 0 496 359" aria-hidden="true" className="absolute inset-0 h-full w-full">
            <path
              d="M247.698 72.3805C287.183 15.3272 317.758 3.82722 360.924 0.327238C427.733 -5.08969 504.643 57.3272 494.486 144.327C475.452 307.37 287.743 292.34 247.698 358.328V72.3805Z"
              fill="#CE2D54"
            />
            <path
              d="M247.698 72.3805C208.212 15.3272 177.637 3.82722 134.471 0.327238C67.6623 -5.08969 -9.24763 57.3272 0.908873 144.327C19.9433 307.37 207.652 292.34 247.698 358.328V72.3805Z"
              fill="#CE2D54"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="-translate-y-[5px] text-8xl tabular-nums leading-none text-[#F2E7DD]">
              {count}
            </span>
            <span className="ml-1 self-end -translate-y-[5px] pb-6 text-sm text-[#F2E7DD]">回</span>
          </div>
        </div>
        <p className="mt-4 text-sm text-[#3C393E]">
          最終更新: {updatedAt}
        </p>
      </div>
    </section>
  );
}
