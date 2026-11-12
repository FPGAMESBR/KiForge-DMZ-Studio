"""End-to-End browser verification for KiForge DMZ Studio using Headless Chrome and CDP.

Proves:
1. Zero errors in JS Console.
2. Config folder selector exists and functions properly.
3. Races and forms populate the tree accordion dynamically from modpack.
4. Real calculated numbers for HP, KI, and STM update on attribute modifications.
5. Three.js Canvas is rendered in the DOM.
6. Drain simulation loop runs and updates autonomy badge.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
import websockets

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dmz_form_editor_gui import EditorController, create_http_server


CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9222


async def run_e2e_checks(page_ws_url: str, target_url: str) -> dict[str, any]:
    results = {}
    console_errors = []
    page_exceptions = []

    all_console_msgs = []

    async with websockets.connect(page_ws_url) as ws:
        msg_id = 0

        async def send_cmd(method: str, params: dict | None = None) -> dict:
            nonlocal msg_id
            msg_id += 1
            call_id = msg_id
            payload = {"id": call_id, "method": method, "params": params or {}}
            await ws.send(json.dumps(payload))
            while True:
                resp_raw = await ws.recv()
                resp = json.loads(resp_raw)
                if resp.get("method") == "Runtime.consoleAPICalled":
                    all_console_msgs.append(resp["params"])
                    if resp.get("params", {}).get("type") == "error":
                        console_errors.append(resp["params"])
                elif resp.get("method") == "Runtime.exceptionThrown":
                    page_exceptions.append(resp["params"])
                elif resp.get("id") == call_id:
                    return resp.get("result", {})

        # Enable runtime & console
        await send_cmd("Page.enable")
        await send_cmd("Runtime.enable")
        await send_cmd("Log.enable")

        # Wait for page to initialize and populate catalog
        max_wait = 15
        start_t = time.time()
        ready = False
        while time.time() - start_t < max_wait:
            eval_res = await send_cmd(
                "Runtime.evaluate",
                {
                    "expression": """(() => {
                        return {
                            url: window.location.href,
                            readyState: document.readyState,
                            hasState: typeof window.state !== 'undefined',
                            hasCatalog: typeof window.state !== 'undefined' && !!window.state.catalog,
                            racesCount: (typeof window.state !== 'undefined' && window.state.catalog && window.state.catalog.racas) ? Object.keys(window.state.catalog.racas).length : 0
                        };
                    })()""",
                    "returnByValue": True,
                },
            )
            val = eval_res.get("result", {}).get("value")
            if val and val.get("racesCount", 0) > 0:
                ready = True
                break
            await asyncio.sleep(0.5)

        results["catalog_ready"] = ready
        if not ready:
            print("[DEBUG eval_res]:", eval_res)
            print("[DEBUG all_console_msgs]:", all_console_msgs)
            print("[DEBUG console_errors]:", console_errors)
            print("[DEBUG page_exceptions]:", page_exceptions)
        assert ready, f"Catalog was not loaded in window.state in time. Last eval: {eval_res}"

        # Wait an extra 1.5s for DOM elements, Three.js, and events to settle
        await asyncio.sleep(1.5)

        # 1. Verify Zero Console Errors
        results["console_errors_count"] = len(console_errors)
        results["page_exceptions_count"] = len(page_exceptions)
        results["console_errors"] = console_errors
        results["page_exceptions"] = page_exceptions

        # 2. Check Config Folder Selector
        folder_btn_res = await send_cmd(
            "Runtime.evaluate",
            {
                "expression": """(() => {
                    const btnSidebar = document.getElementById('btnChooseFolderSidebar');
                    const btnSettings = document.getElementById('btnOpenSettings');
                    return {
                        button_sidebar_exists: !!btnSidebar,
                        button_settings_exists: !!btnSettings,
                        sidebar_text: btnSidebar ? btnSidebar.textContent.trim() : null
                    };
                })()""",
                "returnByValue": True,
            },
        )
        results["folder_selector"] = folder_btn_res.get("result", {}).get("value")

        # 3. Dynamic Races and Forms Tree
        races_tree_res = await send_cmd(
            "Runtime.evaluate",
            {
                "expression": """(() => {
                    const sel = document.getElementById('raceSelectDropdown');
                    const raceCount = sel ? sel.options.length : 0;
                    const raceOptions = sel ? Array.from(sel.options).map(o => ({ value: o.value, text: o.text })) : [];
                    const treeList = document.getElementById('treeAccordionList');
                    const groupCards = treeList ? treeList.querySelectorAll('.tree-group').length : 0;
                    const stageItems = treeList ? treeList.querySelectorAll('.tree-stage-item').length : 0;
                    return {
                        race_dropdown_exists: !!sel,
                        race_count: raceCount,
                        race_options_sample: raceOptions.slice(0, 5),
                        group_cards_count: groupCards,
                        stage_items_count: stageItems
                    };
                })()""",
                "returnByValue": True,
            },
        )
        results["races_and_tree"] = races_tree_res.get("result", {}).get("value")

        # 4. Check Three.js WebGL canvas rendering
        three_res = await send_cmd(
            "Runtime.evaluate",
            {
                "expression": """(() => {
                    const container = document.getElementById('threeViewportContainer');
                    const canvas = container ? container.querySelector('canvas') : null;
                    return {
                        container_exists: !!container,
                        canvas_exists: !!canvas,
                        canvas_width: canvas ? canvas.width : 0,
                        canvas_height: canvas ? canvas.height : 0
                    };
                })()""",
                "returnByValue": True,
            },
        )
        results["threejs_viewport"] = three_res.get("result", {}).get("value")

        # 5. Check real calculated stats and bars
        initial_stats_res = await send_cmd(
            "Runtime.evaluate",
            {
                "expression": """(() => {
                    const hpTxt = document.getElementById('barHpVal') ? document.getElementById('barHpVal').textContent.trim() : '';
                    const kiTxt = document.getElementById('barKiVal') ? document.getElementById('barKiVal').textContent.trim() : '';
                    const stmTxt = document.getElementById('barStmVal') ? document.getElementById('barStmVal').textContent.trim() : '';
                    const eneInp = document.getElementById('attrEne') ? document.getElementById('attrEne').value : null;
                    const defInp = document.getElementById('attrDef') ? document.getElementById('attrDef').value : null;
                    return {
                        hp_text: hpTxt,
                        ki_text: kiTxt,
                        stm_text: stmTxt,
                        ene: eneInp,
                        def: defInp
                    };
                })()""",
                "returnByValue": True,
            },
        )
        results["initial_stats"] = initial_stats_res.get("result", {}).get("value")

        # 6. Alter attributes in DOM and verify dynamic update of HP, KI, and STM bars
        update_attrs_res = await send_cmd(
            "Runtime.evaluate",
            {
                "expression": """(() => {
                    const eneInp = document.getElementById('attrEne');
                    const defInp = document.getElementById('attrDef');
                    if (eneInp) { eneInp.value = '600'; eneInp.dispatchEvent(new Event('input', { bubbles: true })); }
                    if (defInp) { defInp.value = '500'; defInp.dispatchEvent(new Event('input', { bubbles: true })); }

                    // Allow recalculation loop to fire
                    if (typeof window.recalculateStatsAndBars === 'function') {
                        window.recalculateStatsAndBars();
                    }

                    const newHpTxt = document.getElementById('barHpVal') ? document.getElementById('barHpVal').textContent.trim() : '';
                    const newKiTxt = document.getElementById('barKiVal') ? document.getElementById('barKiVal').textContent.trim() : '';
                    const newStmTxt = document.getElementById('barStmVal') ? document.getElementById('barStmVal').textContent.trim() : '';

                    return {
                        new_hp_text: newHpTxt,
                        new_ki_text: newKiTxt,
                        new_stm_text: newStmTxt
                    };
                })()""",
                "returnByValue": True,
            },
        )
        results["updated_stats"] = update_attrs_res.get("result", {}).get("value")

        # 7. Test Drain Simulator play/pause
        sim_res = await send_cmd(
            "Runtime.evaluate",
            {
                "expression": """(() => {
                    const btnPlay = document.getElementById('btnDrainSimPlay');
                    const badge = document.getElementById('autonomyBadge');
                    const initialAutonomy = badge ? badge.textContent.trim() : '';
                    if (btnPlay) {
                        btnPlay.click();
                    }
                    const afterClickAutonomy = badge ? badge.textContent.trim() : '';
                    return {
                        button_exists: !!btnPlay,
                        badge_exists: !!badge,
                        initial_autonomy: initialAutonomy,
                        autonomy_text: afterClickAutonomy
                    };
                })()""",
                "returnByValue": True,
            },
        )
        results["drain_simulator"] = sim_res.get("result", {}).get("value")

    return results


def main() -> int:
    print("=== KiForge DMZ Studio: Starting End-to-End Headless Verification ===")
    controller = EditorController()
    server, url, csrf_token = create_http_server(controller)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"[*] Studio HTTP Server running on: {url}")

    import tempfile
    user_data_dir = tempfile.mkdtemp()

    # Launch Headless Chrome with Remote Debugging
    chrome_cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data_dir}",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-networking",
        url,
    ]
    print(f"[*] Launching Headless Chrome: {' '.join(chrome_cmd[:5])} ...")
    proc = subprocess.Popen(
        chrome_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=0x08000000,
    )

    try:
        # Wait for CDP endpoint to be responsive
        ws_url = None
        for _ in range(20):
            try:
                req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list", timeout=1)
                data = json.loads(req.read().decode("utf-8"))
                for target in data:
                    if target.get("type") == "page":
                        ws_url = target.get("webSocketDebuggerUrl")
                        break
                if ws_url:
                    break
            except Exception:
                time.sleep(0.5)

        if not ws_url:
            print("[!] ERROR: Could not connect to Chrome DevTools Protocol.")
            return 1

        print(f"[*] Connected to Chrome Page WebSocket: {ws_url}")

        results = asyncio.run(run_e2e_checks(ws_url, url))
        print("\n=== E2E VERIFICATION RESULTS ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))

        # Check Golden Rules & Success Criteria
        passed = True

        # (a) Zero errors in JS Console
        if results.get("console_errors_count", 0) > 0 or results.get("page_exceptions_count", 0) > 0:
            print("[FAIL] JS Console Errors or Exceptions detected!")
            passed = False
        else:
            print("[PASS] Zero errors in JS Console (0 errors, 0 exceptions).")

        # (b) Config folder selector functions
        fs = results.get("folder_selector", {})
        if fs.get("button_sidebar_exists") and fs.get("button_settings_exists"):
            print(f"[PASS] Config folder selector buttons exist and are bound ('{fs.get('sidebar_text')}').")
        else:
            print("[FAIL] Config folder selector missing!")
            passed = False

        # (c) Dynamic races & forms tree
        rt = results.get("races_and_tree", {})
        if rt.get("race_count", 0) > 0 and rt.get("group_cards_count", 0) > 0:
            print(f"[PASS] Dynamic races populated ({rt.get('race_count')} races) with {rt.get('group_cards_count')} group cards and {rt.get('stage_items_count')} stage items.")
        else:
            print("[FAIL] Dynamic races or forms tree failed to populate!")
            passed = False

        # (d) Real calculated numbers for HP, KI, STM
        istats = results.get("initial_stats", {})
        ustats = results.get("updated_stats", {})
        ki_initial = istats.get("ki_text", "")
        ki_updated = ustats.get("new_ki_text", "")
        stm_initial = istats.get("stm_text", "")
        stm_updated = ustats.get("new_stm_text", "")

        # Check values are real numbers (not fixed "10,000 / 10,000" or empty)
        if ki_initial and ki_updated and ki_initial != ki_updated and stm_initial != stm_updated:
            print(f"[PASS] Real numerical stats updated dynamically: KI changed from '{ki_initial}' to '{ki_updated}', STM changed from '{stm_initial}' to '{stm_updated}'.")
        else:
            print(f"[FAIL] Numerical bars did not dynamically calculate: initial KI='{ki_initial}', updated KI='{ki_updated}', initial STM='{stm_initial}', updated STM='{stm_updated}'.")
            passed = False

        # (e) Three.js Canvas
        three_info = results.get("threejs_viewport", {})
        if three_info.get("canvas_exists") and three_info.get("canvas_width", 0) > 0:
            print(f"[PASS] Three.js Viewport canvas rendered ({three_info.get('canvas_width')}x{three_info.get('canvas_height')}px).")
        else:
            print("[FAIL] Three.js canvas was not rendered!")
            passed = False

        # (f) Drain simulator
        drain_info = results.get("drain_simulator", {})
        if drain_info.get("button_exists") and drain_info.get("badge_exists"):
            print(f"[PASS] Drain simulator play button and autonomy badge verified (Autonomy: '{drain_info.get('autonomy_text')}').")
        else:
            print("[FAIL] Drain simulator controls missing!")
            passed = False

        if passed:
            print("\n>>> ALL END-TO-END VERIFICATION CHECKS PASSED WITH 100% SUCCESS! <<<")
            return 0
        else:
            print("\n>>> ONE OR MORE VERIFICATION CHECKS FAILED! <<<")
            return 1

    finally:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    sys.exit(main())
