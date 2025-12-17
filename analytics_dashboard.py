import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date
from itertools import combinations
# -----------------------------------------------------------
# PORTFOLIO MODE (Anonymizes sensitive business data)
# -----------------------------------------------------------

PORTFOLIO_MODE = True

# -----------------------------------------------------------
# THEME: Corporate Cannabis — Emerald / Mint Dark Mode
# -----------------------------------------------------------

PRIMARY_EMERALD = "#1C7C54"
MINT = "#88D4AB"
BRIGHT_MINT = "#4CCB8A"
DARK_GRAY = "#2E2E2E"
LIGHT_GRAY = "#F5F5F5"
KPI_TITLE = "#3A3A3A"

# -----------------------------------------------------------
# FORCE TRUE DARK THEME (Overrides Streamlit's Light Mode)
# -----------------------------------------------------------

st.set_page_config(
    page_title="Reatail Sales Analytics Dashboard (Anonymized)",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------
# GLOBAL CSS OVERRIDES (Premium polish)
# -----------------------------------------------------------

st.markdown(f"""
<style>
html, body, [class*="css"] {{
    color: #E8F7F0 !important;
}}

/* Tabs styling + hover */
.stTabs [data-baseweb="tab"] {{
    font-size: 16px;
    padding: 10px 20px;
    border-radius: 8px;
    color: #E8F7F0 !important;
}}

.stTabs [data-baseweb="tab"]:hover {{
    background-color: rgba(76,203,138,0.15);
}}

.stTabs [aria-selected="true"] {{
    background-color: rgba(76,203,138,0.25) !important;
    color: {BRIGHT_MINT} !important;
    font-weight: 700 !important;
}}

/* DataFrame styling */
thead tr th {{
    color: {BRIGHT_MINT} !important;
    font-weight: bold !important;
}}
tbody tr td {{
    color: #E8F7F0 !important;
}}
tbody tr:hover {{
    background-color: #1A1A1A !important;
}}

/* Section cards */
.section-card {{
    background-color: #111111;
    padding: 25px;
    border-radius: 14px;
    margin-bottom: 22px;
    border: 1px solid rgba(76,203,138,0.15);
    box-shadow: 0 0 8px rgba(0,0,0,0.3);
}}

/* Fix wrapping + bullet formatting inside Insights box */
.section-card p,
.section-card li,
.section-card ul {{
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}}

/* Tiny badge for data snapshot */
.snapshot-pill {{
    display:inline-block;
    padding:4px 10px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,0.12);
    font-size:11px;
    margin-right:6px;
    color:#E8F7F0;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# MOBILE FIXES (PHONE-SAFE, DESKTOP-UNCHANGED)
# -----------------------------------------------------------

st.markdown("""
<style>

/* 🔥 1. Fix container padding on phones */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
        padding-top: 0.2rem !important;
    }
}

/* 🔥 2. Make ALL charts truly fluid and prevent overflow */
@media (max-width: 768px) {
    .plot-container.plotly {
        width: 100% !important;
        max-width: 100% !important;
    }
    .js-plotly-plot, .plotly-graph-div {
        width: 100% !important;
        max-width: 100% !important;
    }
}

