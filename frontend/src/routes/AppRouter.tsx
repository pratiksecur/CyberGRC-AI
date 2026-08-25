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
import Register from "@/pages/auth/Register";

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

import CreateAudit from "@/pages/audits/CreateAudit";
import ViewAudit from "@/pages/audits/ViewAudit";
import EditAudit from "@/pages/audits/EditAudit";

import AuditFindings from "@/pages/audit-findings/AuditFindings";

import CreateAuditFinding from "@/pages/audit-findings/CreateAuditFinding";
import ViewAuditFinding from "@/pages/audit-findings/ViewAuditFinding";
import EditAuditFinding from "@/pages/audit-findings/EditAuditFinding";

import CorrectiveActions from "@/pages/corrective-actions/CorrectiveActions";
import CreateCorrectiveAction from "@/pages/corrective-actions/CreateCorrectiveAction";
import ViewCorrectiveAction from "@/pages/corrective-actions/ViewCorrectiveAction";
import EditCorrectiveAction from "@/pages/corrective-actions/EditCorrectiveAction";

import Reports from "@/pages/reports/Reports";
import RiskReport from "@/pages/reports/RiskReport";
import AuditReport from "@/pages/reports/AuditReport";
import ComplianceReport from "@/pages/reports/ComplianceReport";
import CorrectiveActionsReport from "@/pages/reports/CorrectiveActionsReport";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public Route */}

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
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
          path="/audits/new"
          element={
            <ProtectedRoute>
              <CreateAudit />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audits/:id"
          element={
            <ProtectedRoute>
              <ViewAudit />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audits/:id/edit"
          element={
            <ProtectedRoute>
              <EditAudit />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audit-findings"
          element={
            <ProtectedRoute>
              <AuditFindings />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audit-findings/new"
          element={
            <ProtectedRoute>
              <CreateAuditFinding />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audit-findings/:id"
          element={
            <ProtectedRoute>
              <ViewAuditFinding />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audit-findings/:id/edit"
          element={
            <ProtectedRoute>
              <EditAuditFinding />
            </ProtectedRoute>
          }
        />

        <Route
          path="/corrective-actions"
          element={
            <ProtectedRoute>
              <CorrectiveActions />
            </ProtectedRoute>
          }
        />

        <Route
          path="/corrective-actions/new"
          element={
            <ProtectedRoute>
              <CreateCorrectiveAction />
            </ProtectedRoute>
          }
        />

        <Route
          path="/corrective-actions/:id"
          element={
            <ProtectedRoute>
              <ViewCorrectiveAction />
            </ProtectedRoute>
          }
        />

        <Route
          path="/corrective-actions/:id/edit"
          element={
            <ProtectedRoute>
              <EditCorrectiveAction />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <Reports />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/risks"
          element={
            <ProtectedRoute>
              <RiskReport />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/audits"
          element={
            <ProtectedRoute>
              <AuditReport />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/compliance"
          element={
            <ProtectedRoute>
              <ComplianceReport />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/corrective-actions"
          element={
            <ProtectedRoute>
              <CorrectiveActionsReport />
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