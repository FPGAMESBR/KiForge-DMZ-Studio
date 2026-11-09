import copy
import json
import os
from pathlib import Path
import sys
import pytest

_EDITOR_DIR = os.path.abspath(os.path.dirname(__file__))
if _EDITOR_DIR not in sys.path:
    sys.path.insert(0, _EDITOR_DIR)

from dmz_form_editor_core import (
    SecurityPathError,
    add_form,
    apply_batch_scale,
    apply_form_update,
    delete_form,
    detect_addon_origin,
    resolve_race_friendly_name,
    validate_allowed_path,
)
from dmz_form_editor_io import (
    apply_catalog_to_modpack,
    load_catalog_from_json,
    load_catalog_from_modpack,
    save_catalog_to_json,
    scan_dmz_addons,
    toggle_addon_mod,
)


@pytest.fixture()
def mock_modpack(tmp_path: Path) -> Path:
    """Create a realistic miniature Dragon Mine Z config directory."""
    dmz_dir = tmp_path / "config" / "dragonminez"
    saiyan_dir = dmz_dir / "races" / "saiyan"
    saiyan_forms = saiyan_dir / "forms"
    stack_forms = dmz_dir / "forms"
    saiyan_forms.mkdir(parents=True)
    stack_forms.mkdir(parents=True)

    character_data = {
        "configVersion": "2.2.1",
        "hasSaiyanTail": True,
        "formSkillsCosts": {
            "supersaiyanx": {
                "buyFromMaster": False,
                "prices": [480000, 200000],
            },
            "oozaru_skill": {
                "buyFromMaster": False,
                "prices": [-1],
            },
        },
    }
    (saiyan_dir / "character.json").write_text(
        json.dumps(character_data, indent=2), encoding="utf-8"
    )

    ssjx_data = {
        "configVersion": "2.2.1",
        "groupName": "supersaiyanx",
        "formType": "supersaiyanx",
        "forms": {
            "supersaiyan1": {
                "name": "supersaiyan1",
                "unlockOnSkillLevel": 1,
                "auraColor": "#FFD700",
                "hairColor": "#FFE89E",
                "outlineShader": {"enabled": True, "primaryColor": "#FFFF00"},
                "strMultiplier": 2.5,
                "skpMultiplier": 2.5,
                "stmMultiplier": 2.5,
                "defMultiplier": 2.5,
                "vitMultiplier": 1.0,
                "pwrMultiplier": 2.5,
                "eneMultiplier": 1.0,
                "speedMultiplier": 1.0,
                "attackSpeed": 1.0,
                "staminaDrainMultiplier": 1.0,
                "energyDrain": 0.1,
                "staminaDrain": 0.0,
                "healthDrain": 0.0,
                "formStackable": True,
                "stackDrainMultiplier": 2.0,
                "maxMastery": 100.0,
                "masteryPerHitDealt": 0.025,
                "masteryPerHitReceived": 0.025,
                "passiveMasteryEveryFiveSeconds": 0.01,
                "maxCostMultiplier": 0.75,
                "maxStatsMultiplier": 1.0,
                "instantTransformOnMastery": 40.0,
                "requiredDMZLevel": 1,
                "levelRequisite": 0,
                "sagaRequisite": "",
                "formRequisite": "",
                "incompatibleWith": ["ultimate.ultimate"],
            },
            "supersaiyan2": {
                "name": "supersaiyan2",
                "unlockOnSkillLevel": 2,
                "auraColor": "#FFD700",
                "hairColor": "#FFE89E",
                "strMultiplier": 4.0,
                "skpMultiplier": 4.0,
                "stmMultiplier": 4.0,
                "defMultiplier": 4.0,
                "vitMultiplier": 1.0,
                "pwrMultiplier": 4.0,
                "eneMultiplier": 1.0,
                "speedMultiplier": 1.05,
                "attackSpeed": 1.0,
                "energyDrain": 0.18,
                "staminaDrain": 0.0,
                "healthDrain": 0.0,
                "formStackable": True,
                "stackDrainMultiplier": 2.0,
                "maxMastery": 100.0,
                "requiredDMZLevel": 10,
                "levelRequisite": 5,
                "sagaRequisite": "cell_saga",
                "formRequisite": "supersaiyan1",
                "incompatibleWith": [],
            },
            "oozaru_base": {
                "name": "oozaru_base",
                "unlockOnSkillLevel": 0,
                "strMultiplier": 1.2,
                "skpMultiplier": 1.2,
                "stmMultiplier": 1.2,
                "defMultiplier": 1.2,
                "pwrMultiplier": 1.2,
            },
        },
    }
    (saiyan_forms / "supersaiyanx.json").write_text(
        json.dumps(ssjx_data, indent=2), encoding="utf-8"
    )

    oozaru_special = {
        "configVersion": "2.2.1",
        "groupName": "oozaru_special",
        "formType": "oozaru_skill",
        "forms": {
            "ssj5_wish": {
                "name": "ssj5_wish",
                "unlockOnSkillLevel": 1,
                "strMultiplier": 12.0,
                "skpMultiplier": 12.0,
                "stmMultiplier": 12.0,
                "defMultiplier": 12.0,
                "pwrMultiplier": 12.0,
            }
        },
    }
    (saiyan_forms / "oozaru_special.json").write_text(
        json.dumps(oozaru_special, indent=2), encoding="utf-8"
    )

    kaioken_data = {
        "configVersion": "2.2.1",
        "groupName": "kaioken",
        "formType": "kaioken",
        "forms": {
            "x2": {
                "name": "x2",
                "unlockOnSkillLevel": 1,
                "strMultiplier": 1.4,
                "skpMultiplier": 1.4,
                "stmMultiplier": 1.4,
                "defMultiplier": 1.4,
                "pwrMultiplier": 1.4,
                "vitMultiplier": 1.0,
                "eneMultiplier": 1.0,
                "speedMultiplier": 1.1,
                "attackSpeed": 1.0,
                "energyDrain": 0.0,
                "staminaDrain": 0.0,
                "healthDrain": 0.05,
                "formStackable": True,
                "stackDrainMultiplier": 1.5,
                "maxMastery": 100.0,
            }
        },
    }
    (stack_forms / "kaioken.json").write_text(
        json.dumps(kaioken_data, indent=2), encoding="utf-8"
    )

    skills_data = {
        "configVersion": "2.2.1",
        "formSkills": ["supersaiyanx", "oozaru_skill"],
        "stackSkills": ["kaioken"],
        "skills": {
            "supersaiyanx": {"costs": [480000, 200000]},
            "kaioken": {"costs": [8000]},
        },
    }
    (dmz_dir / "skills.json").write_text(
        json.dumps(skills_data, indent=2), encoding="utf-8"
    )

    # Create a miniature mod JAR with saga, quest, and en_us translation
    import zipfile

    mods_dir = tmp_path / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(mods_dir / "dragonminez-2.2.1.jar", "w") as zf:
        zf.writestr(
            "assets/dragonminez/lang/en_us.json",
            json.dumps({"dmz.quest.frieza13.name": "Legendary Super Saiyan"}),
        )
        zf.writestr(
            "data/dragonminez/previousQuests/sagas/frieza_saga.json",
            json.dumps({"id": "frieza_saga", "questFolder": "saga_frieza"}),
        )
        zf.writestr(
            "data/dragonminez/previousQuests/quests/saga_frieza/13_legendary_ssj.json",
            json.dumps({"id": 13, "title": "dmz.quest.frieza13.name"}),
        )

    return dmz_dir


