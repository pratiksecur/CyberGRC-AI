# 🛡️ CyberGRC-AI

### AI-Driven Governance, Risk & Compliance Platform

CyberGRC-AI is an AI-assisted Governance, Risk & Compliance (GRC) platform designed to connect **risk, controls, evidence, audits, findings, corrective actions, risk treatments and continuous monitoring** into a unified security and compliance lifecycle.

The project is being developed with a strong focus on **security engineering, fine-grained authorization, organizational visibility, risk intelligence and AI-assisted decision support**.

The long-term goal is to move beyond static GRC records toward **continuous risk understanding**.

---

## 🚀 Project Overview

Traditional GRC platforms often store risks, controls, evidence, audits and compliance information as separate records.

CyberGRC-AI is designed around the idea that these elements should be connected.

A risk should not exist in isolation.

It should be possible to understand:

> What risks exist?

> What controls address them?

> What evidence supports those controls?

> What findings or remediation activities are associated with the risk?

> How has the risk been treated?

> What is the resulting residual risk?

> Has anything changed that should cause the risk to be reassessed?

CyberGRC-AI brings these relationships together and uses deterministic GRC logic alongside AI-assisted analysis.

---

# 🎯 Problem Statement

Organisational security and compliance information is often distributed across different systems and processes.

Security teams may work with:

- Security events
- Vulnerabilities
- Logs
- Incident data
- Security controls

While GRC teams may work with:

- Risks
- Policies
- Controls
- Evidence
- Audits
- Findings
- Corrective actions
- Compliance frameworks

This creates a gap between:

**what is happening operationally**

and

**what it means from a risk, governance and compliance perspective.**

CyberGRC-AI explores how these domains can be connected through a unified GRC intelligence layer.

---

# 🧠 Core Capabilities

## 1. Risk Management

CyberGRC-AI provides structured risk management capabilities including:

- Risk identification
- Risk scoring
- Likelihood and impact assessment
- Risk ownership
- Risk status
- Risk-control relationships
- Risk intelligence
- Residual risk analysis
- Risk monitoring

---

## 2. Risk Treatment & Residual Risk

Risks can move through a structured treatment lifecycle:

```text
Risk
 ↓
Treatment
 ↓
Approval
 ↓
Residual Risk
 ↓
Monitoring
```

Supported treatment concepts include:

- Mitigate
- Accept
- Transfer
- Avoid
- Treatment plans
- Treatment ownership
- Target dates
- Approval workflows
- Acceptance reasoning
- Residual likelihood
- Residual impact
- Residual risk

Treatment decisions are incorporated into risk intelligence, monitoring and reporting.

The platform also uses deterministic treatment-authority logic to determine which treatment represents the current authoritative residual-risk state.

---

# 🔐 RBAC & Authorization

Security is treated as a core architectural requirement.

CyberGRC-AI implements fine-grained authorization rather than relying only on authentication.

The authorization model includes:

- Role-Based Access Control (RBAC)
- Permission-based authorization
- Object-level authorization
- Ownership checks
- Organizational visibility
- Hierarchical access
- Least-privilege principles
- AI authorization
- Resource-specific access validation

### Roles

| Role | Purpose |
|---|---|
| Admin | Full organizational administration |
| GRC Manager | GRC management and executive intelligence |
| Risk Analyst | Risk and control management |
| Auditor | Audit and compliance visibility |
| Employee | Limited own-resource access |

### Organizational Visibility

Access can be scoped according to:

```text
OWN
SUBORDINATES
ORGANIZATION
```

Being authenticated does not automatically mean a user can access every resource.

Authorization is evaluated according to the user's role, permissions, organizational relationship and the specific resource being accessed.

---

# 🛡️ Security Engineering

CyberGRC-AI has been developed with security controls throughout the application architecture.

Security considerations include:

- Least privilege
- Object-level authorization
- IDOR/BOLA prevention
- Organizational access boundaries
- Authentication with httpOnly cookies and CSRF protection
- Account lockout and a password policy
- Audit trail of every change
- Input validation
- Secure resource visibility
- AI authorization
- Auditability
- Error handling
- Security headers
- Content Security Policy
- Request size limits
- Request correlation IDs
- Controlled CORS
- Secure defaults