/* 🔥 3. Prevent KPI cards from squishing */
@media (max-width: 768px) {
    .element-container:has(.section-card) {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    h2, h3, h4 {
        font-size: 0.9rem !important;
    }
}

/* 🔥 4. Ensure tables shrink properly instead of overflowing */
@media (max-width: 768px) {
    table {
        width: 100% !important;
        font-size: 0.85rem !important;
    }
}

/* 🔥 5. Prevent x-axis labels from clipping on narrow screens */
@media (max-width: 768px) {
    .xaxislayer-above text, .yaxislayer-above text {
        font-size: 0.75rem !important;
    }
}

@media (max-width: 768px) {

    /* Outer wrapper must allow scrolling */
    .chart-scroll {
        overflow-x: auto !important;
        overflow-y: hidden !important;
        -webkit-overflow-scrolling: touch !important;
        display: block !important;
        width: 100% !important;
    }

    /* Inner Plotly graph MUST have a minimum width */
    .chart-scroll .js-plotly-plot,
    .chart-scroll .plotly-graph-div,
    .chart-scroll div[data-testid="stPlotlyChart"] {
        min-width: 850px !important;   /* adjust if needed */
        width: 850px !important;
    }

    /* Prevent Streamlit from forcing 100% width */
    .chart-scroll .stPlotlyChart {
        width: auto !important;
        max-width: none !important;
    }
}



</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    button[kind="header"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# PLOTLY TEMPLATE
# -----------------------------------------------------------

plotly_template = dict(
    layout=dict(
        font=dict(family="Arial", size=13, color=BRIGHT_MINT),
        xaxis=dict(
            showgrid=False,
            linecolor=BRIGHT_MINT,
            tickfont=dict(color=BRIGHT_MINT),
        ),
        yaxis=dict(
            showgrid=False,
            linecolor=BRIGHT_MINT,
            tickfont=dict(color=BRIGHT_MINT),
        ),
        title=dict(font=dict(color=BRIGHT_MINT)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=60, b=40),
        transition=dict(duration=500),
    )
)

# 🔥 Force comma formatting for all charts
plotly_template["layout"]["yaxis"]["tickformat"] = ","


# -----------------------------------------------------------
# UNIVERSAL CHART FIXES
# -----------------------------------------------------------

def clean_axes(fig):
    """Standard formatting for consistent white text + mint axis lines."""
    fig.update_xaxes(
        tickfont=dict(color="#E8F7F0"),          # axis tick labels
        title_font=dict(color="#E8F7F0"),        # axis title
        showline=True,
        linecolor=BRIGHT_MINT,
    )
    fig.update_yaxes(
        tickfont=dict(color="#E8F7F0"),
        title_font=dict(color="#E8F7F0"),
        showline=False,
    )
    return fig


def fix_bar_labels(fig):
    """Keeps labels readable, avoids getting chopped off."""
    fig.update_traces(
        textposition="auto",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF"),
        cliponaxis=False,   # let labels hang slightly outside without being cut
    )
    return fig


def force_gradient_colors(fig):
    fig.update_layout(
        coloraxis=dict(
            colorscale=[
                [0.0, "#BDF5D0"],
                [0.33, "#4CCB8A"],
                [0.66, "#1C7C54"],
                [1.0, "#0E4930"],
            ]
        )
    )
    return fig

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------

st.markdown(
    f"""
<h1 style='color:{PRIMARY_EMERALD}; font-weight:700; margin-bottom:0px;'>
    📊 Retail Sales Analytics Dashboard (Anonymized)
</h1>
<p style='color:{BRIGHT_MINT}; font-size:16px; margin-top:5px;'>
    Executive-level insights into sales performance, customer behavior, product mix, and profitability.
</p>
""",
    unsafe_allow_html=True,
)

st.caption(
    "⚠️ All figures shown are anonymized, scaled, and for portfolio demonstration only. "
    "Visualizations reflect analytical structure and trends, not actual business financials."
)


def format_number_columns(df):
    df2 = df.copy()
    for col in df2.select_dtypes(include=[np.number]).columns:
        df2[col] = df2[col].apply(lambda x: f"{x:,}")
    return df2


# -----------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------

df = pd.read_csv("orders_clean.csv")
items = pd.read_csv("items_clean.csv")

# -----------------------------------------------------------
# HARD ANONYMIZATION MAPS (NON-REVERSIBLE)
# -----------------------------------------------------------



def anonymize_series(series, prefix):
    unique_vals = series.dropna().unique()
    mapping = {v: f"{prefix} {i+1}" for i, v in enumerate(unique_vals)}
    return series.map(mapping), mapping

if PORTFOLIO_MODE:
    items["product_name"], PRODUCT_MAP = anonymize_series(
        items["product_name"], "Product"
    )

    items["vendor_name"], VENDOR_MAP = anonymize_series(
        items["vendor_name"], "Vendor"
    )

    # Optional but recommended
    items["category"], CATEGORY_MAP = anonymize_series(
        items["category"], "Category"
    )

def synthetic_rank_values(series, low=1000, high=50000):
    ranks = series.rank(method="dense")
    scaled = np.interp(ranks, (ranks.min(), ranks.max()), (low, high))
    noise = np.random.uniform(0.85, 1.15, size=len(series))
    return (scaled * noise).round()


# -----------------------------------------------------------
# APPLY SYNTHETIC (NON-REVERSIBLE) VALUES FOR PORTFOLIO MODE
# -----------------------------------------------------------

if PORTFOLIO_MODE:
    # Orders table
    if "total" in df.columns:
        df["total"] = synthetic_rank_values(df["total"], low=20, high=200)

    # Items table
    if "net_sales" in items.columns:
        items["net_sales"] = synthetic_rank_values(items["net_sales"], low=50, high=1500)

    if "total_inventory_sold" in items.columns:
        items["total_inventory_sold"] = synthetic_rank_values(
            items["total_inventory_sold"], low=1, high=40
        )


# Fix missing or blank vendor names (Capeway Cannabis merch)
items["vendor_name"] = items["vendor_name"].fillna("").astype(str)

items.loc[
    items["vendor_name"].str.strip() == "",
    "vendor_name"
] = "Capeway Cannabis"

# Fix mis-tagged RAW / smoking accessories showing as Capeway Cannabis
mask_wrong_capeway = (
    items["vendor_name"].eq("Capeway Cannabis")
    & items["product_name"].str.contains(
        "Raw|Rolling|Tray|Chillum|Paper|Cone|Banger|High Hemp|OCB",
        case=False, na=False
    )
)

items.loc[mask_wrong_capeway, "vendor_name"] = "BMB Wholesale"

items["product_name"] = (
    items["product_name"]
        .str.replace("���", '"', regex=False)
        .str.replace("�", "", regex=False)  # generic cleanup
)


# Convert any Green Gruff product into a clearer unique category
items.loc[items["vendor_name"].str.contains("Green Gruff", case=False, na=False), "category"] = "Dog Treats"

df["order_timestamp"] = pd.to_datetime(df["order_timestamp"])
items["order_timestamp"] = pd.to_datetime(items["order_timestamp"])

df["date"] = df["order_timestamp"].dt.date
items["date"] = items["order_timestamp"].dt.date
df["hour"] = df["order_timestamp"].dt.hour
df["weekday"] = df["order_timestamp"].dt.day_name()

# Normalize customer hash key between orders/items for potential joins
if "customer_id_hash" in items.columns and "customer_hash_id" not in items.columns:
    items["customer_hash_id"] = items["customer_id_hash"]

# Normalize categories in BOTH tables
category_fix_map = {
    "Infuseds": "Flower",
    "Infused": "Flower",
    "Infuseds ": "Flower",
    "infuseds": "Flower",
    "infused": "Flower",

    "Joint": "Joints",  # <-- 🔥 the one you want
}

items["category"] = items["category"].replace(category_fix_map)
df["category"] = df.get("category", pd.Series(index=df.index)).replace(category_fix_map)


# ---------------------------
#   CATEGORY FILTER (FINAL)
# ---------------------------

st.sidebar.header("Filters")


min_date = df["date"].min()
max_date = df["date"].max()

# Date range
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    key="date_range"
)
if isinstance(date_range, (list, tuple)):
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

# Order minimum
order_min_filter = st.sidebar.slider(
    "Minimum Order Total ($)",
    min_value=0.0,
    max_value=float(round(df["total"].max(), 0)),
    value=0.0,
    step=1.0,
    key="order_min"
)

# All categories
all_categories = sorted(items["category"].dropna().unique().tolist())

# Initialize state
if "selected_categories" not in st.session_state:
    st.session_state.selected_categories = all_categories.copy()

# Reset button
if st.sidebar.button("Reset Categories"):
    st.session_state._reset_categories_flag = True
    st.rerun()

# Handle reset before multiselect draws
if st.session_state.get("_reset_categories_flag", False):
    default_categories = all_categories.copy()
    st.session_state.selected_categories = default_categories
    st.session_state._reset_categories_flag = False
else:
    default_categories = st.session_state.selected_categories

# Safe multiselect
selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=all_categories,
    key="selected_categories"
)


st.sidebar.markdown("---")
st.sidebar.caption("Filters apply across all tabs.")

# ---------------------------
# APPLY FILTERS
# ---------------------------

# If nothing selected → empty frames
if len(st.session_state.selected_categories) == 0:
    df_filtered = df.iloc[0:0]
    items_filtered = items.iloc[0:0]

else:
    # Filter items table
    items_filtered = items[
        (items["date"] >= start_date)
        & (items["date"] <= end_date)
        & (items["category"].isin(st.session_state.selected_categories))
    ]

    # Only include orders that appear in filtered items
    valid_orders = items_filtered["order_id"].unique()

    df_filtered = df[
        (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["total"] >= order_min_filter)
        & (df["order_id"].isin(valid_orders))
    ]


# -----------------------------------------------------------
# KPI CARDS
# -----------------------------------------------------------

total_revenue = df_filtered["total"].sum()
avg_order = df_filtered["total"].mean() if len(df_filtered) else 0
unique_customers = (
    df_filtered["customer_hash_id"].nunique() if len(df_filtered) else 0
)



# Avg items/order (based on items table)
if len(df_filtered) and len(items_filtered):
    total_items = items_filtered["total_inventory_sold"].sum()
    n_orders = df_filtered["order_id"].nunique()
    avg_items_order = total_items / n_orders if n_orders else 0
else:
    avg_items_order = 0

# Repeat customer rate
if len(df_filtered):
    df_date_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    visits_series = df_date_range.groupby("customer_hash_id")["order_id"].nunique()
    repeat_rate = (visits_series > 1).mean() * 100
else:
    repeat_rate = 0.0


st.markdown("<br>", unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)


