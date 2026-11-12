"""Core engine for reading, editing, and syncing Dragon Mine Z transformations.

Follows strict immutability (never mutates input dictionaries in-place) and
path-boundary validation against Path Traversal.
"""

from __future__ import annotations

import copy
import os
import re
from typing import Any


class SecurityPathError(ValueError):
    """Raised when a target path escapes allowed root directories."""


DEFAULT_INSTANCE_DIR = ""
DEFAULT_DMZ_CONFIG_DIR = ""
DEFAULT_DESKTOP_DIR = ""
DEFAULT_DESKTOP_JSON = ""
DEFAULT_INSTANCE_JSON = ""

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
    return {
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
            "cor_cabelo": str(fprops.get("hairColor") or ""),
        },
        "addon_origem": detect_addon_origin(group_key, form_id),
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
    for k in ("cor_aura", "cor_cabelo"):
        raw_c = str(vis.get(k) or "").strip()
        if raw_c and not raw_c.startswith("#") and len(raw_c) in (3, 6, 8):
            raw_c = "#" + raw_c
        vis[k] = raw_c
    cloned["visual"] = vis
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
                s_val = str(v).strip()
                if s_val and not s_val.startswith("#") and len(s_val) in (3, 6, 8):
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
        fprops["hairColor"] = vis.get("cor_cabelo", "")

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




# ==============================================================================
# 3-LAYER STUDIO STATE & STAGING DOCK ARCHITECTURE
# ==============================================================================

def init_studio_state(catalog: dict[str, Any]) -> dict[str, Any]:
    """Initialize the 3-layer in-memory state: baseline (immutable), working (active), staging (pending imports)."""
    return {
        "baseline_state": copy.deepcopy(catalog),
        "working_state": copy.deepcopy(catalog),
        "staging_dock": [],
    }


