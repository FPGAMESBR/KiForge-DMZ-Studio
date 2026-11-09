# ⚡ KiForge: DMZ Form Studio (v1.0.0)

<div align="center">
  <img src="assets/kiforge_logo.png" alt="KiForge Logo" width="200" style="border-radius: 20px;" />
  <h3>The Definitive Transformation & Form Studio for Dragon Mine Z (Minecraft 1.20.1 Forge)</h3>
</div>

[![Minecraft 1.20.1](https://img.shields.io/badge/Minecraft-1.20.1_Forge-555555?style=flat&logo=minecraft)](https://files.minecraftforge.net/)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue?style=flat&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/Tests-19%2F19_Passing-brightgreen?style=flat)]()
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows_x64-0078D6?style=flat&logo=windows)](https://github.com/)

**KiForge: DMZ Form Studio** is the definitive standalone visual editor and balancing suite for **Dragon Mine Z (DMZ)** in Minecraft 1.20.1 Forge. It empowers modpack creators, server administrators, and players to seamlessly create, inspect, rebalance, and manage transformations, TP costs, combat multipliers, mastery progression, and DMZ addons without manual JSON editing or game restarts.

---

## 🌐 Bilingual Support / Suporte Bilíngue

KiForge includes **native bilingual support (English & Portuguese)** with an instant one-click toggle switch (`[🌐 EN | PT]`) located directly on the top navigation bar. Every label, tooltip, explanation card, combat stat description, modal, and alert adapts dynamically in real-time.

---

## 🌟 Key Features / Principais Recursos

### 1. ➕ Add & 🗑️ Delete Transformations (with Complete Undo/Redo)
- **Create New Transformations**: Interactive creation dialog allowing full customization of ID, display name, target race, skill tree, skill slot level, TP cost, combat multipliers, drains, mastery, requirements, and visual aura/hair colors.
- **Safe Removal with Undo (`Ctrl+Z`)**: Easily delete unwanted or obsolete forms. Every creation and deletion pushes an immutable snapshot to the undo/redo stack, allowing you to restore any removed transformation immediately.
- **Bi-directional Live File Sync**: When saved, KiForge automatically creates or updates the target `.json` in `config/dragonminez/races/<race>/forms/` and registers skill unlock costs in `character.json`!

### 2. 🧩 DMZ Addons & Mods Manager (Selective Disabling)
- **Automated Addon Discovery**: Deeply scans `mods/` for official and community DMZ addons (`DMZ Ultra`, `DMZ Sparking`, `DMZ Ragnarok`, `DMZ Super`, `DMZ Plus`, `DMZ Custom Forms`, `Unofficial DMZ Addon`, `DMZ Kai Path`, `DMZ Realistic`, etc.).
- **Origin Tagging**: Every transformation in the catalog is automatically tagged with a colorful origin badge displaying which addon or core mod provides it.
- **One-Click Safe Mod Toggling**: Selectively disable or re-enable individual addons directly from the UI. KiForge renames `.jar` ↔ `.jar.disabled`, 100% compliant with CurseForge, Prism Launcher, Modrinth, and Forge standards.
- **Addon Filtering**: Filter the entire transformation table by source addon with a single dropdown.

### 3. 🚀 Infinite Scalability (+50 Races, +1,000 Transformations)
- **Dynamic Race Discovery**: Automatically detects any existing or newly installed race directory in `config/dragonminez/races/`, dynamically generating friendly names without hardcoded limits.
- **High-Performance Architecture**: Zero DOM lag or memory bloat. Renders hundreds of forms at 60 FPS using clean chunking and instant in-memory filtering.
- **Multi-Keyword Search**: Filter across race names, transformation IDs, display titles, saga requirements, master instructors, or origin addons in real-time.

### 4. ⚔️ Full 9-Multiplier Combat Profile (BP)
- **Primary Focus Multipliers**:
  - **STR (Physical Strength)**: Melee combat punches and combo attack damage.
  - **SPD (Movement Speed)**: Walking, running, and flight speed.
  - **DEF (Defense / Resilience)**: Direct damage mitigation against incoming hits.
  - **PWR (Ki Power)**: Energy blasts, beams, and ki skills damage.
- **In-Depth Combat Stats**:
  - **SKP (Special Strike Power)**: Finishers and weapon special strike damage.
  - **STM (Stamina Multiplier)**: Accumulated stamina pool capacity.
  - **VIT (Vitality Multiplier)**: Maximum total health points.
  - **ENE (Energy Multiplier)**: Maximum accumulated ki energy pool.
  - **ATK SPD (Attack Speed)**: Swing frequency and recovery speed.

### 5. 🩸 Drains, Stacking & Mastery Progression
- **Per-Second Drains**: Fine-tune Ki, Stamina, and Health drain rates per second.
- **Kaioken / Buff Stacking**: Toggle `formStackable` and adjust the stack drain multiplier.
- **Mastery Curves**: Configure max mastery, instant transformation threshold, hit dealt/received gains, and passive gain intervals.

### 6. 🎨 RGB & Hex Visual Customizer
- Customize exact aura colors and hair transformation tones with live color pickers and hex inputs.

### 7. 🖥️ Ultra-Responsive Design (FHD, QHD 2K & 4K)
- Purpose-built modern Obsidian theme (`#070A11`, `#0F172A`, `#1E293B`) with high-contrast WCAG AA compliant typography.
- Fluid responsive layout scaling cleanly across:
  - **FHD (1080p - 1920x1080)**
  - **QHD / 2K (1440p - 2560x1440)**
  - **4K Ultra HD (2160p - 3840x2160)**

---

## ⌨️ Keyboard Shortcuts / Atalhos de Teclado

| Shortcut | Action | Descrição |
|---|---|---|
| `Ctrl + Z` | Undo | Desfazer última alteração (edição, adição, exclusão ou escala) |
| `Ctrl + Y` / `Ctrl + Shift + Z` | Redo | Refazer alteração desfeita |
| `Ctrl + S` | Save JSON | Salvar catálogo no arquivo JSON |
| `Escape` | Close Modal | Fechar modal ou menu aberto |
| `↑` / `↓` | Navigate | Navegar rapidamente entre linhas da tabela |

---

## 📁 Repository Structure / Estrutura do Repositório

```text
kiforge-dmz-studio/
├── assets/
│   ├── dmz_form_editor.html        # Modern 3-pane responsive desktop HTML
│   ├── dmz_form_editor.css         # High-contrast Obsidian theme & breakpoints
│   ├── dmz_form_editor.js          # Bilingual I18N engine, virtual DOM & client logic
│   └── dmz_form_editor_presets.js  # Color & tree presets
├── dmz_form_editor_core.py         # Pure functional core, immutable state & validations
├── dmz_form_editor_io.py           # Modpack config sync, backup engine & addon scanner
├── dmz_form_editor_gui.py          # HTTP server, CSRF protection & pywebview launcher
├── dmz_form_editor_sagas.py        # Saga extractor & story quest resolver
├── test_dmz_form_editor.py         # 19 automated unit tests (100% passing)
├── KiForge_DMZ_Form_Studio.spec    # PyInstaller standalone build specification
├── LICENSE                         # MIT License
└── README.md                       # Complete bilingual documentation
```

---

## 🛠️ Installation & Running / Como Instalar e Rodar

### Option A: Standalone Executable (No Python Required)
1. Download **`KiForge_DMZ_Form_Studio.exe`** from the [Releases](https://github.com/) section.
2. Double-click the `.exe` to launch the application.
3. Click **⚙️ Config Folder** to link your Minecraft modpack's `config/dragonminez` directory or an existing `Dragon_Mine_Z_Transformacoes.json` catalog.

### Option B: Running from Source
```bash
# Clone the repository
git clone https://github.com/fpgamesbr/kiforge-dmz-studio.git
cd kiforge-dmz-studio

# Install test dependencies (if running pytest)
pip install pytest pywebview

# Run the test suite
pytest test_dmz_form_editor.py -v

# Launch the visual studio
python dmz_form_editor_gui.py
```

### Option C: Compiling into Standalone `.exe`
```bash
python -m PyInstaller --noconfirm KiForge_DMZ_Form_Studio.spec
# Standalone binary output: dist/KiForge_DMZ_Form_Studio.exe
```

---

## 🛡️ Security & Reliability / Segurança e Confiabilidade

- **Zero Path Traversal**: Strict path boundary validation (`validate_allowed_path`) ensures the tool never accesses or modifies files outside user-authorized directories.
- **CSRF Token Protection**: The integrated local API server operates strictly on loopback (`127.0.0.1`) and validates per-session cryptographic HMAC tokens on every mutating request.
- **Automated Timestamped Backups**: Every write to live modpack configurations creates a full backup under `config/dragonminez/backups_editor/<YYYYMMDD_HHMMSS>/` before applying modifications.

---

## 📜 License / Licença

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for full details.

---

## 👤 Author / Autor

Developed by **Franklin Pereira Barboza (FPGAMESBR)**  
*Dragon Mine Z: Definitive Edition Team*
