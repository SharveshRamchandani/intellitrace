import { ReactNode, useState } from "react";
import { AppSidebar } from "./AppSidebar";
import { Bell } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const notifications = [
  "High Risk Invoice Detected – Supplier T1-Alpha",
  "Cascade chain identified: T3-Delta → T2-Beta → T1-Alpha",
  "Revenue mismatch alert for T1-Zeta Corp",
];

export function AppLayout({ children }: { children: ReactNode }) {
  const [showNotifs, setShowNotifs] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <AppSidebar />
      <div className="ml-[240px] transition-all duration-200">
        {/* Top Bar */}
        <header className="h-16 border-b border-border flex items-center justify-end px-6 sticky top-0 bg-background/80 backdrop-blur-md z-40">
          <div className="relative">
            <button
              onClick={() => setShowNotifs(!showNotifs)}
              className="relative p-2 rounded-xl hover:bg-secondary transition-colors"
            >
              <Bell className="h-5 w-5 text-muted-foreground" />
              <span className="absolute top-1 right-1 h-2.5 w-2.5 rounded-full bg-risk-high animate-pulse-subtle" />
            </button>
            <AnimatePresence>
              {showNotifs && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="absolute right-0 top-12 w-80 bg-card border border-border rounded-2xl shadow-xl overflow-hidden"
                >
                  <div className="p-3 border-b border-border">
                    <span className="text-sm font-semibold text-foreground">Notifications</span>
                  </div>
                  {notifications.map((n, i) => (
                    <div key={i} className="p-3 border-b border-border last:border-0 hover:bg-secondary/50 transition-colors cursor-pointer">
                      <p className="text-sm text-foreground">{n}</p>
                      <p className="text-xs text-muted-foreground mt-1">Just now</p>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
