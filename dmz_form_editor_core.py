"""Core engine for reading, editing, and syncing Dragon Mine Z transformations.

Follows strict immutability (never mutates input dictionaries in-place) and
path-boundary validation against Path Traversal.
"""

from __future__ import annotations

import copy
import os
import re
import secrets
from typing import Any


class SecurityPathError(ValueError):
    """Raised when a target path escapes allowed root directories."""


_CANDIDATE_INSTANCE = r"C:\Users\Franklin\curseforge\minecraft\Instances\Dragon Mine Z Definitive Edition"
_CANDIDATE_CONFIG = r"C:\Users\Franklin\curseforge\minecraft\Instances\Dragon Mine Z Definitive Edition\config\dragonminez"
_CANDIDATE_DESKTOP_JSON = r"C:\Users\Franklin\Desktop\Dragon_Mine_Z_Transformacoes.json"

DEFAULT_INSTANCE_DIR = _CANDIDATE_INSTANCE if os.path.isdir(_CANDIDATE_INSTANCE) else ""
DEFAULT_DMZ_CONFIG_DIR = _CANDIDATE_CONFIG if os.path.isdir(_CANDIDATE_CONFIG) else ""
DEFAULT_DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
DEFAULT_DESKTOP_JSON = _CANDIDATE_DESKTOP_JSON if os.path.isfile(_CANDIDATE_DESKTOP_JSON) else ""
DEFAULT_INSTANCE_JSON = os.path.join(DEFAULT_DMZ_CONFIG_DIR, "todas_as_transformacoes.json") if DEFAULT_DMZ_CONFIG_DIR else ""

RACE_FRIENDLY_NAMES: dict[str, str] = {
    "saiyan": "Saiyajin (Saiyan)",
    "human": "Humano (Human)",
    "namekian": "Namekuseijin (Namekian)",
    "frostdemon": "Demônio do Gelo (Frost Demon)",
    "bioandroid": "Bio-Androide (Bio-Android)",
    "majin": "Majin (Buu)",
    "glind": "Glind",
    "angel": "Anjo (Angel)",
    "android": "Androide (Android)",
    "fullbringer": "Fullbringer (Bleach)",
    "half_saiyan": "Meio-Saiyajin (Half-Saiyan)",
    "kai": "Shin-jin / Kaioh (Kai)",
    "konatsian": "Konatsiano (Konatsian)",
    "makaijin": "Makaijin (Reino dos Demônios)",
    "seiunjin": "Seiunjin (Povo Nebulosa)",
    "sekhari": "Sekhari",
    "shadow_dragon": "Dragão Maligno (Shadow Dragon)",
    "soulreaper": "Shinigami (Soul Reaper / Bleach)",
    "taimujin": "Taimujin (Viajante do Tempo)",
    "tapion": "Guerreiro Espadachim Konatsiano (Tapion)",
    "tuffle": "Tsufurujin (Tuffle)",
    "wizard": "Mago / Feiticeiro (Wizard)",
    "alien": "Alienígena (Alien)",
}

RACE_FRIENDLY_NAMES_BILINGUAL: dict[str, dict[str, str]] = {
    "saiyan": {"pt": "Saiyajin (Saiyan)", "en": "Saiyan"},
    "human": {"pt": "Humano (Human)", "en": "Human"},
    "namekian": {"pt": "Namekuseijin (Namekian)", "en": "Namekian"},
    "frostdemon": {"pt": "Demônio do Gelo (Frost Demon)", "en": "Frost Demon"},
    "bioandroid": {"pt": "Bio-Androide (Bio-Android)", "en": "Bio-Android"},
    "majin": {"pt": "Majin (Buu)", "en": "Majin"},
    "glind": {"pt": "Glind", "en": "Glind"},
    "angel": {"pt": "Anjo (Angel)", "en": "Angel"},
    "android": {"pt": "Androide (Android)", "en": "Android"},
    "fullbringer": {"pt": "Fullbringer (Bleach)", "en": "Fullbringer (Bleach)"},
    "half_saiyan": {"pt": "Meio-Saiyajin (Half-Saiyan)", "en": "Half-Saiyan"},
    "kai": {"pt": "Shin-jin / Kaioh (Kai)", "en": "Core Person / Kai"},
    "konatsian": {"pt": "Konatsiano (Konatsian)", "en": "Konatsian"},
    "makaijin": {"pt": "Makaijin (Reino dos Demônios)", "en": "Makaijin (Demon Realm)"},
    "seiunjin": {"pt": "Seiunjin (Povo Nebulosa)", "en": "Seiunjin (Nebula People)"},
    "sekhari": {"pt": "Sekhari", "en": "Sekhari"},
    "shadow_dragon": {"pt": "Dragão Maligno (Shadow Dragon)", "en": "Shadow Dragon"},
    "soulreaper": {"pt": "Shinigami (Soul Reaper / Bleach)", "en": "Soul Reaper (Bleach)"},
    "taimujin": {"pt": "Taimujin (Viajante do Tempo)", "en": "Taimujin (Time Traveler)"},
    "tapion": {"pt": "Guerreiro Espadachim Konatsiano (Tapion)", "en": "Konatsian Swordsman (Tapion)"},
    "tuffle": {"pt": "Tsufurujin (Tuffle)", "en": "Tuffle"},
    "wizard": {"pt": "Mago / Feiticeiro (Wizard)", "en": "Wizard / Sorcerer"},
    "alien": {"pt": "Alienígena (Alien)", "en": "Alien"},
}


def resolve_race_friendly_name(race_id: str, lang: str = "pt") -> str:
    """Return bilingual friendly name for known races or format unknown races cleanly (50+ races support)."""
    r_low = str(race_id or "").strip().lower()
    if r_low in RACE_FRIENDLY_NAMES_BILINGUAL:
        entry = RACE_FRIENDLY_NAMES_BILINGUAL[r_low]
        return entry.get(lang, entry["pt"])
    if r_low in RACE_FRIENDLY_NAMES:
        return RACE_FRIENDLY_NAMES[r_low]
    # Clean auto-formatting for new races (e.g. 50+ custom races)
    return r_low.replace("_", " ").replace("-", " ").title()


def detect_addon_origin(file_stem: str, form_id: str = "") -> str:
    """Identify which DMZ addon or core mod is responsible for a transformation."""
    s = (str(file_stem or "") + "_" + str(form_id or "")).lower()
    if any(k in s for k in ("ultra", "corrupted", "visored")):
        return "DMZ Ultra"
    if "sparking" in s:
        return "DMZ Sparking"
    if "ragnarok" in s:
        return "DMZ Ragnarok"
    if any(k in s for k in ("kaipath", "kai_")):
        return "DMZ Kai Path"
    if any(k in s for k in ("super", "divinerose", "evildivine", "godritual")):
        return "DMZ Super"
    if "plus" in s:
        return "DMZ Plus"
    if any(k in s for k in ("custom", "created")):
        return "DMZ Custom Forms"
    if any(k in s for k in ("bleach", "soulreaper", "fullbringer", "hollow")):
        return "Unofficial DMZ Addon"
    if "realistic" in s:
        return "DMZ Realistic"
    return "Dragon Mine Z (Core)"

CUSTOM_FORM_NAMES: dict[str, str] = {
    "supersaiyan1": "Super Saiyan 1",
    "supersaiyan2": "Super Saiyan 2",
    "supersaiyan3": "Super Saiyan 3",
    "supersaiyan4": "Super Saiyan 4",
    "supersaiyan5": "Super Saiyan 5",
    "supersaiyan6": "Super Saiyan 6",
    "supersaiyan7": "Super Saiyan 7",
    "supersaiyan8": "Super Saiyan 8",
    "supersaiyan9": "Super Saiyan 9",
    "supersaiyan10": "Super Saiyan 10",
    "supersaiyan": "Super Saiyan",
    "supersaiyanmastered": "Super Saiyan Mastered",
    "super_saiyan_god": "Super Saiyan God",
    "super_saiyan_blue": "Super Saiyan Blue",
    "super_saiyan_rose": "Super Saiyan Rosé",
    "super_saiyan_blue_evolved": "Super Saiyan Blue Evolution",
    "super_saiyan_rose_evolved": "Super Saiyan Rosé Evolved",
    "super_saiyan_rage": "Super Saiyan Rage",
    "supersaiyan4fp": "Super Saiyan 4 Full Power",
    "supersaiyan4lb": "Super Saiyan 4 Limit Breaker",
    "falsesupersaiyan": "False Super Saiyan",
    "goldenoozaru": "Golden Oozaru",
    "oozaru": "Oozaru (Macaco Gigante)",
    "beast": "Beast",
    "ikari": "Ikari (Wrathful)",
    "ssjhybrid": "Super Saiyan Hybrid",
    "ssjfullpower": "Super Saiyan Full Power",
    "ssjlegendary3": "Super Saiyan Lendário 3",
    "ssjlegendary4": "Super Saiyan Lendário 4",
    "ultra": "Ultra Form 1",
    "ultrassj2": "Ultra Super Saiyan 2",
    "ultrassj3": "Ultra Super Saiyan 3",
    "ultrassj4": "Ultra Super Saiyan 4",
    "sign": "Sign (Presságio)",
    "mastered": "Mastered (Completo / Aperfeiçoado)",
    "true": "True (Verdadeiro)",
    "buffed": "Buffed (Muscular)",
    "fullpower": "Full Power (Poder Total)",
    "overdrive": "Overdrive",
    "solaris": "Solaris",
    "shiyoken": "Shiyoken (Quatro Braços)",
    "shin_shiyoken": "Shin Shiyoken",
    "chou_shiyoken": "Chou Shiyoken",
    "giant": "Gigante (Giant Namekian)",
    "supernamekian": "Super Namekuseijin",
    "orangenamek": "Orange Namekian",
    "orange_giant": "Orange Giant Namekian",
    "cellmax": "Cell Max",
    "golden": "Golden Form",
    "black": "Black Form",
    "rage_shenron": "Rage Shenron (5 Estrelas)",
    "nuova_shenron": "Nuova Shenron (4 Estrelas)",
    "syn_shenron": "Syn Shenron (1 Estrela)",
    "omega_shenron": "Omega Shenron (7 Esferas)",
    "baby_parasite": "Baby Parasita (Fase Inicial)",
    "super_baby_1": "Super Baby 1",
    "super_baby_2": "Super Baby 2 (Vingança Tsufurujin)",
    "golden_oozaru_baby": "Golden Oozaru Baby",
    "arcane_awakening": "Despertar Arcano (Magia Antiga)",
    "babidi_sorcery": "Feitiçaria Suprema de Babidi",
    "planet_eater_moro": "Moro Devorador de Planetas (Magia Vital)",
    "angel_moro": "Moro Merus (Magia Angelical)",
    "ocarina_guardian": "Guardião da Ocarina Sagrada",
    "phantom_majin_slayer": "Espadachim Caçador de Hirudegarn",
    "eternal_brave_sword": "Espada Brava Eterna (Lenda de Konats)",
    "resolve": "Determinação de Konats (Resolve)",
    "heroic_spirit": "Espírito Heroico (Heroic Spirit)",
    "brave_heart": "Coração Valente (Brave Heart)",
    "sword_master": "Mestre da Espada Brava",
    "hirudegarn": "Receptáculo de Hirudegarn",
    "partial": "Fullbring Parcial",
    "fullbring": "Fullbring Maduro (Clad-Type)",
    "complete": "Fullbring Completo (Armadura do Executor)",
    "bringer_light": "Luz do Bringer",
    "transcendent_fullbring": "Fullbring Transcendente",
    "overclock": "Sobrecarga de Circuitos (Overclock)",
    "neo_mutant": "Mutante Biológico Neo",
    "arcane_initiate": "Iniciado Arcano",
    "dark_seal": "Selo Arcano Negro",
    "demonic_sorcery": "Alta Feitiçaria de Daima",
    "haze_shenron": "Haze Shenron (2 Estrelas - Poluição)",
    "eis_shenron": "Eis Shenron (3 Estrelas - Gelo)",
    "oceanus_shenron": "Oceanus Shenron (6 Estrelas - Vento/Marés)",
    "disciple_kai": "Discípulo Shin-jin",
    "kaioh_awakening": "Despertar de Kaioh",
    "supreme_kai": "Kaiohshin Sagrado",
    "mystic_unlocked": "Potencial Sagrado Desbloqueado",
    "grand_supreme_kai": "Grande Kaiohshin",
}

