import argparse
import urllib.request
from json import dumps
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
import time

parser=argparse.ArgumentParser()
parser.add_argument("--username")
parser.add_argument("--password")
parser.add_argument("--discord_url")
args=parser.parse_args()

username = args.username
password = args.password
discord_url = args.discord_url

# Course configuration - modify these variables to track different courses
COURSES = {
    'ws': 'INF-P-MS004 - Statistik',
    #'male': 'INF-P-IN009 - Data Science II'
}

# User-Agent needed for discord, otherwise the request gets blocked
headers = {'Content-Type': 'application/json','Accept': 'application/json','User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}

ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--window-size=1920x1080")
firefox_options.binary_location = "/usr/bin/firefox"
firefox_service = webdriver.FirefoxService(executable_path='/usr/bin/geckodriver')
driver = webdriver.Firefox(options=firefox_options, service=firefox_service)

driver.get("https://students.ffhs.ch/campus/#!app/smartdesign.campus.studyplanco")

delay = 10

try:
    driver.find_element(By.ID, "userIdPSelection_iddtext").click()
    driver.find_element(By.XPATH, "//div[@savedvalue='https://idp.ffhs.ch/idp/shibboleth']").click()

    WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "button-submit").click()

    WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, "//a[@name='to-password']")))
    driver.find_element(By.XPATH, "//a[@name='to-password']").click()

    WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.ID, "password")))
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "button-proceed").click()

    WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//sd-checkbox[@id="sso"]//input[@id="input"]')))
    print("Login erfolgreich")

    if (driver.find_element(By.XPATH, '//sd-checkbox[@id="sso"]//input[@id="input"]')):
        driver.find_element(By.XPATH, '//sd-checkbox[@id="sso"]//input[@id="input"]').click()
        driver.find_element(By.ID, "Login_LoginButton").click()
    else:
        driver.find_element(By.XPATH, "//a[@class='button smartdesign-login-button-link']").click()

    print("Campus wird aufgerufen...")
    elem = WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Meine Noten & mein Studienplan")]')))

    print("Zu Noten navigieren...")
    driver.execute_script("arguments[0].click();", elem)

    print("Studienplan laden...")
    course = WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable((By.XPATH, "//sd-list-item[starts-with(@id, 'sd-list_') and contains(@id, '_item_0')]")))

    print("Zu Studienplan navigieren...")
    try:
        time.sleep(2)
        driver.execute_script("arguments[0].click();", course)
    except StaleElementReferenceException:
        driver.find_element(By.XPATH, "//sd-list-item[starts-with(@id, 'sd-list_') and contains(@id, '_item_0')]").click()

    iframe = WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, "//iframe[starts-with(@src, 'https://students.ffhs.ch/')]")))

    print("Zu iFrame mit den Noten navigieren...")
    driver.switch_to.frame(iframe)

    iframe = WebDriverWait(driver, delay, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "INF-P-MS007 - Mathematik für Informatiker III")]/ancestor::tr/td[3]')))

    # Extract grades for configured courses
    grades = {}
    for key, course_name in COURSES.items():
        try:
            grades[key] = driver.find_element(By.XPATH, f'//a[contains(text(), "{course_name}")]/ancestor::tr/td[3]').text
        except:
            grades[key] = ""

    # Check if any grades are published
    published_grades = {k: v for k, v in grades.items() if v != ""}

    if published_grades:
        print("Noten wurden veröffentlicht!")
        for key, grade in published_grades.items():
            print(f"{key.upper()}: {grade}")

        grade_text = ", ".join([f"{k.upper()} {v}" for k, v in published_grades.items()])
        discord_message = {'content': f'Notes published: {grade_text}', 'username': 'Gitea Action'}
        req = urllib.request.urlopen(urllib.request.Request(discord_url, dumps(discord_message).encode("utf-8"), headers))
    else:
        print("Noten wurden noch nicht veröffentlicht")
except Exception as e:
    print(str(e))
    discord_message = {'content':f'{str(e)}','username':'Gitea Action'}
    req = urllib.request.urlopen(urllib.request.Request(discord_url, dumps(discord_message).encode("utf-8"), headers))
finally:
    driver.quit()
