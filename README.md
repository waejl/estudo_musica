# Guitar Study — Plataforma para Estudo de Guitarra

Uma aplicação web moderna, responsiva e robusta focada no estudo de teoria musical aplicada à guitarra. Desenvolvida do zero absoluto com **Python (Flask), PostgreSQL, Docker, Docker Compose, Bootstrap 5 e JavaScript (ES Modules)**.

Todo o sistema é encapsulado de forma modular sob o Blueprint independente `guitar_study`, mapeado sob o prefixo obrigatório `/guitar-study`.

---

## 🚀 Como Iniciar (Quick Start)

### 1. Requisitos
* Docker instalado
* Docker Compose instalado

### 2. Configurando o Ambiente
Como boa prática de segurança de credenciais, o arquivo `.env` não é versionado. Copie o arquivo `.env.example` criado na raiz do projeto:
```bash
cp .env.example .env
```

### 3. Rodando com um único comando
Suba toda a infraestrutura orquestrada em containers com o build automático:
```bash
docker compose up --build
```

O Docker Compose inicializará:
1. **guitar_study_db**: Container PostgreSQL 16 saudável com volume persistente `postgres_data`. Ele roda automaticamente o script de migração e sementes iniciais localizado em `sql/` para criar todas as tabelas e preencher o banco.
2. **guitar_study_web**: Container da aplicação Flask rodando sob o servidor Gunicorn robusto de produção, com suporte a hot-reload para desenvolvimento.