The API follows explicit authorization semantics:

```text
401 → Authentication failure

403 → Authenticated but not authorized

404 → Resource is outside the user's visibility scope
```

### Account security

- **Sign-in:** the access token lives in an httpOnly cookie, and state-changing requests carry an HMAC CSRF token. Tokens carry a version number, so logging out, changing a password, resetting one or deactivating a user ends every session of that user.
- **Lockout:** 5 failed sign-ins for one email within 15 minutes (or 20 from one IP address) return `429` with a `Retry-After` header. Unknown emails are counted too, so the response does not reveal which accounts exist. Limits are set with `LOGIN_MAX_FAILED_ATTEMPTS`, `LOGIN_MAX_FAILED_PER_IP` and `LOGIN_LOCKOUT_MINUTES`.
- **Passwords:** at least 10 characters, at most 72 bytes (the bcrypt limit), not on a list of common passwords, and not the user's name or email name.
- **Emails** are case-insensitive: `Ana@x.com` and `ana@x.com` are the same account.
- **Users:** there is no self-registration. Administrators create, edit, deactivate and reset users in the **Users** page. The first administrator is created from the command line (see Getting Started).

### Audit trail

Every create, update and delete on the main records (users, risks, controls, evidence, audits, findings, corrective actions, risk treatments, frameworks and more) is written to an `audit_logs` table in the same database transaction as the change, so a change cannot be saved without its log entry. Each entry records who, when, what and the old and new values. Passwords are logged as `[changed]`, never as values. Administrators and Auditors can read the trail in the **Audit Trail** page (read-only, filterable, limited to their own organization).

Limits to be aware of: the trail starts when the feature is deployed (nothing is backfilled), bulk SQL updates that bypass the application are not logged, and someone with direct database access could edit the table, so it is not tamper-proof on its own.

### Uploads

Evidence files are checked three ways: the extension must be on the allow list, the declared content type must be allowed, and the first bytes of the file must match the extension (a `.pdf` must start like a PDF; a `.txt` must not contain binary data). Files are stored under server-generated names, size-limited, and only served through an authorized endpoint.

---

# 🧠 GRC Intelligence

CyberGRC-AI connects multiple GRC domains into a unified intelligence layer.

The platform currently connects:

```text
Risks
Controls
Evidence
Audits
Findings
Corrective Actions
Risk Treatments
```

This allows the system to derive relationships such as:

```text
Risk
 ├── Controls
 │    └── Evidence
 │
 ├── Findings
 │    └── Corrective Actions
 │
 └── Risk Treatment
      └── Residual Risk
```

The objective is to provide contextual risk intelligence rather than isolated database records.

---

# 🤖 AI-Assisted GRC

AI is used as an **analysis and decision-support layer**.

The project uses local LLM infrastructure through **Ollama**.

AI-assisted capabilities include:

- Risk analysis
- Control recommendations
- GRC intelligence
- Executive summaries
- Security/compliance analysis
- Risk explanations
- Decision support

AI does not replace deterministic authorization or governance rules.

The architecture intentionally separates:

```text
Deterministic Security & Governance
                +
        AI Decision Support
```

Authorization, visibility and governance boundaries remain enforced by application logic.

---

# 📊 Continuous Monitoring

CyberGRC-AI includes continuous monitoring capabilities designed to connect GRC state with operational changes.

Monitoring can surface events related to:

- Critical risks
- Risk changes
- Audit findings
- Open findings
- Corrective actions
- Critical remediation
- Risk treatment state
- Residual risk

The broader goal is to move from:

```text
Periodic GRC Assessment
```

toward:

```text
Continuous Risk Understanding
```

---

# 📋 Audits, Findings & Corrective Actions

The platform supports the lifecycle from audit observations to remediation.

```text
Audit
 ↓
Finding
 ↓
Corrective Action
 ↓
Remediation
 ↓
Risk State
```

This provides traceability between compliance activities and the risks they affect.

---

# 📚 Compliance & Framework Support

CyberGRC-AI is designed to work across multiple cybersecurity and regulatory frameworks.

The platform currently targets integration with frameworks and regulations including:

- ISO/IEC 27001
- NIST CSF
- GDPR
- NIS2
- DORA

Frameworks can be connected to controls and risks to support compliance mapping and analysis.

### Cross-framework crosswalk

The built-in catalogs are tagged with security themes (access control, logging and monitoring, backup, supplier risk and so on). From those tags the platform suggests, for a person to review:

- requirements in other frameworks related to the one you are looking at;
- further requirements a control may support, based on what it is already mapped to;
- unmapped requirements that controls you already have may cover (**Frameworks → Crosswalk**).

Nothing is mapped automatically. Each suggestion is applied by a person through the normal mapping action, with the usual permissions and audit trail. The crosswalk is an original working aid written for this platform, not an official mapping, and a shared theme does not mean two requirements are equivalent. Frameworks you create or rename yourself are not part of it.

---

# 🏗️ Architecture

High-level architecture:

```text
                         ┌──────────────────────┐
                         │      React UI        │
                         │   TypeScript / Vite  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │      REST API        │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌──────────────┐      ┌──────────────┐      ┌─────────────┐
       │    RBAC      │      │     GRC      │      │     AI      │
       │ Authorization│      │ Intelligence │      │   Ollama    │
       └──────────────┘      └──────────────┘      └─────────────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │     PostgreSQL       │
                         │      Database        │
                         └──────────────────────┘
```

---

# 🛠️ Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- JWT in httpOnly cookies, with CSRF protection
- Passlib / bcrypt
- Uvicorn

## Frontend

- React 19 and TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- Recharts
- Nginx (serves the built app in Docker)

## AI

- Ollama
- Local LLM integration

## Infrastructure

- Docker
- Docker Compose
- PostgreSQL 17
- Nginx
- Persistent Docker volumes

## Monitoring

The backend can expose its metrics in Prometheus text format at `/metrics`. It is off by default; enable it with `METRICS_ENABLED=true` and protect it with `METRICS_AUTH_TOKEN` (sent as the `X-Metrics-Token` header). Prometheus and Grafana are **not** included in this repository; point your own Prometheus at the endpoint if you want dashboards.

## Testing

- Pytest, with `pytest-xdist` for parallel runs
- FastAPI TestClient
- In-memory SQLite for most of the suite (fast)
- A separate suite in `tests/postgres/` that runs against real PostgreSQL: migrations, a check that the models match the migrated schema, and the Alembic single-head check
- GitHub Actions runs the backend tests, the frontend lint and build, and a dependency audit on every push

Production and operations documentation is available in `docs/`:

- `docs/PRODUCTION_DEPLOYMENT.md` — deployment guidance
- `docs/SECURITY_RUNBOOK.md` — security operations and response
- `docs/DISASTER_RECOVERY.md` — backup and recovery guidance

---

# 🐳 Docker Architecture

The project runs using Docker Compose.

Current services:

```text
┌─────────────────────────────┐
│           Docker            │
│                             │
│  ┌───────────┐              │
│  │ PostgreSQL│              │
│  │   :5432   │              │
│  └─────┬─────┘              │
│        │                    │
│  ┌─────▼─────┐              │
│  │  FastAPI  │              │
│  │   :8000   │              │
│  └─────┬─────┘              │
│        │                    │
│  ┌─────▼─────┐              │
│  │  React +  │              │
│  │   Nginx   │              │
│  │   :5173   │              │
│  └───────────┘              │
│                             │
└─────────────────────────────┘
```

PostgreSQL uses a persistent Docker volume.

---

# 🚀 Getting Started

## Prerequisites

