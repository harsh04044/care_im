"""Bot flow: welcome, pick category/patient, then show mock data. POC only."""

from __future__ import annotations

_conversation_state: dict[str, dict] = {}

menu_footer = "\n_Send any message to return to the menu._"
section_sep = "─────────────────────"
welcome_body = (
    "Welcome to *CARE IM Bot* \u2695\ufe0f\n\n"
    "District Hospital Ernakulam\n"
    "What would you like to look up?"
)


def _get_state(sender: str) -> dict:
    if sender not in _conversation_state:
        _conversation_state[sender] = {"step": "welcome"}
    return _conversation_state[sender]


def _reset_state(sender: str) -> None:
    _conversation_state[sender] = {"step": "welcome"}


def reset_all_states() -> None:
    _conversation_state.clear()


MOCK_PATIENTS: dict[str, dict] = {
    "P001": {
        "name": "Arun Kumar",
        "age": 45,
        "dob": "1979",
        "phone": "919876543201",
        "gender": "M",
        "ward": "General Ward 3",
        "bed": "B-12",
        "facility": "District Hospital Ernakulam",
        "admission_date": "2025-03-10",
        "status": "Stable",
        "diagnosis": "Acute bronchitis",
    },
    "P002": {
        "name": "Meera Nair",
        "age": 62,
        "dob": "1962",
        "phone": "919876543202",
        "gender": "F",
        "ward": "ICU-1",
        "bed": "A-05",
        "facility": "District Hospital Ernakulam",
        "admission_date": "2025-03-14",
        "status": "Under observation",
        "diagnosis": "Type 2 diabetes — hyperglycemia",
    },
    "P003": {
        "name": "Ravi Menon",
        "age": 34,
        "dob": "1990",
        "phone": "919876543203",
        "gender": "M",
        "ward": "Surgical Ward 1",
        "bed": "C-08",
        "facility": "Taluk Hospital Aluva",
        "admission_date": "2025-03-12",
        "status": "Post-op recovery",
        "diagnosis": "Appendectomy",
    },
    "P004": {
        "name": "Lakshmi Devi",
        "age": 28,
        "dob": "1996",
        "phone": "919876543204",
        "gender": "F",
        "ward": "Maternity Ward",
        "bed": "M-02",
        "facility": "CHC Perumbavoor",
        "admission_date": "2025-03-15",
        "status": "Stable",
        "diagnosis": "Normal delivery — post-partum care",
    },
}

MOCK_MEDICATIONS: dict[str, list[dict]] = {
    "P001": [
        {"name": "Paracetamol", "dose": "500 mg", "frequency": "8 hourly", "route": "Oral"},
        {"name": "Amoxicillin", "dose": "250 mg", "frequency": "12 hourly", "route": "Oral"},
        {
            "name": "Salbutamol nebulization",
            "dose": "2.5 mg",
            "frequency": "8 hourly",
            "route": "Inhaled",
        },
    ],
    "P002": [
        {
            "name": "Insulin (Regular)",
            "dose": "10 units",
            "frequency": "Before meals",
            "route": "SC",
        },
        {"name": "Metformin", "dose": "500 mg", "frequency": "Twice daily", "route": "Oral"},
        {"name": "Atorvastatin", "dose": "10 mg", "frequency": "At night", "route": "Oral"},
    ],
    "P003": [
        {"name": "Ceftriaxone", "dose": "1 g", "frequency": "12 hourly", "route": "IV"},
        {"name": "Tramadol", "dose": "50 mg", "frequency": "8 hourly (PRN)", "route": "IV"},
    ],
    "P004": [
        {"name": "Iron + Folic Acid", "dose": "1 tab", "frequency": "Once daily", "route": "Oral"},
        {"name": "Calcium", "dose": "500 mg", "frequency": "Twice daily", "route": "Oral"},
    ],
}

MOCK_PROCEDURES: dict[str, list[dict]] = {
    "P001": [
        {"name": "Blood draw (CBC)", "date": "2025-03-15", "status": "Done"},
        {"name": "Chest X-Ray", "date": "2025-03-16", "status": "Scheduled"},
    ],
    "P002": [
        {"name": "ECG", "date": "2025-03-14", "status": "Done"},
        {"name": "HbA1c blood test", "date": "2025-03-15", "status": "Done"},
        {"name": "Fundoscopy", "date": "2025-03-17", "status": "Scheduled"},
    ],
    "P003": [
        {"name": "Appendectomy", "date": "2025-03-12", "status": "Done"},
        {"name": "Wound dressing", "date": "2025-03-16", "status": "Done"},
        {"name": "Suture removal", "date": "2025-03-19", "status": "Scheduled"},
    ],
    "P004": [
        {"name": "Normal delivery", "date": "2025-03-15", "status": "Done"},
        {"name": "Neonatal screening", "date": "2025-03-16", "status": "Scheduled"},
    ],
}


