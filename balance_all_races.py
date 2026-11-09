"""Comprehensive lore-accurate balancing script for Dragon Mine Z transformations.

Uses the user's Saiyan configuration as the reference progression curve:
1. Saga-gated forms vs. Free-unlock (No Saga) forms:
   - Saga-gated forms reward story progression with stronger multipliers and better TP efficiency.
   - Requirement-free (no saga) forms have lower multipliers early/mid-game or require much higher TP.
2. Trade-off philosophy ("Se é boa em algo, é ruim em outra coisa"):
   - Every race and transformation branch has clear strengths and weaknesses across STR, PWR, DEF, SKP, and Drains.
3. Secondary stats protection:
   - Keeps STM, VIT, ENE, SPD, and ATK at 1.0x by default, only applying subtle lore-accurate trade-offs
     (e.g. 0.68x-0.80x SPD on Giants/Grade 3, or 1.10x-1.35x SPD on Speedsters/Assassins/UI).
"""

from __future__ import annotations

import copy
import json
import os
import shutil
from typing import Any

from dmz_form_editor_core import (
    DEFAULT_DESKTOP_JSON,
    DEFAULT_DMZ_CONFIG_DIR,
    DEFAULT_INSTANCE_JSON,
    format_bp_string,
    format_tp_display,
)
from dmz_form_editor_io import (
    apply_catalog_to_modpack,
    load_catalog_from_json,
    load_catalog_from_modpack,
    save_catalog_to_json,
)


def _set_form(
    form: dict[str, Any],
    *,
    tp: int | None = None,
    lvl: int | None = None,
    master: bool | None = None,
    str_m: float | None = None,
    pwr_m: float | None = None,
    def_m: float | None = None,
    skp_m: float | None = None,
    stm_m: float = 1.0,
    vit_m: float = 1.0,
    ene_m: float = 1.0,
    spd_m: float = 1.0,
    atk_m: float = 1.0,
    saga: str | None = "__KEEP__",
    prev: str | None = "__KEEP__",
    drain_ki: float | None = None,
    drain_stm: float | None = None,
    drain_hp: float | None = None,
    stackable: bool | None = None,
    stack_drain: float | None = None,
    incomp: list[str] | None = None,
) -> None:
    if tp is not None:
        form["custo_tp_numerico"] = int(tp)
        form["custo_tp"] = format_tp_display(int(tp))
    if lvl is not None:
        form["nivel_habilidade"] = int(lvl)
    if master is not None:
        form["comprar_no_mestre"] = bool(master)

    m = form["multiplicadores_detalhados"]
    if str_m is not None:
        m["forca_str"] = round(float(str_m), 3)
    if pwr_m is not None:
        m["poder_ki_pwr"] = round(float(pwr_m), 3)
    if def_m is not None:
        m["defesa_def"] = round(float(def_m), 3)
    if skp_m is not None:
        m["golpe_skp"] = round(float(skp_m), 3)
    m["estamina_stm"] = round(float(stm_m), 3)
    m["vitalidade_vit"] = round(float(vit_m), 3)
    m["energia_ene"] = round(float(ene_m), 3)
    m["velocidade_spd"] = round(float(spd_m), 3)
    m["velocidade_ataque"] = round(float(atk_m), 3)

    form["multiplicador_numerico_base"] = m["forca_str"]
    form["multiplicador_bp"] = format_bp_string(m)

    req = form["requisitos"]
    if saga != "__KEEP__":
        req["saga"] = saga
    if prev != "__KEEP__":
        req["forma_previa"] = prev
    if incomp is not None:
        req["incompativel_com"] = list(incomp)

    dr = form["drenos"]
    if drain_ki is not None:
        dr["energia_ki"] = round(float(drain_ki), 4)
    if drain_stm is not None:
        dr["estamina"] = round(float(drain_stm), 4)
    if drain_hp is not None:
        dr["vida"] = round(float(drain_hp), 4)
    if stackable is not None:
        dr["acumulavel"] = bool(stackable)
    if stack_drain is not None:
        dr["mult_dreno_stack"] = round(float(stack_drain), 3)


def _find_form(
    catalog: dict[str, Any], race: str, tree: str, form_id: str
) -> dict[str, Any]:
    t_obj = catalog["racas"][race]["arvores_de_transformacao"][tree]
    for f in t_obj["formas"]:
        if f["id"] == form_id:
            return f
    raise KeyError(f"Form not found: {race}.{tree}.{form_id}")


def _sync_race_slot_prices(race_obj: dict[str, Any]) -> None:
    """Ensure forms sharing (tipo_habilidade, nivel_habilidade) within a race have identical TP."""
    slot_tp: dict[tuple[str, int], int] = {}
    for t_obj in race_obj["arvores_de_transformacao"].values():
        for f in t_obj["formas"]:
            lvl = int(f["nivel_habilidade"])
            tp = int(f["custo_tp_numerico"])
            if lvl > 0 and tp >= 0:
                slot_tp[(f["tipo_habilidade"], lvl)] = tp

    for t_obj in race_obj["arvores_de_transformacao"].values():
        for f in t_obj["formas"]:
            key = (f["tipo_habilidade"], int(f["nivel_habilidade"]))
            if key in slot_tp:
                f["custo_tp_numerico"] = slot_tp[key]
                f["custo_tp"] = format_tp_display(slot_tp[key])


def _clean_saiyan_secondary_stats_and_priceless(cat: dict[str, Any]) -> None:
    """Preserve user's Saiyan STR/PWR/DEF/SKP & TP, fix Priceless (-1) & accidental STM/ENE/SPD inflation."""
    saiyan = cat["racas"]["saiyan"]
    for t_key, t_obj in saiyan["arvores_de_transformacao"].items():
        for f in t_obj["formas"]:
            fid = f["id"]
            m = f["multiplicadores_detalhados"]
            # Fix SKP=1.0 typo and Priceless on supersaiyan4fp / supersaiyan5daima / oozaru.supersaiyan5
            if t_key == "supersaiyan" and fid == "supersaiyan4fp":
                m["golpe_skp"] = 17.0
                f["custo_tp_numerico"] = 450000
                f["custo_tp"] = 450000
                f["requisitos"]["saga"] = "gt_saga:41"
            elif fid in ("supersaiyan5daima", "supersaiyan5") and f["custo_tp_numerico"] < 0:
                f["custo_tp_numerico"] = 450000
                f["custo_tp"] = 450000

            # Normalize secondary stats (STM, VIT, ENE, SPD, ATK) so they don't give broken advantages
            m["estamina_stm"] = 1.0
            m["vitalidade_vit"] = 1.0
            m["energia_ene"] = 1.0

            if t_key == "oozaru" and fid == "oozaru":
                m["velocidade_spd"] = 0.8
                m["velocidade_ataque"] = 0.85
            elif t_key == "oozaru" and fid == "goldenoozaru":
                m["forca_str"] = 14.0
                m["defesa_def"] = 14.0
                m["poder_ki_pwr"] = 10.0
                m["golpe_skp"] = 10.0
                m["velocidade_spd"] = 0.82
                m["velocidade_ataque"] = 0.85
            elif t_key == "ssgrades" and fid == "supersaiyangrade2":
                m["velocidade_spd"] = 0.92
                m["velocidade_ataque"] = 0.95
            elif t_key == "ssgrades" and fid == "supersaiyangrade3":
                m["velocidade_spd"] = 0.72
                m["velocidade_ataque"] = 0.75
            elif t_key == "ultrainstinct":
                # Keep user's exact STR/PWR/DEF/SKP, set sane high speed instead of 150x teleport
                if fid == "sign":
                    m["velocidade_spd"] = 1.3
                    m["velocidade_ataque"] = 1.2
                elif fid == "mastered":
                    m["velocidade_spd"] = 1.4
                    m["velocidade_ataque"] = 1.3
                elif fid == "true":
                    m["velocidade_spd"] = 1.45
                    m["velocidade_ataque"] = 1.35
            elif t_key == "ultraego":
                m["velocidade_spd"] = 1.15
                m["velocidade_ataque"] = 1.1
            else:
                m["velocidade_spd"] = round(min(max(float(m["velocidade_spd"]), 0.7), 1.25), 3)
                m["velocidade_ataque"] = round(min(max(float(m["velocidade_ataque"]), 0.7), 1.2), 3)

            f["multiplicador_numerico_base"] = m["forca_str"]
            f["multiplicador_bp"] = format_bp_string(m)


def _sync_racial_ui_and_ue(cat: dict[str, Any]) -> None:
    """Sync Ultra Ego & Ultra Instinct across all 22 races to match Saiyan's balanced setup."""
    for r_obj in cat["racas"].values():
        trees = r_obj["arvores_de_transformacao"]
        if "ultraego" in trees:
            for f in trees["ultraego"]["formas"]:
                if f["id"] == "mastered":
                    # Destroyer: Huge STR/PWR/DEF/SKP (25x), requires Granolah Saga (Vegeta's Ego) or 1.5M TP
                    _set_form(
                        f,
                        tp=1500000,
                        str_m=25.0,
                        pwr_m=25.0,
                        def_m=25.0,
                        skp_m=25.0,
                        spd_m=1.15,
                        atk_m=1.1,
                        drain_stm=0.06,
                    )
        if "ultrainstinct" in trees:
            for f in trees["ultrainstinct"]["formas"]:
                if f["id"] == "sign":
                    _set_form(
                        f,
                        tp=6000000,
                        str_m=6.0,
                        pwr_m=5.0,
                        def_m=33.0,
                        skp_m=15.0,
                        spd_m=1.3,
                        atk_m=1.2,
                        drain_stm=0.018,
                    )
                elif f["id"] == "mastered":
                    _set_form(
                        f,
                        tp=7000000,
                        str_m=12.0,
                        pwr_m=12.0,
                        def_m=40.0,
                        skp_m=12.0,
                        spd_m=1.4,
                        atk_m=1.3,
                        drain_stm=0.032,
                    )
                elif f["id"] == "true":
                    _set_form(
                        f,
                        tp=8000000,
                        str_m=20.0,
                        pwr_m=10.0,
                        def_m=50.0,
                        skp_m=10.0,
                        spd_m=1.45,
                        atk_m=1.35,
                        drain_ki=0.055,
                        drain_stm=0.045,
                    )


def _balance_half_saiyan(cat: dict[str, Any]) -> None:
    """Half-Saiyan (Gohan/Trunks): Explosive Ki & Emotion (High PWR/SKP/STR, lower DEF)."""
    r = "half_saiyan"
    # ssgrades (No saga on SSJ1 -> worse stats; Grade 2/3 require Android Saga)
    _set_form(_find_form(cat, r, "ssgrades", "supersaiyan"), tp=60000, str_m=2.6, pwr_m=2.8, def_m=2.1, skp_m=2.8, saga=None, drain_ki=0.08)
    _set_form(_find_form(cat, r, "ssgrades", "supersaiyangrade2"), tp=140000, str_m=4.2, pwr_m=4.4, def_m=3.2, skp_m=4.4, spd_m=0.92, atk_m=0.95, saga="android_saga:12", drain_ki=0.14)
    _set_form(_find_form(cat, r, "ssgrades", "supersaiyangrade3"), tp=220000, str_m=6.2, pwr_m=6.0, def_m=4.2, skp_m=6.0, spd_m=0.72, atk_m=0.75, saga="android_saga:12", drain_ki=0.45)

    # supersaiyan (Saga-gated: Cell Games -> Super Perfect Cell -> Buu Saga)
    _set_form(_find_form(cat, r, "supersaiyan", "supersaiyanmastered"), tp=70000, str_m=7.6, pwr_m=8.0, def_m=6.4, skp_m=8.0, saga="android_saga:13", drain_ki=0.03)
    _set_form(_find_form(cat, r, "supersaiyan", "supersaiyan2"), tp=90000, str_m=9.0, pwr_m=9.6, def_m=7.4, skp_m=9.8, spd_m=1.06, saga="android_saga:15", drain_ki=0.16)
    _set_form(_find_form(cat, r, "supersaiyan", "supersaiyan3"), tp=160000, str_m=13.0, pwr_m=13.8, def_m=10.2, skp_m=14.0, saga="buu_saga:23", drain_ki=0.34)

    # legendaryforms (No saga, pure TP like Saiyan's 250k/550k/825k: high STR/PWR, lower DEF)
    _set_form(_find_form(cat, r, "legendaryforms", "ikari"), tp=250000, str_m=6.5, pwr_m=6.2, def_m=4.8, skp_m=6.5, drain_ki=0.12)
    _set_form(_find_form(cat, r, "legendaryforms", "ssjhybrid"), tp=550000, str_m=12.8, pwr_m=12.5, def_m=9.5, skp_m=13.0, drain_ki=0.18)
    _set_form(_find_form(cat, r, "legendaryforms", "ssjfullpower"), tp=850000, str_m=20.0, pwr_m=19.5, def_m=15.0, skp_m=20.0, drain_ki=0.28)

    # godforms (No saga, matches Saiyan godforms Lvl 1 at 10M TP)
    _set_form(_find_form(cat, r, "godforms", "supersaiyangod"), tp=10000000, str_m=30.0, pwr_m=33.0, def_m=25.0, skp_m=33.0, spd_m=1.1, atk_m=1.05, drain_ki=0.16)


