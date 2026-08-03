# Backlog Para Atualizacao Do JSON De Aulas

Este backlog orienta a IA responsavel pelo conteudo das aulas. O objetivo e melhorar o JSON carregado em `bases/aulas_guitarra_iniciante_com_imagens_base64.json`, deixando as aulas mais completas, guiadas e adequadas para aluno leigo.

## Objetivo Geral

Transformar o conteudo das aulas em uma trilha didatica completa para alguem que nunca tocou guitarra.

Cada aula deve ensinar:
- o que fazer;
- por que aquilo importa;
- como posicionar as maos;
- o que o aluno deve ouvir;
- quais erros evitar;
- quanto tempo praticar;
- como saber se conseguiu;
- qual e o proximo passo.

## Formato Recomendado Para Cada Aula

Cada aula do JSON deve conter, sempre que possivel:

- `title`: titulo claro e direto.
- `description`: resumo didatico da aula.
- `order`: ordem da aula na trilha.
- `is_published`: `true` para aula pronta.
- `module`: modulo didatico sugerido.
- `level`: `iniciante`, `basico`, `intermediario` ou `avancado`.
- `estimated_minutes`: duracao estimada.
- `objectives`: lista de objetivos.
- `prerequisites`: conhecimentos necessarios antes da aula.
- `practice_focus`: foco principal da pratica.
- `steps`: etapas sequenciais.

Status tecnico: os campos `module`, `level`, `estimated_minutes`, `objectives`, `prerequisites` e `practice_focus` ja sao suportados pela importacao/exportacao, pelo formulario administrativo e pelas telas de aulas.

## Contrato JSON Suportado Pela Importacao

Use uma lista de aulas na raiz do arquivo:

```json
[
  {
    "title": "Como Segurar a Palheta e Tirar o Primeiro Som",
    "description": "Aprenda a segurar a palheta sem tensao e tocar cordas soltas com som limpo.",
    "module": "Fundamentos para Iniciantes",
    "level": "iniciante",
    "estimated_minutes": 15,
    "objectives": [
      "Segurar a palheta sem apertar demais.",
      "Tocar uma corda por vez com movimento curto.",
      "Manter quatro ataques seguidos com volume parecido."
    ],
    "prerequisites": [
      "Guitarra afinada.",
      "Palheta disponivel.",
      "Sentar com o instrumento apoiado de forma estavel."
    ],
    "practice_focus": "Tocar cordas soltas devagar, com pulso relaxado e som uniforme.",
    "order": 1,
    "is_published": true,
    "steps": [
      {
        "title": "1. Objetivos da aula",
        "content": "<h4>Objetivos</h4><p>Nesta aula voce vai aprender a produzir seus primeiros sons limpos.</p>",
        "resource_type": "none",
        "path": null,
        "exercise_type": null,
        "exercise_params": {},
        "checklist_items": [
          "Entendi o objetivo da aula."
        ],
        "order": 1,
        "media_items": []
      },
      {
        "title": "2. Posicao da palheta",
        "content": "<p>Segure a palheta entre polegar e indicador, deixando apenas a ponta aparecer.</p><h5>Erro comum</h5><p>Apertar demais e travar o pulso.</p>",
        "resource_type": "image",
        "path": "data:image/jpeg;base64,...",
        "exercise_type": "technical_drills",
        "exercise_params": {
          "drill": "palheta_cordas_soltas"
        },
        "checklist_items": [
          "Consegui tocar quatro ataques seguidos com volume parecido.",
          "Mantive o pulso relaxado."
        ],
        "order": 2,
        "media_items": [
          {
            "title": "Video demonstrando o movimento",
            "media_type": "youtube_url",
            "path": "https://www.youtube.com/watch?v=ID_DO_VIDEO",
            "order": 1
          }
        ]
      }
    ]
  }
]
```

Campos aceitos na aula:
- `title`: obrigatorio.
- `description`: texto curto.
- `module`: agrupamento didatico, por exemplo `Fundamentos para Iniciantes`.
- `level`: usar `iniciante`, `basico`, `intermediario` ou `avancado`.
- `estimated_minutes`: numero inteiro em minutos.
- `objectives`: lista de textos ou texto multilinha.
- `prerequisites`: lista de textos ou texto multilinha.
- `practice_focus`: texto curto com o foco pratico.
- `order`: numero inteiro.
- `is_published`: booleano.
- `steps`: lista de etapas.

Regras importantes para a outra IA:
- A raiz do arquivo deve ser uma lista JSON, nao um objeto com chave `lessons`.
- `title` e obrigatorio em cada aula.
- `title` e obrigatorio em cada etapa.
- `objectives` e `prerequisites` devem preferencialmente ser listas de strings.
- `estimated_minutes` deve ser numero inteiro, sem texto como `"15 min"`.
- Use `resource_type: "none"` e `path: null` quando a etapa for apenas texto.
- Use `media_items` para anexos adicionais, como imagem mais video na mesma etapa.