- Docker Desktop (or Docker Engine with the Compose plugin)
- Git
- Optional, for the AI features: [Ollama](https://ollama.com) running on the same computer, with a model pulled (`ollama pull mistral`). Everything else works without it.

For running the tests or developing outside Docker you also need Python 3.12 or newer (the Docker image and CI use 3.12) and Node.js 22.

## 1. Clone and configure

```bash
git clone https://github.com/pratiksecur/CyberGRC-AI.git
cd CyberGRC-AI
```

Create your settings file from the example (`copy` on Windows Command Prompt, `cp` on Linux/macOS):

```bash
cp .env.example .env
```

Open `.env` and set at least `POSTGRES_PASSWORD` and `SECRET_KEY` to long random values. One way to make them:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

`.env` is ignored by git. Never commit it. To replace the secrets later, `python ops/rotate_env.py` writes a new `.env.new` with fresh values and leaves your current `.env` untouched.

## 2. Create the database

The database schema is applied by a one-off migration job, not when the backend starts:

```bash
docker compose --profile migrate build migrate
docker compose --profile migrate run --rm migrate
```

Run the same two commands again after pulling a version that adds migrations.

## 3. Start the application

```bash
docker compose up -d --build
docker compose ps
```

## 4. Create the first administrator

There is no self-registration, and a fresh database has no users. Create the first administrator from the command line; the password is asked for without being shown:

```bash
docker compose exec backend python -m app.seed.create_admin --email you@example.com --full-name "Your Name"
```

Passwords need at least 10 characters. After that, sign in and add everyone else from the **Users** page.

## 5. Load the framework catalogs (optional)

The repository includes control catalogs for NIST CSF, ISO 27001, GDPR, NIS2 and DORA. Preview first, then load:

```bash
docker compose exec backend python -m app.seed.frameworks --organization-id 1 --dry-run
docker compose exec backend python -m app.seed.frameworks --organization-id 1
```

It is safe to run again: existing frameworks are skipped, and nothing is edited or deleted.

## 6. Open the app

| What | Address |
|---|---|
| Web app | http://localhost:5173 |
| API | http://localhost:8000 |
| API documentation (Swagger) | http://localhost:8000/docs |

Use `localhost` exactly as written. Sign-in uses cookies, and the app is built to call the API at `http://localhost:8000` (`VITE_API_URL` in `.env`), so opening it through another address, such as a network IP, needs matching `VITE_API_URL`, `VITE_API_ORIGIN` and `CORS_ORIGINS` settings. The API documentation pages are turned off when `API_DOCS_ENABLED=false`, which is the recommended production setting.

For production settings (hosts, HTTPS, proxy, metrics), read `docs/PRODUCTION_DEPLOYMENT.md`.

---

# 🧪 Testing

The backend has roughly 2,000 automated tests (2,023 passing as of October 2026), covering authentication, RBAC, visibility boundaries, negative authorization cases, account lockout, the audit trail, uploads, pagination, GRC intelligence, risk treatment, continuous monitoring and production hardening.

Most tests run against an in-memory SQLite database, which is fast. The tests in `backend/tests/postgres/` run against a real PostgreSQL database and are **skipped unless `TEST_DATABASE_URL` is set**, so run them before a release.

## Backend

Start the throw-away test database (port 55432, data in memory, never touches your real database):

```bash
docker compose -f docker-compose.test.yml up -d
```

Install the test dependencies once, then run everything in parallel:

```bash
cd backend
pip install -r requirements-dev.txt
```

Point the PostgreSQL tests at the test database, then run:

```bash
# Windows Command Prompt
set TEST_DATABASE_URL=postgresql://cybergrc_test:cybergrc_test_only@127.0.0.1:55432/cybergrc_test

# PowerShell
$env:TEST_DATABASE_URL = "postgresql://cybergrc_test:cybergrc_test_only@127.0.0.1:55432/cybergrc_test"

# Linux / macOS
export TEST_DATABASE_URL=postgresql://cybergrc_test:cybergrc_test_only@127.0.0.1:55432/cybergrc_test

python -m pytest -q -n auto
```

A full run takes about a minute. Without `TEST_DATABASE_URL` the PostgreSQL tests are reported as skipped. Stop the test database with `docker compose -f docker-compose.test.yml down -v`.

## Frontend

```bash
cd frontend
npm ci
npm run lint
npm run build
```

The frontend has no automated tests yet; lint and the TypeScript build are the checks.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request:

- **Backend tests** — the full suite against a PostgreSQL service.
- **Frontend lint and build** — `npm ci`, `npm run lint`, `npm run build`.
- **Dependency audit** — `pip-audit` and `npm audit`. It reports known vulnerabilities but does not block a merge. Read its log and update the package when something relevant shows up.

Dependabot proposes dependency updates automatically (`.github/dependabot.yml`).

---

# 📸 Screenshots

The screenshots below document the current CyberGRC-AI interface and its connected GRC workflow.

> **Screenshot assets:** `assests/screenshots/`  
> **Documented screenshots:** 24 interface captures from the uploaded screenshot set.

## Command Center

<p align="center">
  <img src="assests/screenshots/dashboard.png.png" alt="Command Center / Dashboard" width="900">
</p>

<p align="center"><strong>Command Center / Dashboard</strong></p>

---

## Risk Management

<p align="center">
  <img src="assests/screenshots/risks%201.png" alt="Risk Management" width="900">
</p>

<p align="center"><strong>Risk Management</strong></p>

<p align="center">
  <img src="assests/screenshots/risk%202.png" alt="SQL Injection Risk — GRC Intelligence" width="900">
</p>

<p align="center"><strong>SQL Injection Risk — GRC Intelligence</strong></p>

<p align="center">
  <img src="assests/screenshots/risk%203.png" alt="Risk Management — Recent Risks & Highest Risk" width="900">
</p>

<p align="center"><strong>Risk Management — Recent Risks & Highest Risk</strong></p>

<p align="center">
  <img src="assests/screenshots/risk%204.png" alt="Security Monitoring & Incident Detection Gap — Risk Treatment" width="900">
</p>

<p align="center"><strong>Security Monitoring & Incident Detection Gap — Risk Treatment</strong></p>

---

## Control Management

<p align="center">
  <img src="assests/screenshots/controls.png" alt="Control Management" width="900">
</p>

<p align="center"><strong>Control Management</strong></p>

<p align="center">
  <img src="assests/screenshots/controls%201.png" alt="Control Management — Control List" width="900">
</p>

<p align="center"><strong>Control Management — Control List</strong></p>

<p align="center">
  <img src="assests/screenshots/controls%202.png" alt="Security Monitoring & Incident Detection — Control Details" width="900">
</p>

<p align="center"><strong>Security Monitoring & Incident Detection — Control Details</strong></p>

<p align="center">
  <img src="assests/screenshots/controls_1.png" alt="Control Details — Framework Requirements & Connected GRC Lifecycle" width="900">
</p>

<p align="center"><strong>Control Details — Framework Requirements & Connected GRC Lifecycle</strong></p>

---

## Framework Management

<p align="center">
  <img src="assests/screenshots/frameworks.png" alt="Framework Management" width="900">
</p>

<p align="center"><strong>Framework Management</strong></p>

<p align="center">
  <img src="assests/screenshots/frameworks%201.png" alt="Framework Management — Framework Versions" width="900">
</p>

<p align="center"><strong>Framework Management — Framework Versions</strong></p>

---

## Evidence Management

<p align="center">
  <img src="assests/screenshots/evidence.png" alt="Evidence Management" width="900">
</p>

<p align="center"><strong>Evidence Management</strong></p>

<p align="center">
  <img src="assests/screenshots/evidence_1.png" alt="Evidence Management — Evidence Details" width="900">
</p>

<p align="center"><strong>Evidence Management — Evidence Details</strong></p>

---

## Audit Management

<p align="center">
  <img src="assests/screenshots/audits.png" alt="Audit Management" width="900">
</p>

<p align="center"><strong>Audit Management</strong></p>

<p align="center">
  <img src="assests/screenshots/audits%201.png" alt="Audit Management — Audit Details" width="900">
</p>

<p align="center"><strong>Audit Management — Audit Details</strong></p>

<p align="center">
  <img src="assests/screenshots/audits_1.png" alt="Audit Management — Audit Scope & Findings" width="900">
</p>

<p align="center"><strong>Audit Management — Audit Scope & Findings</strong></p>

---

## Audit Findings

<p align="center">
  <img src="assests/screenshots/audit%20findings.png" alt="Audit Findings" width="900">
</p>

<p align="center"><strong>Audit Findings</strong></p>

<p align="center">
  <img src="assests/screenshots/audit%20findings%201.png" alt="Audit Findings — Finding Details" width="900">
</p>

<p align="center"><strong>Audit Findings — Finding Details</strong></p>

---

## Corrective Actions

<p align="center">
  <img src="assests/screenshots/corrective%20actions.png" alt="Corrective Actions" width="900">
</p>

<p align="center"><strong>Corrective Actions</strong></p>

<p align="center">
  <img src="assests/screenshots/corrective%20actions%201.png" alt="Corrective Actions — Action Details" width="900">
</p>

<p align="center"><strong>Corrective Actions — Action Details</strong></p>

---

## GRC Intelligence

<p align="center">
  <img src="assests/screenshots/GRC%20Intelligence.png" alt="GRC Intelligence" width="900">
</p>

<p align="center"><strong>GRC Intelligence</strong></p>

The GRC Intelligence view connects risks with controls, evidence, findings, corrective actions, frameworks and residual risk.

---

## AI Intelligence

<p align="center">
  <img src="assests/screenshots/ai%20intelligence.png" alt="AI Intelligence" width="900">
</p>

<p align="center"><strong>AI Intelligence</strong></p>

AI is positioned as an analysis and decision-support layer while authorization and governance remain deterministic.

---

## Continuous Monitoring

<p align="center">
  <img src="assests/screenshots/continuous%20monitoring.png" alt="Continuous Monitoring" width="900">
</p>

<p align="center"><strong>Continuous Monitoring</strong></p>

Continuous Monitoring surfaces risk and GRC conditions that require attention.

---

## Reports

<p align="center">
  <img src="assests/screenshots/reports.png" alt="Reports" width="900">
</p>

<p align="center"><strong>Reports</strong></p>


# 🔄 GRC Lifecycle

CyberGRC-AI is designed around a connected GRC lifecycle:

```text
                ┌──────────────┐
                │     Risk     │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   Controls   │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   Evidence   │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │    Audits    │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   Findings   │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │ Corrective   │
                │   Actions    │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │    Risk      │
                │   Treatment  │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │  Residual    │
                │     Risk     │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │ Continuous   │
                │  Monitoring  │
                └──────────────┘
```

---

# 🔄 Continuous Risk Governance & Response

CyberGRC-AI has evolved beyond periodic GRC assessment into a continuous risk lifecycle. The platform now separates deterministic risk state evaluation, response recommendation, governance approval and governed execution.

```text
Continuous Risk State
        ↓
Continuous Risk Response
        ↓
Governance Classification
        ↓
Human Notification / Escalation
        ↓
Persistent Governance Decision
        ↓
Approval / Rejection / Deferral
        ↓
Stale-Response Protection
        ↓
Governed Execution
        ↓
Execution Audit Record
```

### Continuous Risk State

Risk state is derived deterministically from current GRC conditions. The system can identify conditions such as:

- Open critical findings
- Overdue corrective actions
- Overdue or cancelled treatments
- Missing residual-risk information
- Elevated residual risk
- Inactive or ineffective controls
- Stale or missing supporting evidence

The resulting risk posture can be represented as:

```text
CURRENT
DEGRADED
REASSESSMENT_REQUIRED
```

### Continuous Risk Response

The response engine maps the current risk state to explicit response decisions, including:

- Monitor
- Review
- Reassess risk
- Update treatment
- Corrective-action review
- Control review
- Evidence review
- Escalation

The response engine is deterministic and does not allow AI output to bypass governance rules.

### Governed Response Decisions

High-impact responses are persisted as governance decisions and can move through controlled lifecycle states:

```text
PENDING
   ├── APPROVED
   ├── REJECTED
   └── DEFERRED → reconsideration

Changed underlying response
          ↓
        STALE
```

Approvals are bound to the response event that was reviewed. If the underlying continuous-risk response changes, the previous approval becomes stale and cannot be reused for execution.

### Governed Execution

Approved responses are recorded through a separate execution boundary with controls for:

- Human approval verification
- Response-event verification
- Duplicate execution prevention
- Execution actor tracking
- Execution reason preservation
- Decision/event consistency
- Failure-path integrity
- Execution auditability

Execution deliberately does not silently mutate unrelated GRC records. Domain-specific response handlers are being developed as a separate controlled execution layer.

### Governance Architecture

```text
Risk State
    ↓
Response Engine
    ↓
Governance Decision
    ↓
Human Approval
    ↓
Governed Execution
    ↓
Audit Trail
```

This separation keeps security authorization, deterministic governance and AI-assisted analysis distinct.


# 🔮 Future Direction

The next stage of CyberGRC-AI is focused on moving toward **continuous risk understanding**.

One of the key questions being explored is:

> What happens when a risk treatment that was effective yesterday is no longer effective today?

Potential signals include:

- New evidence
- Audit findings
- Overdue remediation
- Control effectiveness changes
- Emerging threats
- Risk score changes
- Treatment state changes
- New security events

The goal is to detect when the current risk state may no longer represent the organisation's actual security posture and trigger appropriate reassessment.

---

# 🧩 Future Integration

CyberGRC-AI is also being explored alongside **ARCC-X**, an event-driven security and GRC concept focused on connecting operational security events with GRC decision-making.

The broader direction is:

```text
Security / Operational Events
            ↓
       Detection
            ↓
      Risk Mapping
            ↓
    GRC Intelligence
            ↓
 Framework / Regulatory Impact
            ↓
    Treatment / Action
            ↓
 Human Approval When Required
            ↓
      Audit Trail
```

This explores a bridge between:

**Security Operations**

and

**Governance, Risk & Compliance**

rather than treating them as separate domains.

---

# 🗺️ Project Status

CyberGRC-AI is an actively developed project.

Current major capabilities include:

- ✅ Authentication with account lockout and a password policy
- ✅ Audit trail and user management
- ✅ Fine-grained RBAC
- ✅ Organizational visibility
- ✅ Object-level authorization
- ✅ Risk management
- ✅ Control management
- ✅ Evidence management
- ✅ Audit management
- ✅ Findings management
- ✅ Corrective actions
- ✅ Risk treatment workflows
- ✅ Residual risk intelligence
- ✅ GRC intelligence
- ✅ Continuous monitoring
- ✅ Continuous risk state evaluation
- ✅ Continuous risk response intelligence
- ✅ Risk treatment governance and finality
- ✅ Notification and response governance
- ✅ Human approval / rejection / deferral workflow
- ✅ Stale-response protection
- ✅ Governed response execution
- ✅ Execution audit integrity
- ✅ AI-assisted GRC analysis
- ✅ Framework mapping
- ✅ Security hardening
- ✅ Docker deployment
- ✅ Swagger / OpenAPI documentation
- ✅ Comprehensive backend test suite

### Current test status

**2,023 backend tests passing — 0 failures** (October 2026, including the PostgreSQL suite)

The backend regression suite includes coverage for continuous risk state, response intelligence, treatment governance, notification governance, governed response decisions, execution controls, authorization boundaries, account security, the audit trail, upload checks and production hardening.

### Known limitations

- The frontend has no automated tests yet, and the production bundle is one large file (route-based code splitting is planned).
- List pages load up to 500 records per request (the API supports `limit`, `offset` and an `X-Total-Count` header; paging controls in the interface are planned).
- The audit trail is not tamper-proof against direct database access, and bulk SQL updates that bypass the application are not logged.
- The AI features need a local Ollama server and a pulled model; without it they are unavailable and the rest of the platform works normally.

---

# 🔐 Security Philosophy

CyberGRC-AI follows a security-first development approach.

Key principles include:

```text
Least Privilege
       +
Defense in Depth
       +
Explicit Authorization
       +
Object-Level Access Control
       +
Organizational Boundaries
       +
Deterministic Governance
       +
AI as Decision Support
```

AI should assist security and GRC teams without bypassing the authorization and governance controls that protect organisational data.

---

# 🤝 Contributing

Contributions, ideas and discussions are welcome.

If you find a security issue, please avoid publicly disclosing sensitive details before the issue has been investigated.

For feature suggestions or improvements, open an issue or submit a pull request.

---

# 👨‍💻 Author

**Pratik Gupta**

Cybersecurity | GRC | Risk Management | Security Engineering | AI in Cybersecurity

GitHub:

https://github.com/pratiksecur

---

# 📄 License

This project is currently under active development.

License information will be added as the project is prepared for broader distribution.