def compute_catalog_diff(
    baseline: dict[str, Any],
    working: dict[str, Any]
) -> list[dict[str, Any]]:
    """Compare baseline and working catalogs, returning a structured list of diff entries."""
    diffs: list[dict[str, Any]] = []

    def index_catalog(cat: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
        idx: dict[tuple[str, str, str], dict[str, Any]] = {}
        for r_key, r_obj in cat.get("racas", {}).items():
            for t_key, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
                for f in t_obj.get("formas", []):
                    fid = str(f.get("id", ""))
                    if fid:
                        idx[(r_key, t_key, fid)] = f
        for g_key, g_obj in cat.get("formas_universais_e_stack", {}).items():
            for f in g_obj.get("formas", []):
                fid = str(f.get("id", ""))
                if fid:
                    idx[("global", g_key, fid)] = f
        return idx

    base_idx = index_catalog(baseline)
    work_idx = index_catalog(working)

    for key, w_form in work_idx.items():
        r_key, g_key, fid = key
        fname = w_form.get("nome", fid)
        if key not in base_idx:
            diffs.append({
                "race": r_key,
                "group": g_key,
                "form_id": fid,
                "form_name": fname,
                "prop": "status",
                "old": None,
                "new": "Nova Forma / New Form",
                "action": "added"
            })
        else:
            b_form = base_idx[key]
            for prop in [
                "multiplicador_bp", "custo_tp", "dreno_energia", "dreno_estamina",
                "dreno_vida", "nivel_habilidade", "aura_tipo", "cabelo_tipo",
                "forma_previa", "mestre"
            ]:
                old_v = b_form.get(prop)
                new_v = w_form.get(prop)
                if old_v != new_v and (old_v is not None or new_v is not None):
                    diffs.append({
                        "race": r_key,
                        "group": g_key,
                        "form_id": fid,
                        "form_name": fname,
                        "prop": prop,
                        "old": str(old_v),
                        "new": str(new_v),
                        "action": "modified"
                    })
            old_m = b_form.get("multiplicadores_detalhados", {})
            new_m = w_form.get("multiplicadores_detalhados", {})
            for m_k in set(old_m.keys()).union(new_m.keys()):
                if old_m.get(m_k) != new_m.get(m_k):
                    diffs.append({
                        "race": r_key,
                        "group": g_key,
                        "form_id": fid,
                        "form_name": fname,
                        "prop": f"mult_{m_k}",
                        "old": str(old_m.get(m_k)),
                        "new": str(new_m.get(m_k)),
                        "action": "modified"
                    })

    for key, b_form in base_idx.items():
        if key not in work_idx:
            r_key, g_key, fid = key
            diffs.append({
                "race": r_key,
                "group": g_key,
                "form_id": fid,
                "form_name": b_form.get("nome", fid),
                "prop": "status",
                "old": "Ativa / Active",
                "new": "Excluída / Deleted",
                "action": "deleted"
            })

    return diffs


def clone_stage(
    working_state: dict[str, Any],
    race_id: str,
    group_key: str,
    source_form_id: str,
    new_form_id: str,
    new_name: str,
) -> dict[str, Any]:
    """Clone an existing stage into the same group with a new ID and display name."""
    new_cat = copy.deepcopy(working_state)
    target_forms: list[dict[str, Any]] | None = None
    target_group: dict[str, Any] | None = None

    if race_id == "global":
        g_obj = new_cat.get("formas_universais_e_stack", {}).get(group_key)
        if g_obj:
            target_group = g_obj
            target_forms = g_obj.get("formas", [])
    else:
        r_obj = new_cat.get("racas", {}).get(race_id)
        if r_obj:
            t_obj = r_obj.get("arvores_de_transformacao", {}).get(group_key)
            if t_obj:
                target_group = t_obj
                target_forms = t_obj.get("formas", [])

    if target_forms is None or target_group is None:
        raise ValueError(f"Grupo {group_key} não encontrado na raça {race_id}")

    # Find source form
    source_form: dict[str, Any] | None = None
    max_level = 0
    for f in target_forms:
        lvl = int(f.get("nivel_habilidade", 1) or 1)
        if lvl > max_level:
            max_level = lvl
        if f.get("id") == source_form_id:
            source_form = f

    if not source_form:
        raise ValueError(f"Forma de origem {source_form_id} não encontrada no grupo {group_key}")

    cloned = copy.deepcopy(source_form)
    clean_id = re.sub(r"[^a-zA-Z0-9_]", "_", new_form_id.strip().lower())
    cloned["id"] = clean_id
    cloned["nome"] = new_name.strip() or f"{source_form.get('nome', '')} (Clone)"
    cloned["nivel_habilidade"] = max_level + 1
    cloned["forma_previa"] = source_form_id

    target_forms.append(cloned)
    target_group["total_formas"] = len(target_forms)
    new_cat["total_transformacoes"] = new_cat.get("total_transformacoes", 0) + 1

    return new_cat


def auto_scale_group(
    working_state: dict[str, Any],
    race_id: str,
    group_key: str,
    multiplier_step_pct: float = 15.0,
    drain_step_pct: float = 10.0,
    base_form_id: str | None = None,
) -> dict[str, Any]:
    """Automatically scale stats and drain progressively across all stages in a group."""
    new_cat = copy.deepcopy(working_state)
    target_forms: list[dict[str, Any]] | None = None

    if race_id == "global":
        g_obj = new_cat.get("formas_universais_e_stack", {}).get(group_key)
        if g_obj:
            target_forms = g_obj.get("formas", [])
    else:
        r_obj = new_cat.get("racas", {}).get(race_id)
        if r_obj:
            t_obj = r_obj.get("arvores_de_transformacao", {}).get(group_key)
            if t_obj:
                target_forms = t_obj.get("formas", [])

    if not target_forms:
        return new_cat

    # Sort stages by unlock level or order
    target_forms.sort(key=lambda x: int(x.get("nivel_habilidade", 1) or 1))

    # Base values from first form
    base = target_forms[0]
    base_mults = copy.deepcopy(base.get("multiplicadores_detalhados", {}))
    base_drain_e = float(base.get("dreno_energia", 0.0) or 0.0)
    base_drain_s = float(base.get("dreno_estamina", 0.0) or 0.0)
    base_drain_h = float(base.get("dreno_vida", 0.0) or 0.0)

    m_factor = 1.0 + (multiplier_step_pct / 100.0)
    d_factor = 1.0 + (drain_step_pct / 100.0)

    for i, form in enumerate(target_forms):
        if i == 0:
            continue
        cur_mults = {}
        for k, v in base_mults.items():
            cur_mults[k] = round(float(v) * (m_factor ** i), 2)
        form["multiplicadores_detalhados"] = cur_mults
        form["multiplicador_bp"] = format_bp_string(cur_mults)
        form["dreno_energia"] = round(base_drain_e * (d_factor ** i), 2)
        form["dreno_estamina"] = round(base_drain_s * (d_factor ** i), 2)
        form["dreno_vida"] = round(base_drain_h * (d_factor ** i), 2)

    return new_cat


def reorder_group_stages(
    working_state: dict[str, Any],
    race_id: str,
    group_key: str,
    ordered_form_ids: list[str],
    auto_update_levels: bool = True,
    start_level: int = 1,
) -> dict[str, Any]:
    """Reorder stages inside a group and optionally update unlockOnSkillLevel sequentially."""
    new_cat = copy.deepcopy(working_state)
    target_forms: list[dict[str, Any]] | None = None
    target_group: dict[str, Any] | None = None

    if race_id == "global":
        g_obj = new_cat.get("formas_universais_e_stack", {}).get(group_key)
        if g_obj:
            target_group = g_obj
            target_forms = g_obj.get("formas", [])
    else:
        r_obj = new_cat.get("racas", {}).get(race_id)
        if r_obj:
            t_obj = r_obj.get("arvores_de_transformacao", {}).get(group_key)
            if t_obj:
                target_group = t_obj
                target_forms = t_obj.get("formas", [])

    if not target_forms or not target_group:
        return new_cat

    form_map = {f.get("id"): f for f in target_forms}
    new_list: list[dict[str, Any]] = []

    for idx, fid in enumerate(ordered_form_ids):
        if fid in form_map:
            f = form_map.pop(fid)
            if auto_update_levels:
                f["nivel_habilidade"] = start_level + idx
            new_list.append(f)

    # Append any remaining forms not in ordered list
    for remaining_f in form_map.values():
        if auto_update_levels:
            remaining_f["nivel_habilidade"] = start_level + len(new_list)
        new_list.append(remaining_f)

    target_group["formas"] = new_list
    return new_cat


def reorder_race_groups(
    working_state: dict[str, Any],
    race_id: str,
    ordered_group_keys: list[str],
) -> dict[str, Any]:
    """Reorder transformation groups within a race."""
    new_cat = copy.deepcopy(working_state)
    r_obj = new_cat.get("racas", {}).get(race_id)
    if not r_obj:
        return new_cat

    arvores = r_obj.get("arvores_de_transformacao", {})
    new_arvores: dict[str, Any] = {}

    for g_key in ordered_group_keys:
        if g_key in arvores:
            new_arvores[g_key] = arvores[g_key]

    for k, v in arvores.items():
        if k not in new_arvores:
            new_arvores[k] = v

    r_obj["arvores_de_transformacao"] = new_arvores
    return new_cat


def add_to_staging_dock(
    staging_dock: list[dict[str, Any]],
    item_payload: dict[str, Any],
    item_type: str = "sub_form",
    source: str = "import",
    origin_hint: str = "",
) -> list[dict[str, Any]]:
    """Add an imported form or group safely into the staging dock out-of-tree."""
    new_dock = copy.deepcopy(staging_dock)
    import uuid

    staging_id = f"stg_{uuid.uuid4().hex[:8]}"
    name = (
        item_payload.get("nome")
        or item_payload.get("name")
        or item_payload.get("groupName")
        or "Item Importado"
    )

    new_dock.append({
        "staging_id": staging_id,
        "type": item_type,
        "name": name,
        "source": source,
        "origin_hint": origin_hint,
        "payload": copy.deepcopy(item_payload),
    })
    return new_dock


def remove_from_staging_dock(
    staging_dock: list[dict[str, Any]],
    staging_id: str,
) -> list[dict[str, Any]]:
    """Remove an item from the staging dock."""
    return [item for item in staging_dock if item.get("staging_id") != staging_id]


def allocate_staging_to_tree(
    working_state: dict[str, Any],
    staging_dock: list[dict[str, Any]],
    staging_id: str,
    target_race: str,
    target_group: str,
    conflict_mode: str = "rename",
    custom_id: str | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    """Allocate an item from staging dock into the working catalog tree."""
    new_cat = copy.deepcopy(working_state)
    target_item = None
    for item in staging_dock:
        if item.get("staging_id") == staging_id:
            target_item = item
            break

    if not target_item:
        raise ValueError(f"Item {staging_id} não encontrado na Gaveta de Importados.")

    payload = copy.deepcopy(target_item["payload"])
    item_type = target_item.get("type", "sub_form")

    # Locate destination
    if target_race == "global":
        g_map = new_cat.setdefault("formas_universais_e_stack", {})
        if target_group not in g_map:
            g_map[target_group] = {
                "arquivo": f"{target_group}.json",
                "tipo_habilidade": target_group,
                "total_formas": 0,
                "formas": []
            }
        grp = g_map[target_group]
    else:
        r_obj = new_cat.setdefault("racas", {}).setdefault(target_race, {
            "id_raca": target_race,
            "nome_exibicao": resolve_race_friendly_name(target_race),
            "total_formas": 0,
            "total_arvores": 0,
            "arvores_de_transformacao": {}
        })
        arv = r_obj.setdefault("arvores_de_transformacao", {})
        if target_group not in arv:
            arv[target_group] = {
                "arquivo": f"{target_group}.json",
                "tipo_habilidade": target_group,
                "total_formas": 0,
                "formas": []
            }
            r_obj["total_arvores"] = len(arv)
        grp = arv[target_group]

    formas = grp.setdefault("formas", [])
    raw_fid = payload.get("id") or payload.get("name") or "custom_form"
    final_fid = custom_id or raw_fid

    # Check collision
    existing_idx = None
    for idx, f in enumerate(formas):
        if f.get("id") == final_fid:
            existing_idx = idx
            break

    if existing_idx is not None:
        if conflict_mode == "replace":
            payload["id"] = final_fid
            formas[existing_idx] = payload
        elif conflict_mode == "merge":
            formas[existing_idx].update(payload)
            formas[existing_idx]["id"] = final_fid
        else:  # rename
            final_fid = f"{final_fid}_custom"
            payload["id"] = final_fid
            formas.append(payload)
    else:
        payload["id"] = final_fid
        formas.append(payload)

    grp["total_formas"] = len(formas)
    new_cat["total_transformacoes"] = new_cat.get("total_transformacoes", 0) + 1

    # Remove from staging dock
    new_dock = remove_from_staging_dock(staging_dock, staging_id)
    return new_cat, new_dock, final_fid


def create_wizard_form(
    working_state: dict[str, Any],
    group_id: str,
    group_name: str,
    target_race: str,
    is_universal: bool = False,
    num_stages: int = 1,
    base_name: str = "",
    base_hair: str = "base",
    base_aura: str = "kakarot",
    base_color_hair: str = "#FFE89E",
    base_color_aura: str = "#FFD700",
) -> dict[str, Any]:
    """Create a new transformation group and initial stages via Guided Wizard."""
    new_cat = copy.deepcopy(working_state)
    clean_group = re.sub(r"[^a-zA-Z0-9_]", "_", group_id.strip().lower())

    stages: list[dict[str, Any]] = []
    display_base = base_name.strip() or group_name.strip() or clean_group.title()

    for i in range(1, max(1, num_stages) + 1):
        stage_id = f"{clean_group}_{i}" if num_stages > 1 else clean_group
        stage_name = f"{display_base} {i}" if num_stages > 1 else display_base
        mult_val = round(1.5 + (i - 1) * 0.8, 2)
        drain_val = round(1.0 + (i - 1) * 0.5, 2)

        stages.append({
            "id": stage_id,
            "nome": stage_name,
            "arvore": clean_group,
            "tipo_habilidade": clean_group,
            "nivel_habilidade": i,
            "custo_tp": int(50000 * i),
            "custo_tp_numerico": int(50000 * i),
            "comprar_no_mestre": False,
            "mestre": "",
            "mestre_nome": "",
            "multiplicador_bp": f"{mult_val}x",
            "multiplicador_numerico_base": mult_val,
            "multiplicadores_detalhados": {
                "forca_str": mult_val,
                "poder_ki_pwr": mult_val,
                "defesa_def": mult_val,
                "golpe_skp": mult_val,
                "estamina_stm": mult_val,
                "vitalidade_vit": 1.0,
                "energia_ene": 1.0,
                "velocidade_spd": 1.1 + (i - 1) * 0.1,
                "velocidade_ataque": 1.05 + (i - 1) * 0.05,
            },
            "dreno_energia": drain_val,
            "dreno_estamina": round(drain_val * 0.5, 2),
            "dreno_vida": 0.0,
            "dreno_outro_mundo": 1.0,
            "dreno_outro_mundo_dominado": 0.5,
            "forma_previa": f"{clean_group}_{i-1}" if i > 1 else "",
            "tipo_forma_previa": clean_group if i > 1 else "",
            "nivel_minimo": 1,
            "saga_obrigatoria": "",
            "muda_aparencia": True,
            "tipo_cabelo": base_hair,
            "cor_cabelo": base_color_hair,
            "tipo_aura": base_aura,
            "cor_aura": base_color_aura,
            "tem_raios": (i >= 2),
            "cor_raios": "#00E5FF",
            "manto_ki_ativo": False,
            "manto_ki_estilo": "fervilhante",
            "manto_ki_cor_interna": "#FF1100",
            "manto_ki_cor_borda": "#FF8800",
            "manto_ki_opacidade": 75,
            "manto_ki_velocidade": 1.0,
            "escala_modelo": 1.0,
            "origem_addon": "Custom Wizard",
            "arquivo_origem": f"{clean_group}.json",
            "caminho_relativo_arquivo": f"{clean_group}.json",
        })

    group_dict = {
        "arquivo": f"{clean_group}.json",
        "tipo_habilidade": clean_group,
        "total_formas": len(stages),
        "formas": stages,
    }

    if is_universal or target_race == "global":
        new_cat.setdefault("formas_universais_e_stack", {})[clean_group] = group_dict
    else:
        r_obj = new_cat.setdefault("racas", {}).setdefault(target_race, {
            "id_raca": target_race,
            "nome_exibicao": resolve_race_friendly_name(target_race),
            "total_formas": 0,
            "total_arvores": 0,
            "arvores_de_transformacao": {}
        })
        r_obj.setdefault("arvores_de_transformacao", {})[clean_group] = group_dict
        r_obj["total_arvores"] = len(r_obj["arvores_de_transformacao"])

    new_cat["total_transformacoes"] = new_cat.get("total_transformacoes", 0) + len(stages)
    return new_cat


def simulate_drain(
    form_data: dict[str, Any],
    base_ki: float = 1000.0,
    base_stm: float = 1000.0,
    base_hp: float = 1000.0,
) -> dict[str, Any]:
    """Calculate simulated drain rates and autonomy time in seconds."""
    ki_drain_per_sec = float(form_data.get("dreno_energia", 0.0) or 0.0)
    stm_drain_per_sec = float(form_data.get("dreno_estamina", 0.0) or 0.0)
    hp_drain_per_sec = float(form_data.get("dreno_vida", 0.0) or 0.0)

    ki_seconds = (base_ki / ki_drain_per_sec) if ki_drain_per_sec > 0 else 99999.0
    stm_seconds = (base_stm / stm_drain_per_sec) if stm_drain_per_sec > 0 else 99999.0
    hp_seconds = (base_hp / hp_drain_per_sec) if hp_drain_per_sec > 0 else 99999.0

    min_autonomy = min(ki_seconds, stm_seconds, hp_seconds)
    limiting_resource = "KI" if min_autonomy == ki_seconds else ("STM" if min_autonomy == stm_seconds else "HP")
    if min_autonomy >= 99999.0:
        min_autonomy = 0.0
        limiting_resource = "None (Infinite)"

    return {
        "ki_drain_per_sec": ki_drain_per_sec,
        "stm_drain_per_sec": stm_drain_per_sec,
        "hp_drain_per_sec": hp_drain_per_sec,
        "autonomy_seconds": round(min_autonomy, 1),
        "limiting_resource": limiting_resource,
    }


__all__ = [
    "init_studio_state",
    "compute_catalog_diff",
    "clone_stage",
    "auto_scale_group",
    "reorder_group_stages",
    "reorder_race_groups",
    "add_to_staging_dock",
    "remove_from_staging_dock",
    "allocate_staging_to_tree",
    "create_wizard_form",
    "simulate_drain",

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
    "apply_batch_balance",
    "apply_batch_scale",
    "apply_form_update",
    "default_allowed_roots",
    "delete_form",
    "detect_addon_origin",
    "format_bp_string",
    "format_tp_display",
    "parse_tp_numeric",
    "resolve_race_friendly_name",
    "validate_allowed_path",
]
