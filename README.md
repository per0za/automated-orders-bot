# 🤖 Automação de Pedidos: WhatsApp & Google Sheets

Um script de automação desenvolvido em Python para otimizar o fluxo de vendas. O robô captura pedidos via WhatsApp, processa os dados, gera identificadores únicos e alimenta uma planilha no Google Sheets em tempo real, calculando automaticamente o status de pagamento de cada pedido.

## ✨ Funcionalidades

- **Leitura Automatizada:** Utiliza Selenium para capturar e ler as mensagens e pedidos recebidos.
- **Agrupamento Inteligente:** Agrupa múltiplos itens de um mesmo cliente sob um ID único (iniciando diretamente na Coluna A da planilha).
- **Cálculo de Status Global:** Lê os valores preenchidos na planilha, soma os totais de produtos e as entradas (adiantamentos) e define o status final do pedido inteiro como `"Pago"`, `"Adiantamento"` ou `"Devendo"`.
- **Modo Oculto (Minimizado):** O navegador roda com a janela minimizada (`minimize_window()`), evitando roubar o foco da tela do usuário, mas permitindo fácil depuração visual se necessário.
- **Setup Automatizado:** Conta com um arquivo `.bat` para configuração de ambiente em apenas um clique em novas máquinas (Windows).

## 🚀 Tecnologias Utilizadas

- **[Python 3.x](https://www.python.org/):** Linguagem principal do projeto.
- **[Selenium WebDriver](https://www.selenium.dev/):** Para automação da navegação e extração de dados.
- **[Gspread / Google API](https://docs.gspread.org/):** Para integração, leitura e escrita de dados no Google Sheets.
- **[python-dotenv](https://pypi.org/project/python-dotenv/):** Para gerenciamento seguro de credenciais e variáveis de ambiente.

## 🛠️ Pré-requisitos

Para rodar este projeto em qualquer máquina, você precisará ter instalado:
- [Python](https://www.python.org/downloads/) (Lembre-se de marcar a opção "Add Python to PATH" durante a instalação).
- Firefox instalado.

## ⚙️ Instalação e Configuração

A instalação deste projeto foi desenhada para ser o mais simples possível utilizando um script de bootstrap.

1. Clone este repositório:
   ```bash
   git clone https://github.com/per0za/automated-orders-bot.git
   ```

2. Acesse a pasta do projeto:

    ```bash
    cd automated-orders-bot
    ```

3. Configuração de Credenciais (MUITO IMPORTANTE):

    - Crie um arquivo chamado .env na raiz do projeto (use o .env.example como base, se houver).

    - Insira o ID da sua planilha do Google Sheets e outras chaves sensíveis neste arquivo.

    - Coloque o seu arquivo .json de credenciais de serviço do Google Cloud (ex: credenciais.json) na raiz do projeto.

    - *Nota: Estes arquivos estão no .gitignore e nunca devem ser commitados.*

4. Setup Automático:

    - Dê um duplo clique no arquivo setup_e_rodar.bat.

    - O script criará automaticamente o ambiente virtual (venv), instalará as dependências listadas no requirements.txt e iniciará a aplicação.

## 💻 Como Usar
Após realizar o setup inicial, sempre que quiser rodar a automação, basta executar o arquivo ```setup_e_rodar.bat novamente```. Ele identificará que o ambiente já está pronto, ativará o ```venv``` e rodará o script principal.

O navegador será aberto e minimizado na barra de tarefas para não atrapalhar o seu fluxo de trabalho, enquanto o console exibirá os logs das ações (leitura de pedidos, processamento de IDs e inserção no Sheets).

## 🔒 Segurança
As melhores práticas de segurança foram aplicadas neste projeto:

- Uso estrito de .gitignore para ocultar o ambiente virtual, arquivos de log de execução, caches do Python e, principalmente, arquivos contendo dados sensíveis.

- Nenhuma chave de API, número de telefone, ID de planilha ou credencial de acesso direto ao Google está *hardcoded* (escrita diretamente) no código-fonte.

Desenvolvido por [Erick Gabriel Peroza](https://github.com/per0za)