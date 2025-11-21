import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="UK House Price Index Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Region Hierarchy Mapping ---
# Since the CSV is "flat" (doesn't say which city is in which county), 
# we define the groups manually here.

Regions = {[
    "London", "South East", "East of England", "South West", "West Midlands", "East Midlands", "North West", "Yorkshire and Humber","North East"
]
    
}

REGION_MAPPING = {
    #London doesn't have any bourghs so skip county section
    "London": [
        "London", "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley", 
        "Camden", "City of London", "City of Westminster", "Croydon", "Ealing", "Enfield", "Greenwich", 
        "Hackney", "Hammersmith and Fulham", "Haringey", "Harrow", "Havering", 
        "Hillingdon", "Hounslow", "Islington", "Kensington and Chelsea", 
        "Kingston upon Thames", "Lambeth", "Lewisham", "Merton", "Newham", 
        "Redbridge", "Richmond upon Thames", "Southwark", "Sutton", "Tower Hamlets", 
        "Waltham Forest", "Wandsworth"
    ],
    "South East":[
        "Brighton and Hove", "Buckinghamshire", "East Sussex", "Hampshire", "Isle of Wight", "Kent", "Medway", 
        "Milton Keynes", "Oxfordshire", "Portsmouth", "Reading", "Slough", "Southhampton", "Surrey", "West Berkshire",
        "West Sussex", "Windsor and Maidenhead", "Wokingham"
    ]

    "South East":[
    # Traditional Counties (These have children LADs)
    'Buckinghamshire': ['Aylesbury Vale','Chiltern','South Bucks','Wycombe'],
    'East Sussex': ['Eastbourne','Hastings','Lewes','Rother','Wealden'],
    'Hampshire': ['Basingstoke and Deane','East Hampshire','Eastleigh','Fareham','Gosport','Hart','Havant','New Forest','Rushmoor','Test Valley','Winchester'],
    'Kent': ['Ashford','Canterbury','Dartford','Dover','Gravesham','Maidstone','Sevenoaks','Shepway','Swale','Thanet','Tonbridge and Malling','Tunbridge Wells'],
    'Oxfordshire': ['Cherwell','Oxford','South Oxfordshire','Vale of White Horse','West Oxfordshire'],
    'Surrey': ['Elmbridge','Epsom and Ewell','Guildford','Mole Valley','Reigate and Banstead','Runnymede','Spelthorne','Surrey Heath','Tandridge','Waverley','Woking'],
    'West Sussex': ['Adur','Arun','Chichester','Crawley','Horsham','Mid Sussex','Worthing'],
# Unitary Authorities (These are their own Local Authority - they have no children LADs)
    'Brighton and Hove': ['Brighton and Hove'],'Isle of Wight': ['Isle of Wight'],'Medway': ['Medway'],'Milton Keynes': ['Milton Keynes'],'Portsmouth': ['Portsmouth'],'Reading': ['Reading'],
    'Slough': ['Slough'],'Southampton': ['Southampton'],'West Berkshire': ['West Berkshire'],'Windsor and Maidenhead': ['Windsor and Maidenhead'],'Wokingham': ['Wokingham'],}]
    
