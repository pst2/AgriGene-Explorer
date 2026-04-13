import streamlit as st
import pandas as pd
from utils.helpers import init_session_state, is_valid_email
from modules.ncbi_fetch import NCBIFetcher
from modules.sequence_analysis import get_basic_stats, find_orfs, translate_sequence
from modules.visualization import (
    plot_length_distribution,
    plot_organism_pie,
    plot_submission_timeline,
    plot_nucleotide_composition,
    plot_gc_heatmap,
)
import plotly.graph_objects as go


st.set_page_config(
    page_title="AgriGene Explorer | Premium Bio Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()


# ----------------- GLOBAL STYLE -----------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    :root {
        --bg-1: #04110D;
        --bg-2: #071B14;
        --panel: rgba(10, 24, 19, 0.82);
        --panel-2: rgba(14, 33, 25, 0.92);
        --panel-3: rgba(18, 39, 30, 0.72);
        --line: rgba(132, 244, 181, 0.14);
        --line-strong: rgba(132, 244, 181, 0.22);
        --text: #F3FFF7;
        --muted: #A2B9AC;
        --soft: #D8FBE4;
        --primary: #63F5A7;
        --primary-2: #32D47B;
        --primary-3: #1CA45C;
        --warn: #FFD88A;
        --shadow: 0 24px 80px rgba(0,0,0,0.32);
        --radius-xl: 28px;
        --radius-lg: 22px;
        --radius-md: 16px;
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 12% 10%, rgba(99,245,167,0.10), transparent 20%),
            radial-gradient(circle at 92% 2%, rgba(50,212,123,0.10), transparent 20%),
            radial-gradient(circle at 50% 120%, rgba(34,130,81,0.14), transparent 30%),
            linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
    }

    .block-container {
        max-width: 1420px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(6,16,12,0.98) 0%, rgba(8,21,16,0.99) 100%);
        border-right: 1px solid rgba(132,244,181,0.10);
    }

    [data-testid="stSidebar"] * {
        color: #F3FFF7;
    }

    .sidebar-shell {
        position: relative;
        overflow: hidden;
        padding: 22px 18px;
        border-radius: 24px;
        background: linear-gradient(145deg, rgba(20,56,41,0.88), rgba(9,24,18,0.92));
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
    }

    .sidebar-shell:after {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        right: -70px;
        top: -80px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(132,244,181,0.20), transparent 65%);
    }

    .sidebar-kicker {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #BCEFD0;
        margin-bottom: 8px;
        font-weight: 800;
    }

    .sidebar-title {
        font-size: 1.45rem;
        font-weight: 900;
        margin: 0;
        position: relative;
        z-index: 1;
    }

    .sidebar-desc {
        margin-top: 8px;
        color: #D2EBDD;
        line-height: 1.65;
        font-size: 0.93rem;
        position: relative;
        z-index: 1;
    }

    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 13px;
        border-radius: 999px;
        background: rgba(99,245,167,0.10);
        border: 1px solid var(--line-strong);
        color: #E8FFF0;
        font-size: 0.85rem;
        font-weight: 800;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 34px;
        border-radius: 30px;
        background:
            radial-gradient(circle at 90% 15%, rgba(132,244,181,0.18), transparent 24%),
            linear-gradient(135deg, rgba(12,31,23,0.96) 0%, rgba(7,18,14,0.98) 100%);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
    }

    .hero:before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, rgba(99,245,167,0.08), transparent 36%);
        pointer-events: none;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 24px;
        align-items: stretch;
        position: relative;
        z-index: 1;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.35rem;
        line-height: 1.05;
        letter-spacing: -0.04em;
        font-weight: 900;
        color: #F5FFF8;
    }

    .hero p {
        margin: 14px 0 0 0;
        max-width: 800px;
        color: #CEE7D7;
        line-height: 1.72;
        font-size: 1rem;
    }

    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }

    .hero-badge {
        padding: 9px 13px;
        border-radius: 999px;
        background: rgba(99,245,167,0.10);
        border: 1px solid var(--line-strong);
        color: #DDFBE7;
        font-size: 0.84rem;
        font-weight: 700;
    }

    .hero-stat-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
        align-content: start;
    }

    .hero-stat {
        padding: 18px;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(16,39,30,0.88), rgba(10,24,18,0.92));
        border: 1px solid var(--line);
        min-height: 110px;
    }

    .hero-stat-label {
        color: #A9C6B4;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 10px;
        font-weight: 700;
    }

    .hero-stat-value {
        color: #F6FFF9;
        font-size: 1.65rem;
        font-weight: 900;
        line-height: 1;
    }

    .hero-stat-sub {
        color: #B9D4C4;
        font-size: 0.88rem;
        margin-top: 10px;
        line-height: 1.5;
    }

    .section-label {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #DBFBE7;
        font-size: 0.95rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0.3rem 0 0.9rem 0;
    }

    .glass-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(14,30,23,0.88), rgba(8,19,15,0.90));
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 18px 18px 14px 18px;
        box-shadow: var(--shadow);
        backdrop-filter: blur(14px);
        margin-bottom: 1rem;
    }

    .glass-card:before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(132,244,181,0.04), transparent 35%);
        pointer-events: none;
    }

    .sub-card {
        background: linear-gradient(180deg, rgba(17,36,28,0.70), rgba(10,24,18,0.72));
        border: 1px solid rgba(132,244,181,0.10);
        border-radius: 18px;
        padding: 16px;
    }

    .insight-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin-top: 10px;
        margin-bottom: 6px;
    }

    .insight-card {
        background: linear-gradient(180deg, rgba(16,36,28,0.92), rgba(10,22,17,0.92));
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 16px;
    }

    .insight-label {
        color: #9CB8A8;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        margin-bottom: 8px;
        font-weight: 700;
    }

    .insight-value {
        color: #F4FFF7;
        font-size: 1.35rem;
        font-weight: 900;
        line-height: 1.1;
    }

    .insight-sub {
        color: #B9D3C4;
        font-size: 0.88rem;
        margin-top: 8px;
    }

    .tiny-note {
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.7;
        margin: 0.1rem 0 0.4rem 0;
    }

    .info-list {
        margin: 0;
        padding-left: 1.1rem;
        color: #D9EFE2;
        line-height: 1.8;
    }

    .premium-callout {
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(99,245,167,0.10), rgba(14,30,23,0.40));
        border: 1px solid var(--line-strong);
        padding: 16px;
        color: #E5FFF0;
        line-height: 1.7;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(16,36,27,0.94), rgba(8,19,15,0.94));
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 16px 16px;
        box-shadow: var(--shadow);
    }

    div[data-testid="stMetricLabel"] {
        color: #A7C0B1;
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: #F4FFF8;
        font-weight: 900;
    }

    div.stButton > button,
    div.stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        min-height: 3rem;
        border-radius: 16px !important;
        border: 1px solid rgba(132,244,181,0.14) !important;
        background: linear-gradient(135deg, rgba(50,212,123,0.98), rgba(99,245,167,0.98)) !important;
        color: #032113 !important;
        font-weight: 900 !important;
        letter-spacing: 0.01em;
        box-shadow: 0 14px 34px rgba(50,212,123,0.22);
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.03);
    }

    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    .stNumberInput input {
        background: rgba(8,18,14,0.95) !important;
        border: 1px solid var(--line) !important;
        color: #F3FFF7 !important;
        border-radius: 14px !important;
    }

    .stRadio > div {
        gap: 10px;
    }

    .stAlert {
        border-radius: 18px;
        border: 1px solid var(--line);
    }

    div[data-testid="stDataFrame"] {
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(132,244,181,0.10);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 14px;
        background: rgba(18,39,30,0.60);
        border: 1px solid rgba(132,244,181,0.08);
        padding: 10px 16px;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99,245,167,0.12) !important;
        border-color: rgba(132,244,181,0.18) !important;
    }

    @media (max-width: 1024px) {
        .hero-grid,
        .insight-strip {
            grid-template-columns: 1fr;
        }
        .hero-stat-grid {
            grid-template-columns: 1fr 1fr;
        }
    }

    @media (max-width: 700px) {
        .hero-stat-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


PLOTLY_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(8,18,14,0.72)",
    "font_color": "#ECFFF3",
    "grid_color": "rgba(132,244,181,0.12)",
    "line_color": "rgba(132,244,181,0.18)",
    "accent": "#63F5A7",
    "accent_2": "#32D47B",
    "accent_3": "#9BFFBF",
    "accent_4": "#1CA45C",
    "accent_5": "#B8FFD3",
}


