import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(page_title="Marketing Campaign Overview", layout="wide")

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
    st.title("Comprehensive Marketing Campaign Analysis")
    
    # KPIs Section
    st.header("Key Performance Indicators (KPIs)")
    kpis = calculate_kpis(df)
    
    # Display KPIs in a more compact format
    kpi_cols = st.columns(3)
    for i, (metric, value) in enumerate(kpis.items()):
        with kpi_cols[i % 3]:
            st.metric(metric, value)
            
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview & Insights",
        "Channel Performance",
        "Demographics Insights",
        "Time-Based Trends",
        "Revenue vs. Spend Analysis"
    ])
    
    # Define custom color sequence
    custom_colors = px.colors.qualitative.Set2
    
    # Overview & Insights Tab
    with tab1:
        st.subheader("Campaign Insights")
        
        # Campaign Comparison using a donut chart for top metrics
        top_campaigns = df.groupby('Campaign_Name').agg({
            'Conversions': 'sum',
            'Revenue_Generated': 'sum',
            'Total_Spend': 'sum'
        }).reset_index().sort_values(by='Conversions', ascending=False).head(10)
        
        fig_campaign_donut = go.Figure(go.Pie(
            labels=top_campaigns['Campaign_Name'],
            values=top_campaigns['Conversions'],
            hole=0.4,
            hoverinfo='label+percent',
            textinfo='label+value',
            marker=dict(colors=custom_colors)
        ))
        fig_campaign_donut.update_layout(title='Top 10 Campaigns by Conversions')
        st.plotly_chart(fig_campaign_donut, use_container_width=True)
    
    # Channel Performance Tab
    with tab2:
        st.subheader("Marketing Channel Comparison")
        
        # Total metrics by channel (grouped bar chart)
        channel_metrics = df.groupby('Marketing_Channel').agg({
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Conversions': 'sum',
            'Total_Spend': 'sum',
            'Revenue_Generated': 'sum'
        }).reset_index()
        
        fig_channel = px.bar(
            channel_metrics,
            x='Marketing_Channel',
            y=['Impressions', 'Conversions', 'Total_Spend'],
            title='Performance by Marketing Channel',
            barmode='group',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_channel, use_container_width=True)
        
        # Channel ROAS heatmap (interactive)
        channel_metrics['ROAS'] = channel_metrics['Revenue_Generated'] / channel_metrics['Total_Spend']
        fig_heatmap = go.Figure(go.Heatmap(
            z=channel_metrics[['Marketing_Channel', 'ROAS']].pivot_table(index='Marketing_Channel', values='ROAS').values,
            x=channel_metrics['Marketing_Channel'],
            y=['ROAS'],
            colorscale='Viridis'
        ))
        fig_heatmap.update_layout(title="Channel ROAS Heatmap")
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Demographics Insights Tab
    with tab3:
        st.subheader("Demographics Breakdown")
        
        # Gender vs Conversions (bar chart)
        gender_metrics = df.groupby('Gender').agg({
            'Conversions': 'sum',
            'Revenue_Generated': 'sum'
        }).reset_index()
        
        fig_gender = px.bar(
            gender_metrics,
            x='Gender',
            y='Conversions',
            title='Conversions by Gender',
            color='Gender',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_gender, use_container_width=True)
        
        # Age Group vs Revenue (pie chart)
        age_metrics = df.groupby('Age_Group').agg({
            'Revenue_Generated': 'sum'
        }).reset_index()
        
        fig_age = px.pie(
            age_metrics,
            values='Revenue_Generated',
            names='Age_Group',
            title='Revenue by Age Group',
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    # Time-Based Trends Tab
    with tab4:
        st.subheader("Campaign Performance Over Time")
        
        # Monthly Performance Trends (line chart)
        df_time = df.copy()
        df_time['Month'] = df_time['Start_Date'].dt.to_period('M')
        time_metrics = df_time.groupby('Month').agg({
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Conversions': 'sum',
            'Revenue_Generated': 'sum'
        }).reset_index()
        
        time_metrics['Month'] = time_metrics['Month'].astype(str).apply(lambda x: datetime.strptime(x, '%Y-%m'))
        
        fig_time = px.line(
            time_metrics,
            x='Month',
            y=['Impressions', 'Conversions', 'Revenue_Generated'],
            title='Monthly Campaign Metrics',
            markers=True,
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Revenue vs Spend Analysis Tab
    with tab5:
        st.subheader("Revenue vs Spend by Campaign")
        
        # Scatter plot showing Revenue vs Spend
        fig_revenue_spend = px.scatter(
            df,
            x='Total_Spend',
            y='Revenue_Generated',
            color='Campaign_Name',
            size='Conversions',
            title='Revenue vs Spend per Campaign',
            hover_data=['Total_Spend', 'Revenue_Generated', 'Conversions'],
            color_discrete_sequence=custom_colors
        )
        st.plotly_chart(fig_revenue_spend, use_container_width=True)

if __name__ == "__main__":
    main()
