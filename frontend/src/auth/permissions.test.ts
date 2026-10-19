import { describe, expect, it } from "vitest";

import { hasPermission } from "./permissions";

describe("hasPermission", () => {
  it("denies everything without a role or with an unknown role", () => {
    expect(hasPermission(undefined, "risks", "view")).toBe(false);
    expect(hasPermission("", "risks", "view")).toBe(false);
    expect(hasPermission("Intern", "risks", "view")).toBe(false);
  });

  it("lets an Admin manage users and delete risks", () => {
    expect(hasPermission("Admin", "users", "create")).toBe(true);
    expect(hasPermission("Admin", "risks", "delete")).toBe(true);
  });

  it("keeps user management to Admins", () => {
    expect(hasPermission("GRC Manager", "users", "create")).toBe(false);
    expect(hasPermission("Risk Analyst", "users", "view")).toBe(false);
    expect(hasPermission("Auditor", "users", "view")).toBe(false);
    expect(hasPermission("Employee", "users", "view")).toBe(false);
  });

  it("gives the executive summary to GRC Managers only", () => {
    expect(hasPermission("GRC Manager", "ai_executive_summary", "view")).toBe(true);
    expect(hasPermission("Admin", "ai_executive_summary", "view")).toBe(false);
    expect(hasPermission("Auditor", "ai_executive_summary", "view")).toBe(false);
  });

  it("makes an Auditor read-only on risks but able to work on audits", () => {
    expect(hasPermission("Auditor", "risks", "view")).toBe(true);
    expect(hasPermission("Auditor", "risks", "update")).toBe(false);
    expect(hasPermission("Auditor", "audits", "create")).toBe(true);
  });

  it("does not let non-managers change frameworks", () => {
    expect(hasPermission("GRC Manager", "frameworks", "update")).toBe(true);
    expect(hasPermission("Risk Analyst", "frameworks", "update")).toBe(false);
    expect(hasPermission("Employee", "frameworks", "view")).toBe(true);
  });

  it("only lets an Employee update corrective actions, not create them", () => {
    expect(hasPermission("Employee", "corrective_actions", "update")).toBe(true);
    expect(hasPermission("Employee", "corrective_actions", "create")).toBe(false);
  });

  it("denies a resource a role has no entry for", () => {
    expect(hasPermission("Employee", "ai", "use")).toBe(false);
    expect(hasPermission("Risk Analyst", "ai", "view")).toBe(false);
  });
});
