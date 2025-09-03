# air_app.py
import streamlit as st
from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import io
import json

# Authenticate with service account
# Load directly from secrets (already a dict)
credentials = dict(st.secrets["bigquery"])
client = bigquery.Client.from_service_account_info(credentials)


st.set_page_config(page_title="🌍 Air Pollution Explorer", layout="wide")
st.title("🌍 Air Pollution Knowledge Explorer")
st.write("Explore air quality data (PM2.5, PM10, NO2, CO) using BigQuery + Streamlit.")

# ------------------- SIDEBAR FILTERS ------------------- #
st.sidebar.header("Filters")

pollutant = st.sidebar.selectbox(
    "Select Pollutant", ["pm25", "pm10", "no2", "co"]
)
country = st.sidebar.text_input("Enter Country Code (e.g., IN, US, CN)", "")

# ------------------- LOAD DATA ------------------- #
@st.cache_data
def load_data(pollutant, country):
    query = f"""
        SELECT country, city, AVG(value) AS avg_pollutant,
               latitude, longitude
        FROM `bigquery-public-data.openaq.global_air_quality`
        WHERE pollutant = '{pollutant}'
        {"AND country = '" + country + "'" if country else ""}
        GROUP BY country, city, latitude, longitude
        ORDER BY avg_pollutant DESC
        LIMIT 20;
    """
    df = client.query(query).to_dataframe()
    return df

df = load_data(pollutant, country)

# ------------------- SHOW DATA ------------------- #
if not df.empty:
    st.subheader(f"📊 Top Cities by {pollutant.upper()}")
    st.dataframe(df)

    # ------------------- BAR CHART ------------------- #
    st.subheader("📈 Visualization")
    fig, ax = plt.subplots(figsize=(12, 6))
    df_sorted = df.sort_values(by="avg_pollutant", ascending=False)
    ax.bar(df_sorted["city"], df_sorted["avg_pollutant"],
           color=plt.cm.coolwarm(df_sorted["avg_pollutant"] / max(df_sorted["avg_pollutant"])))
    ax.set_xlabel("City")
    ax.set_ylabel(f"Average {pollutant.upper()}")
    ax.set_title(f"Top Cities by {pollutant.upper()}")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

    # ------------------- MAP ------------------- #
    st.subheader("🗺️ Pollution Map")
    m = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df.iterrows():
        if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=max(3, row["avg_pollutant"] / 50),
                popup=f"{row['city']} ({row['avg_pollutant']:.2f})",
                color="red",
                fill=True,
                fill_opacity=0.6,
            ).add_to(m)
    st_folium(m, width=700, height=500)

    # ------------------- DOWNLOAD SECTION ------------------- #
    st.subheader("⬇️ Download Data")

    # CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "air_quality.csv", "text/csv")

    # Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="AirQuality")
    excel_data = output.getvalue()

    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="air_quality.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠️ No data found for this selection.")
