import html
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import streamlit as st

st.set_page_config(page_title="E-Commerce Analytics | 2017", page_icon="📊", layout="wide")

NAVY = "#18243A"
BLUE = "#5277E8"
TEAL = "#25A79B"
CORAL = "#F07878"
GRAY = "#748094"

# iOS-style aesthetic: native system font (SF Pro on Apple devices), restrained accents.
st.markdown("""
<style>
:root {color-scheme:light;}
html, body, [class*="css"], [data-testid="stApp"],
[data-testid="stSidebar"], button, input, textarea, select {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
    "Segoe UI Variable", "Segoe UI", Inter, sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: #F7F8FC;
    color: #18243A;
}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #EDF0F5;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap: 0.8rem;}
.block-container {max-width: 1240px; padding: 2.2rem 2.4rem 4rem;}
h1, h2, h3, h4, p, label {letter-spacing: -0.025em;}
h1, h2, h3 {color: #18243A; font-weight: 720 !important;}
h2 {font-size: 1.55rem !important; margin-top: .8rem;}
h3 {font-size: 1.13rem !important; margin-top: .7rem;}
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 12px;
    padding: 8px 10px;
    transition: background .2s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {background: #F2F5FC;}
[data-testid="stSidebar"] hr {border-color: #EEF0F5;}
.hero {padding: .8rem 0 1.55rem;}
.eyebrow {color:#5277E8; font-size:.73rem; font-weight:750; letter-spacing:.12em;}
.hero-title {
    font-size:clamp(2rem,3.3vw,3rem);
    font-weight:760;
    letter-spacing:-.055em;
    color:#18243A;
    line-height:1.08;
    margin:.5rem 0 .7rem;
}
.hero-text {color:#748094; font-size:1rem; letter-spacing:-.012em; line-height:1.55;}
.kpi {
    background:#FFFFFF;
    border:1px solid #EDF0F5;
    border-radius:20px;
    padding:21px 20px 19px;
    min-height:136px;
    box-shadow:0 6px 24px rgba(19,37,71,.035);
    overflow:hidden;
    position:relative;
}
.kpi:before {
    content:""; display:block; width:31px; height:5px; background:var(--accent);
    border-radius:10px; margin-bottom:15px;
}
.kpi-label {font-size:.73rem; font-weight:700; color:#7D8999; letter-spacing:.08em;}
.kpi-value {
    font-size:clamp(1.4rem,2.25vw,2.15rem); font-weight:740;
    color:#18243A; white-space:nowrap; letter-spacing:-.05em; line-height:1.5;
}
.kpi-note {font-size:.74rem; color:#8A94A4; overflow-wrap:anywhere; line-height:1.35;}
.insight {
    background:#EEF2FF;
    padding:17px 20px;
    border-radius:16px;
    border:1px solid #DFE7FF;
    color:#344569;
    margin:.7rem 0 1.4rem;
    line-height:1.6;
    letter-spacing:-.008em;
}
[data-testid="stDataFrame"] {
    background:#fff; border:1px solid #EDF0F5; border-radius:16px; overflow:hidden;
}
[data-testid="stExpander"] {background:#fff; border:1px solid #EDF0F5; border-radius:15px;}
[data-testid="stSelectSlider"] {margin-bottom:12px;}
hr {border-color:#E8ECF3 !important; margin: 1.45rem 0 !important;}
@media (max-width: 800px) {
 .block-container {padding:1.2rem .9rem 2rem;}
 .kpi {padding:15px 14px; min-height:112px;}
 .kpi-value {font-size:1.45rem;}
 .hero-title {font-size:2rem;}
}
</style>
""", unsafe_allow_html=True)


def fmt_money(value):
    return f"R$ {value:,.2f}"


def fmt_short_money(value):
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:,.1f}K"
    return fmt_money(value)


def kpi(label, value, detail, accent):
    st.markdown(
        f'<div class="kpi" style="--accent:{accent}">'
        f'<div class="kpi-label">{html.escape(label)}</div>'
        f'<div class="kpi-value">{html.escape(value)}</div>'
        f'<div class="kpi-note">{html.escape(detail)}</div></div>',
        unsafe_allow_html=True,
    )


def insight(message):
    st.markdown(f'<div class="insight">{message}</div>', unsafe_allow_html=True)