# ---------------------------------------East of England----------------------------------------------------------------
# Parent selection
    "South East";[
    'Bedford', 'Central Bedfordshire', 'Luton', 'Peterborough', 'Southend-on-Sea', 'Thurrock', # Unitary Authorities
    'Cambridgeshire', 'Essex', 'Hertfordshire', 'Norfolk', 'Suffolk'
    #Dropdown of counties without tiers
    'Bedford': ['Bedford'], 'Central Bedfordshire': ['Central Bedfordshire'], 'Luton': ['Luton'],
    'Peterborough': ['Peterborough'], 'Southend-on-Sea': ['Southend-on-Sea'], 'Thurrock': ['Thurrock'],
    # Counties with cities in them
    'Cambridgeshire': ['Cambridge', 'East Cambridgeshire', 'Fenland', 'Huntingdonshire', 'South Cambridgeshire'],
    'Essex': ['Braintree', 'Brentwood', 'Castle Point', 'Chelmsford', 'Colchester', 'Epping Forest', 'Harlow', 'Maldon', 'Rochford', 'Tendring', 'Uttlesford'],
    'Hertfordshire': ['Broxbourne', 'Dacorum', 'East Hertfordshire', 'Hertsmere', 'North Hertfordshire', 'St. Albans', 'Stevenage', 'Three Rivers', 'Watford', 'Welwyn Hatfield'],
    'Norfolk': ['Breckland', 'Broadland', 'Great Yarmouth', 'King\'s Lynn and West Norfolk', 'North Norfolk', 'Norwich', 'South Norfolk'],
    'Suffolk': ['Babergh', 'East Suffolk', 'Ipswich', 'Mid Suffolk', 'West Suffolk'],
# ---------------------------------------South West----------------------------------------------------------------
SOUTH_WEST_GEOGRAPHY = {
    # Traditional Counties (These have children LADs)
    'Dorset': ['Dorset',],
    'Gloucestershire': ['Cheltenham','Cotswold','Forest of Dean','Gloucester','Stroud','Tewkesbury'],
    'Somerset': ['Mendip','Sedgemoor','Somerset West and Taunton','South Somerset'],
    'Wiltshire': ['Wiltshire', # Wiltshire is a Unitary Authority covering the former County Area (excluding Swindon)],
    'Devon': ['East Devon','Exeter','Mid Devon','North Devon','South Hams','Teignbridge','Torridge','West Devon'],
    # Unitary Authorities (These are their own Local Authority)
    'Bath and North East Somerset': ['Bath and North East Somerset'],'Bournemouth, Christchurch and Poole': ['Bournemouth, Christchurch and Poole'],'Bristol, City of': ['Bristol, City of'],
    'Cornwall': ['Cornwall'],'Isles of Scilly': ['Isles of Scilly'],'North Somerset': ['North Somerset'],
    'Plymouth': ['Plymouth'],'South Gloucestershire': ['South Gloucestershire'],'Torbay': ['Torbay'],
}
# ---------------------------------------West Midlands----------------------------------------------------------------
WEST_MIDLANDS_GEOGRAPHY = {
    # Traditional Counties / Unitary Authorities that are Two-Tier
    'Staffordshire': ['Cannock Chase','East Staffordshire','Lichfield','Newcastle-under-Lyme','South Staffordshire','Stafford','Staffordshire Moorlands','Tamworth'],
    'Warwickshire': ['North Warwickshire','Nuneaton and Bedworth','Rugby','Stratford-on-Avon','Warwick'],
    'Worcestershire': ['Bromsgrove','Malvern Hills','Redditch','Worcester','Wychavon','Wyre Forest'],

    # Metropolitan County (Its LADs are Metropolitan Boroughs)
    'West Midlands': ['Birmingham',
'Coventry',
        'Dudley',
        'Sandwell',
        'Solihull',
        'Walsall',
        'Wolverhampton'
    ],

    # Single-Tier Unitary Authorities (LAD is the same as the County name)
    'Herefordshire': ['Herefordshire, County of'], # Note the full name in the HPI data
    'Shropshire': ['Shropshire'],
    'Stoke-on-Trent': ['Stoke-on-Trent'],
    'Telford and Wrekin': ['Telford and Wrekin']
}

# List of all Single-Tier Aggregates (used for logic check)
SINGLE_TIER_AUTHORITIES = [
    'Herefordshire', 'Shropshire', 'Stoke-on-Trent', 'Telford and Wrekin'
]
    ],
    # This key allows users to find ANY region if it's not in the groups above
    "All Regions (A-Z)": [] 
}

# --- 3. Data Loading ---
@st.cache_data
def load_data():
    """Loads and preprocesses the UK HPI data."""
    # Load the new CSV file
    df = pd.read_csv("UK-HPI-full-Shorted 2.csv")

    # Convert Date column
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    
    # Drop rows where Date or RegionName is missing
    df = df.dropna(subset=['Date', 'RegionName'])

    # Ensure necessary columns are numeric
    numeric_cols = [
        'AveragePrice', '12m%Change', 
        'SemiDetachedPrice', 'TerracedPrice', 'FlatPrice', 
        'FTBPrice', 'FTBIndex', 'FTB12m%Change'
    ]
    for col in numeric_cols:
        # Remove commas if present in strings before converting
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

data_load_state = st.text('Loading data...')
try:
    df = load_data()
    data_load_state.success('Data loaded successfully.')
except Exception as e:
    data_load_state.error(f"Error loading data: {e}")
    st.stop()


# --- 4. Sidebar Navigation Logic ---

st.sidebar.header("Navigation")
st.sidebar.subheader("Select Location")