def kpi_box(title, value, subtitle=None):
    st.markdown(
        f"""
    <div style="
        background-color:#ffffff;
        border-radius:12px;
        padding:18px 20px;
        border-left:6px solid {PRIMARY_EMERALD};
        box-shadow:0 1px 4px rgba(0,0,0,0.15);
        height:100%;
    ">
        <h4 style="margin:0 0 4px 0; color:{KPI_TITLE}; font-size:15px;">{title}</h4>
        <h2 style="margin:0; color:{PRIMARY_EMERALD}; font-size:24px;">{value}</h2>
        {"<p style='margin:6px 0 0 0; color:#666; font-size:12px;'>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """,
        unsafe_allow_html=True,
    )


with kpi1:
    kpi_box("Total Revenue", f"${total_revenue:,.2f}", "Across selected date range")
with kpi2:
    kpi_box("Average Order Value", f"${avg_order:,.2f}", "Per completed order")
with kpi3:
    kpi_box("Unique Customers", f"{unique_customers:,}", "Distinct customers served")
with kpi4:
    kpi_box(
        "Repeat Customer Rate",
        f"{repeat_rate:.1f}%",
        "Share of customers with 2+ visits",
    )

# Little “snapshot” line under KPIs
total_orders_selected = df_filtered["order_id"].nunique()
total_items_selected = (
    items_filtered["total_inventory_sold"].sum() if len(items_filtered) else 0
)


st.markdown(
    f"""
    <div style="margin-top:8px; margin-bottom:10px;">
        <span class="snapshot-pill">📅 {start_date} → {end_date}</span>
        <span class="snapshot-pill">🧾 {total_orders_selected:,} orders</span>
        <span class="snapshot-pill">🧺 {total_items_selected:,} items</span>
        <span class="snapshot-pill">🏷️ {len(selected_categories)} categories</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")


# -----------------------------------------------------------
# SECTION WRAPPER HELPERS
# -----------------------------------------------------------


def card_start():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------
# HELPER: compute category pairings (auto-generated bundling)
# -----------------------------------------------------------


@st.cache_data
def compute_category_pairs(items_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build category-level pairings based on items in the same order.
    Returns: DataFrame[category_a, category_b, pair_count]
    """
    if items_df.empty:
        return pd.DataFrame(columns=["category_a", "category_b", "pair_count"])

    pairs_list = []
    order_cats = (
        items_df.dropna(subset=["category"])
        .groupby("order_id")["category"]
        .apply(lambda x: sorted(set(x)))
    )

    for cats in order_cats:
        if len(cats) < 2:
            continue
        for a, b in combinations(cats, 2):
            pairs_list.append((a, b))

    if not pairs_list:
        return pd.DataFrame(columns=["category_a", "category_b", "pair_count"])

    pair_df = pd.DataFrame(pairs_list, columns=["category_a", "category_b"])
    pair_counts = (
        pair_df.value_counts()
        .reset_index(name="pair_count")
        .sort_values("pair_count", ascending=False)
    )
    return pair_counts


# -----------------------------------------------------------
# HELPER: profitability enrichment
# -----------------------------------------------------------

def enrich_with_profit(items_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds estimated margin %, profit and cost to item-level data.
    Margins are rough category-based estimates for stakeholder visibility.
    """
    if items_df.empty:
        return items_df.copy()

    margin_map = {
        # core categories
        "Flower": 0.45,
        "Edibles": 0.50,
        "Joint": 0.55,
        "Joints": 0.55,
        "Preroll Packs": 0.55,
        "Pre-Rolls": 0.55,
        "Prerolls": 0.55,
        "Disposables": 0.48,
        "Cartridges": 0.48,
        "Concentrates": 0.52,
        "Beverages": 0.40,
        "Accessories": 0.60,
    }

    out = items_df.copy()
    out["margin_pct"] = out["category"].map(margin_map).fillna(0.50)
    out["est_gross_profit"] = out["net_sales"] * out["margin_pct"]
    out["est_cost"] = out["net_sales"] - out["est_gross_profit"]
    return out


# -----------------------------------------------------------
# TABS
# -----------------------------------------------------------

tab_overview, tab_products, tab_bundles, tab_customers, tab_time, tab_profit, tab_insights = st.tabs(
    [
        "📍 Overview",
        "🧺 Products",
        "🔗 Bundles & Pairings",
        "👥 Customers",
        "⏱ Time & Patterns",
        "💵 Profitability",
        "💡 Insights",
    ]
)


# -----------------------------------------------------------
# TAB 1 — OVERVIEW
# -----------------------------------------------------------

with tab_overview:

    # Executive summary
    card_start()
    st.markdown(
        f"<h3 style='color:{BRIGHT_MINT};'>🧾 Executive Summary</h3>",
        unsafe_allow_html=True,
    )

    if len(df_filtered) and len(items_filtered):
        total_orders = df_filtered["order_id"].nunique()


        # Category revenue
        category_revenue = items_filtered.groupby("category")["net_sales"].sum()
        if not category_revenue.empty:
            top_category = "Category Segment A"
            top_share = category_revenue.max() / category_revenue.sum() * 100
        else:
            top_category, top_share = "N/A", 0.0

        # Category logic
        if len(category_revenue) == 1:
            category_sentence = (
                f"All sales in the selected filters come from the <b>{top_category}</b> category."
            )
        else:
            category_sentence = (
                f"<b>{top_category}</b> is currently the leading category, "
                f"accounting for <b>{top_share:.1f}%</b> of category-level revenue."
            )

        # Repeat rates
        visits_filtered = df_filtered.groupby("customer_hash_id")["order_id"].nunique()
        repeat_rate_filtered = (visits_filtered > 1).mean() * 100 if len(visits_filtered) else 0

        df_date_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        visits_global = df_date_range.groupby("customer_hash_id")["order_id"].nunique()
        repeat_rate_global = (visits_global > 1).mean() * 100 if len(visits_global) else 0

        # 🔥 NEW LOGIC — ONLY SHOW COMPARISON IF USER SELECTED A SUBSET
        all_selected = set(selected_categories) == set(all_categories)

        if all_selected:
            repeat_sentence = (
                f"Roughly <b>{repeat_rate_global:.1f}%</b> of customers are repeat buyers."
            )
        else:
            repeat_sentence = (
                f"Roughly <b>{repeat_rate_filtered:.1f}%</b> of customers who purchased within these filters "
                f"are repeat buyers, while the overall repeat rate across all customers in this date range "
                f"is <b>{repeat_rate_global:.1f}%</b>."
            )

        # Final summary
        st.markdown(
            f"""
            <div style="max-width:1100px; line-height:1.6; font-size:15px;">
                This view summarizes <b>{total_orders:,}</b> orders over the selected period. 
                Customers spend an average of <b>${avg_order:,.2f}</b> per visit and purchase about 
                <b>{avg_items_order:.2f}</b> items per basket. 
                {repeat_sentence} {category_sentence}
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            "<p style='font-size:14px;'>Adjust filters to see executive KPIs and narrative summary.</p>",
            unsafe_allow_html=True,
        )

    card_end()





    # Revenue Over Time
    card_start()
    st.markdown(
        f"<h3 style='color:{BRIGHT_MINT};'>📅 Revenue Over Time</h3>",
        unsafe_allow_html=True,
    )

    if len(df_filtered):
        daily_revenue = (
            df_filtered.groupby("date")["total"].sum().reset_index()
        )

        fig = px.line(
            daily_revenue,
            x="date",
            y="total",
            title="Daily Revenue Trend",
            labels={"date": "Date", "total": "Revenue ($)"},
        )

        fig.update_traces(
            line=dict(width=4, color=BRIGHT_MINT),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
        )

        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linecolor=BRIGHT_MINT,
            tickfont=dict(color=BRIGHT_MINT, size=11),
            tickformat="%b %d",
            showticklabels=True,
        )
        fig.update_yaxes(
            showgrid=False,
            showline=True,
            linecolor=BRIGHT_MINT,
            tickfont=dict(color=BRIGHT_MINT, size=11),
        )

        # Disable ALL zoom / scroll / drag interactions
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        
        fig.update_layout(
            dragmode=False,
            modebar=dict(
                remove=[
                    "zoom",
                    "pan",
                    "select",
                    "lasso",
                    "zoomIn",
                    "zoomOut",
                    "autoScale",
                    "resetScale"
                ]
            )
        )
        
        fig.update_layout(template=plotly_template, height=360)

        fig = clean_axes(fig)
        with st.container():
            st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("No data for selected filters.")
    card_end()


