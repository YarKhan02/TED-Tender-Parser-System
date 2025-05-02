import streamlit as st
import pandas as pd
import json

# --- Load JSON Data ---
with open("./data/tenders_with_matches.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Normalize tenders into DataFrame for filtering
tenders_data = []
for item in raw_data:
    tender = item["fields"].copy()
    tenders_data.append(tender)

df = pd.DataFrame(tenders_data)

# --- Sidebar Filters ---
st.set_page_config(page_title="TED Tender Matcher", layout="wide")
st.title("📋 TED Tender Matching Dashboard")

locations = sorted(df["Location"].unique())
project_types = sorted(df["Project type"].unique())

location_filter = st.sidebar.selectbox("Filter by Location", ["All"] + locations)
type_filter = st.sidebar.selectbox("Filter by Project Type", ["All"] + project_types)

filtered_df = df.copy()
if location_filter != "All":
    filtered_df = filtered_df[filtered_df["Location"] == location_filter]
if type_filter != "All":
    filtered_df = filtered_df[filtered_df["Project type"] == type_filter]

st.write(f"Showing {len(filtered_df)} tender(s)")

# --- Display Tender Cards ---
for idx, tender_row in filtered_df.iterrows():
    tender_details = tender_row.to_dict()
    project_name = tender_details["Project name"]
    matches = next(item["matches"] for item in raw_data if item["fields"]["Project name"] == project_name)

    with st.expander(f"{tender_details['Project name']} – {tender_details['Location']}"):
        st.markdown("### Tender Details")
        st.json(tender_details)

        st.markdown("### Top 3 Matching References")
        for i, match in enumerate(matches):
            ref = match["reference"]
            score = match["score"]
            reason = match["reason"]

            with st.container():
                st.markdown(f"**{i+1}. {ref['Project Name']}**")
                st.markdown(f"- **Location:** {ref.get('Location', 'N/A')}")
                st.markdown(f"- **Budget:** {ref.get('Budget', 'N/A')}")
                st.markdown(f"- **Type:** {ref.get('Project Type', 'N/A')}")
                st.markdown(f"- **Phases:** {ref.get('Phases', 'N/A')}")
                st.markdown(f"- **Certifications:** {ref.get('Certifications', 'None')}")
                st.markdown(f"- **Score:** `{score}`")
                st.markdown(f"- **Reason:** {reason}")
                st.markdown("---")

# --- CSV Export ---
st.sidebar.markdown("---")
if st.sidebar.button("Export Filtered Tenders"):
    csv_export = filtered_df
    st.sidebar.download_button("Download CSV", csv_export.to_csv(index=False), "filtered_tenders.csv")