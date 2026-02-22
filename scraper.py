import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

print("Hayalet Bot başlatılıyor... Yakalanmamak için Chrome gizlice açılıyor.")

# 1. Normal webdriver yerine undetected_chromedriver kullanıyoruz
options = uc.ChromeOptions()
# Dil ve pencere ayarları ekleyerek gerçekçi yapıyoruz
options.add_argument("--lang=tr-TR") 
driver = uc.Chrome(options=options)

# 2. Sahibinden URL'sine git
url = "https://www.sahibinden.com/vasita/ankara?query_text_mf=ankara+%C3%A7ankaya&query_text=%C3%A7ankaya"
driver.get(url)

# KRİTİK NOKTA: Siteye girince 15 saniye bekliyoruz. 
# EĞER EKRANA "Robot musun?" DİYE BİR KUTUCUK ÇIKARSA, BU 15 SANİYE İÇİNDE KENDİ ELİNLE TIKLA VE ÇÖZ.
# Sen çözdükten sonra bot insan olduğunu sanıp çalışmaya devam edecek!
print("Sayfa yükleniyor... Eğer Captcha (Robot musun) çıkarsa 15 saniye içinde manuel çöz!")
time.sleep(15) 

print("Veriler Çekiliyor...\n")

# 3. Verileri çekme işlemi (Aynı kod)
basliklar = driver.find_elements(By.CSS_SELECTOR, "a.classifiedTitle")
fiyatlar = driver.find_elements(By.CSS_SELECTOR, "td.searchResultsPriceValue span")

print("--- ÇEKİLEN İLANLAR ---\n")

for i in range(min(5, len(basliklar))):
    baslik = basliklar[i].text.strip()
    link = basliklar[i].get_attribute("href")
    
    if i < len(fiyatlar):
        fiyat = fiyatlar[i].text.strip()
    else:
        fiyat = "Fiyat Okunamadı"
    
    # Tam linki oluşturmak için sahibinden domainini ekliyoruz
    tam_link = "https://www.sahibinden.com" + link
    
    print(f"📌 İlan {i+1}: {baslik}")
    print(f"💰 Fiyat: {fiyat}")
    print(f"🔗 Link: {tam_link}\n")

print("İşlem tamamlandı!")
# driver.quit()