# -----------------------------------------------------------
# TAB 2 — PRODUCTS (FULLY POLISHED)
# -----------------------------------------------------------

with tab_products:

    card_start()
    st.markdown(
        f"<h3 style='color:{BRIGHT_MINT};'>🧺 Product Performance</h3>",
        unsafe_allow_html=True,
    )

    if len(items_filtered):

        drill = st.selectbox(
            "Drill down by category",
            options=["All"]
            + sorted(items_filtered["category"].dropna().unique().tolist()),
        )

        if drill == "All":
            items_drill = items_filtered.copy()
        else:
            items_drill = items_filtered[items_filtered["category"] == drill].copy()

        if len(items_drill):

            # Group + clean formatting
            top_products = (
                items_drill.groupby("product_name")["net_sales"]
                .sum()
                .reset_index()
                .sort_values("net_sales", ascending=False)
                .head(15)
            )

            # Create clean numeric + label columns
            top_products["Net Sales ($)"] = top_products["net_sales"].round().astype(int)
            top_products["Product Name"] = top_products["product_name"]

            # Shortened name for chart only
            top_products["Short Name"] = top_products["Product Name"].apply(
                lambda x: x if len(x) <= 40 else x[:40] + "..."
            )

            # 🔥 Correct descending barrel order
            top_products = top_products.sort_values("Net Sales ($)", ascending=False)

            # Dynamic chart height
            chart_height = max(450, len(top_products) * 45)

            # --- Clean, professional bar chart ---

            # Choose a single clean green (or switch to teal/blue here)
            BAR_COLOR = PRIMARY_EMERALD  # or "#4CB3D4" for teal

            fig_prod = px.bar(
                top_products,
                x="Net Sales ($)",
                y="Product Name",
                orientation="h",
                title=f"Top Products — {drill}",
            )

            # Make all bars the same color
            fig_prod.update_traces(
                marker_color=BAR_COLOR,
                text=top_products["Net Sales ($)"],
                texttemplate="$%{text:,.0f}",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Net Sales: $%{x:,.2f}<extra></extra>",
            )

            # Reverse Y so highest is at the top
            fig_prod.update_yaxes(
                autorange="reversed",
                title="Product",
                tickfont=dict(color=BRIGHT_MINT),
            )

            fig_prod.update_xaxes(
                title="Net Sales ($)",
                tickfont=dict(color=BRIGHT_MINT),
            )


            # Disable ALL interaction (tablet-safe)
            fig_prod.update_layout(
                dragmode=False,                  # no dragging
                modebar=dict(                    # remove all zoom tools
                    remove=[
                        "zoom",
                        "pan",
                        "select",
                        "lasso",
                        "zoomIn",
                        "zoomOut",
                        "autoScale",
                        "resetScale"
                    ]
                ),
                template=plotly_template,
                height=450,
                showlegend=False,
                margin=dict(l=0, r=20, t=80, b=30)
            )


            fig_prod = clean_axes(fig_prod)  # still keeps your style helpers
            with st.container():
                st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
                st.plotly_chart(fig_prod, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.info("No product data for selected category.")

    else:
        st.info("No product data.")
    card_end()

    # SEARCH TABLE
    card_start()
    st.markdown("#### 🔍 Search Products")

    if len(items_filtered):
        query = st.text_input("Search by product or vendor:")

        table = items_filtered[
            ["product_name", "vendor_name", "category", "net_sales", "total_inventory_sold"]
        ].copy()

        table = table.rename(
            columns={
                "product_name": "Product Name",
                "vendor_name": "Vendor",
                "category": "Category",
                "net_sales": "Net Sales ($)",
                "total_inventory_sold": "Units Sold",
            }
        )

        # Proper numeric formatting
        table["Net Sales ($)"] = table["Net Sales ($)"].round().astype(int)

        if query:
            mask = (
                table["Product Name"].str.contains(query, case=False, na=False)
                | table["Vendor"].str.contains(query, case=False, na=False)
            )
            table = table[mask]

        table = table.groupby(["Product Name", "Vendor", "Category"]).agg(
            **{
                "Net Sales ($)": ("Net Sales ($)", "sum"),
                "Units Sold": ("Units Sold", "sum"),
            }
        ).reset_index()

        table = table.sort_values("Net Sales ($)", ascending=False)

        # Add formatting ($XX,XXX)
        table["Net Sales ($)"] = table["Net Sales ($)"].apply(lambda x: f"${x:,}")
        table["Units Sold"] = table["Units Sold"].apply(lambda x: f"{x:,}")

        # Right-align numeric columns
        st.dataframe(
            table.style.set_properties(
                **{"text-align": "right"},
                subset=["Net Sales ($)", "Units Sold"],
            ),
            use_container_width=True,
            hide_index=True,
            height=450,
        )

    else:
        st.info("No product data for current filters.")
    card_end()

# -----------------------------------------------------------
# TAB 3 — BUNDLES & PAIRINGS (FINAL POLISHED VERSION)
# -----------------------------------------------------------

with tab_bundles:
    card_start()
    st.markdown(
        f"<h3 style='color:{BRIGHT_MINT};'>🔗 Bundles & Category Pairings</h3>",
        unsafe_allow_html=True,
    )

    if len(items_filtered):

        pair_df = compute_category_pairs(items_filtered[["order_id", "category"]])

        if not pair_df.empty:

            # --- Clean Top Pairs dataframe ---
            top_pairs = pair_df.head(10).copy()
            top_pairs["Category Pair"] = (
                top_pairs["category_a"] + " + " + top_pairs["category_b"]
            )

            display_pairs = top_pairs.copy()
            display_pairs["pair_count"] = display_pairs["pair_count"].apply(
                lambda x: f"{int(x):,}"
            )

            # ----------------------------------------
            # FORCE CONSISTENT HEIGHT FOR SPLIT LAYOUT
            # ----------------------------------------
            TABLE_CHART_HEIGHT = 385  # <-- You can change this, but this matches your screenshot perfectly

            c1, c2 = st.columns([1.05, 1.95])

            # ----------- TABLE -----------
            with c1:
                st.markdown("**Top 10 Category Pairs (by order frequency)**")
                st.dataframe(
                    display_pairs.rename(
                        columns={
                            "category_a": "Category A",
                            "category_b": "Category B",
                            "pair_count": "Number of Orders",
                        }
                    )[["Category A", "Category B", "Number of Orders"]],
                    use_container_width=True,
                    hide_index=True,
                    height=TABLE_CHART_HEIGHT,   # 🔥 forced height
                )

            # ----------- CHART -----------
            with c2:
                BAR_COLOR = PRIMARY_EMERALD

                top_pairs_sorted = top_pairs.sort_values("pair_count", ascending=False)

                fig_pairs = px.bar(
                    top_pairs_sorted,
                    x="pair_count",
                    y="Category Pair",
                    orientation="h",
                    title="Most Common Bundles",
                    labels={
                        "pair_count": "Number of Orders",
                        "Category Pair": "Category Pair",
                    },
                )

                fig_pairs.update_traces(
                    marker_color=BAR_COLOR,
                    text=top_pairs_sorted["pair_count"],
                    texttemplate="%{text:,}",
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>Orders: %{x:,}<extra></extra>",
                )

                fig_pairs.update_yaxes(
                    autorange="reversed",
                    tickfont=dict(color=BRIGHT_MINT),
                )
                fig_pairs.update_xaxes(
                    tickfont=dict(color=BRIGHT_MINT),
                    title="Number of Orders",
                )

                fig_pairs.update_layout(
                    template=plotly_template,
                    height=470,  # 🔥 MATCH THE TABLE
                    margin=dict(l=0, r=20, t=70, b=10),
                    showlegend=False,
                )

                # Remove zoom tools (fixes your “bug out” issue)
                fig_pairs.update_layout(
                    dragmode=False
                )

                fig_pairs = clean_axes(fig_pairs)
                with st.container():
                    st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
                    st.plotly_chart(
                        fig_pairs,
                        use_container_width=True,
                        config={"displayModeBar": False},  # 🔥 NO ZOOM BAR
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
            # ---- Divider matching Overview tab ----
            st.markdown("<hr style='opacity:0.25;'>", unsafe_allow_html=True)

            # ----------- CENTERED INSIGHT BOX -----------
            top_row = top_pairs_sorted.iloc[0]
            pair_count_value = int(top_row["pair_count"])

            st.markdown(
                f"""
                <div style="
                    background-color:#111111;
                    padding:20px;
                    border-radius:10px;
                    border:1px solid rgba(255,255,255,0.08);
                    max-width:1000px;
                    margin-left:auto;
                    margin-right:auto;
                    text-align:center;
                    line-height:1.6;
                ">
                    <p style="font-size:15px; color:#E8F7F0;">
                        Customers show strong bundling behavior. The most frequent pairing is
                        <b>{top_row['category_a']} + {top_row['category_b']}</b>,
                        appearing together in <b>{pair_count_value:,}</b> orders during the
                        selected period. These represent ideal opportunities for curated bundle
                        deals and high-visibility cross-sell prompts at checkout.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            st.info("Not enough category diversity to compute bundles for these filters.")

    else:
        st.info("No item data for selected filters.")

    card_end()



# -----------------------------------------------------------
# TAB 4 — CUSTOMERS (FINAL FIXED VERSION)
# -----------------------------------------------------------

with tab_customers:

    # GLOBAL repeat rate (correct!)
    global_visits = df.groupby("customer_hash_id")["order_id"].nunique()
    global_repeat_rate = (global_visits > 1).mean() * 100

    card_start()
    st.markdown(
        f"<h3 style='color:{BRIGHT_MINT};'>👥 Customer Behavior</h3>",
        unsafe_allow_html=True,
    )

    if len(df_filtered):

        # FILTERED metrics
        visits = df_filtered.groupby("customer_hash_id")["order_id"].nunique()
        avg_visits = visits.mean()
        customer_count = len(visits)

        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("Repeat Customer Rate", f"{global_repeat_rate:.1f}%")
        c2.metric("Average Visits per Customer", f"{avg_visits:.2f}")
        c3.metric("Customer Count", f"{customer_count:,}")

        # ---- VISIT DISTRIBUTION ----
        visit_counts = visits.value_counts().sort_index()

        # Bin everything >10 into one bucket
        over_10 = visit_counts[visit_counts.index > 10].sum()
        under_11 = visit_counts[visit_counts.index <= 10].copy()

        # Build display list
        labels = [str(i) for i in under_11.index]
        values = list(under_11.values)

        # Add "10+" bucket if needed
        if over_10 > 0:
            labels.append("10+")
            values.append(over_10)

        # Build dataframe
        df_plot = pd.DataFrame({
            "visits": pd.Categorical(labels, categories=labels, ordered=True),
            "count": values,
        })

        fig_visits = px.bar(
            df_plot,
            x="visits",
            y="count",
            title="Visit Frequency Distribution (1–10+ Visits)",
            labels={
                "visits": "Number of Visits",
                "count": "Number of Customers",
            },
        )

        fig_visits.update_traces(
            marker_color=PRIMARY_EMERALD,
            hovertemplate="<b>%{x}</b> visits<br>Customers: %{y:,}<extra></extra>",
        )

        fig_visits.update_xaxes(
            type="category",              # 🔥 FORCE CATEGORICAL AXIS
            tickfont=dict(color=BRIGHT_MINT),
            title="Number of Visits",
        )

        fig_visits.update_yaxes(
            tickfont=dict(color=BRIGHT_MINT),
            title="Number of Customers",
        )

        fig_visits.update_layout(
            template=plotly_template,
            height=420,
            dragmode=False,
            modebar_remove=[
                'zoom', 'pan', 'select', 'lasso', 'zoomin', 'zoomout',
                'autoscale', 'resetscale'
            ],
            margin=dict(l=0, r=0, t=60, b=40),
        )

        fig_visits = clean_axes(fig_visits)
        with st.container():
            st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
            st.plotly_chart(fig_visits, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.caption("Customers with more than 10 visits are grouped into the ‘10+’ bucket for readability.")


    else:
        st.info("No customer data.")
    card_end()

    # ---------------------------------------------------
    # TOP CUSTOMERS BY SPEND — FORMATTED WITH NO DECIMALS
    # ---------------------------------------------------

    card_start()
    st.markdown("#### 🥇 Top 20 Customers by Spend")

    if len(df_filtered):

        cs = (
            df_filtered.groupby("customer_hash_id")
            .agg(
                total_spend=("total", "sum"),
                visits=("order_id", "nunique"),
            )
            .reset_index()
        )
        cs["avg_ticket"] = cs["total_spend"] / cs["visits"]

        cs = cs.sort_values("total_spend", ascending=False).head(20).reset_index(drop=True)

        # Clean display names ("Customer #1", etc.)
        cs["Customer"] = ["Customer #" + str(i + 1) for i in cs.index]

        # ---- FORMAT MONEY COLUMNS (NO DECIMALS EVER) ----
        def fmt_whole_dollars(x):
            return f"${int(round(x)):,}"

        cs["Total Spend ($)"] = cs["total_spend"].apply(fmt_whole_dollars)
        cs["Average Ticket ($)"] = cs["avg_ticket"].apply(fmt_whole_dollars)

        # ---- REORDER COLUMNS ----
        cs["Number of Visits"] = cs["visits"]
        cs = cs[["Customer", "Number of Visits", "Total Spend ($)", "Average Ticket ($)"]]

        st.dataframe(cs, use_container_width=True, hide_index=True)

    else:
        st.info("No customers to display.")

    card_end()


# -----------------------------------------------------------
# TAB 5 — TIME PATTERNS (FULLY UPDATED + MATCHED STYLE)
# -----------------------------------------------------------

with tab_time:

    card_start()
    st.markdown(
        f"<h3 style='color:{BRIGHT_MINT};'>⏱ Ordering Patterns</h3>",
        unsafe_allow_html=True,
    )

    if len(df_filtered):

        # ================= REVENUE BY DAY OF WEEK =================
        dow = (
            df_filtered.groupby("weekday")["total"]
            .sum()
            .reindex(
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
            )
            .reset_index()
        )

        fig_dow = px.bar(
            dow,
            x="weekday",
            y="total",
            title="Revenue by Day of Week",
            labels={
                "weekday": "Day of Week",
                "total": "Revenue ($)",
            },
        )

        fig_dow.update_traces(
            marker_color=PRIMARY_EMERALD,
            text=[f"${v:,.0f}" for v in dow["total"]],
            textposition="inside",
            insidetextfont=dict(color="white"),
            hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
        )

        fig_dow.update_xaxes(tickfont=dict(color=BRIGHT_MINT))
        fig_dow.update_yaxes(tickfont=dict(color=BRIGHT_MINT))

        fig_dow.update_layout(
            template=plotly_template,
            height=360,
            dragmode=False,
            modebar_remove=[
                "zoom","pan","select","lasso","zoomin","zoomout",
                "autoscale","resetscale"
            ],
            margin=dict(l=0, r=0, t=60, b=40),
        )

        fig_dow = clean_axes(fig_dow)

        with st.container():
            st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
            st.plotly_chart(fig_dow, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        # ================= AVERAGE ORDER VALUE BY DAY ================
        dow_aov = (
            df_filtered.groupby("weekday")["total"]
            .mean()
            .reindex(
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
            )
            .reset_index()
        )

        fig_aov = px.line(
            dow_aov,
            x="weekday",
            y="total",
            markers=True,
            title="Average Order Value by Day of Week",
            labels={
                "weekday": "Day of Week",
                "total": "Average Order Value ($)",
            },
        )

        fig_aov.update_traces(
            line=dict(width=3, color=BRIGHT_MINT),
            hovertemplate="<b>%{x}</b><br>AOV: $%{y:,.0f}<extra></extra>",
        )

        fig_aov.update_xaxes(
            title="Day of Week",
            tickfont=dict(color=BRIGHT_MINT),
            range=[-0.05, 6.05],   # even framing
            fixedrange=True        # disables zoom/drag on X axis
        )

        fig_aov.update_yaxes(
            title="Average Order Value ($)",
            tickfont=dict(color=BRIGHT_MINT),
            fixedrange=True        # disables zoom/drag on Y axis too
        )

        fig_aov.update_layout(
            template=plotly_template,
            height=320,
            dragmode=False,
            modebar_remove=[
                "zoom", "pan", "select", "lasso",
                "zoomin", "zoomout", "autoscale", "resetscale"
            ],
            margin=dict(l=0, r=0, t=60, b=40),
        )


        fig_aov = clean_axes(fig_aov)
        with st.container():
            st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
            st.plotly_chart(fig_aov, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("No time pattern data.")
    card_end()


    # -----------------------------------------------------------
    # CLEAN HEATMAP — FIXED COLORS, NO ZOOM, NO FAKE HOVER
    # -----------------------------------------------------------

    card_start()
    if len(df_filtered):

        hour_dow = (
            df_filtered.groupby(["weekday", "hour"])["total"]
            .sum()
            .reset_index()
        )

        # Format hour label
        def format_hour(h):
            return (
                "12 AM" if h == 0 else
                f"{h} AM" if h < 12 else
                "12 PM" if h == 12 else
                f"{h-12} PM"
            )

        hour_dow["hour_label"] = hour_dow["hour"].apply(format_hour)

        # Pivot
        heat = hour_dow.pivot(index="hour_label", columns="weekday", values="total")

        # Remove rows with all-zero values
        heat = heat[heat.sum(axis=1) > 0]

        # Correct ordering
        heat = heat.reindex(
            ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            axis=1
        )

        hour_order = [
            "12 AM","1 AM","2 AM","3 AM","4 AM","5 AM",
            "6 AM","7 AM","8 AM","9 AM","10 AM","11 AM",
            "12 PM","1 PM","2 PM","3 PM","4 PM","5 PM",
            "6 PM","7 PM","8 PM","9 PM","10 PM","11 PM",
        ]
        heat = heat.reindex([h for h in hour_order if h in heat.index])

        # Replace 0 with NaN so hover doesn't show fake values
        heat = heat.replace(0, np.nan)

        # Draw heatmap
        fig_heat = px.imshow(
            heat,
            aspect="auto",
            color_continuous_scale=[
                "#dff7e6",  # light mint
                "#74d2a2",  # medium mint
                PRIMARY_EMERALD  # dark emerald
            ],
            title="Revenue Heatmap (Hour of Day × Day of Week)",
            labels={
                "x": "Day of Week",
                "y": "Hour of Day",
                "color": "Revenue ($)",
            },
        )

        fig_heat.update_traces(
            hovertemplate="<b>%{y}</b> on <b>%{x}</b><br>Revenue: $%{z:,.0f}<extra></extra>",
            hoverongaps=False,  # <-- hides NaN hover!
        )

        fig_heat.update_layout(
            template=plotly_template,
            height=420,
            dragmode=False,
            modebar_remove=[
                'zoom','pan','select','lasso','zoomin','zoomout',
                'autoscale','resetscale'
            ],
            margin=dict(l=0, r=0, t=60, b=40),
        )

        fig_heat = clean_axes(fig_heat)
        with st.container():
            st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
            st.plotly_chart(fig_heat, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        # ---------------------------------------
        # WEEKDAY VS WEEKEND SUMMARY — KPIs
        # ---------------------------------------
        st.markdown("---")
        st.markdown("#### Weekday vs Weekend Summary")

        def block_summary(mask, label):
            block = df_filtered[mask]
            orders = block["order_id"].nunique()
            aov = block["total"].mean() if len(block) else 0
            return label, orders, aov

        mon_thu = df_filtered["weekday"].isin(["Monday","Tuesday","Wednesday","Thursday"])
        fri_sat = df_filtered["weekday"].isin(["Friday","Saturday"])
        sunday = df_filtered["weekday"].isin(["Sunday"])

        summaries = [
            block_summary(mon_thu, "Mon–Thu (Weekdays)"),
            block_summary(fri_sat, "Fri–Sat (Stock-Up Days)"),
            block_summary(sunday, "Sunday"),
        ]

        c1, c2, c3 = st.columns(3)
        for col, (label, orders, aov) in zip([c1, c2, c3], summaries):
            with col:
                st.metric(label, f"{orders:,} orders", f"AOV ${aov:,.0f}")

    card_end()


# -----------------------------------------------------------
# TAB 6 — PROFITABILITY (CLEAN + CONSISTENT + UPDATED)
# -----------------------------------------------------------

with tab_profit:
    card_start()
    st.markdown(
        f"<h3 style='color:{BRIGHT_MINT};'>💵 Profitability Overview</h3>",
        unsafe_allow_html=True,
    )

    if len(items_filtered):
        # Use existing helper (keeps your margin model exactly the same)
        items_profit = enrich_with_profit(items_filtered)

        # -----------------------------
        # HIGH-LEVEL KPIs (cleaned)
        # -----------------------------
        # Align profitability with KPI card totals
        total_net_sales = df_filtered["total"].sum()

        total_est_profit = items_profit["est_gross_profit"].sum()

        overall_margin = (
            (total_est_profit / total_net_sales) * 100
            if total_net_sales > 0 else 0
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Net Sales (Tracked Items)", f"${total_net_sales:,.2f}")
        c2.metric("Estimated Gross Profit", f"${total_est_profit:,.2f}")
        c3.metric("Estimated Gross Margin", f"{overall_margin:,.1f}%")

        st.caption("Margins are approximate category assumptions for internal visibility.")
        st.markdown("---")

        # -----------------------------------------------------------
        # CATEGORY PROFITABILITY (CLEAN + FIXED)
        # -----------------------------------------------------------

        # 1. NUMERIC version for calculations + bar chart
        cat_profit = (
            items_profit.groupby("category")
            .agg(
                net_sales=("net_sales", "sum"),
                profit=("est_gross_profit", "sum"),
                units=("total_inventory_sold", "sum"),
                orders=("order_id", "nunique"),
            )
            .reset_index()
        )

        cat_profit["margin_pct"] = (cat_profit["profit"] / cat_profit["net_sales"]) * 100
        cat_profit["profit_per_unit"] = cat_profit["profit"] / cat_profit["units"]
        cat_profit["profit_per_order"] = cat_profit["profit"] / cat_profit["orders"]

        # Keep a clean numeric copy for charts
        cat_profit_chart = cat_profit.copy()

        # 2. FORMATTED version for table
        cat_profit_display = cat_profit.rename(
            columns={
                "category": "Category",
                "net_sales": "Net Sales ($)",
                "profit": "Estimated Profit ($)",
                "units": "Units Sold",
                "orders": "Orders",
                "margin_pct": "Margin (%)",
                "profit_per_unit": "Profit per Unit ($)",
                "profit_per_order": "Profit per Order ($)",
            }
        )

        # Reorder columns for table
        cat_profit_display = cat_profit_display[
            [
                "Category",
                "Orders",
                "Units Sold",
                "Profit per Unit ($)",
                "Profit per Order ($)",
                "Net Sales ($)",
                "Estimated Profit ($)",
                "Margin (%)",
            ]
        ]

        # Sort by estimated profit
        cat_profit_display = cat_profit_display.sort_values(
            "Estimated Profit ($)", ascending=False
        )

        # -----------------------------
        # FORMAT MONEY COLUMNS
        # -----------------------------
        money_cols = [
            "Profit per Unit ($)",
            "Profit per Order ($)",
            "Net Sales ($)",
            "Estimated Profit ($)",
        ]

        for col in money_cols:
            cat_profit_display[col] = cat_profit_display[col].apply(
                lambda x: f"${x:,.0f}"
            )

        # Margin formatting
        cat_profit_display["Margin (%)"] = cat_profit_display["Margin (%)"].apply(
            lambda x: f"{x:,.1f}%"
        )

        # -----------------------------
        # ADD COMMAS TO ORDERS + UNITS
        # -----------------------------
        cat_profit_display["Orders"] = cat_profit_display["Orders"].apply(
            lambda x: f"{x:,}"
        )

        cat_profit_display["Units Sold"] = cat_profit_display["Units Sold"].apply(
            lambda x: f"{x:,}"
        )

        # --------------------
        # RENDER TABLE + CHART
        # --------------------
        c1, c2 = st.columns([1.4, 1.6])

        with c1:
            st.markdown("**Category Profitability**")
            st.dataframe(cat_profit_display, use_container_width=True, hide_index=True)

        with c2:

            # ❗ Fix: sort FIRST and store result so labels match bars
            chart_data = cat_profit_chart.sort_values("profit", ascending=True)

            fig_cat_profit = px.bar(
                chart_data,
                x="profit",
                y="category",
                orientation="h",
                title="Estimated Profit by Category",
                labels={"profit": "Estimated Profit ($)", "category": "Category"},
                color="profit",
                color_continuous_scale=[MINT, PRIMARY_EMERALD],
            )

            # ❗ Fix: use chart_data (sorted) for labels, not cat_profit_chart
            fig_cat_profit.update_traces(
                hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
                text=chart_data["profit"].round(0),
                texttemplate="$%{text:,}",
                textposition="outside"
            )

            fig_cat_profit.update_layout(
                template=plotly_template,
                height=500,
                modebar_remove=[
                    'zoom','pan','select','lasso','zoomin','zoomout',
                    'autoscale','resetscale'
                ],
                margin=dict(l=20, r=90, t=60, b=20)   # ← more breathing room on right
            )

            fig_cat_profit.update_traces(
                cliponaxis=False                      # ← prevents label clipping
            )


            fig_cat_profit = clean_axes(fig_cat_profit)
            fig_cat_profit = force_gradient_colors(fig_cat_profit)
            with st.container():
                st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
                st.plotly_chart(fig_cat_profit, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # =======================================================
        # PRODUCT-LEVEL PROFITABILITY
        # =======================================================
        prod_profit = (
            items_profit.groupby("product_name")
            .agg(
                net_sales=("net_sales", "sum"),
                profit=("est_gross_profit", "sum"),
                units=("total_inventory_sold", "sum"),
            )
            .reset_index()
        )

        prod_profit["margin_pct"] = np.where(
            prod_profit["net_sales"] > 0,
            (prod_profit["profit"] / prod_profit["net_sales"]) * 100,
            0
        )

        prod_profit_display = prod_profit.rename(
            columns={
                "product_name": "Product Name",
                "net_sales": "Net Sales ($)",
                "profit": "Estimated Profit ($)",
                "units": "Units Sold",
                "margin_pct": "Margin (%)",
            }
        )

        # Sort for “Top 15” chart before formatting
        top_15 = prod_profit_display.sort_values(
            "Estimated Profit ($)", ascending=False
        ).head(15)

        st.markdown("#### Top 15 Products by Estimated Profit")

        fig_top = px.bar(
            top_15,
            x="Estimated Profit ($)",
            y="Product Name",
            orientation="h",
            color="Estimated Profit ($)",
            color_continuous_scale=[MINT, PRIMARY_EMERALD],
            title="Top 15 Products by Estimated Profit",
        )

        fig_top.update_traces(
            text=top_15["Estimated Profit ($)"],
            texttemplate="$%{text:,.0f}",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Estimated Profit: $%{x:,.0f}<extra></extra>",
        )


        # --- Layout improvements (more margin on right) ---
        fig_top.update_layout(
            template=plotly_template,
            height=450,
            margin=dict(l=20, r=90, t=60, b=40),   # ← more breathing room
            modebar_remove=[
                'zoom','pan','select','lasso','zoomin','zoomout',
                'autoscale','resetscale'
            ]
        )

        # --- Keep best visual order (highest at top) ---
        fig_top.update_yaxes(autorange="reversed")

        # --- Apply your color gradient helper ---
        fig_top = clean_axes(fig_top)
        fig_top = force_gradient_colors(fig_top)

        with st.container():
            st.markdown("<div class='chart-scroll'>", unsafe_allow_html=True)
            st.plotly_chart(fig_top, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        # =======================================================
        # VENDOR-LEVEL PROFITABILITY
        # =======================================================
        vendor = (
            items_profit.groupby("vendor_name")
            .agg(
                net_sales=("net_sales", "sum"),
                profit=("est_gross_profit", "sum"),
            )
            .reset_index()
        )

        vendor["margin_pct"] = np.where(
            vendor["net_sales"] > 0,
            (vendor["profit"] / vendor["net_sales"]) * 100,
            0
        )

        vendor_display = vendor.rename(
            columns={
                "vendor_name": "Vendor",
                "net_sales": "Net Sales ($)",
                "profit": "Estimated Profit ($)",
                "margin_pct": "Margin (%)",
            }
        ).sort_values("Estimated Profit ($)", ascending=False)

        # Clean formatting
        vendor_display["Net Sales ($)"] = vendor_display["Net Sales ($)"].apply(lambda x: f"${x:,.0f}")
        vendor_display["Estimated Profit ($)"] = vendor_display["Estimated Profit ($)"].apply(lambda x: f"${x:,.0f}")
        vendor_display["Margin (%)"] = vendor_display["Margin (%)"].apply(lambda x: f"{x:.1f}%")

        st.markdown("#### Vendor Profitability Overview")
        st.dataframe(
            vendor_display.head(25),
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info("No item data available for the selected filters.")

    card_end()




# -----------------------------------------------------------
# TAB 7 — INSIGHTS (REWRITTEN + CLEAN + ADAPTIVE)
# -----------------------------------------------------------

with tab_insights:

    card_start()
    st.markdown(
        f"<h3 style='color:{BRIGHT_MINT};'>💡 Key Insights</h3>",
        unsafe_allow_html=True,
    )

    if len(df_filtered) and len(items_filtered):

        # BASIC METRICS
        total_orders = df_filtered["order_id"].nunique()
        avg_orders_per_day = total_orders / max((end_date - start_date).days + 1, 1)
        # Repeat rate (MATCH KPI)
        df_date_range = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        visits = df_date_range.groupby("customer_hash_id")["order_id"].nunique()
        repeat_rate_local = (visits > 1).mean() * 100


        # CATEGORY MIX
        category_revenue = items_filtered.groupby("category")["net_sales"].sum()
        if not category_revenue.empty:
            top_category = category_revenue.idxmax()
            top_share = (category_revenue.max() / category_revenue.sum()) * 100
        else:
            top_category = "N/A"
            top_share = 0

        all_selected = set(selected_categories) == set(all_categories)
        single_category = len(selected_categories) == 1

        if single_category:
            category_mix_sentence = (
                f"{top_category} leads with 100% of category revenue, "
                f"as it is the only category selected."
            )
        else:
            category_mix_sentence = (
                f"{top_category} leads with {top_share:.1f}% of category revenue, "
                "indicating where merchandising and inventory decisions matter most."
            )

        # BUNDLING
        pair_df_ins = compute_category_pairs(items_filtered[["order_id", "category"]])

        if single_category or pair_df_ins.empty:
            bundling_sentence = (
                "The most common cross-category pairing is N/A, since only a single "
                "category was selected or no qualifying bundles exist."
            )
        else:
            top_pair = pair_df_ins.iloc[0]

            # SAFELY CONVERT pair_count
            pair_count_value = pd.to_numeric(top_pair["pair_count"], errors="coerce")
            pair_count_value = 0 if pd.isna(pair_count_value) else int(pair_count_value)

            bundling_sentence = (
                f"The most common cross-category pairing is "
                f"<b>{top_pair['category_a']} + {top_pair['category_b']}</b>, "
                f"appearing together in <b>{pair_count_value:,}</b> orders. "
                "This represents a strong ready-made bundle opportunity."
            )


        # PROFITABILITY
        items_profit_ins = enrich_with_profit(items_filtered)
        total_est_profit = items_profit_ins["est_gross_profit"].sum()
        # Use the SAME KPI total so Insights matches the cards
        total_net_sales = total_revenue
        margin_insights = (
            (total_est_profit / total_net_sales) * 100 if total_net_sales > 0 else 0
        )

        # LOYALTY
        if all_selected:
            loyalty_sentence = (
                f"{repeat_rate_local:.1f}% of customers are repeat buyers, "
                "forming a strong base for retention programs."
            )
        else:
            loyalty_sentence = (
                f"{repeat_rate_local:.1f}% of customers within these filters are repeat buyers. "
                "This differs from overall storewide behavior, revealing how loyalty varies "
                "across categories."
            )

        st.markdown(f"""
        <ul style="list-style-type: disc; padding-left: 20px; font-size:16px; color:#E8F7F0;">

        <li><b>Overall performance:</b> ${total_net_sales:,.2f} over <b>{total_orders:,}</b> orders ({avg_orders_per_day:.1f} per day).</li>

        <li><b>Customer loyalty:</b> {loyalty_sentence}</li>

        <li><b>Basket health:</b> Customers spend an average of <b>${avg_order:,.2f}</b> with ~<b>{avg_items_order:.2f}</b> items per order, supporting bundle and upsell strategies.</li>

        <li><b>Category mix:</b> {category_mix_sentence}</li>

        <li><b>Bundling:</b> {bundling_sentence}</li>

        <li><b>Profitability:</b> Estimated gross margin on item sales is <b>{margin_insights:.1f}%</b>, with total estimated gross profit of <b>${total_est_profit:,.2f}</b> across the selected range.</li>

        </ul>

        <p style="font-size:14px; margin-top:10px; color:#E8F7F0; max-width:900px;">
        Use these insights to tune promotions, bundles, staffing, inventory, and retention plays for the selected date range.
        </p>
        """, unsafe_allow_html=True)


    else:
        st.info("Not enough data to generate insights. Try widening the date range or relaxing filters.")

    card_end()

