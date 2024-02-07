# proxy scrapper

import requests
import threading
import aiohttp
import asyncio
import random
import queue
import time
import json
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

#Async fetch
async def fetch(url, headers, session,):
	async with session.get(url, headers=random.choice(headers)) as response:
		try:
			json = await response.json()
		except:
			json = None

		result = {
		"status": response.status,
		"headers": response.headers,
		"text": await response.text(), 
		"json": json
		}

	return result

# Obtiene proxies de forma bruta
async def get_proxies(threads, headers, session):

	t1 = int(time.time())

	print(" # PROCESO DE OBTENCIÓN DE PROXIES COMENZADO #")

	# Lista de proxies
	proxiesBruto = []

	# método para guardar proxies obtenidas de forma thread safe
	list_lock = threading.Lock()
	def guardar_proxy(proxy):
		with list_lock:
			proxiesBruto.append(proxy)

	# -- Métodos de obtención de proxies --
	async def web_scrappers(headers):
		# ---- Obtención por Web Scrapping ----

		# Métodos web scraping
		async def scrapingGeneral(url, headers, session,):
			response = await fetch(url, headers, session)
			if response["status"] == 200:
				soup = BeautifulSoup(response["text"], 'html.parser')

				table = soup.find('tbody')
				rows = table.find_all('tr')

				for row in rows:
					try:
						columns = row.find_all('td')
						ip = columns[0].text.strip()
						port = int(columns[1].text)

						proxy = f'{ip}:{port}'
						guardar_proxy(proxy)
					except:
						continue
		async def freeproxy_world(headers):
			async with aiohttp.ClientSession() as session:

				tasks = []
				for i in range (1,20):

					url_aux = "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page="+str(i)

					tasks.append(asyncio.ensure_future(fetch(url_aux, headers, session)))

				responses = await asyncio.gather(*tasks)

				for response in responses:

					if response["status"] == 200:

						soup = BeautifulSoup(response["text"], 'html.parser')
						table = soup.find('tbody')
						rows = table.find_all('tr')

						for row in rows:
							try:
								columns = row.find_all('td')
								ip = columns[0].text.strip()
								port = int(columns[1].text)

								proxy = f'{ip}:{port}'
								guardar_proxy(proxy)

							except:
								continue
		async def proxyhub_me(headers):
			async with aiohttp.ClientSession() as session:
				tasks = []
				countries = ["af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fr", "fy", "ga", "gd", "gl", "gu", "ha", "hi", "hr", "hu", "hy", "id", "ig", "is", "it", "ja", "ka", "kk", "km", "kn", "ko", "ky", "lb", "lo", "lt", "lv", "mg", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "no", "pa", "pl", "ps", "pt", "ro", "ru", "si", "sk", "sl", "sn", "so", "sq", "sr", "sv", "sw", "ta", "te", "th", "tl", "tr", "uk", "ur", "uz", "vi", "yi", "yo", "zh", "zu"]

				for country in countries:

					url_aux = f"https://proxyhub.me/en/{country}-free-proxy-list.html"
					tasks.append(asyncio.ensure_future(fetch(url_aux, headers, session)))

				responses = await asyncio.gather(*tasks)

				for response in responses:

					if response["status"] == 200:

						soup = BeautifulSoup(response["text"], 'html.parser')
						table = soup.find('tbody')
						rows = table.find_all('tr')

						for row in rows:
							try:
								columns = row.find_all('td')
								ip = columns[0].text.strip()
								port = int(columns[1].text)

								proxy = f'{ip}:{port}'
								guardar_proxy(proxy)

							except:
								continue
		async def freeproxylist_cc(headers):
			async with aiohttp.ClientSession() as session:

				tasks = []

				for i in range (1,24+1):

					url_aux = f"https://freeproxylist.cc/servers/{i}.html"
					tasks.append(asyncio.ensure_future(fetch(url_aux, headers, session)))

				responses = await asyncio.gather(*tasks)

				for response in responses:

					if response["status"] == 200:

						soup = BeautifulSoup(response["text"], 'html.parser')
						table = soup.find('tbody')
						rows = table.find_all('tr')

						for row in rows:
							try:
								columns = row.find_all('td')
								ip = columns[0].text.strip()
								port = int(columns[1].text)

								proxy = f'{ip}:{port}'
								guardar_proxy(proxy)

							except:
								continue

		urls = [
		"https://free-proxy-list.net", 
		"https://www.us-proxy.org", 
		"https://free-proxy-list.net/uk-proxy.html", 
		"https://www.sslproxies.org/", 
		"https://www.socks-proxy.net",
		"https://www.freeproxy.world",
		"https://proxyhub.me",
		"https://freeproxylist.cc",
		"https://hidemy.life/en/proxy-list-servers"
		]

		# DISTRIBUCIÓN DE MÉTODOS POR THREADS

		tasks = []

		for url in urls:
			# 1
			if url == "https://www.freeproxy.world":
				tasks.append(asyncio.ensure_future(freeproxy_world(headers)))
			# 2
			elif url =="https://proxyhub.me":
				tasks.append(asyncio.ensure_future(proxyhub_me(headers)))
			# 3
			elif url == "https://freeproxylist.cc":
				tasks.append(asyncio.ensure_future(freeproxylist_cc(headers)))

			# GENERAL			
			else:
				await scrapingGeneral(url, headers, session)

		# Run the tasks concurrently
		await asyncio.gather(*tasks)

	async def plain_text(headers, session):
		# ---- Obtención por API PLAIN TEXT ----
		# "ip:port" por línea

		urls = [
		"https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
		"https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt", 
		"https://vpn.fail/free-proxy/txt", 
		"https://www.proxy-list.download/api/v1/get?type=http", 
		"https://www.proxy-list.download/api/v1/get?type=https", 
		"https://www.proxy-list.download/api/v1/get?type=socks4", 
		"https://www.proxy-list.download/api/v1/get?type=socks5"
		]

		tasks = []
	
		for url in urls:
			tasks.append(asyncio.ensure_future(fetch(url, headers, session)))

		responses = await asyncio.gather(*tasks)

		for response in responses:

				if response["status"] == 200:
					data = response["text"]

					# elimina datos que no sean ip:puerto y crea una lista
					patron = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}'
					listaProxiesObtenida = re.findall(patron, data)

					# añade 1 a 1 los proxys a la lista general
					for proxy in listaProxiesObtenida:
						guardar_proxy(proxy)
	async def api(headers, session):
		# ---- Obtención por API JSON ----

		# geonode.com

		tasks = []

		# Threads para API de geonode.com
		for page in range(1, 18):

			url = f"https://proxylist.geonode.com/api/proxy-list?limit=500&page={page}&sort_by=lastChecked&sort_type=desc"
			tasks.append(asyncio.ensure_future(fetch(url, headers, session)))

		responses = await asyncio.gather(*tasks)

		for response in responses:

			if response["status"] == 200:
				data = response["json"]
				for i in range (len(data["data"])):
					ip = data["data"][i]["ip"]
					port = data["data"][i]["port"]
					proxy = f'{ip}:{port}'
					guardar_proxy(proxy)

	#  -- USO DE THREADING PARA INVOCAR LOS MÉTODOS -- 

	# threads usados para invocar métodos de obtención de proxies
	tasks = [web_scrappers(headers), plain_text(headers, session), api(headers, session)]

	# Run the tasks concurrently
	await asyncio.gather(*tasks)


	# ---- DISTRIBUCIÓN DE PROXIES ----

	# borra proxies duplicadas
	proxiesBruto = list(set(proxiesBruto))

	# reparte las proxies entre los threads
	q = int(len(proxiesBruto) / threads)
	proxies = [] # lista de listas de proxies (cada lista para cada thread)
	cursor = 0

	for i in range(threads):
		thread_proxies = []

		#ultimo thread
		if i == threads-1:
			for pos in range (cursor, len(proxiesBruto)):
				thread_proxies.append(proxiesBruto[pos])
			
		#threads con cantidad fija
		else:
			for pos in range(q):
				thread_proxies.append(proxiesBruto[cursor])
				cursor = cursor + 1

		proxies.append(thread_proxies)

	t2 = int(time.time())
	print(f"Proxies no verificados: {len(proxiesBruto)} en {t2-t1} segundos")
	return proxies