def apply_plot_theme(fig):
    if fig is None:
        return fig

    fig.update_layout(
        paper_bgcolor=PLOTLY_THEME["paper_bgcolor"],
        plot_bgcolor=PLOTLY_THEME["plot_bgcolor"],
        font=dict(color=PLOTLY_THEME["font_color"], family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(color=PLOTLY_THEME["font_color"]),
        ),
    )

    try:
        fig.update_xaxes(
            showgrid=True,
            gridcolor=PLOTLY_THEME["grid_color"],
            zeroline=False,
            linecolor=PLOTLY_THEME["line_color"],
            tickfont=dict(color="#D9FBE4"),
            title_font=dict(color="#F3FFF7"),
        )
    except Exception:
        pass

    try:
        fig.update_yaxes(
            showgrid=True,
            gridcolor=PLOTLY_THEME["grid_color"],
            zeroline=False,
            linecolor=PLOTLY_THEME["line_color"],
            tickfont=dict(color="#D9FBE4"),
            title_font=dict(color="#F3FFF7"),
        )
    except Exception:
        pass

    color_cycle = [
        PLOTLY_THEME["accent"],
        PLOTLY_THEME["accent_2"],
        PLOTLY_THEME["accent_3"],
        PLOTLY_THEME["accent_4"],
        PLOTLY_THEME["accent_5"],
    ]

    for i, trace in enumerate(fig.data):
        color = color_cycle[i % len(color_cycle)]
        trace_type = getattr(trace, "type", "")

        try:
            if trace_type in ["bar", "histogram"]:
                trace.marker.color = color
                trace.marker.line = dict(color="rgba(255,255,255,0.10)", width=1)
            elif trace_type in ["scatter", "scattergl"]:
                if getattr(trace, "mode", None) and "lines" in trace.mode:
                    trace.line.color = color
                    trace.line.width = 3
                if getattr(trace, "mode", None) and "markers" in trace.mode:
                    trace.marker.color = color
                    trace.marker.size = 8
            elif trace_type == "pie":
                trace.marker.colors = color_cycle
                trace.textfont = dict(color="#06110D")
                trace.hole = 0.45 if getattr(trace, "hole", 0) == 0 else trace.hole
            elif trace_type == "heatmap":
                trace.colorscale = [
                    [0.0, "#07130F"],
                    [0.2, "#0B231A"],
                    [0.45, "#135233"],
                    [0.7, "#1FA55E"],
                    [1.0, "#9BFFBF"],
                ]
                if hasattr(trace, "colorbar"):
                    trace.colorbar.title.font = dict(color="#ECFFF3")
                    trace.colorbar.tickfont = dict(color="#D9FBE4")
            else:
                if hasattr(trace, "marker") and trace.marker is not None:
                    try:
                        trace.marker.color = color
                    except Exception:
                        pass
        except Exception:
            pass

    return fig


