# HealthKart Influencer Campaign ROI Dashboard

This open-source dashboard helps track and visualize the ROI of influencer campaigns for HealthKart. Built with Streamlit, it allows quick data uploads, campaign analysis, influencer insights, and payout tracking.

## Features
- **Upload/ingest data:** Upload CSVs for influencers, posts, tracking_data, and payouts.
- **Track performance:** Visualize post and influencer metrics.
- **Calculate ROI and ROAS:** See campaign and influencer-level ROAS.
- **Filter:** By brand, product, influencer type (category), and platform.
- **Insights:** Top influencers, best personas, poor ROIs.
- **Export:** Download filtered data as CSV.

## Data Model & Linking Logic

### influencers.csv
| id | name      | category | gender      | follower_count | platform   |
|----|-----------|----------|-------------|---------------|------------|
| 1  | John Doe  | Fitness  | Male        | 100000        | Instagram  |

### posts.csv
| influencer_id | platform   | date       | url           | caption                | reach | likes | comments |
|---------------|------------|------------|---------------|------------------------|-------|-------|----------|
| 1             | Instagram  | 2023-07-01 | https://...   | Check out this product | 5000  | 100   | 10       |

### tracking_data.csv
| source     | campaign                | influencer_id | user_id | product        | date       | orders | revenue |
|------------|-------------------------|--------------|---------|---------------|------------|--------|---------|
| influencer | MuscleBlaze_Protein_1   | 1            | user1   | Protein Powder | 2023-07-02 | 1      | 2000    |

### payouts.csv
| influencer_id | campaign                | basis | rate | orders | total_payout |
|---------------|-------------------------|-------|------|--------|--------------|
| 1             | MuscleBlaze_Protein_1   | order | 100  | 1      | 100          |

#### **Assumptions**
- The payouts table includes a 'campaign' column to allow campaign-level analysis.
- The brand is extracted from the campaign string by splitting by '_' and taking the first part.
- Each influencer is associated with one platform (as per the influencers table).
- The tracking_data records each order (or aggregated revenue) from a user via an influencer's campaign.
- ROAS = Revenue from campaign / Payout for campaign.
- Incremental ROAS is not baseline-adjusted; it is the direct return from the campaign.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install streamlit pandas
   ```
2. **Run the app:**
   ```bash
   streamlit run app.py
   ```
3. **Upload your data:**
   - Use the Home tab to upload CSVs for each dataset, or load example data.

## Usage
- **Home:** Upload data and see a snapshot of each table.
- **Campaign Performance:** Filter and analyze campaigns by brand, product, and platform. View revenue, payout, and ROAS.
- **Influencer Insights:** See top influencers, best personas (by category/gender), and poor ROIs.
- **Payout Tracking:** Track payouts and see ROAS for each payout row.
- **Export:** Download the current view as CSV from any tab.

## Notes
- The dashboard is designed for simulated or real data matching the described schema.
- All calculations handle missing or zero values gracefully.
- For large datasets, performance may vary depending on your machine.

---

**Open-source. Contributions welcome!** 