# Filtra las proxies que funcionan en una nueva lista. 
def validate_proxies(url, headers, proxies, proxies_verificados, thread_id):

	def elite_check(url, headers, proxy):
		status = False

		try:
			proxy_dict = {
				'http': proxy,
				'https': proxy
			}

			response = requests.get(url, headers=random.choice(headers), proxies=proxy_dict, timeout=10)

			if response.status_code == 200:

				# verifica que la proxy sea de tipo ELITE
				if 'X-Forwarded-For' in response.headers:
					#Transparent
					pass
				elif 'Via' in response.headers:
					#Anonymous
					pass
				else:
					#Elite
					status = True
		except:
			pass

		return status

	verified_proxies = set()

	# se leen las proxies del archivo
	proxies_archivo = read_txt("proxies.txt")

	for proxy in proxies:
		if proxy in verified_proxies or proxy in proxies_archivo:
			continue

		# elite checker
		if elite_check("https://marketprices.io", headers, proxy):
			if elite_check("https://www.cual-es-mi-ip.net", headers, proxy):
				if elite_check("https://proxydb.net/anon", headers, proxy):
					if elite_check("https://twitter.com", headers, proxy):
						if elite_check(url, headers, proxy):
							print(f"{proxy}")
							proxies_verificados.put(proxy)

