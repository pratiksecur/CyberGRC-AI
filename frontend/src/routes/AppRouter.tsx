import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Dashboard from "@/pages/dashboard/Dashboard";

import Risks from "@/pages/risks/Risks";
import CreateRisk from "@/pages/risks/CreateRisk";
import ViewRisk from "@/pages/risks/ViewRisk";
import EditRisk from "@/pages/risks/EditRisk";

import Controls from "@/pages/controls/Controls";
import CreateControl from "@/pages/controls/CreateControl";
import ViewControl from "@/pages/controls/ViewControl";
import EditControl from "@/pages/controls/EditControl";

import Frameworks from "@/pages/frameworks/Frameworks";
import CreateFramework from "@/pages/frameworks/CreateFramework";
import ViewFramework from "@/pages/frameworks/ViewFramework";
import EditFramework from "@/pages/frameworks/EditFramework";

import FrameworkControls from "@/pages/framework-controls/FrameworkControls";
import CreateFrameworkControl from "@/pages/framework-controls/CreateFrameworkControl";
import ViewFrameworkControl from "@/pages/framework-controls/ViewFrameworkControl";
import EditFrameworkControl from "@/pages/framework-controls/EditFrameworkControl";

import Evidence from "@/pages/evidence/Evidence";
import CreateEvidence from "@/pages/evidence/CreateEvidence";
import ViewEvidence from "@/pages/evidence/ViewEvidence";
import EditEvidence from "@/pages/evidence/EditEvidence";

import Audits from "@/pages/audits/Audits";
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

import AI from "@/pages/ai/AI";
import Settings from "@/pages/settings/Settings";

import Login from "@/pages/auth/Login";
import Register from "@/pages/auth/Register";

