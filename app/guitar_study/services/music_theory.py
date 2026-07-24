from typing import List, Dict, Any, Tuple
import itertools

# Constantes de Teoria Musical
SHARPS_SCALE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLATS_SCALE = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Equivalência de nomes enarmônicos
ENHARMONICS = {
    "C#": "Db", "Db": "C#",
    "D#": "Eb", "Eb": "D#",
    "F#": "Gb", "Gb": "F#",
    "G#": "Ab", "Ab": "G#",
    "A#": "Bb", "Bb": "A#",
    "B#": "C", "C": "B#",
    "E#": "F", "F": "E#",
    "Cb": "B", "B": "Cb",
    "Fb": "E", "E": "Fb"
}

# Frequências básicas para oitava 4 (Lá 4 = 440 Hz)
# C4 é aproximadamente 261.63 Hz
NOTE_FREQUENCIES = {
    "C": 261.63, "C#": 277.18, "Db": 277.18, "D": 293.66, "D#": 311.13, "Eb": 311.13,
    "E": 329.63, "F": 349.23, "F#": 369.99, "Gb": 369.99, "G": 392.00, "G#": 415.30,
    "Ab": 415.30, "A": 440.00, "A#": 466.16, "Bb": 466.16, "B": 493.88
}

INTERVAL_NAMES = {
    0: "Tônica (1)",
    1: "Segunda Menor (b2)",
    2: "Segunda Maior (2)",
    3: "Terça Menor (b3)",
    4: "Terça Maior (3)",
    5: "Quarta Justa (4)",
    6: "Quinta Diminuta / Quarta Aumentada (b5/#4)",
    7: "Quinta Justa (5)",
    8: "Sexta Menor / Quinta Aumentada (b6/#5)",
    9: "Sexta Maior (6)",
    10: "Sétima Menor (b7)",
    11: "Sétima Maior (7)"
}

INTERVAL_SYMBOLS = {
    0: "1", 1: "b2", 2: "2", 3: "b3", 4: "3", 5: "4", 6: "b5",
    7: "5", 8: "b6", 9: "6", 10: "b7", 11: "7"
}

TUNINGS = {
    "standard": {"name": "Padrão (E A D G B E)", "notes": ["E", "A", "D", "G", "B", "E"]},
    "drop_d": {"name": "Drop D (D A D G B E)", "notes": ["D", "A", "D", "G", "B", "E"]},
    "eb_standard": {"name": "Eb Padrão (Eb Ab Db Gb Bb Eb)", "notes": ["Eb", "Ab", "Db", "Gb", "Bb", "Eb"]},
    "d_standard": {"name": "D Padrão (D G C F A D)", "notes": ["D", "G", "C", "F", "A", "D"]},
    "open_g": {"name": "Open G (D G D G B D)", "notes": ["D", "G", "D", "G", "B", "D"]}
}

