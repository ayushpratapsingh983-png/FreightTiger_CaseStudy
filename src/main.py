import pandas as pd
import os
from processor import calculate_weekly_metrics, apply_baselines
from retriever import get_justification

def main():
    # Paths to data files
    shipments_path = 'data/shipment_records.csv'
    notes_path = 'data/context_notes.csv'
    output_path = 'outputs/FreightTiger_Final_Analysis.csv'

    # Ensure paths are absolute relative to the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shipments_path = os.path.join(base_dir, shipments_path)
    notes_path = os.path.join(base_dir, notes_path)
    output_path = os.path.join(base_dir, output_path)

    # Load Data
    shipments = pd.read_csv(shipments_path)

    # Fix: Create the 'route' column from origin and destination
    if 'route' not in shipments.columns:
        shipments['route'] = shipments['origin'] + '-' + shipments['destination']

    notes = pd.read_csv(notes_path)

    # Step 1: Math
    weekly_grouped = calculate_weekly_metrics(shipments)
    metrics_df = apply_baselines(weekly_grouped, shipments)

    # Step 2: Analysis & Justification
    final_rows = []
    for _, row in metrics_df.iterrows():
        flag, note_id, reason = get_justification(
            row['route'], row['week_of'], row['diff_past'], row['diff_peers'], notes
        )

        final_rows.append({
            'route': row['route'],
            'week_of': row['week_of'].strftime('%Y-%m-%d'),
            'cost_per_tonne_km': round(row['cost_per_tonne_km'], 2),
            'vs_own_history': f"{row['diff_past']:+.1f}% vs this route's past average",
            'vs_similar_routes': f"{row['diff_peers']:+.1f}% vs similar-length routes this week",
            'flagged': flag,
            'matched_note_id': note_id,
            'reason': reason
        })

    # Step 3: Save to CSV
    output_df = pd.DataFrame(final_rows)
    output_df.to_csv(output_path, index=False)
    print(f"Success! Results saved to: {output_path}")

if __name__ == "__main__":
    main()
