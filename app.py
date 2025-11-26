import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="UK House Price Index Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading ---
@st.cache_data
def load_data():
    df = pd.read_csv("UK-HPI-full-Shorted 2.csv")
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['Date', 'RegionName'])
    numeric_cols = [
        'AveragePrice', '12m%Change', 
        'SemiDetachedPrice', 'TerracedPrice', 'FlatPrice', 
        'FTBPrice', 'FTBIndex', 'FTB12m%Change'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Sidebar ---
all_regions = sorted(df['RegionName'].unique())
st.sidebar.header("Navigation Tab: Filter by region")
st.sidebar.subheader("Afternoon Amber")

default_region = 'Nottinghamshire' if 'Nottinghamshire' in all_regions else all_regions[0]
selected_region = st.sidebar.selectbox("Select Region to Analyse:", options=all_regions, index=all_regions.index(default_region))

min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input("Select Time Period:", value=(min_date, max_date), min_value=min_date, max_value=max_date)

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = pd.to_datetime(min_date)
    end_date = pd.to_datetime(max_date)

# Filter Data
filtered_df = df[(df['RegionName'] == selected_region) & (df['Date'] >= start_date) & (df['Date'] <= end_date)].sort_values(by='Date')
latest_date = filtered_df['Date'].max()
latest_data_rows = filtered_df[filtered_df['Date'] == latest_date]

if filtered_df.empty or latest_data_rows.empty:
    st.error(f"No data available for **{selected_region}**.")
    st.stop()

latest_data_row = latest_data_rows.iloc[0]

# --- Main Dashboard Content ---

st.title(f"HomeAgent Dashboard Home for {selected_region}")
st.markdown("This is the historic price change over time up to June 2025")

# --- VISUALISATION SECTION ---
# To get "Top Left" and "Top Middle", we MUST use columns to split the screen horizontally.
# We create 2 spaces here.
col_left, col_right = st.columns(2, gap="medium")

# 1. TOP LEFT: Time Series
with col_left:
    st.subheader("Price Trend Over Time")
    fig_price = px.line(
        filtered_df.dropna(subset=['AveragePrice']),
        x='Date',
        y='AveragePrice',
        title=f'Avg. House Price Trend',
        labels={'AveragePrice': 'Price (£)'},
        template="plotly_white"
    )
    fig_price.update_yaxes(tickprefix='£')
    fig_price.update_layout(hovermode="x unified", title_font_size=16, height=400)
    st.plotly_chart(fig_price, use_container_width=True)

# 2. TOP MIDDLE (Right): Bar Chart
with col_right:
    st.subheader("House type prices over time")
    
    house_type_prices = {
        'House Type': ['Semi-Detached', 'Terraced', 'Flat'],
        'Price': [latest_data_row['SemiDetachedPrice'], latest_data_row['TerracedPrice'], latest_data_row['FlatPrice']]
    }
    df_house_types = pd.DataFrame(house_type_prices).dropna(subset=['Price'])

    if not df_house_types.empty:
        fig_types = px.bar(
            df_house_types,
            x='House Type',
            y='Price',
            title=f'Prices by Type ({latest_date.strftime("%b %Y")})',
            labels={'Price': 'Price (£)'},
            color='House Type',
            template="plotly_white",
        )
        fig_types.update_yaxes(tickprefix='£')
        fig_types.update_layout(showlegend=False, title_font_size=16, height=400)
        st.plotly_chart(fig_types, use_container_width=True)
    else:
        st.info("House type data not available.")

# --- BOTTOM SECTION: METRICS ---
st.markdown("---")
st.subheader(f"Key Metrics for {latest_date.strftime('%B %Y')}")

# We create 5 small columns here so the metrics align in a horizontal row at the bottom
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    val = latest_data_row['AveragePrice']
    st.metric("Avg Price (All)", f"£{val:,.0f}" if not pd.isna(val) else "N/A")

with m2:
    val = latest_data_row['12m%Change']
    st.metric("Annual Change", f"{val:.1f}%" if not pd.isna(val) else "N/A", 
              delta=f"{val:.1f}%" if not pd.isna(val) else None,
              delta_color="normal" if (not pd.isna(val) and val < 0) else "inverse")

with m3:
    val = latest_data_row['FTBPrice']
    st.metric("FTB Price", f"£{val:,.0f}" if not pd.isna(val) else "N/A")

with m4:
    val = latest_data_row['FTBIndex']
    st.metric("FTB Index", f"{val:.1f}" if not pd.isna(val) else "N/A")

with m5:
    val = latest_data_row['FTB12m%Change']
    st.metric("FTB Annual Change", f"{val:.1f}%" if not pd.isna(val) else "N/A",
              delta=f"{val:.1f}%" if not pd.isna(val) else None,
              delta_color="normal" if (not pd.isna(val) and val < 0) else "inverse")
