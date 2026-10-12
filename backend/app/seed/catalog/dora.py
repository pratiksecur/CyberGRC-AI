"""Seed catalog: DORA Regulation 2022/2554."""

FRAMEWORK = {
    "name": "DORA",
    "version": "2022/2554",
    "description": (
        "Digital Operational Resilience Act (Regulation (EU) 2022/2554) for the EU financial "
        "sector: ICT risk management, incident management and reporting, resilience testing, "
        "third-party risk and information sharing. A practical selection of articles; "
        "descriptions are original summaries of the public legal text, not legal advice."
    ),
    "controls": [
        ("Art. 5", "Governance and organisation",
         "The management body defines, approves, oversees and is accountable for the ICT "
         "risk management framework."),
        ("Art. 6", "ICT risk management framework",
         "Maintain a documented, reviewed framework with strategies, policies, procedures "
         "and tools to manage ICT risk."),
        ("Art. 7", "ICT systems, protocols and tools",
         "Use up-to-date, reliable and sufficiently resourced ICT systems that suit the "
         "scale and criticality of operations."),
        ("Art. 8", "Identification",
         "Identify, classify and document ICT-supported business functions, information "
         "assets, dependencies and risk sources."),
        ("Art. 9", "Protection and prevention",
         "Keep ICT systems secure and resilient through security policies, access control, "
         "strong authentication, encryption and patching."),
        ("Art. 10", "Detection",
         "Detect anomalous activity and ICT incidents promptly, with defined thresholds "
         "and alert criteria."),
        ("Art. 11", "Response and recovery",
         "Maintain an ICT business continuity policy and response and recovery plans, "
         "tested and ready to activate."),
        ("Art. 12", "Backup, restoration and recovery",
         "Define backup policies and procedures and test restoration and recovery methods "
         "against objectives."),
        ("Art. 13", "Learning and evolving",
         "Learn from incidents and tests, gather threat information and keep awareness and "
         "training up to date."),
        ("Art. 14", "Communication",
         "Have communication plans for ICT incidents and vulnerabilities, with a designated "
         "spokesperson."),
        ("Art. 17", "ICT-related incident management process",
         "Define and implement a process to detect, manage, log and notify ICT-related "
         "incidents, with roles and escalation."),
        ("Art. 18", "Classification of ICT-related incidents and cyber threats",
         "Classify incidents by criteria such as clients affected, duration, data loss and "
         "criticality of services."),
        ("Art. 19", "Reporting of major ICT-related incidents",
         "Report major ICT-related incidents to the competent authority using the required "
         "stages and templates, and optionally report significant cyber threats."),
        ("Art. 24", "General requirements for resilience testing",
         "Run a proportionate, risk-based digital operational resilience testing programme "
         "at least yearly for critical systems."),
        ("Art. 25", "Testing of ICT tools and systems",
         "Include tests such as vulnerability assessments, scenario-based tests, "
         "performance and end-to-end testing and penetration testing."),
        ("Art. 26", "Advanced testing based on TLPT",
         "Entities in scope carry out threat-led penetration testing at least every three "
         "years on live critical functions."),
        ("Art. 28", "General principles of ICT third-party risk",
         "Manage ICT third-party risk as part of the risk framework, keep a register of "
         "arrangements and keep exit strategies."),
        ("Art. 29", "ICT concentration risk assessment",
         "Assess concentration risk and dependency before entering ICT service "
         "arrangements for critical functions."),
        ("Art. 30", "Key contractual provisions",
         "Contracts with ICT providers must contain required provisions, such as service "
         "levels, security, audit and access rights, and exit terms."),
        ("Art. 45", "Information-sharing arrangements",
         "Financial entities may exchange cyber threat information within trusted "
         "communities, subject to confidentiality and data protection."),
    ],
}