def test_load_catalog_from_modpack_parses_all_fields(mock_modpack: Path) -> None:
    catalog = load_catalog_from_modpack(str(mock_modpack))

    assert catalog["total_racas"] == 1
    assert catalog["total_transformacoes"] == 4
    saiyan = catalog["racas"]["saiyan"]
    ssj_forms = saiyan["arvores_de_transformacao"]["supersaiyanx"]["formas"]

    ssj1 = next(f for f in ssj_forms if f["id"] == "supersaiyan1")
    assert ssj1["custo_tp"] == 480000
    assert ssj1["custo_tp_numerico"] == 480000
    assert ssj1["multiplicador_bp"] == "2.5x"
    assert ssj1["multiplicadores_detalhados"]["forca_str"] == 2.5
    assert ssj1["maestria"]["maestria_transf_instantanea"] == 40.0
    assert ssj1["visual"]["cor_aura"] == "#FFD700"

    oozaru = next(f for f in ssj_forms if f["id"] == "oozaru_base")
    assert oozaru["custo_tp"] == 0
    assert oozaru["custo_tp_numerico"] == 0

    wish_form = saiyan["arvores_de_transformacao"]["oozaru_special"]["formas"][0]
    assert wish_form["custo_tp_numerico"] == -1
    assert "Priceless" in str(wish_form["custo_tp"])

    kaioken = catalog["formas_universais_e_stack"]["kaioken"]["formas"][0]
    assert kaioken["custo_tp"] == 8000
    assert kaioken["drenos"]["vida"] == 0.05


def test_apply_form_update_is_immutable_and_updates_stats_and_tp(
    mock_modpack: Path,
) -> None:
    catalog = load_catalog_from_modpack(str(mock_modpack))
    snapshot = copy.deepcopy(catalog)

    updated = apply_form_update(
        catalog,
        {
            "escopo": "raca",
            "raca": "saiyan",
            "arvore": "supersaiyanx",
            "id": "supersaiyan1",
            "custo_tp_numerico": 650000,
            "comprar_no_mestre": True,
            "multiplicadores_detalhados": {
                "forca_str": 3.5,
                "poder_ki_pwr": 4.0,
                "defesa_def": 3.5,
                "golpe_skp": 3.5,
                "estamina_stm": 3.5,
                "vitalidade_vit": 1.2,
                "energia_ene": 1.1,
                "velocidade_spd": 1.15,
                "velocidade_ataque": 1.1,
            },
            "drenos": {
                "energia_ki": 0.05,
                "estamina": 0.01,
                "vida": 0.0,
                "mult_estamina_golpe": 0.9,
                "acumulavel": False,
                "mult_dreno_stack": 1.5,
            },
            "maestria": {
                "maestria_maxima": 150.0,
                "ganho_golpe_dado": 0.05,
                "ganho_dano_recebido": 0.04,
                "ganho_passivo_5s": 0.02,
                "mult_custo_maestria_max": 0.5,
                "mult_status_maestria_max": 1.25,
                "maestria_transf_instantanea": 50.0,
            },
            "requisitos": {
                "nivel_dmz_minimo": 15,
                "nivel_requisito": 10,
                "saga": "frieza_saga",
                "forma_previa": "",
                "incompativel_com": ["kaioken.x100"],
            },
        },
    )

    # Original catalog MUST NOT be mutated
    assert catalog == snapshot

    ssj1 = updated["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"][
        "formas"
    ][0]
    assert ssj1["custo_tp"] == 650000
    assert ssj1["comprar_no_mestre"] is True
    assert ssj1["multiplicador_bp"] == "3.5x (STR) / 4.0x (PWR)"
    assert ssj1["drenos"]["acumulavel"] is False
    assert ssj1["maestria"]["mult_status_maestria_max"] == 1.25
    assert ssj1["requisitos"]["saga"] == "frieza_saga"


