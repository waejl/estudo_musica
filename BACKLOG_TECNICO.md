# Backlog Tecnico

Este backlog organiza as melhorias tecnicas para transformar a plataforma em um fluxo guiado de aprendizado de guitarra para alunos leigos.

## Prioridade Alta

### 1. Criar progresso de aulas por usuario - CONCLUIDO

Objetivo: permitir que o aluno continue de onde parou e que o sistema recomende a proxima aula.

Escopo tecnico:
- Criar tabela/modelo para progresso de aula por usuario. CONCLUIDO
- Registrar aula iniciada, etapa atual, etapas concluidas e aula concluida. CONCLUIDO
- Exibir status na lista de aulas. CONCLUIDO
- Exibir botao "Continuar aula" quando houver progresso parcial. CONCLUIDO

Criterios de aceite:
- Um aluno consegue iniciar uma aula e marcar etapas como concluidas. CONCLUIDO
- Ao voltar para a lista de aulas, a aula mostra status correto. CONCLUIDO
- O dashboard consegue mostrar a proxima aula ou aula em andamento. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/models.py`
- `app/guitar_study/routes.py`
- `app/guitar_study/api_routes.py`
- `app/guitar_study/templates/guitar_study/lessons_list.html`
- `app/guitar_study/templates/guitar_study/lesson_view.html`
- `sql/*.sql`

### 2. Transformar a lista de aulas em trilha de curso - CONCLUIDO

Objetivo: reduzir a sensacao de biblioteca solta e mostrar uma sequencia didatica clara.

Escopo tecnico:
- Agrupar aulas por modulo/nivel. CONCLUIDO
- Destacar a proxima aula recomendada. CONCLUIDO
- Mostrar ordem, status, duracao estimada e dificuldade. CONCLUIDO
- Manter compatibilidade com aulas base e aulas de escola. CONCLUIDO

Criterios de aceite:
- A pagina de aulas mostra uma trilha ordenada. CONCLUIDO
- O aluno iniciante entende qual aula fazer primeiro. CONCLUIDO
- Aulas avancadas nao competem visualmente com aulas iniciais. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/templates/guitar_study/lessons_list.html`
- `app/guitar_study/routes.py`
- `app/guitar_study/models.py`
- `app/school_admin/forms.py`
- `app/school_admin/templates/school_admin/lesson_form.html`

### 3. Atualizar dashboard para "Treino de Hoje" - CONCLUIDO

Objetivo: fazer o dashboard orientar o estudo diario, nao apenas mostrar estatisticas.

Escopo tecnico:
- Criar bloco principal "Treino de hoje". CONCLUIDO
- Mostrar aula em andamento ou proxima aula. CONCLUIDO
- Mostrar exercicios recomendados com base na aula atual. CONCLUIDO
- Manter os cards de estatisticas como informacao secundaria. CONCLUIDO

Criterios de aceite:
- Um aluno novo ve uma chamada clara para comecar do zero. CONCLUIDO
- Um aluno com progresso ve exatamente onde continuar. CONCLUIDO
- As recomendacoes nao apontam para conteudo avancado antes do basico. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/routes.py`
- `app/guitar_study/templates/guitar_study/dashboard.html`

### 4. Integrar aulas com exercicios existentes - CONCLUIDO

Objetivo: cada aula deve levar o aluno a uma pratica concreta.

Escopo tecnico:
- Permitir que uma etapa de aula tenha um link para exercicio especifico. CONCLUIDO
- Suportar parametros como tipo de exercicio, cordas, casas, nota, escala ou acorde. CONCLUIDO
- Exibir CTA de pratica dentro da etapa da aula. CONCLUIDO

Criterios de aceite:
- Uma aula de notas nas cordas 6 e 5 consegue abrir exercicio limitado a esse conteudo. CONCLUIDO
- Uma aula de escala consegue abrir treino da escala correspondente. CONCLUIDO
- O resultado do exercicio pode ser associado ao estudo do aluno. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/templates/guitar_study/lesson_view.html`
- `app/guitar_study/templates/guitar_study/exercises.html`
- `app/guitar_study/static/js/app.js`
- `app/guitar_study/static/js/fretboard.js`
- `app/guitar_study/api_routes.py`

### 5. Criar checklist/teste de conclusao de aula - CONCLUIDO

Objetivo: dar ao aluno um criterio claro para saber se aprendeu.

Escopo tecnico:
- Permitir checklist por aula ou por etapa. CONCLUIDO
- Registrar respostas simples do aluno. CONCLUIDO
- Permitir marcar aula como concluida apenas apos checklist. CONCLUIDO

Criterios de aceite:
- A aula mostra um bloco "Teste se aprendeu". CONCLUIDO
- O aluno consegue marcar itens como feitos. CONCLUIDO
- A conclusao fica persistida por usuario. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/models.py`
- `app/guitar_study/routes.py`
- `app/guitar_study/api_routes.py`
- `app/guitar_study/templates/guitar_study/lesson_view.html`
- `sql/*.sql`

## Prioridade Media

### 6. Reorganizar menu por nivel de aprendizado - CONCLUIDO

Objetivo: evitar que iniciantes sejam expostos cedo demais a ferramentas avancadas.

Escopo tecnico:
- Separar menu em "Comecar", "Praticar", "Repertorio" e "Teoria". CONCLUIDO
- Manter todas as paginas acessiveis. CONCLUIDO
- Destacar "Curso" ou "Comecar do zero" como entrada principal. CONCLUIDO

Criterios de aceite:
- O menu fica mais simples para aluno iniciante. CONCLUIDO
- Modos gregos, harmonia e circulo de quintas ficam em area avancada. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/templates/guitar_study/_menu.html`
- `app/guitar_study/templates/guitar_study/base.html`

### 7. Melhorar modelo de aulas com metadados didaticos - CONCLUIDO

Objetivo: dar suporte estrutural a nivel, modulo, duracao, prerequisitos e objetivos.

Escopo tecnico:
- Adicionar campos opcionais em `Lesson`. CONCLUIDO
- Atualizar importacao/exportacao de aulas. CONCLUIDO
- Atualizar formulario administrativo. CONCLUIDO
- Exibir metadados nas telas do aluno. CONCLUIDO

Campos suportados:
- `module`
- `level`
- `estimated_minutes`
- `objectives`
- `prerequisites`
- `practice_focus`

Criterios de aceite:
- JSON importado consegue preencher os novos campos. CONCLUIDO
- A tela de administracao permite editar esses campos. CONCLUIDO
- A tela de aulas usa os metadados quando existirem. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/models.py`
- `app/school_admin/forms.py`
- `app/school_admin/routes.py`
- `app/guitar_study/templates/guitar_study/lessons_list.html`
- `app/guitar_study/templates/guitar_study/lesson_view.html`
- `app/school_admin/templates/school_admin/lesson_form.html`
- `scripts/import_data.py`
- `sql/20260724_000000_inicializar_banco.sql`
- `sql/20260731_120000_adicionar_metadados_didaticos_aulas.sql`

### 8. Criar rotas/API para recomendacao didatica - CONCLUIDO

Objetivo: centralizar a regra de "proximo passo" do aluno.

Escopo tecnico:
- Criar funcao ou service para calcular recomendacao. CONCLUIDO
- Usar progresso de aulas e sessoes de estudo. CONCLUIDO
- Evitar regras fixas no dashboard. CONCLUIDO

Criterios de aceite:
- Dashboard e lista de aulas usam a mesma regra. CONCLUIDO
- Aluno novo recebe aula inicial. CONCLUIDO
- Aluno com aula incompleta recebe continuacao. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/routes.py`
- `app/guitar_study/api_routes.py`
- `app/guitar_study/services/`

### 9. Associar sessoes de estudo a aulas - CONCLUIDO

Objetivo: saber quanto tempo o aluno estudou em cada aula ou modulo.

Escopo tecnico:
- Adicionar campos opcionais em sessoes de estudo para `lesson_id` e `resource_id`. CONCLUIDO
- Atualizar registro de pratica. CONCLUIDO
- Exibir tempo estudado no relatorio administrativo. CONCLUIDO

Criterios de aceite:
- Praticas iniciadas dentro de uma aula podem ser vinculadas a ela pela API. CONCLUIDO
- Painel administrativo resume tempo de estudo dos alunos. CONCLUIDO

Arquivos alterados:
- `app/guitar_study/models.py`
- `app/guitar_study/api_routes.py`
- `app/guitar_study/templates/guitar_study/lesson_view.html`
- `sql/*.sql`

## Prioridade Baixa

### 10. Criar modo "iniciante" nas ferramentas - CONCLUIDO

Objetivo: simplificar telas teoricas para quem esta comecando.

Escopo tecnico:
- Criar modo visual com menos controles. CONCLUIDO
- Mostrar entrada principal por curso/trilha antes das ferramentas avancadas. CONCLUIDO
- Guardar preferencia por usuario. CONCLUIDO

Criterios de aceite:
- Iniciante recebe fluxo principal por curso e menu organizado por nivel. CONCLUIDO
- Usuario avancado pode alternar para modo completo nas configuracoes. CONCLUIDO

### 11. Criar relatorios para professor/admin - CONCLUIDO

Objetivo: permitir acompanhamento de alunos por escola.

Escopo tecnico:
- Listar progresso dos alunos. CONCLUIDO
- Mostrar aulas concluidas, tempo de estudo e aulas em andamento. CONCLUIDO
- Filtrar por escola/superadmin conforme permissoes atuais. CONCLUIDO

Criterios de aceite:
- Admin/professor consegue ver atividade agregada dos alunos. CONCLUIDO
- Admin/professor consegue identificar progresso recente por aula. CONCLUIDO

### 12. Melhorar testes automatizados do fluxo didatico - CONCLUIDO

Objetivo: proteger progresso, importacao de aulas e recomendacao de estudo.

Escopo tecnico:
- Testar progresso de aula. CONCLUIDO
- Testar importacao de JSON com novos campos. CONCLUIDO
- Validar fluxo com suite completa. CONCLUIDO

Criterios de aceite:
- Testes cobrem criacao de progresso ao abrir aula. CONCLUIDO
- Testes cobrem aluno com aula em andamento. CONCLUIDO
- Testes cobrem aluno com aula concluida. CONCLUIDO

## Validacao final

- `docker compose exec -T web python -m compileall app scripts`: OK.
- Parse Jinja dos templates alterados: OK.
- `docker compose exec -T web pytest -q`: 40 testes passando.
- Migração `sql/20260731_120000_adicionar_metadados_didaticos_aulas.sql` aplicada no PostgreSQL em execução.
