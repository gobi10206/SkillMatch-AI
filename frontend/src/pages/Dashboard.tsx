import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { SkillGapOut, JobMatchOut } from "../types";

export default function Dashboard() {
  const [careers, setCareers] = useState<SkillGapOut[]>([]);
  const [jobs, setJobs] = useState<JobMatchOut[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [careerRes, jobRes] = await Promise.all([
          api.get("/career/recommend"),
          api.post("/jobs/match"),
        ]);
        setCareers(careerRes.data);
        setJobs(jobRes.data);
      } catch {
        // Errors surface as empty sections — a full toast/error UI is a later polish pass.
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <main className="min-h-screen bg-slate-900 text-white p-8">Loading your dashboard…</main>;

  return (
    <main className="min-h-screen bg-slate-900 text-white p-8 space-y-8">
      <h1 className="text-3xl font-semibold">Your Dashboard</h1>

      <section>
        <h2 className="text-xl font-medium mb-3">Recommended Careers</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {careers.map((c) => (
            <div key={c.career_id} className="bg-slate-800 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">{c.career_title}</h3>
                <span className="text-indigo-400 font-bold">{c.match_score}%</span>
              </div>
              <p className="text-sm text-slate-400 mb-2">{c.explanation}</p>
              {c.missing_skills.length > 0 && (
                <p className="text-xs text-amber-400">Missing: {c.missing_skills.join(", ")}</p>
              )}
            </div>
          ))}
          {careers.length === 0 && <p className="text-slate-500">No recommendations yet — add skills to your profile first.</p>}
        </div>
      </section>

      <section>
        <h2 className="text-xl font-medium mb-3">Job Matches</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {jobs.map((j) => (
            <div key={j.job_id} className="bg-slate-800 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">{j.job_title}</h3>
                <span className="text-indigo-400 font-bold">{j.match_score}%</span>
              </div>
              <p className="text-sm text-slate-400">{j.explanation}</p>
            </div>
          ))}
          {jobs.length === 0 && <p className="text-slate-500">No job matches yet.</p>}
        </div>
      </section>
    </main>
  );
}
