import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(page_title="Marketing Campaign Analysis", layout="wide")

# Load the data
@st.cache_data
def load_data():
    df = pd.read_excel('01JBH83KFF39VMHFD1YC8QR694.xlsx')
    # Convert date columns
    df['Start_Date'] = pd.to_datetime(df['Start_Date'])
    df['End_Date'] = pd.to_datetime(df['End_Date'])
    return df

# Calculate KPIs
def calculate_kpis(df):
    total_impressions = df['Impressions'].sum()
    total_clicks = df['Clicks'].sum()
    total_conversions = df['Conversions'].sum()
    total_spend = df['Total_Spend'].sum()
    total_revenue = df['Revenue_Generated'].sum()
    
    ctr = (total_clicks / total_impressions) * 100
    conversion_rate = (total_conversions / total_clicks) * 100
    cpc = total_spend / total_clicks
    cpa = total_spend / total_conversions
    roas = total_revenue / total_spend
    
    return {
        'Total Impressions': f"{total_impressions:,.0f}",
        'Total Clicks': f"{total_clicks:,.0f}",
        'Total Conversions': f"{total_conversions:,.0f}",
        'Total Spend': f"${total_spend:,.2f}",
        'Total Revenue': f"${total_revenue:,.2f}",
        'CTR': f"{ctr:.2f}%",
        'Conversion Rate': f"{conversion_rate:.2f}%",
        'CPC': f"${cpc:.2f}",
        'CPA': f"${cpa:.2f}",
        'ROAS': f"{roas:.2f}x"
    }

def main():
    # Load data
    df = load_data()
    
    # Title
    st.title("Marketing Campaign Performance Dashboard")
    
    # KPIs Section
    st.header("Key Performance Indicators")
    kpis = calculate_kpis(df)
    
    # Display KPIs in columns
    cols = st.columns(5)
    for i, (metric, value) in enumerate(kpis.items()):
        with cols[i % 5]:
            st.metric(metric, value)
            
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Campaign Performance",
        "Channel Analysis",
        "Demographics",
        "Time Analysis"
    ])
    
    # Define a custom color sequence
    custom_colors = px.colors.qualitative.Plotly
    
    # Campaign Performance Tab
    with tab1:
        st.subheader("Campaign Performance Overview")
        
        # Campaign metrics comparison
        fig_campaign = px.bar(
            df,
            x='Campaign_Name',
            y=['Conversions', 'Clicks', 'Impressions'],
            title='Campaign Metrics Comparison',
            barmode='group',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_campaign, use_container_width=True)
        
        # Calculate Conversion Rate first
        campaign_metrics = df.copy()
        campaign_metrics['Conversion_Rate'] = (campaign_metrics['Conversions'] / campaign_metrics['Clicks']) * 100
        
        # Campaign ROAS and Conversion Rate
        fig_metrics = px.scatter(
            campaign_metrics,
            x='Total_Spend',
            y='Revenue_Generated',
            size='Conversions',
            color='Campaign_Name',
            title='Campaign ROAS Analysis',
            hover_data=['Conversion_Rate'],
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_metrics, use_container_width=True)
    
    # Channel Analysis Tab
    with tab2:
        st.subheader("Marketing Channel Performance")
        
        # Channel metrics
        channel_metrics = df.groupby('Marketing_Channel').agg({
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Conversions': 'sum',
            'Total_Spend': 'sum',
            'Revenue_Generated': 'sum'
        }).reset_index()
        
        # Calculate channel KPIs
        channel_metrics['CTR'] = (channel_metrics['Clicks'] / channel_metrics['Impressions']) * 100
        channel_metrics['Conversion_Rate'] = (channel_metrics['Conversions'] / channel_metrics['Clicks']) * 100
        channel_metrics['ROAS'] = channel_metrics['Revenue_Generated'] / channel_metrics['Total_Spend']
        
        # Channel performance visualization
        fig_channel = px.bar(
            channel_metrics,
            x='Marketing_Channel',
            y=['CTR', 'Conversion_Rate', 'ROAS'],
            title='Channel Performance Metrics',
            barmode='group',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_channel, use_container_width=True)
        
        # Channel spend vs. revenue
        fig_channel_roi = px.scatter(
            channel_metrics,
            x='Total_Spend',
            y='Revenue_Generated',
            size='Conversions',
            color='Marketing_Channel',
            title='Channel ROI Analysis',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_channel_roi, use_container_width=True)
    
    # Demographics Tab
    with tab3:
        st.subheader("Demographics Analysis")
        
        # Age group analysis
        col1, col2 = st.columns(2)
        
        with col1:
            age_metrics = df.groupby('Age_Group').agg({
                'Conversions': 'sum',
                'Revenue_Generated': 'sum'
            }).reset_index()
            
            fig_age = px.pie(
                age_metrics,
                values='Conversions',
                names='Age_Group',
                title='Conversions by Age Group',
                color_discrete_sequence=custom_colors
            )
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            gender_metrics = df.groupby('Gender').agg({
                'Conversions': 'sum',
                'Revenue_Generated': 'sum'
            }).reset_index()
            
            fig_gender = px.pie(
                gender_metrics,
                values='Revenue_Generated',
                names='Gender',
                title='Revenue by Gender',
                color_discrete_sequence=custom_colors
            )
            st.plotly_chart(fig_gender, use_container_width=True)
        
        # Location analysis
        location_metrics = df.groupby('Location').agg({
            'Conversions': 'sum',
            'Revenue_Generated': 'sum',
            'Total_Spend': 'sum'
        }).reset_index()
        
        fig_location = px.bar(
            location_metrics,
            x='Location',
            y=['Conversions', 'Revenue_Generated', 'Total_Spend'],
            title='Performance by Location',
            barmode='group',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_location, use_container_width=True)
    
    # Time Analysis Tab
    with tab4:
        st.subheader("Time-Based Analysis")
        
        # Convert dates and sort
        df_time = df.copy()
        df_time['Month'] = df_time['Start_Date'].dt.to_period('M')
        
        time_metrics = df_time.groupby('Month').agg({
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Conversions': 'sum',
            'Revenue_Generated': 'sum'
        }).reset_index()
        
        # Convert Period to datetime for plotting
        time_metrics['Month'] = time_metrics['Month'].astype(str).apply(lambda x: datetime.strptime(x, '%Y-%m'))
        
        # Time series plot
        fig_time = px.line(
            time_metrics,
            x='Month',
            y=['Impressions', 'Clicks', 'Conversions'],
            title='Campaign Metrics Over Time',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Revenue trend
        fig_revenue = px.line(
            time_metrics,
            x='Month',
            y='Revenue_Generated',
            title='Revenue Trend Over Time',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_revenue, use_container_width=True)

if __name__ == "__main__":
    main()