def _balance_human(cat: dict[str, Any]) -> None:
    """Human: Martial Arts Precision (High SKP/STR, lower DEF) & Infinite-Energy Cyborgs (0 drain, steady stats)."""
    r = "human"
    # superforms (Saga-gated Martial Artist progression)
    _set_form(_find_form(cat, r, "superforms", "buffed"), tp=40000, str_m=4.2, pwr_m=3.8, def_m=3.2, skp_m=4.5, spd_m=0.92, saga="classic_saga:12", drain_ki=0.08)
    _set_form(_find_form(cat, r, "superforms", "fullpower"), tp=65000, str_m=6.0, pwr_m=5.5, def_m=4.6, skp_m=6.5, saga="saiyan_saga:9", drain_ki=0.14)
    _set_form(_find_form(cat, r, "superforms", "overdrive"), tp=120000, str_m=8.8, pwr_m=8.2, def_m=6.5, skp_m=9.5, spd_m=1.06, saga="frieza_saga:10", drain_ki=0.32)
    _set_form(_find_form(cat, r, "superforms", "solaris"), tp=280000, str_m=13.5, pwr_m=13.0, def_m=10.5, skp_m=14.5, spd_m=1.08, saga="buu_saga:35", drain_ki=0.22)
    _set_form(_find_form(cat, r, "superforms", "supernova"), tp=550000, str_m=18.5, pwr_m=18.0, def_m=14.5, skp_m=20.0, spd_m=1.12, atk_m=1.08, saga="u7vsu6_saga:1", drain_ki=0.3)

    # androidforms (Cyborg path: 0 Ki drain advantage -> slightly lower STR/PWR, higher mechanical DEF)
    # Note: androidbase and superandroid share Lvl=1 in androidforms, so let's set androidbase Lvl=1 (90k) and superandroid Lvl=2 (180k), fusedandroid Lvl=3 (350k), superfusedandroid Lvl=4 (750k)
    _set_form(_find_form(cat, r, "androidforms", "androidbase"), lvl=1, tp=90000, str_m=5.0, pwr_m=5.2, def_m=5.6, skp_m=5.0, saga="android_saga:8", drain_ki=0.0)
    _set_form(_find_form(cat, r, "androidforms", "superandroid"), lvl=2, tp=180000, str_m=7.8, pwr_m=8.2, def_m=8.6, skp_m=7.8, saga="android_saga:13", drain_ki=0.0)
    _set_form(_find_form(cat, r, "androidforms", "fusedandroid"), lvl=3, tp=350000, str_m=11.5, pwr_m=12.0, def_m=12.8, skp_m=11.5, saga="movies_saga:22", drain_ki=0.0)
    _set_form(_find_form(cat, r, "androidforms", "superfusedandroid"), lvl=4, tp=750000, str_m=17.0, pwr_m=18.5, def_m=18.0, skp_m=18.5, saga="gt_saga:17", drain_ki=0.0)

    # legendaryforms (Tien's Four Witches / Shiyoken: No saga -> High multi-arm STR/SKP & ATK, low DEF, high Ki drain)
    _set_form(_find_form(cat, r, "legendaryforms", "shiyoken"), tp=150000, str_m=6.2, pwr_m=5.5, def_m=4.2, skp_m=6.5, atk_m=1.1, drain_ki=0.22)
    _set_form(_find_form(cat, r, "legendaryforms", "shin_shiyoken"), tp=400000, str_m=12.2, pwr_m=11.0, def_m=8.0, skp_m=12.8, atk_m=1.15, drain_ki=0.28)
    _set_form(_find_form(cat, r, "legendaryforms", "chou_shiyoken"), tp=850000, str_m=19.0, pwr_m=17.5, def_m=12.5, skp_m=20.0, atk_m=1.2, drain_ki=0.34)

    # thrallforms (Shadow Saga Master forms, matching Saiyan's corruptedforms)
    _set_form(_find_form(cat, r, "thrallforms", "majinthrall"), tp=120000, str_m=8.5, pwr_m=8.0, def_m=6.5, skp_m=8.5, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "thrallforms", "cybermercenary"), tp=250000, str_m=12.5, pwr_m=12.0, def_m=10.0, skp_m=13.0, saga="shadow_saga:4")
    _set_form(_find_form(cat, r, "thrallforms", "darkmasked"), tp=450000, str_m=16.5, pwr_m=16.0, def_m=13.0, skp_m=17.0, saga="shadow_saga:6")

    # Special Android/Majin/Uub forms
    _set_form(_find_form(cat, r, "majinandroidforms", "majinandroid"), tp=1250000, str_m=15.0, pwr_m=16.5, def_m=17.0, skp_m=16.0, saga="buu_saga:21", drain_ki=0.0)
    _set_form(_find_form(cat, r, "majuubstyle", "awakened"), tp=1750000, str_m=22.0, pwr_m=24.0, def_m=20.0, skp_m=24.0, saga="gt_saga:8", drain_ki=0.28)

    # gammaframeforms (Super Hero Movie Saga: Gamma 1 & Gamma 2 Core Breaker)
    _set_form(_find_form(cat, r, "gammaframeforms", "gammaframe"), tp=2500000, str_m=26.0, pwr_m=28.0, def_m=24.0, skp_m=28.0, spd_m=1.1, atk_m=1.06, saga="movies_saga:106")
    _set_form(_find_form(cat, r, "gammaframeforms", "majincircuit"), tp=2500000, str_m=27.0, pwr_m=29.0, def_m=28.0, skp_m=28.0, spd_m=1.08, atk_m=1.06, saga="movies_saga:106")
    _set_form(_find_form(cat, r, "gammaframeforms", "gammaoverdrive"), tp=4500000, str_m=42.0, pwr_m=46.0, def_m=28.0, skp_m=48.0, spd_m=1.16, atk_m=1.1, saga="movies_saga:107", drain_ki=0.4)

    # sageforms (No saga, pure TP 4.5M / 11M: Ki/Skill Masters, fragile DEF)
    _set_form(_find_form(cat, r, "sageforms", "spiritbombsage"), tp=4500000, str_m=26.0, pwr_m=34.0, def_m=24.0, skp_m=35.0, spd_m=1.06)
    _set_form(_find_form(cat, r, "sageforms", "craneascendant"), tp=11000000, str_m=40.0, pwr_m=55.0, def_m=30.0, skp_m=58.0, spd_m=1.15, atk_m=1.12)

    # fistforms (Endgame No-Saga 15M -> 70M TP: High STR & SKP, lower PWR & DEF)
    fist_tiers = [
        ("limitbreaker", 15000000, 38.0, 30.0, 30.0, 38.0),
        ("beyondhuman", 27500000, 70.0, 55.0, 55.0, 70.0),
        ("transcendent", 40000000, 102.0, 80.0, 80.0, 102.0),
        ("godfist", 55000000, 140.0, 110.0, 110.0, 140.0),
        ("divinemartialist", 70000000, 175.0, 140.0, 140.0, 175.0),
    ]
    for fid, tp, s_m, p_m, d_m, k_m in fist_tiers:
        _set_form(_find_form(cat, r, "fistforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=1.08, atk_m=1.05)


def _balance_namekian(cat: dict[str, Any]) -> None:
    """Namekian: Guardian Tank & Mystic Dragon Clan (High DEF & PWR, slower Giants, zero Priceless)."""
    r = "namekian"
    # Standalone giant tree
    _set_form(_find_form(cat, r, "giant", "giant"), tp=50000, str_m=4.5, pwr_m=2.0, def_m=5.0, skp_m=2.0, spd_m=0.75, atk_m=0.7, saga="classic_saga:51", drain_ki=0.09)

    # superforms (Fix Priceless -1 on Lvl 4 and separate levels cleanly: Lvl 1..6)
    _set_form(_find_form(cat, r, "superforms", "giant"), lvl=1, tp=55000, str_m=4.2, pwr_m=2.2, def_m=4.8, skp_m=2.2, spd_m=0.75, atk_m=0.7, saga="classic_saga:51", drain_ki=0.09)
    _set_form(_find_form(cat, r, "superforms", "fullpower"), lvl=1, tp=55000, str_m=5.4, pwr_m=5.8, def_m=6.5, skp_m=5.8, saga="frieza_saga:21", drain_ki=0.14)
    _set_form(_find_form(cat, r, "superforms", "supernamekian"), lvl=2, tp=110000, str_m=8.0, pwr_m=8.8, def_m=10.0, skp_m=8.8, saga="android_saga:108", drain_ki=0.2)
    _set_form(_find_form(cat, r, "superforms", "supernamekian2"), lvl=3, tp=220000, str_m=12.5, pwr_m=13.4, def_m=15.1, skp_m=13.0, saga="buu_saga:4", drain_ki=0.25)
    _set_form(_find_form(cat, r, "superforms", "dragonclan"), lvl=4, tp=350000, str_m=11.0, pwr_m=16.5, def_m=14.5, skp_m=16.5, saga="frieza_saga:105", drain_ki=0.24)
    _set_form(_find_form(cat, r, "superforms", "ultranamekian"), lvl=4, tp=350000, str_m=16.5, pwr_m=17.9, def_m=20.2, skp_m=17.5, saga="buu_saga:35", drain_ki=0.27)
    _set_form(_find_form(cat, r, "superforms", "orange"), lvl=5, tp=1100000, str_m=24.0, pwr_m=23.0, def_m=29.0, skp_m=23.0, vit_m=1.15, saga="movies_saga:109", drain_ki=0.2, drain_stm=0.12)
    _set_form(_find_form(cat, r, "primalnamekian", "primalnamekian"), lvl=6, tp=2250000, str_m=28.0, pwr_m=30.0, def_m=34.0, skp_m=30.0, saga="moro_saga:19", drain_ki=0.28)

    # divineforms (Saga-gated Awakening -> Orange -> Orange Giant -> Super Namekian God)
    _set_form(_find_form(cat, r, "divineforms", "potentialunleashed"), tp=400000, str_m=11.5, pwr_m=12.5, def_m=13.5, skp_m=12.5, saga="buu_saga:24", drain_ki=0.22)
    _set_form(_find_form(cat, r, "divineforms", "golden"), tp=1200000, str_m=25.0, pwr_m=25.0, def_m=30.0, skp_m=25.0, saga="movies_saga:109", drain_ki=0.28)
    _set_form(_find_form(cat, r, "divineforms", "awakenedgoldengiant"), tp=2200000, str_m=38.0, pwr_m=28.0, def_m=44.0, skp_m=28.0, spd_m=0.72, atk_m=0.65, saga="movies_saga:109", drain_ki=0.35)
    _set_form(_find_form(cat, r, "divineforms", "supernamekiangod"), tp=8000000, str_m=56.0, pwr_m=62.0, def_m=68.0, skp_m=62.0, spd_m=1.12, atk_m=1.08, saga="beerus_saga:5", drain_ki=0.32)

    # pureprogress (No-saga Orange Piccolo alternative at 5M / 7.5M TP)
    _set_form(_find_form(cat, r, "pureprogress", "orangepiccolo"), tp=5000000, str_m=35.0, pwr_m=35.0, def_m=42.0, skp_m=35.0, vit_m=1.15, drain_ki=0.18)
    _set_form(_find_form(cat, r, "pureprogress", "giantorangepiccolo"), tp=7500000, str_m=50.0, pwr_m=36.0, def_m=58.0, skp_m=36.0, vit_m=1.2, spd_m=0.72, atk_m=0.6, drain_ki=0.28)

    # legendaryforms (Lord Slug path - No saga: 200k / 450k / 900k TP)
    _set_form(_find_form(cat, r, "legendaryforms", "evilnamek"), tp=200000, str_m=6.0, pwr_m=5.8, def_m=6.5, skp_m=5.8, drain_ki=0.18)
    _set_form(_find_form(cat, r, "legendaryforms", "evilgiantnamek"), tp=450000, str_m=13.5, pwr_m=9.5, def_m=15.0, skp_m=9.5, spd_m=0.76, atk_m=0.72, drain_ki=0.25)
    _set_form(_find_form(cat, r, "legendaryforms", "buffednamek"), tp=900000, str_m=19.0, pwr_m=18.0, def_m=21.0, skp_m=18.5, drain_ki=0.24)

    # daimaoforms (King Piccolo Shadow Saga Master)
    _set_form(_find_form(cat, r, "daimaoforms", "demonkingmantle"), tp=180000, str_m=8.5, pwr_m=9.5, def_m=8.5, skp_m=9.5, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "daimaoforms", "demonkingyouth"), tp=380000, str_m=14.0, pwr_m=15.0, def_m=13.5, skp_m=15.0, saga="shadow_saga:4")

    # dragonforms (No saga 4.5M / 11M TP: High DEF & PWR, lower physical STR)
    _set_form(_find_form(cat, r, "dragonforms", "guruawakening"), tp=4500000, str_m=24.0, pwr_m=34.0, def_m=34.0, skp_m=34.0)
    _set_form(_find_form(cat, r, "dragonforms", "porungaascendant"), tp=11000000, str_m=45.0, pwr_m=50.0, def_m=54.0, skp_m=50.0)

    # elderforms (Endgame No-Saga 15M -> 70M TP: Guardian Tank DEF & PWR focus)
    elder_tiers = [
        ("awakenednamekian", 15000000, 31.0, 36.0, 40.0, 35.0),
        ("ascendednamekian", 27500000, 56.0, 66.0, 74.0, 65.0),
        ("primalnamekian", 40000000, 82.0, 96.0, 108.0, 95.0),
        ("dragonnamekian", 55000000, 112.0, 132.0, 148.0, 130.0),
        ("divinenamekian", 70000000, 142.0, 168.0, 185.0, 165.0),
    ]
    for fid, tp, s_m, p_m, d_m, k_m in elder_tiers:
        _set_form(_find_form(cat, r, "elderforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=1.05, atk_m=1.05)


def _balance_frostdemon(cat: dict[str, Any]) -> None:
    """Frost Demon (Frieza/Cooler): Lethal Evolution & Golden/Black Emperor (High PWR/STR, Stamina/Ki drain trade-off)."""
    r = "frostdemon"
    # evolutionforms (Saga-gated to Frieza Saga -> Movies Cooler -> GT)
    _set_form(_find_form(cat, r, "evolutionforms", "second"), tp=40000, str_m=4.2, pwr_m=3.5, def_m=4.0, skp_m=3.5, saga="frieza_saga:12", drain_ki=0.0)
    _set_form(_find_form(cat, r, "evolutionforms", "third"), tp=65000, str_m=4.8, pwr_m=5.8, def_m=4.5, skp_m=5.8, spd_m=1.06, saga="frieza_saga:13", drain_ki=0.0)
    _set_form(_find_form(cat, r, "evolutionforms", "final"), tp=100000, str_m=7.5, pwr_m=8.0, def_m=7.2, skp_m=8.0, spd_m=1.08, saga="frieza_saga:14", drain_ki=0.0)
    _set_form(_find_form(cat, r, "evolutionforms", "fullpower"), tp=160000, str_m=11.5, pwr_m=10.5, def_m=11.0, skp_m=10.5, spd_m=0.9, saga="frieza_saga:15", drain_ki=0.24)
    _set_form(_find_form(cat, r, "evolutionforms", "fifth"), tp=300000, str_m=15.5, pwr_m=15.0, def_m=16.0, skp_m=15.0, saga="movies_saga:16", drain_ki=0.26)
    _set_form(_find_form(cat, r, "evolutionforms", "fifthfullpower"), tp=900000, str_m=20.0, pwr_m=19.5, def_m=20.0, skp_m=19.5, saga="gt_saga:14", drain_ki=0.32)

    # superforms2 (Golden Frieza in RoF Saga & Black Frieza in Granolah Saga!)
    _set_form(_find_form(cat, r, "superforms2", "golden"), tp=900000, str_m=34.0, pwr_m=36.0, def_m=30.0, skp_m=36.0, spd_m=1.15, atk_m=1.1, saga="rof_saga:7", drain_ki=0.18, drain_stm=0.05)
    _set_form(_find_form(cat, r, "superforms2", "black"), tp=18000000, str_m=175.0, pwr_m=180.0, def_m=150.0, skp_m=180.0, spd_m=1.22, atk_m=1.15, saga="granolah_saga:27", drain_ki=0.35, drain_stm=0.25)

    # legendaryforms (Big Gete Star Cyborg: No saga -> High DEF & negative Ki drain regeneration, lower STR/PWR)
    _set_form(_find_form(cat, r, "legendaryforms", "mecha"), tp=250000, str_m=5.8, pwr_m=5.5, def_m=7.0, skp_m=5.5, drain_ki=0.0)
    _set_form(_find_form(cat, r, "legendaryforms", "metal"), tp=600000, str_m=11.5, pwr_m=11.5, def_m=14.5, skp_m=11.5, drain_ki=-0.05)
    _set_form(_find_form(cat, r, "legendaryforms", "metalcore"), tp=1200000, str_m=18.0, pwr_m=18.5, def_m=23.0, skp_m=18.5, drain_ki=-0.1)

    # tyrantforms (Shadow Saga Master)
    _set_form(_find_form(cat, r, "tyrantforms", "chilledlegacy"), tp=180000, str_m=8.8, pwr_m=9.2, def_m=7.8, skp_m=9.2, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "tyrantforms", "goldencooler"), tp=380000, str_m=13.5, pwr_m=14.0, def_m=12.0, skp_m=14.0, saga="shadow_saga:4")
    _set_form(_find_form(cat, r, "tyrantforms", "darkemperor"), tp=700000, str_m=18.0, pwr_m=18.5, def_m=16.0, skp_m=18.5, saga="shadow_saga:6")

    # emperorforms (No saga 4.5M / 11M TP: High PWR/SKP, lower DEF)
    _set_form(_find_form(cat, r, "emperorforms", "frozensovereign"), tp=4500000, str_m=30.0, pwr_m=33.0, def_m=26.0, skp_m=33.0)
    _set_form(_find_form(cat, r, "emperorforms", "hellfireemperor"), tp=11000000, str_m=48.0, pwr_m=52.0, def_m=39.0, skp_m=52.0)

    # glacierforms (Endgame No-Saga 15M -> 70M TP: High PWR & SKP, lower DEF)
    glacier_tiers = [
        ("truefrost", 15000000, 35.0, 38.0, 30.0, 38.0),
        ("absolutefrost", 27500000, 65.0, 70.0, 55.0, 70.0),
        ("emperorfrost", 40000000, 95.0, 102.0, 80.0, 102.0),
        ("divinefrost", 55000000, 130.0, 140.0, 110.0, 140.0),
        ("eternalfrost", 70000000, 165.0, 178.0, 140.0, 178.0),
    ]
    for fid, tp, s_m, p_m, d_m, k_m in glacier_tiers:
        _set_form(_find_form(cat, r, "glacierforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=1.08, atk_m=1.05)


def _balance_bioandroid(cat: dict[str, Any]) -> None:
    """Bio-Android (Cell): Genetic Adaptation, Android Saga Evolution & Berserker Cell Max."""
    r = "bioandroid"
    # bioevolution (Fixed to actual Android/Cell Saga quests!)
    _set_form(_find_form(cat, r, "bioevolution", "semiperfect"), tp=60000, str_m=5.5, pwr_m=5.5, def_m=5.0, skp_m=5.5, saga="android_saga:11", drain_ki=0.0)
    _set_form(_find_form(cat, r, "bioevolution", "perfect"), tp=110000, str_m=8.0, pwr_m=8.0, def_m=7.8, skp_m=8.0, saga="android_saga:13", drain_ki=0.0)
    _set_form(_find_form(cat, r, "bioevolution", "superperfect"), tp=180000, str_m=11.5, pwr_m=12.0, def_m=11.0, skp_m=12.0, saga="android_saga:15", drain_ki=0.16)
    _set_form(_find_form(cat, r, "bioevolution", "ultraperfect"), tp=320000, str_m=15.5, pwr_m=15.5, def_m=15.0, skp_m=15.5, saga="buu_saga:35", drain_ki=0.26)
    _set_form(_find_form(cat, r, "bioevolution", "hyperperfect"), tp=550000, str_m=19.5, pwr_m=19.5, def_m=18.5, skp_m=19.5, spd_m=1.08, atk_m=1.05, saga="gt_saga:15", drain_ki=0.32)

    # cellmax (Movies Saga 108 + Master: Massive Giant STR/DEF, terrible SPD/ATK & high Ki drain)
    _set_form(_find_form(cat, r, "cellmax", "corruptedgiant"), tp=2500000, str_m=46.0, pwr_m=34.0, def_m=44.0, skp_m=34.0, spd_m=0.68, atk_m=0.45, saga="movies_saga:108", master=True, drain_ki=0.5)

    # biogodforms (No saga, matches Saiyan godforms Lvl 1 & 2 at 10M / 30M TP)
    _set_form(_find_form(cat, r, "biogodforms", "perfectgod"), tp=10000000, str_m=30.0, pwr_m=30.0, def_m=27.0, skp_m=30.0, spd_m=1.1, atk_m=1.05, drain_ki=0.25)
    _set_form(_find_form(cat, r, "biogodforms", "perfectblue"), tp=30000000, str_m=75.0, pwr_m=75.0, def_m=68.0, skp_m=75.0, spd_m=1.15, atk_m=1.1, drain_ki=0.3)

    # 13 Genome Strain Trees (Require bioevolution.perfect, 200k / 500k / 1.25M TP -> 8.5x / 13.5x / 20.0x with racial bias!)
    genome_biases: dict[str, tuple[float, float, float, float, float]] = {
        # tree: (str_bias, pwr_bias, def_bias, skp_bias, spd)
        "genomesaiyan": (1.12, 1.0, 0.85, 1.08, 1.06),
        "genomenamekian": (0.9, 1.02, 1.18, 1.0, 1.02),
        "genomemajin": (0.92, 1.04, 1.16, 1.02, 1.02),
        "genomefrostdemon": (1.02, 1.12, 0.88, 1.1, 1.06),
        "genomeandroid": (1.02, 0.95, 1.12, 1.0, 1.05),
        "genomehuman": (1.05, 0.95, 0.9, 1.15, 1.06),
        "genomeangel": (0.88, 1.12, 1.08, 1.12, 1.1),
        "genomeglind": (0.88, 1.15, 1.0, 1.15, 1.05),
        "genomedemon": (1.1, 1.08, 0.86, 1.06, 1.05),
        "genomesoulreaper": (1.1, 1.0, 0.84, 1.12, 1.12),
        "genometaimujin": (1.08, 0.95, 0.82, 1.15, 1.15),
        "genomesphinxian": (1.08, 0.92, 1.12, 0.98, 1.04),
        "genomealien": (0.92, 1.14, 0.92, 1.14, 1.06),
    }
    base_lvls = [(200000, 8.5), (500000, 13.5), (1250000, 20.0)]
    for g_tree, (sb, pb, db, kb, sp) in genome_biases.items():
        if g_tree in cat["racas"][r]["arvores_de_transformacao"]:
            forms = cat["racas"][r]["arvores_de_transformacao"][g_tree]["formas"]
            for idx, f in enumerate(forms):
                tp, b_mult = base_lvls[min(idx, 2)]
                _set_form(
                    f,
                    tp=tp,
                    str_m=b_mult * sb,
                    pwr_m=b_mult * pb,
                    def_m=b_mult * db,
                    skp_m=b_mult * kb,
                    spd_m=round(1.0 + (sp - 1.0) * (idx + 1) / 3.0, 3),
                    atk_m=1.05,
                    drain_ki=0.12 if g_tree == "genomeandroid" else (0.18 + 0.06 * idx),
                )

    # legendaryforms (Xeno Cell - No saga: 350k / 800k / 1.8M TP)
    _set_form(_find_form(cat, r, "legendaryforms", "xeno"), tp=350000, str_m=6.5, pwr_m=6.5, def_m=5.5, skp_m=6.5)
    _set_form(_find_form(cat, r, "legendaryforms", "xenofp"), tp=800000, str_m=12.5, pwr_m=12.5, def_m=10.5, skp_m=12.5)
    _set_form(_find_form(cat, r, "legendaryforms", "xenomax"), tp=1800000, str_m=19.5, pwr_m=19.5, def_m=16.5, skp_m=19.5)

    # parasiteforms (Shadow Saga Master)
    _set_form(_find_form(cat, r, "parasiteforms", "tuffleparasite"), tp=200000, str_m=9.0, pwr_m=9.5, def_m=8.0, skp_m=9.5, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "parasiteforms", "hellcorruption"), tp=420000, str_m=14.5, pwr_m=15.0, def_m=12.5, skp_m=15.0, saga="shadow_saga:4")

    # geneticforms (No saga 4.5M / 11M TP)
    _set_form(_find_form(cat, r, "geneticforms", "imperfectgenesis"), tp=4500000, str_m=30.0, pwr_m=30.0, def_m=25.0, skp_m=30.0)
    _set_form(_find_form(cat, r, "geneticforms", "absoluteperfection"), tp=11000000, str_m=48.0, pwr_m=48.0, def_m=42.0, skp_m=48.0)

    # coreforms (Endgame No-Saga 15M -> 70M TP: Balanced Apex)
    core_tiers = [
        ("bioperfected", 15000000, 35.0, 35.0, 33.0, 35.0),
        ("superperfectbio", 27500000, 65.0, 65.0, 61.0, 65.0),
        ("bioascension", 40000000, 95.0, 95.0, 90.0, 95.0),
        ("evolutionarycore", 55000000, 130.0, 130.0, 122.0, 130.0),
        ("absolutebio", 70000000, 165.0, 165.0, 155.0, 165.0),
    ]
    for fid, tp, s_m, p_m, d_m, k_m in core_tiers:
        _set_form(_find_form(cat, r, "coreforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=1.08, atk_m=1.05)


def _balance_majin(cat: dict[str, Any]) -> None:
    """Majin (Buu/Janemba/Mira): Elastic Tank & Absorption (High DEF & Chaos PWR, zero Priceless)."""
    r = "majin"
    # pureforms (Fixed to actual Majin Buu Saga quests!)
    _set_form(_find_form(cat, r, "pureforms", "kid"), tp=65000, str_m=5.8, pwr_m=5.8, def_m=6.6, skp_m=5.8, saga="buu_saga:14", drain_ki=0.0)
    _set_form(_find_form(cat, r, "pureforms", "evil"), tp=110000, str_m=8.5, pwr_m=8.5, def_m=7.5, skp_m=8.8, saga="buu_saga:20", drain_ki=0.0)
    _set_form(_find_form(cat, r, "pureforms", "super"), tp=180000, str_m=12.0, pwr_m=12.0, def_m=12.8, skp_m=12.0, saga="buu_saga:22", drain_ki=0.0)
    _set_form(_find_form(cat, r, "pureforms", "ultra"), tp=320000, str_m=16.0, pwr_m=16.5, def_m=15.0, skp_m=16.5, saga="buu_saga:30", drain_ki=0.22)
    _set_form(_find_form(cat, r, "pureforms", "primalmajin"), tp=550000, str_m=20.0, pwr_m=20.5, def_m=18.5, skp_m=20.5, spd_m=1.1, atk_m=1.08, saga="buu_saga:34", drain_ki=0.3)

    # mimicforms (Fix Priceless -1 -> Buu Gotenks & Buu Gohan absorption quests!)
    _set_form(_find_form(cat, r, "mimicforms", "supermajin"), tp=550000, str_m=14.5, pwr_m=16.0, def_m=14.0, skp_m=16.0, spd_m=1.08, saga="buu_saga:26", drain_ki=0.12)
    _set_form(_find_form(cat, r, "mimicforms", "extrasupermajin"), tp=1200000, str_m=23.0, pwr_m=25.0, def_m=22.0, skp_m=25.0, spd_m=1.12, saga="buu_saga:27", drain_ki=0.18)

    # legendaryforms (Janemba path - No saga: 200k / 450k / 1.1M TP)
    _set_form(_find_form(cat, r, "legendaryforms", "innocencedemon"), tp=200000, str_m=5.8, pwr_m=6.0, def_m=6.8, skp_m=6.0, drain_ki=0.0)
    _set_form(_find_form(cat, r, "legendaryforms", "giantinnocencedemon"), tp=450000, str_m=13.0, pwr_m=10.5, def_m=15.0, skp_m=10.5, spd_m=0.78, atk_m=0.75, drain_ki=0.22)
    _set_form(_find_form(cat, r, "legendaryforms", "superdemon"), tp=1100000, str_m=19.5, pwr_m=20.0, def_m=17.5, skp_m=20.5, spd_m=1.1, atk_m=1.08, drain_ki=0.18)

    # maliceforms (Shadow Saga Master)
    _set_form(_find_form(cat, r, "maliceforms", "darkmaskbuu"), tp=180000, str_m=8.5, pwr_m=8.5, def_m=9.2, skp_m=8.5, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "maliceforms", "hatredincarnate"), tp=350000, str_m=13.5, pwr_m=13.5, def_m=11.0, skp_m=14.0, saga="shadow_saga:4")
    _set_form(_find_form(cat, r, "maliceforms", "absorptiontyrant"), tp=680000, str_m=17.5, pwr_m=18.0, def_m=18.5, skp_m=18.0, saga="shadow_saga:6")

    # reflectionforms (No saga 600k / 1.45M / 3.65M TP)
    _set_form(_find_form(cat, r, "reflectionforms", "goldenmimic"), tp=600000, str_m=10.0, pwr_m=10.5, def_m=9.5, skp_m=10.5)
    _set_form(_find_form(cat, r, "reflectionforms", "ascendedmimic"), tp=1450000, str_m=18.0, pwr_m=18.5, def_m=17.0, skp_m=18.5)
    _set_form(_find_form(cat, r, "reflectionforms", "godmimic"), tp=3650000, str_m=29.0, pwr_m=30.0, def_m=28.0, skp_m=30.0)

    # chaosforms (No saga 4.5M / 11M TP: Rampage = Glass Cannon, Absorbed = Tank)
    _set_form(_find_form(cat, r, "chaosforms", "rampagemajin"), tp=4500000, str_m=34.0, pwr_m=34.0, def_m=22.0, skp_m=35.0, spd_m=1.12, atk_m=1.1)
    _set_form(_find_form(cat, r, "chaosforms", "absorbedascendant"), tp=11000000, str_m=46.0, pwr_m=48.0, def_m=54.0, skp_m=48.0, spd_m=1.06)

    # miraforms (Endgame No-Saga 15M -> 70M TP: Tank/DEF & Ki focus)
    mira_tiers = [
        ("majinawakening", 15000000, 34.0, 35.0, 39.0, 35.0),
        ("puremajin", 27500000, 62.0, 65.0, 72.0, 65.0),
        ("chaosmajin", 40000000, 92.0, 95.0, 105.0, 95.0),
        ("demonicmajin", 55000000, 125.0, 130.0, 144.0, 130.0),
        ("divinemajin", 70000000, 160.0, 165.0, 182.0, 165.0),
    ]
    for fid, tp, s_m, p_m, d_m, k_m in mira_tiers:
        _set_form(_find_form(cat, r, "miraforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=1.06, atk_m=1.05)


def _balance_soulreaper(cat: dict[str, Any]) -> None:
    """Soul Reaper (Bleach): High Speed/STR/SKP Glass Cannon, preserving user's zanpakutoforms combat numbers."""
    r = "soulreaper"
    # Keep user's zanpakutoforms STR/PWR/DEF/SKP (10x -> 19x -> 26x -> 50x), normalize secondary stats (STM/VIT/ENE/SPD/ATK)
    _set_form(_find_form(cat, r, "zanpakutoforms", "shikai"), tp=75000, str_m=10.0, pwr_m=10.0, def_m=8.5, skp_m=10.0, spd_m=1.1, atk_m=1.04)
    _set_form(_find_form(cat, r, "zanpakutoforms", "bankai"), tp=450000, str_m=19.0, pwr_m=19.0, def_m=16.0, skp_m=19.0, spd_m=1.18, atk_m=1.08)
    _set_form(_find_form(cat, r, "zanpakutoforms", "vastolorde"), tp=3750000, str_m=26.0, pwr_m=26.0, def_m=21.0, skp_m=26.0, spd_m=1.22, atk_m=1.12)
    _set_form(_find_form(cat, r, "zanpakutoforms", "mugetsu"), tp=8000000, str_m=50.0, pwr_m=50.0, def_m=40.0, skp_m=50.0, spd_m=1.35, atk_m=1.25, drain_ki=2.5, drain_stm=1.5, drain_hp=0.35)

    # hogyokuforms (User set Chrysalis to 15x; scale Ascended to 28x!)
    _set_form(_find_form(cat, r, "hogyokuforms", "hogyokuchrysalis"), tp=1950000, str_m=15.0, pwr_m=15.0, def_m=14.0, skp_m=15.0, spd_m=1.16, atk_m=1.06, saga="shadow_saga:4")
    _set_form(_find_form(cat, r, "hogyokuforms", "hogyokuascended"), tp=3200000, str_m=28.0, pwr_m=28.0, def_m=23.0, skp_m=29.0, spd_m=1.22, atk_m=1.1, saga="shadow_saga:6")

    # legendaryforms (Bloodline Saga: Hollow-born)
    _set_form(_find_form(cat, r, "legendaryforms", "hollowborn"), tp=525000, str_m=14.0, pwr_m=13.5, def_m=10.5, skp_m=14.5, spd_m=1.12, atk_m=1.06, saga="bloodline_soulreaper_saga:1")

    # truezanpakutoforms (Endgame Master 15M -> 70M TP: High STR/SKP & Speed, Glass Cannon DEF)
    tz_tiers = [
        ("trueshikai", 15000000, 38.0, 36.0, 28.0, 40.0, 1.16),
        ("truebankai", 27500000, 72.0, 68.0, 52.0, 75.0, 1.2),
        ("hornofsalvation", 45000000, 118.0, 115.0, 85.0, 122.0, 1.24),
        ("bloodchains", 70000000, 175.0, 170.0, 125.0, 180.0, 1.28),
    ]
    for fid, tp, s_m, p_m, d_m, k_m, sp in tz_tiers:
        _set_form(_find_form(cat, r, "truezanpakutoforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=sp, atk_m=1.1)


def _balance_custom_six_races(cat: dict[str, Any]) -> None:
    """Balance Angel, Glind, Makaijin, Seiunjin, Sekhari, and Taimujin with distinct lore trade-offs."""
    # 1. ANGEL: Divine Grace & Evasion (High DEF, PWR, SKP; lower physical STR)
    r = "angel"
    _set_form(_find_form(cat, r, "angelforms", "haloawakening"), tp=350000, str_m=4.8, pwr_m=6.0, def_m=6.2, skp_m=6.0, spd_m=1.06, saga=None)
    _set_form(_find_form(cat, r, "angelforms", "attendant"), tp=900000, str_m=9.5, pwr_m=11.5, def_m=12.0, skp_m=11.5, spd_m=1.1, saga=None)
    _set_form(_find_form(cat, r, "angelforms", "celestialguide"), tp=2200000, str_m=15.0, pwr_m=18.5, def_m=19.0, skp_m=18.5, spd_m=1.14, saga=None)

    _set_form(_find_form(cat, r, "severedforms", "severedhalo"), tp=450000, str_m=11.5, pwr_m=11.5, def_m=8.5, skp_m=12.0, spd_m=1.1, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "severedforms", "dethroned"), tp=950000, str_m=18.0, pwr_m=18.0, def_m=13.5, skp_m=18.5, spd_m=1.12, saga="shadow_saga:4")

    _set_form(_find_form(cat, r, "legendaryforms", "unboundhalo"), tp=800000, str_m=13.0, pwr_m=14.5, def_m=12.0, skp_m=14.5, spd_m=1.1, saga="bloodline_angel_saga:1")
    _set_form(_find_form(cat, r, "legendaryforms", "starbreaker"), tp=1600000, str_m=20.0, pwr_m=22.5, def_m=18.5, skp_m=22.5, spd_m=1.14, saga="bloodline_angel_saga:2")
    _set_form(_find_form(cat, r, "legendaryforms", "lawlesslight"), tp=3200000, str_m=29.0, pwr_m=32.0, def_m=26.0, skp_m=32.0, spd_m=1.18, saga="bloodline_angel_saga:3")

    _set_form(_find_form(cat, r, "godforms", "highangel"), tp=2000000, str_m=27.0, pwr_m=33.0, def_m=34.0, skp_m=33.0, spd_m=1.15, atk_m=1.08, saga="beerus_saga:7")
    _set_form(_find_form(cat, r, "godforms", "autonomousgrace"), tp=15000000, str_m=68.0, pwr_m=82.0, def_m=85.0, skp_m=82.0, spd_m=1.22, atk_m=1.12, saga="moro_saga:22")
    _set_form(_find_form(cat, r, "godforms", "grandradiance"), tp=70000000, str_m=160.0, pwr_m=190.0, def_m=195.0, skp_m=190.0, spd_m=1.25, atk_m=1.15, saga="godfall_saga:37")

    # 2. GLIND: Divine Magic & Time Power (High PWR & SKP, lower physical STR)
    r = "glind"
    _set_form(_find_form(cat, r, "superforms", "buffed"), tp=60000, str_m=4.8, pwr_m=4.2, def_m=4.5, skp_m=4.2, saga="classic_saga:46")
    _set_form(_find_form(cat, r, "superforms", "outofcontrol"), tp=110000, str_m=6.2, pwr_m=6.8, def_m=5.0, skp_m=6.8, saga="saiyan_saga:12")
    _set_form(_find_form(cat, r, "superforms", "super"), tp=180000, str_m=7.5, pwr_m=9.2, def_m=7.8, skp_m=9.2, saga="frieza_saga:10")
    _set_form(_find_form(cat, r, "superforms", "absorption"), tp=320000, str_m=12.5, pwr_m=15.0, def_m=13.5, skp_m=15.0, saga="buu_saga:1")
    _set_form(_find_form(cat, r, "superforms", "trueform"), tp=600000, str_m=16.5, pwr_m=20.0, def_m=18.0, skp_m=20.0, saga="buu_saga:35")

    _set_form(_find_form(cat, r, "kishinforms", "demongodawakened"), tp=350000, str_m=9.5, pwr_m=12.0, def_m=9.5, skp_m=12.0, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "kishinforms", "demongodtrue"), tp=750000, str_m=14.5, pwr_m=18.5, def_m=14.5, skp_m=18.5, saga="shadow_saga:4")

    _set_form(_find_form(cat, r, "legendaryforms", "transcended"), tp=750000, str_m=7.0, pwr_m=8.5, def_m=7.5, skp_m=8.5, drain_ki=0.3)
    _set_form(_find_form(cat, r, "legendaryforms", "darkking"), tp=1750000, str_m=13.5, pwr_m=16.5, def_m=14.0, skp_m=16.5, drain_ki=0.4)
    _set_form(_find_form(cat, r, "legendaryforms", "timepower_darkking"), tp=3750000, str_m=22.0, pwr_m=25.0, def_m=17.5, skp_m=25.0, drain_ki=0.48)
    _set_form(_find_form(cat, r, "legendaryforms", "timepower_realmoflight"), tp=3750000, str_m=18.0, pwr_m=23.0, def_m=25.0, skp_m=23.0, drain_ki=0.42)

    # 3. TAIMUJIN (Hit): Time-Skip Assassin (High STR, SKP, SPD, ATK; Glass Cannon DEF)
    r = "taimujin"
    _set_form(_find_form(cat, r, "taimujinforms", "chronofocus"), tp=250000, str_m=5.2, pwr_m=4.5, def_m=3.6, skp_m=5.5, spd_m=1.08, atk_m=1.05, saga=None)
    _set_form(_find_form(cat, r, "taimujinforms", "timebreaker"), tp=650000, str_m=10.0, pwr_m=8.8, def_m=7.0, skp_m=10.5, spd_m=1.12, atk_m=1.08, saga=None)
    _set_form(_find_form(cat, r, "taimujinforms", "eternalassassin"), tp=1500000, str_m=16.0, pwr_m=14.0, def_m=11.0, skp_m=17.0, spd_m=1.16, atk_m=1.12, saga=None)

    _set_form(_find_form(cat, r, "ravagerforms", "breakermask"), tp=350000, str_m=11.0, pwr_m=10.0, def_m=8.0, skp_m=11.5, spd_m=1.12, atk_m=1.08, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "ravagerforms", "chronoravager"), tp=750000, str_m=17.0, pwr_m=15.5, def_m=12.5, skp_m=17.5, spd_m=1.15, atk_m=1.1, saga="shadow_saga:4")

    _set_form(_find_form(cat, r, "legendaryforms", "timetorn"), tp=600000, str_m=13.5, pwr_m=12.5, def_m=9.5, skp_m=14.0, spd_m=1.12, saga="bloodline_taimujin_saga:1")
    _set_form(_find_form(cat, r, "legendaryforms", "fracturedhour"), tp=1200000, str_m=21.0, pwr_m=19.5, def_m=15.0, skp_m=22.0, spd_m=1.16, saga="bloodline_taimujin_saga:2")
    _set_form(_find_form(cat, r, "legendaryforms", "endofhours"), tp=2400000, str_m=30.0, pwr_m=28.0, def_m=21.0, skp_m=31.0, spd_m=1.2, saga="bloodline_taimujin_saga:3")

    _set_form(_find_form(cat, r, "chronoforms", "pureprogress"), tp=3500000, str_m=34.0, pwr_m=30.0, def_m=22.0, skp_m=36.0, spd_m=1.2, atk_m=1.15, saga="u7vsu6_saga:8")
    _set_form(_find_form(cat, r, "chronoforms", "chronozenith"), tp=9000000, str_m=56.0, pwr_m=48.0, def_m=35.0, skp_m=58.0, spd_m=1.24, atk_m=1.18, saga="top_saga:29")

    _set_form(_find_form(cat, r, "godforms", "divinechronos"), tp=1200000, str_m=14.0, pwr_m=13.0, def_m=10.0, skp_m=15.0, spd_m=1.14, atk_m=1.1)
    _set_form(_find_form(cat, r, "godforms", "timesovereign"), tp=2800000, str_m=24.0, pwr_m=22.0, def_m=17.0, skp_m=25.0, spd_m=1.18, atk_m=1.14)
    _set_form(_find_form(cat, r, "godforms", "absolutetime"), tp=6000000, str_m=38.0, pwr_m=35.0, def_m=27.0, skp_m=40.0, spd_m=1.22, atk_m=1.18)

    eon_tiers = [
        ("temporalawakening", 15000000, 38.0, 34.0, 27.0, 40.0, 1.14),
        ("timewalker", 27500000, 70.0, 62.0, 50.0, 74.0, 1.16),
        ("temporalascendant", 40000000, 102.0, 90.0, 72.0, 108.0, 1.18),
        ("chronowarrior", 55000000, 140.0, 124.0, 98.0, 148.0, 1.2),
        ("eternaltaimujin", 70000000, 178.0, 156.0, 125.0, 185.0, 1.22),
    ]
    for fid, tp, s_m, p_m, d_m, k_m, sp in eon_tiers:
        _set_form(_find_form(cat, r, "eonforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=sp, atk_m=1.1)

    # 4. MAKAIJIN (Demon Realm): Aggressive STR & PWR, lower DEF
    r = "makaijin"
    _set_form(_find_form(cat, r, "superforms", "demonblood"), tp=120000, str_m=4.6, pwr_m=4.8, def_m=3.6, skp_m=4.6, saga=None)
    _set_form(_find_form(cat, r, "superforms", "hornedfury"), tp=320000, str_m=8.2, pwr_m=8.5, def_m=6.4, skp_m=8.2, saga=None)
    _set_form(_find_form(cat, r, "superforms", "abyssalsovereign"), tp=750000, str_m=13.0, pwr_m=13.5, def_m=10.2, skp_m=13.0, saga=None)
    _set_form(_find_form(cat, r, "superforms", "realmtyrant"), tp=1600000, str_m=18.5, pwr_m=19.5, def_m=14.5, skp_m=19.0, saga="daima_saga:16")

    _set_form(_find_form(cat, r, "demonkingforms", "kingofdemons"), tp=350000, str_m=10.5, pwr_m=11.0, def_m=8.8, skp_m=10.5, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "demonkingforms", "makaioshin"), tp=750000, str_m=16.5, pwr_m=17.0, def_m=13.5, skp_m=16.5, saga="shadow_saga:4")

    _set_form(_find_form(cat, r, "legendaryforms", "abyssborn"), tp=525000, str_m=12.0, pwr_m=12.0, def_m=9.5, skp_m=12.0, saga="bloodline_makaijin_saga:1")
    _set_form(_find_form(cat, r, "legendaryforms", "giantofthepit"), tp=950000, str_m=22.0, pwr_m=15.0, def_m=23.0, skp_m=15.0, spd_m=0.75, atk_m=0.72, saga="bloodline_makaijin_saga:2")
    _set_form(_find_form(cat, r, "legendaryforms", "pitlord"), tp=1800000, str_m=28.0, pwr_m=29.0, def_m=23.0, skp_m=29.0, saga="bloodline_makaijin_saga:3")

    _set_form(_find_form(cat, r, "infernalforms", "demonrealmlord"), tp=3500000, str_m=29.0, pwr_m=31.0, def_m=24.0, skp_m=31.0)
    _set_form(_find_form(cat, r, "infernalforms", "infernalflame"), tp=9000000, str_m=46.0, pwr_m=50.0, def_m=36.0, skp_m=50.0)

    abyss_tiers = [
        ("demonawakening", 15000000, 36.0, 38.0, 29.0, 37.0),
        ("highdemon", 27500000, 66.0, 70.0, 54.0, 68.0),
        ("demongod", 40000000, 96.0, 102.0, 78.0, 100.0),
        ("abyssaldemon", 55000000, 132.0, 140.0, 108.0, 136.0),
        ("demonsovereign", 70000000, 168.0, 178.0, 136.0, 172.0),
    ]
    for fid, tp, s_m, p_m, d_m, k_m in abyss_tiers:
        _set_form(_find_form(cat, r, "abyssforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=1.08, atk_m=1.05)

    # 5. SEIUNJIN (Nebula Folk): Cosmic Ki Caster (High PWR & SKP, lower physical STR)
    r = "seiunjin"
    _set_form(_find_form(cat, r, "superforms", "starbirth"), tp=100000, str_m=3.8, pwr_m=5.0, def_m=4.0, skp_m=5.0, saga=None)
    _set_form(_find_form(cat, r, "superforms", "nebula"), tp=300000, str_m=7.0, pwr_m=9.2, def_m=7.2, skp_m=9.2, saga=None)
    _set_form(_find_form(cat, r, "superforms", "pulsar"), tp=750000, str_m=11.5, pwr_m=14.8, def_m=11.8, skp_m=14.8, saga=None)
    _set_form(_find_form(cat, r, "superforms", "quasarbody"), tp=1800000, str_m=16.5, pwr_m=21.5, def_m=17.0, skp_m=21.5, saga=None)

    _set_form(_find_form(cat, r, "blackholeforms", "voideater"), tp=350000, str_m=9.0, pwr_m=11.5, def_m=10.5, skp_m=11.5, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "blackholeforms", "eventcollapse"), tp=750000, str_m=14.0, pwr_m=17.5, def_m=16.0, skp_m=17.5, saga="shadow_saga:4")

    _set_form(_find_form(cat, r, "legendaryforms", "flarebloom"), tp=525000, str_m=10.5, pwr_m=13.5, def_m=10.0, skp_m=13.5, saga="bloodline_seiunjin_saga:1")
    _set_form(_find_form(cat, r, "legendaryforms", "coronagiant"), tp=950000, str_m=21.0, pwr_m=18.0, def_m=23.0, skp_m=18.0, spd_m=0.76, atk_m=0.74, saga="bloodline_seiunjin_saga:2")
    _set_form(_find_form(cat, r, "legendaryforms", "supernovaheart"), tp=1800000, str_m=23.0, pwr_m=31.0, def_m=24.0, skp_m=31.0, saga="bloodline_seiunjin_saga:3")

    _set_form(_find_form(cat, r, "cosmosforms", "eventhorizon"), tp=3500000, str_m=25.0, pwr_m=34.0, def_m=28.0, skp_m=34.0, spd_m=1.1)
    _set_form(_find_form(cat, r, "cosmosforms", "starforged"), tp=9000000, str_m=40.0, pwr_m=54.0, def_m=44.0, skp_m=54.0, spd_m=1.14)

    # 6. SEKHARI (Egyptian Solar Sphinx): Royal Tank & Physical Juggernaut (High DEF & STR, lower PWR)
    r = "sekhari"
    _set_form(_find_form(cat, r, "superforms", "awakenedguardian"), tp=120000, str_m=4.8, pwr_m=3.8, def_m=5.2, skp_m=4.2, saga=None)
    _set_form(_find_form(cat, r, "superforms", "sunmane"), tp=350000, str_m=8.8, pwr_m=7.0, def_m=9.5, skp_m=7.8, saga=None)
    _set_form(_find_form(cat, r, "superforms", "divinebeast"), tp=850000, str_m=14.0, pwr_m=11.0, def_m=15.0, skp_m=12.5, saga=None)
    _set_form(_find_form(cat, r, "superforms", "pharaohascendant"), tp=2000000, str_m=20.0, pwr_m=16.0, def_m=21.5, skp_m=18.0, saga=None)

    _set_form(_find_form(cat, r, "devourerforms", "heartdevourer"), tp=350000, str_m=11.0, pwr_m=9.0, def_m=12.0, skp_m=10.0, saga="shadow_saga:2")
    _set_form(_find_form(cat, r, "devourerforms", "ammitascendant"), tp=750000, str_m=17.0, pwr_m=14.0, def_m=18.5, skp_m=15.5, saga="shadow_saga:4")

    _set_form(_find_form(cat, r, "legendaryforms", "feralpride"), tp=525000, str_m=13.0, pwr_m=10.0, def_m=11.5, skp_m=12.0, saga="bloodline_sekhari_saga:1")
    _set_form(_find_form(cat, r, "legendaryforms", "dunetitan"), tp=950000, str_m=22.5, pwr_m=14.0, def_m=24.5, skp_m=15.0, spd_m=0.75, atk_m=0.72, saga="bloodline_sekhari_saga:2")
    _set_form(_find_form(cat, r, "legendaryforms", "suneater"), tp=1800000, str_m=30.0, pwr_m=25.0, def_m=28.0, skp_m=28.0, saga="bloodline_sekhari_saga:3")

    _set_form(_find_form(cat, r, "predatorforms", "eclipseprowler"), tp=3500000, str_m=33.0, pwr_m=26.0, def_m=25.0, skp_m=31.0, spd_m=1.15, atk_m=1.12)
    _set_form(_find_form(cat, r, "predatorforms", "solarlion"), tp=9000000, str_m=52.0, pwr_m=42.0, def_m=44.0, skp_m=48.0, spd_m=1.14, atk_m=1.1)

    crown_tiers = [
        ("sphinxawakening", 15000000, 37.0, 30.0, 39.0, 34.0),
        ("royalsekhari", 27500000, 68.0, 55.0, 72.0, 62.0),
        ("celestialsekhari", 40000000, 100.0, 80.0, 106.0, 92.0),
        ("sekhariascendant", 55000000, 136.0, 110.0, 144.0, 125.0),
        ("eternalsekhari", 70000000, 172.0, 140.0, 182.0, 158.0),
    ]
    for fid, tp, s_m, p_m, d_m, k_m in crown_tiers:
        _set_form(_find_form(cat, r, "crownforms", fid), tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=1.06, atk_m=1.05)


def _balance_universal_forms(cat: dict[str, Any]) -> None:
    """Balance all 14 Universal / Stack transformation trees (multipliers 1.25x-3.80x, drains, TP, and incompatibilities)."""
    u = cat["formas_universais_e_stack"]

    # 1. KAIOKEN: User-configured high multipliers (x2=2x up to x100=100x all 4 stats), stackable burst
    if "kaioken" in u:
        kk_tiers = {
            "x2": (8000, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 0.0, None),
            "x3": (30000, 3.0, 3.0, 3.0, 3.0, 1.0, 1.0, 0.0, None),
            "x4": (50000, 4.0, 4.0, 4.0, 4.0, 1.0, 1.0, 0.0, None),
            "x10": (600000, 10.0, 10.0, 10.0, 10.0, 1.0, 1.0, 0.0, None),
            "x20": (2250000, 20.0, 20.0, 20.0, 20.0, 1.0, 1.0, 0.0, None),
            "x100": (15000000, 100.0, 100.0, 100.0, 100.0, 2.0, 2.0, 0.0, None),
        }
        for f in u["kaioken"]["formas"]:
            if f["id"] in kk_tiers:
                tp, s_m, p_m, d_m, k_m, sp, at, hp_d, sg = kk_tiers[f["id"]]
                _set_form(
                    f,
                    tp=tp,
                    str_m=s_m,
                    pwr_m=p_m,
                    def_m=d_m,
                    skp_m=k_m,
                    spd_m=sp,
                    atk_m=at,
                    drain_ki=0.0,
                    drain_stm=0.0,
                    drain_hp=hp_d,
                    saga=sg,
                    stackable=True,
                    stack_drain=1.5,
                    incomp=["ultimate.ultimate", "ultrainstinct.sign", "ultrainstinct.mastered", "ultrainstinct.true", "ultrainstinctx.sign", "ultrainstinctx.mastered"],
                )

    # 2. ULTIMATE (Potential Unleashed): Steady 2.0x all-around boost with 0 Ki/HP drain, incompatible with Kaioken/UI/UE
    if "ultimate" in u:
        for f in u["ultimate"]["formas"]:
            _set_form(
                f,
                tp=1500000,
                str_m=2.0,
                pwr_m=2.0,
                def_m=2.0,
                skp_m=2.0,
                drain_ki=0.0,
                drain_stm=0.0,
                drain_hp=0.0,
                saga="buu_saga:31",
                stackable=True,
                stack_drain=1.25,
                incomp=[
                    "kaioken.x2",
                    "kaioken.x3",
                    "kaioken.x4",
                    "kaioken.x10",
                    "kaioken.x20",
                    "kaioken.x100",
                    "ultraego.sign",
                    "ultraego.mastered",
                    "ultraegox.sign",
                    "ultraegox.mastered",
                    "ultrainstinct.sign",
                    "ultrainstinct.mastered",
                    "ultrainstinct.true",
                    "ultrainstinctx.sign",
                    "ultrainstinctx.mastered",
                ],
            )

    # 3. GOD KI & GOD KI ENHANCEMENT: Early/Mid divine aura stacks (incompatible with full God forms)
    god_incomp = [
        "biogodforms.perfectblue",
        "biogodforms.perfectgod",
        "divineforms.awakenedgoldengiant",
        "divineforms.golden",
        "divineforms.potentialunleashed",
        "divineforms.supernamekiangod",
        "evildivineforms.supersaiyanrose",
        "evildivineforms.supersaiyanrose3",
        "evildivineforms.supersaiyanroseevolved",
        "evildivineforms.supersaiyanrosefullpower",
        "godforms.absolutetime",
        "godforms.autonomousgrace",
        "godforms.divinechronos",
        "godforms.grandradiance",
        "godforms.highangel",
        "godforms.super_saiyan_blue",
        "godforms.super_saiyan_blue_evolved",
        "godforms.super_saiyan_god",
        "godforms.super_saiyan_rose",
        "godforms.super_saiyan_rose_evolved",
        "godforms.supersaiyangod",
        "godforms.timesovereign",
    ]
    if "godki" in u:
        for f in u["godki"]["formas"]:
            if f["id"] == "godki":
                _set_form(f, lvl=1, tp=500000, str_m=1.30, pwr_m=1.35, def_m=1.25, skp_m=1.35, spd_m=1.04, atk_m=1.03, drain_ki=0.06, saga="beerus_saga:1", stackable=True, stack_drain=1.6, incomp=god_incomp)
            elif f["id"] == "divineki":
                _set_form(f, lvl=2, tp=1500000, str_m=1.60, pwr_m=1.65, def_m=1.50, skp_m=1.65, spd_m=1.08, atk_m=1.05, drain_ki=0.10, saga="u7vsu6_saga:1", stackable=True, stack_drain=1.8, incomp=god_incomp)
    if "godkienhancement" in u:
        for f in u["godkienhancement"]["formas"]:
            _set_form(f, lvl=1, tp=1000000, str_m=1.35, pwr_m=1.45, def_m=1.30, skp_m=1.40, spd_m=1.05, atk_m=1.04, drain_ki=0.10, saga="beerus_saga:6", stackable=True, stack_drain=1.6, incomp=god_incomp)

    # 4. KAIPATH KAI & KAIPATH HAKAISHIN: Creation vs Destruction divine stacks
    if "kaipath_kai" in u:
        for f in u["kaipath_kai"]["formas"]:
            if f["id"] == "divine":
                _set_form(f, lvl=1, tp=1500000, str_m=1.40, pwr_m=1.60, def_m=1.60, skp_m=1.60, drain_ki=0.05, saga="buu_saga:1", stackable=True, stack_drain=1.6, incomp=["ultimate.ultimate", "kaipath_hakaishin.hakaishin"])
            elif f["id"] == "rose":
                _set_form(f, lvl=2, tp=3000000, str_m=1.80, pwr_m=2.10, def_m=1.90, skp_m=2.10, spd_m=1.06, drain_ki=0.09, saga="black_saga:5", stackable=True, stack_drain=1.8, incomp=["ultimate.ultimate", "kaipath_hakaishin.hakaishin"])
    if "kaipath_hakaishin" in u:
        for f in u["kaipath_hakaishin"]["formas"]:
            _set_form(f, lvl=1, tp=2500000, str_m=2.15, pwr_m=2.15, def_m=1.75, skp_m=2.20, spd_m=1.06, drain_ki=0.10, saga="beerus_saga:7", stackable=True, stack_drain=1.8, incomp=["ultimate.ultimate", "kaipath_kai.divine", "kaipath_kai.rose"])

    # 5. VISORED MASK (Bleach): Speed & Offense stack, lower DEF, incompatible with Vasto Lorde / Mugetsu / True Zanpakuto
    visored_incomp = [
        "zanpakutoforms.vastolorde",
        "zanpakutoforms.mugetsu",
        "ultimate.ultimate",
        "truezanpakutoforms.trueshikai",
        "truezanpakutoforms.truebankai",
        "truezanpakutoforms.hornofsalvation",
        "truezanpakutoforms.bloodchains",
    ]
    if "visoredmask" in u:
        vm_tiers = {
            "l1": (300000, 1.25, 1.25, 1.10, 1.30, 1.05, 1.03, 0.04, 0.0, "visored_trials:2"),
            "l2": (600000, 1.50, 1.50, 1.30, 1.55, 1.08, 1.05, 0.06, 0.005, "visored_trials:3"),
            "l3": (1200000, 1.80, 1.80, 1.55, 1.85, 1.11, 1.07, 0.09, 0.01, "visored_trials:4"),
            "l4": (2400000, 2.20, 2.20, 1.85, 2.25, 1.14, 1.10, 0.12, 0.015, "visored_trials:5"),
        }
        for f in u["visoredmask"]["formas"]:
            if f["id"] in vm_tiers:
                tp, s_m, p_m, d_m, k_m, sp, at, kd, sd, sg = vm_tiers[f["id"]]
                _set_form(f, tp=tp, str_m=s_m, pwr_m=p_m, def_m=d_m, skp_m=k_m, spd_m=sp, atk_m=at, drain_ki=kd, drain_stm=sd, saga=sg, stackable=True, stack_drain=1.5, incomp=visored_incomp)

    # 6. PICCOLO BIODATA, FRIEZA BIODATA & FROST GOD FORMS: Balanced stack multipliers (1.85x -> 3.10x instead of 5.6x -> 14.0x!)
    if "piccolobiodata" in u:
        for f in u["piccolobiodata"]["formas"]:
            if f["id"] == "orangebioandroid":
                _set_form(f, tp=600000, str_m=1.85, pwr_m=1.85, def_m=2.20, skp_m=1.85, spd_m=1.06, atk_m=1.04, drain_ki=0.12, saga="buu_saga:35", stackable=True, stack_drain=1.8, incomp=[])
            elif f["id"] == "orangegiantbioandroid":
                _set_form(f, tp=1800000, str_m=2.50, pwr_m=2.10, def_m=2.80, skp_m=2.10, spd_m=0.78, atk_m=0.72, drain_ki=0.16, saga="super_hero_saga:10", stackable=True, stack_drain=2.2, incomp=["cellmax.corruptedgiant"])

    if "friezabiodata" in u:
        for f in u["friezabiodata"]["formas"]:
            if f["id"] == "goldenbioandroid":
                _set_form(f, tp=800000, str_m=1.95, pwr_m=2.15, def_m=1.65, skp_m=2.05, spd_m=1.08, atk_m=1.05, drain_ki=0.14, saga="u7vsu6_saga:1", stackable=True, stack_drain=1.8, incomp=[])
            elif f["id"] == "blackbioandroid":
                _set_form(f, tp=2500000, str_m=2.80, pwr_m=3.00, def_m=2.30, skp_m=2.90, spd_m=1.14, atk_m=1.10, drain_ki=0.22, saga="granolah_saga:20", stackable=True, stack_drain=2.2, incomp=[])

    if "frostgodforms" in u:
        for f in u["frostgodforms"]["formas"]:
            if f["id"] == "golden":
                _set_form(f, tp=1500000, str_m=2.10, pwr_m=2.20, def_m=1.75, skp_m=2.15, spd_m=1.10, atk_m=1.06, drain_ki=0.20, saga="u7vsu6_saga:1", stackable=True, stack_drain=2.0, incomp=["evolutionforms.second", "evolutionforms.third"])
            elif f["id"] == "black":
                _set_form(f, tp=4000000, str_m=3.10, pwr_m=3.20, def_m=2.50, skp_m=3.15, spd_m=1.15, atk_m=1.10, drain_ki=0.30, saga="granolah_saga:20", stackable=True, stack_drain=2.4, incomp=["evolutionforms.second", "evolutionforms.third"])

    # 7. ULTRA EGO & ULTRA INSTINCT (Standard & X): Balanced Endgame Stack multipliers (1.75x -> 3.40x instead of 15x-30x!)
    if "ultraego" in u:
        for f in u["ultraego"]["formas"]:
            if f["id"] == "sign":
                _set_form(f, tp=1800000, str_m=1.75, pwr_m=1.75, def_m=1.90, skp_m=1.75, drain_ki=0.0, drain_stm=0.03, saga="moro_saga:24", stackable=True, stack_drain=1.8, incomp=["ultimate.ultimate", "ultrainstinct.sign", "ultrainstinct.mastered", "ultrainstinct.true", "ultrainstinctx.sign", "ultrainstinctx.mastered"])
            elif f["id"] == "mastered":
                _set_form(f, tp=3500000, str_m=2.35, pwr_m=2.35, def_m=2.60, skp_m=2.35, drain_ki=0.0, drain_stm=0.06, saga="granolah_saga:10", stackable=True, stack_drain=2.2, incomp=["ultimate.ultimate", "ultrainstinct.sign", "ultrainstinct.mastered", "ultrainstinct.true", "ultrainstinctx.sign", "ultrainstinctx.mastered"])

    if "ultrainstinct" in u:
        for f in u["ultrainstinct"]["formas"]:
            if f["id"] == "sign":
                _set_form(f, lvl=1, tp=1500000, str_m=1.85, pwr_m=1.85, def_m=1.80, skp_m=1.85, spd_m=1.15, atk_m=1.10, drain_ki=0.12, drain_stm=0.03, saga="top_saga:21", stackable=True, stack_drain=1.8, incomp=["ultimate.ultimate", "ultraego.sign", "ultraego.mastered", "ultraegox.sign", "ultraegox.mastered"])
            elif f["id"] == "mastered":
                _set_form(f, lvl=2, tp=3000000, str_m=2.35, pwr_m=2.35, def_m=2.45, skp_m=2.35, spd_m=1.22, atk_m=1.15, drain_ki=0.15, drain_stm=0.05, saga="top_saga:35", stackable=True, stack_drain=2.2, incomp=["ultimate.ultimate", "ultraego.sign", "ultraego.mastered", "ultraegox.sign", "ultraegox.mastered"])
            elif f["id"] == "true":
                _set_form(f, lvl=3, tp=5500000, str_m=2.90, pwr_m=2.90, def_m=3.00, skp_m=2.90, spd_m=1.25, atk_m=1.18, drain_ki=0.12, drain_stm=0.06, saga="granolah_saga:19", stackable=True, stack_drain=2.4, incomp=["ultimate.ultimate", "ultraego.sign", "ultraego.mastered", "ultraegox.sign", "ultraegox.mastered"])

    if "ultraegox" in u:
        for f in u["ultraegox"]["formas"]:
            if f["id"] == "sign":
                _set_form(f, tp=4500000, str_m=2.50, pwr_m=2.50, def_m=2.10, skp_m=2.55, spd_m=1.08, atk_m=1.06, drain_ki=0.0, drain_stm=0.05, saga="granolah_saga:8", stackable=True, stack_drain=2.2, incomp=["ultimate.ultimate", "ultrainstinct.sign", "ultrainstinct.mastered", "ultrainstinct.true", "ultrainstinctx.sign", "ultrainstinctx.mastered"])
            elif f["id"] == "mastered":
                _set_form(f, tp=10000000, str_m=3.40, pwr_m=3.40, def_m=2.80, skp_m=3.50, spd_m=1.14, atk_m=1.10, drain_ki=0.0, drain_stm=0.09, saga="granolah_saga:18", stackable=True, stack_drain=2.6, incomp=["ultimate.ultimate", "ultrainstinct.sign", "ultrainstinct.mastered", "ultrainstinct.true", "ultrainstinctx.sign", "ultrainstinctx.mastered"])

    if "ultrainstinctx" in u:
        for f in u["ultrainstinctx"]["formas"]:
            if f["id"] == "sign":
                _set_form(f, tp=4500000, str_m=2.30, pwr_m=2.30, def_m=2.55, skp_m=2.35, spd_m=1.18, atk_m=1.12, drain_ki=0.08, drain_stm=0.05, saga="moro_saga:21", stackable=True, stack_drain=2.2, incomp=["ultimate.ultimate", "ultraego.sign", "ultraego.mastered", "ultraegox.sign", "ultraegox.mastered"])
            elif f["id"] == "mastered":
                _set_form(f, tp=10000000, str_m=3.15, pwr_m=3.15, def_m=3.50, skp_m=3.20, spd_m=1.26, atk_m=1.18, drain_ki=0.12, drain_stm=0.09, saga="moro_saga:25", stackable=True, stack_drain=2.6, incomp=["ultimate.ultimate", "ultraego.sign", "ultraego.mastered", "ultraegox.sign", "ultraegox.mastered"])


def _make_raw_stage(
    *,
    level: int,
    hair_color: str,
    aura_color: str,
    lightning_color: str,
    scale: list[float] | None = None,
    hair_type: str = "base",
    body_color1: str = "",
    body_color2: str = "",
    body_color3: str = "",
    eye1: str = "",
    eye2: str = "",
    has_lightnings: bool = True,
    str_m: float = 4.0,
    pwr_m: float = 4.0,
    def_m: float = 4.0,
    skp_m: float = 4.0,
    spd_m: float = 1.0,
    atk_m: float = 1.0,
    drain_ki: float = 0.08,
    drain_stm: float = 0.0,
    saga: str = "",
    prev: str = "",
) -> dict[str, Any]:
    return {
        "unlockOnSkillLevel": level,
        "customModel": "",
        "bodyColor1": body_color1,
        "bodyColor2": body_color2,
        "bodyColor3": body_color3,
        "hairType": hair_type,
        "forcedHairCode": "",
        "hairColor": hair_color,
        "eye1Color": eye1,
        "eye2Color": eye2,
        "auraColor": aura_color,
        "hasLightnings": has_lightnings,
        "lightningColor": lightning_color,
        "modelScaling": scale or [1.0, 1.0, 1.0],
        "strMultiplier": str_m,
        "skpMultiplier": skp_m,
        "stmMultiplier": 1.0,
        "defMultiplier": def_m,
        "vitMultiplier": 1.0,
        "pwrMultiplier": pwr_m,
        "eneMultiplier": 1.0,
        "speedMultiplier": spd_m,
        "energyDrain": drain_ki,
        "staminaDrain": drain_stm,
        "healthDrain": 0.0,
        "attackSpeed": atk_m,
        "staminaDrainMultiplier": 1.0,
        "maxMastery": 100.0,
        "masteryPerHitDealt": 0.035,
        "masteryPerHitReceived": 0.035,
        "passiveMasteryEveryFiveSeconds": 0.005,
        "maxCostMultiplier": 0.5,
        "maxStatsMultiplier": 1.5,
        "instantTransformOnMastery": 25.0,
        "stackOnMastery": 0.0,
        "formStackable": True,
        "stackDrainMultiplier": 1.65,
        "requiredDMZLevel": 1,
        "levelRequisite": 0,
        "sagaRequisite": saga,
        "formRequisite": prev,
        "incompatibleWith": [],
    }


def _copy_race_form_file(races_dir: str, src_race: str, dst_race: str, filename: str) -> None:
    src = os.path.join(races_dir, src_race, "forms", filename)
    dst_dir = os.path.join(races_dir, dst_race, "forms")
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, filename)
    if os.path.isfile(src):
        shutil.copy2(src, dst)


def _remove_race_form_file(races_dir: str, race: str, filename: str) -> None:
    target = os.path.join(races_dir, race, "forms", filename)
    if os.path.isfile(target):
        os.remove(target)


def _write_race_form_tree(
    races_dir: str, race: str, filename: str, form_type: str, forms_map: dict[str, Any]
) -> None:
    dst_dir = os.path.join(races_dir, race, "forms")
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, filename)
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump({"formType": form_type, "forms": forms_map}, fh, indent=2, ensure_ascii=False)


def _ensure_race_char_costs(
    races_dir: str,
    race: str,
    new_costs: dict[str, dict[str, Any]],
    remove_keys: tuple[str, ...] = (),
) -> None:
    char_path = os.path.join(races_dir, race, "character.json")
    if not os.path.isfile(char_path):
        return
    with open(char_path, "r", encoding="utf-8") as fh:
        char_doc = json.load(fh)
    fsc = dict(char_doc.get("formSkillsCosts", {}))
    for rk in remove_keys:
        fsc.pop(rk, None)
    for k, v in new_costs.items():
        fsc[k] = v
    char_doc["formSkillsCosts"] = fsc
    with open(char_path, "w", encoding="utf-8") as fh:
        json.dump(char_doc, fh, indent=2, ensure_ascii=False)


def _provision_small_races_and_skills_json(dmz_config_dir: str) -> None:
    """Provision authentic lore trees for the 8 smaller races (peaking at 52x-60x, 100% stackable)."""
    races_dir = os.path.join(dmz_config_dir, "races")

    # 1. ANDROID: androidforms, gammaframeforms, majinandroidforms (remove generic fistforms)
    for fn in ("androidforms.json", "gammaframeforms.json", "majinandroidforms.json"):
        _copy_race_form_file(races_dir, "human", "android", fn)
    _remove_race_form_file(races_dir, "android", "fistforms.json")
    _ensure_race_char_costs(
        races_dir,
        "android",
        {
            "androidforms": {"buyFromMaster": False, "prices": [90000, 180000, 350000, 750000]},
            "majinandroidforms": {"buyFromMaster": False, "prices": [1250000]},
            "gammaframeforms": {"buyFromMaster": False, "prices": [2500000, 4500000]},
        },
        remove_keys=("fistforms",),
    )

    # 2. KAI (Shin-jin / Kaioh): superforms, kishinforms, legendaryforms (from glind)
    for fn in ("superforms.json", "kishinforms.json", "legendaryforms.json"):
        _copy_race_form_file(races_dir, "glind", "kai", fn)
    _ensure_race_char_costs(
        races_dir,
        "kai",
        {
            "superforms": {"buyFromMaster": False, "prices": [60000, 110000, 180000, 320000, 600000]},
            "kishinforms": {"buyFromMaster": False, "prices": [350000, 750000]},
            "legendaryforms": {"buyFromMaster": False, "prices": [750000, 1750000, 3750000]},
        },
    )

    # 3. KONATSIAN & TAPION: superforms + 3-stage legendaryforms (Konats Sword/Ocarina), remove generic fistforms
    _copy_race_form_file(races_dir, "tapion", "konatsian", "superforms.json")
    _remove_race_form_file(races_dir, "konatsian", "fistforms.json")
    _remove_race_form_file(races_dir, "tapion", "fistforms.json")
    konats_legendary = {
        "ocarina_guardian": _make_raw_stage(
            level=1,
            hair_color="#7DF9FF",
            aura_color="#38BDF8",
            lightning_color="#E0F2FE",
            str_m=15.0,
            pwr_m=14.0,
            def_m=12.5,
            skp_m=16.5,
            spd_m=1.14,
            atk_m=1.12,
            drain_ki=0.14,
            saga="buu_saga:10",
        ),
        "phantom_majin_slayer": _make_raw_stage(
            level=2,
            hair_color="#FDE047",
            aura_color="#F59E0B",
            lightning_color="#FEF08A",
            scale=[1.05, 1.05, 1.05],
            str_m=28.0,
            pwr_m=26.0,
            def_m=23.0,
            skp_m=31.0,
            spd_m=1.18,
            atk_m=1.15,
            drain_ki=0.18,
            saga="buu_saga:31",
            prev="ocarina_guardian",
        ),
        "eternal_brave_sword": _make_raw_stage(
            level=3,
            hair_type="ssj",
            hair_color="#F8FAFC",
            aura_color="#60A5FA",
            lightning_color="#FDE047",
            scale=[1.08, 1.08, 1.08],
            str_m=50.0,
            pwr_m=46.0,
            def_m=42.0,
            skp_m=56.0,
            spd_m=1.22,
            atk_m=1.18,
            drain_ki=0.22,
            saga="super_hero_saga:10",
            prev="phantom_majin_slayer",
        ),
    }
    for r_konats in ("konatsian", "tapion"):
        _write_race_form_tree(races_dir, r_konats, "legendaryforms.json", "legendaryforms", konats_legendary)
        _ensure_race_char_costs(
            races_dir,
            r_konats,
            {
                "superforms": {"buyFromMaster": False, "prices": [80000, 220000, 600000, 1800000]},
                "legendaryforms": {"buyFromMaster": False, "prices": [550000, 1400000, 3600000]},
            },
            remove_keys=("fistforms",),
        )

    # 4. TUFFLE (Tsufurujin / Baby): superforms (4 GT Baby stages) + parasiteforms (remove generic coreforms)
    _copy_race_form_file(races_dir, "bioandroid", "tuffle", "parasiteforms.json")
    _remove_race_form_file(races_dir, "tuffle", "coreforms.json")
    tuffle_super = {
        "baby_parasite": _make_raw_stage(
            level=1,
            hair_color="#E2E8F0",
            aura_color="#38BDF8",
            lightning_color="#EF4444",
            eye1="#EF4444",
            eye2="#EF4444",
            str_m=6.5,
            pwr_m=8.0,
            def_m=6.5,
            skp_m=8.0,
            spd_m=1.08,
            drain_ki=0.10,
            saga="gt_saga:7",
        ),
        "super_baby_1": _make_raw_stage(
            level=2,
            hair_type="ssj",
            hair_color="#F8FAFC",
            aura_color="#EC4899",
            lightning_color="#38BDF8",
            eye1="#EF4444",
            eye2="#EF4444",
            scale=[1.05, 1.05, 1.05],
            str_m=14.0,
            pwr_m=17.0,
            def_m=13.5,
            skp_m=17.0,
            spd_m=1.10,
            drain_ki=0.14,
            saga="gt_saga:9",
            prev="baby_parasite",
        ),
        "super_baby_2": _make_raw_stage(
            level=3,
            hair_type="ssj2",
            hair_color="#FFFFFF",
            aura_color="#A855F7",
            lightning_color="#F43F5E",
            eye1="#EF4444",
            eye2="#EF4444",
            scale=[1.08, 1.08, 1.08],
            str_m=26.0,
            pwr_m=32.0,
            def_m=25.0,
            skp_m=32.0,
            spd_m=1.12,
            drain_ki=0.18,
            saga="gt_saga:11",
            prev="super_baby_1",
        ),
        "golden_oozaru_baby": _make_raw_stage(
            level=4,
            hair_type="oozaru",
            body_color1="#FACC15",
            body_color2="#EAB308",
            body_color3="#CA8A04",
            hair_color="#FDE047",
            aura_color="#FACC15",
            lightning_color="#EF4444",
            eye1="#EF4444",
            eye2="#EF4444",
            scale=[3.2, 3.2, 3.2],
            str_m=56.0,
            pwr_m=50.0,
            def_m=54.0,
            skp_m=48.0,
            spd_m=0.78,
            atk_m=0.75,
            drain_ki=0.22,
            saga="gt_saga:12",
            prev="super_baby_2",
        ),
    }
    _write_race_form_tree(races_dir, "tuffle", "superforms.json", "superforms", tuffle_super)
    _ensure_race_char_costs(
        races_dir,
        "tuffle",
        {
            "superforms": {"buyFromMaster": False, "prices": [120000, 350000, 900000, 2200000]},
            "parasiteforms": {"buyFromMaster": False, "prices": [200000, 420000]},
        },
        remove_keys=("coreforms",),
    )

    # 5. WIZARD (Mago / Moro / Babidi): superforms (4 Magic/Moro stages) + maliceforms + chaosforms (remove generic abyssforms)
    _copy_race_form_file(races_dir, "majin", "wizard", "maliceforms.json")
    _copy_race_form_file(races_dir, "majin", "wizard", "chaosforms.json")
    _remove_race_form_file(races_dir, "wizard", "abyssforms.json")
    wizard_super = {
        "arcane_awakening": _make_raw_stage(
            level=1,
            hair_color="#C084FC",
            aura_color="#9333EA",
            lightning_color="#E9D5FF",
            str_m=4.0,
            pwr_m=6.5,
            def_m=4.2,
            skp_m=6.5,
            spd_m=1.05,
            drain_ki=0.04,
            saga="classic_saga:46",
        ),
        "babidi_sorcery": _make_raw_stage(
            level=2,
            hair_color="#FACC15",
            aura_color="#A855F7",
            lightning_color="#FDE047",
            str_m=8.5,
            pwr_m=14.5,
            def_m=9.0,
            skp_m=14.5,
            spd_m=1.08,
            drain_ki=0.02,
            saga="buu_saga:10",
            prev="arcane_awakening",
        ),
        "planet_eater_moro": _make_raw_stage(
            level=3,
            body_color1="#1E3A8A",
            body_color2="#1D4ED8",
            hair_color="#93C5FD",
            aura_color="#DC2626",
            lightning_color="#F87171",
            scale=[1.12, 1.12, 1.12],
            str_m=22.0,
            pwr_m=36.0,
            def_m=24.0,
            skp_m=36.0,
            spd_m=1.12,
            drain_ki=-0.05,
            saga="moro_saga:7",
            prev="babidi_sorcery",
        ),
        "angel_moro": _make_raw_stage(
            level=4,
            body_color1="#F8FAFC",
            body_color2="#E2E8F0",
            hair_color="#FFFFFF",
            aura_color="#E0F2FE",
            lightning_color="#38BDF8",
            scale=[1.10, 1.10, 1.10],
            str_m=44.0,
            pwr_m=60.0,
            def_m=42.0,
            skp_m=60.0,
            spd_m=1.20,
            atk_m=1.14,
            drain_ki=-0.08,
            saga="moro_saga:25",
            prev="planet_eater_moro",
        ),
    }
    _write_race_form_tree(races_dir, "wizard", "superforms.json", "superforms", wizard_super)
    _ensure_race_char_costs(
        races_dir,
        "wizard",
        {
            "superforms": {"buyFromMaster": False, "prices": [60000, 250000, 1200000, 3800000]},
            "maliceforms": {"buyFromMaster": False, "prices": [180000, 350000, 680000]},
            "chaosforms": {"buyFromMaster": False, "prices": [4500000, 11000000]},
        },
        remove_keys=("abyssforms",),
    )

    # 6. SHADOW DRAGON: expand superforms into 4 GT Dragons + maliceforms (remove generic abyssforms)
    _copy_race_form_file(races_dir, "majin", "shadow_dragon", "maliceforms.json")
    _remove_race_form_file(races_dir, "shadow_dragon", "abyssforms.json")
    shadow_super = {
        "rage_shenron": _make_raw_stage(
            level=1,
            hair_color="#FB923C",
            aura_color="#EA580C",
            lightning_color="#FDE047",
            scale=[1.15, 1.15, 1.15],
            str_m=6.5,
            pwr_m=7.0,
            def_m=8.0,
            skp_m=6.5,
            spd_m=0.92,
            drain_ki=0.10,
            saga="gt_saga:20",
        ),
        "nuova_shenron": _make_raw_stage(
            level=2,
            body_color1="#F59E0B",
            hair_color="#FDE047",
            aura_color="#F97316",
            lightning_color="#FEF08A",
            scale=[1.05, 1.05, 1.05],
            str_m=15.0,
            pwr_m=17.0,
            def_m=13.0,
            skp_m=17.0,
            spd_m=1.18,
            atk_m=1.12,
            drain_ki=0.14,
            saga="gt_saga:27",
            prev="rage_shenron",
        ),
        "syn_shenron": _make_raw_stage(
            level=3,
            body_color1="#F8FAFC",
            body_color2="#1E293B",
            hair_color="#94A3B8",
            aura_color="#6366F1",
            lightning_color="#EF4444",
            scale=[1.12, 1.12, 1.12],
            str_m=28.0,
            pwr_m=30.0,
            def_m=27.0,
            skp_m=29.0,
            spd_m=1.10,
            drain_ki=0.18,
            saga="gt_saga:30",
            prev="nuova_shenron",
        ),
        "omega_shenron": _make_raw_stage(
            level=4,
            body_color1="#FFFFFF",
            body_color2="#0F172A",
            hair_color="#E2E8F0",
            aura_color="#8B5CF6",
            lightning_color="#F43F5E",
            scale=[1.18, 1.18, 1.18],
            str_m=56.0,
            pwr_m=60.0,
            def_m=54.0,
            skp_m=58.0,
            spd_m=1.14,
            atk_m=1.10,
            drain_ki=0.22,
            saga="gt_saga:39",
            prev="syn_shenron",
        ),
    }
    _write_race_form_tree(races_dir, "shadow_dragon", "superforms.json", "superforms", shadow_super)
    _ensure_race_char_costs(
        races_dir,
        "shadow_dragon",
        {
            "superforms": {"buyFromMaster": False, "prices": [100000, 250000, 600000, 2000000]},
            "maliceforms": {"buyFromMaster": False, "prices": [180000, 350000, 680000]},
        },
        remove_keys=("abyssforms",),
    )

    # 7. FULLBRINGER: fullbringerforms + hogyokuforms (remove generic truezanpakutoforms)
    _copy_race_form_file(races_dir, "soulreaper", "fullbringer", "hogyokuforms.json")
    _remove_race_form_file(races_dir, "fullbringer", "truezanpakutoforms.json")
    _ensure_race_char_costs(
        races_dir,
        "fullbringer",
        {
            "fullbringerforms": {"buyFromMaster": False, "prices": [150000, 600000, 2500000]},
            "hogyokuforms": {"buyFromMaster": False, "prices": [1950000, 3200000]},
        },
        remove_keys=("truezanpakutoforms",),
    )

    # 8. Update skills.json so the 8 small races have access to their lore trees and stackSkills are active
    skills_path = os.path.join(dmz_config_dir, "skills.json")
    if os.path.isfile(skills_path):
        with open(skills_path, "r", encoding="utf-8") as fh:
            s_doc = json.load(fh)
        s_doc["androidBlacklistedForms"] = []
        stack_list = list(s_doc.get("stackSkills", []))
        for st_skill in (
            "kaioken",
            "ultimate",
            "piccolobiodata",
            "friezabiodata",
            "frostgodforms",
            "visoredmask",
            "godki",
            "godkienhancement",
            "kaipath_kai",
            "kaipath_hakaishin",
            "ultraego",
            "ultrainstinct",
            "ultraegox",
            "ultrainstinctx",
        ):
            if st_skill not in stack_list:
                stack_list.append(st_skill)
        s_doc["stackSkills"] = stack_list

        skills_map = dict(s_doc.get("skills", {}))
        race_grants = {
            "gammaframeforms": ["human", "android"],
            "majinandroidforms": ["human", "android"],
            "fistforms": ["human"],
            "kishinforms": ["glind", "kai"],
            "parasiteforms": ["bioandroid", "tuffle"],
            "coreforms": ["bioandroid"],
            "maliceforms": ["majin", "wizard", "shadow_dragon"],
            "chaosforms": ["majin", "wizard"],
            "abyssforms": ["makaijin"],
            "hogyokuforms": ["soulreaper", "fullbringer"],
            "truezanpakutoforms": ["soulreaper"],
            "visoredmask": ["soulreaper", "fullbringer"],
        }
        for sk_name, allowed in race_grants.items():
            if sk_name in skills_map:
                skills_map[sk_name]["allowedRaces"] = list(allowed)
        s_doc["skills"] = skills_map
        with open(skills_path, "w", encoding="utf-8") as fh:
            json.dump(s_doc, fh, indent=2, ensure_ascii=False)


def _balance_eight_expanded_races(cat: dict[str, Any]) -> None:
    """Balance the 8 small/expanded races up to 52x-60x with 100% stackable racial forms (so Peak * Stack = 165x-200x)."""
    # 1. ANDROID: Infinite Energy Cyborg (0 Ki drain, high DEF & SKP, peaks at 55x + Stack -> 185x!)
    r = "android"
    _set_form(_find_form(cat, r, "androidforms", "androidbase"), lvl=1, tp=90000, str_m=6.0, pwr_m=5.5, def_m=6.8, skp_m=6.0, drain_ki=0.0, saga="android_saga:8", stackable=True, stack_drain=1.5, incomp=[])
    _set_form(_find_form(cat, r, "androidforms", "superandroid"), lvl=2, tp=180000, str_m=10.5, pwr_m=9.5, def_m=12.0, skp_m=10.5, drain_ki=0.0, saga="android_saga:13", stackable=True, stack_drain=1.5, incomp=[])
    _set_form(_find_form(cat, r, "androidforms", "fusedandroid"), lvl=3, tp=350000, str_m=16.5, pwr_m=15.0, def_m=18.5, skp_m=16.5, drain_ki=0.0, saga="movies_saga:22", stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "androidforms", "superfusedandroid"), lvl=4, tp=750000, str_m=26.0, pwr_m=24.0, def_m=29.0, skp_m=26.5, drain_ki=0.0, saga="gt_saga:17", stackable=True, stack_drain=1.75, incomp=[])

    _set_form(_find_form(cat, r, "majinandroidforms", "majinandroid"), tp=1250000, str_m=22.0, pwr_m=24.0, def_m=25.0, skp_m=24.0, drain_ki=0.0, saga="buu_saga:21", stackable=True, stack_drain=1.7, incomp=[])

    _set_form(_find_form(cat, r, "gammaframeforms", "gammaframe"), tp=2500000, str_m=34.0, pwr_m=35.0, def_m=33.0, skp_m=36.0, spd_m=1.12, atk_m=1.06, drain_ki=0.0, saga="movies_saga:106", stackable=True, stack_drain=1.8, incomp=[])
    _set_form(_find_form(cat, r, "gammaframeforms", "majincircuit"), tp=2500000, str_m=35.0, pwr_m=36.0, def_m=37.0, skp_m=36.0, spd_m=1.10, atk_m=1.06, drain_ki=0.0, saga="movies_saga:106", stackable=True, stack_drain=1.8, incomp=[])
    _set_form(_find_form(cat, r, "gammaframeforms", "gammaoverdrive"), tp=4500000, str_m=52.0, pwr_m=54.0, def_m=42.0, skp_m=56.0, spd_m=1.18, atk_m=1.10, drain_ki=0.12, saga="movies_saga:107", stackable=True, stack_drain=2.0, incomp=[])

    # 2. KAI (Shin-jin / Kaioh): Divine Creation & Time Power (Peaks at 54x PWR/SKP + Stack -> 180x!)
    r = "kai"
    _set_form(_find_form(cat, r, "superforms", "buffed"), tp=60000, str_m=5.0, pwr_m=5.8, def_m=5.5, skp_m=5.8, saga="classic_saga:46", stackable=True, stack_drain=1.5, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "outofcontrol"), tp=110000, str_m=8.0, pwr_m=9.5, def_m=7.5, skp_m=9.5, saga="saiyan_saga:12", stackable=True, stack_drain=1.5, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "super"), tp=180000, str_m=12.0, pwr_m=15.0, def_m=13.0, skp_m=15.0, saga="frieza_saga:10", stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "absorption"), tp=320000, str_m=19.0, pwr_m=24.0, def_m=21.0, skp_m=24.0, saga="buu_saga:1", stackable=True, stack_drain=1.7, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "trueform"), tp=600000, str_m=28.0, pwr_m=35.0, def_m=31.0, skp_m=35.0, saga="buu_saga:35", stackable=True, stack_drain=1.8, incomp=[])

    _set_form(_find_form(cat, r, "kishinforms", "demongodawakened"), tp=350000, str_m=13.0, pwr_m=16.5, def_m=14.0, skp_m=16.5, saga="shadow_saga:2", stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "kishinforms", "demongodtrue"), tp=750000, str_m=21.0, pwr_m=26.0, def_m=22.0, skp_m=26.0, saga="shadow_saga:4", stackable=True, stack_drain=1.75, incomp=[])

    _set_form(_find_form(cat, r, "legendaryforms", "transcended"), tp=750000, str_m=11.0, pwr_m=14.0, def_m=12.5, skp_m=14.0, drain_ki=0.20, stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "legendaryforms", "darkking"), tp=1750000, str_m=22.0, pwr_m=28.0, def_m=24.0, skp_m=28.0, drain_ki=0.28, stackable=True, stack_drain=1.8, incomp=[])
    _set_form(_find_form(cat, r, "legendaryforms", "timepower_darkking"), tp=3750000, str_m=44.0, pwr_m=54.0, def_m=38.0, skp_m=54.0, drain_ki=0.35, stackable=True, stack_drain=2.0, incomp=[])
    _set_form(_find_form(cat, r, "legendaryforms", "timepower_realmoflight"), tp=3750000, str_m=38.0, pwr_m=50.0, def_m=54.0, skp_m=50.0, drain_ki=0.32, stackable=True, stack_drain=2.0, incomp=[])

    # 3. KONATSIAN & TAPION: Brave Sword & Hirudegarn Vessel (Peaks at 56x SKP / 50x STR + Stack -> 185x!)
    for r_konats in ("konatsian", "tapion"):
        _set_form(_find_form(cat, r_konats, "superforms", "resolve"), tp=80000, str_m=5.8, pwr_m=5.2, def_m=4.8, skp_m=6.5, spd_m=1.10, atk_m=1.08, saga="cell_saga:20", stackable=True, stack_drain=1.5, incomp=[])
        _set_form(_find_form(cat, r_konats, "superforms", "heroic_spirit"), tp=220000, str_m=10.5, pwr_m=9.5, def_m=8.8, skp_m=12.0, spd_m=1.14, atk_m=1.10, saga="buu_saga:10", stackable=True, stack_drain=1.6, incomp=[])
        _set_form(_find_form(cat, r_konats, "superforms", "brave_heart"), tp=600000, str_m=17.5, pwr_m=16.0, def_m=14.5, skp_m=20.0, spd_m=1.18, atk_m=1.14, saga="buu_saga:25", stackable=True, stack_drain=1.7, incomp=[])
        _set_form(_find_form(cat, r_konats, "superforms", "hirudegarn"), tp=1800000, str_m=36.0, pwr_m=32.0, def_m=38.0, skp_m=30.0, spd_m=0.78, atk_m=0.75, saga="buu_saga:37", stackable=True, stack_drain=1.9, incomp=[])

        _set_form(_find_form(cat, r_konats, "legendaryforms", "ocarina_guardian"), tp=550000, str_m=15.0, pwr_m=14.0, def_m=12.5, skp_m=16.5, spd_m=1.14, atk_m=1.12, saga="buu_saga:10", stackable=True, stack_drain=1.65, incomp=[])
        _set_form(_find_form(cat, r_konats, "legendaryforms", "phantom_majin_slayer"), tp=1400000, str_m=28.0, pwr_m=26.0, def_m=23.0, skp_m=31.0, spd_m=1.18, atk_m=1.15, saga="buu_saga:31", stackable=True, stack_drain=1.8, incomp=[])
        _set_form(_find_form(cat, r_konats, "legendaryforms", "eternal_brave_sword"), tp=3600000, str_m=50.0, pwr_m=46.0, def_m=42.0, skp_m=56.0, spd_m=1.22, atk_m=1.18, saga="super_hero_saga:10", stackable=True, stack_drain=2.0, incomp=[])

    # 4. TUFFLE (Tsufurujin / Baby): Parasitic Tech & Revenge Death Ball (Peaks at 56x + Stack -> 185x!)
    r = "tuffle"
    _set_form(_find_form(cat, r, "superforms", "baby_parasite"), tp=120000, str_m=6.5, pwr_m=8.0, def_m=6.5, skp_m=8.0, spd_m=1.08, saga="gt_saga:7", stackable=True, stack_drain=1.5, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "super_baby_1"), tp=350000, str_m=14.0, pwr_m=17.0, def_m=13.5, skp_m=17.0, spd_m=1.10, saga="gt_saga:9", stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "super_baby_2"), tp=900000, str_m=26.0, pwr_m=32.0, def_m=25.0, skp_m=32.0, spd_m=1.12, saga="gt_saga:11", stackable=True, stack_drain=1.8, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "golden_oozaru_baby"), tp=2200000, str_m=56.0, pwr_m=50.0, def_m=54.0, skp_m=48.0, spd_m=0.78, atk_m=0.75, saga="gt_saga:12", stackable=True, stack_drain=2.0, incomp=[])

    _set_form(_find_form(cat, r, "parasiteforms", "tuffleparasite"), tp=200000, str_m=12.0, pwr_m=14.0, def_m=11.0, skp_m=14.0, saga="shadow_saga:2", stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "parasiteforms", "hellcorruption"), tp=420000, str_m=20.0, pwr_m=24.0, def_m=18.5, skp_m=24.0, saga="shadow_saga:4", stackable=True, stack_drain=1.75, incomp=[])

    # 5. WIZARD (Mago / Moro): Magic & Ki Absorption (Peaks at 60x PWR/SKP + Stack -> 195x!)
    r = "wizard"
    _set_form(_find_form(cat, r, "superforms", "arcane_awakening"), tp=60000, str_m=4.0, pwr_m=6.5, def_m=4.2, skp_m=6.5, spd_m=1.05, drain_ki=0.04, saga="classic_saga:46", stackable=True, stack_drain=1.5, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "babidi_sorcery"), tp=250000, str_m=8.5, pwr_m=14.5, def_m=9.0, skp_m=14.5, spd_m=1.08, drain_ki=0.02, saga="buu_saga:10", stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "planet_eater_moro"), tp=1200000, str_m=22.0, pwr_m=36.0, def_m=24.0, skp_m=36.0, spd_m=1.12, drain_ki=-0.05, saga="moro_saga:7", stackable=True, stack_drain=1.8, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "angel_moro"), tp=3800000, str_m=44.0, pwr_m=60.0, def_m=42.0, skp_m=60.0, spd_m=1.20, atk_m=1.14, drain_ki=-0.08, saga="moro_saga:25", stackable=True, stack_drain=2.0, incomp=[])

    _set_form(_find_form(cat, r, "maliceforms", "darkmaskbuu"), tp=180000, str_m=8.5, pwr_m=11.5, def_m=9.0, skp_m=11.5, saga="shadow_saga:2", stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "maliceforms", "hatredincarnate"), tp=350000, str_m=13.5, pwr_m=18.0, def_m=13.0, skp_m=18.0, saga="shadow_saga:4", stackable=True, stack_drain=1.7, incomp=[])
    _set_form(_find_form(cat, r, "maliceforms", "absorptiontyrant"), tp=680000, str_m=19.0, pwr_m=26.0, def_m=21.0, skp_m=26.0, saga="shadow_saga:6", stackable=True, stack_drain=1.8, incomp=[])

    _set_form(_find_form(cat, r, "chaosforms", "rampagemajin"), tp=4500000, str_m=28.0, pwr_m=38.0, def_m=25.0, skp_m=38.0, spd_m=1.12, atk_m=1.10, stackable=True, stack_drain=1.9, incomp=[])
    _set_form(_find_form(cat, r, "chaosforms", "absorbedascendant"), tp=11000000, str_m=40.0, pwr_m=54.0, def_m=46.0, skp_m=54.0, spd_m=1.08, stackable=True, stack_drain=2.0, incomp=[])

    # 6. SHADOW DRAGON: 4 GT Shadow Dragons (Peaks at 60x Omega Shenron + Stack -> 195x!)
    r = "shadow_dragon"
    _set_form(_find_form(cat, r, "superforms", "rage_shenron"), tp=100000, str_m=6.5, pwr_m=7.0, def_m=8.0, skp_m=6.5, spd_m=0.92, saga="gt_saga:20", stackable=True, stack_drain=1.5, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "nuova_shenron"), tp=250000, str_m=15.0, pwr_m=17.0, def_m=13.0, skp_m=17.0, spd_m=1.18, atk_m=1.12, saga="gt_saga:27", stackable=True, stack_drain=1.65, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "syn_shenron"), tp=600000, str_m=28.0, pwr_m=30.0, def_m=27.0, skp_m=29.0, spd_m=1.10, saga="gt_saga:30", stackable=True, stack_drain=1.8, incomp=[])
    _set_form(_find_form(cat, r, "superforms", "omega_shenron"), tp=2000000, str_m=56.0, pwr_m=60.0, def_m=54.0, skp_m=58.0, spd_m=1.14, atk_m=1.10, saga="gt_saga:39", stackable=True, stack_drain=2.0, incomp=[])

    _set_form(_find_form(cat, r, "maliceforms", "darkmaskbuu"), tp=180000, str_m=9.5, pwr_m=10.5, def_m=10.0, skp_m=10.5, saga="shadow_saga:2", stackable=True, stack_drain=1.6, incomp=[])
    _set_form(_find_form(cat, r, "maliceforms", "hatredincarnate"), tp=350000, str_m=15.0, pwr_m=16.5, def_m=14.5, skp_m=16.5, saga="shadow_saga:4", stackable=True, stack_drain=1.7, incomp=[])
    _set_form(_find_form(cat, r, "maliceforms", "absorptiontyrant"), tp=680000, str_m=22.0, pwr_m=24.0, def_m=23.0, skp_m=24.0, saga="shadow_saga:6", stackable=True, stack_drain=1.8, incomp=[])

    # 7. FULLBRINGER (Bleach): High Speed & SKP/STR, Fragile DEF (Peaks at 52x Hogyoku + Stack/Mask -> 175x!)
    r = "fullbringer"
    _set_form(_find_form(cat, r, "fullbringerforms", "partial"), tp=150000, str_m=9.0, pwr_m=8.5, def_m=6.5, skp_m=9.5, spd_m=1.15, atk_m=1.10, saga="fullbring_trials:3", stackable=True, stack_drain=1.5, incomp=[])
    _set_form(_find_form(cat, r, "fullbringerforms", "fullbring"), tp=600000, str_m=20.0, pwr_m=18.5, def_m=14.0, skp_m=21.0, spd_m=1.22, atk_m=1.15, saga="fullbring_trials:4", stackable=True, stack_drain=1.65, incomp=[])
    _set_form(_find_form(cat, r, "fullbringerforms", "complete"), tp=2500000, str_m=36.0, pwr_m=34.0, def_m=25.0, skp_m=38.0, spd_m=1.26, atk_m=1.18, saga="fullbring_trials:5", stackable=True, stack_drain=1.85, incomp=[])

    _set_form(_find_form(cat, r, "hogyokuforms", "hogyokuchrysalis"), tp=1950000, str_m=26.0, pwr_m=25.0, def_m=20.0, skp_m=27.0, spd_m=1.18, atk_m=1.10, saga="shadow_saga:4", stackable=True, stack_drain=1.8, incomp=[])
    _set_form(_find_form(cat, r, "hogyokuforms", "hogyokuascended"), tp=3200000, str_m=50.0, pwr_m=48.0, def_m=38.0, skp_m=52.0, spd_m=1.24, atk_m=1.15, saga="shadow_saga:6", stackable=True, stack_drain=2.0, incomp=[])


