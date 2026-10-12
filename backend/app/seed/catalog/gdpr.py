"""Seed catalog: GDPR 2016/679."""

FRAMEWORK = {
    "name": "GDPR",
    "version": "2016/679",
    "description": (
        "General Data Protection Regulation (Regulation (EU) 2016/679): a practical selection "
        "of the articles that most often become controls, covering principles, transparency, "
        "data subject rights, accountability, security, breach handling, impact assessment, "
        "the data protection officer and international transfers. Descriptions are original "
        "summaries of the public legal text, not legal advice. "
    ),
    "controls": [
        ("Art. 5", "Principles relating to processing of personal data",
         "Personal data must be processed lawfully, fairly and transparently, for "
         "specified purposes, minimised, accurate, limited in storage, secure, and with "
         "the controller able to demonstrate compliance."),
        ("Art. 6", "Lawfulness of processing",
         "Every processing activity needs a valid legal basis, such as consent, contract, "
         "legal obligation, vital interests, public task or legitimate interests."),
        ("Art. 7", "Conditions for consent",
         "Where consent is the basis, it must be demonstrable, clearly presented, freely "
         "given and as easy to withdraw as to give."),
        ("Art. 9", "Processing of special categories of personal data",
         "Sensitive data such as health, biometric or political data is prohibited unless "
         "a specific exception applies."),
        ("Art. 12", "Transparent information and communication for data subject rights",
         "Information and responses to data subject requests must be concise, clear, free "
         "of charge in general, and given within the legal deadlines."),
        ("Art. 13", "Information where data is collected from the data subject",
         "Individuals must be told who is processing their data, why, on what basis, for "
         "how long and what their rights are at the point of collection."),
        ("Art. 14", "Information where data was not obtained from the data subject",
         "When data comes from another source, individuals must still be informed, "
         "including where the data originated."),
        ("Art. 15", "Right of access by the data subject",
         "Individuals can obtain confirmation of processing, a copy of their data and "
         "related information."),
        ("Art. 16", "Right to rectification",
         "Individuals can have inaccurate personal data corrected and incomplete data "
         "completed."),
        ("Art. 17", "Right to erasure",
         "Individuals can have their data erased in defined circumstances, for example "
         "when it is no longer needed or consent is withdrawn."),
        ("Art. 18", "Right to restriction of processing",
         "Individuals can require processing to be limited while accuracy or lawfulness is "
         "being resolved."),
        ("Art. 20", "Right to data portability",
         "Individuals can receive data they provided in a structured, commonly used, "
         "machine-readable format and have it transmitted to another controller."),
        ("Art. 21", "Right to object",
         "Individuals can object to processing based on legitimate interests or public "
         "task, and always to direct marketing."),
        ("Art. 22", "Automated individual decision-making, including profiling",
         "Individuals have protections against decisions based solely on automated "
         "processing that significantly affect them."),
        ("Art. 24", "Responsibility of the controller",
         "Controllers must implement and review appropriate technical and organisational "
         "measures and be able to show processing complies."),
        ("Art. 25", "Data protection by design and by default",
         "Data protection must be built into systems and processes from the start, with "
         "only necessary data processed by default."),
        ("Art. 26", "Joint controllers",
         "Where several parties decide purposes and means together, their respective "
         "responsibilities must be set out in a transparent arrangement."),
        ("Art. 28", "Processor",
         "Processing on a controller's behalf requires a binding contract and processors "
         "that give sufficient guarantees of appropriate measures."),
        ("Art. 30", "Records of processing activities",
         "Controllers and processors must maintain written records of their processing "
         "activities, available to the supervisory authority."),
        ("Art. 32", "Security of processing",
         "Appropriate technical and organisational security measures must be applied, "
         "taking risk, state of the art and cost into account."),
        ("Art. 33", "Notification of a personal data breach to the supervisory authority",
         "Breaches likely to risk individuals must be reported to the supervisory "
         "authority without undue delay and where feasible within 72 hours."),
        ("Art. 34", "Communication of a personal data breach to the data subject",
         "Individuals must be told without undue delay when a breach is likely to result "
         "in a high risk to them."),
        ("Art. 35", "Data protection impact assessment",
         "A documented impact assessment is required before processing that is likely to "
         "result in a high risk to individuals."),
        ("Art. 36", "Prior consultation",
         "If an impact assessment shows high residual risk, the supervisory authority must "
         "be consulted before processing starts."),
        ("Art. 37", "Designation of the data protection officer",
         "A data protection officer must be designated in the cases the regulation "
         "specifies, such as large-scale monitoring or special-category processing."),
        ("Art. 38", "Position of the data protection officer",
         "The officer must be involved properly and in good time, be resourced, "
         "independent and report to the highest management level."),
        ("Art. 39", "Tasks of the data protection officer",
         "The officer advises on obligations, monitors compliance, advises on impact "
         "assessments and cooperates with the supervisory authority."),
        ("Art. 44", "General principle for transfers",
         "Transfers of personal data outside the EU or EEA may only occur if the "
         "conditions of the transfer chapter are met."),
        ("Art. 45", "Transfers on the basis of an adequacy decision",
         "Data may flow to a country or organisation the European Commission has decided "
         "ensures an adequate level of protection."),
        ("Art. 46", "Transfers subject to appropriate safeguards",
         "Without an adequacy decision, transfers need safeguards such as standard "
         "contractual clauses or binding corporate rules, with enforceable rights."),
        ("Art. 49", "Derogations for specific situations",
         "Limited exceptions allow transfers without adequacy or safeguards, for example "
         "explicit consent or contract necessity, and must be used narrowly."),
    ],
}