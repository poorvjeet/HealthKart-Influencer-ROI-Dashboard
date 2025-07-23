import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="HealthKart Influencer ROI Dashboard", layout="wide")

# Helper functions
def extract_brand(campaign):
    if pd.isna(campaign):
        return None
    return str(campaign).split('_')[0]

def safe_divide(a, b):
    try:
        return a / b if b else 0
    except Exception:
        return 0

def get_uploaded_df(label, key, example_df=None):
    uploaded = st.file_uploader(label, type=["csv"], key=key)
    if uploaded:
        df = pd.read_csv(uploaded)
        st.success(f"Uploaded {label}")
        return df
    elif example_df is not None:
        if st.button(f"Load Example {label}", key=f"example_{key}"):
            st.session_state[key] = example_df
            st.success(f"Loaded example {label}")
            return example_df
    return None

# Example data for simulation
def get_example_data():
    influencers = pd.DataFrame([
        {"id": 1, "name": "John Doe", "category": "Fitness", "gender": "Male", "follower_count": 100000, "platform": "Instagram"},
        {"id": 2, "name": "Jane Smith", "category": "Wellness", "gender": "Female", "follower_count": 80000, "platform": "YouTube"},
        {"id": 3, "name": "Alex Lee", "category": "Nutrition", "gender": "Non-binary", "follower_count": 50000, "platform": "Instagram"},
    ])
    posts = pd.DataFrame([
        {"influencer_id": 1, "platform": "Instagram", "date": "2023-07-01", "url": "https://insta.com/1", "caption": "Check out this product", "reach": 5000, "likes": 100, "comments": 10},
        {"influencer_id": 2, "platform": "YouTube", "date": "2023-07-03", "url": "https://yt.com/2", "caption": "Amazing results!", "reach": 8000, "likes": 200, "comments": 20},
        {"influencer_id": 3, "platform": "Instagram", "date": "2023-07-05", "url": "https://insta.com/3", "caption": "Healthy living", "reach": 3000, "likes": 50, "comments": 5},
    ])
    tracking_data = pd.DataFrame([
        {"source": "influencer", "campaign": "MuscleBlaze_Protein_1", "influencer_id": 1, "user_id": "user1", "product": "Protein Powder", "date": "2023-07-02", "orders": 1, "revenue": 2000},
        {"source": "influencer", "campaign": "MuscleBlaze_Protein_1", "influencer_id": 1, "user_id": "user2", "product": "Protein Powder", "date": "2023-07-03", "orders": 2, "revenue": 4000},
        {"source": "influencer", "campaign": "Herbalife_Tea_2", "influencer_id": 2, "user_id": "user3", "product": "Herbal Tea", "date": "2023-07-04", "orders": 1, "revenue": 1500},
        {"source": "influencer", "campaign": "MuscleBlaze_Protein_1", "influencer_id": 3, "user_id": "user4", "product": "Protein Powder", "date": "2023-07-05", "orders": 1, "revenue": 1000},
    ])
    payouts = pd.DataFrame([
        {"influencer_id": 1, "campaign": "MuscleBlaze_Protein_1", "basis": "order", "rate": 100, "orders": 3, "total_payout": 300},
        {"influencer_id": 2, "campaign": "Herbalife_Tea_2", "basis": "order", "rate": 150, "orders": 1, "total_payout": 150},
        {"influencer_id": 3, "campaign": "MuscleBlaze_Protein_1", "basis": "order", "rate": 120, "orders": 1, "total_payout": 120},
    ])
    return influencers, posts, tracking_data, payouts

# Session state for dataframes
def get_dataframes():
    if 'influencers' not in st.session_state:
        st.session_state['influencers'], st.session_state['posts'], st.session_state['tracking_data'], st.session_state['payouts'] = get_example_data()
    return (
        st.session_state['influencers'],
        st.session_state['posts'],
        st.session_state['tracking_data'],
        st.session_state['payouts']
    )

def upload_section():
    st.header("Data Upload")
    st.write("Upload your CSV files for each dataset or load example data.")
    influencers = get_uploaded_df("Influencers", "influencers", get_example_data()[0])
    posts = get_uploaded_df("Posts", "posts", get_example_data()[1])
    tracking_data = get_uploaded_df("Tracking Data", "tracking_data", get_example_data()[2])
    payouts = get_uploaded_df("Payouts", "payouts", get_example_data()[3])
    if influencers is not None:
        st.session_state['influencers'] = influencers
    if posts is not None:
        st.session_state['posts'] = posts
    if tracking_data is not None:
        st.session_state['tracking_data'] = tracking_data
    if payouts is not None:
        st.session_state['payouts'] = payouts
    st.write("---")
    st.write("Current Data Snapshots:")
    st.write("Influencers:")
    st.dataframe(st.session_state['influencers'].head())
    st.write("Posts:")
    st.dataframe(st.session_state['posts'].head())
    st.write("Tracking Data:")
    st.dataframe(st.session_state['tracking_data'].head())
    st.write("Payouts:")
    st.dataframe(st.session_state['payouts'].head())