def safe_mode(series, default="N/A"):
    try:
        mode_val = series.mode()
        if len(mode_val) > 0:
            return mode_val.iloc[0]
    except Exception:
        pass
    return default


def render_section(title: str, icon: str = "●"):
    st.markdown(
        f"<div class='section-label'><span>{icon}</span><span>{title}</span></div>",
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str, badges=None):
    badges = badges or []
    badges_html = "".join([f"<span class='hero-badge'>{badge}</span>" for badge in badges])
    setup_text = "Sẵn sàng phân tích" if st.session_state.get("ncbi_email") else "Cần cấu hình truy cập"
    max_results = st.session_state.get("max_results", 0)
    cached_records = st.session_state.get("search_results")
    cached_count = len(cached_records) if isinstance(cached_records, pd.DataFrame) else 0
    st.markdown(
        f"""
        <div class='hero'>
            <div class='hero-grid'>
                <div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                    <div class='hero-badges'>{badges_html}</div>
                </div>
                <div class='hero-stat-grid'>
                    <div class='hero-stat'>
                        <div class='hero-stat-label'>Trạng thái nền tảng</div>
                        <div class='hero-stat-value'>{setup_text}</div>
                        <div class='hero-stat-sub'>Kiểm tra cấu hình NCBI trước khi chạy các tính năng truy vấn trực tiếp.</div>
                    </div>
                    <div class='hero-stat'>
                        <div class='hero-stat-label'>Giới hạn tìm kiếm</div>
                        <div class='hero-stat-value'>{max_results}</div>
                        <div class='hero-stat-sub'>Số bản ghi tối đa được yêu cầu trong mỗi lượt truy vấn.</div>
                    </div>
                    <div class='hero-stat'>
                        <div class='hero-stat-label'>Dữ liệu phiên</div>
                        <div class='hero-stat-value'>{cached_count}</div>
                        <div class='hero-stat-sub'>Bản ghi hiện có trong bộ nhớ phiên của ứng dụng.</div>
                    </div>
                    <div class='hero-stat'>
                        <div class='hero-stat-label'>Định vị sản phẩm</div>
                        <div class='hero-stat-value'>Premium</div>
                        <div class='hero-stat-sub'>Đang được phát triển thêm.</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        """
        <div class='sidebar-shell'>
            <div class='sidebar-kicker'>Bioinformatics Platform</div>
            <h2 class='sidebar-title'>🧬 AgriGene Explorer</h2>
            <div class='sidebar-desc'>Giao diện cao cấp cho truy vấn NCBI, phân tích FASTA, trực quan hóa dữ liệu gen nông nghiệp và trình diễn chuyên môn.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    setup_ready = bool(st.session_state.get("ncbi_email"))
    status_text = "Đã sẵn sàng kết nối NCBI" if setup_ready else "Chưa cấu hình kết nối NCBI"
    st.markdown(
        f"<div class='status-chip'>{'🟢' if setup_ready else '🟠'} {status_text}</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    page = st.radio(
        "Điều hướng",
        [
            "🔍 Khám phá Gen",
            "🧬 Phòng thí nghiệm Trình tự",
            "📊 Bảng điều khiển Sinh học",
            "⚙️ Cài đặt Hệ thống",
        ],
    )

    st.divider()
    st.caption("Luồng sử dụng đề xuất: cấu hình hệ thống → truy vấn gen → phân tích trình tự → trực quan hóa và trình bày kết quả.")


if page == "🔍 Khám phá Gen":
    records = st.session_state.get("search_results")
    render_hero(
        "Không gian Khám phá Gen",
        "Tổ chức khu vực tìm kiếm theo phong cách sản phẩm khoa học cao cấp, giúp bài thi và buổi demo trông gọn, rõ, chuyên nghiệp hơn ngay từ lượt nhìn đầu tiên.",
        badges=["NCBI Entrez", "Metadata xuất chuẩn", "Gene discovery", "Competition-ready UI"],
    )

    species_count = records["Organism"].nunique() if isinstance(records, pd.DataFrame) and not records.empty and "Organism" in records.columns else 0
    dominant_type = safe_mode(records["Gene Type"]) if isinstance(records, pd.DataFrame) and not records.empty and "Gene Type" in records.columns else "N/A"

    left, right = st.columns([1.12, 0.88])

    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_section("Bảng điều khiển truy vấn")
        st.markdown("<div class='tiny-note'>Thiết kế phần nhập liệu rõ khối, thuận lợi khi trình bày trước giám khảo: thao tác ngắn, nhãn dễ hiểu, ưu tiên trọng tâm khoa học.</div>", unsafe_allow_html=True)

        query = st.text_input("Từ khóa gen", placeholder="Ví dụ: rbcL, matK, chloroplast, drought resistance...")
        top_agri_organisms = [
            "",
            "Oryza sativa",
            "Zea mays",
            "Glycine max",
            "Solanum lycopersicum",
            "Triticum aestivum",
            "Solanum tuberosum",
            "Gossypium hirsutum",
            "Brassica napus",
            "Saccharum officinarum",
            "Arachis hypogaea",
        ]
        organism = st.selectbox("Loài mục tiêu", top_agri_organisms)
        gene_type = st.selectbox("Loại sequence", ["All", "CDS", "mRNA", "rRNA", "genomic"])

        cta1, cta2 = st.columns(2)
        with cta1:
            search_clicked = st.button("Chạy tìm kiếm", type="primary", use_container_width=True)
        with cta2:
            clear_clicked = st.button("Làm mới phiên", use_container_width=True)

        if clear_clicked:
            st.session_state["search_results"] = None
            st.success("Đã làm mới dữ liệu tìm kiếm trong phiên hiện tại.")

        st.markdown("</div>", unsafe_allow_html=True)


    if not st.session_state.get("ncbi_email"):
        st.warning("Bạn cần cấu hình Email NCBI ở trang Cài đặt Hệ thống trước khi bắt đầu truy vấn dữ liệu.")
    elif search_clicked:
        if not query and not organism:
            st.error("Vui lòng nhập ít nhất từ khóa gen hoặc tên loài.")
        else:
            with st.spinner("Đang truy vấn NCBI Entrez..."):
                id_list = NCBIFetcher.search_sequences(
                    query,
                    organism,
                    gene_type,
                    st.session_state["max_results"],
                )

                if not id_list:
                    st.info("Không tìm thấy sequence phù hợp.")
                else:
                    st.info(f"Đã tìm thấy {len(id_list)} sequence. Đang tải metadata...")
                    progress_bar = st.progress(10)
                    df_records = NCBIFetcher.fetch_records(id_list)
                    progress_bar.progress(100)
                    if not df_records.empty:
                        st.session_state["search_results"] = df_records
                        st.success(f"Đã nạp {len(df_records)} bản ghi vào bảng điều khiển.")
                    else:
                        st.error("Không thể tải metadata cho các ID đã truy vấn.")

    df_records = st.session_state.get("search_results")
    if isinstance(df_records, pd.DataFrame) and not df_records.empty:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_section("Kết quả nghiên cứu")
        tabs = st.tabs(["Tổng quan", "Bảng dữ liệu", "Xuất dữ liệu"])
        with tabs[0]:
            c1, c2, c3 = st.columns(3)
            c1.metric("Số bản ghi", len(df_records))
            c2.metric("Số loài", df_records["Organism"].nunique() if "Organism" in df_records.columns else 0)
            c3.metric("Loại phổ biến", safe_mode(df_records["Gene Type"]) if "Gene Type" in df_records.columns else "N/A")
            st.markdown("<div class='premium-callout'>Khối tổng quan này nên được dùng khi thuyết trình vì nó cho thấy ngay quy mô dữ liệu, độ đa dạng loài và đặc trưng loại sequence của lượt truy vấn.</div>", unsafe_allow_html=True)
        with tabs[1]:
            st.dataframe(df_records, use_container_width=True, height=440)
        with tabs[2]:
            csv = df_records.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Xuất Metadata CSV",
                data=csv,
                file_name="agrigene_results.csv",
                mime="text/csv",
            )
        st.markdown("</div>", unsafe_allow_html=True)


