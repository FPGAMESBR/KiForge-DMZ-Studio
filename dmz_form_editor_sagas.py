"""Saga/quest preset extraction and modpack folder resolution for DMZ Editor."""

from __future__ import annotations

import json
import os
import re
from typing import Any
import zipfile

SAGA_FRIENDLY_NAMES: dict[str, str] = {
    "classic_saga": "Dragon Ball Clássico",
    "dball_saga": "Dragon Ball ( Pilaf / Red Ribbon )",
    "saiyan_saga": "Saga Saiyajin",
    "frieza_saga": "Saga Freeza (Namekusei)",
    "android_saga": "Saga Androides & Cell",
    "future_saga": "Saga Trunks do Futuro",
    "movies_saga": "Saga Filmes (Broly, Cooler, Janemba...)",
    "buu_saga": "Saga Majin Buu",
    "daima_saga": "Saga Dragon Ball Daima",
    "beerus_saga": "Saga Batalha dos Deuses (Beerus)",
    "rof_saga": "Saga Renascimento de Freeza",
    "u7vsu6_saga": "Saga Torneio Universo 6 vs 7",
    "black_saga": "Saga Goku Black & Zamasu",
    "top_saga": "Saga Torneio do Poder",
    "broly_saga": "Saga DBS: Broly",
    "moro_saga": "Saga Moro",
    "granolah_saga": "Saga Granolah",
    "gt_saga": "Saga Dragon Ball GT",
    "shadow_saga": "Saga Dragões Malignos (Shadow Dragons)",
    "godfall_saga": "Saga Queda dos Deuses (Godfall)",
    "prestige_saga": "Saga Prestígio",
    "bloodline_angel_saga": "Linhagem: Anjo (Angel)",
    "bloodline_makaijin_saga": "Linhagem: Makaijin (Reino Demoníaco)",
    "bloodline_seiunjin_saga": "Linhagem: Seiunjin",
    "bloodline_sekhari_saga": "Linhagem: Sekhari",
    "bloodline_soulreaper_saga": "Linhagem: Shinigami (Soul Reaper)",
    "bloodline_taimujin_saga": "Linhagem: Taimujin (Hit)",
    "bleach_awakening": "Bleach: Despertar",
    "bleach_lost_agent": "Bleach: Agente Perdido",
    "soul_reaper_trials": "Provas Shinigami (Soul Reaper Trials)",
    "fullbring_trials": "Provas Fullbringer (Fullbring Trials)",
    "visored_trials": "Provas Visored (Visored Trials)",
}

SAGA_ORDER: tuple[str, ...] = tuple(SAGA_FRIENDLY_NAMES.keys())

FALLBACK_SAGA_QUESTS: dict[str, list[tuple[int, str]]] = {
    "classic_saga": [(46, "Rei Piccolo / Torneio Clássico")],
    "saiyan_saga": [(1, "Derrotar Raditz"), (5, "Enfrentar Vegeta"), (12, "Fim da Saga Saiyajin")],
    "frieza_saga": [
        (5, "Forças Especiais Ginyu"),
        (10, "Confronto com Freeza"),
        (13, "Freeza Forma Final / Despertar SSJ"),
    ],
    "android_saga": [
        (5, "Chegada dos Androides"),
        (10, "Cell Imperfeito / Semi-Perfeito"),
        (13, "Jogos de Cell"),
        (15, "Derrotar Cell Super Perfeito"),
    ],
    "buu_saga": [
        (1, "Torneio de Artes Marciais"),
        (4, "Despertar de Majin Buu"),
        (35, "Derrotar Kid Buu"),
    ],
    "shadow_saga": [
        (2, "Dragões Malignos Iniciais"),
        (4, "Nova / Eis Shenron"),
        (6, "Omega Shenron"),
    ],
    "bloodline_angel_saga": [(1, "Ato 1"), (2, "Ato 2"), (3, "Ato 3")],
    "bloodline_makaijin_saga": [(1, "Ato 1"), (2, "Ato 2"), (3, "Ato 3")],
    "bloodline_seiunjin_saga": [(1, "Ato 1"), (2, "Ato 2"), (3, "Ato 3")],
    "bloodline_sekhari_saga": [(1, "Ato 1"), (2, "Ato 2"), (3, "Ato 3")],
    "bloodline_soulreaper_saga": [(1, "O Hollow Interior")],
    "bloodline_taimujin_saga": [(1, "Ato 1"), (2, "Ato 2"), (3, "Ato 3")],
    "soul_reaper_trials": [(5, "Prova 5"), (8, "Prova 8"), (9, "Prova 9"), (10, "Prova 10")],
    "fullbring_trials": [(3, "Prova 3"), (4, "Prova 4"), (5, "Prova 5")],
    "visored_trials": [(2, "Prova 2"), (3, "Prova 3"), (4, "Prova 4"), (5, "Prova 5")],
}