def _balance_stackability_rules(cat: dict[str, Any]) -> None:
    """Enforce selective stackability on the 14 main races and full racial stackability on the 8 small races."""
    small_eight = {
        "android",
        "kai",
        "konatsian",
        "tapion",
        "tuffle",
        "wizard",
        "shadow_dragon",
        "fullbringer",
    }

    # 1. For the 8 smaller races: all racial trees are stackable EXCEPT racial ultraego/ultrainstinct
    for r_key in small_eight:
        r_obj = cat["racas"].get(r_key, {})
        for t_key, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
            is_ui_ue = t_key in ("ultraego", "ultrainstinct")
            for f in t_obj.get("formas", []):
                f["drenos"]["acumulavel"] = not is_ui_ue
                if is_ui_ue:
                    f["requisitos"]["incompativel_com"] = ["ultimate.ultimate"]

    # 2. For SAIYAN: apply strict stack rules so apex/giant/berserker/evolved forms cannot stack
    saiyan_stackable_ids: dict[str, set[str]] = {
        "supersaiyan": {
            "supersaiyan",
            "supersaiyanmastered",
            "supersaiyan2",
            "supersaiyan3",
            "supersaiyan4",
        },
        "ssgrades": {"supersaiyan", "supersaiyangrade2"},
        "corruptedforms": {"majinmark", "evilsaiyan", "evilsupersaiyan"},
        "createdforms": {"createdform", "createdform2"},
        "divinerose": {"supersaiyanrose"},
        "godforms": {"super_saiyan_blue"},
        "evildivineforms": {"supersaiyanrose"},
        "legendaryforms": {"ikari", "ssjhybrid"},
        "supersaiyanx": {"supersaiyan1", "supersaiyan2", "supersaiyan3", "supersaiyan4"},
    }
    saiyan_obj = cat["racas"].get("saiyan", {})
    for t_key, t_obj in saiyan_obj.get("arvores_de_transformacao", {}).items():
        allowed_ids = saiyan_stackable_ids.get(t_key, set())
        for f in t_obj.get("formas", []):
            can_stack = f["id"] in allowed_ids
            f["drenos"]["acumulavel"] = can_stack
            if can_stack and f["multiplicador_numerico_base"] >= 50.0:
                f["drenos"]["mult_dreno_stack"] = 2.5
            elif can_stack:
                f["drenos"]["mult_dreno_stack"] = 2.0
            # Clean empty string incompatibilities and keep Ultimate blocked on Legendary/SSJX/SSJ4+/Blue/Rosé
            if t_key in ("legendaryforms", "supersaiyanx", "dmzsparking_af") or f["id"] in (
                "super_saiyan_blue",
                "supersaiyanrose",
                "supersaiyan4fp",
                "supersaiyan4lb",
                "supersaiyan5daima",
                "supersaiyan5",
            ):
                f["requisitos"]["incompativel_com"] = ["ultimate.ultimate"]
            else:
                f["requisitos"]["incompativel_com"] = [
                    x for x in f["requisitos"].get("incompativel_com", []) if x
                ]

    # 3. For the other 13 Main Races: allow stacking ONLY on early/mid-game non-giant forms (<= 25x)
    non_stack_trees = {
        "ultraego",
        "ultrainstinct",
        "beastforms",
        "cellmax",
        "biogodforms",
        "sageforms",
        "geneticforms",
        "chaosforms",
        "infernalforms",
        "cosmosforms",
        "predatorforms",
        "chronoforms",
        "fistforms",
        "dragonforms",
        "glacierforms",
        "coreforms",
        "miraforms",
        "truezanpakutoforms",
        "eonforms",
        "abyssforms",
        "crownforms",
    }
    giant_or_berserk_ids = {
        "giant",
        "orange_giant",
        "awakenedgoldengiant",
        "corruptedgiant",
        "giantinnocencedemon",
        "giantofthepit",
        "coronagiant",
        "dunetitan",
        "vastolorde",
        "mugetsu",
        "supersaiyangrade3",
        "outofcontrol",
    }
    for r_key, r_obj in cat["racas"].items():
        if r_key in small_eight or r_key == "saiyan":
            continue
        for t_key, t_obj in r_obj.get("arvores_de_transformacao", {}).items():
            for f in t_obj.get("formas", []):
                base_mult = float(f.get("multiplicador_numerico_base", 1.0))
                fid = f["id"]
                if (
                    t_key in non_stack_trees
                    or fid in giant_or_berserk_ids
                    or base_mult > 26.0
                ):
                    f["drenos"]["acumulavel"] = False
                else:
                    f["drenos"]["acumulavel"] = True
                    f["drenos"]["mult_dreno_stack"] = 2.25 if base_mult >= 18.0 else 2.0
                # Clean empty strings in incompativel_com
                f["requisitos"]["incompativel_com"] = [
                    x for x in f["requisitos"].get("incompativel_com", []) if x
                ]


