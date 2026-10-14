import pandas as pd

def get_justification(route, week, diff_past, diff_peers, notes_df):
    # Threshold: Flag if cost is > 10% above either baseline
    if diff_past < 10 and diff_peers < 10:
        return "No", "", "Cost is within normal operating parameters."

    # Convert week to datetime
    week_dt = pd.to_datetime(week)

    # Filter notes that actually apply
    relevant_notes = notes_df[
        ((notes_df['applies_to'] == route) | (notes_df['applies_to'] == "All Routes"))
    ]

    for _, note in relevant_notes.iterrows():
        note_date = pd.to_datetime(note['date'])

        # 1. Date Check: Note must be within 7 days of the week_of
        if abs((note_date - week_dt).days) > 7:
            continue

        # 2. Trap Check: Does the note actually explain a COST RISE?
        ignore_keywords = ["not significantly affected", "no major disruptions",
                           "no significant disruptions", "without a rate change",
                           "not part of this dataset"]

        if any(kw in note['note'].lower() for kw in ignore_keywords):
            continue

        # If it passed all checks, it is a valid justification
        return "No (justified)", note['note_id'], f"Matches note {note['note_id']}: {note['note']}"

    # If no valid note was found
    return "Yes", "", "The cost rise is significant but no context note justifies it. Flagged for review."
