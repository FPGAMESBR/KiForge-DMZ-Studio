"""Persistence and modpack I/O routines for Dragon Mine Z transformations.

Handles reading/writing exported JSON catalogs and applying edits back into
DragonMineZ config files (`character.json`, `races/<race>/forms/*.json`,
`forms/*.json`, and `skills.json`) with automatic timestamped backups.
"""

from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import json
import os
import re
import shutil
import sys
from typing import Any
import zipfile

from dmz_form_editor_core import (
    CUSTOM_FORM_NAMES,
    MASTER_FRIENDLY_NAMES,
    RACE_FRIENDLY_NAMES,
    _build_form_entry,
    _normalize_loaded_entry,
    default_allowed_roots,
    detect_addon_origin,
    infer_master_for_form,
    resolve_race_friendly_name,
    validate_allowed_path,
)
from dmz_form_editor_sagas import extract_modpack_sagas

IGNORED_SUBDIRS = {
    "oldbackup",
    ".kaipath-recovery",
    "backups",
    "old_backups",
    "dmzultra/backups",
    "backups_editor",
}

IGNORED_EXTENSIONS = (
    ".dmzultra_hash",
    ".dmzultra_free",
    ".dmzultra_rev",
    ".dmzultra_mutant",
    ".dmzultra_beast_look4",
    ".dmzultra_defaulthairtype",
    ".pre-metadata-recovery-backup",
    ".pre-race-visual-backup",
    ".pre-race-rose-backup",
    ".bak",
    ".disabled",
    ".tmp",
)


IGNORED_FILENAMES = {
    "stats.json",
    "character.json",
    "settings.json",
    "skills.json",
    "todas_as_transformacoes.json",
}


def is_valid_form_json_file(fname: str) -> bool:
    """Strictly filter auxiliary and backup mod files, matching only valid form JSONs."""
    bname = os.path.basename(fname).lower()
    if not bname.endswith(".json"):
        return False
    if bname in IGNORED_FILENAMES:
        return False
    if any(bname.endswith(ext) for ext in IGNORED_EXTENSIONS):
        return False
    if ".pre-" in bname and "-backup" in bname:
        return False
    return True