def balance_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(catalog)
    _clean_saiyan_secondary_stats_and_priceless(out)
    _sync_racial_ui_and_ue(out)
    _balance_half_saiyan(out)
    _balance_human(out)
    _balance_namekian(out)
    _balance_frostdemon(out)
    _balance_bioandroid(out)
    _balance_majin(out)
    _balance_soulreaper(out)
    _balance_custom_six_races(out)
    _balance_eight_expanded_races(out)
    _balance_universal_forms(out)
    _balance_stackability_rules(out)

    for r_obj in out["racas"].values():
        _sync_race_slot_prices(r_obj)
    return out


def main() -> None:
    inst_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dmz_config_dir = DEFAULT_DMZ_CONFIG_DIR or os.path.join(
        inst_dir, "config", "dragonminez"
    )
    desktop_json = DEFAULT_DESKTOP_JSON or os.path.join(
        os.path.expanduser("~"), "Desktop", "Dragon_Mine_Z_Transformacoes.json"
    )
    instance_json = DEFAULT_INSTANCE_JSON or os.path.join(
        dmz_config_dir, "todas_as_transformacoes.json"
    )

    # Preserve the user's balanced Saiyan tree from the existing Desktop JSON
    prev_cat = load_catalog_from_json(desktop_json)
    saiyan_saved = copy.deepcopy(prev_cat["racas"]["saiyan"])

    # Provision the 8 small/sparse races, unlock stackSkills/allowedRaces, and reload modpack
    _provision_small_races_and_skills_json(dmz_config_dir)
    cat = load_catalog_from_modpack(dmz_config_dir)
    cat["racas"]["saiyan"] = saiyan_saved
    cat["total_transformacoes"] = sum(
        r["total_formas"] for r in cat["racas"].values()
    )

    balanced = balance_catalog(cat)
    balanced["caminho_modpack"] = ""
    written = save_catalog_to_json(
        balanced, [desktop_json, instance_json]
    )
    modpack_res = apply_catalog_to_modpack(
        balanced, dmz_config_dir, create_backup=True
    )

    priceless_count = 0
    stackable_racial = 0
    non_stackable_racial = 0
    for r_key, r_obj in balanced["racas"].items():
        for t_key, t_obj in r_obj["arvores_de_transformacao"].items():
            for f in t_obj["formas"]:
                if f["custo_tp_numerico"] < 0:
                    priceless_count += 1
                if f["drenos"]["acumulavel"]:
                    stackable_racial += 1
                else:
                    non_stackable_racial += 1
    for g_key, g_obj in balanced["formas_universais_e_stack"].items():
        for f in g_obj["formas"]:
            if f["custo_tp_numerico"] < 0:
                priceless_count += 1

    print("JSONs saved:", written)
    print("Modpack apply result:", modpack_res)
    print("Total racial transformations:", balanced["total_transformacoes"])
    print(f"Racial Stackable: {stackable_racial} | Non-Stackable: {non_stackable_racial}")
    print("Remaining Priceless (-1) forms:", priceless_count)


if __name__ == "__main__":
    main()
