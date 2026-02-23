import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

print("Hayalet Bot başlatılıyor... Yakalanmamak için Chrome gizlice açılıyor.")

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
# ------------------------------------

print("İtopya Botu başlatılıyor... Bilgisayarlar taranıyor.")

# 1. Normal webdriver yerine undetected_chromedriver kullanıyoruz
options = uc.ChromeOptions()
# Dil ve pencere ayarları ekleyerek gerçekçi yapıyoruz
options.add_argument("--lang=tr-TR") 
driver = uc.Chrome(options=options)

# 2. Sahibinden URL'sine git
url = "https://www.sahibinden.com/vasita/ankara?query_text_mf=ankara+%C3%A7ankaya&query_text=%C3%A7ankaya"
# Senin kopyaladığın İtopya linki
url = "https://www.itopya.com/notebook_k14"
driver.get(url)

# KRİTİK NOKTA: Siteye girince 15 saniye bekliyoruz. 
# EĞER EKRANA "Robot musun?" DİYE BİR KUTUCUK ÇIKARSA, BU 15 SANİYE İÇİNDE KENDİ ELİNLE TIKLA VE ÇÖZ.
# Sen çözdükten sonra bot insan olduğunu sanıp çalışmaya devam edecek!
print("Sayfa yükleniyor... Eğer Captcha (Robot musun) çıkarsa 15 saniye içinde manuel çöz!")
time.sleep(15) 

print("Veriler Çekiliyor...\n")
print("Sayfa yükleniyor, 5 saniye bekleniyor...")
time.sleep(5) 

# 3. Verileri çekme işlemi (Aynı kod)
basliklar = driver.find_elements(By.CSS_SELECTOR, "a.classifiedTitle")
fiyatlar = driver.find_elements(By.CSS_SELECTOR, "td.searchResultsPriceValue span")
# Senin bulduğun class'larla verileri çekiyoruz!
basliklar = driver.find_elements(By.CSS_SELECTOR, "a.title")
# Tüm fiyat bloklarını yakalamak için daha genel bir class kullanıyoruz
fiyatlar = driver.find_elements(By.CSS_SELECTOR, "div.price")

print("--- ÇEKİLEN İLANLAR ---\n")
print(f"\nToplam {len(basliklar)} adet bilgisayar bulundu. Telegram grubuna gönderiliyor...\n")

for i in range(min(5, len(basliklar))):
for i in range(min(5, len(basliklar))): # Test için ilk 5 ürünü çekiyoruz
    baslik = basliklar[i].text.strip()
    link = basliklar[i].get_attribute("href")
    
    if i < len(fiyatlar):
        fiyat = fiyatlar[i].text.strip()
        # Alt alta yazan eski/yeni fiyatları yan yana getirmek için ufak bir düzenleme
        fiyat = fiyatlar[i].text.strip().replace("\n", " - Güncel: ") 
    else:
        fiyat = "Fiyat Okunamadı"
    
    # Tam linki oluşturmak için sahibinden domainini ekliyoruz
    tam_link = "https://www.sahibinden.com" + link
    # TELEGRAM İÇİN YENİ MESAJ TASARIMI
    mesaj = f"💻 <b>İTOPYA STOK/FİYAT BİLDİRİMİ!</b>\n\n📌 <b>Model:</b> {baslik}\n💰 <b>Fiyat:</b> {fiyat}\n🔗 <a href='{link}'>Ürüne Gitmek İçin Tıklayın</a>"
    
    print(f"📌 İlan {i+1}: {baslik}")
    print(f"💰 Fiyat: {fiyat}")
    print(f"🔗 Link: {tam_link}\n")
    telegrama_gonder(mesaj)
    time.sleep(1) # Spama düşmemek için 1 saniye bekleme

print("İşlem tamamlandı!")
# driver.quit()
print("İşlem tamamlandı, lütfen Telegram grubunu kontrol edin!")
try:
    driver.quit()
except OSError:
    pass