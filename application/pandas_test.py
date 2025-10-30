# pandas_test.py
import pandas as pd
import plotly.express as px
import requests
from datetime import date, timedelta

zones = ['SE1','SE2','SE3','SE4']
base_url = "https://www.elprisetjustnu.se/api/v1/prices"

def fetch_prices(day, label):
    dfs = []
    for zone in zones:
        url = f"{base_url}/{day.year}/{day.month:02d}-{day.day:02d}_{zone}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df['time_start'] = pd.to_datetime(df['time_start'])
            df['SEK_per_kWh'] = df['SEK_per_kWh'].astype(float)
            df['zone'] = zone
            df['day'] = label
            dfs.append(df)
    return pd.concat(dfs)

def build_chart():
    today = date.today()
    three_weeks_ago = today - timedelta(weeks=3)
    tomorrow = today + timedelta(days=1)

    df_past = fetch_prices(three_weeks_ago, '3 veckor sedan')
    df_today = fetch_prices(today, 'Idag')
    df_tomorrow = fetch_prices(tomorrow, 'Imorgon')

    combined_df = pd.concat([df_past, df_today, df_tomorrow])

    fig = px.line(
        combined_df,
        x="time_start",
        y="SEK_per_kWh",
        color="zone",
        line_dash="day",
        title="Elpris: 3 veckor sedan, Idag, Imorgon (SE1–SE4)",
        labels={
            "SEK_per_kWh": "Pris (SEK/kWh)",
            "time_start": "Tid",
            "zone": "Prisområde",
            "day": "Dag"
        }
    )

    # Dropdown menu
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(label="Jämför per timme", method="update", args=[{"type": "scatter"}]),
                    dict(label="Jämför dagsmedel", method="update", args=[{"type": "bar"}]),
                    dict(label="Idag vs Imorgon", method="update", args=[{"type": "scatter"}])
                ]),
                direction="down",
                showactive=True
            )
        ]
    )

    return fig.to_html(full_html=False)