Campos aceitos na etapa:
- `title`: obrigatorio.
- `content`: HTML simples.
- `resource_type`: `none`, `image`, `pdf`, `youtube_url` ou `video_url`.
- `path`: URL, caminho, `null` ou base64/data URI.
- `exercise_type`: opcional. Valores suportados: `identify_note`, `find_note`, `intervals`, `free_train`, `harmonic_dictation` ou `technical_drills`.
- `exercise_params`: objeto JSON opcional com parametros para abrir a ferramenta de exercicio.
- `checklist_items`: lista de strings ou texto multilinha com criterios de conclusao da etapa.
- `order`: numero inteiro.
- `media_items`: lista opcional de midias extras.

Campos aceitos em `media_items`:
- `title`: legenda opcional.
- `media_type`: `image`, `pdf`, `youtube_url`, `video_url` ou `fretboard`.
- `path`: URL, caminho, JSON do braco ou base64/data URI.
- `order`: numero inteiro.

## Formato Recomendado Para Cada Etapa

Cada etapa deve conter:

- `title`: nome da etapa.
- `content`: explicacao detalhada em HTML simples.
- `resource_type`: `none`, `image`, `youtube_url`, `video_url` ou `pdf`.
- `path`: caminho, URL ou base64 conforme o tipo de midia.
- `exercise_type`: exercicio opcional ligado a etapa.
- `exercise_params`: parametros opcionais do exercicio em objeto JSON.
- `checklist_items`: criterios objetivos para marcar a etapa como aprendida.
- `order`: ordem da etapa.
- `media_items`: anexos adicionais, quando necessario.

Cada etapa deve seguir este padrao didatico:

1. Explicacao curta.
2. Instrucao pratica.
3. Erro comum.
4. Como conferir se esta certo.
5. Tempo sugerido de pratica.

## Prioridade Alta

### 1. Revisar a trilha inicial para aluno zero

Objetivo: garantir que as primeiras aulas nao dependam de conhecimento previo.

Aulas recomendadas para a primeira fase:
- Conhecendo a guitarra e suas partes.
- Como sentar, apoiar o instrumento e relaxar.
- Nomes das cordas soltas.
- Como segurar a palheta.
- Primeiros sons limpos.
- Numeracao dos dedos.
- Exercicio cromatico 1-2-3-4.
- Primeiros acordes: Em e Am.
- Troca entre Em e Am.
- Primeira batida simples.
- Primeira musica com dois acordes.

Criterios de aceite:
- O aluno entende o que fazer mesmo sem professor ao lado.
- A primeira aula nao fala de escala, campo harmonico ou teoria avancada.
- Cada aula termina com um pequeno teste pratico.

### 2. Adicionar objetivos claros no inicio de cada aula

Objetivo: o aluno deve saber exatamente o que vai aprender.

Exemplo:
```html
<h4>Objetivos da aula</h4>
<ul>
  <li>Segurar a palheta sem tensionar a mao.</li>
  <li>Tocar uma corda por vez com movimento curto.</li>
  <li>Manter volume parecido em quatro ataques seguidos.</li>
</ul>
```

Criterios de aceite:
- Toda aula possui uma etapa inicial com objetivos.
- Os objetivos sao praticos e mensuraveis.

### 3. Adicionar bloco "Como saber se esta certo"

Objetivo: compensar a ausencia de professor presencial.

Exemplos de validacao:
- O som sai limpo, sem trastejar.
- As cordas que nao devem tocar ficam abafadas.
- A mao nao doi.
- A troca de acorde acontece sem parar o ritmo.
- O aluno consegue repetir o exercicio tres vezes.

Criterios de aceite:
- Toda aula tem pelo menos um bloco de verificacao.
- A linguagem e simples, direta e adequada a iniciante.

### 4. Adicionar bloco "Erros comuns"

Objetivo: antecipar dificuldades tipicas de iniciante.

Erros comuns a cobrir:
- apertar demais as cordas;
- tocar longe do traste;
- levantar muito os dedos;
- segurar a palheta com forca excessiva;
- travar o pulso;
- parar o ritmo para trocar acorde;
- apoiar a guitarra de forma instavel;
- tocar cordas que nao fazem parte do acorde.

Criterios de aceite:
- Cada aula tem pelo menos tres erros comuns.
- Cada erro vem com uma correcao pratica.

### 5. Melhorar as midias de apoio

Objetivo: cada aula deve ter recursos visuais suficientes para ensinar sem ambiguidade.

Midias recomendadas:
- imagem da postura correta;
- imagem da mao esquerda;
- imagem da mao da palheta;
- diagrama de acorde;
- imagem do braco com casas destacadas;
- video curto demonstrando o movimento;
- PDF resumo apenas quando fizer sentido.

Criterios de aceite:
- Toda aula essencial tem pelo menos uma imagem ou video.
- Imagens mostram exatamente a acao ensinada.
- Videos devem ser curtos e diretamente relacionados ao passo.

## Prioridade Media

### 6. Criar avaliacoes praticas ao fim de cada aula

