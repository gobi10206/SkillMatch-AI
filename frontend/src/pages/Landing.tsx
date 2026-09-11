import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <main className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center px-6 text-center">
      <h1 className="text-4xl font-bold mb-3">SkillMatch AI</h1>
      <p className="text-slate-400 max-w-xl mb-8">
        Discover the skills you already have, close the gaps to your target career,
        and get matched with learning paths and opportunities — built for SDG 4, 8 &amp; 10.
      </p>
      <div className="flex gap-4">
        <Link to="/register" className="bg-indigo-600 hover:bg-indigo-500 px-6 py-2 rounded-lg font-medium">
          Get Started
        </Link>
        <Link to="/login" className="border border-slate-600 hover:border-slate-400 px-6 py-2 rounded-lg font-medium">
          Log In
        </Link>
      </div>
    </main>
  );
}
