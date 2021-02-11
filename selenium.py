import os
import json
import random
import copy
import datetime
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import xml.etree.cElementTree as ET


class Parser(object):


	# init override
	def __init__(self, *args, **kwargs):
		super(Parser, self).__init__(*args, **kwargs)
		# promenne
		self.filepath = 'C:\\Users\\8350\\Desktop\\'
		self.filename = 'stormware_invoices.xml'
		self.month = 0
		self.year = 0
		self.list_brno = []
		self.list_praha = []


	# vybrani ID danovych dokladu konkretni pokladny a ulozeni do seznamu
	def pokladna(self, kasa, driver):
		WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//select[@name='cashDeskId']")))
		select = Select(self.driver.find_element_by_xpath("//select[@name='cashDeskId']"))
		select.select_by_visible_text(kasa)
		# klikni na filtr
		WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='filter']/div[@class='filter-buttons']/a"))).click()
		# cekej chvili
		time.sleep(5)
		# klikni na druhou zalozku
		self.driver.find_element_by_xpath("//div[@id='content-in']/div/div/ul/li/a[.//text()='Jednotlivé operace']").click()
		# pockej az je nacte vsechny
		time.sleep(5)
		# napln seznam cisly danovych dokladu
		seznam = self.driver.find_elements_by_xpath("((//div[@id='detail']/div[@class='table-holder']/table/tbody/tr/td[9])/a[2])")
		return seznam


	# setdriver
	def setdriver(self):
		# preference chrome ke stahovani souboru XML
		prefs = {
		    'download.default_directory': self.filepath,
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
		self.driver = webdriver.Chrome(chrome_options=options, executable_path='C:\\Users\\8350\\Downloads\\chromedriver_win32\\chromedriver.exe')


	# uvodni selenium
	def selenium_login(self):

		# logni se dovnitr
		self.driver.get('https://www.cbdczech.com/admin/login/')

		# vypln formular
		self.driver.find_element_by_name('email').send_keys("plsekmic@gmail.com")
		self.driver.find_element_by_name('password').send_keys("Kjkszpj2525!!")
		self.driver.find_elements_by_class_name("btn")[0].click()

		# COOKIES WORK - mozna kvuli scrapy v budoucnu
		#data = driver.get_cookies()
		# cookies selenium SAVE 
		#with open('cookie.json', 'w') as outputfile:
		#    json.dump(data, outputfile)
		#    outputfile.close()

	# download souboru objednavek
	def selenium_download(self):

		# pokud stazeny soubor uz existuje, smaz to
		try:
			os.remove(self.filepath + self.filename)
		except OSError:
			pass

		# prejdi ke stahovani exportu objednavek
		self.driver.get('https://www.cbdczech.com/admin/danove-doklady/')

		# proved HOVER
		WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='content-header']/div[@class='content-buttons']/div[@class='open-menu']/span/a")))
		element_to_hover_over = self.driver.find_element_by_xpath("//div[@class='content-header']/div[@class='content-buttons']/div[@class='open-menu']/span/a")
		hover = ActionChains(self.driver).move_to_element(element_to_hover_over)
		hover.perform()
		# proved click nad objevenym prvkem
		WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//a[@href='/admin/export-faktur/']"))).click()

		# vezmi mesic ktery budes resit
		d = datetime.datetime.now()
		self.month = int(d.strftime("%m"))
		self.year = d.year
		# posun o mesic dozadu
		if self.month == 1:
			self.month = 12
			# posun navic rok o 1 zpatky
			self.year -= 1
		else:
			self.month -= 1
		# vyres den
		day = "31"
		# unor
		if self.month == 2:
			if self.year % 4 == 0:
				day = "29"
			else:
				day = "28"
		# 4 6 9 11
		elif self.month == 4 or self.month == 6 or self.month == 9 or self.month == 11:
			day = "30"

		# udaje ke generovani feedu
		WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//form[@id='main-modal-form']/table/tbody/tr/td/input[@id='date-from']"))).send_keys("1." + str(self.month) + "." + str(self.year))
		WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//form[@id='main-modal-form']/table/tbody/tr/td/input[@id='date-until']"))).send_keys(day + "." + str(self.month) + "." + str(self.year))
		WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//form[@id='main-modal-form']/table/tbody/tr/td/p/a"))).click()

	# vytvor seznamy objednavek z pokladen
	def selenium_lists(self):

		self.driver.get('https://www.cbdczech.com/admin/statistika-pokladny/')

		# vyber select roku
		WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//select[@name='monthYear']")))
		select = Select(self.driver.find_element_by_xpath("//select[@name='monthYear']"))
		if self.month < 10:
			self.month = "0" + str(self.month)
		else:
			self.month = str(self.month)

		#select.select_by_value(month + "/" + str(year))
		# DEBUG OVERRIDE !!
		select.select_by_value("02" + "/" + str(self.year))

		# udelej seznamy ID z pokladen
		self.list_brno = self.pokladna("CBD CZECH - prodejna Brno", self.driver)
		self.list_praha = self.pokladna("CBD CZECH - prodejna Praha", self.driver)


	# vytvor nove soubory feedu
	# bw: brno walkin - v seznamu a bez jmena
	# bn: brno z netu - v seznamu a se jmenem
	# pw: praha walkin - v seznamu a bez jmena
	# pn: praha z netu - v seznamu a se jmenem
	# rest: zbytek co je normalne nedefinovanej z netu
	def generate_feeds(self):

		# vnitrni funkce pro jedno mesto, kde je doklad definovany ID z jednoho ze seznamu
		def _city(namespaces, elem, xw,xn):
			# inv:invoice
			for invoice in elem:
				header = invoice.find('inv:invoiceHeader', namespaces)
				partner = header.find('inv:partnerIdentity', namespaces)
				address = partner.find('typ:address', namespaces)
				name = address.find('typ:name', namespaces)
				# pokud neni vlozene jmeno
				if not len(name):
					# je to Brno walkin
					xw.write(ET.tostring(elem, encoding='unicode'))
				# je vlozene jmeno
				else:
					# je to Brno objednavka z shopu
					xn.write(ET.tostring(elem, encoding='unicode'))


		# aktualni namespace v XML feedu
		namespaces = {"dat": "http://www.stormware.cz/schema/version_2/data.xsd", "inv":"http://www.stormware.cz/schema/version_2/invoice.xsd", "typ":"http://www.stormware.cz/schema/version_2/type.xsd"}

		with open(self.filepath + 'brno_walkin.xml', 'w+') as bw, open(self.filepath + 'brno_net.xml', 'w+') as bn, open(self.filepath + 'praha_walkin.xml', 'w+') as pw, open(self.filepath + 'praha_net.xml', 'w+') as pn, open(self.filepath + 'zbytek.xml', 'w+') as rest:
			
			# zapis zacatky souboru
			bw.write('<?xml version="1.0" encoding="UTF-8"?>')
			bw.write('<dat:dataPack id="fa001" ico="08955824" application="StwTest" version="2.0" note="Import" xmlns:dat="http://www.stormware.cz/schema/version_2/data.xsd" xmlns:inv="http://www.stormware.cz/schema/version_2/invoice.xsd" xmlns:typ="http://www.stormware.cz/schema/version_2/type.xsd">')
			bn.write('<?xml version="1.0" encoding="UTF-8"?>')
			bn.write('<dat:dataPack id="fa001" ico="08955824" application="StwTest" version="2.0" note="Import" xmlns:dat="http://www.stormware.cz/schema/version_2/data.xsd" xmlns:inv="http://www.stormware.cz/schema/version_2/invoice.xsd" xmlns:typ="http://www.stormware.cz/schema/version_2/type.xsd">')
			pw.write('<?xml version="1.0" encoding="UTF-8"?>')
			pw.write('<dat:dataPack id="fa001" ico="08955824" application="StwTest" version="2.0" note="Import" xmlns:dat="http://www.stormware.cz/schema/version_2/data.xsd" xmlns:inv="http://www.stormware.cz/schema/version_2/invoice.xsd" xmlns:typ="http://www.stormware.cz/schema/version_2/type.xsd">')
			pn.write('<?xml version="1.0" encoding="UTF-8"?>')
			pn.write('<dat:dataPack id="fa001" ico="08955824" application="StwTest" version="2.0" note="Import" xmlns:dat="http://www.stormware.cz/schema/version_2/data.xsd" xmlns:inv="http://www.stormware.cz/schema/version_2/invoice.xsd" xmlns:typ="http://www.stormware.cz/schema/version_2/type.xsd">')
			rest.write('<?xml version="1.0" encoding="UTF-8"?>')
			rest.write('<dat:dataPack id="fa001" ico="08955824" application="StwTest" version="2.0" note="Import" xmlns:dat="http://www.stormware.cz/schema/version_2/data.xsd" xmlns:inv="http://www.stormware.cz/schema/version_2/invoice.xsd" xmlns:typ="http://www.stormware.cz/schema/version_2/type.xsd">')

			# rozparsuj root
			for event, elem in ET.iterparse(self.filepath + self.filename, events=('start', 'end')):

				# el == danovy doklad
				if elem.tag == '{http://www.stormware.cz/schema/version_2/data.xsd}dataPackItem':

					# pokud je ID dokladu v seznamu Brna
					if elem.attrib['id'] in self.list_brno:
						_city(namespaces, elem, bw, bn)

					# pokud je ID dokladu v seznamu Prahy
					elif elem.attrib['id'] in self.list_praha:
						_city(namespaces, elem, pw, pn)

					# ID dokladu neni v jednom ze seznamu, takze ho dej rovnou do REST
					else:
						rest.write(ET.tostring(elem, encoding='unicode'))

			# zapis konce souboru
			bw.write('</dat:dataPack>')
			pw.write('</dat:dataPack>')
			bn.write('</dat:dataPack>')
			pn.write('</dat:dataPack>')
			rest.write('</dat:dataPack>')


# START
parser = Parser()
#parser.setdriver()
#parser.selenium_login()
#parser.selenium_download()
#parser.selenium_lists()
parser.generate_feeds()

# naukladej seznamy do docasnych souboru: aby se daly zpracovat i offline
# zprovozni odesilani mailem
# nakonec to nahrej na server a spust casovani - docker a headless chrome