MASTER_FRIENDLY_NAMES: dict[str, str] = {
    "kingkai": "Senhor Kaioh (King Kai)",
    "oldkai": "Kaiohshin Antigo (Old Kai)",
    "beerus": "Lord Beerus",
    "whis": "Whis",
    "merus": "Merus",
    "piccolo": "Piccolo",
    "frieza": "Freeza",
    "cell": "Cell",
    "goku": "Goku",
    "vegeta": "Vegeta",
    "gohan": "Gohan",
    "trunks": "Trunks",
    "krillin": "Kuririn",
    "roshi": "Mestre Kame (Roshi)",
    "tien": "Tenshinhan",
    "sparking_tien": "Tenshinhan (Sparking)",
    "yamcha": "Yamcha",
    "guru": "Grande Patriarca (Guru)",
    "karin": "Mestre Karin",
    "popo": "Sr. Popo",
    "dende": "Dende",
    "gero": "Dr. Gero",
    "babidi": "Babidi",
    "dabura": "Dabura",
    "towa": "Towa",
    "buu": "Majin Buu",
    "sparking_buu": "Majin Buu (Sparking)",
    "enma": "Rei Enma",
    "grandkai": "Grande Kaioh (Grand Kai)",
    "master_visored": "Mestre Visored",
    "dmzultra_visored_master": "Mestre Visored (Ultra)",
    "master_soul_society": "Mestre Soul Society",
    "dmzultra_soul_society_master": "Mestre Soul Society (Ultra)",
    "master_fullbring": "Mestre Fullbring",
    "sword_master": "Mestre da Espada Brava (Tapion)",
    "traitor_captain": "Aizen (Capitão Traidor)",
}

DEFAULT_TREE_MASTERS: dict[str, str] = {
    "corruptedforms": "babidi",
    "majinmark": "babidi",
    "majinforms": "babidi",
    "evilsaiyan": "babidi",
    "godforms": "whis",
    "godritual": "whis",
    "godx": "whis",
    "ssjgod": "whis",
    "ultrainstinct": "whis",
    "ultraego": "beerus",
    "hakaishin": "beerus",
    "kaioken": "kingkai",
    "spiritbomb": "kingkai",
    "kaioh": "kingkai",
    "mystic": "oldkai",
    "ultimate": "oldkai",
    "beast": "gohan",
    "konatsiano": "sword_master",
    "sword": "sword_master",
    "brave_sword": "sword_master",
    "shinigami": "master_soul_society",
    "soul_reaper": "master_soul_society",
    "fullbring": "master_fullbring",
    "fullbringer": "master_fullbring",
    "visored": "master_visored",
    "demon": "dabura",
    "makaijin": "dabura",
    "bio_android": "gero",
    "android": "gero",
    "gamma": "gero",
    "sparking": "roshi",
    "turtle": "roshi",
    "shadow_saga": "oldkai",
}


def infer_master_for_form(tree: str, form_id: str, form_type: str = "") -> tuple[str, str]:
    """Infer the training master from form keywords or skill tree when not explicitly bound."""
    tokens = f"{tree} {form_id} {form_type}".lower().replace("_", " ").replace("-", " ")
    for key, m_id in DEFAULT_TREE_MASTERS.items():
        if key in tokens:
            m_nome = MASTER_FRIENDLY_NAMES.get(m_id, m_id.replace("_", " ").title())
            return m_id, m_nome
    return "", ""

PRICELESS_LABEL = "Priceless / Desejo de Shenron / Quest"


def default_allowed_roots() -> list[str]:
    roots = [
        DEFAULT_INSTANCE_DIR,
        DEFAULT_DESKTOP_DIR,
        os.path.abspath(os.getcwd()),
        os.path.expanduser("~"),
    ]
    return [r for r in roots if r]


def validate_allowed_path(
    target_path: str, allowed_roots: list[str] | None = None
) -> str:
    """Resolve real path and ensure it resides within whitelisted roots."""
    if not target_path or not isinstance(target_path, str):
        raise SecurityPathError("Caminho inválido ou vazio.")
    real_target = os.path.realpath(target_path)
    roots = allowed_roots if allowed_roots is not None else default_allowed_roots()
    for root in roots:
        real_root = os.path.realpath(root)
        try:
            if os.path.commonpath([real_target, real_root]) == real_root:
                return real_target
        except ValueError:
            continue
    raise SecurityPathError(
        f"Acesso bloqueado fora dos diretórios permitidos: {target_path}"
    )


def format_bp_string(multipliers: dict[str, float]) -> str:
    str_m = round(float(multipliers.get("forca_str", 1.0)), 3)
    pwr_m = round(float(multipliers.get("poder_ki_pwr", 1.0)), 3)
    def_m = round(float(multipliers.get("defesa_def", 1.0)), 3)
    skp_m = round(float(multipliers.get("golpe_skp", 1.0)), 3)
    if str_m == pwr_m == def_m == skp_m:
        return f"{str_m}x"
    return f"{str_m}x (STR) / {pwr_m}x (PWR)"


def compute_power_tier(form_dict: dict[str, Any]) -> dict[str, Any]:
    """Computes canonical power tier (1 to 10) and hierarchy progression score.
    
    Tiers are determined by original un-modified combat multiplier sum (STR + PWR + DEF + SKP):
      Tier 1: <= 10.0 (Formas Iniciais / Inatas: False SSJ, SSJ1, Oozaru, Kaioken x2)
      Tier 2: 10.0 < sum <= 20.0 (Super Guerreiro I: Grade 2, Grade 3, SSJ2, Kaioken x10)
      Tier 3: 20.0 < sum <= 30.0 (Super Guerreiro II: SSJ3, Majin Mark, Kaioken x20)
      Tier 4: 30.0 < sum <= 45.0 (Super Guerreiro III / Místico: Ultimate, Golden Oozaru, SSJ4)
      Tier 5: 45.0 < sum <= 60.0 (Divino I: Super Saiyajin God, Golden Frieza base)
      Tier 6: 60.0 < sum <= 75.0 (Divino II: Super Saiyajin Blue, SSJ Rosé)
      Tier 7: 75.0 < sum <= 95.0 (Divino III: SSJ Blue Kaioken, Rosé 2, Golden Frieza Max)
      Tier 8: 95.0 < sum <= 120.0 (Evolução Divina / Hakaishin: SSJ Blue Evolution, Rosé 3)
      Tier 9: 120.0 < sum <= 160.0 (Instinto & Ego / Beast: Ultra Instinct Sign, Ultra Ego, Beast)
      Tier 10: > 160.0 (Transcendental / Endgame: Mastered Ultra Instinct, True Ultra Instinct, 200x+)
    """
    mults = form_dict.get("multiplicadores_detalhados", {})
    if "poder_base_original" in form_dict and isinstance(form_dict["poder_base_original"], (int, float)):
        base_sum = float(form_dict["poder_base_original"])
    elif mults:
        base_sum = (
            float(mults.get("forca_str", 1.0))
            + float(mults.get("poder_ki_pwr", 1.0))
            + float(mults.get("defesa_def", 1.0))
            + float(mults.get("golpe_skp", 1.0))
        )
    elif "multiplicador_numerico_base" in form_dict:
        base_sum = float(form_dict["multiplicador_numerico_base"]) * 4.0
    else:
        base_sum = 4.0

    base_sum = max(1.0, round(base_sum, 3))

    if base_sum <= 10.0:
        tier = 1
        tier_label = "Tier 1: Inicial / Inato"
        tier_min, tier_max = 1.0, 10.0
    elif base_sum <= 20.0:
        tier = 2
        tier_label = "Tier 2: Super Guerreiro I"
        tier_min, tier_max = 10.0, 20.0
    elif base_sum <= 30.0:
        tier = 3
        tier_label = "Tier 3: Super Guerreiro II"
        tier_min, tier_max = 20.0, 30.0
    elif base_sum <= 45.0:
        tier = 4
        tier_label = "Tier 4: Super Guerreiro III / Místico"
        tier_min, tier_max = 30.0, 45.0
    elif base_sum <= 60.0:
        tier = 5
        tier_label = "Tier 5: Divino I (God)"
        tier_min, tier_max = 45.0, 60.0
    elif base_sum <= 75.0:
        tier = 6
        tier_label = "Tier 6: Divino II (Blue)"
        tier_min, tier_max = 60.0, 75.0
    elif base_sum <= 95.0:
        tier = 7
        tier_label = "Tier 7: Divino III (Blue Kaioken/Rosé 2)"
        tier_min, tier_max = 75.0, 95.0
    elif base_sum <= 120.0:
        tier = 8
        tier_label = "Tier 8: Evolução Divina (Evolved/Rosé 3)"
        tier_min, tier_max = 95.0, 120.0
    elif base_sum <= 160.0:
        tier = 9
        tier_label = "Tier 9: Instinto & Ego / Beast"
        tier_min, tier_max = 120.0, 160.0
    else:
        tier = 10
        tier_label = "Tier 10: Transcendental / Endgame"
        tier_min, tier_max = 160.0, 250.0

    denom = max(0.1, tier_max - tier_min)
    intra = min(1.0, max(0.0, (base_sum - tier_min) / denom))

    slot = int(form_dict.get("nivel_habilidade", 1) or 1)
    reqs = form_dict.get("requisitos", {})
    has_prior = bool(reqs.get("forma_previa"))
    prior_bonus = 0.06 if has_prior else 0.0
    slot_bonus = min(0.15, max(0.0, (slot - 1) * 0.03))

    rank_score = round(tier + (intra * 0.75) + slot_bonus + prior_bonus, 3)

    return {
        "tier": tier,
        "tier_label": tier_label,
        "base_sum": base_sum,
        "rank_score": rank_score,
    }


def format_tp_display(tp_numeric: int) -> int | str:
    if tp_numeric < 0:
        return PRICELESS_LABEL
    return int(tp_numeric)


