import io
import streamlit as st
from main import (
    load_data,
    build_dual_axis_fig,
    build_scatter_fig,
    build_single_fig,
    guess_band_column,
    band_vendor_stats,
    sheet_name,
    aggregate_metrics,  # <-- EKLENDİ
)

st.set_page_config(page_title="KPI Chart UI", layout="wide")
st.title("KPI Chart UI")

# Subtle modern styling for cards and sections
def inject_css():
    st.markdown(
        """
        <style>
        .kpi-card {border: 1px solid #e6e6e6; border-radius: 10px; padding: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.04);}        
        .kpi-card__header {background: linear-gradient(90deg, #4f81bd 0%, #7aa6d1 100%); color: white; padding: 8px 10px; border-radius: 8px; font-weight: 600;}
        .kpi-card__header--red {background: linear-gradient(90deg, #c0504d 0%, #e07b77 100%);} 
        .kpi-card__body {padding: 10px 8px; font-size: 13px; line-height: 1.45;}
        .kpi-grid {display: grid; grid-template-columns: 1fr 1fr; gap: 12px;}

        /* Subheaders and key-value pills */
        .kpi-subheader {font-weight: 600; color: #6b7280; margin: 8px 2px 6px; letter-spacing: .2px;}
        .metric-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px 10px;}
        .kv {display:flex; align-items:center; justify-content:space-between; background:#f9fafb; border:1px solid #eee; border-radius:8px; padding:6px 8px;}
        .kv .k {color:#6b7280; font-weight:600;}
        .kv .v {color:#111827; font-weight:600;}
        .badge-row {display:flex; flex-wrap:wrap; gap:6px;}
        .badge {display:inline-block; padding:4px 8px; border-radius:9999px; background:#eef2ff; color:#1f3b82; font-weight:600; font-size: 11px;}
        .badge--green {background:#ecfdf5; color:#065f46;}
        .badge--yellow {background:#fef9c3; color:#92400e;}
        .badge--red {background:#fee2e2; color:#7f1d1d;}
        .metric-description {font-size: 11px; color: #9ca3af; margin-top: 2px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

@st.cache_data(show_spinner=False)
def get_data():
    return load_data()

# Varsayılan dosya yolları
DEFAULT_PW_PATH = '/Users/akolukisa/Downloads/PW_Turkcell_DL.xlsx'
DEFAULT_HW_PATHS = ['/Users/akolukisa/Downloads/HW_Turkcell_DL.xlsx', '/Users/akolukisa/Downloads/HW_Turkcell_DL (2).xlsx']
DEFAULT_HW_PATH = DEFAULT_HW_PATHS[0]  # Varsayılan olarak ilk dosya

# Vendor names inputs
col_vn1, col_vn2 = st.columns([1,1])
with col_vn1:
    vendor1_name_input = st.text_input("Vendor 1 name", value="Vendor 1")
with col_vn2:
    vendor2_name_input = st.text_input("Vendor 2 name", value="Vendor 2")

# Dosya yükleme alanları ve sheet adı
col_pw, col_hw, col_sheet = st.columns([1,1,1])
with col_pw:
    pw_file = st.file_uploader("Vendor 1 (PW) Excel", type=["xlsx"], accept_multiple_files=False)
    if pw_file is None:
        try:
            pw_file = open(DEFAULT_PW_PATH, "rb")
        except Exception:
            pw_file = None
with col_hw:
    hw_file = st.file_uploader("Vendor 2 (HW) Excel", type=["xlsx"], accept_multiple_files=False)
    if hw_file is None:
        try:
            hw_file = open(DEFAULT_HW_PATH, "rb")
        except Exception:
            hw_file = None
with col_sheet:
    sheet_name_input = st.text_input("Sheet name", value="Series Formatted Data")

# Try to load data using uploaded files if provided; otherwise fallback to defaults
df = None
try:
    df = load_data(
        hw_source=hw_file,
        pw_source=pw_file,
        sheet_name_override=sheet_name_input.strip() or None,
        vendor1_name=vendor1_name_input,
        vendor2_name=vendor2_name_input,
    )
except SystemExit:
    st.error("Failed to load data. Please upload both Vendor files or ensure default paths exist.")
    df = None

if df is not None:
    # Options from Excel headers (exclude the added 'Source' column)
    excel_columns = [c for c in df.columns if c != 'Source']
    metric_options = excel_columns
    y2_options = ["None"] + excel_columns
else:
    st.stop()

style_options = ["Scatter", "Bar"]

charts_tab, dashboard_tab = st.tabs(["Charts", "Dashboard"])

with charts_tab:
    st.caption("İpucu: Y2 'None' ise, Y1 için seçtiğiniz stil uygulanır (Bar veya Scatter).")
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
    with col1:
        x_col = st.selectbox("Select X metric", metric_options, index=0, help="Metric for X-axis")
    with col2:
        y1_col = st.selectbox("Select Y1 metric", metric_options, index=2, help="Left axis metric")
    with col3:
        y1_style = st.radio("Y1 style", style_options, index=0, horizontal=True)
    with col4:
        y2_sel = st.selectbox("Select Y2 metric (optional)", y2_options, index=0, help="Right axis metric")
    with col5:
        y2_style = st.radio("Y2 style", style_options, index=1, horizontal=True)

    run = st.button("Plot")

    if run:
        if y2_sel == "None":
            # Apply selected style for Y1 when Y2 is None
            left_style = 'bar' if y1_style == 'Bar' else 'scatter'
            fig = build_single_fig(
                df,
                x_col,
                y1_col,
                y1_style=left_style,
                vendor1_label=(vendor1_name_input or 'Vendor 1'),
                vendor2_label=(vendor2_name_input or 'Vendor 2'),
            )
            if fig is not None:
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight")
                buf.seek(0)

                st.pyplot(fig)
                st.download_button(
                    label="Download PNG",
                    data=buf.getvalue(),
                    file_name=(
                        f"single_{(vendor1_name_input or 'Vendor 1')}_vs_{(vendor2_name_input or 'Vendor 2')}_{x_col}_vs_{y1_col}_{left_style}.png"
                        .replace(" ", "_")
                        .replace("/", "_")
                    ),
                    mime="image/png",
                )
            else:
                st.error("Not enough data for the selected metrics.")
        else:
            left_style = 'bar' if y1_style == 'Bar' else 'scatter'
            right_style = 'bar' if y2_style == 'Bar' else 'scatter'

            fig = build_dual_axis_fig(
                df,
                x_col,
                y1_col,
                y2_sel,
                left_style=left_style,
                right_style=right_style,
                vendor1_label=(vendor1_name_input or 'Vendor 1'),
                vendor2_label=(vendor2_name_input or 'Vendor 2'),
            )

            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            st.pyplot(fig)
            st.download_button(
                label="Download PNG",
                data=buf.getvalue(),
                file_name=(
                    f"seperated_plot_{(vendor1_name_input or 'Vendor 1')}_vs_{(vendor2_name_input or 'Vendor 2')}_{x_col}_vs_{y1_col}_and_{y2_sel}_{y1_style.lower()}_{y2_style.lower()}.png"
                    .replace(" ", "_")
                    .replace("/", "_")
                ),
                mime="image/png",
            )

# --- Dashboard Section ---
with dashboard_tab:
    # Pick a band column
    default_band_col = guess_band_column(df)
    band_col = st.selectbox(
        "Band column",
        options=[default_band_col] + [c for c in df.columns if c != default_band_col] if default_band_col else df.columns,
        index=0 if default_band_col else 0,
        help="Which column contains band information? (e.g., 'Band', 'LTE_Band')"
    )

    # Available bands to display
    bands_available = sorted(df[band_col].dropna().astype(str).unique()) if band_col in df.columns else []
    selected_bands = st.multiselect(
        "Bands to display",
        options=bands_available,
        default=bands_available[:3] if len(bands_available) > 0 else [],
    )

    show_dash = st.button("Render Dashboard")

    def get_badge_class(metric_name, value):
        if value is None: return ''
        if metric_name == 'BLER_DL':
            if value > 5: return 'badge--red'
            elif value > 2: return 'badge--yellow'
            else: return 'badge--green'
        if metric_name == 'L1toPDCPTp_ratio':
            if value < 0.8: return 'badge--red'
            elif value < 0.95: return 'badge--yellow'
            else: return 'badge--green'
        elif metric_name in ['QPSK_pct', 'QAM16_pct', 'QAM64_pct', 'QAM256_pct']:
            # Assuming higher order modulation is better, adjust thresholds as needed
            if value > 0.7: return 'badge--green'
            elif value > 0.4: return 'badge--yellow'
            else: return 'badge--red'
        return ''

    def render_card(title, metrics, header_variant):
        # Determine header background based on variant
        header_class = "kpi-card__header"
        if header_variant == 'red':
            header_class += " kpi-card__header--red"
        
        # Generate HTML for metrics
        metric_html = ""
        for metric_name, metric_data in metrics.items():
            if metric_name == 'L1toPDCPTp_ratio':
                continue  # Bu metriği tamamen atla
            value = metric_data['value']
            unit = metric_data['unit']
            description = metric_data['description']
            badge_class = get_badge_class(metric_name, value)

            # Format value: PDCP_DL ve L1_DL için tam sayı, diğer floatlar için 2 basamak
            if metric_name in ['PDCP_DL', 'L1_DL'] and value is not None:
                try:
                    value = int(round(float(value)))
                except:
                    pass
            elif isinstance(value, float) and value is not None:
                value = f"{value:.2f}"

            metric_html += f"<div class='kv'><span class='k'>{metric_name}</span><span class='v'><span class='badge {badge_class}'>{value} {unit}</span></span></div>"

        card_html = f"<div class='kpi-card'><div class='{header_class}'>{title}</div><div class='kpi-card__body'><div class='metric-grid'>{metric_html}</div></div></div>"
        st.markdown(card_html, unsafe_allow_html=True)

    def band_name_from_earfcn(earfcn):
        mapping = {
            '100': 'B1 - 1st Carrier',
            '550': 'B1 - 2nd Carrier',
            '1651': 'B3 - 1st Carrier',
            '1795': 'B3 - 2nd Carrier',
            '6400': 'B20',
            '2850': 'B7',
        }
        return mapping.get(str(int(float(earfcn))), str(int(float(earfcn))))

    if show_dash and band_col:
        try:
            stats = band_vendor_stats(
                df,
                band_col=band_col,
                vendor1_label=(vendor1_name_input or 'Vendor 1'),
                vendor2_label=(vendor2_name_input or 'Vendor 2'),
            )

            # Genel PW ve HW kartları
            pw_general = aggregate_metrics(df[(df['Source'] == (vendor1_name_input or 'Vendor 1')) & (df['LTE_UE_EARFCN_DL'].isin([100, 1651]))])
            hw_general = aggregate_metrics(df[(df['Source'] == (vendor2_name_input or 'Vendor 2')) & (df['LTE_UE_EARFCN_DL'].isin([100, 1651]))])
            st.subheader('All Bands Statistics')
            c1, c2 = st.columns(2)
            with c1:
                render_card(f"{vendor1_name_input or 'Vendor 1'} - All Bands", pw_general, 'blue')
            with c2:
                render_card(f"{vendor2_name_input or 'Vendor 2'} - All Bands", hw_general, 'red')
            st.markdown('---')

            if selected_bands:
                for band in selected_bands:
                    band_int = str(int(float(band)))
                    band_display = band_name_from_earfcn(band)
                    c1, c2 = st.columns(2)
                    with c1:
                        m1 = stats.get((vendor1_name_input or 'Vendor 1'), {}).get(band, {})
                        render_card(f"{vendor1_name_input or 'Vendor 1'} - {band_int} - {band_display}", m1, 'blue')
                    with c2:
                        m2 = stats.get((vendor2_name_input or 'Vendor 2'), {}).get(band, {})
                        render_card(f"{vendor2_name_input or 'Vendor 2'} - {band_int} - {band_display}", m2, 'red')
            else:
                st.info("Please select at least one band.")
        except Exception as e:
            st.error(f"Could not render dashboard: {e}")