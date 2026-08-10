import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Dashboard from "@/pages/dashboard/Dashboard";
import Risks from "@/pages/risks/Risks";
import CreateRisk from "@/pages/risks/CreateRisk";
import Controls from "@/pages/controls/Controls";
import Frameworks from "@/pages/frameworks/Frameworks";
import Evidence from "@/pages/evidence/Evidence";
import Audits from "@/pages/audits/Audits";
import AI from "@/pages/ai/AI";
import Settings from "@/pages/settings/Settings";
import Login from "@/pages/auth/Login";

import ProtectedRoute from "./ProtectedRoute";
import ViewRisk from "@/pages/risks/ViewRisk";
import EditRisk from "@/pages/risks/EditRisk";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public Route */}

        <Route
          path="/login"
          element={<Login />}
        />

        {/* Redirect Root */}

        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />

        {/* Protected Routes */}

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/risks"
          element={
            <ProtectedRoute>
              <Risks />
            </ProtectedRoute>
          }
        />

        <Route
          path="/risks/new"
          element={
            <ProtectedRoute>
              <CreateRisk />
            </ProtectedRoute>
          }
        />

        <Route
        path="/risks/:id"
        element={
            <ProtectedRoute>
              <ViewRisk />
            </ProtectedRoute>
        }
        />

        <Route
          path="/risks/:id/edit"
          element={
            <ProtectedRoute>
              <EditRisk />
            </ProtectedRoute>
          }
        />

        <Route
          path="/controls"
          element={
            <ProtectedRoute>
              <Controls />
            </ProtectedRoute>
          }
        />

        <Route
          path="/frameworks"
          element={
            <ProtectedRoute>
              <Frameworks />
            </ProtectedRoute>
          }
        />

        <Route
          path="/evidence"
          element={
            <ProtectedRoute>
              <Evidence />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audits"
          element={
            <ProtectedRoute>
              <Audits />
            </ProtectedRoute>
          }
        />

        <Route
          path="/ai"
          element={
            <ProtectedRoute>
              <AI />
            </ProtectedRoute>
          }
        />

        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}