def _is_valid_dmz_dir(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    return (
        os.path.isdir(os.path.join(path, "races"))
        or os.path.isdir(os.path.join(path, "forms"))
        or os.path.isfile(os.path.join(path, "skills.json"))
    )


def resolve_modpack_config_dir(raw_path: str) -> str:
    """Resolve user-chosen instance/config/dragonminez path into config/dragonminez."""
    if not raw_path or not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("Informe um caminho de pasta válido.")

    expanded = os.path.realpath(os.path.expanduser(raw_path.strip().strip('"')))
    candidates = (
        expanded,
        os.path.join(expanded, "dragonminez"),
        os.path.join(expanded, "config", "dragonminez"),
        os.path.join(expanded, ".minecraft", "config", "dragonminez"),
    )
    for cand in candidates:
        if _is_valid_dmz_dir(cand):
            return os.path.realpath(cand)

    raise ValueError(
        "Pasta inválida: não foi encontrada a estrutura 'config/dragonminez' "
        "(com subpastas 'races'/'forms' ou 'skills.json')."
    )


def _humanize_quest_filename(filename: str) -> str:
    stem = os.path.splitext(os.path.basename(filename))[0]
    cleaned = re.sub(r"^\d+[_-]?", "", stem)
    return cleaned.replace("_", " ").replace("-", " ").strip().title() or stem


def _collect_used_sagas(catalog: dict[str, Any] | None) -> set[str]:
    used: set[str] = set()
    if not catalog:
        return used
    for r_obj in catalog.get("racas", {}).values():
        for t_obj in r_obj.get("arvores_de_transformacao", {}).values():
            for f in t_obj.get("formas", []):
                saga = (f.get("requisitos") or {}).get("saga")
                if saga:
                    used.add(str(saga).strip())
    for g_obj in catalog.get("formas_universais_e_stack", {}).values():
        for f in g_obj.get("formas", []):
            saga = (f.get("requisitos") or {}).get("saga")
            if saga:
                used.add(str(saga).strip())
    return used


def _scan_jar_sagas(
    mods_dir: str,
    translations: dict[str, str],
    quests_by_saga: dict[str, dict[int, str]],
) -> None:
    jar_names = (
        "dragonminez-2.2.1.jar",
        "dmzrevamp-2.2.4.jar",
        "dmzsparking-1.5.0.9.1.jar",
        "dmzultra-0.4.1.jar",
    )
    folder_to_saga: dict[str, str] = {
        "saga_u6": "u7vsu6_saga",
        "saga_soul_reaper": "soul_reaper_trials",
        "saga_fullbring": "fullbring_trials",
        "saga_visored": "visored_trials",
    }

    for jar_name in jar_names:
        jar_path = os.path.join(mods_dir, jar_name)
        if not os.path.isfile(jar_path):
            continue
        try:
            with zipfile.ZipFile(jar_path, "r") as zf:
                names = zf.namelist()
                # Pass 1: map questFolder -> sagaId
                for member in names:
                    if "/sagas/" in member and member.endswith(".json") and "/geo/" not in member:
                        try:
                            sdoc = json.loads(zf.read(member))
                        except (OSError, json.JSONDecodeError):
                            continue
                        sid = str(sdoc.get("id") or "").strip()
                        qfolder = str(sdoc.get("questFolder") or "").strip()
                        if sid and qfolder:
                            folder_to_saga[qfolder] = sid

                # Pass 2: read quest JSONs inside saga_* folders
                for member in names:
                    if "/quests/saga_" not in member or not member.endswith(".json"):
                        continue
                    parts = member.split("/")
                    qfolder = next((p for p in parts if p.startswith("saga_")), "")
                    if not qfolder:
                        continue
                    saga_id = folder_to_saga.get(qfolder, f"{qfolder[5:]}_saga")
                    try:
                        qdoc = json.loads(zf.read(member))
                    except (OSError, json.JSONDecodeError):
                        continue
                    qid = qdoc.get("id")
                    if not isinstance(qid, int):
                        continue
                    raw_title = str(qdoc.get("title") or qdoc.get("name") or "").strip()
                    translated = translations.get(raw_title, "")
                    if translated:
                        clean_title = re.sub(r"§[0-9a-fk-or]", "", translated).strip()
                    elif raw_title and "." not in raw_title:
                        clean_title = raw_title
                    else:
                        clean_title = _humanize_quest_filename(member)
                    quests_by_saga.setdefault(saga_id, {})[qid] = clean_title
        except (OSError, zipfile.BadZipFile):
            continue


def extract_modpack_sagas(
    instance_dir: str | None,
    translations: dict[str, str],
    catalog: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build structured list of sagas and quest milestones for GUI dropdowns."""
    quests_by_saga: dict[str, dict[int, str]] = {
        sid: {num: title for num, title in items}
        for sid, items in FALLBACK_SAGA_QUESTS.items()
    }

    if instance_dir and os.path.isdir(os.path.join(instance_dir, "mods")):
        _scan_jar_sagas(
            os.path.join(instance_dir, "mods"), translations, quests_by_saga
        )

    used_values = _collect_used_sagas(catalog)
    custom_bare_sagas: list[str] = []

    for used in sorted(used_values):
        if ":" in used:
            sid, qpart = used.split(":", 1)
            if qpart.isdigit():
                qnum = int(qpart)
                quests_by_saga.setdefault(sid, {}).setdefault(
                    qnum, f"Missão {qnum}"
                )
            else:
                custom_bare_sagas.append(used)
        else:
            custom_bare_sagas.append(used)

    order_index = {sid: idx for idx, sid in enumerate(SAGA_ORDER)}
    sorted_saga_ids = sorted(
        quests_by_saga.keys(),
        key=lambda s: (order_index.get(s, 999), s),
    )

    result: list[dict[str, Any]] = []
    for sid in sorted_saga_ids:
        qmap = quests_by_saga[sid]
        quests_list = [
            {
                "valor": f"{sid}:{qnum}",
                "numero": qnum,
                "titulo": qmap[qnum],
                "usado": f"{sid}:{qnum}" in used_values,
            }
            for qnum in sorted(qmap.keys())
        ]
        if quests_list:
            result.append(
                {
                    "id": sid,
                    "nome": SAGA_FRIENDLY_NAMES.get(
                        sid, sid.replace("_", " ").title()
                    ),
                    "quests": quests_list,
                }
            )

    for bare in custom_bare_sagas:
        result.append(
            {
                "id": bare,
                "nome": SAGA_FRIENDLY_NAMES.get(
                    bare, f"Personalizada: {bare}"
                ),
                "quests": [
                    {
                        "valor": bare,
                        "numero": 0,
                        "titulo": bare,
                        "usado": True,
                    }
                ],
            }
        )

    return result


def load_editor_settings(settings_path: str) -> dict[str, str]:
    if not settings_path or not os.path.isfile(settings_path):
        return {}
    try:
        with open(settings_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}
    except (OSError, json.JSONDecodeError):
        return {}
    return {}


def save_editor_settings(settings_path: str, settings: dict[str, str]) -> None:
    if not settings_path:
        return
    os.makedirs(os.path.dirname(os.path.abspath(settings_path)), exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)
