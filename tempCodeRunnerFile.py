import streamlit as st
import pandas as pd
import plotly.express as px
import io
from utils.style import set_style
from utils.helpers import map_area

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(page_title="Permit Dashboard", layout="wide")

# Apply styling and logos
st.markdown(set_style(), unsafe_allow_html=True)

# Centered title
st.markdown("""
    <div class='title-container'>
        <h1>📋 Permit Analysis Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN DASHBOARD FUNCTIONALITY
# ============================================
uploaded_file = st.file_uploader("Upload Permit Excel File", type=["xlsx"])

if uploaded_file:
    # DATA LOADING AND PREPROCESSING
    df_raw = pd.read_excel(uploaded_file, sheet_name="Sheet1")

    # DATE FILTERING
    if "Created Date" in df_raw.columns:
        df_raw["Created Date"] = pd.to_datetime(df_raw["Created Date"], errors='coerce')
        global_min_date = df_raw["Created Date"].min()
        global_max_date = df_raw["Created Date"].max()

        global_start_date, global_end_date = st.date_input(
            "🗕️ Select Global Date Range (applies to entire dashboard):", 
            [global_min_date, global_max_date], 
            key="global_date"
        )

        df = df_raw[
            (df_raw["Created Date"] >= pd.to_datetime(global_start_date)) & 
            (df_raw["Created Date"] <= pd.to_datetime(global_end_date))
        ].copy()

        st.markdown("### 🗕️ Date Filter for All Tables and Charts")
        st.caption("Filter results by Created Date for all permit analysis below.")
        date_filter = st.date_input(
            "Select Date Range for Result Filtering:", 
            [df["Created Date"].min(), df["Created Date"].max()], 
            key="results_filter"
        )
        filtered_df = df[
            (df["Created Date"] >= pd.to_datetime(date_filter[0])) & 
            (df["Created Date"] <= pd.to_datetime(date_filter[1]))
        ].copy()
    else:
        st.warning("❗ 'Created Date' column not found in uploaded file. Date-based filtering has been skipped.")
        df = df_raw.copy()
        filtered_df = df.copy()

    # DATA PREVIEW
    st.subheader("📊 Basic Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)

    with st.expander("📌 Summary Statistics"):
        st.write(df.describe(include='all'))

    # DEPARTMENT FILTER
    st.subheader("🔍 Filter Options")
    departments = st.multiselect(
        "Select Department(s):", 
        df["Department"].dropna().unique()
    )

    if departments:
        filtered_df = filtered_df[filtered_df["Department"].isin(departments)]

    # VISUALIZATIONS
    st.subheader("📈 Permit Counts by Department")
    dept_chart = filtered_df["Department"].value_counts().reset_index()
    dept_chart.columns = ["Department", "Permit Count"]

    fig1 = px.bar(
        dept_chart,
        x="Department",
        y="Permit Count",
        title="Permit Count by Department",
        text="Permit Count",
        color="Department",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(
        xaxis_title="Department",
        yaxis_title="Number of Permits",
        title_font_size=20,
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor='lightgrey')
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.info(f"Total Permit Count: {filtered_df.shape[0]}")

    # WORKFLOW STATE ANALYSIS
    st.subheader("📈 Workflow State Distribution")
    unique_depts = df["Department"].dropna().unique().tolist()
    selected_dept = st.selectbox(
        "Select Department for Workflow State Breakdown (optional):", 
        ["All"] + unique_depts
    )

    wf_df = filtered_df if selected_dept == "All" else filtered_df[filtered_df["Department"] == selected_dept]

    state_chart = wf_df["Workflow State"].value_counts().reset_index()
    state_chart.columns = ["Workflow State", "Count"]
    state_chart["Workflow State"] = state_chart["Workflow State"] + " (" + state_chart["Count"].astype(str) + ")"

    fig2 = px.pie(
        state_chart,
        names="Workflow State",
        values="Count",
        title=f"Workflow State Breakdown - {selected_dept if selected_dept != 'All' else 'All Departments'}",
        color_discrete_sequence=px.colors.qualitative.Set1,
        hole=0.4
    )
    fig2.update_traces(textinfo='percent+label')
    fig2.update_layout(title_font_size=20)
    st.plotly_chart(fig2, use_container_width=True)

    st.success(f"Total Records After Filter: {len(filtered_df)}")

    # AREA MAPPING AND SUMMARY TABLES
    dept_cols = ["CES ELECTRICAL", "CIVIL", "FIRE", "HSEF", "INSTRUMENTATION", "MECHANICAL", "PROCESS"]

    df["Area"] = df["Responsibility Areas"].apply(map_area)
    filtered_df["Area"] = filtered_df["Responsibility Areas"].apply(map_area)
    df["Department"] = df["Department"].str.upper()
    filtered_df["Department"] = filtered_df["Department"].str.upper()

    # CUSTOM SUMMARY TABLE
    st.subheader("📄 Customized Permit Summary Table")

    # Status classification
    df["Status"] = df["Workflow State"].apply(
        lambda x: "PENDING CLOSURE" if str(x).strip().upper() == "PENDING CLOSURE" 
        else ("EXPIRED" if str(x).strip().upper() == "EXPIRED" else None)
    )
    filtered_df["Status"] = filtered_df["Workflow State"].apply(
        lambda x: "PENDING CLOSURE" if str(x).strip().upper() == "PENDING CLOSURE" 
        else ("EXPIRED" if str(x).strip().upper() == "EXPIRED" else None)
    )

    # Create pivot tables
    pivot = pd.pivot_table(
        filtered_df,
        index="Area",
        columns="Department",
        values="Permit Number",
        aggfunc="count",
        fill_value=0
    ).reindex(columns=dept_cols, fill_value=0)

    status_counts = filtered_df[filtered_df["Status"].notna()].groupby(["Area", "Status"]).size().unstack(fill_value=0)

    # Column selection
    all_columns = dept_cols + ["EXPIRED", "PENDING CLOSURE"]
    selected_columns = st.multiselect(
        "Select Columns to Display (apart from Responsibility Areas):", 
        all_columns, 
        default=all_columns
    )

    # Final table construction
    final_table = pivot.join(status_counts, how="outer").fillna(0).astype(int).reset_index()

    for col in ["EXPIRED", "PENDING CLOSURE"]:
        if col not in final_table.columns:
            final_table[col] = 0

    total_row = final_table[dept_cols + ["EXPIRED", "PENDING CLOSURE"]].sum().to_frame().T
    total_row.insert(0, "Area", "TOTAL")
    final_table = pd.concat([final_table, total_row], ignore_index=True)

    final_table.rename(columns={"Area": "RESPONSIBILITY AREAS"}, inplace=True)
    display_table = final_table[["RESPONSIBILITY AREAS"] + selected_columns]
    st.dataframe(display_table, use_container_width=True)

    # Download button for custom summary
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        display_table.to_excel(writer, index=False, sheet_name='Custom Summary')
    output.seek(0)

    st.download_button(
        label="🗕 Download Custom Summary",
        data=output,
        file_name="Custom_Permit_Summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PLANTWISE SUMMARY
    st.subheader("🏭 Plantwise Permit Summary")
    plant_options = ["CPP", "HDPE", "HSEF", "IOP ECR", "IOP NCR", "IOP SCR", "LLDPE", "NCAU", "NCU", "IOP BAGGING", "OTHERS"]
    selected_plant = st.selectbox("Select a Plant:", plant_options)

    # Adjust logic to match full plant name exactly as in Responsibility Areas
    plant_df = filtered_df[filtered_df["Responsibility Areas"].str.contains(selected_plant, case=False, na=False)]

    if plant_df.empty:
        st.warning("No data found for selected plant")
    else:
        plantwise_summary = plant_df.groupby(["Area", "Department"]).size().reset_index(name="Permit Count")
        plantwise_summary.rename(columns={"Area": "RESPONSIBILITY AREA", "Department": "DEPARTMENT"}, inplace=True)
        total_count = plantwise_summary["Permit Count"].sum()
        total_row = pd.DataFrame([["TOTAL", "", total_count]], 
                               columns=["RESPONSIBILITY AREA", "DEPARTMENT", "Permit Count"])
        plantwise_summary = pd.concat([plantwise_summary, total_row], ignore_index=True)
        st.dataframe(plantwise_summary, use_container_width=True)

        # Download button for plantwise summary
        output_plant = io.BytesIO()
        with pd.ExcelWriter(output_plant, engine='xlsxwriter') as writer:
            plantwise_summary.to_excel(writer, index=False, sheet_name='Plantwise Summary')
        output_plant.seek(0)

        st.download_button(
            label="🗕 Download Plantwise Summary",
            data=output_plant,
            file_name="Plantwise_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("Please upload a valid Excel file to view the dashboard.")
