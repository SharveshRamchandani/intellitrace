import { motion } from "framer-motion";
import { Settings as SettingsIcon } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Platform configuration</p>
      </div>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-12 flex flex-col items-center justify-center">
        <SettingsIcon className="h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground text-sm">Settings panel coming soon</p>
      </motion.div>
    </div>
  );
}
