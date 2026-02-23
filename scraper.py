import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import requests
import re
from database import veritabani_kur, urun_isle_ve_kiyasla

# --- AYARLAR ---
TOKEN = "8023968347:AAHdnOPqsgLmVePRfeA1X48iB7KDyU7KpRI"
CHAT_ID = "-5204115535"

def telegrama_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except:
        pass

def fiyat_temizle(fiyat_metni):
    try:
        # Vatan'daki "15.999,00 TL" gibi formatları temizler
        temiz = re.sub(r'[^\d,]', '', fiyat_metni)
        temiz = temiz.replace(',', '.')
        return float(temiz)
    except:
        return 0.0

def vatan_fiyat_avcisi():
    print(f"\n[{time.strftime('%H:%M:%S')}] Vatan Bilgisayar taramaya başlıyor...")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--lang=tr-TR") 
    
    driver = uc.Chrome(options=options, version_main=144)

    try:
        # Vatan Bilgisayar Notebook Kategorisi
        driver.get("https://www.vatanbilgisayar.com/notebook/")
        time.sleep(10) # Sayfanın yüklenmesi için kısa bir bekleme
        
        print("Gidilen URL:", driver.current_url)
        print("Sayfa Başlığı:", driver.title)

        # Vatan Bilgisayar'ın ürün kartı CSS yapıları
        urun_kartlari = driver.find_elements(By.CSS_SELECTOR, ".product-list__content")
        
        islem_goren_sayisi = 0
        bildirim_giden_sayisi = 0

        for kart in urun_kartlari:
            try:
                baslik_elementi = kart.find_element(By.CSS_SELECTOR, ".product-list__product-name")
                fiyat_elementi = kart.find_element(By.CSS_SELECTOR, ".product-list__price")
                
                baslik = baslik_elementi.text.strip()
                fiyat_metni = fiyat_elementi.text.strip()
                
                # Kartın sarmalayıcı linkini alıyoruz
                link_elementi = kart.find_element(By.XPATH, "..")
                link = link_elementi.get_attribute("href")
                
                if not link.startswith("http"): 
                    link = "https://www.vatanbilgisayar.com" + link

                sayisal_fiyat = fiyat_temizle(fiyat_metni)

                if sayisal_fiyat > 0:
                    kiyas_mesaji = urun_isle_ve_kiyasla(ilan_id=link, baslik=baslik, link=link, guncel_fiyat=sayisal_fiyat)
                    islem_goren_sayisi += 1

                    if "İNDİRİM YAKALANDI" in kiyas_mesaji or "YENİ İLAN" in kiyas_mesaji:
                        mesaj = f"💻 <b>VATAN BİLGİSAYAR FIRSATI!</b>\n\n📌 <b>Model:</b> {baslik}\n{kiyas_mesaji}\n\n🔗 <a href='{link}'>Ürüne Git</a>"
                        telegrama_gonder(mesaj)
                        bildirim_giden_sayisi += 1
                        time.sleep(1) # Telegram'dan spam yememek için
            except Exception as e:
                # Reklam veya hatalı kartları pas geç
                continue

        print(f"Tarama bitti: {islem_goren_sayisi} ürün kontrol edildi, {bildirim_giden_sayisi} fırsat Telegrama iletildi.")

    finally:
        try: driver.quit()
        except: pass

# --- BULUT UYUMLU OTOMASYON TETİKLEYİCİSİ ---
if __name__ == "__main__":
    veritabani_kur()
    print("🚀 GITHUB ACTIONS TARAFINDAN TETİKLENDİ: Otomasyon başlatılıyor...")
    vatan_fiyat_avcisi()
    print("✅ İşlem başarıyla tamamlandı. Bulut makinesi kapatılıyor...")