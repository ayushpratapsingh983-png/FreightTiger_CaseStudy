import pandas as pd
import numpy as np

def calculate_weekly_metrics(df):
    # Clean column names to remove leading/trailing spaces
    df.columns = df.columns.str.strip()

    # The actual date column in the CSV is 'shipment_date'
    date_col = 'shipment_date'
    if date_col not in df.columns:
        # Fallback: try to find any column with 'date' in it
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        if not date_col:
            raise KeyError("Could not find a date column (like 'shipment_date') in the CSV file.")

    # Ensure date is datetime
    df[date_col] = pd.to_datetime(df[date_col])

    # Convert each shipment date to its 'week_of' (The Monday of that week)
    # In pandas, .dt.to_period('W').dt.start_time gets the Monday
    df['week_of'] = df[date_col].dt.to_period('W').dt.start_time

    # Standardize cost column name
    cost_col = 'freight_cost_inr' if 'freight_cost_inr' in df.columns else 'freight_cost'

    # Group by route and the new 'week_of' column
    grouped = df.groupby(['route', 'week_of']).agg({
        cost_col: 'sum',
        'quantity_tonnes': 'sum',
        'distance_km': 'sum'
    }).reset_index()

    # Rename the aggregated cost column to a standard name for the rest of the pipeline
    grouped = grouped.rename(columns={cost_col: 'freight_cost'})

    # Calculate cost_per_tonne_km
    # route_distances = average distance for that route
    route_distances = df.groupby('route')['distance_km'].mean().to_dict()

    def get_cost(row):
        dist = route_distances[row['route']]
        # Formula: Total Freight Cost / (Total Quantity * Distance)
        return row['freight_cost'] / (row['quantity_tonnes'] * dist)

    grouped['cost_per_tonne_km'] = grouped.apply(get_cost, axis=1)
    return grouped

def apply_baselines(grouped, raw_df):
    # Map route types - we extract route name from origin-destination
    # Since 'route' column might not exist in raw_df, we create it from origin-destination
    if 'route' not in raw_df.columns:
        raw_df['route'] = raw_df['origin'] + '-' + raw_df['destination']

    route_types = {
        'Mumbai-Pune': 'Short', 'Delhi-Jaipur': 'Short',
        'Ahmedabad-Mumbai': 'Medium', 'Chennai-Bangalore': 'Medium', 'Kolkata-Bhubaneswar': 'Medium',
        'Delhi-Chennai': 'Long', 'Mumbai-Delhi': 'Long'
    }
    grouped['route_type'] = grouped['route'].map(route_types)

    final_data = []

    for route in grouped['route'].unique():
        route_data = grouped[grouped['route'] == route].sort_values('week_of')

        for i, row in route_data.iterrows():
            # 1. VS OWN HISTORY (Previous 8 weeks ONLY)
            history = route_data[(route_data['week_of'] < row['week_of'])].tail(8)
            avg_past = history['cost_per_tonne_km'].mean() if not history.empty else np.nan
            diff_past = ((row['cost_per_tonne_km'] - avg_past) / avg_past * 100) if not np.isnan(avg_past) else 0

            # 2. VS SIMILAR ROUTES (Same week, same type, excluding self)
            peers = grouped[(grouped['week_of'] == row['week_of']) &
                            (grouped['route_type'] == row['route_type']) &
                            (grouped['route'] != route)]
            avg_peers = peers['cost_per_tonne_km'].mean() if not peers.empty else np.nan
            diff_peers = ((row['cost_per_tonne_km'] - avg_peers) / avg_peers * 100) if not np.isnan(avg_peers) else 0

            final_data.append({
                'route': route,
                'week_of': row['week_of'],
                'cost_per_tonne_km': row['cost_per_tonne_km'],
                'diff_past': diff_past,
                'diff_peers': diff_peers
            })

    return pd.DataFrame(final_data)
