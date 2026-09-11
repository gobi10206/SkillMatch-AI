export interface UserOut {
  id: string;
  email: string;
  full_name: string;
  role: "job_seeker" | "employer" | "admin";
  is_active: boolean;
  is_verified: boolean;
}

export interface SkillGapOut {
  career_id: string;
  career_title: string;
  match_score: number;
  existing_skills: string[];
  missing_skills: string[];
  explanation: string;
}

export interface JobMatchOut {
  job_id: string;
  job_title: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation: string;
}