def test_apply_batch_scale_skips_free_and_priceless(mock_modpack: Path) -> None:
    catalog = load_catalog_from_modpack(str(mock_modpack))
    snapshot = copy.deepcopy(catalog)

    scaled_tp = apply_batch_scale(
        catalog,
        target_scope={"tipo": "raca", "raca": "saiyan"},
        field_group="tp",
        factor=2.0,
    )
    assert catalog == snapshot

    ssj_forms = scaled_tp["racas"]["saiyan"]["arvores_de_transformacao"][
        "supersaiyanx"
    ]["formas"]
    ssj1 = next(f for f in ssj_forms if f["id"] == "supersaiyan1")
    oozaru = next(f for f in ssj_forms if f["id"] == "oozaru_base")
    wish = scaled_tp["racas"]["saiyan"]["arvores_de_transformacao"]["oozaru_special"][
        "formas"
    ][0]

    assert ssj1["custo_tp"] == 960000
    assert oozaru["custo_tp"] == 0
    assert wish["custo_tp_numerico"] == -1

    scaled_bp = apply_batch_scale(
        scaled_tp,
        target_scope={"tipo": "arvore", "raca": "saiyan", "arvore": "supersaiyanx"},
        field_group="bp",
        factor=2.0,
    )
    ssj1_bp = scaled_bp["racas"]["saiyan"]["arvores_de_transformacao"][
        "supersaiyanx"
    ]["formas"][0]
    assert ssj1_bp["multiplicadores_detalhados"]["forca_str"] == 5.0
    assert ssj1_bp["multiplicador_bp"] == "5.0x"


def test_save_and_apply_catalog_to_modpack_preserves_shaders_and_creates_backup(
    mock_modpack: Path, tmp_path: Path
) -> None:
    catalog = load_catalog_from_modpack(str(mock_modpack))
    updated = apply_form_update(
        catalog,
        {
            "escopo": "raca",
            "raca": "saiyan",
            "arvore": "supersaiyanx",
            "id": "supersaiyan1",
            "custo_tp_numerico": 777000,
            "multiplicadores_detalhados": {
                "forca_str": 3.0,
                "poder_ki_pwr": 3.0,
                "defesa_def": 3.0,
                "golpe_skp": 3.0,
                "estamina_stm": 3.0,
            },
        },
    )
    updated = apply_form_update(
        updated,
        {
            "escopo": "universal",
            "grupo": "kaioken",
            "id": "x2",
            "custo_tp_numerico": 12000,
            "drenos": {"vida": 0.02},
        },
    )

    out_json = tmp_path / "exported_catalog.json"
    save_catalog_to_json(updated, [str(out_json)], allowed_roots=[str(tmp_path)])
    reloaded_json = load_catalog_from_json(
        str(out_json), allowed_roots=[str(tmp_path)]
    )
    assert (
        reloaded_json["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"][
            "formas"
        ][0]["custo_tp"]
        == 777000
    )

    result = apply_catalog_to_modpack(
        updated,
        str(mock_modpack),
        allowed_roots=[str(tmp_path)],
        create_backup=True,
    )
    assert result["arquivos_atualizados"] >= 4
    assert os.path.isdir(result["pasta_backup"])

    # Verify character.json updated
    char_after = json.loads(
        (mock_modpack / "races" / "saiyan" / "character.json").read_text(
            encoding="utf-8"
        )
    )
    assert char_after["formSkillsCosts"]["supersaiyanx"]["prices"][0] == 777000

    # Verify supersaiyanx.json updated AND preserved outlineShader untouched
    ssjx_after = json.loads(
        (
            mock_modpack / "races" / "saiyan" / "forms" / "supersaiyanx.json"
        ).read_text(encoding="utf-8")
    )
    assert ssjx_after["forms"]["supersaiyan1"]["strMultiplier"] == 3.0
    assert ssjx_after["forms"]["supersaiyan1"]["outlineShader"] == {
        "enabled": True,
        "primaryColor": "#FFFF00",
    }

    # Verify universal stack form & skills.json updated
    kaioken_after = json.loads(
        (mock_modpack / "forms" / "kaioken.json").read_text(encoding="utf-8")
    )
    assert kaioken_after["forms"]["x2"]["healthDrain"] == 0.02

    skills_after = json.loads((mock_modpack / "skills.json").read_text(encoding="utf-8"))
    assert skills_after["skills"]["kaioken"]["costs"][0] == 12000


def test_path_traversal_is_rejected(tmp_path: Path) -> None:
    evil_target = tmp_path.parent / "outside_secret.json"
    with pytest.raises(SecurityPathError):
        validate_allowed_path(str(evil_target), allowed_roots=[str(tmp_path)])


