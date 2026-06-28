import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------
# PAGE SETUP & STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Apex Analytics - Executive Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual design (Light Mode)
st.markdown("""
<style>
    /* Main App Background & Styling */
    .stApp {
        background-color: #f6f8fa;
        color: #24292f;
    }
    
    /* Elegant metric card styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #d0d7de;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(140, 149, 159, 0.1);
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #0969da;
    }
    
    /* Target indicators and adjustments */
    div[data-testid="stMetricLabel"] {
        color: #57606a !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 700 !important; /* Bolded Label */
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        color: #24292f !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    /* Navigation styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #d0d7de;
    }
    
    /* Headers alignment */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
        color: #24292f;
    }
    
    .main-title {
        color: #24292f;
        margin-bottom: 5px;
    }
    
    .sub-title {
        color: #57606a;
        margin-bottom: 30px;
        font-size: 16px;
    }
    
    /* Adjust dividers for light mode */
    hr {
        border-color: #d0d7de !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SYNTHETIC DATA GENERATION
# ---------------------------------------------------------
@st.cache_data
def generate_synthetic_data():
    np.random.seed(42)
    end_date = datetime.now()
    dates = [end_date - timedelta(days=x) for x in range(365)]
    dates.reverse()
    
    # Generate realistic SaaS growth metrics
    base_mrr = 120000
    mrr_growth = np.random.normal(loc=450, scale=300, size=365).cumsum()
    mrr = base_mrr + mrr_growth
    
    # Active Users (slight upward trend with weekend drops)
    base_dau = 15000
    dau_trend = np.sin(np.array(range(365)) * (2 * np.pi / 7)) * 1200  
    dau_growth = np.random.normal(loc=15, scale=50, size=365).cumsum()
    dau = (base_dau + dau_trend + dau_growth).astype(int)
    
    # Conversion Rate (%)
    conv_rate = np.random.normal(loc=2.8, scale=0.15, size=365)
    conv_rate = np.clip(conv_rate, 1.5, 5.0)
    
    # Acquisition Channels
    channels = np.random.choice(
        ['Organic Search', 'Paid Ads', 'Referral', 'Social Media', 'Direct'],
        size=365,
        p=[0.35, 0.30, 0.15, 0.10, 0.10]
    )
    
    # Assemble into DataFrames
    df_daily = pd.DataFrame({
        'Date': dates,
        'MRR': mrr,
        'DAU': dau,
        'ConversionRate': conv_rate,
        'AcquisitionChannel': channels
    })
    
    # Derived subscription tier metrics
    df_customers = pd.DataFrame({
        'CustomerID': [f"C-{i:05d}" for i in range(1, 1501)],
        'Plan': np.random.choice(['Starter', 'Growth', 'Enterprise'], size=1500, p=[0.50, 0.35, 0.15]),
        'Spend': np.random.choice([49, 149, 999], size=1500, p=[0.50, 0.35, 0.15]),
        'Status': np.random.choice(['Active', 'Churned'], size=1500, p=[0.94, 0.06]),
        'Region': np.random.choice(['North America', 'Europe', 'Asia-Pacific', 'Latin America'], size=1500, p=[0.45, 0.30, 0.15, 0.10])
    })
    
    return df_daily, df_customers

df_daily, df_customers = generate_synthetic_data()

# ---------------------------------------------------------
# SIDEBAR / FILTERS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/combo-chart.png", width=64)
    st.title("Apex Workspace")
    st.subheader("Global Filters")
    
    # Date Slider filter
    min_date = df_daily['Date'].min()
    max_date = df_daily['Date'].max()
    
    date_range = st.date_input(
        "Reporting Period",
        value=(max_date - timedelta(days=90), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Multi-select region filter
    regions = df_customers['Region'].unique().tolist()
    selected_regions = st.multiselect("Target Regions", options=regions, default=regions)
    
    st.divider()
    st.markdown("""
    **Quick Actions**
    - [Download Raw Audit Logs](#)
    - [Export Chart Graphics (SVG)](#)
    """)

# Apply filters
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df_daily['Date'].dt.date >= start_date) & (df_daily['Date'].dt.date <= end_date)
    filtered_daily = df_daily.loc[mask]
else:
    filtered_daily = df_daily

filtered_customers = df_customers[df_customers['Region'].isin(selected_regions)]

# ---------------------------------------------------------
# MAIN METRICS (KPIs)
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>Apex Executive SaaS Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Real-time operations, customer distribution, and historical health index</p>", unsafe_allow_html=True)

# Performance Cards Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

# Calculate status KPIs based on current filtered datasets
current_mrr = filtered_daily['MRR'].iloc[-1]
previous_mrr = filtered_daily['MRR'].iloc[0]
mrr_delta = ((current_mrr - previous_mrr) / previous_mrr) * 100

active_users = filtered_daily['DAU'].iloc[-1]
previous_dau = filtered_daily['DAU'].iloc[0]
dau_delta = ((active_users - previous_dau) / previous_dau) * 100

churn_rate = (len(filtered_customers[filtered_customers['Status'] == 'Churned']) / len(filtered_customers)) * 100
avg_conversion = filtered_daily['ConversionRate'].mean()

with kpi1:
    st.metric(
        label="Monthly Recurring Revenue (MRR)",
        value=f"${current_mrr:,.2f}",
        delta=f"{mrr_delta:+.2f}% vs Period Start"
    )

with kpi2:
    st.metric(
        label="Daily Active Users (DAU)",
        value=f"{active_users:,}",
        delta=f"{dau_delta:+.2f}% vs Period Start"
    )

with kpi3:
    st.metric(
        label="Customer Churn Rate",
        value=f"{churn_rate:.2f}%",
        delta="-0.41% vs Last Quarter",
        delta_color="inverse"
    )

with kpi4:
    st.metric(
        label="Average Conversion Rate",
        value=f"{avg_conversion:.2f}%",
        delta="+0.12% Target Buffer"
    )

st.write("") # Spacer

# Common layout styling object for bolder chart labels
bold_font_style = dict(
    font=dict(family="Inter, sans-serif", size=12, color="#24292f"),
    title=dict(font=dict(size=14, family="Inter, sans-serif", weight="bold"))
)

# ---------------------------------------------------------
# DATA VISUALIZATIONS SECTION
# ---------------------------------------------------------
chart_row_1_left, chart_row_1_right = st.columns([2, 1])

with chart_row_1_left:
    st.subheader("Financial Growth Track (MRR & ARR)")
    
    fig_growth = go.Figure()
    
    fig_growth.add_trace(go.Scatter(
        x=filtered_daily['Date'],
        y=filtered_daily['MRR'],
        mode='lines',
        name='MRR',
        line=dict(color='#0969da', width=3),
        fill='tozeroy',
        fillcolor='rgba(9, 105, 218, 0.08)'
    ))
    
    fig_growth.add_trace(go.Scatter(
        x=filtered_daily['Date'],
        y=filtered_daily['MRR'] * 12,
        mode='lines',
        name='Annual Run Rate (ARR Proj.)',
        line=dict(color='#1a7f37', width=1.5, dash='dash')
    ))
    
    fig_growth.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(weight="bold")),
        xaxis=dict(showgrid=True, gridcolor='#d0d7de', title=dict(font=dict(weight="bold")), tickfont=dict(weight="bold")),
        yaxis=dict(showgrid=True, gridcolor='#d0d7de', tickprefix="$", title=dict(font=dict(weight="bold")), tickfont=dict(weight="bold")),
        **bold_font_style
    )
    st.plotly_chart(fig_growth, use_container_width=True)

with chart_row_1_right:
    st.subheader("Subscription Tiers")
    
    tier_counts = filtered_customers['Plan'].value_counts().reset_index()
    tier_counts.columns = ['Plan', 'Count']
    
    fig_tiers = px.pie(
        tier_counts,
        names='Plan',
        values='Count',
        hole=0.6,
        color_discrete_sequence=['#0969da', '#1a7f37', '#8250df']
    )
    
    fig_tiers.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5, font=dict(weight="bold")),
        **bold_font_style
    )
    fig_tiers.update_traces(textfont=dict(weight="bold"))
    st.plotly_chart(fig_tiers, use_container_width=True)


st.divider()

chart_row_2_left, chart_row_2_right = st.columns([1, 1])

with chart_row_2_left:
    st.subheader("Regional Performance Index")
    
    region_data = filtered_customers.groupby('Region').agg(
        Total_Spend=('Spend', 'sum'),
        Customer_Count=('CustomerID', 'count')
    ).reset_index()
    
    fig_regions = px.bar(
        region_data,
        x='Region',
        y='Total_Spend',
        text='Customer_Count',
        labels={'Total_Spend': 'Revenue ($)', 'Customer_Count': 'Customers'},
        color='Region',
        color_discrete_sequence=px.colors.sequential.Sol
    )
    
    fig_regions.update_traces(texttemplate='%{text} Clients', textposition='outside', textfont=dict(weight="bold"))
    fig_regions.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False, title=dict(font=dict(weight="bold")), tickfont=dict(weight="bold")),
        yaxis=dict(showgrid=True, gridcolor='#d0d7de', tickprefix="$", title=dict(font=dict(weight="bold")), tickfont=dict(weight="bold")),
        **bold_font_style
    )
    st.plotly_chart(fig_regions, use_container_width=True)

with chart_row_2_right:
    st.subheader("Acquisition Pipeline Funnel")
    
    channels_df = filtered_daily['AcquisitionChannel'].value_counts().reset_index()
    channels_df.columns = ['Channel', 'Attributions']
    
    fig_channels = px.funnel(
        channels_df,
        y='Channel',
        x='Attributions',
        color='Channel',
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    fig_channels.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(title=dict(font=dict(weight="bold")), tickfont=dict(weight="bold")),
        yaxis=dict(title=dict(font=dict(weight="bold")), tickfont=dict(weight="bold")),
        **bold_font_style
    )
    fig_channels.update_
