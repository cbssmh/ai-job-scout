type Props = {
  label: string;
  value: string | number;
  accent?: "cyan" | "purple" | "default";
  subtext?: string;
};

export default function StatsCard({
  label,
  value,
  accent = "default",
  subtext,
}: Props) {
  const valueColor =
    accent === "cyan"
      ? "text-cyan-300"
      : accent === "purple"
      ? "text-purple-300"
      : "text-white";

  return (
    <div className="rounded-xl border border-white/5 bg-[#111111] p-5 hover:bg-[#161616] transition-colors min-h-[124px]">
      <p className="text-[11px] uppercase tracking-[0.18em] text-zinc-500">
        {label}
      </p>
      <p className={`mt-4 text-4xl font-black ${valueColor}`}>{value}</p>
      {subtext ? (
        <p className="mt-3 text-xs text-zinc-500">{subtext}</p>
      ) : null}
    </div>
  );
}