import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Airbnb Amsterdam",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme toggle ──────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ── Palette (Minty-inspired) ──────────────────────────────────────────────────
MINTY_GREEN  = "#78C2AD"
MINTY_ACCENT = "#F3969A"
MINTY_YELLOW = "#FFCE67"
MINTY_BLUE   = "#6CC3D5"
MINTY_PURPLE = "#8A6BD8"
SEQ_SCALE    = [[0, MINTY_BLUE], [0.5, MINTY_GREEN], [1, MINTY_ACCENT]]
CAT_COLORS   = [MINTY_GREEN, MINTY_ACCENT, MINTY_YELLOW, MINTY_BLUE, MINTY_PURPLE,
                "#FF8C69", "#A8D8B9", "#C9B8E8"]

dark = st.session_state.dark_mode
bg        = "#1A2821" if dark else "#F8FBF9"
card_bg   = "#243328" if dark else "#FFFFFF"
text_col  = "#E2F0EC" if dark else "#2D4A3E"
sub_col   = "#8ABFB0" if dark else "#6C8F82"
border    = "#2E4A3C" if dark else "#D4EDE6"
plot_tmpl = "plotly_dark" if dark else "plotly_white"
map_style = "carto-darkmatter" if dark else "carto-positron"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{
      background-color: {bg};
      color: {text_col};
      font-family: 'Segoe UI', system-ui, sans-serif;
  }}
  .dashboard-title {{
      font-size: 1.85rem;
      font-weight: 700;
      color: {MINTY_GREEN};
      margin: 0;
  }}
  .dashboard-title span {{ color: {text_col}; }}
  .metric-card {{
      background: {card_bg};
      border: 1px solid {border};
      border-radius: 12px;
      padding: 1.1rem 1.2rem;
      text-align: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .metric-value {{
      font-size: 1.9rem;
      font-weight: 700;
      color: {MINTY_GREEN};
  }}
  .metric-label {{
      font-size: 0.8rem;
      color: {sub_col};
      margin-top: 3px;
  }}
  .stTabs [data-baseweb="tab-list"] {{
      background: {card_bg};
      border-radius: 10px;
      padding: 4px;
      gap: 4px;
      border: 1px solid {border};
  }}
  .stTabs [data-baseweb="tab"] {{
      border-radius: 8px;
      color: {sub_col};
      font-weight: 500;
  }}
  .stTabs [aria-selected="true"] {{
      background: {MINTY_GREEN} !important;
      color: #fff !important;
  }}
  .section-heading {{
      font-size: 1rem;
      font-weight: 600;
      color: {text_col};
      margin: 1rem 0 0.4rem;
      border-left: 4px solid {MINTY_GREEN};
      padding-left: 0.6rem;
  }}
  header[data-testid="stHeader"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# ── Data loading & cleaning ───────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("BigML_Dataset_airBnB.csv")

    # Fix European decimal separators in lat/lon
    df["latitude"]  = df["latitude"].astype(str).str.replace(",", ".").astype(float)
    df["longitude"] = df["longitude"].astype(str).str.replace(",", ".").astype(float)

    # Boolean columns
    df["host_is_superhost"] = df["host_is_superhost"].map({"t": True, "f": False})
    df["instant_bookable"]  = df["instant_bookable"].map({"t": True, "f": False})

    # Drop extreme price outliers (keep 1st–99th percentile)
    p1, p99 = df["price"].quantile(0.01), df["price"].quantile(0.99)
    df = df[(df["price"] >= p1) & (df["price"] <= p99)]

    return df

df = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_toggle = st.columns([6, 1])
with col_title:
    st.markdown(
        '<p class="dashboard-title">🏠 <span>Airbnb Amsterdam — Data Analysis</span></p>',
        unsafe_allow_html=True,
    )
with col_toggle:
    label = "☀️ Light" if dark else "🌙 Dark"
    if st.button(label, use_container_width=True):
        st.session_state.dark_mode = not dark
        st.rerun()

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_overview, tab_neighbourhoods, tab_map, tab_rooms = st.tabs(
    ["📊 Overview", "🏘️ Neighbourhoods", "🗺️ Map", "🛏️ Room Types"]
)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Overview
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:
    avg_price     = df["price"].mean()
    total_list    = len(df)
    avg_rating    = df["review_scores_rating"].mean()
    superhost_pct = df["host_is_superhost"].mean() * 100
    avg_avail     = df["availability_365"].mean()

    k1, k2, k3, k4, k5 = st.columns(5)
    for col, val, label in [
        (k1, f"€{avg_price:.0f}",      "Avg Nightly Price"),
        (k2, f"{total_list:,}",         "Total Listings"),
        (k3, f"{avg_rating:.1f}/100",   "Avg Review Score"),
        (k4, f"{superhost_pct:.0f}%",   "Superhost Listings"),
        (k5, f"{avg_avail:.0f} days",   "Avg Availability/yr"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-heading">Price Distribution (€/night)</p>', unsafe_allow_html=True)
        fig = px.histogram(df, x="price", nbins=50,
                           color_discrete_sequence=[MINTY_GREEN], template=plot_tmpl,
                           labels={"price": "Nightly Price (€)"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-heading">Review Score Distribution</p>', unsafe_allow_html=True)
        fig = px.histogram(df.dropna(subset=["review_scores_rating"]),
                           x="review_scores_rating", nbins=30,
                           color_discrete_sequence=[MINTY_ACCENT], template=plot_tmpl,
                           labels={"review_scores_rating": "Review Score (0–100)"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<p class="section-heading">Property Type Breakdown</p>', unsafe_allow_html=True)
        pt = df["property_type"].value_counts().head(8).reset_index()
        pt.columns = ["property_type", "count"]
        fig = px.bar(pt, x="count", y="property_type", orientation="h",
                     color="count", color_continuous_scale=SEQ_SCALE, template=plot_tmpl,
                     labels={"count": "Listings", "property_type": ""})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          coloraxis_showscale=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown('<p class="section-heading">Price vs Review Score</p>', unsafe_allow_html=True)
        sample = df.dropna(subset=["review_scores_rating"]).sample(min(2000, len(df)), random_state=42)
        fig = px.scatter(sample, x="review_scores_rating", y="price",
                         color="room_type", opacity=0.55,
                         color_discrete_sequence=CAT_COLORS, template=plot_tmpl,
                         labels={"review_scores_rating": "Review Score", "price": "Price (€)"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-heading">Cancellation Policy & Instant Bookable</p>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        cancel = df["cancellation_policy"].value_counts().reset_index()
        cancel.columns = ["policy", "count"]
        fig = px.pie(cancel, values="count", names="policy", hole=0.45,
                     color_discrete_sequence=CAT_COLORS, template=plot_tmpl)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with c6:
        ib = df["instant_bookable"].value_counts().reset_index()
        ib.columns = ["bookable", "count"]
        ib["bookable"] = ib["bookable"].map({True: "Instant Bookable", False: "Request Only"})
        fig = px.pie(ib, values="count", names="bookable", hole=0.45,
                     color_discrete_sequence=[MINTY_GREEN, MINTY_ACCENT], template=plot_tmpl)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Neighbourhoods
# ─────────────────────────────────────────────────────────────────────────────
with tab_neighbourhoods:
    st.markdown("<br>", unsafe_allow_html=True)

    nb_agg = (
        df.groupby("neighbourhood_cleansed", as_index=False)
          .agg(avg_price=("price","mean"), listings=("price","count"),
               avg_reviews=("number_of_reviews","mean"),
               avg_rating=("review_scores_rating","mean"),
               avg_avail=("availability_365","mean"))
          .sort_values("avg_price", ascending=False)
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="section-heading">Avg Price by Neighbourhood (€/night)</p>', unsafe_allow_html=True)
        fig = px.bar(nb_agg, x="avg_price", y="neighbourhood_cleansed", orientation="h",
                     color="avg_price", color_continuous_scale=SEQ_SCALE, template=plot_tmpl,
                     labels={"avg_price": "Avg Price (€)", "neighbourhood_cleansed": ""})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          coloraxis_showscale=False, margin=dict(l=0,r=0,t=10,b=0), height=500)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-heading">Listings per Neighbourhood</p>', unsafe_allow_html=True)
        fig = px.pie(nb_agg.sort_values("listings", ascending=False).head(12),
                     values="listings", names="neighbourhood_cleansed", hole=0.42,
                     color_discrete_sequence=px.colors.qualitative.Pastel, template=plot_tmpl)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0), height=500,
                          legend=dict(orientation="v", x=1.02, font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-heading">Avg Review Score by Neighbourhood</p>', unsafe_allow_html=True)
    fig = px.bar(nb_agg.sort_values("avg_rating", ascending=False),
                 x="neighbourhood_cleansed", y="avg_rating",
                 color="avg_rating", color_continuous_scale=SEQ_SCALE, template=plot_tmpl,
                 range_y=[85, 100],
                 labels={"avg_rating": "Avg Review Score", "neighbourhood_cleansed": ""})
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      coloraxis_showscale=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-heading">Avg Availability (days/yr) by Neighbourhood</p>', unsafe_allow_html=True)
    fig = px.bar(nb_agg.sort_values("avg_avail", ascending=False),
                 x="neighbourhood_cleansed", y="avg_avail",
                 color_discrete_sequence=[MINTY_YELLOW], template=plot_tmpl,
                 labels={"avg_avail": "Avg Days Available", "neighbourhood_cleansed": ""})
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Map
# ─────────────────────────────────────────────────────────────────────────────
with tab_map:
    st.markdown("<br>", unsafe_allow_html=True)

    map_col, filter_col = st.columns([4, 1])
    with filter_col:
        st.markdown("**Filter listings**")
        price_range = st.slider(
            "Price range (€/night)",
            int(df.price.min()), int(df.price.max()),
            (int(df.price.quantile(0.05)), int(df.price.quantile(0.95))),
        )
        room_opts = df["room_type"].unique().tolist()
        sel_rooms = st.multiselect("Room type", room_opts, default=room_opts)
        nbhoods = ["All"] + sorted(df["neighbourhood_cleansed"].dropna().unique().tolist())
        sel_nb = st.selectbox("Neighbourhood", nbhoods)
        superhost_only = st.checkbox("Superhosts only", value=False)

    map_df = df[
        (df.price >= price_range[0]) &
        (df.price <= price_range[1]) &
        (df.room_type.isin(sel_rooms))
    ]
    if sel_nb != "All":
        map_df = map_df[map_df.neighbourhood_cleansed == sel_nb]
    if superhost_only:
        map_df = map_df[map_df.host_is_superhost == True]

    # Sample for performance
    plot_df = map_df.sample(min(3000, len(map_df)), random_state=42) if len(map_df) > 3000 else map_df

    with map_col:
        fig = px.scatter_mapbox(
            plot_df,
            lat="latitude", lon="longitude",
            color="price",
            size="number_of_reviews",
            size_max=14,
            hover_name="name",
            hover_data={
                "price": True, "room_type": True,
                "number_of_reviews": True, "neighbourhood_cleansed": True,
                "review_scores_rating": True,
                "latitude": False, "longitude": False,
            },
            color_continuous_scale=SEQ_SCALE,
            zoom=11.2,
            center={"lat": 52.374, "lon": 4.895},
            height=560,
            template=plot_tmpl,
            mapbox_style=map_style,
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=0,b=0),
                          coloraxis_colorbar=dict(title="Price €"))
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Showing **{len(plot_df):,}** of **{len(map_df):,}** filtered listings")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Room Types
# ─────────────────────────────────────────────────────────────────────────────
with tab_rooms:
    st.markdown("<br>", unsafe_allow_html=True)

    rt_agg = (
        df.groupby("room_type", as_index=False)
          .agg(count=("price","count"), avg_price=("price","mean"),
               avg_reviews=("number_of_reviews","mean"),
               avg_rating=("review_scores_rating","mean"),
               avg_avail=("availability_365","mean"))
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="section-heading">Listing Count by Room Type</p>', unsafe_allow_html=True)
        fig = px.bar(rt_agg.sort_values("count", ascending=False),
                     x="room_type", y="count", color="room_type",
                     color_discrete_sequence=CAT_COLORS, template=plot_tmpl,
                     labels={"count": "Listings", "room_type": ""})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-heading">Avg Price by Room Type (€/night)</p>', unsafe_allow_html=True)
        fig = px.bar(rt_agg.sort_values("avg_price", ascending=False),
                     x="room_type", y="avg_price", color="room_type",
                     color_discrete_sequence=CAT_COLORS, template=plot_tmpl,
                     labels={"avg_price": "Avg Price (€)", "room_type": ""})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-heading">Price Distribution by Room Type</p>', unsafe_allow_html=True)
    fig = px.box(df, x="room_type", y="price", color="room_type",
                 color_discrete_sequence=CAT_COLORS, template=plot_tmpl, points="outliers",
                 labels={"price": "Price (€)", "room_type": "Room Type"})
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<p class="section-heading">Avg Review Score by Room Type</p>', unsafe_allow_html=True)
        fig = px.bar(rt_agg.sort_values("avg_rating", ascending=False),
                     x="room_type", y="avg_rating", color="room_type",
                     color_discrete_sequence=CAT_COLORS, template=plot_tmpl, range_y=[85, 100],
                     labels={"avg_rating": "Avg Review Score", "room_type": ""})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown('<p class="section-heading">Superhost Share by Room Type</p>', unsafe_allow_html=True)
        sh = df.dropna(subset=["host_is_superhost"]).groupby(["room_type","host_is_superhost"]).size().reset_index(name="count")
        sh["host_is_superhost"] = sh["host_is_superhost"].map({True: "Superhost", False: "Regular"})
        fig = px.bar(sh, x="room_type", y="count", color="host_is_superhost", barmode="stack",
                     color_discrete_map={"Superhost": MINTY_GREEN, "Regular": MINTY_ACCENT},
                     template=plot_tmpl,
                     labels={"count": "Listings", "room_type": "", "host_is_superhost": ""})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<p style="text-align:center;color:{sub_col};font-size:0.8rem;">'
    f"Airbnb Amsterdam · {len(df):,} listings · Built with Streamlit & Plotly"
    "</p>",
    unsafe_allow_html=True,
)