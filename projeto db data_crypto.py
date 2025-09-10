import requests
import mysql.connector
import json
from email.mime.text import MIMEText  # cria mensagens de email em formato texto
import smtplib  # envia e-mails via protocolo SMTP
import time
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv() # carrega o arquivo .env onde constam as informações sensíveis para a execução do código

url1 = "https://api.binance.com/api/v3/avgPrice?symbol=SOLBRL"
url2 = "https://api.binance.com/api/v3/avgPrice?symbol=XRPBRL"
url3 = "https://api.binance.com/api/v3/avgPrice?symbol=AVAXBRL"

limite_variacao = 0.2  # porcentagem mínima para disparar um e-mail de alerta

remetente = os.getenv("SMTP_REMETENTE")
senha = os.getenv("SMTP_PASSWORD")
destinatario = os.getenv("SMTP_DESTINATARIO")

response1 = requests.get(url1)
response2 = requests.get(url2)
response3 = requests.get(url3)


def consulta_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na requisição: {response.status_code}")
        return None


def processa_moeda(cursor, conn, data, simbolo):
    if not data:
        return None, None

    intervalo_mins = data.get("mins")
    price = float(data.get("price"))

    cursor.execute(
        "SELECT price FROM data_crypto WHERE moeda = %s ORDER BY id DESC LIMIT 4", (simbolo,))
    ultimos_precos_registros = cursor.fetchall()
    ultimos_precos = [float(p[0]) for p in ultimos_precos_registros]

    # inserir novo preço

    cursor.execute("""
        INSERT INTO data_crypto (moeda, intervalo_mins, price)
        VALUES (%s, %s, %s)
    """, (simbolo, intervalo_mins, price))
    conn.commit()

    variacao = 0
    if ultimos_precos:
        ultimo_preco = ultimos_precos[0]
        variacao = ((price - ultimo_preco) / ultimo_preco) * 100

    return price, variacao, ultimos_precos


def main():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES LIKE 'data_crypto'")
    if not cursor.fetchone():
        # se a tabela não existir, cria já com a coluna moeda
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_crypto(
            id INT AUTO_INCREMENT PRIMARY KEY,
            moeda VARCHAR(10),
            intervalo_mins INT,
            price DECIMAL(18,8),
            data_insercao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)
        """)
        conn.commit()

    data1 = consulta_api(url1)  # Solana
    data2 = consulta_api(url2)  # XRP
    data3 = consulta_api(url3)  # AVAX

    price1, variacao1, ultimos_precos1 = processa_moeda(
        cursor, conn, data1, "SOL")
    price2, variacao2, ultimos_precos2 = processa_moeda(
        cursor, conn, data2, "XRP")
    price3, variacao3, ultimos_precos3 = processa_moeda(
        cursor, conn, data3, "AVAX")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(remetente, senha)

        def enviar_email(simbolo, price, variacao, ultimos_precos):

            corpo = f"O preço da {simbolo} variou {variacao:.2f}% nos últimos 15 min e atingiu {price:.2f} BRL. \n"
            if ultimos_precos:
                corpo += "Comparações com valores anteriores: \n"

                for i, preco_antigo in enumerate(ultimos_precos[1:], start=1):
                    variacao_antiga = (
                        (price - preco_antigo) / preco_antigo) * 100
                    tempo_atras = (i + 1) * 15
                    corpo += f"- {tempo_atras} min atrás: {preco_antigo:.2f} BRL -> {variacao_antiga:.2f}% \n"

            msg = MIMEText(corpo)
            msg["Subject"] = f"Alerta de Preço - {simbolo}"
            msg["From"] = remetente
            msg["To"] = destinatario
            servidor.send_message(msg)
            print(f"E-mail enviado para {simbolo}!")

        for simbolo, price, variacao, ultimos_precos in [
            ("SOL", price1, variacao1, ultimos_precos1),
            ("XRP", price2, variacao2, ultimos_precos2),
            ("AVAX", price3, variacao3, ultimos_precos3)
        ]:

            if variacao is None or abs(variacao) < limite_variacao:
                print(
                    f"Variação de {simbolo} abaixo do limite ({limite_variacao}%).")
            else:
                enviar_email(simbolo, price, variacao, ultimos_precos)

    cursor.close()
    conn.close()

def horario_atual():
    return datetime.now().strftime("%H:%M")

horario_final = "22:00"

if __name__ == "__main__":
    while True:
        agora = horario_atual()
        if agora >= horario_final:
            print(f"Horário final atingido ({horario_final}). Encerrando o script...")
            break

        print(f"Execução iniciada às {agora}...")
        main()
        print("Aguardando 15 minutos para a próxima execução...\n")
        time.sleep(15 * 60)