def preprocess_data():
    influencers, posts, tracking_data, payouts = get_dataframes()
    tracking_data = tracking_data.copy()
    payouts = payouts.copy()
    tracking_data['brand'] = tracking_data['campaign'].apply(extract_brand)
    payouts['brand'] = payouts['campaign'].apply(extract_brand)
    return influencers, posts, tracking_data, payouts

def campaign_performance_tab():
    st.header("Campaign Performance")
    influencers, posts, tracking_data, payouts = preprocess_data()
    # Filters
    brands = sorted(tracking_data['brand'].dropna().unique())
    products = sorted(tracking_data['product'].dropna().unique())
    platforms = sorted(influencers['platform'].dropna().unique())
    brand_filter = st.multiselect("Brand", brands, default=brands)
    product_filter = st.multiselect("Product", products, default=products)
    platform_filter = st.multiselect("Platform", platforms, default=platforms)
    # Filter tracking_data
    filtered = tracking_data[
        tracking_data['brand'].isin(brand_filter) &
        tracking_data['product'].isin(product_filter)
    ]
    # Get influencer platforms
    influencer_platform = influencers.set_index('id')['platform'].to_dict()
    filtered['platform'] = filtered['influencer_id'].map(influencer_platform)
    filtered = filtered[filtered['platform'].isin(platform_filter)]
    # Aggregate by campaign
    campaign_group = filtered.groupby(['campaign', 'brand', 'product']).agg(
        revenue=('revenue', 'sum'),
        orders=('orders', 'sum'),
        influencers=('influencer_id', 'nunique')
    ).reset_index()
    # Get payout per campaign
    payout_group = payouts.groupby('campaign').agg(total_payout=('total_payout', 'sum')).reset_index()
    campaign_group = campaign_group.merge(payout_group, on='campaign', how='left')
    campaign_group['ROAS'] = campaign_group.apply(lambda row: safe_divide(row['revenue'], row['total_payout']), axis=1)
    st.dataframe(campaign_group)
    st.bar_chart(campaign_group.set_index('campaign')[['revenue', 'total_payout']])
    st.write("---")
    if st.button("Export Campaign Performance to CSV"):
        csv = campaign_group.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "campaign_performance.csv", "text/csv")

def influencer_insights_tab():
    st.header("Influencer Insights")
    influencers, posts, tracking_data, payouts = preprocess_data()
    # Aggregate revenue and payout per influencer
    revenue_group = tracking_data.groupby('influencer_id').agg(total_revenue=('revenue', 'sum'), total_orders=('orders', 'sum')).reset_index()
    payout_group = payouts.groupby('influencer_id').agg(total_payout=('total_payout', 'sum')).reset_index()
    df = influencers.merge(revenue_group, left_on='id', right_on='influencer_id', how='left').merge(payout_group, left_on='id', right_on='influencer_id', how='left')
    df['ROAS'] = df.apply(lambda row: safe_divide(row['total_revenue'], row['total_payout']), axis=1)
    st.dataframe(df[["name", "category", "gender", "platform", "follower_count", "total_revenue", "total_payout", "ROAS"]])
    st.write("Top Influencers by ROAS:")
    st.dataframe(df.sort_values("ROAS", ascending=False).head(10)[["name", "ROAS"]])
    st.write("Best Personas (by category and gender):")
    persona_group = df.groupby(['category', 'gender']).agg(avg_roas=('ROAS', 'mean'), total_revenue=('total_revenue', 'sum')).reset_index()
    st.dataframe(persona_group.sort_values("avg_roas", ascending=False))
    st.write("Poor ROIs (ROAS < 1):")
    st.dataframe(df[df['ROAS'] < 1][["name", "ROAS"]])
    st.write("---")
    if st.button("Export Influencer Insights to CSV"):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "influencer_insights.csv", "text/csv")

def payout_tracking_tab():
    st.header("Payout Tracking")
    influencers, posts, tracking_data, payouts = preprocess_data()
    # Merge payouts with influencer name
    payouts = payouts.merge(influencers[['id', 'name']], left_on='influencer_id', right_on='id', how='left')
    # Get revenue for each payout row (by influencer and campaign)
    rev = tracking_data.groupby(['influencer_id', 'campaign']).agg(revenue=('revenue', 'sum')).reset_index()
    payouts = payouts.merge(rev, on=['influencer_id', 'campaign'], how='left')
    payouts['ROAS'] = payouts.apply(lambda row: safe_divide(row['revenue'], row['total_payout']), axis=1)
    st.dataframe(payouts[["name", "campaign", "basis", "rate", "orders", "total_payout", "revenue", "ROAS"]])
    st.write("---")
    if st.button("Export Payout Tracking to CSV"):
        csv = payouts.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "payout_tracking.csv", "text/csv")

def main():
    st.title("HealthKart Influencer Campaign ROI Dashboard")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Campaign Performance", "Influencer Insights", "Payout Tracking"])
    if page == "Home":
        upload_section()
    elif page == "Campaign Performance":
        campaign_performance_tab()
    elif page == "Influencer Insights":
        influencer_insights_tab()
    elif page == "Payout Tracking":
        payout_tracking_tab()

if __name__ == "__main__":
    main() 