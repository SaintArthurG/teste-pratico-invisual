from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import requests
import shutil
import os
import json

urlNode = "http://localhost:3000/filmes"

chrome_driver = "./chromedriver"

options = Options()
options.add_argument("--log-level=3")

service = Service(executable_path=chrome_driver)

driver = webdriver.Chrome(service=service, options=options)

#driver.get("https://www.google.com.br/")
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

regex = r"\d+\.\s(.+?)\n(\d{4})(\d+h\s\d+m)[^\n]*\n(\d,\d)"
padrao = re.compile(regex,re.MULTILINE)

dados_filmes = []

for match in padrao.finditer(lista_filmes.text):
    titulo = match.group(1)
    ano = int(match.group(2))
    duracao = match.group(3).strip()
    nota = float(match.group(4).replace(',', '.'))
    
    try:
        print(f"BUSCANDO ESSE{titulo}")
        link_filme = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//a[h3[contains(text(), "{titulo}")]]'))
        ).get_attribute("href")
    except Exception as e:
        print(f"Não foi possível encontrar o link para {titulo}, erro: {e}")
        continue

    dados_filme = {
        "titulo": titulo,
        "ano": ano,
        "duracao": duracao,
        "nota": nota,
        "link": link_filme,
    }

    dados_filmes.append(dados_filme)

    with open('links.txt', 'w', encoding='utf-8') as f:
        for line in dados_filmes:
            f.write(str(line))
        


for filme in dados_filmes:
    print(filme["link"])
    driver.get(filme["link"])
    time.sleep(5)

    try:
        sinopse_data_text = driver.find_element(By.CSS_SELECTOR, '.sc-bf30a0e-2.bRimta').get_attribute("textContent")
        time.sleep(1)
        filme["sinopse"] = sinopse_data_text.strip()
        print(f"Sinopse para {filme['titulo']}")
    except Exception as e:
        print(f"Não foi possível capturar a sinopse para {filme['titulo']}, erro: {e}")
        filme["sinopse"] = "Sinopse não disponível"

    requests.post(urlNode, json=dados_filmes)


driver.quit()

origem = 'filmes.xlsx'

destino = 'arquivos'

if not os.path.exists(destino):
    os.makedirs(destino)

shutil.move(origem, destino)