def test_editor_controller_undo_redo_and_persistence(
    mock_modpack: Path, tmp_path: Path
) -> None:
    from dmz_form_editor_gui import EditorController

    desktop_json = tmp_path / "Desktop" / "Dragon_Mine_Z_Transformacoes.json"
    instance_json = mock_modpack / "todas_as_transformacoes.json"

    ctrl = EditorController(
        dmz_config_dir=str(mock_modpack),
        desktop_json_path=str(desktop_json),
        instance_json_path=str(instance_json),
        allowed_roots=[str(tmp_path)],
    )
    state0 = ctrl.get_state_payload()
    assert state0["dirty"] is False
    assert state0["can_undo"] is False

    state1 = ctrl.update_form(
        {
            "escopo": "raca",
            "raca": "saiyan",
            "arvore": "supersaiyanx",
            "id": "supersaiyan1",
            "custo_tp_numerico": 555000,
        }
    )
    assert state1["dirty"] is True
    assert state1["can_undo"] is True
    ssj1 = state1["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"][
        "supersaiyanx"
    ]["formas"][0]
    assert ssj1["custo_tp"] == 555000

    # Undo restores 480000
    state_undo = ctrl.undo()
    assert state_undo["can_redo"] is True
    ssj1_undo = state_undo["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"][
        "supersaiyanx"
    ]["formas"][0]
    assert ssj1_undo["custo_tp"] == 480000

    # Redo reapplies 555000
    state_redo = ctrl.redo()
    ssj1_redo = state_redo["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"][
        "supersaiyanx"
    ]["formas"][0]
    assert ssj1_redo["custo_tp"] == 555000

    # Apply to modpack + JSON
    apply_res = ctrl.apply_to_modpack_and_json()
    assert apply_res["arquivos_atualizados"] >= 1
    assert desktop_json.is_file()
    assert instance_json.is_file()
    assert ctrl.get_state_payload()["dirty"] is False


