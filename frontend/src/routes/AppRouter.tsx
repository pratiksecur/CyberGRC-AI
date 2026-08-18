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

import CreateControl from "@/pages/controls/CreateControl";
import ViewControl from "@/pages/controls/ViewControl";
import EditControl from "@/pages/controls/EditControl";

import CreateFramework from "@/pages/frameworks/CreateFramework";
import ViewFramework from "@/pages/frameworks/ViewFramework";
import EditFramework from "@/pages/frameworks/EditFramework";

import CreateEvidence from "@/pages/evidence/CreateEvidence";
import ViewEvidence from "@/pages/evidence/ViewEvidence";
import EditEvidence from "@/pages/evidence/EditEvidence";

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
          path="/controls/new"
          element={
            <ProtectedRoute>
              <CreateControl />
            </ProtectedRoute>
          }
        />

        <Route
          path="/controls/:id"
          element={
            <ProtectedRoute>
              <ViewControl />
            </ProtectedRoute>
          }
        />

        <Route
          path="/controls/:id/edit"
          element={
            <ProtectedRoute>
              <EditControl />
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
          path="/frameworks/new"
          element={
            <ProtectedRoute>
              <CreateFramework />
            </ProtectedRoute>
          }
        />

        <Route
          path="/frameworks/:id"
          element={
            <ProtectedRoute>
              <ViewFramework />
            </ProtectedRoute>
          }
        />

        <Route
          path="/frameworks/:id/edit"
          element={
            <ProtectedRoute>
              <EditFramework />
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
          path="/evidence/new"
          element={
            <ProtectedRoute>
              <CreateEvidence />
            </ProtectedRoute>
          }
        />

        <Route
          path="/evidence/:id"
          element={
            <ProtectedRoute>
              <ViewEvidence />
            </ProtectedRoute>
          }
        />

        <Route
          path="/evidence/:id/edit"
          element={
            <ProtectedRoute>
              <EditEvidence />
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