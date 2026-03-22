"use client";

import { useEffect, useMemo, useState } from "react";
import RecommendationCard from "../src/components/RecommendationCard";
import Sidebar from "../src/components/Sidebar";
import StatsCard from "../src/components/StatsCard";
import { getJobs, runRecommendations } from "../src/lib/api";
import type { Job, Recommendation } from "../src/types";

export default function HomePage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [skills, setSkills] = useState("Python, FastAPI, Docker, AWS");
  const [countries, setCountries] = useState("Germany");
  const [visaNeeded, setVisaNeeded] = useState(true);

  useEffect(() => {
    async function loadJobs() {
      try {
        setLoadingJobs(true);
        const data = await getJobs();
        setJobs(Array.isArray(data) ? data : []);
      } catch (err) {
        setError("jobs 데이터를 불러오지 못했습니다.");
      } finally {
        setLoadingJobs(false);
      }
    }

    loadJobs();
  }, []);

  async function handleRunRecommendations() {
    try {
      setLoadingRecommendations(true);
      setError(null);

      const data = await runRecommendations({
        skills: skills
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        preferred_countries: countries
          .split(",")
          .map((c) => c.trim())
          .filter(Boolean),
        visa_needed: visaNeeded,
      });

      if (Array.isArray(data)) {
        setRecommendations(data);
      } else if (data.recommendations) {
        setRecommendations(data.recommendations);
      } else {
        setRecommendations([data]);
      }
    } catch (err) {
      setError("recommendations 실행에 실패했습니다.");
    } finally {
      setLoadingRecommendations(false);
    }
  }

  const averageMatchScore = useMemo(() => {
    if (recommendations.length === 0) return 0;
    const total = recommendations.reduce(
      (sum, item) => sum + (item.match_score ?? 0),
      0
    );
    return Math.round(total / recommendations.length);
  }, [recommendations]);

  const topMatchesCount = useMemo(() => {
    return recommendations.filter((item) => (item.match_score ?? 0) >= 90)
      .length;
  }, [recommendations]);

  return (
    <main className="min-h-screen bg-black text-white px-4 py-6 md:px-6">
      <div className="mx-auto max-w-[1440px] lg:flex lg:gap-6">
        <Sidebar />

        <div className="flex-1">
          <div className="mb-10">
            <p className="text-[11px] uppercase tracking-[0.22em] text-zinc-500 mb-3">
              Precision Intelligence
            </p>
            <h1 className="text-4xl md:text-5xl font-black tracking-tight mb-3">
              AI Job Scout Dashboard
            </h1>
            <p className="text-zinc-400 max-w-2xl">
              FastAPI 기반 AI 채용 추천 시스템 프론트엔드. 실시간 채용 공고,
              AI 분석 파이프라인, explainable recommendation scoring을 한 화면에서
              확인합니다.
            </p>
          </div>

          <section className="grid gap-4 md:grid-cols-3 mb-8">
            <StatsCard
              label="Stored Jobs"
              value={jobs.length}
              subtext="현재 저장된 채용 공고 수"
            />
            <StatsCard
              label="Average Match Score"
              value={`${averageMatchScore}%`}
              accent="cyan"
              subtext="추천 결과 평균 점수"
            />
            <StatsCard
              label="Top Matches"
              value={topMatchesCount}
              accent="purple"
              subtext="90점 이상 추천 공고"
            />
          </section>

          <section className="rounded-2xl border border-white/5 bg-[#111111] p-6 mb-8">
            <div className="flex items-start justify-between gap-4 mb-6 flex-col md:flex-row md:items-center">
              <div>
                <p className="text-[11px] uppercase tracking-[0.2em] text-zinc-500 mb-2">
                  Recommendation Engine
                </p>
                <h2 className="text-2xl font-bold">Run Recommendations</h2>
              </div>

              <div className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs text-cyan-300">
                Curator Active
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Skills
                </label>
                <input
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-[#181818] px-4 py-3 outline-none focus:border-cyan-400/40"
                  placeholder="Python, FastAPI, Docker"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Preferred Countries
                </label>
                <input
                  value={countries}
                  onChange={(e) => setCountries(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-[#181818] px-4 py-3 outline-none focus:border-cyan-400/40"
                  placeholder="Germany, Netherlands"
                />
              </div>
            </div>

            <label className="flex items-center gap-3 mt-4">
              <input
                type="checkbox"
                checked={visaNeeded}
                onChange={(e) => setVisaNeeded(e.target.checked)}
              />
              <span className="text-sm text-zinc-300">
                Visa sponsorship needed
              </span>
            </label>

            <button
              onClick={handleRunRecommendations}
              disabled={loadingRecommendations}
              className="mt-6 rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-black disabled:opacity-50 hover:brightness-110 transition"
            >
              {loadingRecommendations ? "Running..." : "Run Recommendation Engine"}
            </button>
          </section>

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
              {error}
            </div>
          )}

          <section className="mb-10">
            <div className="flex items-center justify-between gap-4 mb-4">
              <div>
                <p className="text-[11px] uppercase tracking-[0.2em] text-zinc-500 mb-2">
                  Ranked Output
                </p>
                <h2 className="text-2xl font-bold">Recommended Jobs</h2>
              </div>

              <span className="text-sm text-zinc-500">
                {recommendations.length} results
              </span>
            </div>

            {recommendations.length === 0 ? (
              <div className="rounded-2xl border border-white/5 bg-[#111111] p-6 text-zinc-400">
                아직 추천 결과가 없습니다. 위에서 추천을 실행하세요.
              </div>
            ) : (
              <div className="grid gap-4 xl:grid-cols-2">
                {recommendations.map((job, index) => (
                  <RecommendationCard
                    key={job.id ?? index}
                    job={job}
                    index={index}
                  />
                ))}
              </div>
            )}
          </section>

          <section>
            <div className="flex items-center justify-between gap-4 mb-4">
              <div>
                <p className="text-[11px] uppercase tracking-[0.2em] text-zinc-500 mb-2">
                  Source Data
                </p>
                <h2 className="text-2xl font-bold">Stored Jobs</h2>
              </div>

              <span className="text-sm text-zinc-500">
                {loadingJobs ? "Loading..." : `${jobs.length} jobs`}
              </span>
            </div>

            {loadingJobs ? (
              <div className="rounded-2xl border border-white/5 bg-[#111111] p-6 text-zinc-400">
                jobs 불러오는 중...
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {jobs.map((job, index) => (
                  <div
                    key={job.id ?? index}
                    className="rounded-xl border border-white/5 bg-[#111111] p-5 hover:bg-[#161616] transition-colors"
                  >
                    <h3 className="text-lg font-semibold">
                      {job.title ?? "Untitled Job"}
                    </h3>
                    <p className="text-sm text-zinc-400 mt-1">
                      {job.company ?? "Unknown Company"} ·{" "}
                      {job.location ?? "Location not specified"}
                    </p>

                    {job.url && (
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-block mt-4 text-sm text-cyan-400 hover:underline"
                      >
                        Open original posting →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}