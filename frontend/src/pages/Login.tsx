import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const ok = await login(email, password);
    if (ok) navigate("/dashboard");
  }

  return (
    <main className="min-h-screen bg-slate-900 text-white flex items-center justify-center px-6">
      <form onSubmit={handleSubmit} className="bg-slate-800 p-8 rounded-xl w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-semibold">Log in</h1>
        <input
          type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 rounded bg-slate-700 outline-none" required
        />
        <input
          type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 rounded bg-slate-700 outline-none" required
        />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-500 py-2 rounded font-medium">
          {loading ? "Logging in..." : "Log In"}
        </button>
        <p className="text-sm text-slate-400">
          No account? <Link to="/register" className="text-indigo-400">Register</Link>
        </p>
      </form>
    </main>
  );
}
