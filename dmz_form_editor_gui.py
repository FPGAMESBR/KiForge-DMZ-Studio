"""Visual Desktop GUI & Localhost API Server for Dragon Mine Z Transformations.

Serves the interactive 3-pane editor strictly on 127.0.0.1 with per-session
CSRF token protection, immutable Undo/Redo snapshots, configurable modpack path,
and native pywebview window.
"""

from __future__ import annotations

import argparse
import copy
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import secrets
import subprocess
import sys
import threading
from typing import Any
import webbrowser

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

# Ensure standalone editor directory is importable when launched directly via pythonw.exe
_PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dmz_form_editor_core import (  # noqa: E402
    DEFAULT_DESKTOP_JSON,
    DEFAULT_DMZ_CONFIG_DIR,
    DEFAULT_INSTANCE_JSON,
    SecurityPathError,
    add_form,
    apply_batch_balance,
    apply_batch_scale,
    apply_form_update,
    MASTER_FRIENDLY_NAMES,
    default_allowed_roots,
    delete_form,
    validate_allowed_path,
    init_studio_state,
    compute_catalog_diff,
    clone_stage,
    auto_scale_group,
    reorder_group_stages,
    reorder_race_groups,
    add_to_staging_dock,
    remove_from_staging_dock,
    allocate_staging_to_tree,
    create_wizard_form,
    simulate_drain,
)
from dmz_form_editor_io import (  # noqa: E402
    apply_catalog_to_modpack,
    load_catalog_from_json,
    load_catalog_from_modpack,
    save_catalog_to_json,
    scan_dmz_addons,
    toggle_addon_mod,
    get_backup_dir,
    create_zip_backup,
    open_backup_folder,
    resolve_dmz_config_dir,
    export_selective_mold,
    parse_import_payload,
    inspect_mod_jars,
)
from dmz_form_editor_sagas import run_health_check  # noqa: E402
from balance_all_races import balance_catalog  # noqa: E402
from dmz_form_editor_sagas import (  # noqa: E402
    extract_modpack_sagas,
    load_editor_settings,
    resolve_modpack_config_dir,
    save_editor_settings,
)

_BUNDLE_DIR = getattr(sys, "_MEIPASS", _PROJECT_ROOT)
_APP_DIR = (
    os.path.dirname(os.path.abspath(sys.executable))
    if getattr(sys, "frozen", False)
    else _PROJECT_ROOT
)
ASSETS_DIR = os.path.join(_BUNDLE_DIR, "assets")
DEFAULT_SETTINGS_PATH = os.path.join(
    _APP_DIR, "dmz_editor_settings.json"
)
MAX_HISTORY = 30
MAX_BODY_BYTES = 2 * 1024 * 1024


def _empty_catalog() -> dict[str, Any]:
    return {
        "titulo": "Dragon Mine Z - Guia Completo de Transformações, Custos de TP e Multiplicadores de BP",
        "versao_modpack": "Dragon Mine Z RPG 1.20.1",
        "caminho_modpack": "",
        "total_racas": 0,
        "total_transformacoes": 0,
        "racas": {},
        "formas_universais_e_stack": {},
        "opcoes_sagas": extract_modpack_sagas(None, {}),
        "opcoes_mestres": [
            {"id": m_id, "nome": m_name}
            for m_id, m_name in sorted(MASTER_FRIENDLY_NAMES.items(), key=lambda x: x[1])
        ],
    }


def _powershell_pick_folder(start_dir: str = "") -> str:
    """Native topmost Windows folder picker via isolated PowerShell process."""
    start = (
        start_dir
        if (start_dir and os.path.isdir(start_dir))
        else os.path.expanduser("~")
    )
    clean_start = start.replace("'", "''")
    script = (
        "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; "
        "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
        "$f.Description = 'Selecione a pasta do Modpack ou config/dragonminez'; "
        f"$f.SelectedPath = '{clean_start}'; "
        "$f.ShowNewFolderButton = $false; "
        "$form = New-Object System.Windows.Forms.Form; "
        "$form.TopMost = $true; "
        "if ($f.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) { "
        "    Write-Output $f.SelectedPath "
        "}"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            creationflags=0x08000000,
            timeout=180,
        )
        return res.stdout.strip()
    except Exception:
        return ""


def _powershell_pick_json(start_dir: str = "") -> str:
    """Native topmost Windows OpenFileDialog via isolated PowerShell process."""
    start = (
        start_dir
        if (start_dir and os.path.isdir(start_dir))
        else os.path.expanduser("~")
    )
    clean_start = start.replace("'", "''")
    script = (
        "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; "
        "$f = New-Object System.Windows.Forms.OpenFileDialog; "
        "$f.Title = 'Selecione o arquivo .json de Transformações'; "
        "$f.Filter = 'Arquivos JSON (*.json)|*.json|Todos os Arquivos (*.*)|*.*'; "
        f"$f.InitialDirectory = '{clean_start}'; "
        "$form = New-Object System.Windows.Forms.Form; "
        "$form.TopMost = $true; "
        "if ($f.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) { "
        "    Write-Output $f.FileName "
        "}"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            creationflags=0x08000000,
            timeout=180,
        )
        return res.stdout.strip()
    except Exception:
        return ""


