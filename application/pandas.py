# pandas.py
# This file will contain your pandas logic for generating table and chart data

# Example: pseudo data for table and chart
# Replace this with your pandas code later

data_rows = [
    {'id': 1, 'name': 'Alpha', 'value': 4567, 'status': 'Active'},
    {'id': 2, 'name': 'Beta', 'value': 3421, 'status': 'Pending'},
    {'id': 3, 'name': 'Gamma', 'value': 5892, 'status': 'Active'},
    {'id': 4, 'name': 'Delta', 'value': 2156, 'status': 'Inactive'},
    {'id': 5, 'name': 'Epsilon', 'value': 7234, 'status': 'Active'},
    {'id': 6, 'name': 'Zeta', 'value': 4123, 'status': 'Pending'},
]

# For chart: extract values and names
chart_labels = [row['name'] for row in data_rows]  # Use pandas to get column later
chart_values = [row['value'] for row in data_rows] # Use pandas to get column later

# TODO: Replace pseudo data above with pandas DataFrame logic
# Example:
# import pandas as pd
# df = pd.read_csv('your_data.csv')
# data_rows = df.to_dict('records')
# chart_labels = df['name'].tolist()
# chart_values = df['value'].tolist()