def get_backups_dir() -> str:
    """Return local studio backups directory, resolving via sys.executable when frozen."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    b_dir = os.path.join(base_dir, "backups")
    os.makedirs(b_dir, exist_ok=True)
    return b_dir


def prune_old_backups(backups_dir: str, max_keep: int = 30) -> None:
    """Keep only the latest N .zip backup archives, removing older ones."""
    if not os.path.isdir(backups_dir):
        return
    zips = [
        os.path.join(backups_dir, f)
        for f in os.listdir(backups_dir)
        if f.lower().endswith(".zip")
    ]
    zips.sort(key=os.path.getmtime, reverse=True)
    for old_zip in zips[max_keep:]:
        try:
            os.remove(old_zip)
        except OSError:
            pass


def list_backups() -> list[dict[str, Any]]:
    """List all available local backups ordered by timestamp (newest first)."""
    b_dir = get_backups_dir()
    if not os.path.isdir(b_dir):
        return []
    items: list[dict[str, Any]] = []
    for fname in sorted(os.listdir(b_dir), reverse=True):
        if fname.lower().endswith(".zip"):
            fpath = os.path.join(b_dir, fname)
            try:
                st = os.stat(fpath)
                iso_str = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                items.append({
                    "filename": fname,
                    "path": fpath,
                    "size_bytes": st.st_size,
                    "size_kb": round(st.st_size / 1024, 1),
                    "created_at": iso_str,
                    "created_iso": iso_str,
                })
            except OSError:
                continue
    return items


def create_modpack_backup_zip(
    files_to_backup: list[str],
    dmz_root: str,
    backups_dir: str | None = None,
) -> str | None:
    """Create a compressed .zip archive of files before modifying modpack."""
    existing_files = [f for f in files_to_backup if os.path.isfile(f)]
    if not existing_files:
        return None
    b_dir = backups_dir or get_backups_dir()
    os.makedirs(b_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(b_dir, f"backup_{stamp}.zip")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fpath in existing_files:
            rel = os.path.relpath(fpath, dmz_root)
            zf.write(fpath, arcname=rel)

    prune_old_backups(b_dir, max_keep=30)
    return zip_path


def atomic_save_json(target_path: str, data: Any, indent: int = 2) -> None:
    """Safely write JSON to a .tmp file first, flush, fsync, and atomic os.replace.
    Also synchronizes .dmzultra_hash SHA-256 for dmzultra compatibility.
    """
    tmp_path = f"{target_path}.tmp"
    parent = os.path.dirname(target_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass
    os.replace(tmp_path, target_path)

    # If target has a corresponding .dmzultra_hash or is dmzultra-related, update hash!
    hash_file = f"{target_path}.dmzultra_hash"
    if os.path.isfile(hash_file) or "dmzultra" in target_path.lower():
        with open(target_path, "rb") as fh:
            h = hashlib.sha256(fh.read()).hexdigest().lower()
        hash_tmp = f"{hash_file}.tmp"
        with open(hash_tmp, "w", encoding="utf-8") as fh:
            fh.write(h)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:
                pass
        os.replace(hash_tmp, hash_file)


def _load_mod_translations(instance_dir: str | None) -> dict[str, str]:
    if not instance_dir or not os.path.isdir(instance_dir):
        return {}
    merged: dict[str, str] = {}
    mods_dir = os.path.join(instance_dir, "mods")
    if not os.path.isdir(mods_dir):
        return {}

    for fname in sorted(os.listdir(mods_dir)):
        if not fname.lower().endswith(".jar"):
            continue
        jar_path = os.path.join(mods_dir, fname)
        try:
            with zipfile.ZipFile(jar_path, "r") as zf:
                for member in zf.namelist():
                    if member.endswith("en_us.json") or member.endswith("pt_br.json"):
                        try:
                            data = json.loads(zf.read(member))
                            if isinstance(data, dict):
                                merged.update(data)
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
        except (OSError, zipfile.BadZipFile):
            continue
    return merged


def _resolve_display_name(
    translations: dict[str, str], race: str, group: str, form_id: str
) -> str:
    keys = (
        f"race.dragonminez.{race}.form.{group}.{form_id}",
        f"race.dragonminez.{race}.form.{form_id}",
        f"race.dragonminez.stack.form.{group}.{form_id}",
        f"race.dragonminez.stack.form.{form_id}",
        f"form.dragonminez.{form_id}",
        f"skill.dragonminez.{form_id}",
    )
    for key in keys:
        if key in translations:
            return re.sub(r"§[0-9a-fk-or]", "", str(translations[key])).strip()
    if form_id in CUSTOM_FORM_NAMES:
        return CUSTOM_FORM_NAMES[form_id]
    return form_id.replace("_", " ").replace("-", " ").title()


def _resolve_tp_and_master(
    char_costs: dict[str, Any],
    global_skills: dict[str, Any],
    form_type: str,
    stem: str,
    form_id: str,
    level: int,
    skill_offerings: dict[str, list[str]] | None = None,
) -> tuple[int, bool, str, str]:
    found_masters: list[str] = []
    if skill_offerings:
        keys_to_check = {k for k in (form_type, stem, form_id) if k}
        for m_id, m_skills in skill_offerings.items():
            if keys_to_check.intersection(m_skills):
                found_masters.append(m_id)

    buy_from_master = len(found_masters) > 0
    mestre_id = ", ".join(found_masters)
    mestre_nomes = [MASTER_FRIENDLY_NAMES.get(m, m.title()) for m in found_masters]
    mestre_nome = " / ".join(mestre_nomes)

    for key in (form_type, stem, form_id):
        if key and key in char_costs:
            entry = char_costs[key]
            if isinstance(entry, dict):
                if "buyFromMaster" in entry:
                    buy_from_master = bool(entry.get("buyFromMaster", False))
                prices = entry.get("prices", [])
            else:
                prices = entry if isinstance(entry, list) else []
            if level == 0:
                return 0, buy_from_master, mestre_id, mestre_nome
            if 0 < level <= len(prices):
                val = int(prices[level - 1])
                if buy_from_master and not mestre_nome:
                    inf_id, inf_nome = infer_master_for_form(stem, form_id, form_type)
                    if inf_id:
                        mestre_id, mestre_nome = inf_id, inf_nome
                return (-1 if val < 0 else val), buy_from_master, mestre_id, mestre_nome

    if level == 0:
        return 0, buy_from_master, mestre_id, mestre_nome

    for key in (form_type, stem, form_id):
        if key and key in global_skills:
            costs = global_skills[key].get("costs", [])
            if 0 < level <= len(costs):
                val = int(costs[level - 1])
                if buy_from_master and not mestre_nome:
                    inf_id, inf_nome = infer_master_for_form(stem, form_id, form_type)
                    if inf_id:
                        mestre_id, mestre_nome = inf_id, inf_nome
                return (-1 if val < 0 else val), buy_from_master, mestre_id, mestre_nome

    if buy_from_master and not mestre_nome:
        inf_id, inf_nome = infer_master_for_form(stem, form_id, form_type)
        if inf_id:
            mestre_id, mestre_nome = inf_id, inf_nome

    return -1, buy_from_master, mestre_id, mestre_nome


def _read_race_entry(
    races_dir: str,
    race: str,
    global_skills: dict[str, Any],
    translations: dict[str, str],
    skill_offerings: dict[str, list[str]] | None = None,
) -> tuple[dict[str, Any], int]:
    char_path = os.path.join(races_dir, race, "character.json")
    char_costs: dict[str, Any] = {}
    if os.path.isfile(char_path):
        with open(char_path, "r", encoding="utf-8") as fh:
            char_costs = json.load(fh).get("formSkillsCosts", {})

    r_forms_dir = os.path.join(races_dir, race, "forms")
    trees: dict[str, Any] = {}
    race_count = 0

    stats_path = os.path.join(races_dir, race, "stats.json")
    race_stats: dict[str, Any] = {}
    if os.path.isfile(stats_path):
        try:
            with open(stats_path, "r", encoding="utf-8") as fh:
                race_stats = json.load(fh)
        except Exception:
            race_stats = {}

    if os.path.isdir(r_forms_dir):
        for fname in sorted(os.listdir(r_forms_dir)):
            if not is_valid_form_json_file(fname):
                continue
            stem = fname[:-5]
            fpath = os.path.join(r_forms_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as fh:
                    fdata = json.load(fh)
            except (OSError, json.JSONDecodeError):
                continue

            ftype = str(fdata.get("formType") or stem)
            forms_dict = fdata.get("forms", {})
            if not isinstance(forms_dict, dict):
                continue

            tree_forms: list[dict[str, Any]] = []
            for form_id, fprops in forms_dict.items():
                lvl = int(fprops.get("unlockOnSkillLevel", 1))
                tp_num, buy_master, m_id, m_nome = _resolve_tp_and_master(
                    char_costs,
                    global_skills,
                    ftype,
                    stem,
                    form_id,
                    lvl,
                    skill_offerings=skill_offerings,
                )
                disp = _resolve_display_name(translations, race, stem, form_id)
                tree_forms.append(
                    _build_form_entry(
                        form_id=form_id,
                        display_name=disp,
                        group_key=stem,
                        form_type=ftype,
                        level=lvl,
                        tp_num=tp_num,
                        buy_from_master=buy_master,
                        fprops=fprops,
                        is_universal=False,
                        mestre=m_id,
                        mestre_nome=m_nome,
                    )
                )
                race_count += 1

            if tree_forms:
                trees[stem] = {
                    "arquivo": fname,
                    "tipo_habilidade": ftype,
                    "total_formas": len(tree_forms),
                    "formas": tree_forms,
                }

    race_payload = {
        "id_raca": race,
        "nome_exibicao": resolve_race_friendly_name(race),
        "total_formas": race_count,
        "total_arvores": len(trees),
        "arvores_de_transformacao": trees,
        "stats": race_stats,
    }
    return race_payload, race_count


def load_catalog_from_modpack(
    dmz_config_dir: str,
    instance_dir: str | None = None,
    allowed_roots: list[str] | None = None,
) -> dict[str, Any]:
    """Read live DragonMineZ config files and return a rich catalog dict."""
    roots = (
        allowed_roots
        if allowed_roots is not None
        else [dmz_config_dir, *default_allowed_roots()]
    )
    safe_dmz = validate_allowed_path(dmz_config_dir, allowed_roots=roots)
    inferred_instance = instance_dir or os.path.dirname(os.path.dirname(safe_dmz))
    translations = _load_mod_translations(inferred_instance)

    skills_path = os.path.join(safe_dmz, "skills.json")
    global_skills: dict[str, Any] = {}
    skill_offerings: dict[str, list[str]] = {}
    if os.path.isfile(skills_path):
        with open(skills_path, "r", encoding="utf-8") as fh:
            raw_s = json.load(fh)
            global_skills = raw_s.get("skills", {})
            skill_offerings = raw_s.get("skillOfferings", {})

    races_dir = os.path.join(safe_dmz, "races")
    races = (
        sorted(
            d
            for d in os.listdir(races_dir)
            if os.path.isdir(os.path.join(races_dir, d)) and d.lower() not in IGNORED_SUBDIRS
        )
        if os.path.isdir(races_dir)
        else []
    )

    racas_map: dict[str, Any] = {}
    total_forms = 0
    for race in races:
        race_payload, count = _read_race_entry(
            races_dir, race, global_skills, translations, skill_offerings=skill_offerings
        )
        racas_map[race] = race_payload
        total_forms += count

    global_forms_dir = os.path.join(safe_dmz, "forms")
    universal_map: dict[str, Any] = {}
    if os.path.isdir(global_forms_dir):
        for fname in sorted(os.listdir(global_forms_dir)):
            if not is_valid_form_json_file(fname):
                continue
            stem = fname[:-5]
            fpath = os.path.join(global_forms_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as fh:
                    fdata = json.load(fh)
            except (OSError, json.JSONDecodeError):
                continue

            ftype = str(fdata.get("formType") or stem)
            forms_dict = fdata.get("forms", {})
            if not isinstance(forms_dict, dict):
                continue

            u_forms: list[dict[str, Any]] = []
            for form_id, fprops in forms_dict.items():
                lvl = int(fprops.get("unlockOnSkillLevel", 1))
                tp_num, buy_master, m_id, m_nome = _resolve_tp_and_master(
                    {},
                    global_skills,
                    ftype,
                    stem,
                    form_id,
                    lvl,
                    skill_offerings=skill_offerings,
                )
                disp = _resolve_display_name(translations, "stack", stem, form_id)
                u_forms.append(
                    _build_form_entry(
                        form_id=form_id,
                        display_name=disp,
                        group_key=stem,
                        form_type=ftype,
                        level=lvl,
                        tp_num=tp_num,
                        buy_from_master=buy_master,
                        fprops=fprops,
                        is_universal=True,
                        mestre=m_id,
                        mestre_nome=m_nome,
                    )
                )

            if u_forms:
                universal_map[stem] = {
                    "arquivo": fname,
                    "tipo": ftype,
                    "formas": u_forms,
                }

    catalog: dict[str, Any] = {
        "titulo": "Dragon Mine Z - Guia Completo de Transformações, Custos de TP e Multiplicadores de BP",
        "versao_modpack": "Dragon Mine Z RPG 1.20.1",
        "caminho_modpack": "",
        "total_racas": len(races),
        "total_transformacoes": total_forms,
        "racas": racas_map,
        "formas_universais_e_stack": universal_map,
    }
    catalog["opcoes_sagas"] = extract_modpack_sagas(
        inferred_instance, translations, catalog
    )
    catalog["opcoes_mestres"] = [
        {"id": m_id, "nome": m_name}
        for m_id, m_name in sorted(MASTER_FRIENDLY_NAMES.items(), key=lambda x: x[1])
    ]
    return catalog


def load_catalog_from_json(
    json_path: str, allowed_roots: list[str] | None = None
) -> dict[str, Any]:
    """Load an exported transformation catalog JSON and normalize missing fields."""
    safe_path = validate_allowed_path(json_path, allowed_roots=allowed_roots)
    with open(safe_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    result = copy.deepcopy(raw)
    result["caminho_modpack"] = ""
    for race_obj in result.get("racas", {}).values():
        for tree_obj in race_obj.get("arvores_de_transformacao", {}).values():
            tree_obj["formas"] = [
                _normalize_loaded_entry(f, is_universal=False)
                for f in tree_obj.get("formas", [])
            ]
    for grp_obj in result.get("formas_universais_e_stack", {}).values():
        grp_obj["formas"] = [
            _normalize_loaded_entry(f, is_universal=True)
            for f in grp_obj.get("formas", [])
        ]
    if not result.get("opcoes_sagas"):
        result["opcoes_sagas"] = extract_modpack_sagas(None, {}, result)
    result["opcoes_mestres"] = [
        {"id": m_id, "nome": m_name}
        for m_id, m_name in sorted(MASTER_FRIENDLY_NAMES.items(), key=lambda x: x[1])
    ]
    return result


def save_catalog_to_json(
    catalog: dict[str, Any],
    json_paths: list[str],
    allowed_roots: list[str] | None = None,
) -> list[str]:
    """Persist catalog JSON to one or more whitelisted file paths."""
    sanitized = {**catalog, "caminho_modpack": ""}
    written: list[str] = []
    for path in json_paths:
        if not path or not str(path).strip():
            continue
        safe_path = validate_allowed_path(path, allowed_roots=allowed_roots)
        atomic_save_json(safe_path, sanitized)
        written.append(safe_path)
    return written


def _apply_entry_to_raw_form(
    raw_form: dict[str, Any], entry: dict[str, Any]
) -> dict[str, Any]:
    """Return a new raw DMZ form dict updating edited stats while keeping visuals/shaders."""
    out = copy.deepcopy(entry.get("_raw_payload") or raw_form)
    out["unlockOnSkillLevel"] = int(entry["nivel_habilidade"])

    mults = entry["multiplicadores_detalhados"]
    out["strMultiplier"] = float(mults["forca_str"])
    out["pwrMultiplier"] = float(mults["poder_ki_pwr"])
    out["defMultiplier"] = float(mults["defesa_def"])
    out["skpMultiplier"] = float(mults["golpe_skp"])
    out["stmMultiplier"] = float(mults["estamina_stm"])
    out["vitMultiplier"] = float(mults["vitalidade_vit"])
    out["eneMultiplier"] = float(mults["energia_ene"])
    out["speedMultiplier"] = float(mults["velocidade_spd"])
    out["attackSpeed"] = float(mults["velocidade_ataque"])

    drenos = entry["drenos"]
    out["energyDrain"] = float(drenos["energia_ki"])
    out["staminaDrain"] = float(drenos["estamina"])
    out["healthDrain"] = float(drenos["vida"])
    out["staminaDrainMultiplier"] = float(drenos["mult_estamina_golpe"])
    out["formStackable"] = bool(drenos["acumulavel"])
    out["stackDrainMultiplier"] = float(drenos["mult_dreno_stack"])
    if "stackOnMastery" in out:
        out["stackOnMastery"] = 0.0 if bool(drenos["acumulavel"]) else 100.0

    maestria = entry["maestria"]
    out["maxMastery"] = float(maestria["maestria_maxima"])
    out["masteryPerHitDealt"] = float(maestria["ganho_golpe_dado"])
    out["masteryPerHitReceived"] = float(maestria["ganho_dano_recebido"])
    out["passiveMasteryEveryFiveSeconds"] = float(maestria["ganho_passivo_5s"])
    out["maxCostMultiplier"] = float(maestria["mult_custo_maestria_max"])
    out["maxStatsMultiplier"] = float(maestria["mult_status_maestria_max"])
    out["instantTransformOnMastery"] = float(maestria["maestria_transf_instantanea"])

    reqs = entry["requisitos"]
    out["requiredDMZLevel"] = int(reqs["nivel_dmz_minimo"])
    out["levelRequisite"] = int(reqs["nivel_requisito"])
    out["sagaRequisite"] = str(reqs["saga"] or "")
    out["formRequisite"] = str(reqs["forma_previa"] or "")
    out["incompatibleWith"] = list(reqs["incompativel_com"])

    vis = entry.get("visual", {})
    if vis.get("cor_aura"):
        raw_aura = str(vis["cor_aura"]).strip()
        if raw_aura and not raw_aura.startswith("#") and len(raw_aura) in (3, 6, 8):
            raw_aura = "#" + raw_aura
        out["auraColor"] = raw_aura
    if vis.get("cor_cabelo"):
        raw_hair = str(vis["cor_cabelo"]).strip()
        if raw_hair and not raw_hair.startswith("#") and len(raw_hair) in (3, 6, 8):
            raw_hair = "#" + raw_hair
        out["hairColor"] = raw_hair
    if vis.get("cor_cabelo_secundaria"):
        raw_sh = str(vis["cor_cabelo_secundaria"]).strip()
        if raw_sh and not raw_sh.startswith("#") and len(raw_sh) in (3, 6, 8):
            raw_sh = "#" + raw_sh
        out["secondaryHairColor"] = raw_sh
    if vis.get("tipo_cabelo"):
        out["hairType"] = str(vis["tipo_cabelo"]).strip()
    if vis.get("tipo_modelo"):
        out["modelType"] = str(vis["tipo_modelo"]).strip()
    if "brilho_emissivo" in vis:
        out["emissive"] = bool(vis["brilho_emissivo"])
    if vis.get("cor_olho_1"):
        raw_e1 = str(vis["cor_olho_1"]).strip()
        if raw_e1 and not raw_e1.startswith("#") and len(raw_e1) in (3, 6, 8):
            raw_e1 = "#" + raw_e1
        out["eyeColor1"] = raw_e1
    if vis.get("cor_olho_2"):
        raw_e2 = str(vis["cor_olho_2"]).strip()
        if raw_e2 and not raw_e2.startswith("#") and len(raw_e2) in (3, 6, 8):
            raw_e2 = "#" + raw_e2
        out["eyeColor2"] = raw_e2
    if vis.get("cor_pele"):
        raw_sk = str(vis["cor_pele"]).strip()
        if raw_sk and not raw_sk.startswith("#") and len(raw_sk) in (3, 6, 8):
            raw_sk = "#" + raw_sk
        out["skinColor"] = raw_sk
    if "escala" in vis:
        out["modelScale"] = float(vis["escala"])
    if "raios" in vis and isinstance(vis["raios"], dict):
        out["lightning"] = copy.deepcopy(vis["raios"])
    if "manto" in vis and isinstance(vis["manto"], dict):
        out["cloak"] = copy.deepcopy(vis["manto"])

    return out


def _create_raw_form_scaffold(entry: dict[str, Any]) -> dict[str, Any]:
    """Generate a valid raw Dragon Mine Z form dict structure for a newly created form."""
    vis = entry.get("visual", {})
    mults = entry.get("multiplicadores_detalhados", {})
    drenos = entry.get("drenos", {})
    maestria = entry.get("maestria", {})
    reqs = entry.get("requisitos", {})

    aura = str(vis.get("cor_aura", "")).strip()
    if aura and not aura.startswith("#") and len(aura) in (3, 6, 8):
        aura = "#" + aura
    hair = str(vis.get("cor_cabelo", "")).strip()
    if hair and not hair.startswith("#") and len(hair) in (3, 6, 8):
        hair = "#" + hair

    return {
        "name": entry.get("id", "custom_form"),
        "unlockOnSkillLevel": int(entry.get("nivel_habilidade", 1)),
        "auraColor": aura or "#FFFFFF",
        "hairColor": hair or "#FFFFFF",
        "hairType": str(vis.get("tipo_cabelo", "base")),
        "modelType": str(vis.get("tipo_modelo", "player")),
        "outlineShader": {"enabled": False, "primaryColor": "#FFFFFF"},
        "strMultiplier": float(mults.get("forca_str", 1.0)),
        "pwrMultiplier": float(mults.get("poder_ki_pwr", 1.0)),
        "defMultiplier": float(mults.get("defesa_def", 1.0)),
        "skpMultiplier": float(mults.get("golpe_skp", 1.0)),
        "stmMultiplier": float(mults.get("estamina_stm", 1.0)),
        "vitMultiplier": float(mults.get("vitalidade_vit", 1.0)),
        "eneMultiplier": float(mults.get("energia_ene", 1.0)),
        "speedMultiplier": float(mults.get("velocidade_spd", 1.0)),
        "attackSpeed": float(mults.get("velocidade_ataque", 1.0)),
        "staminaDrainMultiplier": float(drenos.get("mult_estamina_golpe", 1.0)),
        "energyDrain": float(drenos.get("energia_ki", 0.0)),
        "staminaDrain": float(drenos.get("estamina", 0.0)),
        "healthDrain": float(drenos.get("vida", 0.0)),
        "formStackable": bool(drenos.get("acumulavel", True)),
        "stackDrainMultiplier": float(drenos.get("mult_dreno_stack", 2.0)),
        "maxMastery": float(maestria.get("maestria_maxima", 100.0)),
        "masteryPerHitDealt": float(maestria.get("ganho_golpe_dado", 0.025)),
        "masteryPerHitReceived": float(maestria.get("ganho_dano_recebido", 0.025)),
        "passiveMasteryEveryFiveSeconds": float(maestria.get("ganho_passivo_5s", 0.01)),
        "maxCostMultiplier": float(maestria.get("mult_custo_maestria_max", 0.75)),
        "maxStatsMultiplier": float(maestria.get("mult_status_maestria_max", 1.0)),
        "instantTransformOnMastery": float(
            maestria.get("maestria_transf_instantanea", 40.0)
        ),
        "requiredDMZLevel": int(reqs.get("nivel_dmz_minimo", 1)),
        "levelRequisite": int(reqs.get("nivel_requisito", 0)),
        "sagaRequisite": str(reqs.get("saga") or ""),
        "formRequisite": str(reqs.get("forma_previa") or ""),
        "incompatibleWith": list(reqs.get("incompativel_com", [])),
    }


def _sync_race_files(
    safe_dmz: str,
    r_key: str,
    r_obj: dict[str, Any],
) -> int:
    race_dir = os.path.join(safe_dmz, "races", r_key)
    if not os.path.isdir(race_dir):
        return 0

    updated = 0
    char_path = os.path.join(race_dir, "character.json")
    char_doc: dict[str, Any] | None = None
    if os.path.isfile(char_path):
        with open(char_path, "r", encoding="utf-8") as fh:
            char_doc = json.load(fh)
    char_modified = False

    for t_key, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
        fname = t_obj.get("arquivo") or f"{t_key}.json"
        fpath = validate_allowed_path(
            os.path.join(race_dir, "forms", fname), allowed_roots=[safe_dmz]
        )
        raw_tree: dict[str, Any] = {}
        if os.path.isfile(fpath):
            with open(fpath, "r", encoding="utf-8") as fh:
                raw_tree = json.load(fh)
        else:
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            raw_tree = {
                "configVersion": "2.2.1",
                "groupName": t_key,
                "formType": t_obj.get("tipo_habilidade", t_key),
                "forms": {},
            }
        raw_forms = dict(raw_tree.get("forms", {}))
        tree_changed = False
        current_catalog_ids = set()
        for entry in t_obj.get("formas", []):
            fid = entry["id"]
            current_catalog_ids.add(fid)
            if fid in raw_forms:
                new_raw = _apply_entry_to_raw_form(raw_forms[fid], entry)
                if new_raw != raw_forms[fid]:
                    raw_forms[fid] = new_raw
                    tree_changed = True
            else:
                raw_forms[fid] = _create_raw_form_scaffold(entry)
                tree_changed = True

        for existing_fid in list(raw_forms.keys()):
            if existing_fid not in current_catalog_ids:
                del raw_forms[existing_fid]
                tree_changed = True

        if tree_changed or not os.path.isfile(fpath):
            atomic_save_json(fpath, {**raw_tree, "forms": raw_forms})
            updated += 1

        if char_doc is not None:
            fsc = dict(char_doc.get("formSkillsCosts", {}))
            for entry in t_obj.get("formas", []):
                lvl = int(entry["nivel_habilidade"])
                if lvl <= 0:
                    continue
                tp_num = int(entry["custo_tp_numerico"])
                buy_master = bool(entry.get("comprar_no_mestre", False))
                skill_key = next(
                    (
                        k
                        for k in (entry["tipo_habilidade"], t_key, entry["id"])
                        if k and k in fsc
                    ),
                    entry["tipo_habilidade"] or t_key,
                )
                if skill_key not in fsc and tp_num < 0 and not buy_master:
                    continue
                cur_item = fsc.get(
                    skill_key, {"buyFromMaster": buy_master, "prices": []}
                )
                if isinstance(cur_item, list):
                    prices = list(cur_item)
                    new_item: Any = {"buyFromMaster": buy_master, "prices": prices}
                else:
                    prices = list(cur_item.get("prices", []))
                    new_item = {
                        **cur_item,
                        "buyFromMaster": buy_master,
                        "prices": prices,
                    }
                while len(prices) < lvl:
                    prices.append(-1)
                if prices[lvl - 1] != tp_num or cur_item != new_item:
                    prices[lvl - 1] = tp_num
                    fsc[skill_key] = new_item
                    char_modified = True
            if char_modified:
                char_doc = {**char_doc, "formSkillsCosts": fsc}

    if char_doc is not None and char_modified:
        atomic_save_json(char_path, char_doc)
        updated += 1

    return updated


def apply_catalog_to_modpack(
    catalog: dict[str, Any],
    dmz_config_dir: str,
    allowed_roots: list[str] | None = None,
    create_backup: bool = True,
) -> dict[str, Any]:
    """Write all catalog edits directly into DragonMineZ config files safely.
    Backups are created as a compressed .zip inside studio backups directory,
    leaving ZERO backup artifacts inside the modpack directory.
    """
    roots = (
        allowed_roots
        if allowed_roots is not None
        else [dmz_config_dir, *default_allowed_roots()]
    )
    safe_dmz = validate_allowed_path(dmz_config_dir, allowed_roots=roots)

    # Collect files that could be changed for .zip backup
    files_to_backup: list[str] = []
    for r_key, r_obj in catalog.get("racas", {}).items():
        race_dir = os.path.join(safe_dmz, "races", r_key)
        cp = os.path.join(race_dir, "character.json")
        if os.path.isfile(cp):
            files_to_backup.append(cp)
        for t_key, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
            fname = t_obj.get("arquivo") or f"{t_key}.json"
            fp = os.path.join(race_dir, "forms", fname)
            if os.path.isfile(fp):
                files_to_backup.append(fp)
    for g_key, g_obj in catalog.get("formas_universais_e_stack", {}).items():
        fname = g_obj.get("arquivo") or f"{g_key}.json"
        fp = os.path.join(safe_dmz, "forms", fname)
        if os.path.isfile(fp):
            files_to_backup.append(fp)
    sp = os.path.join(safe_dmz, "skills.json")
    if os.path.isfile(sp):
        files_to_backup.append(sp)

    backup_dir = get_backups_dir()
    backup_file: str | None = None
    if create_backup and files_to_backup:
        backup_file = create_modpack_backup_zip(
            files_to_backup, dmz_root=safe_dmz, backups_dir=backup_dir
        )

    updated_files = 0
    for r_key, r_obj in catalog.get("racas", {}).items():
        updated_files += _sync_race_files(safe_dmz, r_key, r_obj)

    skills_path = os.path.join(safe_dmz, "skills.json")
    skills_doc: dict[str, Any] | None = None
    if os.path.isfile(skills_path):
        with open(skills_path, "r", encoding="utf-8") as fh:
            skills_doc = json.load(fh)
    skills_modified = False

    for g_key, g_obj in catalog.get("formas_universais_e_stack", {}).items():
        fname = g_obj.get("arquivo") or f"{g_key}.json"
        fpath = validate_allowed_path(
            os.path.join(safe_dmz, "forms", fname), allowed_roots=[safe_dmz]
        )
        raw_grp: dict[str, Any] = {}
        if os.path.isfile(fpath):
            with open(fpath, "r", encoding="utf-8") as fh:
                raw_grp = json.load(fh)
        else:
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            raw_grp = {
                "configVersion": "2.2.1",
                "groupName": g_key,
                "formType": g_obj.get("tipo", g_key),
                "forms": {},
            }
        raw_forms = dict(raw_grp.get("forms", {}))
        grp_changed = False
        current_u_ids = set()
        for entry in g_obj.get("formas", []):
            fid = entry["id"]
            current_u_ids.add(fid)
            if fid in raw_forms:
                new_raw = _apply_entry_to_raw_form(raw_forms[fid], entry)
                if new_raw != raw_forms[fid]:
                    raw_forms[fid] = new_raw
                    grp_changed = True
            else:
                raw_forms[fid] = _create_raw_form_scaffold(entry)
                grp_changed = True

        for existing_fid in list(raw_forms.keys()):
            if existing_fid not in current_u_ids:
                del raw_forms[existing_fid]
                grp_changed = True

        if grp_changed or not os.path.isfile(fpath):
            atomic_save_json(fpath, {**raw_grp, "forms": raw_forms})
            updated_files += 1

        if skills_doc is not None:
            skills_map = dict(skills_doc.get("skills", {}))
            for entry in g_obj.get("formas", []):
                lvl = int(entry["nivel_habilidade"])
                tp_num = int(entry["custo_tp_numerico"])
                if lvl <= 0 or tp_num < 0:
                    continue
                s_key = next(
                    (
                        k
                        for k in (g_key, entry["tipo_habilidade"], entry["id"])
                        if k and k in skills_map
                    ),
                    g_key or entry["tipo_habilidade"],
                )
                if s_key:
                    s_entry = dict(
                        skills_map.get(s_key, {"costs": [], "allowedRaces": []})
                    )
                    costs = list(s_entry.get("costs", []))
                    while len(costs) < lvl:
                        costs.append(-1)
                    if costs[lvl - 1] != tp_num or s_key not in skills_map:
                        costs[lvl - 1] = tp_num
                        s_entry["costs"] = costs
                        skills_map[s_key] = s_entry
                        skills_modified = True
            if skills_modified:
                skills_doc = {**skills_doc, "skills": skills_map}

    if skills_doc is not None:
        skill_offerings = dict(skills_doc.get("skillOfferings", {}))
        offerings_changed = False

        # Ensure masters offer the skills in-game when buyFromMaster is enabled
        for r_obj in catalog.get("racas", {}).values():
            for t_key, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
                for entry in t_obj.get("formas", []):
                    m_id = str(entry.get("mestre") or "").strip().lower()
                    if entry.get("comprar_no_mestre") and m_id:
                        s_key = entry.get("tipo_habilidade") or t_key or entry.get("id")
                        if m_id in skill_offerings:
                            cur_offs = list(skill_offerings[m_id])
                            if s_key not in cur_offs:
                                cur_offs.append(s_key)
                                skill_offerings[m_id] = cur_offs
                                offerings_changed = True
                        else:
                            skill_offerings[m_id] = [s_key]
                            offerings_changed = True

        for g_key, g_obj in catalog.get("formas_universais_e_stack", {}).items():
            for entry in g_obj.get("formas", []):
                m_id = str(entry.get("mestre") or "").strip().lower()
                if entry.get("comprar_no_mestre") and m_id:
                    s_key = entry.get("tipo_habilidade") or g_key or entry.get("id")
                    if m_id in skill_offerings:
                        cur_offs = list(skill_offerings[m_id])
                        if s_key not in cur_offs:
                            cur_offs.append(s_key)
                            skill_offerings[m_id] = cur_offs
                            offerings_changed = True
                    else:
                        skill_offerings[m_id] = [s_key]
                        offerings_changed = True

        if offerings_changed:
            skills_doc["skillOfferings"] = skill_offerings
            skills_modified = True

    if skills_doc is not None and skills_modified:
        atomic_save_json(skills_path, skills_doc)
        updated_files += 1

    return {
        "arquivos_atualizados": updated_files,
        "pasta_backup": backup_dir if updated_files > 0 else None,
        "arquivo_backup": backup_file,
        "caminho_modpack": safe_dmz,
    }


_ADDONS_CACHE: dict[str, tuple[float, list[dict[str, Any]]]] = {}


def scan_dmz_addons(instance_dir: str | None, force: bool = False) -> list[dict[str, Any]]:
    """Scan mods directory for DMZ addons and return structured status and metadata."""
    if not instance_dir or not os.path.isdir(instance_dir):
        return []
    mods_dir = os.path.join(instance_dir, "mods")
    if not os.path.isdir(mods_dir):
        return []

    try:
        mtime = os.path.getmtime(mods_dir)
    except OSError:
        mtime = 0.0

    if not force and mods_dir in _ADDONS_CACHE:
        cached_mtime, cached_list = _ADDONS_CACHE[mods_dir]
        if cached_mtime == mtime:
            return copy.deepcopy(cached_list)

    addons: list[dict[str, Any]] = []
    dmz_keywords = (
        "dragon",
        "dmz",
        "kai",
        "ragnarok",
        "unofficial",
        "ultra",
        "sparking",
        "super",
        "customforms",
        "bleed",
    )

    for fname in sorted(os.listdir(mods_dir)):
        low = fname.lower()
        is_jar = low.endswith(".jar")
        is_disabled = low.endswith(".jar.disabled")
        if not (is_jar or is_disabled):
            continue

        fpath = os.path.join(mods_dir, fname)
        try:
            size_mb = round(os.path.getsize(fpath) / (1024 * 1024), 2)
        except OSError:
            size_mb = 0.0

        enabled = is_jar
        mod_id = fname.split("-")[0].replace(".jar", "").replace(".disabled", "")
        display_name = mod_id.replace("_", " ").title()
        version = ""
        authors = ""
        description = ""
        is_dmz_addon = any(k in low for k in dmz_keywords)
        contributed_forms: list[str] = []

        try:
            with zipfile.ZipFile(fpath, "r") as zf:
                namelist = zf.namelist()
                for n in namelist:
                    if "dragonminez" in n.lower() or "dmz" in n.lower():
                        is_dmz_addon = True
                    if n.endswith("mods.toml"):
                        toml_content = zf.read(n).decode(
                            "utf-8", errors="ignore"
                        )
                        m_id = re.search(
                            r'modId\s*=\s*["\']([^"\']+)["\']', toml_content
                        )
                        if m_id:
                            mod_id = m_id.group(1)
                        m_name = re.search(
                            r'displayName\s*=\s*["\']([^"\']+)["\']',
                            toml_content,
                        )
                        if m_name:
                            display_name = m_name.group(1)
                        m_ver = re.search(
                            r'version\s*=\s*["\']([^"\']+)["\']', toml_content
                        )
                        if m_ver:
                            version = m_ver.group(1)
                        m_auth = re.search(
                            r'authors\s*=\s*["\']([^"\']+)["\']', toml_content
                        )
                        if m_auth:
                            authors = m_auth.group(1)
                        m_desc = re.search(
                            r'description\s*=\s*[\'"]{3}([\s\S]*?)[\'"]{3}',
                            toml_content,
                        ) or re.search(
                            r'description\s*=\s*["\']([^"\']+)["\']',
                            toml_content,
                        )
                        if m_desc:
                            description = m_desc.group(1).strip()
                    if "forms/" in n and n.endswith(".json"):
                        contributed_forms.append(os.path.basename(n)[:-5])
        except (OSError, zipfile.BadZipFile):
            pass

        if is_dmz_addon:
            addons.append(
                {
                    "mod_id": mod_id,
                    "display_name": display_name,
                    "filename": fname,
                    "version": version or "1.0.0",
                    "authors": authors or "Community",
                    "description": (
                        description[:160] + "..."
                        if len(description) > 160
                        else description
                    ),
                    "enabled": enabled,
                    "size_mb": size_mb,
                    "contributed_forms": sorted(set(contributed_forms)),
                }
            )

    _ADDONS_CACHE[mods_dir] = (mtime, copy.deepcopy(addons))
    return addons


def toggle_addon_mod(
    instance_dir: str,
    filename: str,
    enable: bool,
    allowed_roots: list[str] | None = None,
) -> dict[str, Any]:
    """Safely enable or disable a mod by renaming between .jar and .jar.disabled."""
    safe_inst = validate_allowed_path(instance_dir, allowed_roots=allowed_roots)
    mods_dir = os.path.join(safe_inst, "mods")
    _ADDONS_CACHE.pop(mods_dir, None)
    if not os.path.isdir(mods_dir):
        raise FileNotFoundError(f"Pasta de mods não encontrada: {mods_dir}")

    clean_fname = os.path.basename(filename)
    cur_path = os.path.join(mods_dir, clean_fname)
    if not os.path.isfile(cur_path):
        raise FileNotFoundError(
            f"Arquivo do mod não encontrado: {clean_fname}"
        )

    if enable:
        if clean_fname.endswith(".jar.disabled"):
            new_fname = clean_fname[:-9]
            new_path = os.path.join(mods_dir, new_fname)
            os.rename(cur_path, new_path)
            return {"ok": True, "filename": new_fname, "enabled": True}
        return {"ok": True, "filename": clean_fname, "enabled": True}
    else:
        if clean_fname.endswith(".jar"):
            new_fname = clean_fname + ".disabled"
            new_path = os.path.join(mods_dir, new_fname)
            os.rename(cur_path, new_path)
            return {"ok": True, "filename": new_fname, "enabled": False}
        return {"ok": True, "filename": clean_fname, "enabled": False}
