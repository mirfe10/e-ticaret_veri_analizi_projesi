import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from scipy import stats
import statsmodels.api as sm
import json
import os
# ----------------------------------------
# 1. SAYFA AYARLARI VE RENK PALETLERİ
# ----------------------------------------
st.set_page_config(page_title="E-Ticaret Veri Analizi Projesi", page_icon="📊", layout="wide")

# Modern Renk Paletleri
plotly_colors_app2 = ["#FF8C00", "#8A2BE2", "#FFA500", "#9370DB", "#FF7F50"]  # Turuncu-Mor
plotly_colors_app1 = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]  # Modern Teal-Orange

current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = current_dir + "/"


# ----------------------------------------
# 2. VERİ YÜKLEME FONKSİYONLARI
# ----------------------------------------
@st.cache_data
def load_geo_data():
    df_customer = pd.read_csv(BASE_PATH + "olist_customers_dataset.csv")
    df_order = pd.read_csv(BASE_PATH + "olist_orders_dataset.csv")
    df_order_item = pd.read_csv(BASE_PATH + "olist_order_items_dataset.csv")
    df_product = pd.read_csv(BASE_PATH + "olist_products_dataset.csv")

    with open(BASE_PATH + 'brazil_states.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    df_order = df_order[df_order['order_status'] == 'delivered'].copy()
    df_order.dropna(subset=['order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date'],
                    inplace=True)

    tr_dict = {
        'cama_mesa_banho': 'Yatak & Banyo', 'esporte_lazer': 'Spor & Eğlence',
        'moveis_decoracao': 'Mobilya & Dekorasyon',
        'beleza_saude': 'Güzellik & Sağlık', 'utilidades_domesticas': 'Ev Eşyaları', 'automotivo': 'Otomotiv',
        'informatica_acessorios': 'Bilgisayar Aksesuar', 'brinquedos': 'Oyuncaklar',
        'relogios_presentes': 'Saat & Hediyelik',
        'telefonia': 'Telefon', 'bebes': 'Bebek Ürünleri', 'perfumaria': 'Parfümeri', 'papelaria': 'Kırtasiye',
        'fashion_bolsas_e_acessorios': 'Moda & Çanta', 'cool_stuff': 'Trend Eşyalar',
        'ferramentas_jardim': 'Bahçe Aletleri',
        'pet_shop': 'Pet Shop', 'eletronicos': 'Elektronik'
    }
    df_product['product_category_name'] = df_product['product_category_name'].map(tr_dict).fillna(
        df_product['product_category_name'].str.replace('_', ' ').str.title())
    df_product['product_category_name'] = df_product['product_category_name'].fillna('Diger')

    for col in ['product_name_lenght', 'product_description_lenght', 'product_photos_qty']:
        df_product[col] = df_product[col].fillna(df_product[col].median())
    df_product.dropna(subset=['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'],
                      inplace=True)

    df_master = pd.merge(df_order, df_order_item, on='order_id', how='inner')
    df_master = pd.merge(df_master, df_product, on='product_id', how='inner')
    df_master = pd.merge(df_master,
                         df_customer[['customer_id', 'customer_city', 'customer_state', 'customer_zip_code_prefix']],
                         on='customer_id', how='inner')

    df_master['order_purchase_timestamp'] = pd.to_datetime(df_master['order_purchase_timestamp'])
    df_master['order_delivered_customer_date'] = pd.to_datetime(df_master['order_delivered_customer_date'])
    df_master['delivery_days'] = (
                df_master['order_delivered_customer_date'] - df_master['order_purchase_timestamp']).dt.days
    df_master['order_month'] = df_master['order_purchase_timestamp'].dt.to_period('M').astype(str)

    return df_master, geojson_data


@st.cache_data
def load_payment_data():
    try:
        payments = pd.read_csv(BASE_PATH + 'olist_order_payments_dataset.csv')
        items = pd.read_csv(BASE_PATH + 'olist_order_items_dataset.csv')
        products = pd.read_csv(BASE_PATH + 'olist_products_dataset.csv')
        translation = pd.read_csv(BASE_PATH + 'product_category_name_translation.csv')
        if 'order_id' not in items.columns:
            raise ValueError("Bölgesel ayar tetiklendi.")
    except:
        payments = pd.read_csv(BASE_PATH + 'olist_order_payments_dataset.csv', sep=';')
        items = pd.read_csv(BASE_PATH + 'olist_order_items_dataset.csv', sep=';')
        products = pd.read_csv(BASE_PATH + 'olist_products_dataset.csv', sep=';')
        translation = pd.read_csv(BASE_PATH + 'product_category_name_translation.csv', sep=';')

    for d in [payments, items, products, translation]:
        d.columns = d.columns.str.strip()

    df = payments.merge(items, on='order_id', how='inner')
    df = df.merge(products, on='product_id', how='inner')
    df = df.merge(translation, on='product_category_name', how='left')
    df.dropna(subset=['payment_value', 'payment_installments'], inplace=True)
    return df


# ----------------------------------------
# 3. YAN MENÜ (SIDEBAR) NAVİGASYON
# ----------------------------------------
st.sidebar.title("📌 Menü")
app_mode = st.sidebar.radio("Analiz Modülü Seçin:",
                            ["🌎 Konu 1: Coğrafi ve Lojistik Analizi",
                             "💳 Konu 2: Ödeme ve Kategori Analizi"])
st.sidebar.markdown("---")
st.sidebar.info("Brezilya e-ticaret veri seti üzerinden hazırlanmış interaktif analiz paneli.")

# ==================================================================================================
# MODÜL 1: COĞRAFİ VE LOJİSTİK ANALİZİ (ESKİ APP1 - MODERNİZE EDİLMİŞ)
# ==================================================================================================
if app_mode == "🌎 Konu 1: Coğrafi ve Lojistik Analizi":
    st.title("🌎 Brezilya E-Ticaret Coğrafi Müşteri Davranışı Analizi")
    st.markdown("**Grup A Dönem Projesi** - *Plotly ile Modernize Edilmiş İstatistiksel EDA*")
    st.markdown("---")

    with st.spinner("Coğrafi veri seti yükleniyor..."):
        df_geo, geojson_data = load_geo_data()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Sipariş", f"{df_geo['order_id'].nunique():,}")
    col2.metric("Toplam Ciro (BRL)", f"{df_geo['price'].sum():,.0f}")
    col3.metric("Farklı Müşteri Şehri", f"{df_geo['customer_city'].nunique():,}")
    col4.metric("Ort. Teslimat Süresi", f"{df_geo['delivery_days'].mean():.1f} Gün")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🗺️ Haritalar", "📊 Modern EDA", "🔬 Hipotez Testleri"])

    with tab1:
        st.header("Brezilya Eyalet Bazlı Harita Analizi")
        state_data = df_geo.groupby('customer_state').agg(
            Toplam_Siparis=('order_id', 'count'),
            Ortalama_Harcama=('price', 'mean'),
            Ortalama_Teslimat_Gunu=('delivery_days', 'mean')
        ).reset_index().rename(columns={'customer_state': 'Eyalet'})
        state_data['Log_Siparis'] = np.log10(state_data['Toplam_Siparis'])

        fig_map1 = px.choropleth(
            state_data, geojson=geojson_data, locations='Eyalet', featureidkey='properties.sigla',
            color='Log_Siparis', color_continuous_scale='Magma_r',
            hover_data={'Log_Siparis': False, 'Eyalet': False, 'Toplam_Siparis': True, 'Ortalama_Harcama': ':.2f'},
            labels={'Toplam_Siparis': 'Toplam Sipariş', 'Ortalama_Harcama': 'Ort. Harcama (BRL)'},
            title="Eyaletlere Göre Müşteri Alışveriş Hacmi (Log10)"
        )
        fig_map1.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
        fig_map1.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=500, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_map1, use_container_width=True)

        fig_map2 = px.choropleth(
            state_data, geojson=geojson_data, locations='Eyalet', featureidkey='properties.sigla',
            color='Ortalama_Teslimat_Gunu', color_continuous_scale='Teal',
            hover_data={'Ortalama_Teslimat_Gunu': ':.1f', 'Eyalet': False},
            title="Eyaletlere Göre Ortalama Teslimat Süresi (Gün)"
        )
        fig_map2.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
        fig_map2.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=500, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_map2, use_container_width=True)

    with tab2:
        st.header("Keşifsel Veri Analizi (EDA)")
        top10_states = df_geo['customer_state'].value_counts().head(10).index.tolist()
        df_top10 = df_geo[df_geo['customer_state'].isin(top10_states)]

        col_eda1, col_eda2 = st.columns(2)
        with col_eda1:
            st.subheader("1. Eyaletlere Göre Harcama Dağılımı (Boxplot)")
            fig_box = px.box(df_top10, x='customer_state', y='price', color='customer_state',
                             color_discrete_sequence=plotly_colors_app1)
            fig_box.update_layout(yaxis=dict(range=[0, 600]), showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_box, use_container_width=True)

            st.subheader("3. İlk 5 Eyaletin Satıştaki Payı (Donut Chart)")
            top5_counts = df_geo['customer_state'].value_counts().head(5)
            pie_data = pd.DataFrame({'Eyalet': top5_counts.index, 'Sayi': top5_counts.values})
            pie_data.loc[len(pie_data)] = ['Diğer', len(df_geo) - top5_counts.sum()]

            fig_pie = px.pie(pie_data, values='Sayi', names='Eyalet', hole=0.5,
                             color_discrete_sequence=plotly_colors_app1)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(showlegend=False, margin=dict(t=10, b=10, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_eda2:
            st.subheader("2. Aylık Sipariş Trendi (Area Plot)")
            monthly_orders = df_geo.groupby('order_month').size().reset_index(name='Sipariş Sayısı')
            fig_line = px.area(monthly_orders, x='order_month', y='Sipariş Sayısı', markers=True,
                               color_discrete_sequence=['#2a9d8f'])
            fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Ay", yaxis_title="Sipariş")
            st.plotly_chart(fig_line, use_container_width=True)

            st.subheader("4. Lojistik ve Davranış Korelasyon Matrisi")
            corr_cols = ['price', 'freight_value', 'delivery_days', 'product_photos_qty']
            corr_matrix = df_geo[corr_cols].corr()
            fig_corr = px.imshow(corr_matrix, text_auto='.2f', color_continuous_scale='RdBu_r', aspect="auto")
            fig_corr.update_layout(margin=dict(t=10, b=10, l=0, r=0))
            st.plotly_chart(fig_corr, use_container_width=True)

    with tab3:
        st.header("🔬 İstatistiksel Hipotez Testleri ve Dağılımlar")

        st.markdown("### 1. SP vs RJ Eyaletleri Harcama Dağılımı (Welch's T-Testi)")
        sp_prices = df_geo[(df_geo['customer_state'] == 'SP') & (df_geo['price'] < 500)]['price'].dropna()
        rj_prices = df_geo[(df_geo['customer_state'] == 'RJ') & (df_geo['price'] < 500)]['price'].dropna()
        t_stat, p_t = stats.ttest_ind(sp_prices, rj_prices, equal_var=False)

        col_t1, col_t2 = st.columns([1, 2])
        with col_t2:
            # Seaborn KDE yerine Plotly Figure Factory KDE
            fig_kde = ff.create_distplot([sp_prices, rj_prices], ['SP (São Paulo)', 'RJ (Rio de Janeiro)'],
                                         show_hist=False, show_rug=False, colors=['#264653', '#e76f51'])
            fig_kde.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=0, r=0))
            st.plotly_chart(fig_kde, use_container_width=True)
        with col_t1:
            st.metric("Welch's T-Test P-Değeri", "< 0.001" if p_t < 0.001 else f"{p_t:.4f}")
            if p_t < 0.05:
                st.success("Sonuç: ANLAMLI. Harcama ortalamaları istatistiksel olarak birbirinden farklıdır.")
            else:
                st.info("Sonuç: ANLAMLI DEĞİL.")

        st.markdown("---")
        st.markdown("### 2. Kategori ve Eyalet İlişkisi (Ki-Kare Testi)")
        top5_list = top10_states[:5]
        top_cats = df_geo['product_category_name'].value_counts().head(5).index.tolist()
        df_cat = df_geo[df_geo['customer_state'].isin(top5_list) & df_geo['product_category_name'].isin(top_cats)]

        cross = pd.crosstab(df_cat['customer_state'], df_cat['product_category_name'])
        chi2, p_chi, dof, expected = stats.chi2_contingency(cross)

        col_c1, col_c2 = st.columns([1, 2])
        with col_c2:
            cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100
            cross_pct = cross_pct.reset_index().melt(id_vars='customer_state')
            fig_bar = px.bar(cross_pct, x='customer_state', y='value', color='product_category_name',
                             color_discrete_sequence=plotly_colors_app1, title="Eyaletlere Göre Kategori Yüzdeleri")
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', barmode='stack', yaxis_title="% Oran",
                                  xaxis_title="Eyalet")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_c1:
            st.metric("Ki-Kare P-Değeri", "< 0.001" if p_chi < 0.001 else f"{p_chi:.4f}")
            if p_chi < 0.05:
                st.success("Sonuç: ANLAMLI. Eyalet ile tercih edilen kategori arasında güçlü bir ilişki vardır.")
            else:
                st.info("Sonuç: ANLAMLI DEĞİL.")