import ProtectedRoute from "./ProtectedRoute";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ================================================== */}
        {/* PUBLIC ROUTES */}
        {/* ================================================== */}

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        {/* ================================================== */}
        {/* ROOT */}
        {/* ================================================== */}

        <Route
          path="/"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

        {/* ================================================== */}
        {/* DASHBOARD */}
        {/* ================================================== */}

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* RISKS */}
        {/* ================================================== */}

        <Route
          path="/risks"
          element={
            <ProtectedRoute
              resource="risks"
              action="view"
            >
              <Risks />
            </ProtectedRoute>
          }
        />

        <Route
          path="/risks/new"
          element={
            <ProtectedRoute
              resource="risks"
              action="create"
            >
              <CreateRisk />
            </ProtectedRoute>
          }
        />

        <Route
          path="/risks/:id"
          element={
            <ProtectedRoute
              resource="risks"
              action="view"
            >
              <ViewRisk />
            </ProtectedRoute>
          }
        />

        <Route
          path="/risks/:id/edit"
          element={
            <ProtectedRoute
              resource="risks"
              action="update"
            >
              <EditRisk />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* CONTROLS */}
        {/* ================================================== */}

        <Route
          path="/controls"
          element={
            <ProtectedRoute
              resource="controls"
              action="view"
            >
              <Controls />
            </ProtectedRoute>
          }
        />

        <Route
          path="/controls/new"
          element={
            <ProtectedRoute
              resource="controls"
              action="create"
            >
              <CreateControl />
            </ProtectedRoute>
          }
        />

        <Route
          path="/controls/:id"
          element={
            <ProtectedRoute
              resource="controls"
              action="view"
            >
              <ViewControl />
            </ProtectedRoute>
          }
        />

        <Route
          path="/controls/:id/edit"
          element={
            <ProtectedRoute
              resource="controls"
              action="update"
            >
              <EditControl />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* FRAMEWORKS */}
        {/* ================================================== */}

        <Route
          path="/frameworks"
          element={
            <ProtectedRoute
              resource="frameworks"
              action="view"
            >
              <Frameworks />
            </ProtectedRoute>
          }
        />

        <Route
          path="/frameworks/new"
          element={
            <ProtectedRoute
              resource="frameworks"
              action="create"
            >
              <CreateFramework />
            </ProtectedRoute>
          }
        />

        <Route
          path="/frameworks/:id"
          element={
            <ProtectedRoute
              resource="frameworks"
              action="view"
            >
              <ViewFramework />
            </ProtectedRoute>
          }
        />

        <Route
          path="/frameworks/:id/edit"
          element={
            <ProtectedRoute
              resource="frameworks"
              action="update"
            >
              <EditFramework />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* FRAMEWORK CONTROLS */}
        {/* ================================================== */}

        <Route
          path="/framework-controls"
          element={
            <ProtectedRoute
              resource="framework_controls"
              action="view"
            >
              <FrameworkControls />
            </ProtectedRoute>
          }
        />

        <Route
          path="/framework-controls/new"
          element={
            <ProtectedRoute
              resource="framework_controls"
              action="create"
            >
              <CreateFrameworkControl />
            </ProtectedRoute>
          }
        />

        <Route
          path="/framework-controls/:id"
          element={
            <ProtectedRoute
              resource="framework_controls"
              action="view"
            >
              <ViewFrameworkControl />
            </ProtectedRoute>
          }
        />

        <Route
          path="/framework-controls/:id/edit"
          element={
            <ProtectedRoute
              resource="framework_controls"
              action="update"
            >
              <EditFrameworkControl />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* EVIDENCE */}
        {/* ================================================== */}

        <Route
          path="/evidence"
          element={
            <ProtectedRoute
              resource="evidence"
              action="view"
            >
              <Evidence />
            </ProtectedRoute>
          }
        />

        <Route
          path="/evidence/new"
          element={
            <ProtectedRoute
              resource="evidence"
              action="create"
            >
              <CreateEvidence />
            </ProtectedRoute>
          }
        />

        <Route
          path="/evidence/:id"
          element={
            <ProtectedRoute
              resource="evidence"
              action="view"
            >
              <ViewEvidence />
            </ProtectedRoute>
          }
        />

        <Route
          path="/evidence/:id/edit"
          element={
            <ProtectedRoute
              resource="evidence"
              action="update"
            >
              <EditEvidence />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* AUDITS */}
        {/* ================================================== */}

        <Route
          path="/audits"
          element={
            <ProtectedRoute
              resource="audits"
              action="view"
            >
              <Audits />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audits/new"
          element={
            <ProtectedRoute
              resource="audits"
              action="create"
            >
              <CreateAudit />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audits/:id"
          element={
            <ProtectedRoute
              resource="audits"
              action="view"
            >
              <ViewAudit />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audits/:id/edit"
          element={
            <ProtectedRoute
              resource="audits"
              action="update"
            >
              <EditAudit />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* AUDIT FINDINGS */}
        {/* ================================================== */}

        <Route
          path="/audit-findings"
          element={
            <ProtectedRoute
              resource="audit_findings"
              action="view"
            >
              <AuditFindings />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audit-findings/new"
          element={
            <ProtectedRoute
              resource="audit_findings"
              action="create"
            >
              <CreateAuditFinding />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audit-findings/:id"
          element={
            <ProtectedRoute
              resource="audit_findings"
              action="view"
            >
              <ViewAuditFinding />
            </ProtectedRoute>
          }
        />

        <Route
          path="/audit-findings/:id/edit"
          element={
            <ProtectedRoute
              resource="audit_findings"
              action="update"
            >
              <EditAuditFinding />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* CORRECTIVE ACTIONS */}
        {/* ================================================== */}

        <Route
          path="/corrective-actions"
          element={
            <ProtectedRoute
              resource="corrective_actions"
              action="view"
            >
              <CorrectiveActions />
            </ProtectedRoute>
          }
        />

        <Route
          path="/corrective-actions/new"
          element={
            <ProtectedRoute
              resource="corrective_actions"
              action="create"
            >
              <CreateCorrectiveAction />
            </ProtectedRoute>
          }
        />

        <Route
          path="/corrective-actions/:id"
          element={
            <ProtectedRoute
              resource="corrective_actions"
              action="view"
            >
              <ViewCorrectiveAction />
            </ProtectedRoute>
          }
        />

        <Route
          path="/corrective-actions/:id/edit"
          element={
            <ProtectedRoute
              resource="corrective_actions"
              action="update"
            >
              <EditCorrectiveAction />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* REPORTS */}
        {/* ================================================== */}

        <Route
          path="/reports"
          element={
            <ProtectedRoute
              resource="reports"
              action="view"
            >
              <Reports />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/risks"
          element={
            <ProtectedRoute
              resource="reports"
              action="view"
            >
              <RiskReport />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/audits"
          element={
            <ProtectedRoute
              resource="reports"
              action="view"
            >
              <AuditReport />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/compliance"
          element={
            <ProtectedRoute
              resource="reports"
              action="view"
            >
              <ComplianceReport />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports/corrective-actions"
          element={
            <ProtectedRoute
              resource="reports"
              action="view"
            >
              <CorrectiveActionsReport />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* AI */}
        {/* ================================================== */}

        <Route
          path="/ai"
          element={
            <ProtectedRoute
              resource="ai"
              action="view"
            >
              <AI />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* SETTINGS */}
        {/* ================================================== */}

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