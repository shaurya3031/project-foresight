import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Foresight Dashboard", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        # Load risk summary
        df_risk = pd.read_csv("data/processed/risk_summary.csv")
        
        # Load forecast (Fold 1 only for latest forecast)
        df_forecast = pd.read_csv("data/processed/final_forecast.csv")
        df_forecast = df_forecast[df_forecast['fold'] == 1].copy()
        df_forecast['date'] = pd.to_datetime(df_forecast['date'])
        
        # Load history
        df_history = pd.read_csv("data/processed/analysis_ready.csv")
        df_history['date'] = pd.to_datetime(df_history['date'])
        
        return df_risk, df_forecast, df_history
    except Exception as e:
        st.error(f"Error loading data: {e}. Please ensure the pipeline (Phase 1-4) has been run successfully.")
        return None, None, None

with st.spinner("Loading Dashboard Data..."):
    df_risk, df_forecast, df_history = load_data()

if df_risk is None:
    st.stop()

# --- SIDEBAR NAV & FILTERS ---
st.sidebar.title("Foresight Navigation")
page = st.sidebar.radio("Go to", ["Executive Summary", "SKU Deep Dive"])

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")
all_categories = sorted(df_risk['category'].unique())
selected_category = st.sidebar.selectbox("Select Category", ["All Categories"] + all_categories)

# Apply category filter
if selected_category != "All Categories":
    df_risk = df_risk[df_risk['category'] == selected_category]
    if not df_forecast.empty and 'category' in df_forecast.columns:
        df_forecast = df_forecast[df_forecast['category'] == selected_category]
    if not df_history.empty and 'category' in df_history.columns:
        df_history = df_history[df_history['category'] == selected_category]

# --- PAGE 1: EXECUTIVE SUMMARY ---
if page == "Executive Summary":
    st.title("Executive Summary")
    
    if df_risk.empty:
        st.warning("No data available for the selected category.")
        st.stop()
        
    # KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    
    # 1. Latest 8-Week WAPE (calculate from forecast)
    total_abs_err = (df_forecast['units_sold'] - df_forecast['model_p50']).abs().sum()
    total_actual = df_forecast['units_sold'].abs().sum()
    overall_wape = total_abs_err / total_actual if total_actual > 0 else 0
    col1.metric("Latest 8-Week WAPE", f"{overall_wape:.2%}")
    
    # 2. Total INR at Risk (Stockout)
    stockout_risk = df_risk[df_risk['quadrant'] == 'Reorder Now']['rupee_impact'].sum()
    col2.metric("Total Value at Risk (Stockouts)", f"INR {stockout_risk:,.0f}")
    
    # 3. Total INR Tied Up (Overstock)
    overstock_risk = df_risk[df_risk['quadrant'].isin(['Markdown / Clear', 'Dead Stock'])]['rupee_impact'].sum()
    col3.metric("Capital Tied Up (Overstock)", f"INR {overstock_risk:,.0f}")
    
    st.markdown("---")
    
    # Action Required Table
    st.subheader("Action Required SKUs (At-Risk Inventory)")
    at_risk = df_risk[df_risk['quadrant'].isin(['Reorder Now', 'Markdown / Clear', 'Dead Stock'])].copy()
    at_risk = at_risk.sort_values(by='rupee_impact', ascending=False)
    
    if not at_risk.empty:
        st.dataframe(
            at_risk[['sku_id', 'category', 'quadrant', 'on_hand_units', 'lead_time_days', 'rupee_impact']].style.format({
                'rupee_impact': 'INR {:,.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No at-risk inventory detected for the selected filters!")
        
    st.markdown("---")
    
    # Quadrant Distribution
    st.subheader("Inventory Health Distribution")
    quad_counts = df_risk['quadrant'].value_counts().reset_index()
    quad_counts.columns = ['Quadrant', 'SKU Count']
    st.bar_chart(quad_counts.set_index('Quadrant'))

# --- PAGE 2: SKU DEEP DIVE ---
elif page == "SKU Deep Dive":
    st.title("SKU Deep Dive")
    
    if df_risk.empty:
        st.warning("No SKUs available for the selected category.")
        st.stop()
        
    # SKU Selector
    sku_list = sorted(df_risk['sku_id'].unique())
    selected_sku = st.sidebar.selectbox("Select SKU", sku_list)
    
    # Get SKU data
    sku_risk = df_risk[df_risk['sku_id'] == selected_sku].iloc[0]
    sku_hist = df_history[df_history['sku_id'] == selected_sku].sort_values('date')
    sku_fcst = df_forecast[df_forecast['sku_id'] == selected_sku].sort_values('date')
    
    # Display SKU KPIs
    st.subheader(f"SKU Overview: {selected_sku}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Category", sku_risk['category'])
    
    # Risk quadrant styling
    quad_color = "green"
    if sku_risk['quadrant'] == 'Reorder Now': quad_color = "red"
    elif sku_risk['quadrant'] in ['Markdown / Clear', 'Dead Stock']: quad_color = "orange"
    
    c2.markdown(f"**Risk Quadrant**<br/><span style='color:{quad_color}; font-size:24px; font-weight:bold;'>{sku_risk['quadrant']}</span>", unsafe_allow_html=True)
    c3.metric("On-Hand Inventory", f"{sku_risk['on_hand_units']:,.0f} units")
    c4.metric("Rupee Impact", f"INR {sku_risk['rupee_impact']:,.0f}")
    
    st.markdown("---")
    
    # Empty State check for forecast
    if sku_fcst.empty:
        st.warning(f"No forecast data available for {selected_sku}.")
    else:
        # Plotly Line Chart
        st.subheader("Historical Sales vs. Forecast (P10 - P90)")
        
        # Weekly aggregation for history to match forecast
        hist_weekly = sku_hist.groupby(pd.Grouper(key='date', freq='W-MON'))['units_sold'].sum().reset_index()
        
        fig = go.Figure()
        
        # History Trace
        if not hist_weekly.empty:
            fig.add_trace(go.Scatter(
                x=hist_weekly['date'], 
                y=hist_weekly['units_sold'],
                mode='lines+markers',
                name='Historical Sales',
                line=dict(color='blue')
            ))
        
        # P50 Forecast Trace
        fig.add_trace(go.Scatter(
            x=sku_fcst['date'], 
            y=sku_fcst['model_p50'],
            mode='lines+markers',
            name='Forecast (P50)',
            line=dict(color='orange', dash='dash')
        ))
        
        # P10 - P90 Confidence Band
        fig.add_trace(go.Scatter(
            x=pd.concat([sku_fcst['date'], sku_fcst['date'][::-1]]),
            y=pd.concat([sku_fcst['model_p90'], sku_fcst['model_p10'][::-1]]),
            fill='toself',
            fillcolor='rgba(255,165,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name='P10-P90 Confidence Interval'
        ))
        
        # Layout updates
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Units Sold / Forecasted",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