def test_http_api_server_csrf_and_endpoints(
    mock_modpack: Path, tmp_path: Path
) -> None:
    import urllib.error
    import urllib.request
    from dmz_form_editor_gui import EditorController, create_http_server

    desktop_json = tmp_path / "Desktop" / "Dragon_Mine_Z_Transformacoes.json"
    instance_json = mock_modpack / "todas_as_transformacoes.json"
    ctrl = EditorController(
        dmz_config_dir=str(mock_modpack),
        desktop_json_path=str(desktop_json),
        instance_json_path=str(instance_json),
        allowed_roots=[str(tmp_path)],
    )

    server, url, token = create_http_server(ctrl)
    import threading

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        # GET / returns HTML with embedded token
        with urllib.request.urlopen(f"{url}/", timeout=5) as resp:
            html = resp.read().decode("utf-8")
            assert resp.status == 200
            assert "Dragon Mine Z" in html

        # GET /api/state works
        with urllib.request.urlopen(f"{url}/api/state", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
            assert data["catalog"]["total_racas"] == 1

        # POST without X-DMZ-Token must fail with 403
        req_no_csrf = urllib.request.Request(
            f"{url}/api/save-json",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(req_no_csrf, timeout=5)
        assert exc_info.value.code == 403

        # POST with valid X-DMZ-Token succeeds
        payload = json.dumps(
            {
                "escopo": "raca",
                "raca": "saiyan",
                "arvore": "supersaiyanx",
                "id": "supersaiyan1",
                "custo_tp_numerico": 900000,
            }
        ).encode("utf-8")
        req_ok = urllib.request.Request(
            f"{url}/api/update-form",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-DMZ-Token": token,
            },
            method="POST",
        )
        with urllib.request.urlopen(req_ok, timeout=5) as resp:
            updated_data = json.loads(resp.read().decode("utf-8"))
            assert updated_data["ok"] is True
            ssj1 = updated_data["catalog"]["racas"]["saiyan"][
                "arvores_de_transformacao"
            ]["supersaiyanx"]["formas"][0]
            assert ssj1["custo_tp"] == 900000

        # Static assets & 404
        for asset in ("/assets/dmz_form_editor.css", "/assets/dmz_form_editor.js"):
            with urllib.request.urlopen(f"{url}{asset}", timeout=5) as resp:
                assert resp.status == 200
                assert len(resp.read()) > 100

        with pytest.raises(urllib.error.HTTPError) as nf_err:
            urllib.request.urlopen(f"{url}/unknown-route", timeout=5)
        assert nf_err.value.code == 404

        def post_json(endpoint: str, body: dict) -> dict:
            req = urllib.request.Request(
                f"{url}{endpoint}",
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json", "X-DMZ-Token": token},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                return json.loads(r.read().decode("utf-8"))

        assert post_json(
            "/api/batch-scale",
            {"escopo_alvo": {"tipo": "tudo"}, "campo": "bp", "fator": 1.5},
        )["ok"]
        assert post_json("/api/undo", {})["ok"]
        assert post_json("/api/redo", {})["ok"]
        assert len(post_json("/api/save-json", {})["json_salvos"]) >= 1
        assert post_json("/api/reload", {"source": "json"})["source"] == "json"
        assert post_json("/api/reload", {"source": "modpack"})["source"] == "modpack"
        assert post_json("/api/apply-modpack", {})["ok"]

        # Bad factor returns 400
        with pytest.raises(urllib.error.HTTPError) as bad_err:
            post_json(
                "/api/batch-scale",
                {"escopo_alvo": {"tipo": "tudo"}, "campo": "tp", "fator": -2},
            )
        assert bad_err.value.code == 400
    finally:
        server.shutdown()
        server.server_close()


def test_json_only_fallback_and_headless_cli(
    mock_modpack: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import dmz_form_editor_gui as gui_mod

    desktop_json = tmp_path / "Desktop" / "Dragon_Mine_Z_Transformacoes.json"
    cat = load_catalog_from_modpack(str(mock_modpack))
    save_catalog_to_json(cat, [str(desktop_json)], allowed_roots=[str(tmp_path)])

    # Controller falls back to JSON when modpack folder is absent
    ctrl_json = gui_mod.EditorController(
        dmz_config_dir=str(tmp_path / "non_existent_modpack"),
        desktop_json_path=str(desktop_json),
        instance_json_path=str(tmp_path / "non_existent_modpack" / "out.json"),
        allowed_roots=[str(tmp_path)],
    )
    assert ctrl_json.get_state_payload()["source"] == "json"

    monkeypatch.setattr(gui_mod, "DEFAULT_DMZ_CONFIG_DIR", str(mock_modpack))
    monkeypatch.setattr(gui_mod, "DEFAULT_DESKTOP_JSON", str(desktop_json))
    monkeypatch.setattr(
        gui_mod, "DEFAULT_INSTANCE_JSON", str(mock_modpack / "todas.json")
    )
    monkeypatch.setattr(gui_mod, "default_allowed_roots", lambda: [str(tmp_path)])
    # Rebind default args via monkeypatching EditorController init defaults
    orig_init = gui_mod.EditorController.__init__
    monkeypatch.setattr(
        gui_mod.EditorController,
        "__init__",
        lambda self: orig_init(
            self,
            dmz_config_dir=str(mock_modpack),
            desktop_json_path=str(desktop_json),
            instance_json_path=str(mock_modpack / "todas.json"),
            allowed_roots=[str(tmp_path)],
        ),
    )
    assert gui_mod.main(["--headless-check"]) == 0


def test_io_module_imports_cleanly_first() -> None:
    import subprocess
    import sys

    creationflags = 0x08000000 if os.name == "nt" else 0
    proc = subprocess.run(
        [sys.executable, "-c", "import dmz_form_editor_io; print('OK')"],
        cwd=_EDITOR_DIR,
        capture_output=True,
        text=True,
        check=True,
        creationflags=creationflags,
    )
    assert proc.stdout.strip() == "OK"


def test_resolve_modpack_config_dir_variants(
    mock_modpack: Path, tmp_path: Path
) -> None:
    from dmz_form_editor_sagas import resolve_modpack_config_dir

    instance_root = mock_modpack.parent.parent
    config_parent = mock_modpack.parent

    expected = os.path.realpath(str(mock_modpack))
    assert resolve_modpack_config_dir(str(mock_modpack)) == expected
    assert resolve_modpack_config_dir(str(config_parent)) == expected
    assert resolve_modpack_config_dir(str(instance_root)) == expected

    empty_dir = tmp_path / "pasta_vazia_invalida"
    empty_dir.mkdir()
    with pytest.raises(ValueError, match="dragonminez"):
        resolve_modpack_config_dir(str(empty_dir))


def test_extract_sagas_and_dynamic_folder_switching(
    mock_modpack: Path, tmp_path: Path
) -> None:
    import shutil
    import urllib.request
    from dmz_form_editor_gui import EditorController, create_http_server

    # Create a second modpack copy with a distinct TP cost to verify switching
    second_root = tmp_path / "OutroModpack"
    second_dmz = second_root / "config" / "dragonminez"
    shutil.copytree(mock_modpack, second_dmz)
    char2_path = second_dmz / "races" / "saiyan" / "character.json"
    char2 = json.loads(char2_path.read_text(encoding="utf-8"))
    char2["formSkillsCosts"]["supersaiyanx"]["prices"][0] = 123456
    char2_path.write_text(json.dumps(char2, indent=2), encoding="utf-8")

    settings_file = tmp_path / "dmz_editor_settings.json"
    desktop_json = tmp_path / "Desktop" / "Dragon_Mine_Z_Transformacoes.json"

    ctrl = EditorController(
        dmz_config_dir=str(mock_modpack),
        desktop_json_path=str(desktop_json),
        instance_json_path=str(mock_modpack / "todas.json"),
        allowed_roots=[str(tmp_path)],
        settings_path=str(settings_file),
    )
    st0 = ctrl.get_state_payload()
    assert len(st0["catalog"]["opcoes_sagas"]) >= 5
    # Verify cell_saga from mock_modpack fixture is included in saga options
    saga_ids = {s["id"] for s in st0["catalog"]["opcoes_sagas"]}
    assert "frieza_saga" in saga_ids

    server, url, token = create_http_server(ctrl)
    import threading

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        # Switch folder by passing the instance root (auto-resolves config/dragonminez)
        req = urllib.request.Request(
            f"{url}/api/settings",
            data=json.dumps({"dmz_config_dir": str(second_root)}).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-DMZ-Token": token},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            switched = json.loads(resp.read().decode("utf-8"))
            assert switched["ok"] is True
            assert os.path.realpath(switched["dmz_config_dir"]) == os.path.realpath(
                str(second_dmz)
            )
            ssj1 = switched["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"][
                "supersaiyanx"
            ]["formas"][0]
            assert ssj1["custo_tp"] == 123456
            assert settings_file.is_file()
    finally:
        server.shutdown()
        server.server_close()


def test_unconfigured_setup_popup_and_blank_paths(
    mock_modpack: Path, tmp_path: Path
) -> None:
    from dmz_form_editor_gui import EditorController

    desktop_json = tmp_path / "Dragon_Mine_Z_Transformacoes.json"
    cat = load_catalog_from_modpack(str(mock_modpack))
    assert cat["caminho_modpack"] == ""
    save_catalog_to_json(cat, [str(desktop_json)], allowed_roots=[str(tmp_path)])
    raw_saved = json.loads(desktop_json.read_text(encoding="utf-8"))
    assert raw_saved["caminho_modpack"] == ""

    settings_file = tmp_path / "empty_settings.json"
    ctrl = EditorController(
        dmz_config_dir="",
        desktop_json_path="",
        instance_json_path="",
        allowed_roots=[str(tmp_path)],
        settings_path=str(settings_file),
    )
    st = ctrl.get_state_payload()
    assert st["needs_setup"] is True
    assert st["source"] == "unconfigured"
    assert st["dmz_config_dir"] == ""
    assert st["desktop_json"] == ""

    # Load JSON only without modpack folder
    st_json = ctrl.update_paths(
        {"dmz_config_dir": "", "desktop_json_path": str(desktop_json)}
    )
    assert st_json["needs_setup"] is False
    assert st_json["source"] == "json"
    assert st_json["catalog"]["total_racas"] == 1

    # Clear paths back to blank
    st_cleared = ctrl.update_paths({"clear_paths": True})
    assert st_cleared["needs_setup"] is True
    assert st_cleared["dmz_config_dir"] == ""
    assert st_cleared["desktop_json"] == ""


def test_desktop_json_prioritized_over_raw_modpack(
    mock_modpack: Path, tmp_path: Path
) -> None:
    from dmz_form_editor_gui import EditorController

    # Create a custom catalog where ssj1 has a unique TP and multiplier
    desktop_json = tmp_path / "Dragon_Mine_Z_Transformacoes.json"
    cat = load_catalog_from_modpack(str(mock_modpack))
    cat["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"][0]["custo_tp_numerico"] = 999999
    cat["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"][0]["multiplicadores_detalhados"]["forca_str"] = 88.0
    save_catalog_to_json(cat, [str(desktop_json)], allowed_roots=[str(tmp_path)])

    # Initialize controller with BOTH dmz_config_dir and desktop_json_path
    ctrl = EditorController(
        dmz_config_dir=str(mock_modpack),
        desktop_json_path=str(desktop_json),
        instance_json_path="",
        allowed_roots=[str(tmp_path)],
    )
    st = ctrl.get_state_payload()
    assert st["source"] == "json"
    form = st["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"][0]
    # Verify the custom values from the JSON were preserved, NOT overwritten by raw modpack defaults!
    assert form["custo_tp_numerico"] == 999999
    assert form["multiplicadores_detalhados"]["forca_str"] == 88.0


def test_universal_forms_master_offerings_and_visual_sync(
    mock_modpack: Path, tmp_path: Path
) -> None:
    # Add skills.json with skillOfferings
    skills_file = mock_modpack / "skills.json"
    skills_data = {
        "configVersion": "2.2.1",
        "skills": {
            "kaioken": {"costs": [8000, 30000], "allowedRaces": []}
        },
        "skillOfferings": {
            "kingkai": ["kaioken"]
        },
        "stackSkills": ["kaioken"]
    }
    with open(skills_file, "w", encoding="utf-8") as f:
        json.dump(skills_data, f)

    # Add global stack form
    forms_dir = mock_modpack / "forms"
    forms_dir.mkdir(parents=True, exist_ok=True)
    kaioken_form = {
        "formType": "kaioken",
        "forms": {
            "x2": {
                "name": "x2",
                "unlockOnSkillLevel": 1,
                "strMultiplier": 2.0,
                "pwrMultiplier": 2.0,
                "defMultiplier": 2.0,
                "skpMultiplier": 2.0,
                "stmMultiplier": 1.0,
                "vitMultiplier": 1.0,
                "eneMultiplier": 1.0,
                "speedMultiplier": 1.0,
                "attackSpeed": 1.0,
                "energyDrain": 0.0,
                "staminaDrain": 0.0,
                "healthDrain": 0.5,
                "formStackable": True,
                "auraColor": "DB182C",
                "sagaRequisite": "saiyan_saga:10"
            }
        }
    }
    with open(forms_dir / "kaioken.json", "w", encoding="utf-8") as f:
        json.dump(kaioken_form, f)

    catalog = load_catalog_from_modpack(str(mock_modpack))
    assert "kaioken" in catalog["formas_universais_e_stack"]
    k_form = catalog["formas_universais_e_stack"]["kaioken"]["formas"][0]
    # Check that master offering was resolved to True
    assert k_form["comprar_no_mestre"] is True
    # Check that saga requisite was loaded
    assert k_form["requisitos"]["saga"] == "saiyan_saga:10"
    # Check that auraColor got normalized
    assert k_form["visual"]["cor_aura"] == "DB182C"

    # Test applying visual updates
    update_payload = {
        "escopo": "universal",
        "grupo": "kaioken",
        "id": "x2",
        "visual": {"cor_aura": "#FF0000", "cor_cabelo": "#00FF00"}
    }
    updated_cat = apply_form_update(catalog, update_payload)
    up_form = updated_cat["formas_universais_e_stack"]["kaioken"]["formas"][0]
    assert up_form["visual"]["cor_aura"] == "#FF0000"
    assert up_form["visual"]["cor_cabelo"] == "#00FF00"


def test_add_and_delete_form_with_undo_redo(mock_modpack: Path, tmp_path: Path) -> None:
    from dmz_form_editor_gui import EditorController

    ctrl = EditorController(
        dmz_config_dir=str(mock_modpack),
        desktop_json_path="",
        instance_json_path="",
        allowed_roots=[str(tmp_path)],
    )
    init_st = ctrl.get_state_payload()
    total_before = init_st["catalog"]["total_transformacoes"]
    assert total_before >= 3

    # Add a new transformation to saiyan supersaiyanx
    new_form_payload = {
        "escopo": "raca",
        "raca": "saiyan",
        "arvore": "supersaiyanx",
        "id": "ssj_primal_custom",
        "nome": "Super Saiyan Primal",
        "nivel_habilidade": 3,
        "custo_tp_numerico": 980000,
        "multiplicadores_detalhados": {
            "forca_str": 7.5,
            "poder_ki_pwr": 7.5,
            "defesa_def": 7.0,
            "golpe_skp": 7.5,
        },
        "visual": {"cor_aura": "#FF4500", "cor_cabelo": "#8B0000"},
        "drenos": {"energia_ki": 0.25, "acumulavel": True},
    }
    st_added = ctrl.add_form(new_form_payload)
    assert st_added["catalog"]["total_transformacoes"] == total_before + 1
    forms_list = st_added["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"]
    assert any(f["id"] == "ssj_primal_custom" for f in forms_list)
    assert st_added["can_undo"] is True
    assert st_added["dirty"] is True

    # Test Undo of add_form
    st_undone = ctrl.undo()
    assert st_undone["catalog"]["total_transformacoes"] == total_before
    forms_list_u = st_undone["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"]
    assert not any(f["id"] == "ssj_primal_custom" for f in forms_list_u)
    assert st_undone["can_redo"] is True

    # Test Redo of add_form
    st_redone = ctrl.redo()
    assert st_redone["catalog"]["total_transformacoes"] == total_before + 1
    forms_list_r = st_redone["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"]
    assert any(f["id"] == "ssj_primal_custom" for f in forms_list_r)

    # Delete form
    del_payload = {
        "escopo": "raca",
        "raca": "saiyan",
        "arvore": "supersaiyanx",
        "id": "ssj_primal_custom",
    }
    st_deleted = ctrl.delete_form(del_payload)
    assert st_deleted["catalog"]["total_transformacoes"] == total_before
    assert not any(f["id"] == "ssj_primal_custom" for f in st_deleted["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"])

    # Test Undo of delete_form (restores the deleted form!)
    st_undo_del = ctrl.undo()
    assert st_undo_del["catalog"]["total_transformacoes"] == total_before + 1
    assert any(f["id"] == "ssj_primal_custom" for f in st_undo_del["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"])


def test_add_and_delete_live_modpack_sync(mock_modpack: Path, tmp_path: Path) -> None:
    cat = load_catalog_from_modpack(str(mock_modpack))
    add_payload = {
        "escopo": "raca",
        "raca": "saiyan",
        "arvore": "supersaiyanx",
        "id": "ssj_omega",
        "nome": "Super Saiyan Omega",
        "nivel_habilidade": 3,
        "custo_tp_numerico": 555555,
        "multiplicadores_detalhados": {"forca_str": 9.9, "poder_ki_pwr": 9.9, "defesa_def": 9.9, "golpe_skp": 9.9},
        "visual": {"cor_aura": "#00FFFF", "cor_cabelo": "#00FFFF"},
    }
    cat2 = add_form(cat, add_payload)
    res = apply_catalog_to_modpack(cat2, str(mock_modpack))
    assert res["arquivos_atualizados"] >= 1

    # Verify file on disk received the new form
    ssjx_file = mock_modpack / "races" / "saiyan" / "forms" / "supersaiyanx.json"
    ssjx_data = json.loads(ssjx_file.read_text(encoding="utf-8"))
    assert "ssj_omega" in ssjx_data["forms"]
    assert ssjx_data["forms"]["ssj_omega"]["strMultiplier"] == 9.9
    assert ssjx_data["forms"]["ssj_omega"]["auraColor"] == "#00FFFF"

    # Now delete the form from catalog and apply back
    cat3 = delete_form(cat2, {"escopo": "raca", "raca": "saiyan", "arvore": "supersaiyanx", "id": "ssj_omega"})
    res2 = apply_catalog_to_modpack(cat3, str(mock_modpack))
    assert res2["arquivos_atualizados"] >= 1

    ssjx_data2 = json.loads(ssjx_file.read_text(encoding="utf-8"))
    assert "ssj_omega" not in ssjx_data2["forms"]
    assert "supersaiyan1" in ssjx_data2["forms"]


def test_dynamic_50_plus_races_and_bilingual_names(tmp_path: Path) -> None:
    dmz_dir = tmp_path / "config" / "dragonminez"
    races_dir = dmz_dir / "races"
    races_dir.mkdir(parents=True)

    # Create 55 dynamic races
    for i in range(1, 56):
        r_name = f"custom_race_{i}"
        r_dir = races_dir / r_name / "forms"
        r_dir.mkdir(parents=True)
        form_file = r_dir / "base_tree.json"
        form_file.write_text(json.dumps({
            "configVersion": "2.2.1",
            "groupName": "base_tree",
            "formType": "base_tree",
            "forms": {
                f"form_r{i}": {
                    "name": f"form_r{i}",
                    "unlockOnSkillLevel": 1,
                    "strMultiplier": 1.5 + (i * 0.1),
                    "pwrMultiplier": 1.5 + (i * 0.1),
                    "defMultiplier": 1.5,
                    "skpMultiplier": 1.5,
                }
            }
        }), encoding="utf-8")

    cat = load_catalog_from_modpack(str(dmz_dir), allowed_roots=[str(tmp_path)])
    assert cat["total_racas"] == 55
    assert cat["total_transformacoes"] == 55

    # Check that bilingual and dynamic naming worked seamlessly
    assert resolve_race_friendly_name("saiyan", lang="pt") == "Saiyajin (Saiyan)"
    assert resolve_race_friendly_name("saiyan", lang="en") == "Saiyan"
    assert resolve_race_friendly_name("custom_race_42") == "Custom Race 42"
    assert cat["racas"]["custom_race_1"]["nome_exibicao"] == "Custom Race 1"


def test_scan_dmz_addons_and_toggle(tmp_path: Path) -> None:
    import zipfile
    inst_dir = tmp_path / "test_instance"
    mods_dir = inst_dir / "mods"
    mods_dir.mkdir(parents=True)

    # 1. Active addon jar
    jar_ultra = mods_dir / "dmzultra-0.4.1.jar"
    with zipfile.ZipFile(jar_ultra, "w") as zf:
        zf.writestr("META-INF/mods.toml", """
[[mods]]
modId="dmzultra"
version="0.4.1"
displayName="DMZ Ultra"
authors="Luigga"
description="Ultra Instinct addon"
""")
        zf.writestr("data/dragonminez/races/saiyan/forms/ultraforms.json", "{}")

    # 2. Disabled addon jar
    jar_sparking = mods_dir / "dmzsparking-1.5.0.jar.disabled"
    with zipfile.ZipFile(jar_sparking, "w") as zf:
        zf.writestr("META-INF/mods.toml", """
[[mods]]
modId="dmzsparking"
version="1.5.0"
displayName="DMZ Sparking"
authors="Yami"
description="Sparking forms"
""")

    addons = scan_dmz_addons(str(inst_dir))
    assert len(addons) == 2
    ultra = next(a for a in addons if a["mod_id"] == "dmzultra")
    sparking = next(a for a in addons if a["mod_id"] == "dmzsparking")
    assert ultra["enabled"] is True
    assert sparking["enabled"] is False
    assert ultra["display_name"] == "DMZ Ultra"
    assert sparking["display_name"] == "DMZ Sparking"

    # Test toggling ultra off (.jar -> .jar.disabled)
    res_off = toggle_addon_mod(str(inst_dir), "dmzultra-0.4.1.jar", enable=False, allowed_roots=[str(tmp_path)])
    assert res_off["ok"] is True
    assert res_off["enabled"] is False
    assert (mods_dir / "dmzultra-0.4.1.jar.disabled").is_file()
    assert not (mods_dir / "dmzultra-0.4.1.jar").is_file()

    # Test toggling sparking on (.jar.disabled -> .jar)
    res_on = toggle_addon_mod(str(inst_dir), "dmzsparking-1.5.0.jar.disabled", enable=True, allowed_roots=[str(tmp_path)])
    assert res_on["ok"] is True
    assert res_on["enabled"] is True
    assert (mods_dir / "dmzsparking-1.5.0.jar").is_file()
    assert not (mods_dir / "dmzsparking-1.5.0.jar.disabled").is_file()


def test_api_endpoints_add_delete_addons_and_language(mock_modpack: Path, tmp_path: Path) -> None:
    import urllib.request
    from dmz_form_editor_gui import EditorController, create_http_server

    ctrl = EditorController(
        dmz_config_dir=str(mock_modpack),
        desktop_json_path="",
        instance_json_path="",
        allowed_roots=[str(tmp_path)],
    )
    server, url, token = create_http_server(ctrl)
    import threading

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        # Test /api/addons GET
        req_a = urllib.request.Request(f"{url}/api/addons")
        with urllib.request.urlopen(req_a, timeout=5) as resp:
            data_a = json.loads(resp.read().decode("utf-8"))
            assert data_a["ok"] is True
            assert isinstance(data_a["addons"], list)

        # Test /api/language POST
        req_l = urllib.request.Request(
            f"{url}/api/language",
            data=json.dumps({"language": "en"}).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-DMZ-Token": token},
            method="POST",
        )
        with urllib.request.urlopen(req_l, timeout=5) as resp:
            data_l = json.loads(resp.read().decode("utf-8"))
            assert data_l["ok"] is True
            assert data_l["language"] == "en"

        # Test /api/form/add POST
        add_p = {
            "escopo": "raca",
            "raca": "saiyan",
            "arvore": "supersaiyanx",
            "id": "ssj_api_test",
            "nome": "Super Saiyan API",
            "nivel_habilidade": 4,
            "custo_tp_numerico": 1000000,
        }
        req_add = urllib.request.Request(
            f"{url}/api/form/add",
            data=json.dumps(add_p).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-DMZ-Token": token},
            method="POST",
        )
        with urllib.request.urlopen(req_add, timeout=5) as resp:
            data_add = json.loads(resp.read().decode("utf-8"))
            assert data_add["ok"] is True
            forms = data_add["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"]
            assert any(f["id"] == "ssj_api_test" for f in forms)

        # Test /api/form/delete POST
        del_p = {
            "escopo": "raca",
            "raca": "saiyan",
            "arvore": "supersaiyanx",
            "id": "ssj_api_test",
        }
        req_del = urllib.request.Request(
            f"{url}/api/form/delete",
            data=json.dumps(del_p).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-DMZ-Token": token},
            method="POST",
        )
        with urllib.request.urlopen(req_del, timeout=5) as resp:
            data_del = json.loads(resp.read().decode("utf-8"))
            assert data_del["ok"] is True
            forms = data_del["catalog"]["racas"]["saiyan"]["arvores_de_transformacao"]["supersaiyanx"]["formas"]
            assert not any(f["id"] == "ssj_api_test" for f in forms)
    finally:
        server.shutdown()
        server.server_close()



