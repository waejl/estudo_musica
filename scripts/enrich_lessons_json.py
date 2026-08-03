import json

STEP_EXERCISE_DEFAULTS = {
    1: ("technical_drills", {"drill": "som_limpo", "strings": "1,2,3,4,5,6"}),
    2: ("technical_drills", {"drill": "palhetada_alternada", "strings": "1,2,3,4,5,6", "bpm": 60}),
    3: ("technical_drills", {"drill": "chromatic_1234", "frets": "1-4", "bpm": 50}),
    4: ("technical_drills", {"drill": "finger_independence", "patterns": "1324,1423,2413", "bpm": 45}),
    5: ("find_note", {"strings": "6,5", "notes": "C,D,E,F,G,A,B", "frets": "0-12"}),
    6: ("free_train", {"focus": "open_chords", "chords": "Em,Am,C,G"}),
    7: ("technical_drills", {"drill": "rhythm_basic", "patterns": "seminimas,colcheias", "bpm": 60}),
    8: ("free_train", {"root": "A", "scale": "pentatonic_minor", "position": 1}),
    9: ("free_train", {"focus": "melodic_chords", "chords": "C,Am", "bpm": 50}),
}

VIDEO_LINKS = {
    1: [
        (1, "Aula de apoio: guitarra do zero absoluto", "https://www.youtube.com/watch?v=O8GG68sJs24"),
        (5, "Revisão: noções básicas para começar na guitarra", "https://www.youtube.com/watch?v=X3182sxwuuU"),
    ],
    2: [
        (2, "Apoio visual: posicionamento de palheta e primeiros movimentos", "https://www.youtube.com/watch?v=2sXe55LwR4o"),
        (5, "Repertório fácil: primeira música com poucos acordes", "https://www.youtube.com/watch?v=rFXpbrJ6gaM"),
    ],
    3: [
        (6, "Aula de apoio: como usar o metrônomo", "https://www.youtube.com/watch?v=Yc_ZmW_KRXo"),
        (7, "Repertório técnico: riffs fáceis para iniciantes", "https://www.youtube.com/watch?v=vBEcWOOR_F8"),
    ],
    4: [
        (6, "Aplicação musical: músicas fáceis na guitarra", "https://www.youtube.com/watch?v=PFkA50I8j6I"),
    ],
    5: [
        (4, "Apoio: localização das notas no braço", "https://www.youtube.com/watch?v=-x9meZWShhg"),
        (6, "Repertório: riffs fáceis usando regiões conhecidas", "https://www.youtube.com/watch?v=vBEcWOOR_F8"),
    ],
    6: [
        (2, "Apoio: acordes básicos para violão e guitarra", "https://www.youtube.com/watch?v=oCLdgA8OfrY"),
        (5, "Repertório: 4 acordes e várias músicas", "https://www.youtube.com/watch?v=_Mo5f7Huic4"),
        (7, "Repertório: sequência G D Em C", "https://www.youtube.com/watch?v=sKUXP9LcYeQ"),
    ],
    7: [
        (1, "Apoio: como ouvir a pulsação de uma música", "https://www.youtube.com/watch?v=dFELF2TWYs0"),
        (3, "Apoio: semínimas, colcheias e figuras rítmicas", "https://www.youtube.com/watch?v=9_Myylb1sqg"),
        (6, "Aulão de ritmo: treino de batidas", "https://www.youtube.com/watch?v=Io6_mtL9abs"),
    ],
    8: [
        (2, "Apoio: pentatônica na guitarra", "https://www.youtube.com/watch?v=no9U6vBumcY"),
        (7, "Aplicação: solos fáceis com pentatônica", "https://www.youtube.com/watch?v=vZVGsh0OOdE"),
        (8, "Repertório: 3 solos fáceis para iniciantes", "https://www.youtube.com/watch?v=rX1EmBt-DhE"),
    ],
    9: [
        (1, "Apoio: tríades e formação de acordes", "https://www.youtube.com/watch?v=hR_UhlUGS4A"),
        (3, "Apoio: CAGED na prática", "https://www.youtube.com/watch?v=DwnfzVpQlxs"),
        (7, "Apoio: acordes e tríades na guitarra", "https://www.youtube.com/watch?v=sGqWlslzEV4"),
    ],
}

