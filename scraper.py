import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import requests
import re
from database import veritabani_kur, urun_isle_ve_kiyasla

print("Hayalet Bot başlatılıyor... Yakalanmamak için Chrome gizlice açılıyor.")

# --- BOT MASTER BURAYI DOLDURACAK ---
TOKEN = "8023968347:AAHdnOPqsgLmVePRfeA1X48iB7KDyU7KpRI"
CHAT_ID = "-5204115535"  # Eksi işaretiyle başlayan grup ID'nizi buraya yapıştırın!

def telegrama_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Mesaj gruba başarıyla iletildi!")
    else:
        print(f"❌ TELEGRAM HATASI: {response.text}")

def fiyat_temizle(fiyat_metni):
    """ '25.999,00 TL' gibi metinleri 25999.0 sayı formatına çevirir """
    try:
        # Sadece rakamları ve virgülü al
        temiz = re.sub(r'[^\d,]', '', fiyat_metni)
        # Virgülü noktaya çevir (Python ondalıkları nokta ile anlar)
        temiz = temiz.replace(',', '.')
        return float(temiz)
    except:
        return 0.0

# ------------------------------------

print("İtopya Botu başlatılıyor... Bilgisayarlar taranıyor.")

# Bot başlarken veritabanının hazır olduğundan emin olalım
veritabani_kur()

# 1. Normal webdriver yerine undetected_chromedriver kullanıyoruz
options = uc.ChromeOptions()
options.add_argument("--lang=tr-TR") 
driver = uc.Chrome(options=options)

# 2. İtopya URL'sine git
url = "https://www.itopya.com/notebook_k14"
driver.get(url)

print("Sayfa yükleniyor... Eğer Captcha (Robot musun) çıkarsa 15 saniye içinde manuel çöz!")
time.sleep(15) 

print("Veriler Çekiliyor, 5 saniye bekleniyor...\n")
time.sleep(5) 

# 3. Verileri çekme işlemi
# 3. Verileri çekme işlemi
basliklar = driver.find_elements(By.CSS_SELECTOR, "a.title")
# SENİN BULDUĞUN CLASS'I BURAYA EKLEDİK:
fiyatlar = driver.find_elements(By.CSS_SELECTOR, "span.old-price") 

print("--- ÇEKİLEN İLANLAR ---\n")
print(f"\nToplam {len(basliklar)} adet bilgisayar bulundu. İşleniyor...\n")

# Test için ilk 5 ürünü çekiyoruz
islenen_urun_sayisi = 0
for i in range(len(basliklar)):
    if islenen_urun_sayisi >= 5: # 5 ürüne ulaştıysak döngüyü durdur
        break

    baslik = basliklar[i].text.strip()
    
    # EĞER BAŞLIK BOŞSA (Reklam vs. ise) BU ADIMI ATLA, SONRAKİNE GEÇ
    if not baslik:
        continue 
        
    link = basliklar[i].get_attribute("href")
    if not link.startswith("http"):
        link = "https://www.itopya.com" + link
    
    if i < len(fiyatlar):
        fiyat_metni = fiyatlar[i].text.strip().replace("\n", " ")
        sayisal_fiyat = fiyat_temizle(fiyat_metni)
    else:
        fiyat_metni = "Fiyat Okunamadı"
        sayisal_fiyat = 0.0
    
    # VERİTABANI İŞLEMİ
    kiyas_mesaji = urun_isle_ve_kiyasla(ilan_id=link, baslik=baslik, link=link, guncel_fiyat=sayisal_fiyat)
    
    # TELEGRAM MESAJI
    mesaj = f"💻 <b>İTOPYA BİLDİRİMİ!</b>\n\n📌 <b>Model:</b> {baslik}\n💰 <b>Fiyat:</b> {fiyat_metni}\n📊 <b>Durum:</b> {kiyas_mesaji}\n\n🔗 <a href='{link}'>Ürüne Gitmek İçin Tıklayın</a>"
    
    print(f"📌 İlan {i+1}: {baslik}")
    print(f"💰 Fiyat: {fiyat_metni} (Matematiksel: {sayisal_fiyat})")
    print(f"📊 Veritabanı Sonucu: {kiyas_mesaji}\n")
    
    telegrama_gonder(mesaj)
    islenen_urun_sayisi += 1
    time.sleep(1)

print("İşlem tamamlandı, lütfen Telegram grubunu kontrol edin!")
try:
    driver.quit()
except OSError:
    pass