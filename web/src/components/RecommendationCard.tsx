import Link from "next/link";
import type { Recommendation } from "../types";

type Props = {
  job: Recommendation;
  index: number;
};

export default function RecommendationCard({ job, index }: Props) {
  const score = job.match_score ?? 0;

  const matchLabel =
    score >= 90 ? "High Match" : score >= 70 ? "Strong Match" : "Match";

  const matchLabelColor =
    score >= 90
      ? "text-cyan-300"
      : score >= 70
      ? "text-zinc-300"
      : "text-purple-300";

  const tagList =
    job.matched_skills && job.matched_skills.length > 0
      ? job.matched_skills
      : [];

  const companyInitial = (job.company ?? "U").charAt(0).toUpperCase();

  return (
    <div className="group bg-[#131313] hover:bg-[#1a1919] transition-colors p-5 rounded-xl border border-white/5 flex flex-col md:flex-row gap-5">
      <div className="flex-shrink-0">
        <div className="w-14 h-14 bg-black rounded-xl flex items-center justify-center border border-white/10 text-zinc-300 text-base font-bold">
          {companyInitial}
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex justify-between items-start gap-4">
          <div className="min-w-0">
            <h3 className="text-lg font-bold text-white pr-4 leading-snug line-clamp-2">
              <Link
                href={`/job/${job.id ?? index}`}
                className="hover:text-cyan-300 transition-colors"
              >
                {job.title ?? "Untitled Job"}
              </Link>
            </h3>

            <p className="text-sm text-zinc-400 font-medium mt-2">
              {job.company ?? "Unknown Company"} •{" "}
              {job.location ?? "Location not specified"}
            </p>
          </div>

          <div className="flex flex-col items-end shrink-0">
            <span
              className={`text-[10px] uppercase font-bold tracking-widest ${matchLabelColor}`}
            >
              {matchLabel}
            </span>
            <span className="text-2xl font-black text-white">{score}%</span>
          </div>
        </div>

        {tagList.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4 mt-4">
            {tagList.slice(0, 4).map((skill) => (
              <span
                key={skill}
                className="px-2 py-0.5 bg-[#262626] text-[10px] rounded text-zinc-300 border border-white/10"
              >
                {skill}
              </span>
            ))}
          </div>
        )}

        <div className="grid grid-cols-2 gap-3 mt-1">
          <div className="rounded-xl bg-[#1a1a1a] p-3">
            <p className="text-zinc-500 text-xs">Skill Score</p>
            <p className="mt-1 font-semibold text-white">
              {job.skill_score ?? 0}
            </p>
          </div>
          <div className="rounded-xl bg-[#1a1a1a] p-3">
            <p className="text-zinc-500 text-xs">Language Bonus</p>
            <p className="mt-1 font-semibold text-white">
              {job.language_bonus ?? 0}
            </p>
          </div>
          <div className="rounded-xl bg-[#1a1a1a] p-3">
            <p className="text-zinc-500 text-xs">Visa Bonus</p>
            <p className="mt-1 font-semibold text-white">
              {job.visa_bonus ?? 0}
            </p>
          </div>
          <div className="rounded-xl bg-[#1a1a1a] p-3">
            <p className="text-zinc-500 text-xs">Location Bonus</p>
            <p className="mt-1 font-semibold text-white">
              {job.location_bonus ?? 0}
            </p>
          </div>
        </div>

        {job.missing_skills && job.missing_skills.length > 0 && (
          <div className="mt-4">
            <p className="text-xs text-zinc-500 mb-2 uppercase tracking-wide">
              Missing Skills
            </p>
            <div className="flex flex-wrap gap-2">
              {job.missing_skills.slice(0, 4).map((skill) => (
                <span
                  key={skill}
                  className="px-2 py-0.5 bg-red-500/10 text-[10px] rounded text-red-300 border border-red-500/20"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="pt-4 border-t border-white/5 flex justify-between items-center mt-4">
          <span className="text-[10px] text-zinc-500">
            AI-ranked recommendation
          </span>

          <Link
            href={`/job/${job.id ?? index}`}
            className="text-xs font-bold text-cyan-300 hover:underline flex items-center gap-1"
          >
            View Intelligence Report →
          </Link>
        </div>
      </div>
    </div>
  );
}