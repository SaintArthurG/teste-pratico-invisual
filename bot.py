from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re
import requests
import shutil
import os

urlNode = "http://localhost:3000/filmes"

chrome_driver = "./chromedriver"

options = Options()
options.add_argument("--log-level=3")

service = Service(executable_path=chrome_driver)

driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com.br/")
time.sleep(2)

driver.get("https://www.imdb.com/pt/chart/top/")
time.sleep(5)
try:
    lista_filmes = WebDriverWait(driver, 6).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ipc-metadata-list.ipc-metadata-list--dividers-between.sc-2b8fdbce-0.emPbxy.compact-list-view.ipc-metadata-list--base"))
    )
except Exception as e:
    print(f"Erro ao encontrar a lista de filmes: {e}")
    driver.quit()

regex =r"\d+\.\s+(.*?)\n(\d{4}).*?\n(\d,\d)"
padrao = re.compile(regex,re.MULTILINE)

dados_filmes = []

for match in padrao.finditer(lista_filmes.text):
    titulo = match.group(1)
    ano = int(match.group(2))
    nota = float(match.group(3).replace(',', '.'))

    try:
        link_filme = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//a[h3[contains(text(), "{titulo}")]]'))
        ).get_attribute("href")

    except Exception as e:
        print(f"Não foi possível encontrar o link para {titulo}, erro: {e}")
        continue

    dados_filme = {
        "titulo": titulo,
        "ano": ano,
        "nota": nota,
        "link": link_filme,
    }

    dados_filmes.append(dados_filme)

for filme in dados_filmes:
    print(filme["link"])
    driver.get(filme["link"])
    time.sleep(5)

    try:
        sinopse_data_text = driver.find_element(By.CSS_SELECTOR, '.sc-bf30a0e-2.bRimta').get_attribute("textContent")
        try:
            div = driver.find_element(By.CSS_SELECTOR, "div.sc-13687a64-0.iOkLEK")
            ul = div.find_element(By.CSS_SELECTOR, "ul.ipc-inline-list.ipc-inline-list--show-dividers.sc-cb6a22b2-2.aFhKV.baseAlt.baseAlt")
            itens = ul.find_elements(By.CSS_SELECTOR, "li.ipc-inline-list__item")
            duracao = itens[-1].get_attribute("textContent")
        except Exception as ex:
            print(f"erro ao pegar duracao {ex}")
            filme["duracao"] = "0"
            continue
            
        time.sleep(1)
        filme["duracao"] = duracao.strip()
        filme["sinopse"] = sinopse_data_text.strip()
    except Exception as e:
        print(f"Não foi possível capturar a sinopse para {filme['titulo']}, erro: {e}")
        filme["sinopse"] = "Sinopse não disponível"
        continue

    requests.post(urlNode, json=dados_filmes)

driver.quit()

origem = 'filmes.xlsx'

destino = f"{datetime.now().day}{datetime.now().month}{datetime.now().year}{datetime.now().hour}{datetime.now().minute}{datetime.now().second}"

if not os.path.exists(destino):
    os.makedirs(destino)

shutil.move(origem, destino)
