import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="DVD Rental Analysis Project",
    page_icon="🎬",
    layout="wide"
)

@st.cache_data
def load_data():
    customer_df = pd.read_csv("Customer_behaviour_and_retention_dataset.csv")
    film_df = pd.read_csv("Film_performance_and_inventory_dataset.csv")
    store_df = pd.read_csv("Store_and_staff_performance.csv")
    geography_df = pd.read_csv("Geographic_and_market_analysis.csv")


    if 'rental_date' in customer_df.columns:
        customer_df['rental_date'] = pd.to_datetime(customer_df['rental_date'])

    return customer_df, film_df, store_df, geography_df

customer_df, film_df, store_df, geography_df = load_data()


st.sidebar.title("📊 Dashboard Controls")


page = st.sidebar.radio("Navigate", [
    "Customer Analysis",
    "Film Performance",
    "Store & Staff Performance",
    "Geographic & Market Analysis"
])


st.sidebar.subheader("Filters")


date_range = None
if 'rental_date' in customer_df.columns:
    date_range = st.sidebar.date_input(
        "Date Range",
        [customer_df['rental_date'].min(), customer_df['rental_date'].max()]
    )


category_filter = []
if 'category' in film_df.columns:
    category_filter = st.sidebar.multiselect(
        "Category",
        film_df['category'].unique()
    )


store_filter = []
if 'store' in store_df.columns:
    store_filter = st.sidebar.multiselect(
        "Store",
        store_df['store'].unique()
    )


country_filter = []
if 'country' in customer_df.columns:
    country_filter = st.sidebar.multiselect(
        "Country",
        customer_df['country'].unique()
    )

# -------------------- PAGE 1: CUSTOMER ANALYSIS --------------------
if page == "Customer Analysis":

    df = customer_df.copy()

    
    if date_range and len(date_range) == 2:
        df = df[
            (df['rental_date'] >= pd.to_datetime(date_range[0])) &
            (df['rental_date'] <= pd.to_datetime(date_range[1]))
        ]

    if country_filter:
        df = df[df['country'].isin(country_filter)]

    st.title("👥 Customer Analysis")

    
    total_customers = df['first_name'].nunique()
    total_revenue = df['total_amount_spent'].sum()
    total_rentals = df['first_name'].count()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", total_customers)
    col2.metric("Total Revenue", f"${total_revenue:,.0f}")
    col3.metric("Total Rentals", total_rentals)

    
    st.subheader("Top Customers")

    top_customers = (
        df.groupby('first_name')['total_amount_spent']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(top_customers, x='first_name', y='total_amount_spent')
    st.plotly_chart(fig, use_container_width=True)

    
    repeat = df.groupby('first_name')['total_no_of_rentals'].count()
    retention_rate = (repeat > 1).mean()
    st.metric("Retention Rate", f"{retention_rate:.2%}")

    # Churn
    if 'rental_date' in df.columns:
        last_rental = df.groupby('first_name')['rental_date'].max()
        churn_threshold = df['rental_date'].max() - pd.Timedelta(days=30)
        churn_rate = (last_rental < churn_threshold).mean()
        st.metric("Churn Risk", f"{churn_rate:.2%}")

# -------------------- PAGE 2: FILM PERFORMANCE --------------------
elif page == "Film Performance":

    df = film_df.copy()


    if category_filter:
        df = df[df['category'].isin(category_filter)]

    st.title("🎬 Film Performance")

    # KPIs
    total_revenue = df['total_rental_revenue'].sum()
    total_rentals = df['total_num_of_rental'].count()
    total_films = df['film_title'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Total Rentals", total_rentals)
    col3.metric("Total Films", total_films)

    # Top Films
    st.subheader("Top Films")

    top_films = (
        df.groupby('film_title')['total_rental_revenue']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(top_films, x='film_title', y='total_rental_revenue')
    st.plotly_chart(fig, use_container_width=True)

    
    st.subheader("Revenue by Category")

    category_rev = (
        df.groupby('category')['total_rental_revenue']
        .sum()
        .reset_index()
    )

    fig2 = px.bar(category_rev, x='category', y='total_rental_revenue')
    st.plotly_chart(fig2, use_container_width=True)

    # Inventory Risk
    st.subheader("Inventory Risk")

    inventory = df.groupby('film_title').agg({
        'total_num_of_rental': 'count',
        'inventory_count': 'mean'
    }).reset_index()

    inventory['risk_score'] = inventory['total_num_of_rental'] / inventory['inventory_count']

    st.dataframe(inventory.sort_values(by='risk_score', ascending=False).head(10))

# -------------------- PAGE 3: STORE & STAFF --------------------
elif page == "Store & Staff Performance":

    df = store_df.copy()

    
    if store_filter:
        df = df[df['store'].isin(store_filter)]

    st.title("🏪 Store & Staff Performance")

    
    total_revenue = df['total_revenue_collected'].sum()
    total_rentals_processed = df['total_rental_processed'].sum()
    total_staff = df['store_id'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Total Rental_Processed", total_rentals_processed)
    col3.metric("Total Staff", total_staff)

    
    st.subheader("Store Performance")

    store_perf = (
        df.groupby('first_name')['total_revenue_collected']
        .sum()
        .reset_index()
    )

    fig = px.bar(store_perf, x='first_name', y='total_revenue_collected')
    st.plotly_chart(fig, use_container_width=True)

    
    st.subheader("Staff Efficiency")

    staff_perf = (
        df.groupby('first_name')['total_rental_processed']
        .sum()
        .reset_index()
    )

    fig2 = px.bar(staff_perf, x='first_name', y='total_rental_processed')
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------- GEOGRAPHIC INSIGHTS --------------------
elif page == "Geographic & Market Analysis":
    df = geography_df.copy()

    if country_filter:
        df = df[df['country'].isin(country_filter)]

    if date_range and len(date_range) == 2:
        df = df[
            (df['rental_date'] >= pd.to_datetime(date_range[0])) &
            (df['rental_date'] <= pd.to_datetime(date_range[1]))
        ]

    if country_filter:
        df = df[df['country'].isin(country_filter)]

    st.title("🌍 Geography & Market Analysis")
    st.subheader("🌍 Geographic Insights")
    
    
    total_revenue = df['total_revenue'].sum()
    total_countries = df['country'].nunique()
    total_customers = df['unique_customers'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Total Countries", total_countries)
    col3.metric("Total Customers", total_customers)

    
    st.subheader("Revenue by Country (Map View)")

    country_rev = (
        df.groupby('country')['total_revenue']
        .sum()
        .reset_index()
    )

    fig_map = px.choropleth(
        country_rev,
        locations='country',
        locationmode='country names',
        color='total_revenue',
        color_continuous_scale='Blues'
    )

    st.plotly_chart(fig_map, use_container_width=True)

    
    st.subheader("Top Revenue by City")

    city_rev = (
        df.groupby('city')['total_revenue']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig_city = px.bar(
        city_rev,
        x='city',
        y='total_revenue'
    )

    st.plotly_chart(fig_city, use_container_width=True)
