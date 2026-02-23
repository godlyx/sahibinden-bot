import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import requests
import re
from database import veritabani_kur, urun_isle_ve_kiyasla

# --- AYARLAR ---
TOKEN = "8023968347:AAHdnOPqsgLmVePRfeA1X48iB7KDyU7KpRI"
CHAT_ID = "-5204115535"
BEKLEME_SURESI_DAKIKA = 60 # Bot her 15 dakikada bir uyanıp siteyi tarayacak

def telegrama_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except:
        pass

def fiyat_temizle(fiyat_metni):
    try:
        temiz = re.sub(r'[^\d,]', '', fiyat_metni)
        temiz = temiz.replace(',', '.')
        return float(temiz)
    except:
        return 0.0

def itopya_fiyat_avcisi():
    print(f"\n[{time.strftime('%H:%M:%S')}] Fiyat Avcısı taramaya başlıyor...")
    options = uc.ChromeOptions()
    options.add_argument("--headless") # Pencereyi gizler
    options.add_argument("--no-sandbox") # Sunucu ortamında güvenli çalışma sağlar
    options.add_argument("--lang=tr-TR") 
    driver = uc.Chrome(options=options)

    try:
        # İtopya Laptop Kategorisi
        driver.get("https://www.itopya.com/notebook_k14")
        time.sleep(15) 

        basliklar = driver.find_elements(By.CSS_SELECTOR, "a.title")
        fiyatlar = driver.find_elements(By.CSS_SELECTOR, "span.old-price")

        islem_goren_sayisi = 0
        bildirim_giden_sayisi = 0

        for i in range(len(basliklar)):
            baslik = basliklar[i].text.strip()
            if not baslik or "notebook" not in baslik.lower() and "laptop" not in baslik.lower(): 
                continue 
            
            link = basliklar[i].get_attribute("href")
            if not link.startswith("http"): link = "https://www.itopya.com" + link
            
            if i < len(fiyatlar):
                fiyat_metni = fiyatlar[i].text.strip().replace("\n", " ")
                sayisal_fiyat = fiyat_temizle(fiyat_metni)
            else:
                continue # Fiyatı okunamayanları pas geç

            # Veritabanına sor: Fiyat düştü mü?
            kiyas_mesaji = urun_isle_ve_kiyasla(ilan_id=link, baslik=baslik, link=link, guncel_fiyat=sayisal_fiyat)
            islem_goren_sayisi += 1

            # SADECE İNDİRİM VARSA VEYA YENİ ÜRÜNSE TELEGRAMA AT
            if "İNDİRİM YAKALANDI" in kiyas_mesaji or "YENİ İLAN" in kiyas_mesaji:
                mesaj = f"💻 <b>İTOPYA STOK/FİYAT BİLDİRİMİ!</b>\n\n📌 <b>Model:</b> {baslik}\n{kiyas_mesaji}\n\n🔗 <a href='{link}'>Ürüne Git</a>"
                telegrama_gonder(mesaj)
                bildirim_giden_sayisi += 1
                time.sleep(1)

        print(f"Tarama bitti: {islem_goren_sayisi} ürün kontrol edildi, {bildirim_giden_sayisi} fırsat Telegrama iletildi.")

    finally:
        try: driver.quit()
        except: pass

# --- OTOMASYON DÖNGÜSÜ ---
if __name__ == "__main__":
    veritabani_kur()
    print("🚀 FİYAT AVCISI OTOMASYONU BAŞLATILDI!\nBot arka planda fırsat kolluyor...")
    
    while True:
        itopya_fiyat_avcisi()
        print(f"⏳ Bot uyku moduna geçti. {BEKLEME_SURESI_DAKIKA} dakika sonra tekrar tarayacak...\n")
        time.sleep(BEKLEME_SURESI_DAKIKA * 60)