def parse_tp_numeric(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return -1 if int(value) < 0 else int(value)
    if isinstance(value, str):
        stripped = value.strip()
        low = stripped.lower()
        if not stripped or "priceless" in low or "desejo" in low:
            return -1
        if "inato" in low or "gratuito" in low:
            return 0
        try:
            num = int(float(stripped))
            return -1 if num < 0 else num
        except ValueError:
            return -1
    return -1


def _build_form_entry(
    *,
    form_id: str,
    display_name: str,
    group_key: str,
    form_type: str,
    level: int,
    tp_num: int,
    buy_from_master: bool,
    fprops: dict[str, Any],
    is_universal: bool = False,
    mestre: str = "",
    mestre_nome: str = "",
) -> dict[str, Any]:
    mults = {
        "forca_str": round(float(fprops.get("strMultiplier", 1.0)), 3),
        "poder_ki_pwr": round(float(fprops.get("pwrMultiplier", 1.0)), 3),
        "defesa_def": round(float(fprops.get("defMultiplier", 1.0)), 3),
        "golpe_skp": round(float(fprops.get("skpMultiplier", 1.0)), 3),
        "estamina_stm": round(float(fprops.get("stmMultiplier", 1.0)), 3),
        "vitalidade_vit": round(float(fprops.get("vitMultiplier", 1.0)), 3),
        "energia_ene": round(float(fprops.get("eneMultiplier", 1.0)), 3),
        "velocidade_spd": round(float(fprops.get("speedMultiplier", 1.0)), 3),
        "velocidade_ataque": round(float(fprops.get("attackSpeed", 1.0)), 3),
    }
    res = {
        "id": form_id,
        "nome": display_name,
        "arvore" if not is_universal else "grupo": group_key,
        "tipo_habilidade": form_type,
        "nivel_habilidade": int(level),
        "custo_tp": format_tp_display(tp_num),
        "custo_tp_numerico": tp_num,
        "comprar_no_mestre": buy_from_master,
        "mestre": str(mestre or ""),
        "mestre_nome": str(mestre_nome or ""),
        "multiplicador_bp": format_bp_string(mults),
        "multiplicador_numerico_base": mults["forca_str"],
        "multiplicadores_detalhados": mults,
        "drenos": {
            "energia_ki": round(float(fprops.get("energyDrain", 0.0)), 4),
            "estamina": round(float(fprops.get("staminaDrain", 0.0)), 4),
            "vida": round(float(fprops.get("healthDrain", 0.0)), 4),
            "mult_estamina_golpe": round(
                float(fprops.get("staminaDrainMultiplier", 1.0)), 3
            ),
            "acumulavel": bool(fprops.get("formStackable", True)),
            "mult_dreno_stack": round(
                float(fprops.get("stackDrainMultiplier", 2.0)), 3
            ),
        },
        "maestria": {
            "maestria_maxima": round(float(fprops.get("maxMastery", 100.0)), 2),
            "ganho_golpe_dado": round(
                float(fprops.get("masteryPerHitDealt", 0.025)), 4
            ),
            "ganho_dano_recebido": round(
                float(fprops.get("masteryPerHitReceived", 0.025)), 4
            ),
            "ganho_passivo_5s": round(
                float(fprops.get("passiveMasteryEveryFiveSeconds", 0.01)), 4
            ),
            "mult_custo_maestria_max": round(
                float(fprops.get("maxCostMultiplier", 0.75)), 3
            ),
            "mult_status_maestria_max": round(
                float(fprops.get("maxStatsMultiplier", 1.0)), 3
            ),
            "maestria_transf_instantanea": round(
                float(fprops.get("instantTransformOnMastery", 40.0)), 2
            ),
        },
        "requisitos": {
            "nivel_dmz_minimo": int(fprops.get("requiredDMZLevel", 1)),
            "nivel_requisito": int(fprops.get("levelRequisite", 0)),
            "saga": fprops.get("sagaRequisite") or None,
            "forma_previa": fprops.get("formRequisite") or None,
            "incompativel_com": list(fprops.get("incompatibleWith", [])),
        },
        "visual": {
            "cor_aura": str(fprops.get("auraColor") or ""),
            "tipo_aura": str(fprops.get("auraType") or "default"),
            "cor_cabelo": str(fprops.get("hairColor") or ""),
            "cor_cabelo_secundaria": str(fprops.get("hairColor2") or ""),
            "tipo_cabelo": str(fprops.get("hairType") or "Base"),
            "tipo_modelo": str(fprops.get("modelType") or "Base"),
            "brilho_emissivo": bool(fprops.get("emissiveGlow", False)),
            "cor_olho_1": str(fprops.get("eye1Color") or ""),
            "cor_olho_2": str(fprops.get("eye2Color") or ""),
            "cor_pele": str(fprops.get("bodyColor1") or fprops.get("skinColor") or ""),
            "escala": float(fprops.get("scale") or fprops.get("size") or 1.0),
            "raios": {
                "ativo": bool(fprops.get("sparksEnabled", fprops.get("lightning", False))),
                "cor": str(fprops.get("sparksColor") or "#00FFFF"),
                "intensidade": float(fprops.get("sparksIntensity", 1.0)),
            },
            "manto": {
                "ativo": bool(fprops.get("cloakEnabled", False)),
                "estilo": str(fprops.get("cloakStyle") or "fervilhante"),
                "cor_interna": str(fprops.get("cloakColorInner") or "#FF4500"),
                "cor_borda": str(fprops.get("cloakColorBorder") or "#FFD700"),
                "opacidade": float(fprops.get("cloakOpacity", 0.7)),
                "velocidade_pulsacao": float(fprops.get("cloakPulseSpeed", 1.0)),
            },
        },
        "addon_origem": detect_addon_origin(group_key, form_id),
        "_raw_payload": copy.deepcopy(fprops),
    }
    pinfo = compute_power_tier(res)
    res["poder_base_original"] = pinfo["base_sum"]
    res["categoria_poder"] = pinfo["tier"]
    res["tier_label"] = pinfo["tier_label"]
    res["tier_rank_score"] = pinfo["rank_score"]
    return res


def _normalize_loaded_entry(
    entry: dict[str, Any], is_universal: bool
) -> dict[str, Any]:
    """Ensure backwards compatibility when opening older exported JSONs."""
    cloned = copy.deepcopy(entry)
    tp_num = (
        int(cloned["custo_tp_numerico"])
        if "custo_tp_numerico" in cloned
        else parse_tp_numeric(cloned.get("custo_tp", -1))
    )
    cloned["custo_tp_numerico"] = tp_num
    cloned["custo_tp"] = format_tp_display(tp_num)
    cloned.setdefault("comprar_no_mestre", False)
    cloned.setdefault("mestre", "")
    cloned.setdefault("mestre_nome", "")
    if cloned.get("comprar_no_mestre") and not cloned.get("mestre_nome"):
        inf_id, inf_nome = infer_master_for_form(
            cloned.get("arvore" if not is_universal else "grupo", ""),
            cloned.get("id", ""),
            cloned.get("tipo_habilidade", ""),
        )
        if inf_id:
            cloned["mestre"] = inf_id
            cloned["mestre_nome"] = inf_nome
    cloned.setdefault(
        "tipo_habilidade",
        cloned.get("arvore" if not is_universal else "grupo", ""),
    )
    cloned.setdefault(
        "addon_origem",
        detect_addon_origin(
            cloned.get("arvore" if not is_universal else "grupo", ""),
            cloned.get("id", ""),
        ),
    )

    mults = dict(cloned.get("multiplicadores_detalhados", {}))
    base_val = float(
        mults.get("forca_str", cloned.get("multiplicador_numerico_base", 1.0))
    )
    for k, default in (
        ("forca_str", base_val),
        ("poder_ki_pwr", base_val),
        ("defesa_def", base_val),
        ("golpe_skp", base_val),
        ("estamina_stm", 1.0),
        ("vitalidade_vit", 1.0),
        ("energia_ene", 1.0),
        ("velocidade_spd", 1.0),
        ("velocidade_ataque", 1.0),
    ):
        mults.setdefault(k, default)
    cloned["multiplicadores_detalhados"] = mults
    cloned["multiplicador_numerico_base"] = mults["forca_str"]
    cloned["multiplicador_bp"] = format_bp_string(mults)

    drenos = dict(cloned.get("drenos", {}))
    for k, default in (
        ("energia_ki", 0.0),
        ("estamina", 0.0),
        ("vida", 0.0),
        ("mult_estamina_golpe", 1.0),
        ("acumulavel", True),
        ("mult_dreno_stack", 2.0),
    ):
        drenos.setdefault(k, default)
    cloned["drenos"] = drenos

    maestria = dict(cloned.get("maestria", {}))
    for k, default in (
        ("maestria_maxima", 100.0),
        ("ganho_golpe_dado", 0.025),
        ("ganho_dano_recebido", 0.025),
        ("ganho_passivo_5s", 0.01),
        ("mult_custo_maestria_max", 0.75),
        ("mult_status_maestria_max", 1.0),
        ("maestria_transf_instantanea", 40.0),
    ):
        maestria.setdefault(k, default)
    cloned["maestria"] = maestria

    reqs = dict(cloned.get("requisitos", {}))
    for k, default in (
        ("nivel_dmz_minimo", 1),
        ("nivel_requisito", 0),
        ("saga", None),
        ("forma_previa", None),
        ("incompativel_com", []),
    ):
        reqs.setdefault(k, default)
    cloned["requisitos"] = reqs

    vis = dict(cloned.get("visual", {}))
    for k in ("cor_aura", "cor_cabelo", "cor_cabelo_secundaria", "cor_olho_1", "cor_olho_2", "cor_pele"):
        raw_c = str(vis.get(k) or "").strip()
        if raw_c and not raw_c.startswith("#") and len(raw_c) in (3, 6, 8):
            raw_c = "#" + raw_c
        vis[k] = raw_c
    vis.setdefault("tipo_aura", "default")
    vis.setdefault("tipo_cabelo", "Base")
    vis.setdefault("tipo_modelo", "Base")
    vis.setdefault("brilho_emissivo", False)
    vis.setdefault("escala", 1.0)

    raios = dict(vis.get("raios", {})) if isinstance(vis.get("raios"), dict) else {}
    raios.setdefault("ativo", False)
    raios.setdefault("cor", "#00FFFF")
    raios.setdefault("intensidade", 1.0)
    vis["raios"] = raios

    manto = dict(vis.get("manto", {})) if isinstance(vis.get("manto"), dict) else {}
    manto.setdefault("ativo", False)
    manto.setdefault("estilo", "fervilhante")
    manto.setdefault("cor_interna", "#FF4500")
    manto.setdefault("cor_borda", "#FFD700")
    manto.setdefault("opacidade", 0.7)
    manto.setdefault("velocidade_pulsacao", 1.0)
    vis["manto"] = manto

    cloned["visual"] = vis
    cloned.setdefault("_raw_payload", {})
    pinfo = compute_power_tier(cloned)
    cloned.setdefault("poder_base_original", pinfo["base_sum"])
    cloned["categoria_poder"] = pinfo["tier"]
    cloned["tier_label"] = pinfo["tier_label"]
    cloned["tier_rank_score"] = pinfo["rank_score"]
    return cloned


def _merge_single_form_changes(
    entry: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    updated = copy.deepcopy(entry)

    if "nome" in payload and isinstance(payload["nome"], str):
        updated["nome"] = payload["nome"].strip() or updated["nome"]
    if "nivel_habilidade" in payload:
        updated["nivel_habilidade"] = max(0, int(payload["nivel_habilidade"]))
    if "custo_tp_numerico" in payload or "custo_tp" in payload:
        raw_tp = payload.get("custo_tp_numerico", payload.get("custo_tp"))
        tp_num = parse_tp_numeric(raw_tp)
        updated["custo_tp_numerico"] = tp_num
        updated["custo_tp"] = format_tp_display(tp_num)
    if "comprar_no_mestre" in payload:
        updated["comprar_no_mestre"] = bool(payload["comprar_no_mestre"])
    if "mestre" in payload:
        updated["mestre"] = str(payload["mestre"]).strip()
    if "mestre_nome" in payload:
        updated["mestre_nome"] = str(payload["mestre_nome"]).strip()
    if updated.get("comprar_no_mestre") and not updated.get("mestre_nome"):
        inf_id, inf_nome = infer_master_for_form(
            updated.get("arvore", updated.get("grupo", "")),
            updated.get("id", ""),
            updated.get("tipo_habilidade", ""),
        )
        if inf_id:
            updated["mestre"] = inf_id
            updated["mestre_nome"] = inf_nome
    if "addon_origem" in payload:
        updated["addon_origem"] = str(payload["addon_origem"]).strip()

    if "visual" in payload and isinstance(payload["visual"], dict):
        vis = dict(updated.get("visual", {}))
        for k, v in payload["visual"].items():
            if v is not None:
                if isinstance(v, dict):
                    sub = dict(vis.get(k, {})) if isinstance(vis.get(k), dict) else {}
                    sub.update(v)
                    vis[k] = sub
                elif isinstance(v, (int, float, bool)):
                    vis[k] = v
                else:
                    s_val = str(v).strip()
                    if s_val and not s_val.startswith("#") and len(s_val) in (3, 6, 8) and ("cor" in k or "color" in k.lower()):
                        s_val = "#" + s_val
                    vis[k] = s_val
        updated["visual"] = vis

    if "multiplicadores_detalhados" in payload:
        mults = dict(updated["multiplicadores_detalhados"])
        for k, v in payload["multiplicadores_detalhados"].items():
            if k in mults and v is not None:
                mults[k] = round(float(v), 4)
        updated["multiplicadores_detalhados"] = mults
        updated["multiplicador_numerico_base"] = mults["forca_str"]
        updated["multiplicador_bp"] = format_bp_string(mults)

    if "drenos" in payload:
        drenos = dict(updated["drenos"])
        for k, v in payload["drenos"].items():
            if k == "acumulavel":
                drenos[k] = bool(v)
            elif k in drenos and v is not None:
                drenos[k] = round(float(v), 4)
        updated["drenos"] = drenos

    if "maestria" in payload:
        maestria = dict(updated["maestria"])
        for k, v in payload["maestria"].items():
            if k in maestria and v is not None:
                maestria[k] = round(float(v), 4)
        updated["maestria"] = maestria

    if "requisitos" in payload:
        reqs = dict(updated["requisitos"])
        r_in = payload["requisitos"]
        if "nivel_dmz_minimo" in r_in:
            reqs["nivel_dmz_minimo"] = max(0, int(r_in["nivel_dmz_minimo"]))
        if "nivel_requisito" in r_in:
            reqs["nivel_requisito"] = max(0, int(r_in["nivel_requisito"]))
        if "saga" in r_in:
            s_val = str(r_in["saga"] or "").strip()
            reqs["saga"] = s_val if s_val else None
        if "forma_previa" in r_in:
            f_val = str(r_in["forma_previa"] or "").strip()
            reqs["forma_previa"] = f_val if f_val else None
        if "incompativel_com" in r_in:
            inc = r_in["incompativel_com"]
            if isinstance(inc, str):
                reqs["incompativel_com"] = [
                    x.strip() for x in inc.split(",") if x.strip()
                ]
            elif isinstance(inc, list):
                reqs["incompativel_com"] = [
                    str(x).strip() for x in inc if str(x).strip()
                ]
        updated["requisitos"] = reqs

    pinfo = compute_power_tier(updated)
    updated.setdefault("poder_base_original", pinfo["base_sum"])
    updated["categoria_poder"] = pinfo["tier"]
    updated["tier_label"] = pinfo["tier_label"]
    updated["tier_rank_score"] = pinfo["rank_score"]
    return updated


def apply_form_update(
    catalog: dict[str, Any], update_payload: dict[str, Any]
) -> dict[str, Any]:
    """Return a NEW catalog dictionary with the requested form update applied."""
    new_cat = copy.deepcopy(catalog)
    escopo = update_payload.get("escopo", "raca")
    target_id = str(update_payload.get("id", ""))

    if escopo == "universal":
        grupo = str(update_payload.get("grupo", ""))
        grp_obj = new_cat.get("formas_universais_e_stack", {}).get(grupo)
        if not grp_obj:
            raise KeyError(f"Grupo universal não encontrado: {grupo}")
        new_forms = []
        matched_entry: dict[str, Any] | None = None
        for form in grp_obj["formas"]:
            if form["id"] == target_id:
                matched_entry = _merge_single_form_changes(form, update_payload)
                new_forms.append(matched_entry)
            else:
                new_forms.append(form)
        if matched_entry is None:
            raise KeyError(f"Forma universal não encontrada: {target_id}")
        lvl = matched_entry["nivel_habilidade"]
        if lvl > 0 and (
            "custo_tp_numerico" in update_payload or "custo_tp" in update_payload
        ):
            for f in new_forms:
                if f["id"] != target_id and f["nivel_habilidade"] == lvl:
                    f["custo_tp_numerico"] = matched_entry["custo_tp_numerico"]
                    f["custo_tp"] = matched_entry["custo_tp"]
        grp_obj["formas"] = new_forms
        return new_cat

    race_key = str(update_payload.get("raca", ""))
    tree_key = str(update_payload.get("arvore", ""))
    race_obj = new_cat.get("racas", {}).get(race_key)
    if not race_obj:
        raise KeyError(f"Raça não encontrada: {race_key}")
    tree_obj = race_obj.get("arvores_de_transformacao", {}).get(tree_key)
    if not tree_obj:
        raise KeyError(f"Árvore não encontrada: {tree_key}")

    matched_race_form: dict[str, Any] | None = None
    updated_tree_forms = []
    for form in tree_obj["formas"]:
        if form["id"] == target_id:
            matched_race_form = _merge_single_form_changes(form, update_payload)
            updated_tree_forms.append(matched_race_form)
        else:
            updated_tree_forms.append(form)

    if matched_race_form is None:
        raise KeyError(f"Forma não encontrada: {target_id}")
    tree_obj["formas"] = updated_tree_forms

    skill_type = matched_race_form["tipo_habilidade"]
    skill_lvl = matched_race_form["nivel_habilidade"]
    tp_changed = "custo_tp_numerico" in update_payload or "custo_tp" in update_payload
    master_changed = "comprar_no_mestre" in update_payload

    if tp_changed or master_changed:
        for t_obj in race_obj["arvores_de_transformacao"].values():
            for f in t_obj["formas"]:
                if f["tipo_habilidade"] == skill_type:
                    if master_changed:
                        f["comprar_no_mestre"] = matched_race_form["comprar_no_mestre"]
                    if (
                        tp_changed
                        and skill_lvl > 0
                        and f["nivel_habilidade"] == skill_lvl
                    ):
                        f["custo_tp_numerico"] = matched_race_form["custo_tp_numerico"]
                        f["custo_tp"] = matched_race_form["custo_tp"]

    return new_cat


def _scale_single_entry(
    entry: dict[str, Any], field_group: str, factor: float
) -> dict[str, Any]:
    return _apply_rule_to_entry(
        entry,
        "escala_simples",
        {"campo": field_group, "fator": factor},
    )


def _apply_rule_to_entry(
    entry: dict[str, Any],
    regra: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    cloned = copy.deepcopy(entry)
    mults = dict(cloned.get("multiplicadores_detalhados", {}))
    base_val = float(
        mults.get("forca_str", cloned.get("multiplicador_numerico_base", 1.0))
    )
    for k in (
        "forca_str",
        "poder_ki_pwr",
        "defesa_def",
        "golpe_skp",
        "estamina_stm",
        "vitalidade_vit",
        "energia_ene",
        "velocidade_spd",
        "velocidade_ataque",
    ):
        mults.setdefault(
            k,
            base_val
            if k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp")
            else 1.0,
        )

    drenos = dict(cloned.get("drenos", {}))
    drenos.setdefault("energia_ki", 0.0)
    drenos.setdefault("estamina", 0.0)
    drenos.setdefault("vida", 0.0)

    if regra in ("escala_simples", "scale"):
        campo = str(payload.get("campo", "tp"))
        fator = float(payload.get("fator", 1.0))
        if fator <= 0:
            raise ValueError("O fator de multiplicação deve ser maior que zero.")
        if campo == "tp":
            tp_num = cloned["custo_tp_numerico"]
            if tp_num > 0:
                scaled = max(1, int(round(tp_num * fator)))
                cloned["custo_tp_numerico"] = scaled
                cloned["custo_tp"] = format_tp_display(scaled)
        elif campo == "bp":
            for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp"):
                mults[k] = round(float(mults[k]) * fator, 3)
        elif campo == "ofensivo":
            for k in ("forca_str", "poder_ki_pwr", "golpe_skp"):
                mults[k] = round(float(mults[k]) * fator, 3)
        elif campo == "defensivo":
            for k in ("defesa_def", "vitalidade_vit"):
                mults[k] = round(float(mults[k]) * fator, 3)
        elif campo == "dreno_ki":
            drenos["energia_ki"] = round(
                float(drenos.get("energia_ki", 0.0)) * fator, 4
            )
        elif campo == "dreno_estamina":
            drenos["estamina"] = round(
                float(drenos.get("estamina", 0.0)) * fator, 4
            )
        elif campo == "velocidade":
            for k in ("velocidade_spd", "velocidade_ataque"):
                mults[k] = round(float(mults[k]) * fator, 3)

    elif regra == "risco_recompensa":
        fator_bp = float(payload.get("fator_bp", 1.30))
        fator_dreno_ki = float(payload.get("fator_dreno_ki", 1.50))
        fator_dreno_stm = float(payload.get("fator_dreno_estamina", 1.50))
        for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp"):
            mults[k] = round(float(mults[k]) * fator_bp, 3)
        cur_ki = float(drenos.get("energia_ki", 0.0))
        if cur_ki > 0:
            drenos["energia_ki"] = round(cur_ki * fator_dreno_ki, 4)
        elif fator_dreno_ki > 1.0 and mults["forca_str"] >= 2.0:
            drenos["energia_ki"] = 0.08
        cur_stm = float(drenos.get("estamina", 0.0))
        if cur_stm > 0:
            drenos["estamina"] = round(cur_stm * fator_dreno_stm, 4)

    elif regra in ("teto_hierarquico", "hierarchical_tier"):
        teto_maximo = float(payload.get("teto_maximo", payload.get("limite_maximo", 50.0)))
        piso_minimo = float(payload.get("piso_minimo", 4.0))
        curva = str(payload.get("curva", "suave"))

        if teto_maximo <= piso_minimo:
            teto_maximo = piso_minimo + 1.0

        pinfo = compute_power_tier(cloned)
        rank = pinfo["rank_score"]

        # Rank ranges from ~1.0 to ~10.5. Normalize progress x in [0.0, 1.0]
        x = min(1.0, max(0.0, (rank - 1.0) / 9.0))

        if curva == "suave":
            factor_curve = (x ** 1.15)
        elif curva == "agressiva":
            factor_curve = (x ** 1.35)
        else:  # "linear"
            factor_curve = x

        target_sum = round(piso_minimo + (teto_maximo - piso_minimo) * factor_curve, 3)

        current_sum = sum(
            float(mults[k])
            for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp")
        )
        if current_sum > 0:
            scale_ratio = target_sum / current_sum
            for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp"):
                mults[k] = round(max(0.1, float(mults[k]) * scale_ratio), 3)

    elif regra == "teto_maximo":
        tipo_teto = str(payload.get("tipo_teto", "soma"))
        limite = float(payload.get("limite_maximo", 50.0))
        if tipo_teto == "hierarquico":
            pinfo = compute_power_tier(cloned)
            rank = pinfo["rank_score"]
            x = min(1.0, max(0.0, (rank - 1.0) / 9.0))
            curva = str(payload.get("curva", "suave"))
            factor_curve = (x ** 1.15) if curva == "suave" else ((x ** 1.35) if curva == "agressiva" else x)
            piso_minimo = float(payload.get("piso_minimo", 4.0))
            if limite <= piso_minimo:
                limite = piso_minimo + 1.0
            target_sum = round(piso_minimo + (limite - piso_minimo) * factor_curve, 3)
            current_sum = sum(
                float(mults[k])
                for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp")
            )
            if current_sum > 0:
                scale_ratio = target_sum / current_sum
                for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp"):
                    mults[k] = round(max(0.1, float(mults[k]) * scale_ratio), 3)
        elif tipo_teto == "soma":
            soma_atual = sum(
                float(mults[k])
                for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp")
            )
            if soma_atual > limite and soma_atual > 0:
                ratio = limite / soma_atual
                for k in (
                    "forca_str",
                    "poder_ki_pwr",
                    "defesa_def",
                    "golpe_skp",
                ):
                    mults[k] = round(float(mults[k]) * ratio, 3)
        elif tipo_teto == "individual":
            for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp"):
                if float(mults[k]) > limite:
                    mults[k] = round(limite, 3)

    elif regra == "recalcular_tp":
        ratio = float(payload.get("ratio_tp_por_bp", 25000.0))
        preservar = bool(payload.get("preservar_especiais", True))
        tp_num = cloned["custo_tp_numerico"]
        if not (preservar and tp_num <= 0):
            soma_bp = sum(
                float(mults[k])
                for k in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp")
            )
            calc_tp = max(1000, int(round((soma_bp / 4.0) * ratio)))
            cloned["custo_tp_numerico"] = calc_tp
            cloned["custo_tp"] = format_tp_display(calc_tp)

    elif regra == "normalizar_drenos":
        teto = float(payload.get("teto_dreno_ki", 0.60))
        piso = float(payload.get("piso_dreno_ki", 0.05))
        cur_ki = float(drenos.get("energia_ki", 0.0))
        if cur_ki > teto:
            drenos["energia_ki"] = teto
        elif cur_ki < piso and mults["forca_str"] >= 3.0:
            drenos["energia_ki"] = piso

    elif regra == "especializacao":
        papel = str(payload.get("papel", "berserker"))
        if papel == "berserker":
            mults["forca_str"] = round(mults["forca_str"] * 1.4, 3)
            mults["poder_ki_pwr"] = round(mults["poder_ki_pwr"] * 1.2, 3)
            mults["defesa_def"] = round(mults["defesa_def"] * 0.8, 3)
            mults["velocidade_spd"] = round(mults["velocidade_spd"] * 0.9, 3)
        elif papel == "ki_blaster":
            mults["poder_ki_pwr"] = round(mults["poder_ki_pwr"] * 1.5, 3)
            mults["golpe_skp"] = round(mults["golpe_skp"] * 1.25, 3)
            mults["forca_str"] = round(mults["forca_str"] * 0.8, 3)
            drenos["energia_ki"] = round(
                max(0.1, float(drenos.get("energia_ki", 0.0)) * 1.2), 4
            )
        elif papel == "tanque":
            mults["defesa_def"] = round(mults["defesa_def"] * 1.6, 3)
            mults["vitalidade_vit"] = round(mults["vitalidade_vit"] * 1.4, 3)
            mults["velocidade_spd"] = round(mults["velocidade_spd"] * 0.75, 3)
            mults["forca_str"] = round(mults["forca_str"] * 0.85, 3)
        elif papel == "speedster":
            mults["velocidade_spd"] = round(mults["velocidade_spd"] * 1.5, 3)
            mults["velocidade_ataque"] = round(mults["velocidade_ataque"] * 1.4, 3)
            mults["defesa_def"] = round(mults["defesa_def"] * 0.8, 3)

    cloned["multiplicadores_detalhados"] = mults
    cloned["multiplicador_numerico_base"] = mults["forca_str"]
    cloned["multiplicador_bp"] = format_bp_string(mults)
    cloned["drenos"] = drenos
    pinfo = compute_power_tier(cloned)
    cloned.setdefault("poder_base_original", pinfo["base_sum"])
    cloned["categoria_poder"] = pinfo["tier"]
    cloned["tier_label"] = pinfo["tier_label"]
    cloned["tier_rank_score"] = pinfo["rank_score"]
    return cloned


def apply_batch_balance(
    catalog: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Immutably apply advanced batch balancing rules across a scope and optional selected form IDs."""
    if not isinstance(payload, dict):
        raise ValueError("Payload inválido para balanceamento em lote.")

    new_cat = copy.deepcopy(catalog)
    regra = str(payload.get("regra", "escala_simples"))
    target_scope = payload.get("escopo_alvo", payload.get("escopo", {"tipo": "tudo"}))
    scope_type = target_scope.get("tipo", "tudo")
    target_race = target_scope.get("raca")
    target_tree = target_scope.get("arvore")
    target_group = target_scope.get("grupo")

    selected_ids = payload.get("formas_selecionadas")
    selected_set = set(selected_ids) if selected_ids is not None else None

    updated_tp_map: dict[tuple[str, int], int] = {}

    if scope_type in ("tudo", "raca", "arvore"):
        for r_key, r_obj in new_cat.get("racas", {}).items():
            if scope_type in ("raca", "arvore") and r_key != target_race:
                continue
            for t_key, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
                if scope_type == "arvore" and t_key != target_tree:
                    continue
                new_forms = []
                for f in t_obj.get("formas", []):
                    if selected_set is not None and f.get("id") not in selected_set:
                        new_forms.append(f)
                    else:
                        scaled = _apply_rule_to_entry(f, regra, payload)
                        new_forms.append(scaled)
                        lvl = scaled.get("nivel_habilidade", 0)
                        st = scaled.get("tipo_habilidade", "")
                        if lvl > 0 and st:
                            updated_tp_map[(st, lvl)] = scaled["custo_tp_numerico"]
                t_obj["formas"] = new_forms

    if scope_type in ("tudo", "universal"):
        for g_key, g_obj in new_cat.get("formas_universais_e_stack", {}).items():
            if scope_type == "universal" and target_group and g_key != target_group:
                continue
            new_forms = []
            for f in g_obj.get("formas", []):
                if selected_set is not None and f.get("id") not in selected_set:
                    new_forms.append(f)
                else:
                    scaled = _apply_rule_to_entry(f, regra, payload)
                    new_forms.append(scaled)
                    lvl = scaled.get("nivel_habilidade", 0)
                    st = scaled.get("tipo_habilidade", "")
                    if lvl > 0 and st:
                        updated_tp_map[(st, lvl)] = scaled["custo_tp_numerico"]
            g_obj["formas"] = new_forms

    if updated_tp_map:
        for r_obj in new_cat.get("racas", {}).values():
            for t_obj in r_obj.get("arvores_de_transformacao", {}).values():
                for f in t_obj.get("formas", []):
                    pair = (
                        f.get("tipo_habilidade", ""),
                        f.get("nivel_habilidade", 0),
                    )
                    if pair in updated_tp_map:
                        tp_val = updated_tp_map[pair]
                        f["custo_tp_numerico"] = tp_val
                        f["custo_tp"] = format_tp_display(tp_val)
        for g_obj in new_cat.get("formas_universais_e_stack", {}).values():
            for f in g_obj.get("formas", []):
                pair = (
                    f.get("tipo_habilidade", ""),
                    f.get("nivel_habilidade", 0),
                )
                if pair in updated_tp_map:
                    tp_val = updated_tp_map[pair]
                    f["custo_tp_numerico"] = tp_val
                    f["custo_tp"] = format_tp_display(tp_val)

    return new_cat


def apply_batch_scale(
    catalog: dict[str, Any],
    target_scope: dict[str, Any],
    field_group: str,
    factor: float,
) -> dict[str, Any]:
    """Immutably scale TP or BP multipliers across a scope (tudo, raca, arvore, universal)."""
    return apply_batch_balance(
        catalog,
        {
            "regra": "escala_simples",
            "campo": field_group,
            "fator": factor,
            "escopo_alvo": target_scope,
        },
    )


def _extract_fprops_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    fprops: dict[str, Any] = {}
    mults = payload.get("multiplicadores_detalhados", {})
    if mults:
        fprops["strMultiplier"] = mults.get("forca_str", 1.0)
        fprops["pwrMultiplier"] = mults.get("poder_ki_pwr", 1.0)
        fprops["defMultiplier"] = mults.get("defesa_def", 1.0)
        fprops["skpMultiplier"] = mults.get("golpe_skp", 1.0)
        fprops["stmMultiplier"] = mults.get("estamina_stm", 1.0)
        fprops["vitMultiplier"] = mults.get("vitalidade_vit", 1.0)
        fprops["eneMultiplier"] = mults.get("energia_ene", 1.0)
        fprops["speedMultiplier"] = mults.get("velocidade_spd", 1.0)
        fprops["attackSpeed"] = mults.get("velocidade_ataque", 1.0)
    elif "multiplicador_numerico_base" in payload:
        b = float(payload["multiplicador_numerico_base"])
        fprops["strMultiplier"] = b
        fprops["pwrMultiplier"] = b
        fprops["defMultiplier"] = b
        fprops["skpMultiplier"] = b

    drenos = payload.get("drenos", {})
    if drenos:
        fprops["energyDrain"] = drenos.get("energia_ki", 0.0)
        fprops["staminaDrain"] = drenos.get("estamina", 0.0)
        fprops["healthDrain"] = drenos.get("vida", 0.0)
        fprops["staminaDrainMultiplier"] = drenos.get("mult_estamina_golpe", 1.0)
        fprops["formStackable"] = drenos.get("acumulavel", True)
        fprops["stackDrainMultiplier"] = drenos.get("mult_dreno_stack", 2.0)

    maestria = payload.get("maestria", {})
    if maestria:
        fprops["maxMastery"] = maestria.get("maestria_maxima", 100.0)
        fprops["masteryPerHitDealt"] = maestria.get("ganho_golpe_dado", 0.025)
        fprops["masteryPerHitReceived"] = maestria.get("ganho_dano_recebido", 0.025)
        fprops["passiveMasteryEveryFiveSeconds"] = maestria.get("ganho_passivo_5s", 0.01)
        fprops["maxCostMultiplier"] = maestria.get("mult_custo_maestria_max", 0.75)
        fprops["maxStatsMultiplier"] = maestria.get("mult_status_maestria_max", 1.0)
        fprops["instantTransformOnMastery"] = maestria.get("maestria_transf_instantanea", 40.0)

    reqs = payload.get("requisitos", {})
    if reqs:
        fprops["requiredDMZLevel"] = reqs.get("nivel_dmz_minimo", 1)
        fprops["levelRequisite"] = reqs.get("nivel_requisito", 0)
        fprops["sagaRequisite"] = reqs.get("saga")
        fprops["formRequisite"] = reqs.get("forma_previa")
        fprops["incompatibleWith"] = reqs.get("incompativel_com", [])

    vis = payload.get("visual", {})
    if vis:
        fprops["auraColor"] = vis.get("cor_aura", "")
        fprops["auraType"] = vis.get("tipo_aura", "default")
        fprops["hairColor"] = vis.get("cor_cabelo", "")
        fprops["hairColor2"] = vis.get("cor_cabelo_secundaria", "")
        fprops["hairType"] = vis.get("tipo_cabelo", "Base")
        fprops["modelType"] = vis.get("tipo_modelo", "Base")
        fprops["emissiveGlow"] = bool(vis.get("brilho_emissivo", False))
        fprops["eye1Color"] = vis.get("cor_olho_1", "")
        fprops["eye2Color"] = vis.get("cor_olho_2", "")
        fprops["bodyColor1"] = vis.get("cor_pele", "")
        fprops["scale"] = float(vis.get("escala", 1.0))
        raios = vis.get("raios", {}) if isinstance(vis.get("raios"), dict) else {}
        fprops["sparksEnabled"] = bool(raios.get("ativo", False))
        fprops["sparksColor"] = str(raios.get("cor", "#00FFFF"))
        fprops["sparksIntensity"] = float(raios.get("intensidade", 1.0))
        manto = vis.get("manto", {}) if isinstance(vis.get("manto"), dict) else {}
        fprops["cloakEnabled"] = bool(manto.get("ativo", False))
        fprops["cloakStyle"] = str(manto.get("estilo", "fervilhante"))
        fprops["cloakColorInner"] = str(manto.get("cor_interna", "#FF4500"))
        fprops["cloakColorBorder"] = str(manto.get("cor_borda", "#FFD700"))
        fprops["cloakOpacity"] = float(manto.get("opacidade", 0.7))
        fprops["cloakPulseSpeed"] = float(manto.get("velocidade_pulsacao", 1.0))

    fprops["unlockOnSkillLevel"] = payload.get("nivel_habilidade", 1)
    return fprops


def add_form(catalog: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Immutably insert a new transformation into the catalog with full validation."""
    new_cat = copy.deepcopy(catalog)
    escopo = payload.get("escopo", "raca")
    target_id = str(payload.get("id", "")).strip().lower()
    if not target_id:
        raise ValueError("ID da transformação não pode ser vazio.")

    clean_id = re.sub(r"[^a-z0-9_]", "_", target_id)
    display_name = (
        str(payload.get("nome", "")).strip()
        or clean_id.replace("_", " ").title()
    )

    if escopo == "universal":
        grupo = str(payload.get("grupo", "geral")).strip().lower() or "geral"
        univ_map = new_cat.setdefault("formas_universais_e_stack", {})
        if grupo not in univ_map:
            univ_map[grupo] = {
                "arquivo": f"{grupo}.json",
                "tipo": grupo,
                "formas": [],
            }
        grp_obj = univ_map[grupo]
        if any(f["id"] == clean_id for f in grp_obj["formas"]):
            raise ValueError(
                f"Forma com ID '{clean_id}' já existe no grupo universal '{grupo}'."
            )

        new_entry = _build_form_entry(
            form_id=clean_id,
            display_name=display_name,
            group_key=grupo,
            form_type=str(payload.get("tipo_habilidade", grupo)),
            level=int(payload.get("nivel_habilidade", 1)),
            tp_num=parse_tp_numeric(
                payload.get("custo_tp_numerico", payload.get("custo_tp", 0))
            ),
            buy_from_master=bool(payload.get("comprar_no_mestre", False)),
            fprops=_extract_fprops_from_payload(payload),
            is_universal=True,
            mestre=str(payload.get("mestre", "")),
            mestre_nome=str(payload.get("mestre_nome", "")),
        )
        new_entry["addon_origem"] = payload.get("addon_origem") or detect_addon_origin(
            grupo, clean_id
        )
        grp_obj["formas"].append(new_entry)
        new_cat["total_transformacoes"] = (
            new_cat.get("total_transformacoes", 0) + 1
        )
        return new_cat

    race_key = str(payload.get("raca", "")).strip().lower()
    if not race_key:
        raise ValueError("Raça alvo deve ser especificada.")
    tree_key = str(payload.get("arvore", "")).strip().lower()
    if not tree_key:
        tree_key = "custom_forms"

    racas_map = new_cat.setdefault("racas", {})
    if race_key not in racas_map:
        racas_map[race_key] = {
            "id_raca": race_key,
            "nome_exibicao": resolve_race_friendly_name(race_key),
            "total_formas": 0,
            "total_arvores": 0,
            "arvores_de_transformacao": {},
        }
        new_cat["total_racas"] = len(racas_map)

    race_obj = racas_map[race_key]
    trees = race_obj.setdefault("arvores_de_transformacao", {})
    if tree_key not in trees:
        trees[tree_key] = {
            "arquivo": f"{tree_key}.json",
            "tipo_habilidade": tree_key,
            "total_formas": 0,
            "formas": [],
        }
        race_obj["total_arvores"] = len(trees)

    tree_obj = trees[tree_key]
    if any(f["id"] == clean_id for f in tree_obj["formas"]):
        raise ValueError(
            f"Forma com ID '{clean_id}' já existe na árvore '{tree_key}' da raça '{race_key}'."
        )

    new_entry = _build_form_entry(
        form_id=clean_id,
        display_name=display_name,
        group_key=tree_key,
        form_type=str(
            payload.get(
                "tipo_habilidade", tree_obj.get("tipo_habilidade", tree_key)
            )
        ),
        level=int(payload.get("nivel_habilidade", 1)),
        tp_num=parse_tp_numeric(
            payload.get("custo_tp_numerico", payload.get("custo_tp", 0))
        ),
        buy_from_master=bool(payload.get("comprar_no_mestre", False)),
        fprops=_extract_fprops_from_payload(payload),
        is_universal=False,
        mestre=str(payload.get("mestre", "")),
        mestre_nome=str(payload.get("mestre_nome", "")),
    )
    new_entry["addon_origem"] = payload.get("addon_origem") or detect_addon_origin(
        tree_key, clean_id
    )
    tree_obj["formas"].append(new_entry)
    tree_obj["total_formas"] = len(tree_obj["formas"])
    race_obj["total_formas"] = sum(len(t["formas"]) for t in trees.values())
    new_cat["total_transformacoes"] = (
        new_cat.get("total_transformacoes", 0) + 1
    )
    return new_cat


def delete_form(catalog: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Immutably remove a transformation from the catalog."""
    new_cat = copy.deepcopy(catalog)
    escopo = payload.get("escopo", "raca")
    target_id = str(payload.get("id", "")).strip().lower()
    if not target_id:
        raise ValueError("ID da transformação a ser removida não pode ser vazio.")

    if escopo == "universal":
        grupo = str(payload.get("grupo", "")).strip().lower()
        univ_map = new_cat.get("formas_universais_e_stack", {})
        if grupo not in univ_map:
            raise KeyError(f"Grupo universal '{grupo}' não encontrado.")
        grp_obj = univ_map[grupo]
        orig_len = len(grp_obj["formas"])
        grp_obj["formas"] = [f for f in grp_obj["formas"] if f["id"] != target_id]
        if len(grp_obj["formas"]) == orig_len:
            raise KeyError(
                f"Forma universal '{target_id}' não encontrada no grupo '{grupo}'."
            )
        new_cat["total_transformacoes"] = max(
            0, new_cat.get("total_transformacoes", 0) - 1
        )
        return new_cat

    race_key = str(payload.get("raca", "")).strip().lower()
    tree_key = str(payload.get("arvore", "")).strip().lower()
    race_obj = new_cat.get("racas", {}).get(race_key)
    if not race_obj:
        raise KeyError(f"Raça '{race_key}' não encontrada.")
    tree_obj = race_obj.get("arvores_de_transformacao", {}).get(tree_key)
    if not tree_obj:
        raise KeyError(f"Árvore '{tree_key}' não encontrada na raça '{race_key}'.")

    orig_len = len(tree_obj["formas"])
    tree_obj["formas"] = [f for f in tree_obj["formas"] if f["id"] != target_id]
    if len(tree_obj["formas"]) == orig_len:
        raise KeyError(f"Forma '{target_id}' não encontrada na árvore '{tree_key}'.")

    tree_obj["total_formas"] = len(tree_obj["formas"])
    race_obj["total_formas"] = sum(
        len(t["formas"]) for t in race_obj["arvores_de_transformacao"].values()
    )
    new_cat["total_transformacoes"] = max(
        0, new_cat.get("total_transformacoes", 0) - 1
    )
    return new_cat


def compute_stats_and_bars(
    race_stats: dict[str, Any] | None,
    attributes: dict[str, Any] | None,
    multipliers: dict[str, Any] | None,
) -> dict[str, Any]:
    """Calculate real maximums for HP, KI, and STM as well as scaled combat attributes
    using the race's stats.json scaling factors and the form's multipliers.
    """
    stats_cfg = race_stats or {}
    race_class = stats_cfg.get("classes", {}).get("race", {})
    base_stats = race_class.get("baseStats", {})
    scaling = race_class.get("statScaling", {})

    # Default character attributes if not provided: 50.0 baseline or baseStats * 10
    attrs = dict(attributes or {})
    str_val = float(attrs.get("STR", attrs.get("forca", base_stats.get("STR", 5) * 10)))
    def_val = float(attrs.get("DEF", attrs.get("RES", attrs.get("defesa", base_stats.get("RES", 2) * 10))))
    spd_val = float(attrs.get("SPD", attrs.get("velocidade", 50.0)))
    pwr_val = float(attrs.get("PWR", attrs.get("poder", base_stats.get("PWR", 1) * 10)))
    skp_val = float(attrs.get("SKP", attrs.get("golpe", base_stats.get("SKP", 3) * 10)))
    ene_val = float(attrs.get("ENE", attrs.get("energia", base_stats.get("ENE", 1) * 10)))
    vit_val = float(attrs.get("VIT", attrs.get("vitalidade", base_stats.get("VIT", 1) * 10)))

    mults = dict(multipliers or {})
    m_str = float(mults.get("forca_str", 1.0))
    m_pwr = float(mults.get("poder_ki_pwr", 1.0))
    m_def = float(mults.get("defesa_def", 1.0))
    m_skp = float(mults.get("golpe_skp", 1.0))
    m_spd = float(mults.get("velocidade_spd", 1.0))
    m_vit = float(mults.get("vitalidade_vit", 1.0))
    m_ene = float(mults.get("energia_ene", 1.0))
    m_stm = float(mults.get("estamina_stm", 1.0))

    vit_scaling = float(scaling.get("VIT_scaling", 0.95))
    ene_scaling = float(scaling.get("ENE_scaling", 1.0))
    stm_scaling = float(scaling.get("STM_scaling", 1.1))

    # Real combat attributes multiplied by form
    final_str = round(str_val * m_str, 1)
    final_def = round(def_val * m_def, 1)
    final_spd = round(spd_val * m_spd, 1)
    final_pwr = round(pwr_val * m_pwr, 1)
    final_skp = round(skp_val * m_skp, 1)
    final_ene = round(ene_val * m_ene, 1)
    final_vit = round(vit_val * m_vit, 1)
    final_stm = round(def_val * m_stm, 1)

    # Real maximums calibrated to Dragon Mine Z RPG scale
    max_hp = int(round(100.0 + (vit_val * vit_scaling * m_vit * 30.0)))
    max_ki = int(round(100.0 + (ene_val * ene_scaling * m_ene * 50.0)))
    max_stm = int(round(100.0 + (def_val * stm_scaling * m_stm * 20.0)))

    return {
        "atributos_base": {
            "STR": str_val,
            "DEF": def_val,
            "SPD": spd_val,
            "PWR": pwr_val,
            "SKP": skp_val,
            "ENE": ene_val,
            "VIT": vit_val,
        },
        "atributos_finais": {
            "STR": final_str,
            "DEF": final_def,
            "SPD": final_spd,
            "PWR": final_pwr,
            "SKP": final_skp,
            "ENE": final_ene,
            "VIT": final_vit,
            "STM": final_stm,
        },
        "max_hp": max_hp,
        "max_ki": max_ki,
        "max_stm": max_stm,
    }


def compute_drain_rates_and_autonomy(
    max_hp: int | float,
    max_ki: int | float,
    max_stm: int | float,
    drains: dict[str, Any] | None,
) -> dict[str, Any]:
    """Calculate exact per-second drain numbers and autonomy duration in seconds."""
    dr = drains or {}
    ki_d = float(dr.get("energia_ki", 0.0))
    stm_d = float(dr.get("estamina", 0.0))
    hp_d = float(dr.get("vida", 0.0))

    # In DMZ, drains <= 1.0 are % of max per second, > 1.0 are flat points/sec
    ki_pts_sec = round((ki_d * max_ki) if ki_d <= 1.0 else ki_d, 2)
    stm_pts_sec = round((stm_d * max_stm) if stm_d <= 1.0 else stm_d, 2)
    hp_pts_sec = round((hp_d * max_hp) if hp_d <= 1.0 else hp_d, 2)

    ki_autonomy = round(max_ki / ki_pts_sec, 1) if ki_pts_sec > 0 else None
    stm_autonomy = round(max_stm / stm_pts_sec, 1) if stm_pts_sec > 0 else None
    hp_autonomy = round(max_hp / hp_pts_sec, 1) if hp_pts_sec > 0 else None

    valid_autonomies = [a for a in (ki_autonomy, stm_autonomy) if a is not None]
    overall_autonomy = min(valid_autonomies) if valid_autonomies else None

    return {
        "ki_dreno_segundo": ki_pts_sec,
        "estamina_dreno_segundo": stm_pts_sec,
        "vida_dreno_segundo": hp_pts_sec,
        "autonomia_ki_segundos": ki_autonomy,
        "autonomia_estamina_segundos": stm_autonomy,
        "autonomia_vida_segundos": hp_autonomy,
        "autonomia_geral_segundos": overall_autonomy,
    }


def reorder_forms(
    catalog: dict[str, Any],
    race_id: str,
    tree_id: str,
    new_order: list[str],
    auto_update_skill_level: bool = True,
) -> dict[str, Any]:
    """Reorder forms inside a tree, optionally updating unlockOnSkillLevel (1, 2, 3...)."""
    new_cat = copy.deepcopy(catalog)
    is_univ = race_id in ("universal", "formas_universais_e_stack")
    if is_univ:
        univ_map = new_cat.setdefault("formas_universais_e_stack", {})
        if tree_id not in univ_map:
            raise KeyError(f"Grupo universal '{tree_id}' não encontrado.")
        forms_list = univ_map[tree_id].get("formas", [])
    else:
        race_obj = new_cat.setdefault("racas", {}).get(race_id)
        if not race_obj:
            raise KeyError(f"Raça '{race_id}' não encontrada.")
        tree_obj = race_obj.setdefault("arvores_de_transformacao", {}).get(tree_id)
        if not tree_obj:
            raise KeyError(f"Árvore '{tree_id}' não encontrada na raça '{race_id}'.")
        forms_list = tree_obj.get("formas", [])

    forms_by_id = {f["id"]: f for f in forms_list}
    reordered = []
    seen = set()
    for fid in new_order:
        if fid in forms_by_id and fid not in seen:
            reordered.append(forms_by_id[fid])
            seen.add(fid)
    for f in forms_list:
        if f["id"] not in seen:
            reordered.append(f)

    if auto_update_skill_level:
        for idx, f in enumerate(reordered, start=1):
            f["nivel_habilidade"] = idx
            if "_raw_payload" in f and isinstance(f["_raw_payload"], dict):
                f["_raw_payload"]["unlockOnSkillLevel"] = idx

    if is_univ:
        univ_map[tree_id]["formas"] = reordered
    else:
        tree_obj["formas"] = reordered
    return new_cat


def duplicate_form(
    catalog: dict[str, Any],
    race_id: str,
    tree_id: str,
    form_id: str,
    new_id: str = "",
    new_name: str = "",
) -> dict[str, Any]:
    """Duplicate an existing transformation stage directly in its tree."""
    new_cat = copy.deepcopy(catalog)
    is_univ = race_id in ("universal", "formas_universais_e_stack")
    if is_univ:
        target_container = new_cat.setdefault("formas_universais_e_stack", {}).get(tree_id, {})
    else:
        target_container = (
            new_cat.setdefault("racas", {})
            .get(race_id, {})
            .get("arvores_de_transformacao", {})
            .get(tree_id, {})
        )
    forms_list = target_container.get("formas", [])
    src_idx = next((i for i, f in enumerate(forms_list) if f["id"] == form_id), None)
    if src_idx is None:
        raise KeyError(f"Forma original '{form_id}' não encontrada.")

    src = forms_list[src_idx]
    clean_id = (
        re.sub(r"[^a-z0-9_]", "_", str(new_id).strip().lower())
        if new_id
        else f"{form_id}_clone"
    )
    # Ensure uniqueness
    candidate_id = clean_id
    counter = 1
    existing_ids = {f["id"] for f in forms_list}
    while candidate_id in existing_ids:
        candidate_id = f"{clean_id}_{counter}"
        counter += 1

    clone_entry = copy.deepcopy(src)
    clone_entry["id"] = candidate_id
    clone_entry["nome"] = new_name.strip() if new_name else f"{src.get('nome', form_id)} (Cópia)"
    clone_entry["nivel_habilidade"] = int(src.get("nivel_habilidade", 1)) + 1
    if "_raw_payload" in clone_entry and isinstance(clone_entry["_raw_payload"], dict):
        clone_entry["_raw_payload"]["unlockOnSkillLevel"] = clone_entry["nivel_habilidade"]

    forms_list.insert(src_idx + 1, clone_entry)
    target_container["formas"] = forms_list
    target_container["total_formas"] = len(forms_list)
    new_cat["total_transformacoes"] = new_cat.get("total_transformacoes", 0) + 1
    return new_cat


def auto_scale_tree(
    catalog: dict[str, Any],
    race_id: str,
    tree_id: str,
    mult_step_pct: float = 15.0,
    drain_step_pct: float = 20.0,
) -> dict[str, Any]:
    """Automatically scale multipliers (+X%) and drains (+Y%) sequentially across tree stages."""
    new_cat = copy.deepcopy(catalog)
    is_univ = race_id in ("universal", "formas_universais_e_stack")
    if is_univ:
        container = new_cat.setdefault("formas_universais_e_stack", {}).get(tree_id, {})
    else:
        container = (
            new_cat.setdefault("racas", {})
            .get(race_id, {})
            .get("arvores_de_transformacao", {})
            .get(tree_id, {})
        )
    forms = container.get("formas", [])
    if not forms:
        return new_cat

    mult_factor = 1.0 + (float(mult_step_pct) / 100.0)
    drain_factor = 1.0 + (float(drain_step_pct) / 100.0)

    for i in range(1, len(forms)):
        prev = forms[i - 1]
        curr = forms[i]
        p_mults = prev.get("multiplicadores_detalhados", {})
        c_mults = dict(curr.get("multiplicadores_detalhados", {}))
        for stat_key in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp", "velocidade_spd"):
            base_v = float(p_mults.get(stat_key, c_mults.get(stat_key, 1.0)))
            c_mults[stat_key] = round(base_v * mult_factor, 3)
        curr["multiplicadores_detalhados"] = c_mults
        curr["multiplicador_numerico_base"] = c_mults["forca_str"]
        curr["multiplicador_bp"] = format_bp_string(c_mults)

        p_dr = prev.get("drenos", {})
        c_dr = dict(curr.get("drenos", {}))
        for dr_key in ("energia_ki", "estamina", "vida"):
            base_d = float(p_dr.get(dr_key, c_dr.get(dr_key, 0.0)))
            if base_d > 0:
                c_dr[dr_key] = round(base_d * drain_factor, 4)
        curr["drenos"] = c_dr

        pinfo = compute_power_tier(curr)
        curr["categoria_poder"] = pinfo["tier"]
        curr["tier_label"] = pinfo["tier_label"]
        curr["tier_rank_score"] = pinfo["rank_score"]

    return new_cat


def import_to_staging(
    staging_dock: list[dict[str, Any]], items_or_json: Any
) -> tuple[list[dict[str, Any]], int]:
    """Import forms into staging dock without affecting the active modpack tree."""
    new_dock = list(staging_dock)
    imported_count = 0

    parsed = items_or_json
    if isinstance(items_or_json, str):
        try:
            parsed = json.loads(items_or_json)
        except Exception as exc:
            raise ValueError(f"Formato JSON inválido para importação: {exc}")

    candidates: list[dict[str, Any]] = []
    if isinstance(parsed, dict):
        if "formas" in parsed and isinstance(parsed["formas"], list):
            candidates.extend(parsed["formas"])
        elif "racas" in parsed:
            for r_key, r_obj in parsed.get("racas", {}).items():
                for t_key, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
                    for f in t_obj.get("formas", []):
                        f_copy = copy.deepcopy(f)
                        f_copy["origin_hint"] = {"race": r_key, "tree": t_key}
                        candidates.append(f_copy)
            for g_key, g_obj in parsed.get("formas_universais_e_stack", {}).items():
                for f in g_obj.get("formas", []):
                    f_copy = copy.deepcopy(f)
                    f_copy["origin_hint"] = {"race": "universal", "tree": g_key}
                    candidates.append(f_copy)
        elif "id" in parsed:
            candidates.append(parsed)
    elif isinstance(parsed, list):
        candidates.extend(parsed)

    for item in candidates:
        if isinstance(item, dict) and item.get("id"):
            normalized = _normalize_loaded_entry(item, is_universal=False)
            normalized.setdefault("staging_id", f"stg_{secrets.token_hex(4)}")
            new_dock.append(normalized)
            imported_count += 1

    return new_dock, imported_count


def allocate_from_staging(
    catalog: dict[str, Any],
    staging_dock: list[dict[str, Any]],
    staging_id: str,
    target_race: str,
    target_tree: str,
    target_index: int | None = None,
    conflict_strategy: str = "replace",  # 'replace', 'merge', 'rename'
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Allocate an item from staging dock into the active working tree."""
    new_cat = copy.deepcopy(catalog)
    new_dock = list(staging_dock)

    item_idx = next(
        (i for i, f in enumerate(new_dock) if f.get("staging_id") == staging_id or f.get("id") == staging_id),
        None,
    )
    if item_idx is None:
        raise KeyError(f"Item com ID '{staging_id}' não encontrado na gaveta de espera.")

    item = copy.deepcopy(new_dock.pop(item_idx))
    form_id = item["id"]

    is_univ = target_race in ("universal", "formas_universais_e_stack")
    if is_univ:
        univ_map = new_cat.setdefault("formas_universais_e_stack", {})
        if target_tree not in univ_map:
            univ_map[target_tree] = {
                "arquivo": f"{target_tree}.json",
                "tipo": target_tree,
                "formas": [],
            }
        forms_list = univ_map[target_tree]["formas"]
    else:
        racas_map = new_cat.setdefault("racas", {})
        if target_race not in racas_map:
            racas_map[target_race] = {
                "id_raca": target_race,
                "nome_exibicao": resolve_race_friendly_name(target_race),
                "total_formas": 0,
                "total_arvores": 0,
                "arvores_de_transformacao": {},
            }
        race_obj = racas_map[target_race]
        trees = race_obj.setdefault("arvores_de_transformacao", {})
        if target_tree not in trees:
            trees[target_tree] = {
                "arquivo": f"{target_tree}.json",
                "tipo_habilidade": target_tree,
                "total_formas": 0,
                "formas": [],
            }
            race_obj["total_arvores"] = len(trees)
        forms_list = trees[target_tree]["formas"]

    existing_idx = next((i for i, f in enumerate(forms_list) if f["id"] == form_id), None)
    if existing_idx is not None:
        if conflict_strategy == "replace":
            forms_list[existing_idx] = item
        elif conflict_strategy == "merge":
            forms_list[existing_idx] = _merge_single_form_changes(forms_list[existing_idx], item)
        elif conflict_strategy == "rename":
            candidate = f"{form_id}_custom"
            ctr = 1
            e_ids = {f["id"] for f in forms_list}
            while candidate in e_ids:
                candidate = f"{form_id}_custom_{ctr}"
                ctr += 1
            item["id"] = candidate
            item["nome"] = f"{item.get('nome', form_id)} (Custom)"
            if target_index is not None and 0 <= target_index <= len(forms_list):
                forms_list.insert(target_index, item)
            else:
                forms_list.append(item)
    else:
        if target_index is not None and 0 <= target_index <= len(forms_list):
            forms_list.insert(target_index, item)
        else:
            forms_list.append(item)

    if not is_univ:
        race_obj = new_cat["racas"][target_race]
        race_obj["arvores_de_transformacao"][target_tree]["total_formas"] = len(forms_list)
        race_obj["total_formas"] = sum(
            len(t["formas"]) for t in race_obj["arvores_de_transformacao"].values()
        )
    new_cat["total_transformacoes"] = sum(
        sum(len(t["formas"]) for t in r.get("arvores_de_transformacao", {}).values())
        for r in new_cat.get("racas", {}).values()
    ) + sum(len(g.get("formas", [])) for g in new_cat.get("formas_universais_e_stack", {}).values())

    return new_cat, new_dock, item


def remove_from_staging(
    staging_dock: list[dict[str, Any]], staging_id: str
) -> list[dict[str, Any]]:
    return [
        f
        for f in staging_dock
        if f.get("staging_id") != staging_id and f.get("id") != staging_id
    ]


def export_selective_package(
    catalog: dict[str, Any], selected_items: list[dict[str, Any]]
) -> dict[str, Any]:
    """Generate self-contained JSON package containing only user-selected forms."""
    pkg: dict[str, Any] = {
        "titulo": "Dragon Mine Z - Pacote de Transformações Exportado",
        "versao_modpack": catalog.get("versao_modpack", "Dragon Mine Z RPG 1.20.1"),
        "racas": {},
        "formas_universais_e_stack": {},
        "total_racas": 0,
        "total_transformacoes": 0,
    }

    total_count = 0
    for sel in selected_items:
        r_id = sel.get("race") or sel.get("race_id", "")
        t_id = sel.get("tree") or sel.get("tree_id", "")
        f_id = sel.get("form_id") or sel.get("form", "")

        if r_id in ("universal", "formas_universais_e_stack"):
            src_grp = catalog.get("formas_universais_e_stack", {}).get(t_id)
            if src_grp:
                dst_grp = pkg["formas_universais_e_stack"].setdefault(
                    t_id,
                    {
                        "arquivo": src_grp.get("arquivo", f"{t_id}.json"),
                        "tipo": src_grp.get("tipo", t_id),
                        "formas": [],
                    },
                )
                for f in src_grp.get("formas", []):
                    if not f_id or f["id"] == f_id:
                        if not any(x["id"] == f["id"] for x in dst_grp["formas"]):
                            f_cloned = copy.deepcopy(f)
                            f_cloned["origin_hint"] = {"race": "universal", "tree": t_id}
                            dst_grp["formas"].append(f_cloned)
                            total_count += 1
        else:
            src_race = catalog.get("racas", {}).get(r_id)
            if src_race:
                dst_race = pkg["racas"].setdefault(
                    r_id,
                    {
                        "id_raca": r_id,
                        "nome_exibicao": src_race.get("nome_exibicao", r_id),
                        "total_formas": 0,
                        "total_arvores": 0,
                        "arvores_de_transformacao": {},
                    },
                )
                src_tree = src_race.get("arvores_de_transformacao", {}).get(t_id)
                if src_tree:
                    dst_tree = dst_race["arvores_de_transformacao"].setdefault(
                        t_id,
                        {
                            "arquivo": src_tree.get("arquivo", f"{t_id}.json"),
                            "tipo_habilidade": src_tree.get("tipo_habilidade", t_id),
                            "total_formas": 0,
                            "formas": [],
                        },
                    )
                    for f in src_tree.get("formas", []):
                        if not f_id or f["id"] == f_id:
                            if not any(x["id"] == f["id"] for x in dst_tree["formas"]):
                                f_cloned = copy.deepcopy(f)
                                f_cloned["origin_hint"] = {"race": r_id, "tree": t_id}
                                dst_tree["formas"].append(f_cloned)
                                total_count += 1
                    dst_tree["total_formas"] = len(dst_tree["formas"])
                dst_race["total_formas"] = sum(
                    len(t["formas"]) for t in dst_race["arvores_de_transformacao"].values()
                )
                dst_race["total_arvores"] = len(dst_race["arvores_de_transformacao"])

    pkg["total_racas"] = len(pkg["racas"])
    pkg["total_transformacoes"] = total_count
    return pkg


def compute_state_diff(
    baseline_catalog: dict[str, Any] | None, current_catalog: dict[str, Any] | None
) -> dict[str, Any]:
    """Compute detailed visual diff between baseline disk state and working state in RAM."""
    def _flatten_catalog(cat: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
        out = {}
        if not cat:
            return out
        for r_id, r_obj in cat.get("racas", {}).items():
            for t_id, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
                for f in t_obj.get("formas", []):
                    key = f"{r_id}:{t_id}:{f['id']}"
                    out[key] = f
        for g_id, g_obj in cat.get("formas_universais_e_stack", {}).items():
            for f in g_obj.get("formas", []):
                key = f"universal:{g_id}:{f['id']}"
                out[key] = f
        return out

    base_forms = _flatten_catalog(baseline_catalog)
    curr_forms = _flatten_catalog(current_catalog)

    added = []
    deleted = []
    modified = []

    for k, curr_f in curr_forms.items():
        if k not in base_forms:
            added.append({
                "key": k,
                "id": curr_f["id"],
                "nome": curr_f.get("nome", curr_f["id"]),
                "arvore": curr_f.get("arvore", curr_f.get("grupo", "")),
                "custo_tp": curr_f.get("custo_tp", 0),
                "multiplicador_bp": curr_f.get("multiplicador_bp", "1.0x"),
            })
        else:
            base_f = base_forms[k]
            diffs = []
            for field in ("nome", "custo_tp_numerico", "nivel_habilidade", "comprar_no_mestre", "mestre"):
                if base_f.get(field) != curr_f.get(field):
                    diffs.append({"campo": field, "antes": base_f.get(field), "depois": curr_f.get(field)})
            b_m = base_f.get("multiplicadores_detalhados", {})
            c_m = curr_f.get("multiplicadores_detalhados", {})
            for m_key in ("forca_str", "poder_ki_pwr", "defesa_def", "golpe_skp", "velocidade_spd", "vitalidade_vit", "energia_ene", "estamina_stm"):
                if b_m.get(m_key) != c_m.get(m_key):
                    diffs.append({"campo": f"mult_{m_key}", "antes": b_m.get(m_key), "depois": c_m.get(m_key)})
            b_d = base_f.get("drenos", {})
            c_d = curr_f.get("drenos", {})
            for d_key in ("energia_ki", "estamina", "vida"):
                if b_d.get(d_key) != c_d.get(d_key):
                    diffs.append({"campo": f"dreno_{d_key}", "antes": b_d.get(d_key), "depois": c_d.get(d_key)})
            b_v = base_f.get("visual", {})
            c_v = curr_f.get("visual", {})
            for v_key in ("cor_aura", "cor_cabelo", "tipo_cabelo", "tipo_modelo", "escala"):
                if b_v.get(v_key) != c_v.get(v_key):
                    diffs.append({"campo": f"visual_{v_key}", "antes": b_v.get(v_key), "depois": c_v.get(v_key)})

            if diffs:
                modified.append({
                    "key": k,
                    "id": curr_f["id"],
                    "nome": curr_f.get("nome", curr_f["id"]),
                    "arvore": curr_f.get("arvore", curr_f.get("grupo", "")),
                    "alteracoes": diffs,
                })

    for k, base_f in base_forms.items():
        if k not in curr_forms:
            deleted.append({
                "key": k,
                "id": base_f["id"],
                "nome": base_f.get("nome", base_f["id"]),
                "arvore": base_f.get("arvore", base_f.get("grupo", "")),
            })

    return {
        "total_adicionadas": len(added),
        "total_removidas": len(deleted),
        "total_modificadas": len(modified),
        "total_alteracoes": len(added) + len(deleted) + len(modified),
        "adicionadas": added,
        "removidas": deleted,
        "modificadas": modified,
    }


def validate_integrity(
    catalog: dict[str, Any], config_dir: str | None = None
) -> dict[str, Any]:
    """Perform health-check verifying form references, requirements, and sagas."""
    errors: list[str] = []
    warnings: list[str] = []

    all_form_ids: set[str] = set()
    for r_id, r_obj in catalog.get("racas", {}).items():
        for t_id, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
            for f in t_obj.get("formas", []):
                all_form_ids.add(f["id"])
                all_form_ids.add(f"{t_id}.{f['id']}")
                all_form_ids.add(f"{r_id}.{t_id}.{f['id']}")
    for g_id, g_obj in catalog.get("formas_universais_e_stack", {}).items():
        for f in g_obj.get("formas", []):
            all_form_ids.add(f["id"])
            all_form_ids.add(f"{g_id}.{f['id']}")

    saga_options = {s.get("id", "") for s in catalog.get("opcoes_sagas", []) if s.get("id")}

    for r_id, r_obj in catalog.get("racas", {}).items():
        for t_id, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
            for f in t_obj.get("formas", []):
                reqs = f.get("requisitos", {})
                prev = reqs.get("forma_previa")
                if prev and prev not in all_form_ids:
                    warnings.append(
                        f"[{r_id}/{t_id}/{f['id']}] Forma prévia '{prev}' não foi encontrada no modpack."
                    )
                saga = reqs.get("saga")
                if saga and saga_options and saga not in saga_options:
                    warnings.append(
                        f"[{r_id}/{t_id}/{f['id']}] Saga requerida '{saga}' não consta na lista conhecida de sagas."
                    )
                for incomp in reqs.get("incompativel_com", []):
                    if incomp and incomp not in all_form_ids:
                        warnings.append(
                            f"[{r_id}/{t_id}/{f['id']}] Forma incompatível '{incomp}' não foi encontrada."
                        )

    return {
        "status": "ok" if len(errors) == 0 else "error",
        "ok": len(errors) == 0,
        "erros": errors,
        "avisos": warnings,
        "total_erros": len(errors),
        "total_avisos": len(warnings),
    }


__all__ = [
    "CUSTOM_FORM_NAMES",
    "DEFAULT_DESKTOP_DIR",
    "DEFAULT_DESKTOP_JSON",
    "DEFAULT_DMZ_CONFIG_DIR",
    "DEFAULT_INSTANCE_DIR",
    "DEFAULT_INSTANCE_JSON",
    "PRICELESS_LABEL",
    "RACE_FRIENDLY_NAMES",
    "RACE_FRIENDLY_NAMES_BILINGUAL",
    "SecurityPathError",
    "add_form",
    "allocate_from_staging",
    "apply_batch_balance",
    "apply_batch_scale",
    "apply_form_update",
    "auto_scale_tree",
    "compute_drain_rates_and_autonomy",
    "compute_state_diff",
    "compute_stats_and_bars",
    "default_allowed_roots",
    "delete_form",
    "detect_addon_origin",
    "duplicate_form",
    "export_selective_package",
    "format_bp_string",
    "format_tp_display",
    "import_to_staging",
    "parse_tp_numeric",
    "remove_from_staging",
    "reorder_forms",
    "resolve_race_friendly_name",
    "validate_allowed_path",
    "validate_integrity",
]
