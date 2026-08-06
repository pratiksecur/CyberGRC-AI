import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "@/pages/dashboard/Dashboard";
import Risks from "@/pages/risks/Risks";
import Controls from "@/pages/controls/Controls";
import Frameworks from "@/pages/frameworks/Frameworks";
import Evidence from "@/pages/evidence/Evidence";
import Audits from "@/pages/audits/Audits";
import AI from "@/pages/ai/AI";
import Settings from "@/pages/settings/Settings";
import Login from "@/pages/auth/Login";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Temporary during UI development */}
        <Route path="/" element={<Dashboard />} />

        <Route path="/login" element={<Login />} />

        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/risks" element={<Risks />} />
        <Route path="/controls" element={<Controls />} />
        <Route path="/frameworks" element={<Frameworks />} />
        <Route path="/evidence" element={<Evidence />} />
        <Route path="/audits" element={<Audits />} />
        <Route path="/ai" element={<AI />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </BrowserRouter>
  );
}