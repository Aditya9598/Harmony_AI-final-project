import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <section className="space-y-6">
      <div className="glass-card p-8">
        <p className="text-harmony-200 text-sm uppercase tracking-widest">Healthcare + AI Platform</p>
        <h2 className="mt-3 text-4xl font-bold text-white">Harmony AI - Virtual Intelligence</h2>
        <p className="mt-4 max-w-2xl text-slate-200">
          A premium digital wellness experience with skin condition analysis, emotional support guidance,
          and a modern health dashboard.
        </p>
        <div className="mt-6 flex gap-3">
          <Link to="/skin-detection" className="rounded-xl bg-harmony-500 px-5 py-3 text-white hover:bg-harmony-400">
            Start Skin Detection
          </Link>
          <Link to="/wellness-chatbot" className="rounded-xl border border-white/30 px-5 py-3 text-white hover:bg-white/10">
            Open Wellness Chatbot
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <article className="glass-card p-5">
          <h3 className="text-lg font-semibold text-white">Skin Disease Detection</h3>
          <p className="mt-2 text-sm text-slate-300">
            Upload skin images to receive AI-assisted classification, confidence score, and guidance.
          </p>
        </article>
        <article className="glass-card p-5">
          <h3 className="text-lg font-semibold text-white">Mental Wellness Chatbot</h3>
          <p className="mt-2 text-sm text-slate-300">
            Structured emotional support responses for stress, anxiety, loneliness, and life balance.
          </p>
        </article>
        <article className="glass-card p-5">
          <h3 className="text-lg font-semibold text-white">Health Dashboard</h3>
          <p className="mt-2 text-sm text-slate-300">
            Responsive dashboard cards with calm, modern visual design for healthcare-grade UX.
          </p>
        </article>
      </div>
    </section>
  );
}
