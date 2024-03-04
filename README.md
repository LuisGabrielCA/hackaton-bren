# Hackaton-Bren

## Descrição

Este é um projeto de Prova de Conceito (PoC) para desenvolver um agente de vendas utilizando a LangChain para facilitar conversas inteligentes.
<br>

## Tecnologias Utilizadas
- LangGraph
- FastAPI

<br>

## Instalação
1- Navegue até o diretório do projeto, execute o comando:
```bash
$ pip install -r requirements.txt
```

2- Renomeie o arquivo .env.example para .env e preencha as variáveis de ambiente conforme necessário. Aqui estão as variáveis que você precisará definir:
```
OPENAI_API_KEY
TAVILY_API_KEY

3- Inicie o servidor da API entrando na pasta app e executando o comando abaixo:
```bash
$ uvicorn main:app --reload 

4- O servidor estara rodando na porta 8000 como default.
```

<br>