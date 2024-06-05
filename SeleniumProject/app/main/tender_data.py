from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import schedule
import time
from .models import Tenders, Keywords

# darko's imports
from django.core.mail import send_mail
from django.conf import settings
from selenium.webdriver.chrome.options import Options


def update_data():
    dan, mesec, godina = datetime.now().day, datetime.now().month, datetime.now().year
    formatirani_datum = f"{dan}.{mesec}.{godina}"
    print(formatirani_datum)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://cejn.gov.me/tenders")

    try:
        message_window = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "cdk-overlay-0"))
        )

        WebDriverWait(driver, 10).until_not(
            EC.visibility_of_element_located((By.CLASS_NAME, "loading-shade"))
        )

        ok_button = message_window.find_element(By.XPATH, ".//button[contains(@class, 'doneBtn')]")
        ok_button.click()
        print("")

    except Exception as e:
        print("Prozor nije pronadjen ili se pojavila greska:", e)

    opisi_tendera = driver.find_elements(By.CLASS_NAME, "colTitle")

    for opis_tendera in opisi_tendera:
        tekst_opisa = opis_tendera.text

        # keywords = ['marketing', 'digital', 'brosura', 'flajer', 'dizajn', 'websajt', 'veb sajt',
        #             'aplikacija', 'aplikacije', 'facebook', 'google', 'seo', 'hosting', 'media buying', 'reklamiranje',
        #             'reklama', 'reklame', 'advertising', 'kreativa']

        last_keywords_entry = Keywords.objects.latest('id')
        keywords = [keyword.strip().strip("'") for keyword in last_keywords_entry.kljucne_rijeci.split(',')]

        # Roditeljski <tr> element koji sadrzi trenutni opis tendera
        parent = opis_tendera.find_element(By.XPATH, "./ancestor::tr")

        status = parent.find_element(By.CLASS_NAME, "colStatus").text
        datum_objave = parent.find_element(By.CLASS_NAME, "colPublishedOn").text

        try:
            datum_objave = str(datum_objave).split()[0]
        except:
            pass

        if status.strip() == "U toku" and any(kljucna_rijec in tekst_opisa.lower() for kljucna_rijec in keywords):
            if datum_objave.strip() == formatirani_datum:
                sifra = parent.find_element(By.CLASS_NAME, "colId").text

                print("Opis tendera:", tekst_opisa)
                print("Status:", status)
                print("Datum objave:", datum_objave)
                print("Šifra tendera:", sifra)
                print("-" * 30)

                # Tenders.objects.get_or_create(
                #     opis=tekst_opisa,
                #     status=status,
                #     datum_objave=datum_objave,
                #     sifra=sifra
                # )

                # Darko's code--------------------------------------------------------------

                tender_exists = Tenders.objects.filter(sifra=sifra).exists()

                if not tender_exists:
                    tender = Tenders(
                        opis=tekst_opisa,
                        status=status,
                        datum_objave=datum_objave,
                        sifra=sifra
                    )
                    tender.save()

                    title = f'Tender -  {sifra}'
                    # receivers = ['djyuyu322@gmail.com']
                    receivers = ['josifjole32@gmail.com']
                    message = f'<p>Sifra: <strong>{sifra}</strong></p>\
                                <p>Datum objave: <strong>{datum_objave}</strong></p>\
                                <p>Status: <strong>{status}</strong></p>\
                                <br />\
                                <p><strong>{tekst_opisa}</strong></p>\
                                <br />\
                                <strong>https://cejn.gov.me/tenders/view-tender/{tender.sifra}</strong>'

                    send_mail(
                        subject=title,
                        message='',
                        html_message=message,
                        from_email='settings.EMAIL_HOST_USER',
                        recipient_list=receivers,
                        fail_silently=False
                    )
                # aisolutiontenderi2024!
                # ------------------------------------------------------------------------

    driver.quit()


# Azuriranja podataka svakog dana u 23:59h
# schedule.every().day.at("23:59").do(update_data)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)