def polish(ax, grid="y"):
    ax.set_facecolor("white")
    ax.set_axisbelow(True)
    ax.grid(axis=grid, color="#E9EDF4", linewidth=.7)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0, labelcolor=NAVY, labelsize=9)


@st.cache_data(show_spinner="Memuat dataset...")
def load_data():
    directory = Path(__file__).resolve().parent / "data"
    customer = pd.read_csv(directory / "customers_dataset.csv")
    orders = pd.read_csv(directory / "orders_dataset.csv")
    items = pd.read_csv(directory / "order_items_dataset.csv")
    products = pd.read_csv(directory / "products_dataset.csv")
    translation = pd.read_csv(directory / "product_category_name_translation.csv")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    products["product_category_name"] = products["product_category_name"].fillna("unknown")
    orders_customer = orders.merge(
        customer[["customer_id", "customer_unique_id"]],
        on="customer_id", how="left", validate="many_to_one"
    )
    valid_orders = orders_customer.loc[
        orders_customer["order_status"].eq("delivered")
        & orders_customer["order_purchase_timestamp"].dt.year.eq(2017)
    ].copy()
    sales = items.merge(
        valid_orders[["order_id", "customer_unique_id", "order_purchase_timestamp"]],
        on="order_id", how="inner", validate="many_to_one"
    )
    sales = sales.merge(
        products[["product_id", "product_category_name"]],
        on="product_id", how="left", validate="many_to_one"
    ).merge(translation, on="product_category_name", how="left", validate="many_to_one")
    sales["category"] = sales["product_category_name_english"].fillna(
        sales["product_category_name"]
    ).fillna("unknown")
    sales["sales_value"] = sales["price"]  # tidak termasuk freight
    sales["month"] = sales["order_purchase_timestamp"].dt.to_period("M").astype(str)
    return sales


@st.cache_data(show_spinner="Menghitung sales dan RFM...")
def analyse(sales):
    monthly = (sales.groupby("month", as_index=False)
               .agg(total_sales=("sales_value", "sum"), total_orders=("order_id", "nunique"))
               .sort_values("month").reset_index(drop=True))
    category = (sales.groupby("category", as_index=False)
                .agg(total_sales=("sales_value", "sum"), total_orders=("order_id", "nunique"))
                .sort_values("total_sales", ascending=False).reset_index(drop=True))
    category["contribution_pct"] = category["total_sales"] / category["total_sales"].sum() * 100

    by_order = (sales.groupby(["customer_unique_id", "order_id"], as_index=False)
                .agg(order_date=("order_purchase_timestamp", "max"),
                     order_value=("sales_value", "sum")))
    rfm = (by_order.groupby("customer_unique_id", as_index=False)
           .agg(last_purchase=("order_date", "max"),
                frequency=("order_id", "nunique"),
                monetary=("order_value", "sum")))
    rfm["recency"] = (pd.Timestamp("2018-01-01") - rfm["last_purchase"]).dt.days
    rfm["R_score"] = pd.cut(
        rfm["recency"], bins=[-1, 30, 90, 180, 270, float("inf")],
        labels=[5, 4, 3, 2, 1]
    ).astype(int)
    rfm["F_score"] = rfm["frequency"].clip(upper=5)
    rfm["M_score"] = pd.qcut(
        rfm["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    def segment(row):
        if row["R_score"] >= 4 and row["F_score"] >= 2:
            return "Loyal Customers"
        if row["R_score"] >= 4:
            return "Recent Customers"
        if row["R_score"] <= 2 and row["M_score"] >= 4:
            return "At Risk High Value"
        if row["R_score"] <= 2:
            return "Inactive Customers"
        return "Regular Customers"

    rfm["segment"] = rfm.apply(segment, axis=1)
    summary = (rfm.groupby("segment", as_index=False)
               .agg(total_customers=("customer_unique_id", "nunique"),
                    avg_recency=("recency", "mean"),
                    avg_frequency=("frequency", "mean"),
                    avg_monetary=("monetary", "mean"),
                    total_monetary=("monetary", "sum")))
    summary["percentage"] = summary["total_customers"] / summary["total_customers"].sum() * 100
    return monthly, category, rfm, summary


def chart_monthly(monthly):
    fig, ax = plt.subplots(figsize=(10.4, 4.2), dpi=115)
    fig.patch.set_facecolor("white")
    x = list(range(len(monthly)))
    values = monthly["total_sales"].to_numpy()
    ax.plot(x, values, color=BLUE, marker="o", markersize=5, linewidth=2.5)
    pos = int(monthly["total_sales"].argmax())
    ax.scatter([pos], [values[pos]], s=80, color=CORAL, zorder=4)
    ax.annotate(fmt_short_money(values[pos]), (pos, values[pos]),
                xytext=(0, 14), textcoords="offset points", ha="center",
                color=CORAL, weight="bold", fontsize=10)
    ax.set_xticks(x, pd.to_datetime(monthly["month"]).dt.strftime("%b"))
    ax.set_ylim(bottom=0, top=values.max() * 1.23)
    ax.set_ylabel("Penjualan (R$)", color=NAVY)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v / 1000:,.0f}K"))
    polish(ax)
    fig.tight_layout()
    return fig


def chart_category(category, top_n):
    data = category.head(top_n).sort_values("total_sales")
    fig, ax = plt.subplots(figsize=(10.4, max(4.2, top_n * .48)), dpi=115)
    fig.patch.set_facecolor("white")
    peak = category.iloc[0]["category"]
    colors = [CORAL if name == peak else BLUE for name in data["category"]]
    bars = ax.barh(data["category"].str.replace("_", " ").str.title(),
                   data["total_sales"], color=colors, height=.65)
    max_value = data["total_sales"].max()
    for bar, val, pct in zip(bars, data["total_sales"], data["contribution_pct"]):
        ax.text(val + max_value * .015, bar.get_y() + bar.get_height() / 2,
                f"{val / 1000:,.0f}K  |  {pct:.1f}%", va="center", fontsize=9, color=NAVY)
    ax.set_xlim(0, max_value * 1.45)
    ax.set_xlabel("Penjualan (R$)", color=NAVY)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v / 1000:,.0f}K"))
    polish(ax, grid="x")
    fig.tight_layout()
    return fig


