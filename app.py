        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#21262d', tickprefix="$")
    )
    st.plotly_chart(fig_regions, use_container_width=True)

with chart_row_2_right:
    st.subheader("Acquisition Pipeline Funnel")
    
    # Channel distribution
    channels_df = filtered_daily['AcquisitionChannel'].value_counts().reset_index()
    channels_df.columns = ['Channel', 'Attributions']
    
    fig_channels = px.funnel(
        channels_df,
        y='Channel',
        x='Attributions',
        color='Channel',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig_channels.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig_channels, use_container_width=True)

# ---------------------------------------------------------
# DETAILED AUDIT DATA TABLE
# ---------------------------------------------------------
st.divider()
st.subheader("Customer Profiles Registry")
st.dataframe(
    filtered_customers.head(100),
    column_config={
        "Spend": st.column_config.NumberColumn("Lifetime Value", format="$%d"),
        "CustomerID": "Account Reference",
        "Status": st.column_config.TextColumn("Tier Status")
    },
    use_container_width=True
)
```eof
```text:requirements.txt
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
```eof

### How to Deploy this to Streamlit Community Cloud (Option 1):

1. **Host on GitHub:** Create a new GitHub repository (e.g., `saas-dashboard`) and push the two files (`app.py` and `requirements.txt`) directly to the root of that repository.
2. **Launch Streamlit:** Log in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
3. **Connect Your App:** Click **Deploy an App**, search for your repository name, and specify:
   * **Main file path:** `app.py`
4. **Deploy:** Hit **Deploy!** Your app will be running live on the web with a clean, responsive layout within 1-2 minutes.

Your presentation-grade Streamlit application is configured and ready! Let me know if you would like to swap out any of the synthetic metrics or charts for other business vectors.