# obtiene las proxies del archivo .txt
def read_txt(nombre_archivo):
	# se leen las proxies del archivo
	with open(nombre_archivo, 'r') as archivo:
		proxies_archivo =  set(line.strip() for line in archivo)
	return proxies_archivo

# guarda las proxies en un .txt (se acomulan)
def save_proxies(proxy_list):
	nombre_archivo = "proxies.txt"

	with open(nombre_archivo, 'a') as archivo:
		for proxy in proxy_list:
			archivo.write(proxy + '\n')

	print("-- PROXIES GUARDADAS CORRECTAMENTE --")
	
async def main():
	# Settings
	headers = [
	{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"},
	{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.0"},
	{"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko"},
	{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"},
	{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15"},
	{"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"},
	{"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1"},
	{"User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1"},
	{"User-Agent": "Mozilla/5.0 (Android 8.0.0; Mobile; LG-US998 Build/OPR1.170623.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.137 Mobile Safari/537.36"},
	{"User-Agent": "Mozilla/5.0 (Android 8.0.0; Tablet; rv:61.0) Gecko/61.0 Firefox/61.0"},
	{"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Mobile Safari/537.36"},
	{"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"},
	{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"},
	{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.0"}
	]
	destination_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=max&interval=5d"
	nThreads = 100

	#----------------------


	# Obtiene las proxies no verificadas en listas individuales para cada thread
	async with aiohttp.ClientSession() as session:
		proxies = await get_proxies(nThreads, headers, session)

	proxies_verificados = queue.Queue()

	# Ejecuta verificador de forma aasyncrona
	threads = []
	for i in range(nThreads):
		t = threading.Thread(target=validate_proxies, args=(destination_url, headers, proxies[i], proxies_verificados, i))
		t.start()
		threads.append(t)

	# Espera a que todos los threads terminen
	for t in threads:
		t.join()

	print("Todos los threads han finalizado.")

	# guarda las proxies en "proxies.txt"
	proxy_list = list(proxies_verificados.queue)
	save_proxies(proxy_list)

if __name__ == '__main__':
	asyncio.run(main())