def _build_welcome_message() -> dict:
    body = welcome_body
    return {
        "message_type": "interactive",
        "content": body,
        "metadata": {
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "btn_patient", "title": "Patient Info"}},
                        {
                            "type": "reply",
                            "reply": {"id": "btn_medications", "title": "Medications"},
                        },
                        {"type": "reply", "reply": {"id": "btn_procedures", "title": "Procedures"}},
                    ],
                },
            },
        },
    }


def _build_patient_list(category: str) -> dict:
    rows = []
    for pid, p in MOCK_PATIENTS.items():
        rows.append(
            {
                "id": f"select_{pid}",
                "title": p["name"],
                "description": f"{p['ward']} | {p['facility']}",
            }
        )

    labels = {
        "patient": "Patient Info",
        "medications": "Medications",
        "procedures": "Procedures",
    }
    label = labels.get(category, category.title())
    prompt = f"Select a patient to view *{label}*:"

    return {
        "message_type": "interactive",
        "content": prompt,
        "metadata": {
            "interactive": {
                "type": "list",
                "body": {"text": prompt},
                "action": {
                    "button": "Choose Patient",
                    "sections": [
                        {
                            "title": "Admitted Patients",
                            "rows": rows,
                        },
                    ],
                },
            },
            "category": category,
        },
    }


def _build_patient_info(patient_id: str) -> dict:
    p = MOCK_PATIENTS[patient_id]
    text = (
        f"*Patient Record — {p['name']}*\n"
        f"{section_sep}\n"
        f"*ID:* {patient_id}\n"
        f"*Age:* {p['age']} | *Gender:* {p['gender']}\n"
        f"*Facility:* {p['facility']}\n"
        f"*Ward:* {p['ward']} | *Bed:* {p['bed']}\n"
        f"*Admitted:* {p['admission_date']}\n"
        f"*Diagnosis:* {p['diagnosis']}\n"
        f"*Status:* {p['status']}\n"
        f"{menu_footer}"
    )
    return {"message_type": "text", "content": text, "metadata": {}}


def _build_patient_section(
    *,
    patient_id: str,
    title: str,
    items: list[dict],
    empty_line: str,
    item_line,
) -> dict:
    p = MOCK_PATIENTS[patient_id]
    lines = [f"*{title} — {p['name']}*", section_sep]
    for item in items:
        lines.append(item_line(item))
    if not items:
        lines.append(empty_line)
    lines.append(menu_footer)
    return {"message_type": "text", "content": "\n".join(lines), "metadata": {}}


def _build_medications_info(patient_id: str) -> dict:
    meds = MOCK_MEDICATIONS.get(patient_id, [])
    return _build_patient_section(
        patient_id=patient_id,
        title="Medications",
        items=meds,
        empty_line="_No medications on record._",
        item_line=lambda m: f"\u2022 *{m['name']}* {m['dose']} — {m['frequency']} ({m['route']})",
    )


def _build_procedures_info(patient_id: str) -> dict:
    procs = MOCK_PROCEDURES.get(patient_id, [])

    def _procedure_line(pr: dict) -> str:
        status_icon = "\u2705" if pr["status"] == "Done" else "\U0001f552"
        return f"{status_icon} *{pr['name']}* — {pr['date']} ({pr['status']})"

    return _build_patient_section(
        patient_id=patient_id,
        title="Procedures",
        items=procs,
        empty_line="_No procedures on record._",
        item_line=_procedure_line,
    )


def get_care_reply(text: str, sender: str = "") -> dict:
    if not sender:
        return _build_welcome_message()

    state = _get_state(sender)
    step = state.get("step", "welcome")
    raw = (text or "").strip().lower()

    if step == "welcome":
        if raw in ("btn_patient", "btn_medications", "btn_procedures"):
            category_map = {
                "btn_patient": "patient",
                "btn_medications": "medications",
                "btn_procedures": "procedures",
            }
            category = category_map[raw]
            state["step"] = "select_patient"
            state["category"] = category
            return _build_patient_list(category)

        return _build_welcome_message()

    if step == "select_patient":
        if raw.startswith("select_"):
            patient_id = raw.replace("select_", "").upper()
            if patient_id in MOCK_PATIENTS:
                category = state.get("category", "patient")
                _reset_state(sender)
                builders = {
                    "patient": _build_patient_info,
                    "medications": _build_medications_info,
                    "procedures": _build_procedures_info,
                }
                if category in builders:
                    return builders[category](patient_id)

        _reset_state(sender)
        return _build_welcome_message()

    _reset_state(sender)
    return _build_welcome_message()
