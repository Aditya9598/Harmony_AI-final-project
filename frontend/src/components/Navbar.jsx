import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Home" },
  { to: "/skin-detection", label: "Skin Detection" },
  { to: "/wellness-chatbot", label: "Wellness Chatbot" },
];

export default function Navbar() {
  const appName = import.meta.env.VITE_APP_NAME || "Harmony AI";

  return (
    <header className="mx-auto mt-6 w-[95%] max-w-6xl glass-card">
      <div className="flex flex-wrap items-center justify-between px-6 py-4">
        <h1 className="text-xl font-semibold text-white">{appName} - Virtual Intelligence</h1>
        <nav className="flex gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-xl px-4 py-2 text-sm transition ${
                  isActive ? "bg-white/20 text-white" : "text-slate-200 hover:bg-white/10"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