# -- Step 1: Choose the Parent Region (e.g., Nottinghamshire) --
parent_options = list(REGION_MAPPING.keys())
selected_parent = st.sidebar.selectbox("1. Select Region/County:", parent_options, index=0)

# -- Step 2: Choose the City/District based on Step 1 --
if selected_parent == "All Regions (A-Z)":
    # If they want to see everything, show all unique regions from the DataFrame
    available_sub_regions = sorted(df['RegionName'].unique())
else:
    # Otherwise, grab the specific list from our dictionary
    # We also filter this list to ensure these names actually exist in the CSV to prevent errors
    mapped_names = REGION_MAPPING[selected_parent]
    available_sub_regions = [name for name in mapped_names if name in df['RegionName'].unique()]
    
    # If our mapping has names that aren't in the CSV, warn the user (optional debugging)
    if not available_sub_regions:
        st.sidebar.warning(f"No data found matching the hierarchy for {selected_parent}. Try 'All Regions'.")
        available_sub_regions = sorted(df['RegionName'].unique())

selected_region = st.sidebar.selectbox(f"2. Select City/District in {selected_parent}:", available_sub_regions)


# --- 5. Date Filtering ---
st.sidebar.subheader("Time Period")
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = pd.to_datetime(min_date)
    end_date = pd.to_datetime(max_date)


# --- 6. Data Processing for Dashboard ---
filtered_df = df[
    (df['RegionName'] == selected_region) &
    (df['Date'] >= start_date) &
    (df['Date'] <= end_date)
].sort_values(by='Date')

# Check if data exists
if filtered_df.empty:
    st.error(f"No data available for **{selected_region}** in the selected dates.")
    st.stop()

# Get Latest Data
latest_date = filtered_df['Date'].max()
latest_data_row = filtered_df[filtered_df['Date'] == latest_date].iloc[0]


# --- 7. Dashboard Layout ---

st.title(f"HomeAgent Dashboard: {selected_region}")
st.markdown(f"Historic price change for **{selected_region}** (Part of {selected_parent})")

col_viz_1, col_viz_2, col_metrics_3 = st.columns([2, 1.5, 1])

# --- CHART 1: Line Graph ---
with col_viz_1:
    st.subheader("Price Trend Over Time")
    fig_price = px.line(
        filtered_df.dropna(subset=['AveragePrice']), 
        x='Date', 
        y='AveragePrice',
        labels={'AveragePrice': 'Avg Price (£)'},
        template="plotly_white"
    )
    fig_price.update_yaxes(tickprefix='£')
    fig_price.update_layout(hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_price, use_container_width=True)

# --- CHART 2: Bar Chart (Types) ---
with col_viz_2:
    st.subheader("Prices by Property Type")
    
    # Safely getting values (handling cases where columns might be missing)
    type_data = {
        'Type': ['Semi-Detached', 'Terraced', 'Flat'],
        'Price': [
            latest_data_row.get('SemiDetachedPrice', None), 
            latest_data_row.get('TerracedPrice', None), 
            latest_data_row.get('FlatPrice', None)
        ]
    }
    df_types = pd.DataFrame(type_data).dropna()
    
    if not df_types.empty:
        fig_types = px.bar(
            df_types, x='Type', y='Price', color='Type',
            title=f"Prices as of {latest_date.strftime('%b %Y')}",
            template="plotly_white"
        )
        fig_types.update_yaxes(tickprefix='£')
        fig_types.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_types, use_container_width=True)
    else:
        st.info("Property type breakdown not available.")

# --- METRICS ---
with col_metrics_3:
    st.subheader("Key Metrics")
    st.write(f"**Data: {latest_date.strftime('%B %Y')}**")
    st.divider()

    # Helper to display metrics safely
    def safe_metric(label, val, suffix="", is_percent=False):
        if pd.isna(val):
            st.metric(label, "N/A")
        else:
            if is_percent:
                st.metric(label, f"{val:.1f}%", delta=f"{val:.1f}%", delta_color="normal" if val < 0 else "inverse")
            else:
                st.metric(label, f"£{val:,.0f}")

    safe_metric("Average Price", latest_data_row.get('AveragePrice'))
    safe_metric("12m Change", latest_data_row.get('12m%Change'), is_percent=True)
    
    st.write("### FTB Stats")
    safe_metric("FTB Price", latest_data_row.get('FTBPrice'))
    safe_metric("FTB 12m Change", latest_data_row.get('FTB12m%Change'), is_percent=True)

st.divider()
