"""Seed catalog: NIST CSF 2.0."""

FRAMEWORK = {
    "name": "NIST CSF 2.0",
    "version": "2.0",
    "description": (
        "NIST Cybersecurity Framework 2.0 at category level: the 22 categories across the six "
        "functions (Govern, Identify, Protect, Detect, Respond, Recover). Descriptions are "
        "original summaries; see the official NIST publication for the full subcategories. "
    ),
    "controls": [
        ("GV.OC", "Organizational Context",
         "Understand the mission, stakeholders, legal obligations and dependencies that "
         "shape cybersecurity risk decisions."),
        ("GV.RM", "Risk Management Strategy",
         "Set and communicate priorities, risk appetite and risk tolerance that guide "
         "cybersecurity risk decisions."),
        ("GV.RR", "Roles, Responsibilities, and Authorities",
         "Assign, resource and communicate accountability for cybersecurity risk "
         "management across the organization."),
        ("GV.PO", "Policy",
         "Establish, communicate, enforce and keep current the cybersecurity policy the "
         "organization follows."),
        ("GV.OV", "Oversight",
         "Use the results of risk management activities to review and adjust strategy and "
         "performance."),
        ("GV.SC", "Cybersecurity Supply Chain Risk Management",
         "Identify, assess and manage cybersecurity risk from suppliers and third parties "
         "across the relationship lifecycle."),
        ("ID.AM", "Asset Management",
         "Keep inventories of hardware, software, services, data and suppliers, and rank "
         "them by importance to the business."),
        ("ID.RA", "Risk Assessment",
         "Understand cybersecurity risk to operations, assets and people by identifying "
         "threats, vulnerabilities and likely impacts."),
        ("ID.IM", "Improvement",
         "Find improvements to cybersecurity risk management from assessments, exercises, "
         "incidents and lessons learned."),
        ("PR.AA", "Identity Management, Authentication, and Access Control",
         "Limit access to physical and logical assets to authorized users, services and "
         "hardware, in line with assessed risk."),
        ("PR.AT", "Awareness and Training",
         "Give personnel the awareness and skills they need to carry out their "
         "cybersecurity responsibilities."),
        ("PR.DS", "Data Security",
         "Protect data at rest, in transit and in use to preserve its confidentiality, "
         "integrity and availability."),
        ("PR.PS", "Platform Security",
         "Manage the security of hardware, software and services through their lifecycle, "
         "including configuration, patching and logging."),
        ("PR.IR", "Technology Infrastructure Resilience",
         "Design and manage security architecture so networks and environments stay "
         "protected and resilient, with adequate capacity."),
        ("DE.CM", "Continuous Monitoring",
         "Monitor assets, networks, people and services to find anomalies, indicators of "
         "compromise and other adverse events."),
        ("DE.AE", "Adverse Event Analysis",
         "Analyze anomalies and indicators to characterize events, correlate information "
         "and declare cybersecurity incidents."),
        ("RS.MA", "Incident Management",
         "Manage responses to detected incidents, including triage, validation, "
         "prioritization and escalation."),
        ("RS.AN", "Incident Analysis",
         "Investigate incidents to understand what happened and to support effective "
         "response and recovery."),
        ("RS.CO", "Incident Response Reporting and Communication",
         "Coordinate and share incident response information with internal and external "
         "stakeholders as required."),
        ("RS.MI", "Incident Mitigation",
         "Contain and eradicate incidents to limit their spread and effects."),
        ("RC.RP", "Incident Recovery Plan Execution",
         "Carry out the recovery plan to restore operations and services affected by "
         "incidents."),
        ("RC.CO", "Incident Recovery Communication",
         "Coordinate restoration and recovery communication with internal and external "
         "parties."),
    ],
}