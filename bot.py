from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re

chrome_driver = "./chromedriver.exe"

options = Options()
options.add_argument("--log-level=3")
#options.add_argument("--headless") #(sem interface gráfica)

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

padrao = re.compile(
    r"(\d+)\.\s+(.*?)\n"
    r"(\d{4})(\d+h\s*\d+m)\d*\n"
    r"([\d,]+)\n",
    re.MULTILINE
)

dados_filmes = []

for match in padrao.finditer(lista_filmes.text):
    colocacao = int(match.group(1))
    titulo = match.group(2).strip()
    ano = int(match.group(3))
    duracao = match.group(4).strip()
    nota = float(match.group(5).replace(',', '.'))
    try:
        link_filme = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//a[h3[contains(text(), "{titulo}")]]'))
        ).get_attribute("href")
    except Exception as e:
        print(f"Não foi possível encontrar o link para {titulo}, erro: {e}")
        continue

    dados_filme = {
        "colocacao": colocacao,
        "titulo": titulo,
        "ano": ano,
        "duracao": duracao,
        "nota": nota,
        "link": link_filme,
    }
    dados_filmes.append(dados_filme)

for filme in dados_filmes:
    print(f"Procurando link para: {filme['titulo']}")
    driver.get(filme["link"])
    time.sleep(2)
    try:
        sinopse_data_text = driver.find_element(By.CSS_SELECTOR, '.sc-bf30a0e-2.bRimta').get_attribute("textContent")
        time.sleep(1)
        filme["sinopse"] = sinopse_data_text
        print(f"Sinopse para {filme['titulo']}: {filme['sinopse']}")
    except Exception as e:
        print(f"Não foi possível capturar a sinopse para {filme['titulo']}, erro: {e}")
        filme["sinopse"] = "Sinopse não disponível"
        print(f"Sinopse para {filme['titulo']}: {filme['sinopse']}")
    dados_filmes.append(filme)

print("Escrevendo dados no arquivo JSON...")
with open('filmes.json', 'w', encoding='utf-8') as f:
    json.dump(dados_filmes, f, ensure_ascii=False, indent=2)

driver.quit()