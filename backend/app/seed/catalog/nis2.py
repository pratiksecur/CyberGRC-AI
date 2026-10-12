"""Seed catalog: NIS2 Directive 2022/2555."""

FRAMEWORK = {
    "name": "NIS2 Directive",
    "version": "2022/2555",
    "description": (
        "Directive (EU) 2022/2555 on measures for a high common level of cybersecurity: "
        "management-body accountability (Art. 20), the ten minimum risk-management measures "
        "(Art. 21(2)) and incident reporting deadlines (Art. 23). Descriptions are original "
        "summaries of the public legal text, not legal advice. National transposition laws "
        "may add requirements."
    ),
    "controls": [
        ("Art. 20(1)", "Governance: management approval and oversight",
         "Management bodies must approve the cybersecurity risk-management measures, oversee "
         "their implementation and can be held accountable for infringements."),
        ("Art. 20(2)", "Governance: management training",
         "Members of management bodies must follow cybersecurity training, and entities "
         "should offer similar training to employees regularly."),
        ("Art. 21(2)(a)", "Risk analysis and information system security policies",
         "Maintain policies on risk analysis and on the security of information systems."),
        ("Art. 21(2)(b)", "Incident handling",
         "Have processes to prevent, detect, respond to and handle security incidents."),
        ("Art. 21(2)(c)", "Business continuity and crisis management",
         "Plan for business continuity, including backup management, disaster recovery and "
         "crisis management."),
        ("Art. 21(2)(d)", "Supply chain security",
         "Manage security in relationships with direct suppliers and service providers."),
        ("Art. 21(2)(e)", "Security in acquisition, development and maintenance",
         "Secure the acquisition, development and maintenance of network and information "
         "systems, including vulnerability handling and disclosure."),
        ("Art. 21(2)(f)", "Assessing effectiveness of measures",
         "Use policies and procedures to assess whether the cybersecurity risk-management "
         "measures are effective."),
        ("Art. 21(2)(g)", "Cyber hygiene and cybersecurity training",
         "Apply basic cyber hygiene practices and provide cybersecurity training."),
        ("Art. 21(2)(h)", "Cryptography and encryption",
         "Use policies and procedures for cryptography and, where appropriate, encryption."),
        ("Art. 21(2)(i)", "Human resources security, access control and asset management",
         "Cover personnel security, access control policies and asset management."),
        ("Art. 21(2)(j)", "Multi-factor authentication and secure communications",
         "Use multi-factor or continuous authentication and secured voice, video, text and "
         "emergency communications where appropriate."),
        ("Art. 23(4)(a)", "Incident reporting: early warning within 24 hours",
         "For a significant incident, send an early warning to the national CSIRT or "
         "competent authority within 24 hours of becoming aware."),
        ("Art. 23(4)(b)", "Incident reporting: notification within 72 hours",
         "Within 72 hours of becoming aware, submit an incident notification with an initial "
         "assessment, severity and impact."),
        ("Art. 23(4)(d)", "Incident reporting: final report within one month",
         "Submit a final report no later than one month after the notification, covering "
         "root cause, mitigation and cross-border impact."),
    ],
}