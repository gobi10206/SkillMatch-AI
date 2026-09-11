import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("job_seeker");
  const { register, loading, error } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const ok = await register(email, password, fullName, role);
    if (ok) navigate("/onboarding");
  }

  return (
    <main className="min-h-screen bg-slate-900 text-white flex items-center justify-center px-6">
      <form onSubmit={handleSubmit} className="bg-slate-800 p-8 rounded-xl w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-semibold">Create your account</h1>
        <input
          placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)}
          className="w-full px-3 py-2 rounded bg-slate-700 outline-none" required
        />
        <input
          type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 rounded bg-slate-700 outline-none" required
        />
        <input
          type="password" placeholder="Password (min 8 characters)" value={password}
          onChange={(e) => setPassword(e.target.value)} minLength={8}
          className="w-full px-3 py-2 rounded bg-slate-700 outline-none" required
        />
        <select value={role} onChange={(e) => setRole(e.target.value)} className="w-full px-3 py-2 rounded bg-slate-700 outline-none">
          <option value="job_seeker">Job Seeker / Student</option>
          <option value="employer">Employer</option>
        </select>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-500 py-2 rounded font-medium">
          {loading ? "Creating account..." : "Create Account"}
        </button>
        <p className="text-sm text-slate-400">
          Already have an account? <Link to="/login" className="text-indigo-400">Log in</Link>
        </p>
      </form>
    </main>
  );
}
