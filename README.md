# 🌎 Brezilya E-Ticaret (Olist) Analiz ve İstatistik Paneli

Bu proje, Brezilya'nın önde gelen e-ticaret platformu **Olist**'e ait gerçek pazar verilerini kullanarak; coğrafi dağılım, lojistik performansı, müşteri harcama alışkanlıkları ve ödeme yöntemlerini analiz eden kapsamlı bir **Veri Bilimi ve İstatistik** web uygulamasıdır. 

Jupyter Notebook üzerinde gerçekleştirilen gelişmiş analitik modeller ve istatistiksel testler, **Streamlit** ve **Plotly** kullanılarak interaktif bir panele (dashboard) dönüştürülmüştür.

---

## 🚀 Proje Modülleri ve Özellikler

### 🗺️ Modül 1: Coğrafi ve Lojistik Analizi
* **Talep Yoğunlaşması:** Sipariş hacimlerinin eyalet bazında coğrafi analizi ve pazar payı dağılımları.
* **Lojistik Varyansı:** Eyaletler arası ortalama teslimat sürelerindeki eşitsizliklerin tespiti.
* **İnteraktif Haritalar:** Brezilya coğrafyası üzerinde Choropleth ve yoğunluk haritaları.

### 💳 Modül 2: Ödeme ve Kategori Analizi
* **Müşteri Eğilimleri:** En çok tercih edilen ödeme yöntemleri ve taksit sayılarının analizi.
* **Dashboard Yapısı:** Grid sistemleri (Subplots) ile tek ekranda çok boyutlu finansal analiz panelleri.

---

## 📊 Kullanılan İstatistiksel Yöntemler

Bu proje, sadece basit görselleştirmelerle sınırlı kalmayıp, verideki ilişkileri akademik standartlarda doğrulamak için aşağıdaki hipotez testlerini içerir:

1. **Welch T-Testi:** Farklı metropol bölgelerindeki ortalama harcama tutarlarının istatistiksel olarak anlamlı bir farklılık gösterip göstermediğinin testi ($p < 0.05$).
2. **Tek Yönlü ANOVA:** Çeşitli ödeme yöntemlerinin (Kredi Kartı, Boleto, Voucher vb.) sepet tutarı üzerindeki etkisinin çoklu grup karşılaştırması.
3. **Ki-Kare (Chi-Square) Testi:** Müşteri coğrafyası ile tercih edilen ödeme yöntemi arasındaki kategorik bağımlılığın incelenmesi.
4. **OLS Regresyon Analizi:** Taksit sayısının toplam harcama tutarı üzerindeki etkisinin modellenmesi.

---

## 🛠️ Teknolojiler

* **Web Framework:** `Streamlit`
* **Veri Manipülasyonu:** `Pandas`, `NumPy`
* **Görselleştirme:** `Plotly Express`, `Plotly Graph Objects`
* **İstatistiksel Modelleme:** `SciPy (stats)`, `Statsmodels`

---

## ⚠️ Veri Seti Hakkında Önemli Not (Kurulum Öncesi)

GitHub'ın dosya boyutu sınırları (25 MB+) nedeniyle orijinal Olist veri seti bu depoya **eklenmemiştir**. Projeyi yerelinizde çalıştırmak için:
1. Veri setini [Kaggle Olist Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) adresinden indirin.
2. İndirdiğiniz `.csv` dosyalarını projenin ana dizinindeki `datasets/` (veya kodunuzda belirttiğiniz) klasörüne çıkartın.