def chart_segment(summary):
    data = summary.sort_values("total_customers")
    fig, ax = plt.subplots(figsize=(10.4, 4.4), dpi=115)
    fig.patch.set_facecolor("white")
    colors = [CORAL if s == "At Risk High Value" else TEAL for s in data["segment"]]
    bars = ax.barh(data["segment"], data["total_customers"], color=colors, height=.62)
    max_value = data["total_customers"].max()
    for bar, val, pct in zip(bars, data["total_customers"], data["percentage"]):
        ax.text(val + max_value * .014, bar.get_y() + bar.get_height() / 2,
                f"{val:,}  ({pct:.2f}%)", va="center", fontsize=9, color=NAVY)
    ax.set_xlim(0, max_value * 1.37)
    ax.set_xlabel("Jumlah pelanggan", color=NAVY)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:,.0f}"))
    polish(ax, grid="x")
    fig.tight_layout()
    return fig


def show_chart(fig):
    st.pyplot(fig, width="stretch")
    plt.close(fig)


try:
    sales = load_data()
    monthly, category, rfm, summary = analyse(sales)
except (FileNotFoundError, KeyError, ValueError) as error:
    st.error("Data belum berhasil dimuat. Pastikan lima CSV asli ada di folder 'data' dan kolomnya sesuai dataset Olist.")
    st.code(str(error))
    st.stop()

with st.sidebar:
    st.title("◈ E-Commerce")
    st.caption("2017 ANALYTICS DASHBOARD")
    st.divider()
    page = st.radio("Navigasi", ["Overview", "Sales Performance", "Customer Segmentation"])
    st.divider()
    st.markdown("**Periode:** Januari–Desember 2017")
    st.markdown("**Status:** Delivered")
    st.markdown("**Mata uang:** Brazilian Real (R$)")
    st.caption("Sumber: Brazilian E-Commerce Public Dataset by Olist")

st.markdown(
    '<div class="hero"><div class="eyebrow">BUSINESS INTELLIGENCE · 2017</div>'
    '<div class="hero-title">E-Commerce Analytics Dashboard</div>'
    '<div class="hero-text">Sales performance dan segmentasi pelanggan berdasarkan transaksi berhasil dikirim selama 2017.</div></div>',
    unsafe_allow_html=True,
)

cols = st.columns(4, gap="small")
with cols[0]:
    kpi("TOTAL SALES", fmt_short_money(sales["sales_value"].sum()),
        f"Nilai tepat: {fmt_money(sales['sales_value'].sum())}", BLUE)
