import { lazy, Suspense } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from "@/pages/auth/Login";

import ProtectedRoute from "./ProtectedRoute";

// Pages are loaded on demand, so the first visit downloads only the code it
// needs instead of the whole application.
const Dashboard = lazy(() => import("@/pages/dashboard/Dashboard"));
const Risks = lazy(() => import("@/pages/risks/Risks"));
const CreateRisk = lazy(() => import("@/pages/risks/CreateRisk"));
const ViewRisk = lazy(() => import("@/pages/risks/ViewRisk"));
const EditRisk = lazy(() => import("@/pages/risks/EditRisk"));
const Controls = lazy(() => import("@/pages/controls/Controls"));
const CreateControl = lazy(() => import("@/pages/controls/CreateControl"));
const ViewControl = lazy(() => import("@/pages/controls/ViewControl"));
const EditControl = lazy(() => import("@/pages/controls/EditControl"));
const Frameworks = lazy(() => import("@/pages/frameworks/Frameworks"));
const CreateFramework = lazy(() => import("@/pages/frameworks/CreateFramework"));
const ViewFramework = lazy(() => import("@/pages/frameworks/ViewFramework"));
const EditFramework = lazy(() => import("@/pages/frameworks/EditFramework"));
const FrameworkCrosswalk = lazy(() => import("@/pages/frameworks/FrameworkCrosswalk"));
const FrameworkControls = lazy(() => import("@/pages/framework-controls/FrameworkControls"));
const CreateFrameworkControl = lazy(() => import("@/pages/framework-controls/CreateFrameworkControl"));
const ViewFrameworkControl = lazy(() => import("@/pages/framework-controls/ViewFrameworkControl"));
const EditFrameworkControl = lazy(() => import("@/pages/framework-controls/EditFrameworkControl"));
const Evidence = lazy(() => import("@/pages/evidence/Evidence"));
const CreateEvidence = lazy(() => import("@/pages/evidence/CreateEvidence"));
const ViewEvidence = lazy(() => import("@/pages/evidence/ViewEvidence"));
const EditEvidence = lazy(() => import("@/pages/evidence/EditEvidence"));
const Audits = lazy(() => import("@/pages/audits/Audits"));
const CreateAudit = lazy(() => import("@/pages/audits/CreateAudit"));
const ViewAudit = lazy(() => import("@/pages/audits/ViewAudit"));
const EditAudit = lazy(() => import("@/pages/audits/EditAudit"));
const AuditFindings = lazy(() => import("@/pages/audit-findings/AuditFindings"));
const CreateAuditFinding = lazy(() => import("@/pages/audit-findings/CreateAuditFinding"));
const ViewAuditFinding = lazy(() => import("@/pages/audit-findings/ViewAuditFinding"));
const EditAuditFinding = lazy(() => import("@/pages/audit-findings/EditAuditFinding"));
const CorrectiveActions = lazy(() => import("@/pages/corrective-actions/CorrectiveActions"));
const CreateCorrectiveAction = lazy(() => import("@/pages/corrective-actions/CreateCorrectiveAction"));
const ViewCorrectiveAction = lazy(() => import("@/pages/corrective-actions/ViewCorrectiveAction"));
const EditCorrectiveAction = lazy(() => import("@/pages/corrective-actions/EditCorrectiveAction"));
const GRCIntelligence = lazy(() => import("@/pages/intelligence/GRCIntelligence"));
const Monitoring = lazy(() => import("@/pages/monitoring/Monitoring"));
const Reports = lazy(() => import("@/pages/reports/Reports"));
const RiskReport = lazy(() => import("@/pages/reports/RiskReport"));
const AuditReport = lazy(() => import("@/pages/reports/AuditReport"));
const ComplianceReport = lazy(() => import("@/pages/reports/ComplianceReport"));
const CorrectiveActionsReport = lazy(() => import("@/pages/reports/CorrectiveActionsReport"));
const CreateRiskTreatment = lazy(() => import("@/pages/risk-treatments/CreateRiskTreatment"));
const ViewRiskTreatment = lazy(() => import("@/pages/risk-treatments/ViewRiskTreatment"));
const EditRiskTreatment = lazy(() => import("@/pages/risk-treatments/EditRiskTreatment"));
const KnowledgeGraph = lazy(() => import("@/pages/intelligence/KnowledgeGraph"));
const AI = lazy(() => import("@/pages/ai/AI"));
const AIGRCAnalyst = lazy(() => import("@/pages/ai/AIGRCAnalyst"));
const Settings = lazy(() => import("@/pages/settings/Settings"));
const Register = lazy(() => import("@/pages/auth/Register"));
const Users = lazy(() => import("@/pages/users/Users"));
const AuditLog = lazy(() => import("@/pages/audit-log/AuditLog"));

function PageLoading() {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex min-h-screen items-center justify-center text-sm text-gray-500"
    >
      Loading…
    </div>
  );
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoading />}>
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
          element={
            <ProtectedRoute
              resource="users"
              action="create"
            >
              <Register />
            </ProtectedRoute>
          }
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
        {/* RISK TREATMENTS */}
        {/* ================================================== */}

        <Route
          path="/risk-treatments/new"
          element={
            <ProtectedRoute
              resource="risk_treatments"
              action="create"
            >
              <CreateRiskTreatment />
            </ProtectedRoute>
          }
        />

        <Route
          path="/risk-treatments/:id"
          element={
            <ProtectedRoute
              resource="risk_treatments"
              action="view"
            >
              <ViewRiskTreatment />
            </ProtectedRoute>
          }
        />

        <Route
          path="/risk-treatments/:id/edit"
          element={
            <ProtectedRoute
              resource="risk_treatments"
              action="update"
            >
              <EditRiskTreatment />
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
          path="/frameworks/crosswalk"
          element={
            <ProtectedRoute
              resource="control_framework_mappings"
              action="view"
            >
              <FrameworkCrosswalk />
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
        {/* GRC INTELLIGENCE */}
        {/* ================================================== */}

        <Route
          path="/intelligence"
          element={
            <ProtectedRoute
              resource="risks"
              action="view"
            >
              <GRCIntelligence />
            </ProtectedRoute>
          }
        />

        <Route
          path="/knowledge-graph"
          element={
            <ProtectedRoute
              resource="risks"
              action="view"
            >
              <KnowledgeGraph />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* CONTINUOUS MONITORING */}
        {/* ================================================== */}

        <Route
          path="/monitoring"
          element={
            <ProtectedRoute
              resource="risks"
              action="view"
            >
              <Monitoring />
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

        {/* AI GRC ANALYST */}
        <Route
          path="/ai/grc-analyst"
          element={
            <ProtectedRoute
              resource="ai"
              action="view"
            >
              <AIGRCAnalyst />
            </ProtectedRoute>
          }
        />
        
        {/* ================================================== */}
        {/* USERS */}
        {/* ================================================== */}

        <Route
          path="/users"
          element={
            <ProtectedRoute
              resource="users"
              action="create"
            >
              <Users />
            </ProtectedRoute>
          }
        />

        {/* ================================================== */}
        {/* AUDIT TRAIL */}
        {/* ================================================== */}

        <Route
          path="/audit-log"
          element={
            <ProtectedRoute>
              <AuditLog />
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
      </Suspense>
    </BrowserRouter>
  );
}