class EditorController:
    """Thread-safe controller managing immutable catalog snapshots and persistence."""

    def __init__(
        self,
        dmz_config_dir: str = DEFAULT_DMZ_CONFIG_DIR,
        desktop_json_path: str = DEFAULT_DESKTOP_JSON,
        instance_json_path: str = DEFAULT_INSTANCE_JSON,
        allowed_roots: list[str] | None = None,
        settings_path: str | None = None,
    ) -> None:
        self._lock = threading.Lock()
        self._strict_roots = allowed_roots is not None
        self._allowed_roots = (
            list(allowed_roots)
            if allowed_roots is not None
            else default_allowed_roots()
        )
        self._settings_path = (
            settings_path
            if settings_path is not None
            else (None if self._strict_roots else DEFAULT_SETTINGS_PATH)
        )
        self._dmz_config_dir = dmz_config_dir if (dmz_config_dir and os.path.isdir(dmz_config_dir)) else ""
        self._desktop_json_path = desktop_json_path if (desktop_json_path and os.path.isfile(desktop_json_path)) else (desktop_json_path if self._strict_roots else "")
        self._instance_json_path = instance_json_path if (instance_json_path and os.path.isfile(instance_json_path)) else (instance_json_path if self._strict_roots else "")
        self._window_ref: Any = None

        if self._settings_path:
            saved = load_editor_settings(self._settings_path)
            saved_dmz = saved.get("dmz_config_dir", "").strip()
            if saved_dmz and os.path.isdir(saved_dmz):
                self._dmz_config_dir = saved_dmz
                self._instance_json_path = os.path.join(
                    saved_dmz, "todas_as_transformacoes.json"
                )
                if not self._strict_roots:
                    self._authorize_modpack_root(saved_dmz)
            saved_json = saved.get("desktop_json_path", "").strip()
            if saved_json and os.path.isfile(saved_json):
                self._desktop_json_path = saved_json
                if not self._strict_roots:
                    j_dir = os.path.dirname(os.path.realpath(saved_json))
                    if j_dir and j_dir not in self._allowed_roots:
                        self._allowed_roots = [*self._allowed_roots, j_dir]

        self._undo_stack: list[dict[str, Any]] = []
        self._redo_stack: list[dict[str, Any]] = []
        self._dirty = False
        self._source = "unconfigured"
        self._language = "pt"
        if self._settings_path:
            try:
                saved_lang = load_editor_settings(self._settings_path).get("language", "pt")
                if saved_lang in ("pt", "en"):
                    self._language = saved_lang
            except Exception:
                pass
        self._staging_dock: list[dict[str, Any]] = []
        self._catalog = self._initial_load()
        self._baseline_state: dict[str, Any] = copy.deepcopy(self._catalog)

    def attach_window(self, window: Any) -> None:
        self._window_ref = window

    def _authorize_modpack_root(self, dmz_dir: str) -> None:
        real_dmz = os.path.realpath(dmz_dir)
        inst_root = os.path.dirname(os.path.dirname(real_dmz))
        for candidate in (real_dmz, inst_root):
            if candidate and candidate not in self._allowed_roots:
                self._allowed_roots = [*self._allowed_roots, candidate]

    def _initial_load(self) -> dict[str, Any]:
        for jpath in (self._desktop_json_path, self._instance_json_path):
            if jpath and os.path.isfile(jpath):
                try:
                    loaded = load_catalog_from_json(jpath, allowed_roots=self._allowed_roots)
                    if loaded and loaded.get("racas"):
                        self._source = "json"
                        return loaded
                except Exception:
                    pass
        if self._dmz_config_dir and os.path.isdir(self._dmz_config_dir):
            self._source = "modpack"
            return load_catalog_from_modpack(
                self._dmz_config_dir, allowed_roots=self._allowed_roots
            )
        self._source = "unconfigured"
        return _empty_catalog()

    def _build_state_unlocked(
        self, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        modpack_ok = bool(self._dmz_config_dir and os.path.isdir(self._dmz_config_dir))
        json_ok = bool(
            (self._desktop_json_path and os.path.isfile(self._desktop_json_path))
            or (self._instance_json_path and os.path.isfile(self._instance_json_path))
        )
        base: dict[str, Any] = {
            "ok": True,
            "catalog": self._catalog,
            "source": self._source,
            "needs_setup": not modpack_ok and not json_ok,
            "dirty": self._dirty,
            "can_undo": len(self._undo_stack) > 0,
            "can_redo": len(self._redo_stack) > 0,
            "modpack_available": modpack_ok,
            "desktop_json": self._desktop_json_path,
            "instance_json": self._instance_json_path,
            "dmz_config_dir": self._dmz_config_dir,
            "default_dmz_config_dir": DEFAULT_DMZ_CONFIG_DIR,
            "language": self._language,
            "staging_dock": self._staging_dock,
            "diff_count": len(compute_catalog_diff(self._baseline_state, self._catalog)),
            "health": run_health_check(self._catalog),
            "backup_dir": get_backup_dir(),
        }
        if extra:
            return {**base, **extra}
        return base

    def get_state_payload(self) -> dict[str, Any]:
        with self._lock:
            return self._build_state_unlocked()

    def _push_undo_unlocked(self) -> None:
        self._undo_stack = [*self._undo_stack[-(MAX_HISTORY - 1) :], self._catalog]
        self._redo_stack = []

    def update_form(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Payload inválido para atualização de forma.")
        with self._lock:
            next_catalog = apply_form_update(self._catalog, payload)
            self._push_undo_unlocked()
            self._catalog = next_catalog
            self._dirty = True
            return self._build_state_unlocked()

    def batch_balance(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Payload inválido para balanceamento em lote.")
        with self._lock:
            next_catalog = apply_batch_balance(self._catalog, payload)
            self._push_undo_unlocked()
            self._catalog = next_catalog
            self._dirty = True
            return self._build_state_unlocked()

    def batch_scale(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.batch_balance(payload)

    def undo(self) -> dict[str, Any]:
        with self._lock:
            if not self._undo_stack:
                return self._build_state_unlocked()
            prev = self._undo_stack[-1]
            self._undo_stack = self._undo_stack[:-1]
            self._redo_stack = [*self._redo_stack, self._catalog]
            self._catalog = prev
            self._dirty = True
            return self._build_state_unlocked()

    def redo(self) -> dict[str, Any]:
        with self._lock:
            if not self._redo_stack:
                return self._build_state_unlocked()
            nxt = self._redo_stack[-1]
            self._redo_stack = self._redo_stack[:-1]
            self._undo_stack = [*self._undo_stack, self._catalog]
            self._catalog = nxt
            self._dirty = True
            return self._build_state_unlocked()

    def add_form(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Payload inválido para adição de forma.")
        with self._lock:
            next_catalog = add_form(self._catalog, payload)
            self._push_undo_unlocked()
            self._catalog = next_catalog
            self._dirty = True
            return self._build_state_unlocked()

    def delete_form(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Payload inválido para remoção de forma.")
        with self._lock:
            next_catalog = delete_form(self._catalog, payload)
            self._push_undo_unlocked()
            self._catalog = next_catalog
            self._dirty = True
            return self._build_state_unlocked()

    def set_language(self, lang: str) -> dict[str, Any]:
        target = "en" if str(lang).strip().lower() == "en" else "pt"
        with self._lock:
            self._language = target
            if self._settings_path:
                try:
                    cur_settings = load_editor_settings(self._settings_path)
                    cur_settings["language"] = target
                    save_editor_settings(self._settings_path, cur_settings)
                except Exception:
                    pass
            return self._build_state_unlocked()

    def get_addons(self, force: bool = False) -> list[dict[str, Any]]:
        with self._lock:
            inst_dir = (
                os.path.dirname(os.path.dirname(self._dmz_config_dir))
                if self._dmz_config_dir
                else ""
            )
            return scan_dmz_addons(inst_dir, force=force)

    def open_mods_folder(self) -> dict[str, Any]:
        with self._lock:
            inst_dir = (
                os.path.dirname(os.path.dirname(self._dmz_config_dir))
                if self._dmz_config_dir
                else ""
            )
            if not inst_dir:
                raise ValueError("Nenhum Modpack configurado.")
            mods_dir = os.path.join(inst_dir, "mods")
            if not os.path.isdir(mods_dir):
                raise FileNotFoundError(f"Pasta de mods não encontrada: {mods_dir}")
            validate_allowed_path(mods_dir, allowed_roots=self._allowed_roots)
            try:
                os.startfile(mods_dir)
                return {"ok": True, "path": mods_dir}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

    def toggle_addon(self, filename: str, enable: bool) -> dict[str, Any]:
        with self._lock:
            inst_dir = (
                os.path.dirname(os.path.dirname(self._dmz_config_dir))
                if self._dmz_config_dir
                else ""
            )
            if not inst_dir:
                raise ValueError("Nenhum Modpack configurado.")
            res = toggle_addon_mod(
                inst_dir, filename, enable, allowed_roots=self._allowed_roots
            )
            addons = scan_dmz_addons(inst_dir)
            return {"ok": True, "res": res, "addons": addons}

    def update_paths(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Payload de configuração inválido.")

        if payload.get("clear_paths"):
            with self._lock:
                self._dmz_config_dir = ""
                self._desktop_json_path = ""
                self._instance_json_path = ""
                self._source = "unconfigured"
                self._catalog = _empty_catalog()
                self._dirty = False
                if self._settings_path:
                    save_editor_settings(
                        self._settings_path,
                        {"dmz_config_dir": "", "desktop_json_path": ""},
                    )
                return self._build_state_unlocked()

        raw_dmz = (
            DEFAULT_DMZ_CONFIG_DIR
            if payload.get("reset_default")
            else str(payload.get("dmz_config_dir") or "").strip()
        )
        raw_json = str(
            payload.get("desktop_json_path")
            if "desktop_json_path" in payload
            else self._desktop_json_path
        ).strip()

        if not raw_dmz and not raw_json:
            raise ValueError(
                "Selecione a pasta config do Modpack ou o arquivo .json de transformações."
            )

        with self._lock:
            if raw_dmz:
                resolved_dmz = resolve_modpack_config_dir(raw_dmz)
                if self._strict_roots:
                    validate_allowed_path(
                        resolved_dmz, allowed_roots=self._allowed_roots
                    )
                else:
                    self._authorize_modpack_root(resolved_dmz)

                new_desktop_json = raw_json
                if new_desktop_json:
                    if self._strict_roots:
                        validate_allowed_path(
                            new_desktop_json, allowed_roots=self._allowed_roots
                        )
                    else:
                        json_dir = os.path.dirname(os.path.realpath(new_desktop_json))
                        if json_dir and json_dir not in self._allowed_roots:
                            self._allowed_roots = [*self._allowed_roots, json_dir]

                if new_desktop_json and os.path.isfile(new_desktop_json):
                    fresh_catalog = load_catalog_from_json(
                        new_desktop_json, allowed_roots=self._allowed_roots
                    )
                    self._source = "json"
                else:
                    fresh_catalog = load_catalog_from_modpack(
                        resolved_dmz, allowed_roots=self._allowed_roots
                    )
                    self._source = "modpack"
                self._push_undo_unlocked()
                self._dmz_config_dir = resolved_dmz
                self._desktop_json_path = new_desktop_json
                self._instance_json_path = os.path.join(
                    resolved_dmz, "todas_as_transformacoes.json"
                )
                self._catalog = fresh_catalog
                self._dirty = False
            else:
                expanded_json = os.path.realpath(
                    os.path.expanduser(raw_json.strip('"'))
                )
                if not os.path.isfile(expanded_json):
                    raise ValueError(
                        f"Arquivo JSON não encontrado: {raw_json}"
                    )
                if self._strict_roots:
                    validate_allowed_path(
                        expanded_json, allowed_roots=self._allowed_roots
                    )
                else:
                    json_dir = os.path.dirname(expanded_json)
                    if json_dir and json_dir not in self._allowed_roots:
                        self._allowed_roots = [*self._allowed_roots, json_dir]

                fresh_catalog = load_catalog_from_json(
                    expanded_json, allowed_roots=self._allowed_roots
                )
                self._push_undo_unlocked()
                self._dmz_config_dir = ""
                self._instance_json_path = ""
                self._desktop_json_path = expanded_json
                self._catalog = fresh_catalog
                self._source = "json"
                self._dirty = False

            if self._settings_path:
                save_editor_settings(
                    self._settings_path,
                    {
                        "dmz_config_dir": self._dmz_config_dir,
                        "desktop_json_path": self._desktop_json_path,
                    },
                )
            return self._build_state_unlocked()

    def browse_folder(self) -> dict[str, Any]:
        start_dir = (
            self._dmz_config_dir
            if (self._dmz_config_dir and os.path.isdir(self._dmz_config_dir))
            else os.path.expanduser("~")
        )
        chosen = ""
        if self._window_ref is not None:
            try:
                import webview

                res = self._window_ref.create_file_dialog(
                    webview.FOLDER_DIALOG, directory=start_dir
                )
                if res and len(res) > 0:
                    chosen = str(res[0])
            except Exception:
                chosen = ""

        if not chosen and sys.platform == "win32":
            try:
                chosen = _powershell_pick_folder(start_dir)
            except Exception:
                chosen = ""

        if not chosen:
            try:
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                try:
                    chosen = filedialog.askdirectory(
                        initialdir=start_dir,
                        title="Selecione a pasta do Modpack ou config/dragonminez",
                    )
                finally:
                    root.destroy()
            except Exception:
                chosen = ""

        return {"ok": True, "path": chosen or "", "selected_path": chosen or ""}

    def browse_json_file(self) -> dict[str, Any]:
        start_dir = (
            os.path.dirname(self._desktop_json_path)
            if (self._desktop_json_path and os.path.isdir(os.path.dirname(self._desktop_json_path)))
            else os.path.expanduser("~")
        )
        chosen = ""
        if self._window_ref is not None:
            try:
                import webview

                res = self._window_ref.create_file_dialog(
                    webview.OPEN_DIALOG,
                    directory=start_dir,
                    file_types=("Arquivos JSON (*.json)", "Todos os arquivos (*.*)"),
                )
                if res and len(res) > 0:
                    chosen = str(res[0])
            except Exception:
                chosen = ""

        if not chosen and sys.platform == "win32":
            try:
                chosen = _powershell_pick_json(start_dir)
            except Exception:
                chosen = ""

        if not chosen:
            try:
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                try:
                    chosen = filedialog.askopenfilename(
                        initialdir=start_dir,
                        title="Selecione o arquivo .json de Transformações",
                        filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
                    )
                finally:
                    root.destroy()
            except Exception:
                chosen = ""

        return {"ok": True, "path": chosen or "", "selected_path": chosen or ""}

    def detect_known_locations(self) -> dict[str, Any]:
        """Auto-detect existing DMZ modpack folders and JSON files on this machine."""
        user_home = os.path.expanduser("~")
        desktop_dir = os.path.join(user_home, "Desktop")
        appdata_dir = os.path.expandvars(r"%APPDATA%\.minecraft\config\dragonminez")

        candidates_modpack = [
            os.path.join(desktop_dir, "Dragon_Mine_Z_Client", ".minecraft", "config", "dragonminez"),
            os.path.join(desktop_dir, "Dragon_Mine_Z_Client"),
            os.path.join(desktop_dir, "Dragon_Mine_Z_Server", "config", "dragonminez"),
            os.path.join(desktop_dir, "Dragon_Mine_Z_Server"),
            os.path.join(desktop_dir, "Dragon Mine Z- Definitive Edition-v1.0"),
            appdata_dir,
            DEFAULT_DMZ_CONFIG_DIR,
        ]

        candidates_json = [
            os.path.join(desktop_dir, "Dragon_Mine_Z_Transformacoes.json"),
            os.path.join(desktop_dir, "dmz_transformations_guide.json"),
            DEFAULT_DESKTOP_JSON,
            DEFAULT_INSTANCE_JSON,
        ]

        found_modpacks: list[str] = []
        for p in candidates_modpack:
            if p and os.path.isdir(p):
                real_p = os.path.realpath(p)
                if real_p not in found_modpacks:
                    found_modpacks.append(real_p)

        found_jsons: list[str] = []
        for j in candidates_json:
            if j and os.path.isfile(j):
                real_j = os.path.realpath(j)
                if real_j not in found_jsons:
                    found_jsons.append(real_j)

        return {
            "ok": True,
            "detected_modpacks": found_modpacks,
            "detected_jsons": found_jsons,
        }

    def reload_catalog(self, source: str = "modpack") -> dict[str, Any]:
        with self._lock:
            if (
                source == "modpack"
                and self._dmz_config_dir
                and os.path.isdir(self._dmz_config_dir)
            ):
                fresh = load_catalog_from_modpack(
                    self._dmz_config_dir, allowed_roots=self._allowed_roots
                )
                self._source = "modpack"
            else:
                target = (
                    self._desktop_json_path
                    if (self._desktop_json_path and os.path.isfile(self._desktop_json_path))
                    else self._instance_json_path
                )
                if not target or not os.path.isfile(target):
                    raise ValueError(
                        "Nenhum arquivo JSON ou pasta do Modpack configurada para recarregar."
                    )
                fresh = load_catalog_from_json(
                    target, allowed_roots=self._allowed_roots
                )
                self._source = "json"
            self._push_undo_unlocked()
            self._catalog = fresh
            self._dirty = False
            return self._build_state_unlocked()

    def _target_json_paths(self) -> list[str]:
        targets: list[str] = []
        if self._desktop_json_path and self._desktop_json_path.strip():
            targets.append(self._desktop_json_path)
        if self._instance_json_path and self._instance_json_path.strip():
            inst_parent = os.path.dirname(self._instance_json_path)
            if inst_parent and os.path.isdir(inst_parent):
                targets.append(self._instance_json_path)
        if not targets:
            desktop_path = os.path.join(
                os.path.expanduser("~"), "Desktop", "Dragon_Mine_Z_Transformacoes.json"
            )
            self._desktop_json_path = desktop_path
            d_dir = os.path.dirname(os.path.realpath(desktop_path))
            if d_dir and d_dir not in self._allowed_roots:
                self._allowed_roots = [*self._allowed_roots, d_dir]
            targets.append(desktop_path)
        return targets

    def save_json_only(self) -> dict[str, Any]:
        with self._lock:
            saved = save_catalog_to_json(
                self._catalog,
                self._target_json_paths(),
                allowed_roots=self._allowed_roots,
            )
            self._dirty = False
            return self._build_state_unlocked({"json_salvos": saved})

    def apply_to_modpack_and_json(self) -> dict[str, Any]:
        with self._lock:
            mod_res = apply_catalog_to_modpack(
                self._catalog,
                self._dmz_config_dir,
                allowed_roots=self._allowed_roots,
                create_backup=True,
            )

            # Auto-sync to companion modpack folders (Client, Server, CurseForge) if detected
            if not self._strict_roots:
                companion_dirs = [
                    r"c:\Users\Franklin\Desktop\Dragon_Mine_Z_Client\.minecraft\config\dragonminez",
                    r"c:\Users\Franklin\Desktop\Dragon_Mine_Z_Server\config\dragonminez",
                    r"c:\Users\Franklin\curseforge\minecraft\Instances\Dragon Mine Z (2)\config\dragonminez",
                ]
                for cdir in companion_dirs:
                    if (
                        os.path.isdir(cdir)
                        and os.path.realpath(cdir) != os.path.realpath(self._dmz_config_dir)
                    ):
                        try:
                            c_roots = [*self._allowed_roots, cdir, os.path.realpath(cdir)]
                            apply_catalog_to_modpack(
                                self._catalog,
                                cdir,
                                allowed_roots=c_roots,
                                create_backup=False,
                            )
                        except Exception:
                            pass

            saved = save_catalog_to_json(
                self._catalog,
                self._target_json_paths(),
                allowed_roots=self._allowed_roots,
            )
            self._dirty = False
            return self._build_state_unlocked(
                {
                    "arquivos_atualizados": mod_res["arquivos_atualizados"],
                    "pasta_backup": mod_res["pasta_backup"],
                    "json_salvos": saved,
                }
            )



    def get_diff(self) -> dict[str, Any]:
        with self._lock:
            diffs = compute_catalog_diff(self._baseline_state, self._catalog)
            return {"ok": True, "diffs": diffs, "total_diffs": len(diffs)}

    def open_backups_folder(self) -> dict[str, Any]:
        opened = open_backup_folder()
        return {"ok": opened, "backup_dir": get_backup_dir()}

    def clone_stage_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            race = str(payload.get("raca", "saiyan"))
            group = str(payload.get("arvore", "supersaiyan"))
            source_id = str(payload.get("source_id", ""))
            new_id = str(payload.get("new_id", f"{source_id}_clone"))
            new_name = str(payload.get("new_name", ""))
            self._catalog = clone_stage(self._catalog, race, group, source_id, new_id, new_name)
            self._push_undo_unlocked()
            self._dirty = True
            return self._build_state_unlocked({"selected_id": new_id})

    def auto_scale_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            race = str(payload.get("raca", "saiyan"))
            group = str(payload.get("arvore", "supersaiyan"))
            m_step = float(payload.get("multiplier_step_pct", 15.0))
            d_step = float(payload.get("drain_step_pct", 10.0))
            self._catalog = auto_scale_group(self._catalog, race, group, m_step, d_step)
            self._push_undo_unlocked()
            self._dirty = True
            return self._build_state_unlocked()

    def reorder_stages_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            race = str(payload.get("raca", "saiyan"))
            group = str(payload.get("arvore", "supersaiyan"))
            ordered = list(payload.get("ordered_ids", []))
            auto_lvl = bool(payload.get("auto_update_levels", True))
            start_lvl = int(payload.get("start_level", 1))
            self._catalog = reorder_group_stages(self._catalog, race, group, ordered, auto_lvl, start_lvl)
            self._push_undo_unlocked()
            self._dirty = True
            return self._build_state_unlocked()

    def reorder_groups_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            race = str(payload.get("raca", "saiyan"))
            ordered = list(payload.get("ordered_groups", []))
            self._catalog = reorder_race_groups(self._catalog, race, ordered)
            self._push_undo_unlocked()
            self._dirty = True
            return self._build_state_unlocked()

    def staging_import_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            raw = payload.get("payload")
            items = parse_import_payload(raw)
            for it in items:
                self._staging_dock = add_to_staging_dock(
                    self._staging_dock,
                    it.get("payload", {}),
                    item_type=it.get("type", "sub_form"),
                    source="import",
                    origin_hint=it.get("origin_hint", ""),
                )
            return self._build_state_unlocked({"imported_count": len(items)})

    def staging_delete_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            stg_id = str(payload.get("staging_id", ""))
            self._staging_dock = remove_from_staging_dock(self._staging_dock, stg_id)
            return self._build_state_unlocked()

    def staging_allocate_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            stg_id = str(payload.get("staging_id", ""))
            target_race = str(payload.get("target_race", "saiyan"))
            target_group = str(payload.get("target_group", "custom_group"))
            conflict = str(payload.get("conflict_mode", "rename"))
            new_id = payload.get("custom_id")
            self._catalog, self._staging_dock, fid = allocate_staging_to_tree(
                self._catalog, self._staging_dock, stg_id, target_race, target_group, conflict, new_id
            )
            self._push_undo_unlocked()
            self._dirty = True
            return self._build_state_unlocked({"allocated_id": fid})

    def wizard_create_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._catalog = create_wizard_form(
                self._catalog,
                group_id=str(payload.get("group_id", "")),
                group_name=str(payload.get("group_name", "")),
                target_race=str(payload.get("target_race", "saiyan")),
                is_universal=bool(payload.get("is_universal", False)),
                num_stages=int(payload.get("num_stages", 1)),
                base_name=str(payload.get("base_name", "")),
                base_hair=str(payload.get("base_hair", "base")),
                base_aura=str(payload.get("base_aura", "kakarot")),
                base_color_hair=str(payload.get("base_color_hair", "#FFE89E")),
                base_color_aura=str(payload.get("base_color_aura", "#FFD700")),
            )
            self._push_undo_unlocked()
            self._dirty = True
            return self._build_state_unlocked({"new_group": payload.get("group_id")})

    def selective_export_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            selection = payload.get("selection", {})
            author = str(payload.get("author", "KiForge User"))
            notes = str(payload.get("notes", ""))
            mold = export_selective_mold(self._catalog, selection, author, notes)
            return {"ok": True, "mold": mold}

    def simulate_drain_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        form_data = payload.get("form", {})
        base_ki = float(payload.get("base_ki", 1000.0))
        base_stm = float(payload.get("base_stm", 1000.0))
        base_hp = float(payload.get("base_hp", 1000.0))
        sim = simulate_drain(form_data, base_ki, base_stm, base_hp)
        return {"ok": True, "simulation": sim}

    def auto_balance_all_action(self) -> dict[str, Any]:
        with self._lock:
            self._catalog = balance_catalog(self._catalog)
            self._push_undo_unlocked()
            self._dirty = True
            return self._build_state_unlocked()


STATIC_ASSETS: dict[str, tuple[str, str]] = {
    "/assets/dmz_form_editor.css": (
        "dmz_form_editor.css",
        "text/css; charset=utf-8",
    ),
    "/assets/dmz_form_editor.js": (
        "dmz_form_editor.js",
        "application/javascript; charset=utf-8",
    ),
    "/assets/dmz_form_editor_presets.js": (
        "dmz_form_editor_presets.js",
        "application/javascript; charset=utf-8",
    ),
    "/assets/kiforge_logo.png": (
        "kiforge_logo.png",
        "image/png",
    ),
    "/assets/favicon.ico": (
        "favicon.ico",
        "image/x-icon",
    ),
    "/assets/three.min.js": (
        "three.min.js",
        "application/javascript; charset=utf-8",
    ),
    "/assets/OrbitControls.js": (
        "OrbitControls.js",
        "application/javascript; charset=utf-8",
    ),
}


def create_http_server(
    controller: EditorController,
) -> tuple[ThreadingHTTPServer, str, str]:
    """Create a localhost-only HTTP server bound to an ephemeral port."""
    csrf_token = secrets.token_urlsafe(24)

    class EditorRequestHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def _send_bytes(
            self, status: int, content_type: str, body: bytes
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self' 'unsafe-inline'",
            )
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: int, data: dict[str, Any]) -> None:
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self._send_bytes(status, "application/json; charset=utf-8", raw)

        def _read_json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > MAX_BODY_BYTES:
                raise ValueError("Payload excede o tamanho máximo permitido.")
            if length == 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError("Corpo JSON deve ser um objeto.")
            return parsed

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/":
                html_path = os.path.join(ASSETS_DIR, "dmz_form_editor.html")
                with open(html_path, "r", encoding="utf-8") as fh:
                    html = fh.read().replace("{{CSRF_TOKEN}}", csrf_token)
                self._send_bytes(
                    200, "text/html; charset=utf-8", html.encode("utf-8")
                )
                return

            if path in STATIC_ASSETS:
                fname, mime = STATIC_ASSETS[path]
                asset_path = os.path.join(ASSETS_DIR, fname)
                with open(asset_path, "rb") as fh:
                    self._send_bytes(200, mime, fh.read())
                return

            if path == "/api/state":
                self._send_json(200, controller.get_state_payload())
                return

            if path == "/api/addons":
                force = "force=1" in self.path or "reload=1" in self.path
                self._send_json(200, {"ok": True, "addons": controller.get_addons(force=force)})
                return

            self._send_json(404, {"ok": False, "error": "Rota não encontrada."})

        def do_POST(self) -> None:  # noqa: N802
            sent_token = self.headers.get("X-DMZ-Token", "")
            if not sent_token or not hmac.compare_digest(sent_token, csrf_token):
                self._send_json(
                    403, {"ok": False, "error": "Token de sessão inválido (CSRF)."}
                )
                return

            path = self.path.split("?", 1)[0]
            try:
                body = self._read_json_body()
                if path == "/api/update-form":
                    self._send_json(200, controller.update_form(body))
                elif path == "/api/form/add":
                    self._send_json(200, controller.add_form(body))
                elif path == "/api/form/delete":
                    self._send_json(200, controller.delete_form(body))
                elif path == "/api/addons/toggle":
                    fname = str(body.get("filename", "")).strip()
                    en = bool(body.get("enabled", True))
                    self._send_json(200, controller.toggle_addon(fname, en))
                elif path == "/api/addons/open-folder":
                    self._send_json(200, controller.open_mods_folder())
                elif path == "/api/language":
                    lang = str(body.get("language", "pt"))
                    self._send_json(200, controller.set_language(lang))
                elif path in ("/api/batch-scale", "/api/batch-balance"):
                    self._send_json(200, controller.batch_balance(body))
                elif path == "/api/undo":
                    self._send_json(200, controller.undo())
                elif path == "/api/redo":
                    self._send_json(200, controller.redo())
                elif path == "/api/reload":
                    src = str(body.get("source", "modpack"))
                    self._send_json(200, controller.reload_catalog(src))
                elif path == "/api/settings":
                    self._send_json(200, controller.update_paths(body))
                elif path == "/api/detect-locations":
                    self._send_json(200, controller.detect_known_locations())
                elif path == "/api/browse-folder":
                    self._send_json(200, controller.browse_folder())
                elif path == "/api/browse-json":
                    self._send_json(200, controller.browse_json_file())
                elif path == "/api/save-json":
                    self._send_json(200, controller.save_json_only())
                elif path == "/api/apply-modpack":
                    self._send_json(200, controller.apply_to_modpack_and_json())
                elif path == "/api/diff":
                    self._send_json(200, controller.get_diff())
                elif path == "/api/backups/open":
                    self._send_json(200, controller.open_backups_folder())
                elif path == "/api/stage/clone":
                    self._send_json(200, controller.clone_stage_action(body))
                elif path == "/api/stage/auto-scale":
                    self._send_json(200, controller.auto_scale_action(body))
                elif path == "/api/stage/reorder":
                    self._send_json(200, controller.reorder_stages_action(body))
                elif path == "/api/group/reorder":
                    self._send_json(200, controller.reorder_groups_action(body))
                elif path == "/api/staging/import":
                    self._send_json(200, controller.staging_import_action(body))
                elif path == "/api/staging/delete":
                    self._send_json(200, controller.staging_delete_action(body))
                elif path == "/api/staging/allocate":
                    self._send_json(200, controller.staging_allocate_action(body))
                elif path == "/api/wizard/create":
                    self._send_json(200, controller.wizard_create_action(body))
                elif path == "/api/export/selective":
                    self._send_json(200, controller.selective_export_action(body))
                elif path == "/api/drain/simulate":
                    self._send_json(200, controller.simulate_drain_action(body))
                elif path == "/api/balance-all":
                    self._send_json(200, controller.auto_balance_all_action())

                else:
                    self._send_json(404, {"ok": False, "error": "Endpoint inexistente."})
            except (ValueError, KeyError, SecurityPathError, json.JSONDecodeError) as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
            except OSError as exc:
                self._send_json(500, {"ok": False, "error": f"Erro de arquivo: {exc}"})

    server = ThreadingHTTPServer(("127.0.0.1", 0), EditorRequestHandler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}"
    return server, url, csrf_token


def launch_gui(headless_check: bool = False) -> int:
    """Start local API server and open native desktop window via pywebview."""
    controller = EditorController()
    server, url, _ = create_http_server(controller)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        if headless_check:
            state = controller.get_state_payload()
            print(
                f"OK: {url} | racas={state['catalog']['total_racas']} | "
                f"formas={state['catalog']['total_transformacoes']} | "
                f"sagas={len(state['catalog'].get('opcoes_sagas', []))}"
            )
            return 0

        try:
            import webview

            win = webview.create_window(
                title="Dragon Mine Z — Editor Visual de Transformações",
                url=url,
                width=1480,
                height=920,
                min_size=(1120, 700),
                background_color="#0B0F19",
            )
            controller.attach_window(win)
            webview.start()
            return 0
        except Exception:
            webbrowser.open(url)
            server_thread.join()
            return 0
    finally:
        server.shutdown()
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Editor Visual de Transformações do Dragon Mine Z"
    )
    parser.add_argument(
        "--headless-check",
        action="store_true",
        help="Inicializa o servidor e valida o carregamento sem abrir janela.",
    )
    args = parser.parse_args(argv)
    return launch_gui(headless_check=args.headless_check)


if __name__ == "__main__":
    raise SystemExit(main())
