export type Job = {
  id?: number | string;
  title?: string;
  company?: string;
  location?: string;
  url?: string;
};

export type AnalysisResult = {
  id?: number | string;
  role?: string;
  tech_stack?: string | string[];
  experience_level?: string;
  language_requirement?: string;
  visa_sponsorship?: boolean | string;
};

export type Recommendation = {
  id?: number | string;
  title?: string;
  company?: string;
  location?: string;
  match_score?: number;
  skill_score?: number;
  language_bonus?: number;
  visa_bonus?: number;
  location_bonus?: number;
  matched_skills?: string[];
  missing_skills?: string[];
};