class MusicTheoryService:
    """Serviço de lógica musical pura (SOLID & DRY)."""

    @staticmethod
    def get_chromatic_scale(preference: str = "sharps") -> List[str]:
        """Retorna a escala cromática conforme preferência por sustenidos ou bemóis."""
        return SHARPS_SCALE if preference == "sharps" else FLATS_SCALE

    @staticmethod
    def note_to_index(note: str) -> int:
        """Converte uma nota para o índice cromático correspondente (0-11)."""
        # Normaliza a nota
        note = note.strip()
        if note in SHARPS_SCALE:
            return SHARPS_SCALE.index(note)
        if note in FLATS_SCALE:
            return FLATS_SCALE.index(note)
        # Se for enarmônica exótica
        normalized = ENHARMONICS.get(note)
        if normalized:
            if normalized in SHARPS_SCALE:
                return SHARPS_SCALE.index(normalized)
            if normalized in FLATS_SCALE:
                return FLATS_SCALE.index(normalized)
        raise ValueError(f"Nota inválida: {note}")

    @classmethod
    def index_to_note(cls, index: int, preference: str = "sharps") -> str:
        """Converte um índice cromático de volta para string de nota."""
        scale = cls.get_chromatic_scale(preference)
        return scale[index % 12]

    @classmethod
    def get_note_by_fret(cls, open_string_note: str, fret: int, preference: str = "sharps") -> str:
        """Calcula a nota de uma determinada casa do braço de guitarra."""
        start_index = cls.note_to_index(open_string_note)
        target_index = (start_index + fret) % 12
        return cls.index_to_note(target_index, preference)

    @classmethod
    def get_frequency_for_fret(cls, open_string_note: str, fret: int, string_index: int = None) -> float:
        """Calcula a frequência acústica real da nota com base na corda e casa na guitarra física."""
        # Se string_index não for fornecido, tenta inferir a oitava base com base na nota da corda solta
        # Convenção padrão de oitava na afinação EADGBE (do grave para o agudo):
        # E2 (6ª corda), A2 (5ª corda), D3 (4ª corda), G3 (3ª corda), B3 (2ª corda), E4 (1ª corda)
        
        # Mapeia oitava base por índice da corda se fornecido (0 a 5, do grave para o agudo)
        # Se for Drop D, a 6ª corda solta vira D2, mas a oitava base continua 2.
        # Se for D Standard, as oitavas se mantêm equivalentes.
        base_octave = 3 # oitava média como fallback
        
        if string_index is not None:
            # Associa a oitava base correta para as 6 cordas padrão (0=aguda, 5=grave)
            index_to_octave = {
                0: 4,  # 1ª corda (E4 aguda no topo)
                1: 3,  # 2ª corda (B3)
                2: 3,  # 3ª corda (G3)
                3: 3,  # 4ª corda (D3)
                4: 2,  # 5ª corda (A2)
                5: 2,  # 6ª corda (E2 grave na base)
            }
            base_octave = index_to_octave.get(string_index, 3)
        else:
            # Fallback inteligente se o índice da corda não for informado
            note_upper = open_string_note.upper().strip()
            if note_upper == "E":
                base_octave = 2
            elif note_upper in ["A", "B"]:
                base_octave = 2
            else:
                base_octave = 3
                
        # Calcula o índice cromático da corda solta
        start_idx = cls.note_to_index(open_string_note)
        
        # Calcula a oitava real em que a nota se encontra na casa (fret)
        # Conforme a casa sobe, a oitava aumenta a cada 12 semitons
        actual_octave = base_octave + (start_idx + fret) // 12
        
        # Calcula o índice cromático da nota alvo (na casa)
        target_idx = (start_idx + fret) % 12
        
        # Fórmula física real de afinação temperada (Lá 4 = 440 Hz)
        # d é a distância em semitons em relação a A4 (nota index 9, oitava 4)
        d = (actual_octave - 4) * 12 + target_idx - 9
        
        frequency = 440.0 * (2.0 ** (d / 12.0))
        return round(frequency, 2)

    @classmethod
    def get_interval_name_and_symbol(cls, root: str, target: str) -> Tuple[str, str]:
        """Calcula o intervalo entre a tônica (root) e a nota alvo (target)."""
        root_idx = cls.note_to_index(root)
        target_idx = cls.note_to_index(target)
        semitones = (target_idx - root_idx) % 12
        return INTERVAL_NAMES[semitones], INTERVAL_SYMBOLS[semitones]

    @classmethod
    def get_scale_notes_and_intervals(cls, root: str, scale_type: str, preference: str = "sharps") -> Dict[str, Any]:
        """Calcula as notas, intervalos e fórmula de uma escala."""
        scales_formulas = {
            "major": {"name": "Maior (Jônio)", "intervals": [0, 2, 4, 5, 7, 9, 11], "formula": "1 - 2 - 3 - 4 - 5 - 6 - 7", "desc": "Luminosa e alegre. Base de toda teoria ocidental."},
            "minor": {"name": "Menor Natural (Eólio)", "intervals": [0, 2, 3, 5, 7, 8, 10], "formula": "1 - 2 - b3 - 4 - 5 - b6 - b7", "desc": "Melancólica, emotiva e sombria. Amplamente utilizada no rock e metal."},
            "minor_harmonic": {"name": "Menor Harmônica", "intervals": [0, 2, 3, 5, 7, 8, 11], "formula": "1 - 2 - b3 - 4 - 5 - b6 - 7", "desc": "Som exótico, árabe ou clássico, devido ao intervalo de 1 tom e meio entre b6 e 7."},
            "minor_melodic": {"name": "Menor Melódica", "intervals": [0, 2, 3, 5, 7, 9, 11], "formula": "1 - 2 - b3 - 4 - 5 - 6 - 7", "desc": "Som sofisticado, clássico, muito utilizada no jazz e improvisação."},
            "pentatonic_major": {"name": "Pentatônica Maior", "intervals": [0, 2, 4, 7, 9], "formula": "1 - 2 - 3 - 5 - 6", "desc": "Escala de 5 notas, som extremamente melódico, impossível de errar nota (sem semitons)."},
            "pentatonic_minor": {"name": "Pentatônica Menor", "intervals": [0, 3, 5, 7, 10], "formula": "1 - b3 - 4 - 5 - b7", "desc": "A escala mais famosa da guitarra. Essencial para rock, blues e solos em geral."},
            "blues_major": {"name": "Blues Maior", "intervals": [0, 2, 3, 4, 7, 9], "formula": "1 - 2 - b3 - 3 - 5 - 6", "desc": "Pentatônica maior adicionando a Blue Note (terça menor) para tempero country/blues."},
            "blues_minor": {"name": "Blues Menor", "intervals": [0, 3, 5, 6, 7, 10], "formula": "1 - b3 - 4 - b5 - 5 - b7", "desc": "A clássica pentatônica menor com a adição da 'Blue Note' (quinta diminuta). Som rústico e expressivo."},
            "chromatic": {"name": "Cromática", "intervals": list(range(12)), "formula": "Todos os 12 semitons", "desc": "Contém todas as 12 notas do sistema temperado ocidental. Usada para exercícios mecânicos e passagens cromáticas."}
        }

        if scale_type not in scales_formulas:
            raise ValueError(f"Tipo de escala inválido: {scale_type}")

        formula_info = scales_formulas[scale_type]
        root_idx = cls.note_to_index(root)
        
        notes = []
        intervals = []
        symbols = []
        
        for semitone in formula_info["intervals"]:
            note_idx = (root_idx + semitone) % 12
            notes.append(cls.index_to_note(note_idx, preference))
            intervals.append(INTERVAL_NAMES[semitone])
            symbols.append(INTERVAL_SYMBOLS[semitone])
            
        return {
            "key": f"{root}_{scale_type}",
            "root": root,
            "scale_type": scale_type,
            "name": f"{root} {formula_info['name']}",
            "notes": notes,
            "intervals": intervals,
            "symbols": symbols,
            "formula": formula_info["formula"],
            "description": formula_info["desc"],
            "chords_related": cls._get_related_chords_for_scale(scale_type, root, preference)
        }

    @classmethod
    def get_mode_notes_and_intervals(cls, root: str, mode_type: str, preference: str = "sharps") -> Dict[str, Any]:
        """Calcula os dados do Modo Grego selecionado."""
        modes_info = {
            "ionian": {
                "name": "Jônio", "intervals": [0, 2, 4, 5, 7, 9, 11], "formula": "1 - 2 - 3 - 4 - 5 - 6 - 7", 
                "parent": "Escala Maior (1º Grau)", "char_note": "4ª Justa (evitar repouso) ou 7ª Maior",
                "chord": "Maj7", "feeling": "Alegre, resoluto, estável", "desc": "É o próprio modo maior natural.",
                "compare_major": "Idêntico à Escala Maior."
            },
            "dorian": {
                "name": "Dórico", "intervals": [0, 2, 3, 5, 7, 9, 10], "formula": "1 - 2 - b3 - 4 - 5 - 6 - b7", 
                "parent": "Escala Maior (2º Grau)", "char_note": "6ª Maior (o F# no tom de Lá)",
                "chord": "m6 ou m7", "feeling": "Sombrio, mas com esperança, misterioso, jazzístico", "desc": "Muito usado por Santana, Pink Floyd (Breathe, OOTD) e no jazz.",
                "compare_major": "Escala menor natural com a 6ª maior elevada.", "compare_minor": "Diferencia-se da escala menor pela 6ª maior (intervalo mais brilhante)."
            },
            "phrygian": {
                "name": "Frígio", "intervals": [0, 1, 3, 5, 7, 8, 10], "formula": "1 - b2 - b3 - 4 - 5 - b6 - b7", 
                "parent": "Escala Maior (3º Grau)", "char_note": "2ª Menor (b2)",
                "chord": "m7 ou sus(b9)", "feeling": "Espanhol, flamenco, tenso, agressivo, pesado", "desc": "Super comum no heavy metal, música flamenca e trilhas sonoras de suspense.",
                "compare_major": "Escala menor natural com a 2ª menor abaixada.", "compare_minor": "Diferencia-se da escala menor pela 2ª menor (b2) adicionando tensão extrema."
            },
            "lydian": {
                "name": "Lídio", "intervals": [0, 2, 4, 6, 7, 9, 11], "formula": "1 - 2 - 3 - #4 - 5 - 6 - 7", 
                "parent": "Escala Maior (4º Grau)", "char_note": "4ª Aumentada (#4)",
                "chord": "Maj7(#11)", "feeling": "Espacial, místico, flutuante, sonhador, heróico", "desc": "Favorito de Joe Satriani (Flying in a Blue Dream) e Steve Vai. Muito usado em filmes de ficção científica.",
                "compare_major": "Escala maior com a 4ª aumentada (#4).", "compare_minor": "Não se aplica (é de caráter maior)."
            },
            "mixolydian": {
                "name": "Mixolídio", "intervals": [0, 2, 4, 5, 7, 9, 10], "formula": "1 - 2 - 3 - 4 - 5 - 6 - b7", 
                "parent": "Escala Maior (5º Grau)", "char_note": "7ª Menor (b7)",
                "chord": "7 (Dominante)", "feeling": "Bluesy, festivo, folk, rock clássico", "desc": "O som do rock clássico, AC/DC, Guns N' Roses (Sweet Child O' Mine) e MPB/Nordeste.",
                "compare_major": "Escala maior com a 7ª menor (b7).", "compare_minor": "Não se aplica (é de caráter maior)."
            },
            "aeolian": {
                "name": "Eólio", "intervals": [0, 2, 3, 5, 7, 8, 10], "formula": "1 - 2 - b3 - 4 - 5 - b6 - b7", 
                "parent": "Escala Maior (6º Grau)", "char_note": "6ª Menor (b6)",
                "chord": "m7", "feeling": "Triste, introspectivo, épico", "desc": "É a escala menor natural.",
                "compare_major": "Escala menor natural.", "compare_minor": "Idêntico à menor natural."
            },
            "locrian": {
                "name": "Lócrio", "intervals": [0, 1, 3, 5, 6, 8, 10], "formula": "1 - b2 - b3 - 4 - b5 - b6 - b7", 
                "parent": "Escala Maior (7º Grau)", "char_note": "5ª Diminuta (b5)",
                "chord": "m7(b5) - Meio Diminuto", "feeling": "Instável, sombrio, inacabado, caótico", "desc": "O modo mais tenso e menos utilizado devido à ausência de uma 5ª justa estável.",
                "compare_major": "Escala menor natural com a 2ª menor (b2) e 5ª diminuta (b5) abaixadas.", "compare_minor": "Escala menor com b2 e b5. Extremamente tenso."
            }
        }

        if mode_type not in modes_info:
            raise ValueError(f"Modo Grego inválido: {mode_type}")

        mode_data = modes_info[mode_type]
        root_idx = cls.note_to_index(root)
        
        notes = []
        intervals = []
        symbols = []
        
        for semitone in mode_data["intervals"]:
            note_idx = (root_idx + semitone) % 12
            notes.append(cls.index_to_note(note_idx, preference))
            intervals.append(INTERVAL_NAMES[semitone])
            symbols.append(INTERVAL_SYMBOLS[semitone])
            
        return {
            "key": f"{root}_{mode_type}",
            "root": root,
            "mode_type": mode_type,
            "name": f"{root} {mode_data['name']}",
            "notes": notes,
            "intervals": intervals,
            "symbols": symbols,
            "formula": mode_data["formula"],
            "parent": mode_data["parent"],
            "characteristic_note": mode_data["char_note"],
            "characteristic_chord": mode_data["chord"],
            "feeling": mode_data["feeling"],
            "description": mode_data["desc"],
            "comparison_major": mode_data["compare_major"],
            "comparison_minor": mode_data.get("compare_minor", "Não aplicável.")
        }

    @classmethod
    def get_chord_notes_and_intervals(cls, root: str, chord_type: str, preference: str = "sharps") -> Dict[str, Any]:
        """Calcula as notas e a formação de um Acorde."""
        chords_formulas = {
            "major": {"name": "Maior (Tread)", "intervals": [0, 4, 7], "formula": "1 - 3 - 5", "desc": "Consonante e feliz. Tríade básica maior."},
            "minor": {"name": "Menor (Tríade)", "intervals": [0, 3, 7], "formula": "1 - b3 - 5", "desc": "Triste e introspectivo. Tríade básica menor."},
            "augmented": {"name": "Aumentado", "intervals": [0, 4, 8], "formula": "1 - 3 - #5", "desc": "Tenso e expansivo. Quinta aumentada gera sensação de suspense."},
            "diminuted": {"name": "Diminuto", "intervals": [0, 3, 6], "formula": "1 - b3 - b5", "desc": "Altamente instável e tenso. Tríade do acorde meio diminuto."},
            "sus2": {"name": "Sus2 (Segunda Suspensa)", "intervals": [0, 2, 7], "formula": "1 - 2 - 5", "desc": "Neutro, moderno, sem terça. A segunda suspensa traz ar de frescor."},
            "sus4": {"name": "Sus4 (Quarta Suspensa)", "intervals": [0, 5, 7], "formula": "1 - 4 - 5", "desc": "Gera uma forte tensão que pede resolução na terça maior ou menor."},
            "maj7": {"name": "Maior com Sétima (Maj7)", "intervals": [0, 4, 7, 11], "formula": "1 - 3 - 5 - 7", "desc": "Aveludado, sofisticado, som típico de bossa nova e MPB."},
            "dom7": {"name": "Dominante com Sétima (7)", "intervals": [0, 4, 7, 10], "formula": "1 - 3 - 5 - b7", "desc": "O som clássico do blues. Forte tensão instável (trítono entre 3 e b7) que pede resolução."},
            "min7": {"name": "Menor com Sétima (m7)", "intervals": [0, 3, 7, 10], "formula": "1 - b3 - 5 - b7", "desc": "Suave, jazzístico e muito agradável. Reduz a melancolia da tríade menor pura."},
            "half_dim": {"name": "Meio Diminuto (m7b5)", "intervals": [0, 3, 6, 10], "formula": "1 - b3 - b5 - b7", "desc": "Típico acorde de passagem ou segundo grau menor em progressões de jazz."},
            "dim7": {"name": "Diminuto com Sétima (dim7)", "intervals": [0, 3, 6, 9], "formula": "1 - b3 - b5 - bb7", "desc": "Tensão máxima simétrica. Usado para modular para qualquer tom ou criar passagem cromática."}
        }

        if chord_type not in chords_formulas:
            raise ValueError(f"Tipo de acorde inválido: {chord_type}")

        formula_info = chords_formulas[chord_type]
        root_idx = cls.note_to_index(root)
        
        notes = []
        intervals = []
        symbols = []
        
        for semitone in formula_info["intervals"]:
            note_idx = (root_idx + semitone) % 12
            notes.append(cls.index_to_note(note_idx, preference))
            intervals.append(INTERVAL_NAMES[semitone])
            symbols.append(INTERVAL_SYMBOLS[semitone])

        # Formas do sistema CAGED para fins visuais no Frontend
        caged_shapes = cls._get_caged_shapes_info(root, chord_type)
            
        return {
            "key": f"{root}_{chord_type}",
            "root": root,
            "chord_type": chord_type,
            "name": f"{root} {formula_info['name']}",
            "notes": notes,
            "intervals": intervals,
            "symbols": symbols,
            "formula": formula_info["formula"],
            "description": formula_info["desc"],
            "caged_shapes": caged_shapes
        }

    @staticmethod
    def _get_related_chords_for_scale(scale_type: str, root: str, preference: str) -> List[str]:
        """Método auxiliar que sugere acordes do campo harmônico da escala."""
        # Se for escala maior natural, gera a tríade ou tétrade do campo harmônico
        # I Maj7, IIm7, IIIm7, IVMaj7, V7, VIm7, VIIm7b5
        if scale_type == "major":
            notes = ["I", "II", "III", "IV", "V", "VI", "VII"]
            chords = ["maj7", "min7", "min7", "maj7", "dom7", "min7", "half_dim"]
            # Ex: Cmaj7, Dm7, Em7, Fmaj7, G7, Am7, Bm7b5
            # Vamos gerar apenas uma string simplificada dos graus em texto
            return ["I Maj7", "II m7", "III m7", "IV Maj7", "V 7 (Dominante)", "VI m7", "VII m7(b5)"]
        elif scale_type == "minor":
            return ["I m7", "II m7(b5)", "III Maj7", "IV m7", "V m7", "VI Maj7", "VII 7"]
        elif scale_type == "pentatonic_minor":
            return ["I m7", "III Maj7", "IV m7", "V m7", "VII 7"]
        elif scale_type == "blues_minor":
            return ["I 7", "IV 7", "V 7"]
        return ["I (Acorde Tônica)", "IV (Acorde Subdominante)", "V (Acorde Dominante)"]

    @classmethod
    def _get_caged_shapes_info(cls, root: str, chord_type: str) -> List[Dict[str, Any]]:
        """Gera informações e posições reais absolutas no braço da guitarra para o CAGED completo (5 Formas: C, A, G, E, D)."""
        root_idx = cls.note_to_index(root)
        
        is_minor = "minor" in chord_type or "min" in chord_type or "dim" in chord_type or "half" in chord_type
        is_maj7 = "maj7" in chord_type
        is_dom7 = "dom7" in chord_type or chord_type == "7"
        is_m7 = "m7" in chord_type or "min7" in chord_type
        
        # Função auxiliar para garantir que as casas caibam no braço de 22 casas
        def trans_frets(base, rel_pattern):
            abs_list = []
            for r in reversed(rel_pattern):
                if r == -1:
                    abs_list.append(-1)
                else:
                    val = base + r
                    if val > 22:
                        val -= 12
                    if val < 0:
                        val += 12
                    abs_list.append(val)
            return abs_list

        # -------------------------------------------------------------
        # 1. FORMA DE MI (E SHAPE) - Tônica na 6ª corda (E, index 4)
        # -------------------------------------------------------------
        fret_e = (root_idx - 4) % 12
        if is_minor:
            rel_e = [0, 2, 2, 0, 0, 0]
            desc_e = "Formato de Mi Menor (Em Shape)"
        elif is_maj7:
            rel_e = [0, 2, 1, 1, 0, 0]
            desc_e = "Formato de Mi com 7ª Maior"
        elif is_dom7:
            rel_e = [0, 2, 0, 1, 0, 0]
            desc_e = "Formato de Mi com 7ª Dominante"
        elif is_m7:
            rel_e = [0, 2, 0, 0, 0, 0]
            desc_e = "Formato de Mi Menor com 7ª"
        else:
            rel_e = [0, 2, 2, 1, 0, 0]
            desc_e = "Formato de Mi Maior (E Shape)"
            
        abs_e = trans_frets(fret_e, rel_e)

        # -------------------------------------------------------------
        # 2. FORMA DE LÁ (A SHAPE) - Tônica na 5ª corda (A, index 9)
        # -------------------------------------------------------------
        fret_a = (root_idx - 9) % 12
        if is_minor:
            rel_a = [-1, 0, 2, 2, 1, 0]
            desc_a = "Formato de Lá Menor (Am Shape)"
        elif is_maj7:
            rel_a = [-1, 0, 2, 1, 2, 0]
            desc_a = "Formato de Lá com 7ª Maior"
        elif is_dom7:
            rel_a = [-1, 0, 2, 0, 2, 0]
            desc_a = "Formato de Lá com 7ª Dominante"
        elif is_m7:
            rel_a = [-1, 0, 2, 0, 1, 0]
            desc_a = "Formato de Lá Menor com 7ª"
        else:
            rel_a = [-1, 0, 2, 2, 2, 0]
            desc_a = "Formato de Lá Maior (A Shape)"
            
        abs_a = trans_frets(fret_a, rel_a)

        # -------------------------------------------------------------
        # 3. FORMA DE DÓ (C SHAPE) - Tônica na 5ª corda, recuo de 3 casas
        # -------------------------------------------------------------
        fret_c = (fret_a - 3) % 12
        if is_minor:
            rel_c = [-1, 3, 1, 0, 1, 0] # Forma de Cm (raro mas modelado)
            desc_c = "Formato de Dó Menor (Cm Shape)"
        elif is_maj7:
            rel_c = [-1, 3, 2, 0, 0, 0]
            desc_c = "Formato de Dó com 7ª Maior"
        elif is_dom7:
            rel_c = [-1, 3, 2, 3, 1, 0]
            desc_c = "Formato de Dó com 7ª Dominante"
        elif is_m7:
            rel_c = [-1, 3, 1, 3, 1, 0]
            desc_c = "Formato de Dó Menor com 7ª"
        else:
            rel_c = [-1, 3, 2, 0, 1, 0]
            desc_c = "Formato de Dó Maior (C Shape)"
            
        abs_c = trans_frets(fret_c, rel_c)

        # -------------------------------------------------------------
        # 4. FORMA DE SOL (G SHAPE) - Tônica na 6ª corda, recuo de 3 casas
        # -------------------------------------------------------------
        fret_g = (fret_e - 3) % 12
        if is_minor:
            rel_g = [3, 1, 0, 0, 0, 3]
            desc_g = "Formato de Sol Menor (Gm Shape)"
        elif is_maj7:
            rel_g = [3, 2, 0, 0, 0, 2]
            desc_g = "Formato de Sol com 7ª Maior"
        elif is_dom7:
            rel_g = [3, 2, 0, 0, 0, 1]
            desc_g = "Formato de Sol com 7ª Dominante"
        elif is_m7:
            rel_g = [3, 1, 0, 0, 0, 1]
            desc_g = "Formato de Sol Menor com 7ª"
        else:
            rel_g = [3, 2, 0, 0, 0, 3]
            desc_g = "Formato de Sol Maior (G Shape)"
            
        abs_g = trans_frets(fret_g, rel_g)

        # -------------------------------------------------------------
        # 5. FORMA DE RÉ (D SHAPE) - Tônica na 4ª corda (D, index 2), recuo de 2
        # -------------------------------------------------------------
        fret_d = (root_idx - 2) % 12
        if is_minor:
            rel_d = [-1, -1, 0, 2, 3, 1]
            desc_d = "Formato de Ré Menor (Dm Shape)"
        elif is_maj7:
            rel_d = [-1, -1, 0, 2, 2, 2]
            desc_d = "Formato de Ré com 7ª Maior"
        elif is_dom7:
            rel_d = [-1, -1, 0, 2, 1, 2]
            desc_d = "Formato de Ré com 7ª Dominante"
        elif is_m7:
            rel_d = [-1, -1, 0, 2, 1, 1]
            desc_d = "Formato de Ré Menor com 7ª"
        else:
            rel_d = [-1, -1, 0, 2, 3, 2]
            desc_d = "Formato de Ré Maior (D Shape)"
            
        abs_d = trans_frets(fret_d, rel_d)

        # Junta os 5 formatos
        shapes = [
            {
                "shape_name": desc_c,
                "base_fret": "Nut (Aberta)" if fret_c == 0 else f"Casa {fret_c}",
                "frets_relative": rel_c,
                "frets_absolute": abs_c,
                "muted_strings": [6] if abs_c[-1] == -1 else []
            },
            {
                "shape_name": desc_a,
                "base_fret": "Nut (Aberta)" if fret_a == 0 else f"Casa {fret_a}",
                "frets_relative": rel_a,
                "frets_absolute": abs_a,
                "muted_strings": [6] if abs_a[-1] == -1 else []
            },
            {
                "shape_name": desc_g,
                "base_fret": "Nut (Aberta)" if fret_g == 0 else f"Casa {fret_g}",
                "frets_relative": rel_g,
                "frets_absolute": abs_g,
                "muted_strings": []
            },
            {
                "shape_name": desc_e,
                "base_fret": "Nut (Aberta)" if fret_e == 0 else f"Casa {fret_e}",
                "frets_relative": rel_e,
                "frets_absolute": abs_e,
                "muted_strings": []
            },
            {
                "shape_name": desc_d,
                "base_fret": "Nut (Aberta)" if fret_d == 0 else f"Casa {fret_d}",
                "frets_relative": rel_d,
                "frets_absolute": abs_d,
                "muted_strings": [5, 6]
            }
        ]
        return shapes

    @classmethod
    def get_harmony_info(cls, root: str, scale_type: str, preference: str = "sharps") -> Dict[str, Any]:
        """Calcula dinamicamente o Campo Harmônico e as Preparações (V7) para os graus do tom."""
        if scale_type not in ["major", "minor"]:
            scale_type = "major"
            
        root_idx = cls.note_to_index(root)
        
        # Estrutura de intervalos das escalas em semitons
        scale_intervals = [0, 2, 4, 5, 7, 9, 11] if scale_type == "major" else [0, 2, 3, 5, 7, 8, 10]
        roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
        
        # Qualidades dos acordes (Tétrades) por grau
        if scale_type == "major":
            graus_qualities = ["maj7", "min7", "min7", "maj7", "dom7", "min7", "half_dim"]
            graus_functions = [
                {"name": "Tônica", "role": "Repouso absoluto, estabilidade e conclusão da frase musical.", "color": "success"},
                {"name": "Subdominante", "role": "Afastamento suave, tensão moderada de transição ou preparação.", "color": "primary"},
                {"name": "Tônica", "role": "Estabilidade secundária, atua como substituto de repouso.", "color": "success"},
                {"name": "Subdominante", "role": "Sensação de movimento e afastamento da tônica fundamental.", "color": "primary"},
                {"name": "Dominante", "role": "Tensão forte! Contém o trítono que pede resolução imediata na Tônica.", "color": "danger"},
                {"name": "Tônica", "role": "Estabilidade menor (tom relativo), excelente substituto de conclusão.", "color": "success"},
                {"name": "Dominante", "role": "Tensão muito forte, acorde de passagem para resolução na tônica.", "color": "danger"}
            ]
        else:
            # Menor natural
            graus_qualities = ["min7", "half_dim", "maj7", "min7", "min7", "maj7", "dom7"]
            graus_functions = [
                {"name": "Tônica", "role": "Repouso melancólico do tom menor, estabilidade principal.", "color": "success"},
                {"name": "Subdominante", "role": "Afastamento menor, tensão moderada de caráter sombrio.", "color": "primary"},
                {"name": "Tônica", "role": "Estabilidade maior (relativa), traz luminosidade temporária ao tom menor.", "color": "success"},
                {"name": "Subdominante", "role": "Movimento menor, afasta o ouvinte do centro tonal.", "color": "primary"},
                {"name": "Dominante", "role": "Tensão menor. Muitas vezes alterado para dominante maior (V7) para acentuar a resolução.", "color": "danger"},
                {"name": "Subdominante", "role": "Grande afastamento, cor lídia heróica no campo menor.", "color": "primary"},
                {"name": "Dominante", "role": "Tensão de transição, excelente para modular ou preparar o retorno do tom menor.", "color": "danger"}
            ]
            
        graus_list = []
        
        for idx, semitone in enumerate(scale_intervals):
            # Calcula a nota do grau
            note_idx = (root_idx + semitone) % 12
            grau_note = cls.index_to_note(note_idx, preference)
            
            # Qualidade do acorde da tétrade
            quality = graus_qualities[idx]
            acorde_name = f"{grau_note} {quality.replace('maj7', 'Maj7').replace('min7', 'm7').replace('dom7', '7').replace('half_dim', 'm7(b5)')}"
            
            # Calcula as notas do acorde do grau
            chord_data = cls.get_chord_notes_and_intervals(grau_note, quality, preference)
            chord_notes = chord_data["notes"]
            
            # ---------------------------------------------------------
            # CALCULA O ACORDE DE PREPARO V7 (DOMINANTE SECUNDÁRIO)
            # O acorde V7 de qualquer grau está 5 graus acima (7 semitons / 5ª Justa!)
            # ---------------------------------------------------------
            preparo_root_idx = (note_idx + 7) % 12
            preparo_root = cls.index_to_note(preparo_root_idx, preference)
            
            preparo_acorde = f"{preparo_root}7" # Dominante (qualidade dom7)
            preparo_data = cls.get_chord_notes_and_intervals(preparo_root, "dom7", preference)
            preparo_notes = preparo_data["notes"]
            
            # Explicação da cadência
            preparo_explanation = f"O acorde dominante {preparo_acorde} cria uma forte tensão de trítono entre as notas {preparo_notes[1]} (sua terça) e {preparo_notes[3]} (sua sétima) que resolvem de forma natural e repousante por semitom nas notas {chord_notes[0]} e {chord_notes[1]} do acorde {acorde_name}."
            
            graus_list.append({
                "numeral": roman_numerals[idx],
                "root": grau_note,
                "quality": quality,
                "acorde_name": acorde_name,
                "notes": chord_notes,
                "function": graus_functions[idx]["name"],
                "function_role": graus_functions[idx]["role"],
                "function_color": graus_functions[idx]["color"],
                "preparo_acorde": preparo_acorde,
                "preparo_notes": preparo_notes,
                "preparo_explanation": preparo_explanation
            })
            
        return {
            "key": f"{root}_{scale_type}_harmony",
            "root": root,
            "scale_type": scale_type,
            "scale_name": f"Campo Harmônico de {root} " + ("Maior" if scale_type == "major" else "Menor Natural"),
            "graus": graus_list
        }

    @staticmethod
    def _is_playable(frets: List[int]) -> bool:
        """Verifica se um voicing é humanamente tocável."""
        pressed = [f for f in frets if f is not None and f > 0]
        if not pressed:
            return True

        min_fret = min(pressed)
        unique_frets = sorted(list(set(pressed)))
        
        # Contagem de casas que precisam de um dedo
        strings_at_min = len([f for f in pressed if f == min_fret])
        can_barre = strings_at_min >= 2
        
        # Dedos necessários: 1 para o barre + 1 para cada outra casa única
        other_unique_frets = [f for f in unique_frets if f != min_fret]
        fingers_needed = (1 if can_barre else len(unique_frets))
        if can_barre:
            fingers_needed += len(other_unique_frets)

        # Se precisar de mais de 4 dedos, impossível
        if fingers_needed > 4:
            return False
            
        # Calcula o "span" (alcance) da mão
        span = max(pressed) - min_fret
        
        # Se não houver pestana (barre), 4 dedos e um alcance de 4 casas é impossível
        if not can_barre and fingers_needed == 4 and span >= 4:
            return False
            
        # Dedos esticados (ex: casa 1, 3, 5) são difíceis, mas possíveis
        return True

    @staticmethod
    def _get_voicing_difficulty(frets: List[int]) -> str:
        """Estima a dificuldade de um voicing."""
        pressed = [f for f in frets if f is not None and f > 0]
        if not pressed:
            return 'easy'

        min_fret = min(pressed)
        unique_frets = sorted(list(set(pressed)))
        
        strings_at_min = len([f for f in pressed if f == min_fret])
        can_barre = strings_at_min >= 2
        
        other_unique_frets = len([f for f in unique_frets if f != min_fret])
        fingers_needed = (1 + other_unique_frets) if can_barre else len(unique_frets)
        
        span = max(pressed) - min_fret
        has_open_strings = any(f == 0 for f in frets if f is not None)

        if has_open_strings and fingers_needed <= 2:
            return 'easy'
        if fingers_needed <= 2 and span <= 2:
            return 'easy'
        if fingers_needed == 4 or span >= 4 or (can_barre and other_unique_frets >= 3):
            return 'hard'
        return 'medium'

    @classmethod
    def get_all_voicings(
        cls, 
        chord_notes: List[str], 
        root_note: str, 
        tuning_notes: List[str], 
        fret_count: int = 12,
        preference: str = "sharps"
    ) -> List[Dict[str, Any]]:
        """
        Encontra todos os voicings (formas) tocáveis de um acorde na guitarra.
        Um voicing é uma combinação de notas em diferentes cordas.
        """
        chord_indices = {cls.note_to_index(n) for n in chord_notes}
        root_idx = cls.note_to_index(root_note)
        num_strings = len(tuning_notes)
        
        # 1. Mapeia todas as notas do acorde no braço inteiro
        # O formato é: [[(fret, note_idx), ...], ...] onde o índice principal é a corda
        fretboard_chord_tones = []
        for i in range(num_strings):
            string_open_note = tuning_notes[i]
            string_tones = []
            for fret in range(fret_count + 1):
                note = cls.get_note_by_fret(string_open_note, fret, preference)
                note_idx = cls.note_to_index(note)
                if note_idx in chord_indices:
                    string_tones.append({"fret": fret, "note_idx": note_idx})
            fretboard_chord_tones.append(string_tones)

        # 2. Itera sobre todos os agrupamentos de cordas possíveis (3, 4, 5, 6 cordas)
        all_voicings = []
        seen_voicings = set()

        for num_played_strings in range(3, num_strings + 1):
            for start_string_idx in range(num_strings - num_played_strings + 1):
                
                string_group_indices = range(start_string_idx, start_string_idx + num_played_strings)
                
                # Gera todas as combinações de notas para este grupo de cordas
                tone_groups = [fretboard_chord_tones[i] for i in string_group_indices]
                
                # itertools.product faz a mágica da combinação
                for combo in itertools.product(*tone_groups):
                    # combo é uma tupla de dicionários de notas, uma para cada corda
                    
                    # 3. Valida o voicing gerado
                    current_frets = [tone['fret'] for tone in combo]
                    
                    # Filtro de alcance: um voicing com mais de 4-5 casas de distância é impossível
                    pressed_frets = [f for f in current_frets if f > 0]
                    if pressed_frets and (max(pressed_frets) - min(pressed_frets) > 4):
                        continue
                        
                    # Verifica se todas as notas do acorde estão presentes no voicing
                    present_note_indices = {tone['note_idx'] for tone in combo}
                    if not chord_indices.issubset(present_note_indices):
                        continue

                    # Constrói o voicing no formato do frontend (array de 6 elementos)
                    # -1 significa corda não tocada (muted)
                    full_fret_pattern = [-1] * num_strings
                    for i, string_idx in enumerate(string_group_indices):
                        full_fret_pattern[string_idx] = current_frets[i]
                    
                    # Evita duplicatas
                    voicing_key = tuple(full_fret_pattern)
                    if voicing_key in seen_voicings:
                        continue
                    seen_voicings.add(voicing_key)

                    # Verifica a tocabilidade com base no número de dedos e alcance
                    if not cls._is_playable(full_fret_pattern):
                        continue

                    # 4. Adiciona o voicing válido à lista
                    bass_note_idx = combo[-1]['note_idx'] # A última nota da combinação é a mais grave
                    min_fret = min(pressed_frets) if pressed_frets else 0
                    
                    all_voicings.append({
                        "frets": full_fret_pattern, # Array com 6 posições
                        "played_strings": num_played_strings,
                        "min_fret": min_fret,
                        "max_fret": max(pressed_frets) if pressed_frets else 0,
                        "has_root_in_bass": bass_note_idx == root_idx,
                        "bass_note_idx": bass_note_idx,
                        "difficulty": cls._get_voicing_difficulty(full_fret_pattern)
                    })
        
        # Ordena por casa mínima, depois por número de cordas
        all_voicings.sort(key=lambda v: (v['min_fret'], -v['played_strings']))
        
        return all_voicings