### 4. Acesso ao Sistema
Abra seu navegador e acesse a URL da plataforma:
👉 **[http://localhost:5000/guitar-study/](http://localhost:5000/guitar-study/)**

O sistema abrirá na tela de login. Use as credenciais do usuário de demonstração inserido automaticamente pelas sementes do Postgres:
* **Usuário:** `demo`
* **Senha:** `admin123`

---

## 🎯 Funcionalidades Principais Implementadas

1. **Dashboard do Guitarrista:** Acompanhamento de tempo de estudo em tempo real, contagem de sessões realizadas, sequência de dias seguidos estudados (streak), progresso semanal, últimas atividades detalhadas, metas ativas com barra de progresso real e recomendações dinâmicas de tópicos para praticar.
2. **Braço de Guitarra Interativo:** O núcleo do estúdio! Um braço gerado dinamicamente com HTML/CSS de 22 casas, marcadores de bolinhas duplo na casa 12, espessuras reais de cordas (da fina E aguda até a grossa E grave).
   * **Áudio Realista:** Clicar em qualquer nota toca a frequência física correspondente sintetizada em tempo real via **Web Audio API** do navegador (com harmônicos e decay de guitarra acústica, funcionando offline!).
   * **Análise da Nota:** O clique revela nome, oitava científica, frequência exata em Hz, nota enarmônica, corda/casa e uma breve explicação teórica do intervalo dela em relação à tônica escolhida.
   * **Modos de Exibição:** Alterne instantaneamente entre ocultar todas as notas, mostrar tudo, mostrar somente notas naturais, somente a tônica, notas por letra (C, D, E) ou símbolos de intervalos (1, b3, 5).
3. **Estudo de Escalas:** Filtros por Tônica, Tipo de Escala (Maior, Menor natural, Harmônica, Melódica, Pentatônicas, Blues, Cromática) e tipo de exibição. Revela as notas e graus, fórmula, acordes recomendados do Campo Harmônico, audição da escala inteira ascendente/descendente e mapeia os padrões inteiros sobre o braço com a tônica em destaque vermelho-fogo com brilho.
4. **Estudo de Modos Gregos:** Análise teórica de Jônio, Dórico, Frígio, Lídio, Mixolídio, Eólio e Lócrio, detalhando acorde característico, sensação emocional provocada, nota de sabor característica e mapeamento no braço.
   * **Comparador de Modos:** Escolha dois modos e a tônica e compare em tempo real a tabela comparativa de graus, quais notas são comuns (iguais) e quais notas são diferentes (foco do solo!). O braço sobrepõe ambos para você ver as diferenças geométricas de digitação!
5. **Dicionário de Acordes:** Tríades e tétrades (maior, menor, maj7, dominante, m7, m7b5, dim7, sus2, sus4) com formação teórica, audição arpejada realista do acorde (strumming) e **Diagramas do Sistema CAGED** dinâmicos mostrando posições de dedos e casas relativas.
6. **Exercícios Interativos (Treino Gamificado):**
   * *Exercício 1: Identificar a Nota:* O sistema sorteia uma corda/casa no braço de forma aleatória e toca seu som; você responde por múltipla escolha.
   * *Exercício 2: Encontrar a Nota:* O sistema sorteia uma nota (ex: D#) e você deve clicar na posição geométrica correta diretamente no braço!
   * *Exercício 3: Identificar o Intervalo:* Desafio de identificar a distância em graus relativos entre a tônica mostrada e a nota destacada.
   * Ao fim de 10 rodadas, calcula o score %, tempo total e grava os resultados persistentes na tabela de tentativas do Postgres!
7. **Cronômetro Integrado de Prática:** Ao estudar o braço ou escalas, você pode iniciar um cronômetro de estudos. Ao terminar, o sistema permite salvar no seu histórico com anotações pessoais do que praticou no dia.
8. **Configurações:** Altere seu perfil (Nome, E-mail, Senha), preferências de exibição do braço (afinação padrão, casas 21/22/24, sustenidos/bemóis, tema claro/escuro) e **cadastre afinações personalizadas** que ficam imediatamente disponíveis nos seletores!

---

## 🛠️ Arquitetura do Projeto e Estrutura de Pastas

A aplicação segue princípios de design limpo de software, aplicando **SOLID, DRY, Repository/Service Pattern e Application Factory**.

```text
estudo_musica/ (Raiz do repositório)
├── app/
│   ├── __init__.py                # Application Factory (create_app), setup de logs rotativos e tratamento global de erros
│   ├── config.py                  # Classes de configuração de ambiente (Dev, Prod, Test com SQLite em memória)
│   ├── extensions.py              # Instâncias das extensões isoladas (SQLAlchemy, LoginManager)
│   └── guitar_study/              # Módulo exclusivo do Blueprint guitar_study (totalmente isolado)
│       ├── __init__.py            # Inicializador e registro de Blueprint sob o prefixo /guitar-study
│       ├── models.py              # Mapeamento do banco de dados (Users, UserSettings, Favorites, StudySessions, etc.)
│       ├── routes.py              # Rotas HTML (renderizadores de Dashboard, Fretboard, Scales, Modes, Chords, etc.)
│       ├── auth_routes.py         # Rotas de segurança (login, register, logout, alteração de perfil e afinação custom)
│       ├── api_routes.py          # APIs JSON RESTful de notas, braço, escalas, favoritos, exercícios e estudos
│       ├── services/
│       │   └── music_theory.py    # Serviço de teoria musical pura (cálculos de braço, acordes, escalas e enarmônicos)
│       ├── templates/
│       │   └── guitar_study/      # Templates HTML exclusivos (base, _menu, login, register, dashboard, fretboard, etc.)
│       └── static/                # Arquivos estáticos exclusivos servidos sob /guitar-study/static/...
│           ├── css/
│           │   └── app.css        # Estilos customizados da plataforma, cards, e o design do Braço de Guitarra
│           └── js/
│               ├── app.js         # Lógica global (favorites toggle, toast bootstrap, estudos sync)
│               ├── audio-engine.js# Engine de som que sintetiza áudio de guitarra via Web Audio API
│               └── fretboard.js   # Componente dinâmico que renderiza e gerencia cliques no braço
├── sql/
│   └── 20260724_000000_inicializar_banco.sql # Script SQL inicial executado pelo postgres-initdb (Tabelas e sementes)
├── tests/                         # Testes automatizados com Pytest
│   ├── conftest.py                # Fixtures e setup do banco de testes em memória SQLite
│   ├── test_music_theory.py       # Testes unitários do serviço de teoria musical
│   ├── test_auth.py               # Testes de autenticação, registro de usuários e controle de acesso
│   └── test_api.py                # Testes de endpoints de API RESTful
├── docs/
│   └── backlog.html               # Backlog de desenvolvimento persistente com trilha de auditoria
├── Dockerfile                     # Construção do container da aplicação web Flask/Gunicorn (Python 3.12-slim)
├── compose.yaml                   # Orquestração de serviços web e db (PostgreSQL 16)
├── requirements.txt               # Dependências do Python (Flask, psycopg2, cryptography, pytest, ruff)
├── .env.example                   # Exemplo de configurações de variáveis de ambiente
└── run.py                         # Ponto de entrada que carrega dotenv e roda create_app()
```

---

## 🧪 Como Executar os Testes Automatizados

Os testes rodam de forma totalmente isolada em banco de dados SQLite rápido em memória, garantindo alta velocidade e segurança de regressões.

### Executando dentro do container Docker ativo:
```bash
docker exec -it guitar_study_web pytest -v
```

### Executando localmente (caso possua ambiente virtual configurado):
```bash
pip install -r requirements.txt
pytest -v
```

---

## 🪵 Como Consultar os Logs

A aplicação possui um sistema de logs rotativos de até 10MB que registra inicializações, logins, tentativas de exercícios e erros do servidor de forma organizada, preservando dados sensíveis de usuários (senhas/cookies nunca são logados).

### Ver logs no host via terminal do Docker Compose:
```bash
docker compose logs -f web
```

### Consultar o arquivo de logs persistente gravado em disco:
```bash
tail -n 100 logs/guitar_study.log
```

---

## 🗄️ Acesso ao Banco de Dados e Gerenciamento (PostgreSQL)

O banco de dados PostgreSQL persiste de forma segura sob o volume nomeado `postgres_data`.

### Acessar a CLI do PostgreSQL (psql) diretamente:
```bash
docker exec -it guitar_study_db psql -U guitar_user -d guitar_db
```

### Realizar Backup completo das tabelas e dados:
```bash
docker exec -t guitar_study_db pg_dumpall -c -U guitar_user > backup_guitar_study.sql
```

### Restaurar Backup completo:
```bash
cat backup_guitar_study.sql | docker exec -i guitar_study_db psql -U guitar_user -d guitar_db
```

---

## 🔒 Segurança e Práticas de Código
* **Proteção contra Injeção de SQL:** Utilização nativa do ORM Flask-SQLAlchemy com parametrização de queries automática.
* **Criptografia Segura:** Senhas de usuários armazenadas com hash forte através do algoritmo `scrypt` do Werkzeug Security.
* **Isolamento de Dados:** Filtros rigorosos associando sessões de estudos, afinações e favoritos ao ID do `current_user` logado, impedindo que dados vazem ou sejam acessados por terceiros.
* **Cookies Protegidos:** Cookies de sessão HTTPOnly e com SameSite "Lax" ativo para evitar sequestro de sessões (XSS/CSRF).
* **Escape Nativo:** Todos os inputs de formulários do Jinja2 sofrem escape nativo impedindo XSS no frontend.
* **Ruff:** Verificação de padrões de formatação PEP8 do Python para manter o código limpo, legível e livre de detritos.