with cols[1]:
    kpi("TOTAL ORDERS", f"{sales['order_id'].nunique():,}", "Pesanan delivered", NAVY)
with cols[2]:
    kpi("UNIQUE CUSTOMERS", f"{sales['customer_unique_id'].nunique():,}", "Pelanggan unik", TEAL)
with cols[3]:
    kpi("ORDER ITEMS", f"{len(sales):,}", "Baris item pesanan", CORAL)
st.write("")

peak = monthly.loc[monthly["total_sales"].idxmax()]
leading = category.iloc[0]
at_risk = summary.loc[summary["segment"].eq("At Risk High Value")].iloc[0]

if page == "Overview":
    st.header("Business Overview")
    st.caption("Ringkasan dua fokus analisis: tren penjualan dan segmentasi pelanggan.")
    st.subheader("Tren Nilai Penjualan Bulanan")
    show_chart(chart_monthly(monthly))
    insight(f"<b>Temuan utama:</b> Puncak penjualan terjadi pada <b>{html.escape(peak['month'])}</b> "
            f"sebesar <b>{fmt_money(peak['total_sales'])}</b>.")
    st.subheader("Distribusi Segmen Pelanggan")
    show_chart(chart_segment(summary))
    insight(f"<b>Prioritas retensi:</b> <b>At Risk High Value</b> terdiri dari "
            f"<b>{at_risk['total_customers']:,} pelanggan</b> "
            f"({at_risk['percentage']:.2f}%) yang bernilai tinggi tetapi sudah lama tidak bertransaksi.")

elif page == "Sales Performance":
    st.header("Sales Performance")
    st.markdown("**Pertanyaan bisnis:** Bagaimana perkembangan total nilai penjualan bulanan dan kategori produk apa yang memberikan kontribusi penjualan terbesar selama Januari–Desember 2017?")
    st.subheader("Monthly Sales Trend")
    show_chart(chart_monthly(monthly))
    first, last = monthly.iloc[0], monthly.iloc[-1]
    insight(f"<b>Insight:</b> Penjualan naik dari <b>{fmt_money(first['total_sales'])}</b> "
            f"pada Januari ke <b>{fmt_money(last['total_sales'])}</b> pada Desember, "
            f"meskipun terjadi fluktuasi antarbulan. Puncaknya pada November "
            f"(<b>{fmt_money(peak['total_sales'])}</b>), lalu menurun pada Desember.")
    with st.expander("Lihat data penjualan per bulan"):
        st.dataframe(monthly.rename(columns={"month": "Bulan", "total_sales": "Total Sales (R$)",
                                                 "total_orders": "Total Orders"}).style.format(
            {"Total Sales (R$)": "{:,.2f}", "Total Orders": "{:,.0f}"}),
            hide_index=True, width="stretch")
    st.subheader("Kontribusi Kategori Produk")
    top_n = st.select_slider("Jumlah kategori yang ditampilkan", options=[5, 10, 15], value=10)
    show_chart(chart_category(category, top_n))
    insight(f"<b>Kategori terbesar:</b> <b>{html.escape(str(leading['category']))}</b> "
            f"menyumbang <b>{fmt_money(leading['total_sales'])}</b> "
            f"atau <b>{leading['contribution_pct']:.2f}%</b> dari total penjualan.")
    st.dataframe(category.head(top_n).rename(columns={
        "category": "Category", "total_sales": "Sales (R$)",
        "total_orders": "Orders", "contribution_pct": "Contribution (%)"
    }).style.format({"Sales (R$)": "{:,.2f}", "Orders": "{:,.0f}",
                     "Contribution (%)": "{:.2f}%"}), hide_index=True, width="stretch")
    st.markdown("**Rekomendasi:** Prioritaskan pengelolaan stok dan promosi kategori dengan kontribusi besar. Gunakan pola lonjakan menjelang November sebagai masukan perencanaan kapasitas dan kampanye, tanpa menganggap pola satu tahun pasti berulang.")

