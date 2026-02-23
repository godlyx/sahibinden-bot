import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import requests
import re
from database import veritabani_kur, urun_isle_ve_kiyasla

# --- AYARLAR ---
TOKEN = "8023968347:AAHdnOPqsgLmVePRfeA1X48iB7KDyU7KpRI"
CHAT_ID = "-5204115535"
# Not: BEKLEME_SURESI_DAKIKA silindi çünkü zamanlamayı artık GitHub Actions (cron) yapacak.

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
    # Eski --headless yerine yeni nesil görünmez modu kullanıyoruz
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Bota gerçek bir bilgisayar ekranı ölçüsü veriyoruz
    options.add_argument("--window-size=1920,1080")
    # Bota "Ben bulut sunucusu değilim, Windows 10 kullanan normal bir insanım" dedirtiyoruz
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--lang=tr-TR") 
    
    driver = uc.Chrome(options=options, version_main=144)
    try:
        # İtopya Laptop Kategorisi
        driver.get("https://www.itopya.com/notebook_k14")
        time.sleep(15) 
        
        # --- TEŞHİS İÇİN EKLENEN KISIM ---
        print("Gidilen URL:", driver.current_url)
        print("Sayfa Başlığı:", driver.title)
        print("Sayfa Kaynağı Uzunluğu:", len(driver.page_source))
        # ---------------------------------

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

# --- BULUT UYUMLU OTOMASYON TETİKLEYİCİSİ ---
if __name__ == "__main__":
    veritabani_kur()
    print("🚀 GITHUB ACTIONS TARAFINDAN TETİKLENDİ: Otomasyon başlatılıyor...")
    
    # Döngü olmadan sadece bir kez çalıştır
    itopya_fiyat_avcisi()
    
    print("✅ İşlem başarıyla tamamlandı. Bulut makinesi kapatılıyor...")