import { Bot, ShieldCheck } from 'lucide-react';

export function Header() {
  return (
    <header className="hero">
      <div className="hero__content">
        <div className="hero__eyebrow">
          <ShieldCheck size={18} /> Secure internal analytics workspace
        </div>
        <h1>InsightForge - Secure AI Insights Assistant</h1>
        <p>
          Ask leadership questions across SQL, CSV, and PDF sources while keeping data access behind approved backend tools.
        </p>
      </div>
    </header>
  );
}