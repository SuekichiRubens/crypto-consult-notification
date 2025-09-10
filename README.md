# 🚀 Monitoramento e Notificação de Preços de Criptomoedas


Este projeto realiza consultas de preços de criptomoedas em tempo real utilizando rotas próprias da Binance, guarda seus valores em um banco de dados MySQL 
e envia alertas por e-mail quando a variação identificada for maior que um limite definido. Isso permite o acompanhamento de mudanças relevantes nos valores
das moedas sem o acompanhamento síncrono dos painéis de cada moeda na Corretora.

<br>

**⚡ Funcionalidades**

✔️Consulta os preços médios de SOL, XRP e AVAX na Binance.

✔️Cria a tabela de dados no MySQL caso não exista.

✔️Armazena os valores em uma tabela MySQL.

✔️Calcula a variação percentual em relação aos últimos registros.

✔️Envia alertas por e-mail caso a variação ultrapasse um limite definido.

✔️Executa automaticamente a cada 15 minutos até o horário final configurado.

<br>

**🛠️ Tecnologias Utilizadas**

🔲Linguagem: Python 3.8+

🔲Banco de dados: MySQL

🔲APIs e Integrações: Protocolo https / JSON

🔲Trigger de e-mail: Protocolo SMTP

<br>

Bibliotecas Python:

<br>

🔹requests → consulta API da Binance

🔹mysql-connector-python → conexão com MySQL

🔹python-dotenv → carregamento de variáveis de ambiente

🔹smtplib / email.mime → envio de e-mails

🔹API: Binance API (preço médio das criptomoedas)

🔹SMTP: Gmail ou outro provedor de e-mail compatível
