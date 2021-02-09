from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import os
import json
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime


# preference chrome ke stahovani souboru XML
prefs = {
    'download.default_directory': 'C:\\Users\\8350\\Desktop\\',
    'download.prompt_for_download': False,
    'download.extensions_to_open': 'xml',
    'safebrowsing.enabled': True
}
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', prefs)
options.add_argument("start-maximized")
options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
options.add_argument("--disable-extensions")
options.add_argument("--safebrowsing-disable-download-protection")
options.add_argument("safebrowsing-disable-extension-blacklist")

# remote chrome headless
driver = webdriver.Chrome(chrome_options = options, executable_path='C:\\Users\\8350\\Downloads\\chromedriver_win32\\chromedriver.exe')

# logni se dovnitr
driver.get('https://www.cbdczech.com/admin/login/')

# vypln formular
driver.find_element_by_name('email').send_keys("")
driver.find_element_by_name('password').send_keys("")
driver.find_elements_by_class_name("btn")[0].click()

# COOKIES WORK
data = driver.get_cookies()
# cookies selenium SAVE 
with open('cookie.json', 'w') as outputfile:
    json.dump(data, outputfile)
    outputfile.close()

# prejdi ke stahovani exportu objednavek
driver.get('https://www.cbdczech.com/admin/danove-doklady/')

# proved HOVER
element_to_hover_over = driver.find_element_by_xpath("//div[@class='content-header']/div[@class='content-buttons']/div[@class='open-menu']/span/a")
hover = ActionChains(driver).move_to_element(element_to_hover_over)
hover.perform()
# proved click nad objevenym prvkem
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/admin/export-faktur/']"))).click()

# vezmi mesic ktery budes resit
d = datetime.datetime.now()
month = int(d.strftime("%m"))
year = d.year
# posun o mesic dozadu
if month == 1:
	month = 12
	# posun navic rok o 1 zpatky
	year -= 1
else:
	month -= 1
# vyres den
day = "31"
# unor
if month == 2:
	if year % 4 == 0:
		day = "29"
	else:
		day = "28"
# 4 6 9 11
elif month == 4 or month == 6 or month == 9 or month == 11:
	day = "30"

# udaje ke generovani feedu
WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//form[@id='main-modal-form']/table/tbody/tr/td/input[@id='date-from']"))).send_keys("1." + str(month) + "." + str(year))
WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//form[@id='main-modal-form']/table/tbody/tr/td/input[@id='date-until']"))).send_keys(day + "." + str(month) + "." + str(year))
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//form[@id='main-modal-form']/table/tbody/tr/td/p/a"))).click()

# B: NAPARSUJ SEZNAM CISEL OBJEDNAVEK CO JSOU Z PRODEJEN A ULOZ JE DO DVOU POLI
driver.get('https://www.cbdczech.com/admin/statistika-pokladny/')
list_praha = []
list_brno = []

# C: zpracuj feed na 5 a posli ji to. podle obou seznamu vyhledej ty co jsou z prodejen: if in:, pokud jsou prazdne do jednoho seznamu, pokud plne do druheho, zbytek do tretiho souboru

# D: nahrat na server, docker s chrome headless
