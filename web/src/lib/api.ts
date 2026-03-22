const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function getJobs() {
  const res = await fetch(`${API_BASE_URL}/jobs/`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch jobs");
  }

  return res.json();
}

export async function getAnalysis() {
  const res = await fetch(`${API_BASE_URL}/analysis/`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch analysis");
  }

  return res.json();
}

export async function runRecommendations(payload: {
  skills: string[];
  preferred_countries: string[];
  visa_needed: boolean;
}) {
  const res = await fetch(`${API_BASE_URL}/recommendations/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Failed to run recommendations");
  }

  return res.json();
}