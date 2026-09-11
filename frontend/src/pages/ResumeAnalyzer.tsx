import { useState } from "react";
import { api } from "../services/api";

interface ExtractedSkill {
  skill_id: string;
  skill_name: string;
  confidence: number;
  method: string;
  evidence_text: string;
}

export default function ResumeAnalyzer() {
  const [resumeText, setResumeText] = useState("");
  const [extracted, setExtracted] = useState<ExtractedSkill[]>([]);
  const [accepted, setAccepted] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function analyze() {
    const { data } = await api.post("/resume/analyze", { resume_text: resumeText });
    setExtracted(data.extracted_skills);
    setAccepted(new Set(data.extracted_skills.map((s: ExtractedSkill) => s.skill_id)));
  }

  function toggle(skillId: string) {
    setAccepted((prev) => {
      const next = new Set(prev);
      next.has(skillId) ? next.delete(skillId) : next.add(skillId);
      return next;
    });
  }

  async function confirmSkills() {
    setSubmitting(true);
    const actions = extracted.map((s) => ({
      skill_id: s.skill_id,
      action: accepted.has(s.skill_id) ? "accept" : "reject",
    }));
    await api.post("/skills/verify", actions);
    setSubmitting(false);
    setMessage("Skills saved to your profile.");
  }

  return (
    <main className="min-h-screen bg-slate-900 text-white p-8 max-w-3xl mx-auto space-y-6">
      <h1 className="text-3xl font-semibold">Resume Analyzer</h1>
      <p className="text-slate-400 text-sm">
        Paste your resume or describe your experience — including informal, freelance, or volunteer
        work. AI-inferred skills are shown below for you to review before they're saved.
      </p>

      <textarea
        value={resumeText} onChange={(e) => setResumeText(e.target.value)} rows={8}
        placeholder="Paste your resume text or describe your experience here..."
        className="w-full p-3 rounded bg-slate-800 outline-none"
      />
      <button onClick={analyze} className="bg-indigo-600 hover:bg-indigo-500 px-5 py-2 rounded font-medium">
        Analyze
      </button>

      {extracted.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-xl font-medium">AI-Inferred Skills — review before saving</h2>
          {extracted.map((s) => (
            <label key={s.skill_id} className="flex items-start gap-3 bg-slate-800 p-3 rounded-lg cursor-pointer">
              <input type="checkbox" checked={accepted.has(s.skill_id)} onChange={() => toggle(s.skill_id)} className="mt-1" />
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{s.skill_name}</span>
                  <span className="text-xs text-slate-500">
                    {Math.round(s.confidence * 100)}% confidence · {s.method}
                  </span>
                </div>
                <p className="text-xs text-slate-500 italic">"{s.evidence_text}"</p>
              </div>
            </label>
          ))}
          <button
            onClick={confirmSkills} disabled={submitting}
            className="bg-emerald-600 hover:bg-emerald-500 px-5 py-2 rounded font-medium"
          >
            {submitting ? "Saving..." : "Save Reviewed Skills"}
          </button>
          {message && <p className="text-emerald-400 text-sm">{message}</p>}
        </section>
      )}
    </main>
  );
}
