# Rematch Analyzer

Uma aplicação web desenvolvida em Flask para análise avançada e comparação de jogadores do jogo de futebol online **Rematch**. Utiliza scraping dinâmico com Playwright para obter estatísticas do RematchTracker e Inteligência Artificial (Google Gemini) para gerar insights sobre o estilo de jogo, pontos fortes e fracos dos jogadores.

## 🚀 Início Rápido

### Pré-requisitos
Certifique-se de ter o Python instalado (versão 3.8+ recomendada).

### Instalação

1. Instale as dependências listadas no `requirements.txt`:
```bash
pip install -r requirements.txt
```

2. Instale os navegadores necessários para o Playwright (usado para o scraping dinâmico):
```bash
playwright install chromium
```

3. Execute a aplicação:
```bash
python app.py
```
O servidor será iniciado em `http://127.0.0.1:5000` (ou na porta configurada pelo Flask).

## ✨ Funcionalidades

- **Scraping Dinâmico Avançado:** Coleta dados em tempo real da página do jogador no RematchTracker (Rank, Grade, Playing Style) extraindo informações complexas e elementos dinâmicos usando Playwright.
- **Análise Individual com IA:** Utiliza o Google Gemini 2.5 Pro para analisar o perfil do jogador, destacando pontos fortes, fracos e fornecendo recomendações com base nas suas estatísticas e área de atuação (Ofensiva/Defensiva/Geral).
- **Duelo de Jogadores:** Permite comparar o perfil de dois jogadores lado a lado, avaliando qual tem vantagem técnica, diferenças de estilo de jogo e desempenho estatístico.
- **Processamento de Estatísticas:** Calcula métricas avançadas como taxa de vitória, precisão de chutes, participação em gols, entre outras.

## ⚙️ Configuração

Atualmente, o projeto utiliza chaves de API embutidas diretamente no código (como a do `google.generativeai`). Para um ambiente de produção seguro, recomenda-se configurar essas chaves através de variáveis de ambiente.

| Variável Necessária (Sugestão) | Descrição |
|----------|-------------|
| `GEMINI_API_KEY` | Chave de API para o Google Gemini |
| `FLASK_SECRET_KEY` | Chave secreta para sessões do Flask |

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask, Python
- **Scraping:** Playwright, BeautifulSoup4, requests
- **IA:** Google Generative AI (Gemini)
- **Frontend:** HTML, Jinja2 Templates (servidos pelo Flask)

## 📄 Licença

MIT