REPERTORY_BLOCKS = {
    2: '<h4>Repertório sugerido em vídeo</h4><ul><li><a href="https://www.youtube.com/watch?v=rFXpbrJ6gaM" target="_blank" rel="noopener">Músicas fáceis com 2 acordes</a></li></ul>',
    3: '<h4>Repertório sugerido em vídeo</h4><ul><li><a href="https://www.youtube.com/watch?v=vBEcWOOR_F8" target="_blank" rel="noopener">10 riffs fáceis de guitarra para iniciantes</a></li></ul>',
    4: '<h4>Repertório sugerido em vídeo</h4><ul><li><a href="https://www.youtube.com/watch?v=PFkA50I8j6I" target="_blank" rel="noopener">6 músicas fáceis na guitarra</a></li></ul>',
    5: '<h4>Repertório sugerido em vídeo</h4><ul><li><a href="https://www.youtube.com/watch?v=vBEcWOOR_F8" target="_blank" rel="noopener">Riffs fáceis para aplicar notas no braço</a></li></ul>',
    6: '<h4>Repertório sugerido em vídeo</h4><ul><li><a href="https://www.youtube.com/watch?v=_Mo5f7Huic4" target="_blank" rel="noopener">4 acordes e várias músicas</a></li><li><a href="https://www.youtube.com/watch?v=sKUXP9LcYeQ" target="_blank" rel="noopener">Músicas com G D Em C</a></li></ul>',
    7: '<h4>Repertório sugerido em vídeo</h4><ul><li><a href="https://www.youtube.com/watch?v=Io6_mtL9abs" target="_blank" rel="noopener">Treino de ritmo para tocar junto</a></li></ul>',
    8: '<h4>Repertório sugerido em vídeo</h4><ul><li><a href="https://www.youtube.com/watch?v=vZVGsh0OOdE" target="_blank" rel="noopener">Solos fáceis com pentatônica</a></li><li><a href="https://www.youtube.com/watch?v=rX1EmBt-DhE" target="_blank" rel="noopener">3 solos fáceis para iniciantes</a></li></ul>',
    9: '<h4>Repertório sugerido em vídeo</h4><ul><li><a href="https://www.youtube.com/watch?v=DwnfzVpQlxs" target="_blank" rel="noopener">CAGED para ligar acordes e melodia</a></li></ul>',
}


def should_skip_exercise(title):
    lowered = title.lower()
    return "objetivo" in lowered or "por que" in lowered or "erros comuns" in lowered or "segurança" in lowered


def ensure_step_contract(step, lesson_order, step_order):
    step["order"] = step.get("order") or step_order
    step["media_items"] = step.get("media_items") or []
    exercise_type, exercise_params = STEP_EXERCISE_DEFAULTS.get(lesson_order, (None, {}))
    if should_skip_exercise(step.get("title", "")):
        exercise_type, exercise_params = None, {}
    step["exercise_type"] = step.get("exercise_type") if "exercise_type" in step else exercise_type
    step["exercise_params"] = step.get("exercise_params") if "exercise_params" in step else exercise_params
    step["checklist_items"] = step.get("checklist_items") or [
        "Li e pratiquei esta etapa com atenção.",
        "Consigo repetir o que foi pedido sem dor e sem pressa."
    ]


def ensure_youtube_media(lesson):
    lesson_order = lesson.get("order")
    steps = lesson.get("steps", [])
    for step_order, title, url in VIDEO_LINKS.get(lesson_order, []):
        if not (1 <= step_order <= len(steps)):
            continue
        media_items = steps[step_order - 1].setdefault("media_items", [])
        if any(item.get("path") == url for item in media_items):
            continue
        next_order = max([item.get("order", 0) for item in media_items] or [0]) + 1
        media_items.append({
            "title": title,
            "media_type": "youtube_url",
            "path": url,
            "order": next_order
        })


def ensure_repertory_block(lesson):
    block = REPERTORY_BLOCKS.get(lesson.get("order"))
    if not block or not lesson.get("steps"):
        return
    final_step = lesson["steps"][-1]
    if "Repertório sugerido em vídeo" not in final_step.get("content", ""):
        final_step["content"] = final_step.get("content", "") + "\n\n" + block