Objetivo: dar criterio para concluir a aula.

Modelo de etapa final:
```html
<h4>Teste se aprendeu</h4>
<ol>
  <li>Repita o exercicio por 60 segundos.</li>
  <li>Observe se o som continua limpo.</li>
  <li>Marque a aula como concluida apenas se conseguiu repetir sem dor e sem pressa.</li>
</ol>
```

Criterios de aceite:
- Toda aula termina com uma avaliacao pratica.
- A avaliacao usa metas simples: tempo, repeticoes ou clareza do som.

### 7. Adicionar rotina diaria sugerida

Objetivo: ajudar o aluno a saber o que praticar fora da aula.

Exemplo:
```html
<h4>Treino de hoje - 10 minutos</h4>
<ul>
  <li>2 min: cordas soltas com palheta.</li>
  <li>3 min: exercicio 1-2-3-4 devagar.</li>
  <li>3 min: troca Em para Am.</li>
  <li>2 min: tocar junto com metronomo lento.</li>
</ul>
```

Criterios de aceite:
- Toda aula inicial tem rotina de 5 a 15 minutos.
- A rotina e realista para iniciante.

### 8. Ligar cada aula a exercicios da plataforma

Objetivo: conectar conteudo com pratica interativa.

Mapeamento sugerido:
- Nomes das cordas -> exercicio de identificar nota.
- Notas nas cordas 6 e 5 -> exercicio de encontrar nota.
- Cromatico -> tecnica e aquecimento.
- Pentatonica -> treino livre carregando escala.
- Acordes -> dicionario de acordes e pratica de troca.

Criterios de aceite:
- Cada aula tem uma etapa "Pratique na ferramenta".
- O texto informa qual ferramenta abrir e o que selecionar.

### 9. Inserir repertorio progressivo

Objetivo: fazer o aluno tocar musica real cedo.

Sequencia recomendada:
- Musica com 1 acorde para ritmo.
- Musica com 2 acordes: Em e Am.
- Musica com 3 acordes: G, C e D.
- Musica com 4 acordes: G, D, Em e C.
- Riff simples em uma corda.
- Frase simples com pentatonica menor.

Criterios de aceite:
- O aluno toca algo musical ate a aula 5 ou 6.
- As cifras usam acordes ja ensinados.

## Prioridade Baixa

### 10. Criar aulas de revisao

Objetivo: consolidar antes de avancar.

Aulas sugeridas:
- Revisao 1: postura, palheta e som limpo.
- Revisao 2: cromatico e troca de cordas.
- Revisao 3: primeiros acordes.
- Revisao 4: ritmo e troca de acordes.

Criterios de aceite:
- Cada revisao mistura conteudo anterior.
- Cada revisao tem checklist de dominio.

### 11. Criar aulas de diagnostico

Objetivo: ajudar aluno que ja sabe algo a entrar no ponto correto da trilha.

Diagnosticos sugeridos:
- Consigo tirar som limpo?
- Sei trocar dois acordes?
- Sei manter ritmo?
- Sei encontrar notas no braco?

Criterios de aceite:
- O diagnostico orienta qual aula fazer.
- O texto nao reprova o aluno, apenas recomenda caminho.

### 12. Melhorar linguagem para aluno leigo

Objetivo: remover termos tecnicos antes da explicacao.

Regras de escrita:
- Evitar "tonica", "intervalo", "campo harmonico" nas primeiras aulas, salvo explicando em linguagem simples.
- Usar frases curtas.
- Dar comandos observaveis.
- Preferir "coloque o dedo 2 na casa 2 da corda 5" em vez de teoria abstrata.
- Explicar uma novidade por vez.

Criterios de aceite:
- Um iniciante consegue seguir a aula sem pesquisar termos externos.
- Termos teoricos aparecem apenas quando necessarios e explicados.

## Checklist De Qualidade Para A Outra IA

Antes de entregar uma aula atualizada, verificar:

- A aula tem objetivo claro.
- A aula tem passos curtos e ordenados.
- A aula mostra como praticar.
- A aula explica erros comuns.
- A aula explica como conferir se esta certo.
- A aula tem imagem ou video quando o movimento fisico importa.
- A aula tem teste final.
- A aula indica proxima aula ou proxima pratica.
- O conteudo nao pula etapas.
- O JSON continua valido.

## Observacoes Sobre Midias

Para imagens:
- usar imagens claras, bem enquadradas e especificas;
- evitar imagem decorativa;
- mostrar mao, corda, casa ou postura quando esse for o conteudo;
- quando usar base64, garantir que o tamanho do JSON continue aceitavel.

Para videos:
- preferir videos curtos por etapa;
- evitar videos longos sem marcacao de tempo;
- usar YouTube quando o sistema ja suportar `youtube_url`;
- cada video deve demonstrar exatamente o passo descrito.

Para PDFs:
- usar como resumo imprimivel;
- nao substituir a explicacao principal da aula por PDF;
- manter PDF como apoio, nao como conteudo obrigatorio escondido.