else:
    st.header("Customer Segmentation · RFM")
    st.markdown("**Pertanyaan bisnis:** Bagaimana segmentasi berdasarkan Recency, Frequency, dan Monetary selama Januari–Desember 2017, serta segmen mana yang perlu diprioritaskan untuk retensi?")
    st.subheader("Distribusi Segmen Pelanggan")
    show_chart(chart_segment(summary))
    insight(f"<b>Prioritas retensi — At Risk High Value:</b> "
            f"<b>{at_risk['total_customers']:,}</b> pelanggan "
            f"({at_risk['percentage']:.2f}%), rata-rata recency "
            f"<b>{at_risk['avg_recency']:.2f} hari</b> dan monetary "
            f"<b>{fmt_money(at_risk['avg_monetary'])}</b>. "
            "Segmen ini ditandai coral untuk menyorot prioritas, bukan jumlah pelanggan terbanyak.")
    st.subheader("RFM Summary")
    formatted = summary.sort_values("total_customers", ascending=False).rename(columns={
        "segment": "Segment", "total_customers": "Customers", "avg_recency": "Avg. Recency (days)",
        "avg_frequency": "Avg. Frequency", "avg_monetary": "Avg. Monetary (R$)",
        "total_monetary": "Total Monetary (R$)", "percentage": "Share (%)"
    })
    st.dataframe(formatted.style.format({
        "Customers": "{:,.0f}", "Avg. Recency (days)": "{:.2f}",
        "Avg. Frequency": "{:.2f}", "Avg. Monetary (R$)": "{:,.2f}",
        "Total Monetary (R$)": "{:,.2f}", "Share (%)": "{:.2f}%"
    }), hide_index=True, width="stretch")
    st.subheader("Rata-rata RFM")
    rr = st.columns(3)
    with rr[0]:
        kpi("RECENCY", f"{rfm['recency'].mean():.2f} hari", "Sejak transaksi terakhir", BLUE)
    with rr[1]:
        kpi("FREQUENCY", f"{rfm['frequency'].mean():.2f}", "Pesanan per pelanggan", TEAL)
    with rr[2]:
        kpi("MONETARY", fmt_short_money(rfm["monetary"].mean()), "Rata-rata nilai belanja", CORAL)
    st.subheader("Strategi Retensi")
    st.markdown("**At Risk High Value:** kampanye reaktivasi terarah; **Recent Customers:** insentif pembelian kedua; **Loyal Customers:** program loyalitas; **Regular Customers:** promosi untuk meningkatkan frekuensi; **Inactive Customers:** reaktivasi selektif sesuai potensi pelanggan.")
    with st.expander("Metodologi dan aturan segmentasi RFM"):
        st.markdown("""
**Unit analisis:** `customer_unique_id`, berdasarkan pesanan berstatus *delivered* tahun 2017.

- **Recency (R):** selisih hari antara tanggal pembelian terakhir dan **1 Januari 2018**. Skor 5: ≤30 hari; 4: 31–90; 3: 91–180; 2: 181–270; 1: >270 hari.
- **Frequency (F):** jumlah pesanan unik per pelanggan; skor = jumlah tersebut dengan batas atas 5.
- **Monetary (M):** total harga item yang dibeli per pelanggan (tanpa ongkir); skor 1–5 dari kuintil peringkat Monetary.
- **Loyal Customers:** R ≥ 4 dan F ≥ 2.
- **Recent Customers:** R ≥ 4, selain Loyal.
- **At Risk High Value:** R ≤ 2 dan M ≥ 4.
- **Inactive Customers:** R ≤ 2, selain At Risk High Value.
- **Regular Customers:** pelanggan lain.

Aturan diterapkan **berurutan** sesuai urutan di atas. RFM ini bersifat deskriptif dan tidak memakai model machine learning.
""")

st.divider()
with st.expander("Sumber data dan batasan analisis"):
    st.markdown("""
- **Dataset:** Brazilian E-Commerce Public Dataset by Olist.
- **Cakupan:** pesanan berstatus *delivered* dengan tanggal pembelian pada Januari–Desember 2017.
- **Penjualan:** penjumlahan kolom `price` pada detail item, **tidak termasuk ongkos kirim (`freight_value`)**. Angka bukan pendapatan bersih atau laba.
- **Jumlah order:** `order_id` unik; **jumlah pelanggan:** `customer_unique_id` unik; **order items:** jumlah baris detail item.
- **Kategori:** nama kategori versi Inggris bila tersedia, jika tidak menggunakan nama asli.
- **RFM:** dihitung untuk pelanggan dengan transaksi *delivered* pada periode tersebut, menggunakan tanggal acuan 1 Januari 2018. Temuan tidak otomatis mewakili kondisi pelanggan saat ini.
""")
st.caption("Sumber: Brazilian E-Commerce Public Dataset by Olist | Delivered orders 2017 | Mata uang R$")
