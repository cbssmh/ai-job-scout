type NavItem = {
  label: string;
  active?: boolean;
};

const navItems: NavItem[] = [
  { label: "Dashboard", active: true },
  { label: "Jobs" },
  { label: "Analytics" },
  { label: "Network" },
  { label: "Settings" },
];

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex lg:w-[240px] lg:flex-col lg:justify-between lg:rounded-2xl lg:border lg:border-white/5 lg:bg-[#111111] lg:p-5 lg:sticky lg:top-6 lg:h-[calc(100vh-48px)]">
      <div>
        <div className="mb-8">
          <p className="text-white text-lg font-bold">Precision Intelligence</p>
          <p className="text-xs text-zinc-500 mt-1">Stealth Curator</p>
        </div>

        <nav className="space-y-2">
          {navItems.map((item) => (
            <button
              key={item.label}
              className={`w-full text-left rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
                item.active
                  ? "bg-[#1b1b1b] text-white border border-white/5"
                  : "text-zinc-400 hover:bg-[#171717] hover:text-white"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <button className="mt-8 w-full rounded-xl bg-cyan-400 px-4 py-3 text-sm font-semibold text-black hover:brightness-110 transition">
          + New Search
        </button>
      </div>

      <div className="space-y-3">
        <button className="w-full text-left rounded-xl px-4 py-3 text-sm text-zinc-400 hover:bg-[#171717] hover:text-white transition-colors">
          Help
        </button>
        <button className="w-full text-left rounded-xl px-4 py-3 text-sm text-zinc-400 hover:bg-[#171717] hover:text-white transition-colors">
          Logout
        </button>

        <div className="border-t border-white/5 pt-4">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-full bg-[#f5d0a9] text-black flex items-center justify-center text-sm font-bold">
              A
            </div>
            <div>
              <p className="text-sm font-medium text-white">Alex Chen</p>
              <p className="text-xs text-zinc-500">Premium Curator</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}