def enrich():
    file_path = 'bases/aulas_guitarra_iniciante_com_imagens_base64.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lessons = json.load(f)
        
    print(f"Lendo {len(lessons)} aulas para enriquecimento didático de elite...")
    
    # Mapeamento didático baseado no BACKLOG_AULAS_JSON.md
    didactics_map = {
        1: {
            "module": "Fundamentos para Iniciantes",
            "level": "iniciante",
            "estimated_minutes": 30,
            "objectives": [
                "Sentar-se e manter a guitarra de maneira estável com postura correta.",
                "Apoiar o antebraço sem pressionar excessivamente o instrumento.",
                "Posicionar o polegar atrás do braço da guitarra de forma firme e relaxada.",
                "Pressionar a corda próximo ao traste de metal usando a menor força necessária.",
                "Produzir cinco notas consecutivas sem trastejar ou abafar o som."
            ],
            "prerequisites": [
                "Nenhum! Esta é a aula marco zero para quem nunca encostou em uma guitarra."
            ],
            "practice_focus": "Postura corporal relaxada e treino de pressão mínima dos dedos sobre as cordas."
        },
        2: {
            "module": "Fundamentos para Iniciantes",
            "level": "iniciante",
            "estimated_minutes": 20,
            "objectives": [
                "Segurar a palheta corretamente com o polegar e indicador sem travar o pulso.",
                "Tocar cordas soltas com movimentos curtos e econômicos.",
                "Manter volume uniforme e regular tanto em golpes para baixo quanto para cima.",
                "Executar a troca de cordas com o movimento fluido de palhetada alternada."
            ],
            "prerequisites": [
                "Guitarra afinada no padrão de afinação selecionado.",
                "Ter uma palheta de espessura média (0.70mm a 1.00mm) em mãos."
            ],
            "practice_focus": "Ataque rítmico, movimento curto de palheta e relaxamento muscular da mão direita."
        },
        3: {
            "module": "Independência e Sincronização",
            "level": "iniciante",
            "estimated_minutes": 25,
            "objectives": [
                "Compreender e usar a numeração universal de dedos (1, 2, 3, 4) da mão esquerda.",
                "Executar o clássico exercício cromático 1-2-3-4 na primeira corda de forma estável.",
                "Sincronizar perfeitamente o golpe de palheta com a pressão de dedos nos trastes.",
                "Utilizar o metrônomo regulado em 50 BPM tocando exatamente uma nota por clique."
            ],
            "prerequisites": [
                "Compreender a postura básica de segurar o braço da guitarra.",
                "Saber realizar golpes básicos para baixo e para cima com a palheta."
            ],
            "practice_focus": "Sincronismo absoluto entre as mãos esquerda e direita sob pulsação rítmica do metrônomo."
        },
        4: {
            "module": "Independência e Sincronização",
            "level": "basico",
            "estimated_minutes": 30,
            "objectives": [
                "Desenvolver e treinar a força e independência dos dedos 3 (anelar) e 4 (mínimo).",
                "Executar padrões não lineares variados (1-3-2-4, 1-4-2-3, 2-4-1-3) na escala de madeira.",
                "Controlar o levantamento dos dedos para que fiquem bem próximos às cordas (economia de movimento).",
                "Manter a palhetada alternada regular mesmo sob saltos de trastes não lineares."
            ],
            "prerequisites": [
                "Conseguir executar o exercício cromático 1-2-3-4 de forma limpa a 50 BPM."
            ],
            "practice_focus": "Independência muscular fina da mão esquerda e relaxamento de dedos ociosos."
        },
        5: {
            "module": "Teoria Aplicada ao Braço",
            "level": "basico",
            "estimated_minutes": 25,
            "objectives": [
                "Compreender e fixar na mente as regras físicas de Tons e Semitons na teoria musical.",
                "Identificar o semitom natural entre as notas E-F e B-C em qualquer parte.",
                "Localizar e memorizar todas as notas naturais nas cordas 6 (Mi) e 5 (Lá).",
                "Utilizar as notas localizadas como fundamentais de power chords no rock."
            ],
            "prerequisites": [
                "Saber afinar o instrumento e conhecer o nome físico das 6 cordas soltas."
            ],
            "practice_focus": "Geometria do braço, mapeamento visual de notas de base e fixação de semitons naturais."
        },
        6: {
            "module": "Harmonia para Iniciantes",
            "level": "iniciante",
            "estimated_minutes": 30,
            "objectives": [
                "Montar as formas físicas completas dos acordes abertos Em, Am, C e G.",
                "Aprender a dedilhar e checar o som de cada corda de forma individual para evitar abafamento.",
                "Praticar a transição e troca de acordes no tempo certo sem pausar o andamento.",
                "Tocar as três primeiras progressões harmônicas clássicas e populares do curso."
            ],
            "prerequisites": [
                "Conseguir pressionar notas de forma isolada sem travar o polegar ou o pulso."
            ],
            "practice_focus": "Anatomia e arquitetura física de fôrmas de acordes abertos e pressão limpa dos dedos."
        },
        7: {
            "module": "Ritmo e Acompanhamento",
            "level": "iniciante",
            "estimated_minutes": 25,
            "objectives": [
                "Sentir, acompanhar e subdividir o pulso do metrônomo de forma instintiva e corporal.",
                "Compreender e tocar ritmos com figuras de semínimas (uma nota por tempo).",
                "Executar colcheias de forma precisa usando palhetadas alternadas constantes.",
                "Manter o movimento contínuo da mão rítmica mesmo quando não houver palhetada ativa."
            ],
            "prerequisites": [
                "Conseguir montar os fáceis acordes abertos Em e Am com som limpo."
            ],
            "practice_focus": "Subdivisão rítmica corporal estável e controle dinâmico da palhetada alternada."
        },
        8: {
            "module": "Improvisação e Solos",
            "level": "basico",
            "estimated_minutes": 30,
            "objectives": [
                "Memorizar e tocar de forma ascendente e descendente a posição 1 da escala pentatônica menor de Lá.",
                "Localizar visualmente as três ocorrências da nota tônica A dentro do desenho da escala.",
                "Compreender e criar frases musicais unindo as notas da escala a pausas e repetições.",
                "Executar a variação melódica de encerramento para criar licks lógicos e bonitos."
            ],
            "prerequisites": [
                "Dominar a palhetada alternada em velocidade confortável com o metrônomo."
            ],
            "practice_focus": "Padrões geométricos de escalas, localização de tônicas de Lá e improvisação melódica."
        },
        9: {
            "module": "Improvisação e Solos",
            "level": "intermediario",
            "estimated_minutes": 35,
            "objectives": [
                "Compreender o conceito e a aplicação prática de acordes melódicos na guitarra.",
                "Tocar e sustentar as notas da harmonia de base enquanto a melodia principal se move.",
                "Executar pequenas frases de pergunta e resposta sobre fôrmas estáticas de acordes.",
                "Executar a progressão completa unindo baixos graves, acordes médios e melodia aguda."
            ],
            "prerequisites": [
                "Dominar os acordes abertos C e Am e conseguir solar a pentatônica menor."
            ],
            "practice_focus": "Independência física dos dedos para manter notas presas enquanto dedilha licks agudos."
        }
    }
    
    for lesson in lessons:
        order = lesson.get('order')
        if order in didactics_map:
            didactics = didactics_map[order]
            # Injeta todos os campos didáticos novos de forma limpa na raiz
            lesson["module"] = didactics["module"]
            lesson["level"] = didactics["level"]
            lesson["estimated_minutes"] = didactics["estimated_minutes"]
            lesson["objectives"] = didactics["objectives"]
            lesson["prerequisites"] = didactics["prerequisites"]
            lesson["practice_focus"] = didactics["practice_focus"]
            
            # Enriquecimentos no content dos passos para guiar sem professor presencial:
            for step_order, step in enumerate(lesson.get("steps", []), 1):
                title = step.get("title", "")
                ensure_step_contract(step, order, step_order)
                
                # Se for a etapa final (Critério de conclusão ou Avaliação):
                if ("conclusão" in title.lower() or "avaliação" in title.lower()) and "Como saber se você conseguiu concluir esta aula" not in step["content"]:
                    step["content"] = step["content"] + "\n\n<h4>Como saber se você conseguiu concluir esta aula:</h4>\n<ul>\n  <li>O som de cada nota sai perfeitamente limpo, sem zunido de traste e sem abafamento involuntário de cordas vizinhas.</li>\n  <li>Você consegue repetir o exercício ou progressão por três vezes consecutivas sem errar a ordem de notas ou travar o metrônomo.</li>\n  <li>Seu ombro, punho e polegar permanecem relaxados e confortáveis de início a fim, sem dores físicas.</li>\n</ul>\n\n<h4>Rotina Prática Diária Sugerida (10 Minutos):</h4>\n<ul>\n  <li><strong>2 minutos:</strong> Aquecimento corporal e alongamento leve de dedos e punho.</li>\n  <li><strong>4 minutos:</strong> Prática focada e lenta do exercício principal proposto na aula.</li>\n  <li><strong>4 minutos:</strong> Tocar junto com a ferramenta interativa de metrônomo ou de braço limpo para fixação auditiva.</li>\n</ul>"
                
                # Se for a etapa de erros comuns:
                elif ("erros comuns" in title.lower() or "segurança" in title.lower()) and "Dica de Ouro de Prevenção" not in step["content"]:
                    step["content"] = step["content"] + "\n\n<h4>Dica de Ouro de Prevenção:</h4>\n<ul>\n  <li><strong>Se os dedos doerem:</strong> Faça pausas frequentes. É normal a ponta dos dedos ficar levemente sensível no início, mas dores nas articulações ou no punho indicam força excessiva. Pare imediatamente.</li>\n  <li><strong>Se as cordas vizinhas abafarem:</strong> curve mais os dedos da mão esquerda como se fossem martelos, tocando as cordas estritamente com a pontinha dos dedos (use as unhas bem cortadas!).</li>\n  <li><strong>Se o som trastejar:</strong> Pressione a corda bem colada ao metal do traste direito (nunca em cima e nunca longe à esquerda!).</li>\n</ul>"

            ensure_youtube_media(lesson)
            ensure_repertory_block(lesson)
                    
    # Salva o arquivo JSON enriquecido com segurança
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(lessons, f, indent=2, ensure_ascii=False)
        
    print("Enriquecimento didático de elite concluído com 100% de sucesso!")

if __name__ == '__main__':
    enrich()