elif page == "🧬 Phòng thí nghiệm Trình tự":
    render_hero(
        "Phòng thí nghiệm Trình tự",
        "Biến phần phân tích FASTA thành một khu vực có cảm giác như công cụ nghiên cứu thực thụ: sang, rõ, có nhịp trình bày và đủ sức thuyết phục trong thi chuyên môn.",
        badges=["FASTA", "ORF", "Protein translation", "Nucleotide profile"],
    )

    input_method = st.radio("Chế độ nhập", ["Dán FASTA", "Accession NCBI"], horizontal=True)
    seq_data = ""
    header = ""

    left, right = st.columns([1.08, 0.92])

    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_section("Nguồn trình tự", "🧬")
        if input_method == "Dán FASTA":
            raw_fasta = st.text_area(
                "Dán chuỗi FASTA",
                height=260,
                placeholder=">sample_gene\nATGAAACCCGGGTTTAA...",
            )
            if raw_fasta:
                lines = raw_fasta.split("\n")
                if lines[0].startswith(">"):
                    header = lines[0]
                    seq_data = "".join(lines[1:]).replace(" ", "").replace("\n", "")
                else:
                    seq_data = raw_fasta.replace(" ", "").replace("\n", "")
        else:
            acc_id = st.text_input("Accession ID", placeholder="Ví dụ: NM_001159351")
            if st.button("Tải từ NCBI", type="primary", use_container_width=True):
                if not st.session_state["ncbi_email"]:
                    st.error("Bạn chưa cấu hình Email NCBI trong Cài đặt Hệ thống.")
                elif acc_id:
                    with st.spinner(f"Đang tải accession {acc_id}..."):
                        header, seq_data = NCBIFetcher.fetch_fasta(acc_id)
                        if seq_data:
                            st.success("Đã tải FASTA thành công từ NCBI.")
                else:
                    st.warning("Vui lòng nhập Accession ID.")
        st.markdown("</div>", unsafe_allow_html=True)


    if seq_data:
        stats = get_basic_stats(seq_data)
        orfs = find_orfs(seq_data)

        plot_col, right_col = st.columns([1.02, 0.98])
        with plot_col:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            render_section("Thành phần nucleotide")
            st.plotly_chart(apply_plot_theme(plot_nucleotide_composition(stats)), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right_col:
            tabs = st.tabs(["Bảng ORF", "Dịch Protein"])
            with tabs[0]:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                render_section("Bảng ORF")
                if orfs:
                    df_orfs = pd.DataFrame(orfs, columns=["Bắt đầu (nt)", "Kết thúc (nt)", "Khung đọc"])
                    st.dataframe(df_orfs, use_container_width=True, height=360)
                else:
                    st.info("Không phát hiện ORF phù hợp theo điều kiện hiện tại.")
                st.markdown("</div>", unsafe_allow_html=True)
            with tabs[1]:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                render_section("Dịch Protein", "🧬")
                if st.button("Dịch DNA sang Protein", type="primary"):
                    protein_seq = translate_sequence(seq_data)
                    st.text_area("Chuỗi axit amin", value=protein_seq, height=220)
                else:
                    st.markdown("<div class='premium-callout'>Nhấn nút dịch protein để tạo ra chuỗi axit amin và dùng phần này như điểm nhấn trong bài trình bày về pipeline phân tích sinh học phân tử.</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)


elif page == "Bảng điều khiển Sinh học":
    df = st.session_state.get("search_results")
    render_hero(
        "Bảng điều khiển Sinh học",
        "Tập trung vào bố cục có chiều sâu thị giác, phù hợp với thi học thuật: nhìn vào là thấy dữ liệu, tầng thông tin, và cách kể chuyện khoa học rõ ràng.",
        badges=["Dashboard premium", "Data storytelling", "Research presentation", "Visual hierarchy"],
    )

    if isinstance(df, pd.DataFrame) and not df.empty:
        records_count = len(df)
        organisms = df["Organism"].nunique() if "Organism" in df.columns else 0
        dominant = safe_mode(df["Gene Type"]) if "Gene Type" in df.columns else "N/A"
    else:
        records_count = 0
        organisms = 0
        dominant = "N/A"

    source_col, state_col = st.columns([1.05, 0.95])
    with source_col:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_section("Nguồn dữ liệu")
        uploaded_file = st.file_uploader("Tải lên CSV metadata", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
        st.markdown("<div class='tiny-note'>Bạn có thể dùng dữ liệu từ tab Khám phá Gen hoặc nạp CSV riêng để trình bày nhiều kịch bản phân tích khác nhau.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


    if isinstance(df, pd.DataFrame) and not df.empty:
        top_row = st.columns(2)
        bottom_row = st.columns(2)

        with top_row[0]:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            render_section("Phân bố độ dài sequence")
            st.plotly_chart(apply_plot_theme(plot_length_distribution(df)), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with top_row[1]:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            render_section("Thành phần loài")
            st.plotly_chart(apply_plot_theme(plot_organism_pie(df)), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with bottom_row[0]:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            render_section("Mốc thời gian nộp dữ liệu")
            st.plotly_chart(apply_plot_theme(plot_submission_timeline(df)), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with bottom_row[1]:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            render_section("Bản đồ nhiệt GC")
            st.plotly_chart(apply_plot_theme(plot_gc_heatmap(df)), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='premium-callout'>Gợi ý diễn giải: dùng biểu đồ phân bố độ dài để phát hiện ngoại lệ, biểu đồ thành phần loài để nhận diện thiên lệch mẫu, timeline để thấy động lực tăng trưởng dữ liệu, và bản đồ nhiệt GC để thảo luận cấu trúc trình tự giữa các nhóm.</div>", unsafe_allow_html=True)
    else:
        st.info("Chưa có dữ liệu để hiển thị bảng điều khiển.")


elif page == "⚙️ Cài đặt Hệ thống":
    render_hero(
        "Cài đặt Hệ thống",
        "Giữ phần cấu hình gọn nhưng sang: đủ độ tin cậy để trình bày như một sản phẩm hoàn thiện thay vì một bản demo vội vàng.",
        badges=["System access", "NCBI setup", "Stable workflow", "Professional finish"],
    )

    left, right = st.columns([1.02, 0.98])

    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_section("Thiết lập truy cập NCBI", "🔐")
        st.markdown(
            "<div class='tiny-note'>NCBI yêu cầu email để sử dụng E-utilities. Khóa API là tùy chọn nhưng giúp tăng giới hạn request và tạo cảm giác sản phẩm được chuẩn bị nghiêm túc.</div>",
            unsafe_allow_html=True,
        )
        with st.form("settings_form"):
            email_input = st.text_input(
                "Email NCBI",
                value=st.session_state["ncbi_email"],
                placeholder="you@example.com",
            )
            api_key_input = st.text_input(
                "Khóa API",
                value=st.session_state["ncbi_api_key"],
                type="password",
            )
            max_res = st.slider(
                "Số kết quả tìm kiếm tối đa",
                min_value=10,
                max_value=200,
                value=st.session_state["max_results"],
                step=10,
            )
            submitted = st.form_submit_button("Lưu cấu hình", use_container_width=True)
            if submitted:
                if not is_valid_email(email_input):
                    st.error("Định dạng email chưa hợp lệ.")
                else:
                    st.session_state["ncbi_email"] = email_input
                    st.session_state["ncbi_api_key"] = api_key_input
                    st.session_state["max_results"] = max_res
                    st.success("Đã lưu cấu hình hệ thống thành công.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_section("Tình trạng nền tảng", "🛰️")
        st.metric("Email NCBI", "Đã cấu hình" if st.session_state["ncbi_email"] else "Chưa đặt")
        st.metric("Khóa API", "Đã lưu" if st.session_state["ncbi_api_key"] else "Trống")
        st.metric("Số kết quả tối đa", st.session_state["max_results"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        