# ==================================================================================================
# MODÜL 2: ÖDEME VE KATEGORİ ANALİZİ (ESKİ APP - DOKUNULMADI, ZATEN PLOTLY İDİ)
# ==================================================================================================
elif app_mode == "💳 Konu 2: Ödeme ve Kategori Analizi":
    st.title("💳 E-Ticaret Müşteri Davranışı: Ödeme ve Kategori Analizi")
    st.markdown("Brezilya e-ticaret pazar yeri verileri üzerinden interaktif analiz paneli. (Grup B - Konu 2)")
    st.markdown("---")

    with st.spinner("Ödeme veri seti yükleniyor..."):
        df_pay = load_payment_data()

    tab1, tab2, tab3 = st.tabs(
        ["📊 Temel Görselleştirmeler", "🚀 İleri Seviye Görselleştirmeler", "🧮 İstatistiksel Analizler"])

    with tab1:
        st.header("Ödeme Yöntemi ve Taksit Dağılımı")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Ödeme Yöntemlerinin Kullanım Sayıları")
            payment_counts = df_pay['payment_type'].value_counts().reset_index()
            payment_counts.columns = ['payment_type', 'count']
            fig1 = px.bar(payment_counts, x='payment_type', y='count', color='payment_type',
                          color_discrete_sequence=plotly_colors_app2)
            fig1.update_layout(showlegend=False, margin=dict(t=10, b=10, l=0, r=0), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Ödeme Yöntemi Payları")
            fig2 = px.pie(payment_counts, values='count', names='payment_type', hole=0.5,
                          color_discrete_sequence=plotly_colors_app2)
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            fig2.update_layout(showlegend=False, margin=dict(t=10, b=10, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.subheader("Taksit Sayısı Dağılımı (1-24)")
        fig3 = px.histogram(df_pay, x='payment_installments', nbins=24, color_discrete_sequence=['#8A2BE2'])
        fig3.update_layout(yaxis_title="Frekans", bargap=0.1, margin=dict(t=10, b=10, l=0, r=0),
                           plot_bgcolor="rgba(0,0,0,0)")
        fig3.update_xaxes(tickmode='linear', tick0=1, dtick=1)
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.header("Kategori ve Tutar Yoğunluk Analizleri")
        q95 = df_pay['payment_value'].quantile(0.95)
        df_filtered = df_pay[df_pay['payment_value'] < q95]

        col_adv1, col_adv2 = st.columns([1.2, 1])
        with col_adv1:
            st.subheader("Ödeme Yöntemine Göre Tutar (Violin Plot)")
            fig4 = px.violin(df_filtered, x='payment_type', y='payment_value', color='payment_type', box=True,
                             color_discrete_sequence=plotly_colors_app2)
            fig4.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10, l=0, r=0))
            st.plotly_chart(fig4, use_container_width=True)

        with col_adv2:
            st.subheader("Ödeme Yöntemi x Taksit Sayısı Matrisi")
            heatmap_data = pd.crosstab(df_pay['payment_installments'], df_pay['payment_type'])
            fig5 = px.imshow(heatmap_data, text_auto=True, color_continuous_scale="Purpor", aspect="auto")
            fig5.update_layout(margin=dict(t=10, b=10, l=0, r=0))
            st.plotly_chart(fig5, use_container_width=True)

        st.divider()
        st.subheader("Hiyerarşik Ödeme Yapısı (Sunburst)")
        top5_cats = df_pay['product_category_name_english'].value_counts().nlargest(5).index
        df_top5 = df_pay[df_pay['product_category_name_english'].isin(top5_cats)]
        fig_sunburst = px.sunburst(df_top5,
                                   path=['product_category_name_english', 'payment_type', 'payment_installments'],
                                   values='payment_value', color_discrete_sequence=plotly_colors_app2)
        fig_sunburst.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig_sunburst, use_container_width=True)

    with tab3:
        st.header("Hipotez Testleri ve Gelişmiş Combo Grafik")
        top10_cat_data = df_pay.groupby('product_category_name_english').agg(
            avg_price=('price', 'mean'), avg_installments=('payment_installments', 'mean')
        ).sort_values('avg_price', ascending=False).head(10)

        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
        fig_combo.add_trace(go.Bar(x=top10_cat_data.index, y=top10_cat_data['avg_price'], name='Ortalama Fiyat (BRL)',
                                   marker_color='#FF8C00', opacity=0.85), secondary_y=False)
        fig_combo.add_trace(
            go.Scatter(x=top10_cat_data.index, y=top10_cat_data['avg_installments'], name='Ortalama Taksit Sayısı',
                       mode='lines+markers', line=dict(color='#8A2BE2', width=3), marker=dict(size=8)),
            secondary_y=True)
        fig_combo.update_layout(plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=10, l=0, r=0),
                                legend=dict(x=0.85, y=1.1))
        fig_combo.update_yaxes(title_text="Ortalama Fiyat", secondary_y=False)
        fig_combo.update_yaxes(title_text="Ortalama Taksit", secondary_y=True)
        st.plotly_chart(fig_combo, use_container_width=True)

        st.divider()
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.markdown("##### 1. Bağımsız Örneklem T-Testi (Kredi Kartı vs Boleto)")
            cc = df_pay[df_pay['payment_type'] == 'credit_card']['payment_value']
            bol = df_pay[df_pay['payment_type'] == 'boleto']['payment_value']
            t_stat, p_val = stats.ttest_ind(cc, bol, equal_var=False)
            st.metric(label="T-Testi P-Değeri", value=f"{p_val:.3f}")
            if p_val < 0.05:
                st.success("Anlamlı Fark Var.")
            else:
                st.warning("Anlamlı Fark Yok")

        with col_stat2:
            st.markdown("##### 2. ANOVA Testi (4 Ödeme Yöntemi Ortalamaları)")
            vou = df_pay[df_pay['payment_type'] == 'voucher']['payment_value']
            deb = df_pay[df_pay['payment_type'] == 'debit_card']['payment_value']
            f_stat, p_val_anova = stats.f_oneway(cc, bol, vou, deb)
            st.metric(label="ANOVA P-Değeri", value=f"{p_val_anova:.4e}")
            if p_val_anova < 0.05: st.success("Grup Farkı: Hedefli varyans farkı mevcuttur.")
