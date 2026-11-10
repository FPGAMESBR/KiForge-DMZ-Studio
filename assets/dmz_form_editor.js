(() => {
  "use strict";

  const csrfToken = document.body.dataset.csrfToken || "";

  const I18N = {
    pt: {
      app_title: "KiForge: DMZ Form Studio",
      app_subtitle: "Editor e Balanceador de Transformações de Dragon Mine Z",
      modpack_connected: "Modpack Conectado",
      json_mode: "Arquivo JSON",
      select_path: "Selecione Arquivo / Pasta",
      unsaved_changes: "Alterações não salvas",
      btn_config_folder: "⚙️ Pasta Config",
      btn_undo: "↶ Desfazer",
      btn_redo: "↷ Refazer",
      btn_batch: "⚡ Escala em Lote",
      btn_reload: "↻ Ler Modpack",
      btn_save_json: "💾 Salvar JSON",
      btn_apply: "🚀 Salvar + Aplicar no Modpack",
      btn_add_form: "+ Nova Forma",
      btn_addons: "🧩 Addons & Mods",
      btn_delete_form: "🗑️ Excluir",
      confirm_form: "✓ Confirmar Forma",
      filter_sidebar: "Filtrar raça na lateral...",
      all_races_label: "Todas as Raças",
      universal_forms_label: "Formas Universais & Stack",
      search_placeholder: "Buscar por nome, ID, árvore, tipo, saga ou addon...",
      filter_all: "Filtro: Todas as Formas",
      filter_tp_paid: "Com Custo TP (> 0)",
      filter_priceless: "Priceless / Desejo (-1)",
      filter_free: "Gratuitas / Inatas (0)",
      filter_saga: "Com Saga Obrigatória",
      filter_master: "Compra em Mestre",
      sort_default: "Ordem: Padrão da Árvore",
      sort_tp_desc: "Maior Custo TP",
      sort_tp_asc: "Menor Custo TP",
      sort_bp_desc: "Maior Multiplicador BP",
      sort_bp_asc: "Menor Multiplicador BP",
      sort_name_asc: "Nome (A → Z)",
      th_transformation: "Transformação",
      th_race_tree: "Raça / Árvore",
      th_tp_cost: "Custo TP",
      th_multipliers: "Mult. Status (BP)",
      th_drains: "Drenos (/s)",
      th_reqs: "Requisitos & Flags",
      inspector_empty_title: "Selecione uma Transformação",
      inspector_empty_desc: "Clique em qualquer linha da tabela ao centro para inspecionar e editar Custo de TP, Multiplicadores de BP, Drenos, Maestria e Requisitos.",
      card_tp_title: "1. Custo de TP & Desbloqueio",
      lbl_tp_cost: "Custo de TP (-1 = Priceless, 0 = Inato)",
      lbl_skill_slot: "Nível na Habilidade (Slot)",
      btn_free: "Gratuito (0)",
      btn_priceless: "Priceless (-1)",
      chk_buy_master: "Exigir Compra em Mestre (buyFromMaster)",
      master_box_title: "🥋 Mestre que Ensina / Vende",
      master_hint: "Disponível para aprender interagindo com o mestre no jogo.",
      card_bp_title: "2. Multiplicadores de Status (BP)",
      lbl_str: "Força Física (STR)",
      desc_str: "Dano de socos e combos corpo a corpo",
      lbl_pwr: "Poder de Ki (PWR)",
      desc_pwr: "Dano de rajadas, beams e skills de ki",
      lbl_def: "Resistência / Defesa (DEF)",
      desc_def: "Mitigação direta de danos sofridos",
      lbl_skp: "Poder de Golpe Especial (SKP)",
      desc_skp: "Dano de técnicas de finalização",
      lbl_spd: "Velocidade de Movimento (SPD)",
      desc_spd: "Rapidez ao andar, correr e voar",
      lbl_atk_spd: "Velocidade de Ataque",
      desc_atk_spd: "Frequência e recuperação de golpes",
      lbl_stm: "Multiplicador de Estamina (STM)",
      desc_stm: "Teto de estamina acumulada",
      lbl_vit: "Multiplicador de Vitalidade (VIT)",
      desc_vit: "Vida total máxima do guerreiro",
      lbl_ene: "Multiplicador de Energia (ENE)",
      desc_ene: "Teto de ki máximo acumulado",
      card_drains_title: "3. Drenos (/s) & Empilhamento (Stack)",
      lbl_drain_ki: "Dreno de Ki (/s)",
      lbl_drain_stm: "Dreno de Estamina (/s)",
      lbl_drain_hp: "Dreno de Vida (/s)",
      lbl_drain_hit: "Mult. Dreno Estamina por Golpe",
      chk_stackable: "Permitir Empilhar com Kaioken/Buffs (formStackable)",
      lbl_stack_mult: "Multiplicador de Dreno ao Empilhar",
      card_mastery_title: "4. Maestria da Forma",
      lbl_max_mastery: "Maestria Máxima",
      lbl_instant_transf: "Nível de Maestria para Transf. Instantânea",
      lbl_mastery_hit_dealt: "Ganho por Golpe Dado",
      lbl_mastery_hit_rcv: "Ganho por Dano Recebido",
      lbl_mastery_passive: "Ganho Passivo a cada 5s",
      lbl_max_cost_mult: "Mult. Custo Ki com Maestria Máx",
      lbl_max_stats_mult: "Mult. Status com Maestria Máx",
      card_reqs_title: "5. Requisitos & Vínculo Narrativo",
      lbl_min_dmz: "Nível Mínimo do Personagem (requiredDMZLevel)",
      lbl_min_skill_req: "Nível Requisito na Árvore (levelRequisite)",
      lbl_saga_req: "Saga Obrigatória para Desbloqueio",
      lbl_prev_form: "Forma Prévia Obrigatória (Requisito)",
      lbl_incompatible: "Formas Incompatíveis (Bloqueio Mútuo)",
      lbl_quick_shortcuts: "Atalhos Comuns:",
      card_visual_title: "6. Efeitos Visuais & Shader",
      lbl_aura_hex: "Cor da Aura (Hex)",
      lbl_hair_hex: "Cor do Cabelo (Hex)",
      addon_all: "Todos os Addons",
      addon_core: "Dragon Mine Z (Core)",
      modal_add_title: "➕ Adicionar Nova Transformação",
      modal_add_desc: "Preencha os atributos para criar uma transformação balanceada diretamente no catálogo e nos arquivos do jogo.",
      modal_del_title: "🗑️ Confirmar Remoção de Transformação",
      modal_del_note: "Você pode desfazer essa remoção a qualquer momento pressionando Ctrl+Z.",
      modal_addons_title: "🧩 Gerenciador de Addons & Mods do DMZ",
      modal_addons_desc: "Ative ou desative mods e pacotes de formas do modpack de forma 100% segura e compatível com CurseForge.",
      addon_th_status: "Status",
      addon_th_name: "Nome do Mod",
      addon_th_version: "Versão",
      addon_th_author: "Autor",
      addon_th_file: "Arquivo .jar",
      addon_th_size: "Tamanho",
      addon_enabled: "Ativo",
      addon_disabled: "Desativado",
      btn_close: "Fechar",
      btn_cancel: "Cancelar",
      btn_confirm_add: "Criar Transformação",
      btn_confirm_del: "Confirmar Remoção",
      shortcuts_hint: "Dica: use ↑ / ↓ para navegar · Ctrl+Z desfaz · Ctrl+S salva",
      lbl_training_master: "Mestre que Ensina / Vende",
      lbl_master_desc: "Disponível para aprender interagindo com o mestre no jogo.",
      aura_live_title: "Visualização em Tempo Real",
      lbl_aura_presets: "Paleta Rápida Dragon Ball:",
      btn_open_mods: "📁 Abrir Pasta Mods",
      btn_reload_mods: "🔄 Recarregar",
      addons_loading_title: "Escaneando pasta de mods do Modpack...",
      addons_loading_sub: "Lendo arquivos .jar, metadados e compatibilidade de transformações",
      tab_all: "Todos",
      tab_active: "Ativos",
      tab_disabled: "Desativados",
      addons_safe_hint: "Desativar renomeia para .jar.disabled de forma 100% segura sem apagar nada.",
      opt_no_saga: "— Nenhuma saga exigida —",
      opt_no_master: "— Nenhum mestre vinculado —",
      opt_custom_master: "Personalizado / Outro...",
      add_sec1_title: "📁 1. Identificação & Localização na Árvore",
      lbl_add_scope: "Escopo",
      opt_add_scope_race: "Específica de Raça",
      opt_add_scope_universal: "Universal / Stack",
      lbl_add_race: "Raça",
      lbl_add_tree: "Árvore / Grupo",
      lbl_add_id: "ID Técnico da Forma",
      badge_user_created: "Você Cria",
      hint_add_id: "⚙️ Identificador único salvo no modpack (slug minúsculo).",
      lbl_add_nome: "Nome de Exibição",
      hint_add_nome: "🎮 Nome que os jogadores verão na HUD e habilidades.",
      lbl_add_addon: "Addon / Pacote de Origem",
      hint_add_addon: "Origem da forma para filtros.",
      add_sec2_title: "💰 2. Economia de TP & Requisitos de Desbloqueio",
      lbl_add_tp: "Custo de TP",
      lbl_add_lvl: "Nível Slot Habilidade (Slot Level)",
      lbl_add_master: "Mestre que Ensina (Opcional)",
      lbl_add_saga: "Saga Obrigatória para Desbloqueio",
      lbl_add_prev: "Forma Prévia Obrigatória (Requisito)",
      add_sec3_title: "⚔️ 3. Multiplicadores de Status (Battle Power)",
      lbl_add_mult_all: "Multiplicar Todos:",
      add_sec4_title: "✨ 4. Efeitos Visuais & Aura da Transformação",
      add_aura_preview_title: "Visualização em Tempo Real da Forma",
      add_aura_paleta_title: "Paleta Rápida Dragon Ball:",
      lbl_add_aura_hex: "Cor da Aura (Hex)",
      lbl_add_hair_hex: "Cor do Cabelo (Hex)",
      btn_add_confirm_submit: "✨ Criar Transformação",
    },
    en: {
      app_title: "KiForge: DMZ Form Studio",
      app_subtitle: "Official Dragon Mine Z Transformation & Form Balancer",
      modpack_connected: "Modpack Connected",
      json_mode: "JSON File",
      select_path: "Select File / Folder",
      unsaved_changes: "Unsaved Changes",
      btn_config_folder: "⚙️ Config Folder",
      btn_undo: "↶ Undo",
      btn_redo: "↷ Redo",
      btn_batch: "⚡ Batch Scale",
      btn_reload: "↻ Read Modpack",
      btn_save_json: "💾 Save JSON",
      btn_apply: "🚀 Save + Apply to Modpack",
      btn_add_form: "+ New Form",
      btn_addons: "🧩 Addons & Mods",
      btn_delete_form: "🗑️ Delete",
      confirm_form: "✓ Confirm Form",
      filter_sidebar: "Filter race in sidebar...",
      all_races_label: "All Races",
      universal_forms_label: "Universal & Stack Forms",
      search_placeholder: "Search by name, ID, tree, type, saga, or addon...",
      filter_all: "Filter: All Forms",
      filter_tp_paid: "With TP Cost (> 0)",
      filter_priceless: "Priceless / Wish (-1)",
      filter_free: "Free / Innate (0)",
      filter_saga: "With Required Saga",
      filter_master: "Master Purchase",
      sort_default: "Order: Tree Default",
      sort_tp_desc: "Highest TP Cost",
      sort_tp_asc: "Lowest TP Cost",
      sort_bp_desc: "Highest BP Multiplier",
      sort_bp_asc: "Lowest BP Multiplier",
      sort_name_asc: "Name (A → Z)",
      th_transformation: "Transformation",
      th_race_tree: "Race / Tree",
      th_tp_cost: "TP Cost",
      th_multipliers: "Combat Mults (BP)",
      th_drains: "Drains (/s)",
      th_reqs: "Requirements & Flags",
      inspector_empty_title: "Select a Transformation",
      inspector_empty_desc: "Click any row in the center table to inspect and edit TP Costs, BP Multipliers, Drains, Mastery, and Requirements.",
      card_tp_title: "1. TP Cost & Unlock",
      lbl_tp_cost: "TP Cost (-1 = Priceless, 0 = Free)",
      lbl_skill_slot: "Skill Slot Level",
      btn_free: "Free (0)",
      btn_priceless: "Priceless (-1)",
      chk_buy_master: "Require Master Purchase (buyFromMaster)",
      master_box_title: "🥋 Training Master",
      master_hint: "Available to learn by interacting with the master in-game.",
      card_bp_title: "2. Combat Multipliers (BP)",
      lbl_str: "Physical Strength (STR)",
      desc_str: "Melee punches and combo attack damage",
      lbl_pwr: "Ki Power (PWR)",
      desc_pwr: "Damage of blasts, beams, and ki skills",
      lbl_def: "Defense / Resilience (DEF)",
      desc_def: "Direct damage mitigation",
      lbl_skp: "Special Strike Power (SKP)",
      desc_skp: "Damage multiplier for special strike moves",
      lbl_spd: "Movement Speed (SPD)",
      desc_spd: "Walking, running, and flight speed",
      lbl_atk_spd: "Attack Speed",
      desc_atk_spd: "Swing frequency and recovery time",
      lbl_stm: "Stamina Multiplier (STM)",
      desc_stm: "Maximum accumulated stamina pool",
      lbl_vit: "Vitality Multiplier (VIT)",
      desc_vit: "Total maximum warrior health points",
      lbl_ene: "Energy Multiplier (ENE)",
      desc_ene: "Maximum accumulated ki energy pool",
      card_drains_title: "3. Drains (/s) & Stacking",
      lbl_drain_ki: "Ki Drain (/s)",
      lbl_drain_stm: "Stamina Drain (/s)",
      lbl_drain_hp: "Health Drain (/s)",
      lbl_drain_hit: "Stamina Drain Mult per Hit",
      chk_stackable: "Allow Stacking with Kaioken/Buffs (formStackable)",
      lbl_stack_mult: "Stacking Drain Multiplier",
      card_mastery_title: "4. Form Mastery",
      lbl_max_mastery: "Maximum Mastery",
      lbl_instant_transf: "Mastery Level for Instant Transformation",
      lbl_mastery_hit_dealt: "Gain per Hit Dealt",
      lbl_mastery_hit_rcv: "Gain per Damage Received",
      lbl_mastery_passive: "Passive Gain Every 5s",
      lbl_max_cost_mult: "Ki Cost Mult at Max Mastery",
      lbl_max_stats_mult: "Stats Mult at Max Mastery",
      card_reqs_title: "5. Requirements & Story Progression",
      lbl_min_dmz: "Min Character Level (requiredDMZLevel)",
      lbl_min_skill_req: "Tree Requisite Level (levelRequisite)",
      lbl_saga_req: "Required Saga to Unlock",
      lbl_prev_form: "Required Prior Form (Requisite)",
      lbl_incompatible: "Incompatible Forms (Mutual Block)",
      lbl_quick_shortcuts: "Common Shortcuts:",
      card_visual_title: "6. Visual Effects & Shaders",
      lbl_aura_hex: "Aura Color (Hex)",
      lbl_hair_hex: "Hair Color (Hex)",
      addon_all: "All Addons",
      addon_core: "Dragon Mine Z (Core)",
      modal_add_title: "➕ Add New Transformation",
      modal_add_desc: "Fill in the attributes to create a custom-balanced transformation directly in the catalog and game configs.",
      modal_del_title: "🗑️ Confirm Transformation Removal",
      modal_del_note: "You can undo this deletion at any time by pressing Ctrl+Z.",
      modal_addons_title: "🧩 DMZ Addons & Mods Manager",
      modal_addons_desc: "Safely enable or disable mods and form packs with full CurseForge compatibility.",
      addon_th_status: "Status",
      addon_th_name: "Mod Name",
      addon_th_version: "Version",
      addon_th_author: "Author",
      addon_th_file: ".jar File",
      addon_th_size: "Size",
      addon_enabled: "Enabled",
      addon_disabled: "Disabled",
      btn_close: "Close",
      btn_cancel: "Cancel",
      btn_confirm_add: "Create Transformation",
      btn_confirm_del: "Confirm Deletion",
      shortcuts_hint: "Tip: use ↑ / ↓ to navigate · Ctrl+Z undos · Ctrl+S saves",
      lbl_training_master: "Training Master / Vendor",
      lbl_master_desc: "Available to learn by interacting with this master in-game.",
      aura_live_title: "Real-Time Visualizer",
      lbl_aura_presets: "Dragon Ball Quick Palette:",
      btn_open_mods: "📁 Open Mods Folder",
      btn_reload_mods: "🔄 Reload",
      addons_loading_title: "Scanning Modpack mods directory...",
      addons_loading_sub: "Inspecting .jar files, toml metadata and form integrations",
      tab_all: "All",
      tab_active: "Enabled",
      tab_disabled: "Disabled",
      addons_safe_hint: "Disabling safely renames to .jar.disabled without deleting anything.",
      opt_no_saga: "— No saga required —",
      opt_no_master: "— No master bound —",
      opt_custom_master: "Custom / Other...",
      add_sec1_title: "📁 1. Identification & Tree Placement",
      lbl_add_scope: "Scope",
      opt_add_scope_race: "Race-Specific",
      opt_add_scope_universal: "Universal / Stack",
      lbl_add_race: "Race",
      lbl_add_tree: "Tree / Group",
      lbl_add_id: "Technical Form ID",
      badge_user_created: "You Create",
      hint_add_id: "⚙️ Unique technical slug saved in modpack (lowercase).",
      lbl_add_nome: "Display Name",
      hint_add_nome: "🎮 Visible in-game name shown in HUD & skill tree.",
      lbl_add_addon: "Origin Addon / Pack",
      hint_add_addon: "Origin package used for catalog filtering.",
      add_sec2_title: "💰 2. TP Economy & Unlock Requirements",
      lbl_add_tp: "TP Cost",
      lbl_add_lvl: "Skill Slot Level (Slot Level)",
      lbl_add_master: "Teaching Master (Optional)",
      lbl_add_saga: "Required Saga to Unlock",
      lbl_add_prev: "Required Prior Form (Requisite)",
      add_sec3_title: "⚔️ 3. Combat Multipliers (Battle Power)",
      lbl_add_mult_all: "Multiply All:",
      add_sec4_title: "✨ 4. Visual Effects & Transformation Aura",
      add_aura_preview_title: "Real-Time Form Visualizer",
      add_aura_paleta_title: "Quick Dragon Ball Palette:",
      lbl_add_aura_hex: "Aura Color (Hex)",
      lbl_add_hair_hex: "Hair Color (Hex)",
      btn_add_confirm_submit: "✨ Create Transformation",
    }
  };

  const state = {
    catalog: null,
    source: "modpack",
    language: localStorage.getItem("kiforge_lang") || "pt",
    dirty: false,
    canUndo: false,
    canRedo: false,
    modpackAvailable: true,
    navScope: "all_races",
    selectedTree: "all",
    addonFilter: "all",
    raceFilterText: "",
    searchText: "",
    quickFilter: "all",
    sortBy: "default",
    flatRows: [],
    selectedKey: null,
    inspectorDirty: false,
    addonsList: [],
  };

  const el = (id) => document.getElementById(id);

  function t(key) {
    const lang = state.language === "en" ? "en" : "pt";
    return I18N[lang][key] || I18N["pt"][key] || key;
  }

  function setLanguage(newLang) {
    state.language = newLang === "en" ? "en" : "pt";
    localStorage.setItem("kiforge_lang", state.language);
    
    // Notify server asynchronously
    apiPost("/api/language", { language: state.language }).catch(() => {});

    // Update Language Toggle Button text
    const btn = el("btnLangToggle");
    if (btn) {
      btn.textContent = state.language === "en" ? "🌐 EN" : "🌐 PT";
      btn.title = state.language === "en" ? "Language: English (Click for PT)" : "Idioma: Português (Clique para EN)";
    }

    // Update static data-i18n elements
    document.querySelectorAll("[data-i18n]").forEach((elem) => {
      const k = elem.getAttribute("data-i18n");
      if (k) elem.textContent = t(k);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((elem) => {
      const k = elem.getAttribute("data-i18n-placeholder");
      if (k) elem.placeholder = t(k);
    });

    const sh = el("shortcutsHint");
    if (sh) sh.textContent = t("shortcuts_hint");

    renderHeader();
    renderSidebar();
    renderTreeChips();
    rebuildAndRenderTable();
    refreshInspectorFromSelection();
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function resolveAuraDotColor(f) {
    if (!f) return "#64748B";
    const raw = f.visual && f.visual.cor_aura;
    if (raw) {
      let str = String(raw).trim();
      if (!str.startsWith("#") && /^[0-9a-fA-F]{3,8}$/.test(str)) {
        str = "#" + str;
      }
      if (/^#[0-9a-fA-F]{3,8}$/.test(str)) {
        const lower = str.toLowerCase();
        if (lower !== "#000000" && lower !== "#14141a") {
          return str;
        }
      }
    }
    const token = `${f.id || ""} ${f.nome || ""} ${f.arvore || ""} ${f.grupo || ""}`.toLowerCase();
    if (token.includes("kaioken")) return "#EF4444";
    if (token.includes("rose")) return "#F43F5E";
    if (token.includes("blue")) return "#0EA5E9";
    if (token.includes("ego") || token.includes("hakaishin")) return "#A855F7";
    if (token.includes("instinct") || token.includes("silver") || token.includes("true")) return "#E2E8F0";
    if (token.includes("god") || token.includes("divine")) return "#FB923C";
    if (token.includes("golden") || token.includes("gold") || token.includes("super")) return "#EAB308";
    if (token.includes("orange")) return "#F97316";
    if (token.includes("black")) return "#4338CA";
    if (token.includes("ultimate") || token.includes("mystic")) return "#F8FAFC";
    if (token.includes("visored") || token.includes("hollow")) return "#DC2626";
    if (token.includes("demon") || token.includes("evil") || token.includes("malice")) return "#8B5CF6";
    if (token.includes("beast")) return "#C084FC";
    if (token.includes("ikari")) return "#22C55E";
    return "#64748B";
  }

  function resolveHairColor(f) {
    if (!f || !f.visual || !f.visual.cor_cabelo) return "";
    let str = String(f.visual.cor_cabelo).trim();
    if (!str.startsWith("#") && /^[0-9a-fA-F]{3,8}$/.test(str)) {
      str = "#" + str;
    }
    if (/^#[0-9a-fA-F]{3,8}$/.test(str)) {
      return str;
    }
    return "";
  }

  const formatNumberPt = (num) => Number(num).toLocaleString(state.language === "en" ? "en-US" : "pt-BR");

  function showToast(msg, isError = false) {
    const item = document.createElement("div");
    item.className = isError ? "toast error" : "toast";
    item.textContent = msg;
    el("toastContainer").appendChild(item);
    setTimeout(() => item.remove(), 4200);
  }

  async function apiGet(path) {
    const res = await fetch(path, { headers: { Accept: "application/json" } });
    const data = await res.json();
    if (!res.ok || !data.ok) throw new Error(data.error || `Erro HTTP ${res.status}`);
    return data;
  }

  async function apiPost(path, bodyObj = {}) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-DMZ-Token": csrfToken },
      body: JSON.stringify(bodyObj),
    });
    const data = await res.json();
    if (!res.ok || !data.ok) throw new Error(data.error || `Erro HTTP ${res.status}`);
    return data;
  }

  function applyServerState(data) {
    state.catalog = data.catalog;
    if (data.source) state.source = data.source;
    if (data.language && !localStorage.getItem("kiforge_lang")) {
      state.language = data.language;
    }
    state.needsSetup = Boolean(data.needs_setup);
    state.dirty = Boolean(data.dirty);
    state.canUndo = Boolean(data.can_undo);
    state.canRedo = Boolean(data.can_redo);
    if (typeof data.modpack_available === "boolean") state.modpackAvailable = data.modpack_available;
    if ("dmz_config_dir" in data) state.dmzConfigDir = data.dmz_config_dir || "";
    if ("desktop_json" in data) state.desktopJson = data.desktop_json || "";
    if ("default_dmz_config_dir" in data) state.defaultDmzConfigDir = data.default_dmz_config_dir || "";
    state.inspectorDirty = false;

    populateAddonFilterOptions();
    renderHeader();
    renderSidebar();
    renderTreeChips();
    rebuildAndRenderTable();
    refreshInspectorFromSelection();
  }

  function populateAddonFilterOptions() {
    const select = el("addonFilterSelect");
    if (!select || !state.catalog) return;
    const curVal = select.value;
    const addons = new Set();
    
    // Scan all forms in catalog to gather addons
    Object.values(state.catalog.racas || {}).forEach((r) => {
      Object.values(r.arvores_de_transformacao || {}).forEach((t) => {
        (t.formas || []).forEach((f) => {
          if (f.addon_origem) addons.add(f.addon_origem);
        });
      });
    });
    Object.values(state.catalog.formas_universais_e_stack || {}).forEach((g) => {
      (g.formas || []).forEach((f) => {
        if (f.addon_origem) addons.add(f.addon_origem);
      });
    });

    select.innerHTML = `<option value="all">${t("addon_all")}</option>`;
    Array.from(addons).sort().forEach((addName) => {
      const opt = document.createElement("option");
      opt.value = addName;
      opt.textContent = addName;
      select.appendChild(opt);
    });
    if (Array.from(addons).includes(curVal)) {
      select.value = curVal;
    }
  }

  function renderHeader() {
    const cat = state.catalog;
    if (!cat) return;

    const pill = el("statusSourcePill");
    if (state.source === "modpack") {
      pill.className = "status-pill modpack";
      pill.textContent = t("modpack_connected");
    } else if (state.source === "json") {
      pill.className = "status-pill json";
      pill.textContent = t("json_mode");
    } else {
      pill.className = "status-pill dirty";
      pill.textContent = t("select_path");
    }

    let univCount = 0;
    Object.values(cat.formas_universais_e_stack || {}).forEach((g) => {
      univCount += (g.formas || []).length;
    });

    const isEn = state.language === "en";
    el("statusCounts").textContent = isEn
      ? `${cat.total_racas || 0} races · ${cat.total_transformacoes || 0} race forms · ${univCount} universal`
      : `${cat.total_racas || 0} raças · ${cat.total_transformacoes || 0} formas de raça · ${univCount} universais`;

    const pInfo = el("statusPathInfo");
    if (pInfo) {
      if (state.dmzConfigDir) {
        const parts = state.dmzConfigDir.replace(/\\/g, "/").split("/");
        pInfo.textContent = parts.slice(-3).join("/");
        pInfo.title = state.dmzConfigDir;
      } else if (state.desktopJson) {
        pInfo.textContent = state.desktopJson.replace(/\\/g, "/").split("/").pop();
        pInfo.title = state.desktopJson;
      } else {
        pInfo.textContent = "";
      }
    }

    const dirtyPill = el("statusDirtyPill");
    dirtyPill.style.display = state.dirty ? "inline-block" : "none";
    dirtyPill.textContent = t("unsaved_changes");

    el("btnUndo").disabled = !state.canUndo;
    el("btnRedo").disabled = !state.canRedo;
    el("btnApplyModpack").disabled = !state.modpackAvailable;

    el("btnUndo").title = state.canUndo
      ? (isEn ? "Undo last change (Ctrl+Z)" : "Desfazer última alteração (Ctrl+Z)")
      : (isEn ? "Undo (Ctrl+Z) - Available after making changes" : "Desfazer (Ctrl+Z) - Disponível após modificar uma forma");
    el("btnRedo").title = state.canRedo
      ? (isEn ? "Redo last change (Ctrl+Y)" : "Refazer alteração (Ctrl+Y)")
      : (isEn ? "Redo (Ctrl+Y)" : "Refazer (Ctrl+Y)");

    const langBtn = el("btnLangToggle");
    if (langBtn) {
      langBtn.textContent = state.language === "en" ? "🌐 EN" : "🌐 PT";
    }
  }

  function renderSidebar() {
    const nav = el("navList");
    nav.innerHTML = "";
    const cat = state.catalog;
    if (!cat) return;

    const addNavItem = (scopeKey, label, count) => {
      const item = document.createElement("div");
      item.className = "nav-item" + (state.navScope === scopeKey ? " active" : "");
      item.innerHTML = `<span>${escapeHtml(label)}</span><span class="count">${count}</span>`;
      item.addEventListener("click", () => {
        state.navScope = scopeKey;
        state.selectedTree = "all";
        renderSidebar();
        renderTreeChips();
        rebuildAndRenderTable();
      });
      nav.appendChild(item);
    };

    let univCount = 0;
    Object.values(cat.formas_universais_e_stack || {}).forEach((g) => {
      univCount += (g.formas || []).length;
    });

    addNavItem("all_races", t("all_races_label"), cat.total_transformacoes || 0);
    addNavItem("universal", t("universal_forms_label"), univCount);

    const secRacas = document.createElement("div");
    secRacas.className = "nav-section-label";
    secRacas.textContent = state.language === "en" ? "Playable Races" : "Raças Jogáveis";
    nav.appendChild(secRacas);

    const q = state.raceFilterText.trim().toLowerCase();
    const races = Object.values(cat.racas || {}).sort((a, b) =>
      String(a.nome_exibicao).localeCompare(String(b.nome_exibicao))
    );

    races.forEach((r) => {
      const hay = `${r.id_raca} ${r.nome_exibicao}`.toLowerCase();
      if (q && !hay.includes(q)) return;
      addNavItem(`race:${r.id_raca}`, r.nome_exibicao, r.total_formas || 0);
    });
  }

  function renderTreeChips() {
    const bar = el("treeChipBar");
    bar.innerHTML = "";
    const cat = state.catalog;
    if (!cat) return;

    const trees = [];
    if (state.navScope === "universal") {
      Object.keys(cat.formas_universais_e_stack || {}).forEach((g) => trees.push(g));
    } else if (state.navScope.startsWith("race:")) {
      const rKey = state.navScope.slice(5);
      const rObj = (cat.racas || {})[rKey];
      if (rObj) {
        Object.keys(rObj.arvores_de_transformacao || {}).forEach((t) => trees.push(t));
      }
    }

    if (trees.length === 0) return;

    const makeChip = (val, label) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chip" + (state.selectedTree === val ? " active" : "");
      btn.textContent = label;
      btn.addEventListener("click", () => {
        state.selectedTree = val;
        renderTreeChips();
        rebuildAndRenderTable();
      });
      bar.appendChild(btn);
    };

    makeChip("all", state.language === "en" ? "All Trees" : "Todas as Árvores");
    trees.forEach((tree) => makeChip(tree, tree));
  }

  function collectFilteredRows() {
    const cat = state.catalog;
    if (!cat) return [];
    const rows = [];

    if (state.navScope === "universal") {
      Object.entries(cat.formas_universais_e_stack || {}).forEach(([gKey, gObj]) => {
        if (state.selectedTree !== "all" && state.selectedTree !== gKey) return;
        (gObj.formas || []).forEach((form) => {
          rows.push({
            key: `universal:${gKey}:${form.id}`,
            escopo: "universal",
            raca: "",
            racaNome: state.language === "en" ? "Universal / Stack" : "Universal / Stack",
            arvore: gKey,
            form,
          });
        });
      });
    } else {
      const targetRace = state.navScope.startsWith("race:")
        ? state.navScope.slice(5)
        : null;
      Object.entries(cat.racas || {}).forEach(([rKey, rObj]) => {
        if (targetRace && rKey !== targetRace) return;
        Object.entries(rObj.arvores_de_transformacao || {}).forEach(([tKey, tObj]) => {
          if (targetRace && state.selectedTree !== "all" && state.selectedTree !== tKey) {
            return;
          }
          (tObj.formas || []).forEach((form) => {
            rows.push({
              key: `raca:${rKey}:${tKey}:${form.id}`,
              escopo: "raca",
              raca: rKey,
              racaNome: rObj.nome_exibicao || rKey,
              arvore: tKey,
              form,
            });
          });
        });
      });
    }

    const q = state.searchText.trim().toLowerCase();
    const qf = state.quickFilter;
    const af = state.addonFilter;

    const filtered = rows.filter((item) => {
      const f = item.form;
      const tp = f.custo_tp_numerico;
      if (qf === "tp_paid" && !(tp > 0)) return false;
      if (qf === "priceless" && !(tp < 0)) return false;
      if (qf === "free" && tp !== 0) return false;
      if (qf === "has_saga" && !(f.requisitos && f.requisitos.saga)) return false;
      if (qf === "master_only" && !f.comprar_no_mestre) return false;

      if (af !== "all") {
        if ((f.addon_origem || "") !== af) return false;
      }

      if (q) {
        const saga = (f.requisitos && f.requisitos.saga) || "";
        const addon = f.addon_origem || "";
        const tpLabel = tp < 0 ? "priceless shenron wish desejo" : String(tp);
        const hay = `${f.nome} ${f.id} ${item.racaNome} ${item.raca} ${item.arvore} ${f.tipo_habilidade} ${saga} ${addon} ${tpLabel}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    if (state.sortBy === "tp_desc") filtered.sort((a, b) => b.form.custo_tp_numerico - a.form.custo_tp_numerico);
    else if (state.sortBy === "tp_asc") filtered.sort((a, b) => a.form.custo_tp_numerico - b.form.custo_tp_numerico);
    else if (state.sortBy === "bp_desc") filtered.sort((a, b) => b.form.multiplicador_numerico_base - a.form.multiplicador_numerico_base);
    else if (state.sortBy === "bp_asc") filtered.sort((a, b) => a.form.multiplicador_numerico_base - b.form.multiplicador_numerico_base);
    else if (state.sortBy === "name_asc") filtered.sort((a, b) => String(a.form.nome).localeCompare(String(b.form.nome)));
    return filtered;
  }

  function renderTpBadgeHtml(tpNum) {
    const isEn = state.language === "en";
    if (tpNum < 0) return `<span class="badge badge-priceless">${isEn ? "Priceless / Wish" : "Priceless / Desejo"}</span>`;
    if (tpNum === 0) return `<span class="badge badge-free">${isEn ? "Free (0 TP)" : "Gratuito (0 TP)"}</span>`;
    return `<span class="badge badge-tp">${formatNumberPt(tpNum)} TP</span>`;
  }

  function rebuildAndRenderTable() {
    state.flatRows = collectFilteredRows();
    const count = state.flatRows.length;
    el("resultsLabel").textContent = state.language === "en"
      ? `Displaying ${count} transformations`
      : `Exibindo ${count} transformações`;

    const tbody = el("formsTableBody");
    const htmlParts = state.flatRows.map((row) => {
      const f = row.form;
      const aura = resolveAuraDotColor(f);
      const hair = resolveHairColor(f);
      const isSel = row.key === state.selectedKey ? " selected" : "";
      const drains = f.drenos || {};
      const drainParts = [];
      if (drains.energia_ki) drainParts.push(`Ki ${drains.energia_ki}`);
      if (drains.estamina) drainParts.push(`Stm ${drains.estamina}`);
      if (drains.vida) drainParts.push(`HP ${drains.vida}`);
      const drainTxt = drainParts.length ? drainParts.join(" · ") : "0";

      const mults = f.multiplicadores_detalhados || {};
      const strM = mults.forca_str ?? f.multiplicador_numerico_base ?? 1.0;
      const pwrM = mults.poder_ki_pwr ?? strM;
      const defM = mults.defesa_def ?? strM;
      const spdM = mults.velocidade_spd ?? 1.0;

      const flags = [];
      if (f.comprar_no_mestre) {
        const mName = f.mestre_nome || f.mestre || (state.language === "en" ? "Master" : "Mestre");
        flags.push(`<span class="badge badge-master" title="Mestre: ${escapeHtml(mName)}">🥋 ${escapeHtml(mName)}</span>`);
      }
      if (f.requisitos && f.requisitos.saga) flags.push(`<span class="badge badge-saga">${escapeHtml(f.requisitos.saga)}</span>`);
      if (f.requisitos && f.requisitos.forma_previa) flags.push(`<span class="badge badge-req">Req: ${escapeHtml(f.requisitos.forma_previa)}</span>`);
      if (drains.acumulavel) flags.push(`<span class="badge badge-stack">Stack</span>`);

      const addonHtml = f.addon_origem
        ? `<span class="badge badge-addon" style="margin-left:6px;">${escapeHtml(f.addon_origem)}</span>`
        : "";

      const hairDotHtml = hair ? `<span class="hair-dot" style="background:${hair}; box-shadow:0 0 4px ${hair};" title="Cabelo: ${hair}"></span>` : "";
      const auraBadgeHtml = (f.visual && f.visual.cor_aura)
        ? `<span class="aura-hex-badge" style="background:${aura}18; color:${aura}; border:1px solid ${aura}55;">${aura}</span>`
        : "";

      return `
        <tr class="form-row${isSel}" data-key="${escapeHtml(row.key)}">
          <td>
            <div class="form-title-cell">
              <div class="aura-orb-wrapper" title="Aura: ${aura}${hair ? ` | Cabelo: ${hair}` : ''}">
                <div class="aura-orb" style="background: radial-gradient(circle at 35% 30%, #ffffff 0%, ${aura} 60%, rgba(0,0,0,0.7) 100%); box-shadow: 0 0 10px ${aura}, inset 0 0 3px rgba(255,255,255,0.75);"></div>
                ${hairDotHtml}
              </div>
              <div>
                <div class="form-name-text">
                  <span>${escapeHtml(f.nome)}</span>
                  ${auraBadgeHtml}
                  ${addonHtml}
                </div>
                <div class="form-id-text">${escapeHtml(f.id)} · Slot ${f.nivel_habilidade}</div>
              </div>
            </div>
          </td>
          <td>
            <div style="font-weight:600;">${escapeHtml(row.racaNome)}</div>
            <div class="preset-id-hint">${escapeHtml(row.arvore)}</div>
          </td>
          <td>${renderTpBadgeHtml(f.custo_tp_numerico)}</td>
          <td>
            <div style="font-family:var(--font-mono); font-weight:700; color:#38BDF8;">${escapeHtml(f.multiplicador_bp || `${strM}x`)}</div>
            <div style="font-size:10px; color:var(--text-muted);">STR ${strM}x · PWR ${pwrM}x · DEF ${defM}x · SPD ${spdM}x</div>
          </td>
          <td style="font-family:var(--font-mono); font-size:11px; color:#FCD34D;">${escapeHtml(drainTxt)}</td>
          <td><div class="flags-cell">${flags.join("") || '<span style="color:var(--text-muted); font-size:11px;">—</span>'}</div></td>
        </tr>
      `;
    });

    tbody.innerHTML = htmlParts.join("");

    tbody.querySelectorAll(".form-row").forEach((tr) => {
      tr.addEventListener("click", () => {
        const k = tr.getAttribute("data-key");
        selectFormRow(k);
      });
    });
  }

  function selectFormRow(key) {
    state.selectedKey = key;
    el("formsTableBody").querySelectorAll(".form-row").forEach((tr) => {
      if (tr.getAttribute("data-key") === key) tr.classList.add("selected");
      else tr.classList.remove("selected");
    });
    refreshInspectorFromSelection();
  }

  function findSelectedRow() {
    if (!state.selectedKey) return null;
    return state.flatRows.find((r) => r.key === state.selectedKey) || null;
  }

  function refreshInspectorFromSelection() {
    const sel = findSelectedRow();
    const emptyBox = el("inspectorEmpty");
    const contentBox = el("inspectorContent");
    if (!sel) {
      emptyBox.style.display = "flex";
      contentBox.style.display = "none";
      return;
    }

    emptyBox.style.display = "none";
    contentBox.style.display = "flex";

    const f = sel.form;
    el("inspTitle").textContent = f.nome;
    el("inspSub").textContent = `${sel.racaNome} · ${sel.arvore} · ${f.id}`;
    
    const badgeAddon = el("inspAddonBadge");
    if (badgeAddon) {
      badgeAddon.textContent = f.addon_origem || "Core";
    }

    // Populate Inspector Fields
    el("inpTp").value = f.custo_tp_numerico;
    el("inpSkillLvl").value = f.nivel_habilidade;
    el("chkBuyMaster").checked = Boolean(f.comprar_no_mestre);
    populateMastersSelect(f.mestre, f.mestre_nome);

    const mults = f.multiplicadores_detalhados || {};
    el("mult_str").value = mults.forca_str ?? 1.0;
    el("mult_pwr").value = mults.poder_ki_pwr ?? 1.0;
    el("mult_def").value = mults.defesa_def ?? 1.0;
    el("mult_skp").value = mults.golpe_skp ?? 1.0;
    el("mult_spd").value = mults.velocidade_spd ?? 1.0;
    el("mult_atk_spd").value = mults.velocidade_ataque ?? 1.0;
    el("mult_stm").value = mults.estamina_stm ?? 1.0;
    el("mult_vit").value = mults.vitalidade_vit ?? 1.0;
    el("mult_ene").value = mults.energia_ene ?? 1.0;

    const dr = f.drenos || {};
    el("dr_ki").value = dr.energia_ki ?? 0.0;
    el("dr_stm").value = dr.estamina ?? 0.0;
    el("dr_hp").value = dr.vida ?? 0.0;
    el("dr_stm_hit").value = dr.mult_estamina_golpe ?? 1.0;
    el("dr_stack_mult").value = dr.mult_dreno_stack ?? 2.0;
    el("chkStackable").checked = Boolean(dr.acumulavel);

    const mst = f.maestria || {};
    el("mst_max").value = mst.maestria_maxima ?? 100.0;
    el("mst_instant").value = mst.maestria_transf_instantanea ?? 40.0;
    el("mst_hit_dealt").value = mst.ganho_golpe_dado ?? 0.025;
    el("mst_hit_rcv").value = mst.ganho_dano_recebido ?? 0.025;
    el("mst_passive").value = mst.ganho_passivo_5s ?? 0.01;
    el("mst_cost_mult").value = mst.mult_custo_maestria_max ?? 0.75;
    el("mst_stat_mult").value = mst.mult_status_maestria_max ?? 1.0;

    const rq = f.requisitos || {};
    el("req_dmz_lvl").value = rq.nivel_dmz_minimo ?? 1;
    el("req_lvl_req").value = rq.nivel_requisito ?? 0;
    el("req_saga").value = rq.saga || "";
    populateSagasSelect(rq.saga || "");
    el("req_prev_form").value = rq.forma_previa || "";
    populatePrevFormSelect(rq.forma_previa || "");

    const incompats = rq.incompativel_com || [];
    el("req_incompatible").value = incompats.join(", ");
    renderIncompatibleTags(incompats);
    populateIncompatibleSelect();

    const vis = f.visual || {};
    el("vis_aura").value = vis.cor_aura || "";
    el("vis_hair").value = vis.cor_cabelo || "";
    if (vis.cor_aura && vis.cor_aura.startsWith("#") && vis.cor_aura.length === 7) {
      el("vis_aura_picker").value = vis.cor_aura;
    }
    if (vis.cor_cabelo && vis.cor_cabelo.startsWith("#") && vis.cor_cabelo.length === 7) {
      el("vis_hair_picker").value = vis.cor_cabelo;
    }

    updateInspectorPreviews();
    updateAuraLivePreview();
  }

  function updateInspectorPreviews() {
    const tpVal = parseInt(el("inpTp").value, 10);
    const prevTp = el("inspTpPreview");
    if (tpVal < 0) {
      prevTp.textContent = state.language === "en" ? "Priceless / Wish" : "Priceless / Desejo";
      prevTp.className = "badge badge-priceless";
    } else if (tpVal === 0) {
      prevTp.textContent = state.language === "en" ? "Free (0 TP)" : "Gratuito (0 TP)";
      prevTp.className = "badge badge-free";
    } else {
      prevTp.textContent = `${formatNumberPt(tpVal || 0)} TP`;
      prevTp.className = "badge badge-tp";
    }

    const strM = parseFloat(el("mult_str").value) || 1.0;
    const pwrM = parseFloat(el("mult_pwr").value) || 1.0;
    const prevBp = el("inspBpPreview");
    prevBp.textContent = strM === pwrM ? `${strM}x` : `${strM}x (STR) / ${pwrM}x (PWR)`;
  }

  function populateSagasSelect(selectedVal) {
    const sel = el("req_saga_select");
    if (!sel) return;
    const sagas = (state.catalog && state.catalog.opcoes_sagas) || [];
    sel.innerHTML = `<option value="">${t("opt_no_saga")}</option>`;

    let foundExact = false;
    const cleanSel = (selectedVal || "").trim();

    sagas.forEach((saga) => {
      const optgroup = document.createElement("optgroup");
      optgroup.label = saga.nome;
      (saga.quests || []).forEach((q) => {
        const opt = document.createElement("option");
        opt.value = q.valor;
        const qNumText = q.numero > 0 ? `[#${q.numero}] ` : "";
        opt.textContent = `${qNumText}${q.titulo} (${q.valor})`;
        if (cleanSel && q.valor === cleanSel) {
          opt.selected = true;
          foundExact = true;
        }
        optgroup.appendChild(opt);
      });
      if (optgroup.children.length > 0) {
        sel.appendChild(optgroup);
      }
    });

    if (cleanSel && !foundExact) {
      const customOpt = document.createElement("option");
      customOpt.value = cleanSel;
      customOpt.textContent = `Personalizada: ${cleanSel}`;
      customOpt.selected = true;
      sel.appendChild(customOpt);
    }

    if (!cleanSel) {
      sel.value = "";
    }
  }

  function populateMastersSelect(masterId, masterName) {
    const sel = el("inpMasterSelect");
    const badge = el("inpMasterBadge");
    if (!sel) return;
    const masters = (state.catalog && state.catalog.opcoes_mestres) || [];
    sel.innerHTML = `<option value="">${t("opt_no_master")}</option>`;

    const curId = (masterId || "").trim();
    let found = false;

    masters.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = `${m.nome} (${m.id})`;
      if (curId && (m.id === curId || m.nome === masterName)) {
        opt.selected = true;
        found = true;
      }
      sel.appendChild(opt);
    });

    if (curId && !found) {
      const opt = document.createElement("option");
      opt.value = curId;
      opt.textContent = `${masterName || curId} (${curId})`;
      opt.selected = true;
      sel.appendChild(opt);
    }

    if (badge) {
      const activeName = masterName || (sel.selectedOptions[0] && sel.selectedOptions[0].textContent) || "—";
      badge.textContent = curId ? `🥋 ${activeName.split("(")[0].trim()}` : "—";
    }

    sel.disabled = !el("chkBuyMaster").checked;
  }

  function updateAuraLivePreview() {
    const auraInp = el("vis_aura");
    const hairInp = el("vis_hair");
    let auraHex = (auraInp && auraInp.value.trim()) || "";
    let hairHex = (hairInp && hairInp.value.trim()) || "";

    if (auraHex && !auraHex.startsWith("#") && /^[0-9a-fA-F]{3,8}$/.test(auraHex)) auraHex = "#" + auraHex;
    if (hairHex && !hairHex.startsWith("#") && /^[0-9a-fA-F]{3,8}$/.test(hairHex)) hairHex = "#" + hairHex;
    if (!auraHex) {
      const sel = findSelectedRow();
      auraHex = sel ? resolveAuraDotColor(sel.form) : "#FFD700";
    }
    if (!hairHex) hairHex = "#000000";

    const glow = el("auraFlameGlow");
    const orb = el("auraFlameOrb");
    const hairDot = el("hairFlameDot");
    const badgeAura = el("auraHexBadge");
    const badgeHair = el("hairHexBadge");

    if (glow) glow.style.background = auraHex;
    if (orb) {
      orb.style.background = `radial-gradient(circle at 35% 30%, #ffffff 0%, ${auraHex} 60%, rgba(0,0,0,0.7) 100%)`;
      orb.style.boxShadow = `0 0 14px ${auraHex}`;
    }
    if (hairDot) hairDot.style.background = hairHex;
    if (badgeAura) {
      badgeAura.textContent = `Aura: ${auraHex}`;
      badgeAura.style.color = auraHex;
      badgeAura.style.borderColor = auraHex;
      badgeAura.style.background = `${auraHex}22`;
    }
    if (badgeHair) {
      badgeHair.textContent = `Cabelo: ${hairHex}`;
      badgeHair.style.borderColor = hairHex;
    }
  }

  function getAllCatalogForms(excludeId = null) {
    const list = [];
    const cat = state.catalog || {};

    // 1. Race forms
    Object.entries(cat.racas || {}).forEach(([rKey, rObj]) => {
      const rNome = rObj.nome_exibicao || rKey;
      Object.entries(rObj.arvores_de_transformacao || {}).forEach(([tKey, tObj]) => {
        (tObj.formas || []).forEach((form) => {
          if (excludeId && (form.id === excludeId || `${tKey}.${form.id}` === excludeId)) return;
          list.push({
            id: form.id,
            nome: form.nome || form.id,
            raca: rKey,
            racaNome: rNome,
            arvore: tKey,
            escopo: "raca",
            qualifiedId: `${tKey}.${form.id}`,
            addon: form.addon_origem || "",
          });
        });
      });
    });

    // 2. Universal forms
    Object.entries(cat.formas_universais_e_stack || {}).forEach(([gKey, gObj]) => {
      (gObj.formas || []).forEach((form) => {
        if (excludeId && (form.id === excludeId || `${gKey}.${form.id}` === excludeId)) return;
        list.push({
          id: form.id,
          nome: form.nome || form.id,
          raca: "universal",
          racaNome: "Universal / Stack",
          arvore: gKey,
          escopo: "universal",
          qualifiedId: `${gKey}.${form.id}`,
          addon: form.addon_origem || "",
        });
      });
    });

    return list;
  }

  function populatePrevFormSelect(selectedVal) {
    const sel = el("req_prev_form_select");
    if (!sel) return;
    const curRow = findSelectedRow();
    const curTree = curRow ? curRow.arvore : "";
    const curRace = curRow ? curRow.raca : "";
    const curId = curRow ? curRow.form.id : "";

    sel.innerHTML = `<option value="">${state.language === "en" ? "— No prior form required —" : "— Nenhuma forma prévia exigida —"}</option>`;

    const allForms = getAllCatalogForms(curId);
    const cleanSel = (selectedVal || "").trim();
    let foundExact = false;

    const sameTree = [];
    const sameRaceOtherTrees = [];
    const universalForms = [];
    const otherForms = [];

    allForms.forEach((f) => {
      if (curRow && curRow.escopo === "raca") {
        if (f.raca === curRace && f.arvore === curTree) sameTree.push(f);
        else if (f.raca === curRace) sameRaceOtherTrees.push(f);
        else if (f.escopo === "universal") universalForms.push(f);
        else otherForms.push(f);
      } else {
        if (f.escopo === "universal" && f.arvore === curTree) sameTree.push(f);
        else if (f.escopo === "universal") universalForms.push(f);
        else otherForms.push(f);
      }
    });

    const addGroup = (label, list) => {
      if (!list || list.length === 0) return;
      const grp = document.createElement("optgroup");
      grp.label = label;
      list.forEach((f) => {
        const opt = document.createElement("option");
        opt.value = f.qualifiedId;
        opt.textContent = `${f.nome} (${f.qualifiedId})`;
        if (cleanSel && (f.qualifiedId === cleanSel || f.id === cleanSel)) {
          opt.selected = true;
          foundExact = true;
        }
        grp.appendChild(opt);
      });
      sel.appendChild(grp);
    };

    const isEn = state.language === "en";
    addGroup(isEn ? `⚡ Same Tree (${curTree})` : `⚡ Mesma Árvore (${curTree})`, sameTree);
    addGroup(isEn ? `🧬 Other Trees of Race (${curRow ? curRow.racaNome : ""})` : `🧬 Outras Árvores da Raça (${curRow ? curRow.racaNome : ""})`, sameRaceOtherTrees);
    addGroup(isEn ? "🌌 Universal & Stack Forms" : "🌌 Formas Universais & Stack", universalForms);
    addGroup(isEn ? "🌐 Other Races" : "🌐 Outras Raças", otherForms);

    if (cleanSel && !foundExact) {
      const customOpt = document.createElement("option");
      customOpt.value = cleanSel;
      customOpt.textContent = `Personalizada: ${cleanSel}`;
      customOpt.selected = true;
      sel.appendChild(customOpt);
    }

    if (!cleanSel) {
      sel.value = "";
    }
  }

  function getIncompatibleList() {
    const raw = (el("req_incompatible") ? el("req_incompatible").value : "") || "";
    return raw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  }

  function setIncompatibleList(list) {
    const unique = Array.from(new Set(list));
    if (el("req_incompatible")) {
      el("req_incompatible").value = unique.join(", ");
    }
    renderIncompatibleTags(unique);
  }

  function renderIncompatibleTags(list) {
    const container = el("incompatibleTagsContainer");
    const countBadge = el("incompatibleCountBadge");
    if (!container) return;
    container.innerHTML = "";

    const items = list || [];
    if (countBadge) {
      countBadge.textContent = state.language === "en"
        ? `${items.length} incompatible`
        : `${items.length} incompatíveis`;
    }

    if (items.length === 0) {
      container.innerHTML = `<span style="font-size:11px; color:var(--text-muted); font-style:italic;">${state.language === "en" ? "No mutual block configured (stacks freely)." : "Nenhum bloqueio mútuo configurado (pode acumular livremente)."}</span>`;
      return;
    }

    const allForms = getAllCatalogForms();
    const formMap = new Map();
    allForms.forEach((f) => {
      formMap.set(f.qualifiedId, f.nome);
      formMap.set(f.id, f.nome);
    });

    items.forEach((id) => {
      const friendlyName = formMap.get(id) || id;
      const tag = document.createElement("span");
      tag.className = "incompat-tag";
      tag.innerHTML = `
        <span class="incompat-tag-text">🚫 <strong>${escapeHtml(friendlyName)}</strong> <span style="font-family:var(--font-mono); font-size:9.5px; opacity:0.8;">(${escapeHtml(id)})</span></span>
        <button type="button" class="incompat-tag-remove" data-id="${escapeHtml(id)}" title="Remover incompatibilidade">✕</button>
      `;
      container.appendChild(tag);
    });

    container.querySelectorAll(".incompat-tag-remove").forEach((btn) => {
      btn.addEventListener("click", () => {
        const idToRemove = btn.getAttribute("data-id");
        removeIncompatibleForm(idToRemove);
      });
    });
  }

  function populateIncompatibleSelect() {
    const sel = el("req_incompatible_select");
    if (!sel) return;
    const curRow = findSelectedRow();
    const curTree = curRow ? curRow.arvore : "";
    const curRace = curRow ? curRow.raca : "";
    const curId = curRow ? curRow.form.id : "";

    sel.innerHTML = `<option value="">${state.language === "en" ? "➕ Select a form to add to mutual block..." : "➕ Selecione uma forma para adicionar ao bloqueio mútuo..."}</option>`;

    const allForms = getAllCatalogForms(curId);
    const sameTree = [];
    const sameRaceOtherTrees = [];
    const universalForms = [];
    const otherForms = [];

    allForms.forEach((f) => {
      if (curRow && curRow.escopo === "raca") {
        if (f.raca === curRace && f.arvore === curTree) sameTree.push(f);
        else if (f.raca === curRace) sameRaceOtherTrees.push(f);
        else if (f.escopo === "universal") universalForms.push(f);
        else otherForms.push(f);
      } else {
        if (f.escopo === "universal" && f.arvore === curTree) sameTree.push(f);
        else if (f.escopo === "universal") universalForms.push(f);
        else otherForms.push(f);
      }
    });

    const isEn = state.language === "en";
    const addGroup = (label, list) => {
      if (!list || list.length === 0) return;
      const grp = document.createElement("optgroup");
      grp.label = label;
      list.forEach((f) => {
        const opt = document.createElement("option");
        opt.value = f.qualifiedId;
        opt.textContent = `${f.nome} (${f.qualifiedId})`;
        grp.appendChild(opt);
      });
      sel.appendChild(grp);
    };

    addGroup(isEn ? "🌌 Universal & Stack Forms (Most Common)" : "🌌 Formas Universais & Stack (Mais Comuns)", universalForms);
    addGroup(isEn ? `⚡ Same Tree (${curTree})` : `⚡ Mesma Árvore (${curTree})`, sameTree);
    addGroup(isEn ? `🧬 Other Trees of Race (${curRow ? curRow.racaNome : ""})` : `🧬 Outras Árvores da Raça (${curRow ? curRow.racaNome : ""})`, sameRaceOtherTrees);
    addGroup(isEn ? "🌐 Other Races" : "🌐 Outras Raças", otherForms);
  }

  function addIncompatibleForm(formId) {
    if (!formId) return;
    const cur = getIncompatibleList();
    if (!cur.includes(formId)) {
      cur.push(formId);
      setIncompatibleList(cur);
      showToast(state.language === "en" ? `Added ${formId} to incompatible forms!` : `Adicionada incompatibilidade com ${formId}!`);
    } else {
      showToast(state.language === "en" ? "Form is already in incompatible list." : "Essa forma já está na lista de incompatíveis.", true);
    }
    if (el("req_incompatible_select")) el("req_incompatible_select").value = "";
  }

  function removeIncompatibleForm(formId) {
    if (!formId) return;
    const cur = getIncompatibleList().filter((x) => x !== formId);
    setIncompatibleList(cur);
  }

  function updateAddFormAuraPreview() {
    const auraInp = el("add_cor_aura");
    const hairInp = el("add_cor_cabelo");
    let auraHex = (auraInp && auraInp.value.trim()) || "#FFD700";
    let hairHex = (hairInp && hairInp.value.trim()) || "#FFE89E";

    if (auraHex && !auraHex.startsWith("#") && /^[0-9a-fA-F]{3,8}$/.test(auraHex)) auraHex = "#" + auraHex;
    if (hairHex && !hairHex.startsWith("#") && /^[0-9a-fA-F]{3,8}$/.test(hairHex)) hairHex = "#" + hairHex;

    const glow = el("addAuraFlameGlow");
    const orb = el("addAuraFlameOrb");
    const hairDot = el("addHairFlameDot");
    const badgeAura = el("addAuraHexBadge");
    const badgeHair = el("addHairHexBadge");

    if (glow) glow.style.background = auraHex;
    if (orb) {
      orb.style.background = `radial-gradient(circle at 35% 30%, #ffffff 0%, ${auraHex} 60%, rgba(0,0,0,0.7) 100%)`;
      orb.style.boxShadow = `0 0 12px ${auraHex}`;
    }
    if (hairDot) hairDot.style.background = hairHex;
    if (badgeAura) {
      badgeAura.textContent = `Aura: ${auraHex}`;
      badgeAura.style.color = auraHex;
      badgeAura.style.borderColor = auraHex;
      badgeAura.style.background = `${auraHex}22`;
    }
    if (badgeHair) {
      badgeHair.textContent = `Cabelo: ${hairHex}`;
      badgeHair.style.borderColor = hairHex;
    }
    if (el("add_cor_aura_picker") && auraHex.length === 7) el("add_cor_aura_picker").value = auraHex;
    if (el("add_cor_cabelo_picker") && hairHex.length === 7) el("add_cor_cabelo_picker").value = hairHex;
  }

  function updateAddFormBpPreview() {
    const str = parseFloat(el("add_mult_str").value) || 1.0;
    const pwr = parseFloat(el("add_mult_pwr").value) || 1.0;
    const prev = el("addBpPreview");
    if (prev) {
      prev.textContent = str === pwr ? `${str.toFixed(2)}x` : `${str.toFixed(2)}x (STR) / ${pwr.toFixed(2)}x (PWR)`;
    }
  }

  function updateAddFormTpPreview() {
    const tpVal = parseInt(el("add_tp").value, 10);
    const badge = el("addTpBadgePreview");
    if (!badge) return;
    if (tpVal < 0) {
      badge.textContent = state.language === "en" ? "Priceless / Wish" : "Priceless / Desejo";
      badge.className = "badge badge-priceless";
    } else if (tpVal === 0) {
      badge.textContent = state.language === "en" ? "Free (0 TP)" : "Gratuito (0 TP)";
      badge.className = "badge badge-free";
    } else {
      badge.textContent = `${formatNumberPt(tpVal || 0)} TP`;
      badge.className = "badge badge-tp";
    }
  }

  function buildFormUpdatePayload() {
    const sel = findSelectedRow();
    if (!sel) return null;

    const mSel = el("inpMasterSelect");
    const chosenMasterId = (mSel && el("chkBuyMaster").checked) ? mSel.value.trim() : "";
    const chosenMasterName = (mSel && chosenMasterId && mSel.selectedOptions[0])
      ? mSel.selectedOptions[0].textContent.split("(")[0].trim()
      : "";

    const payload = {
      escopo: sel.escopo,
      id: sel.form.id,
      raca: sel.raca,
      arvore: sel.arvore,
      grupo: sel.arvore,
      custo_tp_numerico: parseInt(el("inpTp").value, 10),
      nivel_habilidade: parseInt(el("inpSkillLvl").value, 10),
      comprar_no_mestre: el("chkBuyMaster").checked,
      mestre: chosenMasterId,
      mestre_nome: chosenMasterName,
      multiplicadores_detalhados: {
        forca_str: parseFloat(el("mult_str").value) || 1.0,
        poder_ki_pwr: parseFloat(el("mult_pwr").value) || 1.0,
        defesa_def: parseFloat(el("mult_def").value) || 1.0,
        golpe_skp: parseFloat(el("mult_skp").value) || 1.0,
        velocidade_spd: parseFloat(el("mult_spd").value) || 1.0,
        velocidade_ataque: parseFloat(el("mult_atk_spd").value) || 1.0,
        estamina_stm: parseFloat(el("mult_stm").value) || 1.0,
        vitalidade_vit: parseFloat(el("mult_vit").value) || 1.0,
        energia_ene: parseFloat(el("mult_ene").value) || 1.0,
      },
      drenos: {
        energia_ki: parseFloat(el("dr_ki").value) || 0.0,
        estamina: parseFloat(el("dr_stm").value) || 0.0,
        vida: parseFloat(el("dr_hp").value) || 0.0,
        mult_estamina_golpe: parseFloat(el("dr_stm_hit").value) || 1.0,
        mult_dreno_stack: parseFloat(el("dr_stack_mult").value) || 2.0,
        acumulavel: el("chkStackable").checked,
      },
      maestria: {
        maestria_maxima: parseFloat(el("mst_max").value) || 100.0,
        maestria_transf_instantanea: parseFloat(el("mst_instant").value) || 40.0,
        ganho_golpe_dado: parseFloat(el("mst_hit_dealt").value) || 0.025,
        ganho_dano_recebido: parseFloat(el("mst_hit_rcv").value) || 0.025,
        ganho_passivo_5s: parseFloat(el("mst_passive").value) || 0.01,
        mult_custo_maestria_max: parseFloat(el("mst_cost_mult").value) || 0.75,
        mult_status_maestria_max: parseFloat(el("mst_stat_mult").value) || 1.0,
      },
      requisitos: {
        nivel_dmz_minimo: parseInt(el("req_dmz_lvl").value, 10) || 1,
        nivel_requisito: parseInt(el("req_lvl_req").value, 10) || 0,
        saga: el("req_saga").value.trim() || null,
        forma_previa: el("req_prev_form").value.trim() || null,
        incompativel_com: el("req_incompatible").value
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      },
      visual: {
        cor_aura: el("vis_aura").value.trim(),
        cor_cabelo: el("vis_hair").value.trim(),
      },
    };
    return payload;
  }

  async function handleApplyForm() {
    const payload = buildFormUpdatePayload();
    if (!payload) return;
    try {
      const data = await apiPost("/api/update-form", payload);
      applyServerState(data);
      showToast(state.language === "en" ? "Transformation updated!" : "Transformação atualizada com sucesso!");
    } catch (err) {
      showToast(err.message, true);
    }
  }

  // Modal Helpers
  function openModal(id) {
    const modal = el(id);
    if (!modal) return;
    modal.classList.add("active");
    modal.classList.add("open");
  }

  function closeModal(id) {
    const modal = el(id);
    if (!modal) return;
    modal.classList.remove("active");
    modal.classList.remove("open");
  }

  function closeAllModals() {
    document.querySelectorAll(".modal-backdrop").forEach((m) => {
      m.classList.remove("active");
      m.classList.remove("open");
    });
  }

  // Add Form Modal logic
  function openAddFormModal() {
    const cat = state.catalog;
    if (!cat) return;

    const rSelect = el("add_raca");
    const tSelect = el("add_arvore");
    rSelect.innerHTML = "";
    tSelect.innerHTML = "";

    const races = Object.values(cat.racas || {}).sort((a, b) =>
      String(a.nome_exibicao).localeCompare(String(b.nome_exibicao))
    );
    races.forEach((r) => {
      const opt = document.createElement("option");
      opt.value = r.id_raca;
      opt.textContent = r.nome_exibicao;
      rSelect.appendChild(opt);
    });

    const updateTreeSelect = () => {
      tSelect.innerHTML = "";
      const chosenRace = rSelect.value;
      const rObj = (cat.racas || {})[chosenRace];
      if (rObj) {
        Object.keys(rObj.arvores_de_transformacao || {}).forEach((tName) => {
          const opt = document.createElement("option");
          opt.value = tName;
          opt.textContent = tName;
          tSelect.appendChild(opt);
        });
      }
      const optCustom = document.createElement("option");
      optCustom.value = "customforms";
      optCustom.textContent = "+ customforms";
      tSelect.appendChild(optCustom);
    };

    const escopoSelect = el("add_escopo");
    const raceGroup = el("add_race_group");
    const scopeGrid = el("add_scope_grid");
    const lblTree = el("lbl_add_arvore");

    const updateScopeAndTrees = () => {
      const isUniversal = escopoSelect && escopoSelect.value === "universal";
      if (isUniversal) {
        if (raceGroup) raceGroup.style.display = "none";
        if (scopeGrid) scopeGrid.style.gridTemplateColumns = "1fr 1fr";
        if (lblTree) {
          lblTree.textContent = state.language === "en" ? "Universal Group" : "Grupo Universal";
        }
        tSelect.innerHTML = "";
        const uGroups = Object.keys(cat.formas_universais_e_stack || {});
        if (uGroups.length === 0) uGroups.push("stack", "forms");
        uGroups.forEach((g) => {
          const opt = document.createElement("option");
          opt.value = g;
          opt.textContent = g;
          tSelect.appendChild(opt);
        });
        const optCustom = document.createElement("option");
        optCustom.value = "customgroup";
        optCustom.textContent = "+ customgroup";
        tSelect.appendChild(optCustom);
      } else {
        if (raceGroup) raceGroup.style.display = "";
        if (scopeGrid) scopeGrid.style.gridTemplateColumns = "";
        if (lblTree) {
          lblTree.textContent = state.language === "en" ? "Transformation Tree" : "Árvore de Transformação";
        }
        updateTreeSelect();
      }
    };

    if (escopoSelect) escopoSelect.onchange = updateScopeAndTrees;
    rSelect.onchange = updateTreeSelect;
    updateScopeAndTrees();

    // Populate Sagas Select
    const sagaSel = el("add_saga_select");
    if (sagaSel) {
      sagaSel.innerHTML = `<option value="">${state.language === "en" ? "— No saga required —" : "— Nenhuma saga exigida —"}</option>`;
      const sagas = (cat && cat.opcoes_sagas) || [];
      sagas.forEach((saga) => {
        const optgroup = document.createElement("optgroup");
        optgroup.label = saga.nome;
        (saga.quests || []).forEach((q) => {
          const opt = document.createElement("option");
          opt.value = q.valor;
          const qNum = q.numero > 0 ? `[#${q.numero}] ` : "";
          opt.textContent = `${qNum}${q.titulo} (${q.valor})`;
          optgroup.appendChild(opt);
        });
        if (optgroup.children.length > 0) sagaSel.appendChild(optgroup);
      });
    }

    // Populate Master Select
    const mSel = el("add_mestre_select");
    if (mSel) {
      mSel.innerHTML = `<option value="">${state.language === "en" ? "— No master required —" : "— Nenhum mestre exigido —"}</option>`;
      const masters = (cat && cat.opcoes_mestres) || [];
      masters.forEach((m) => {
        const opt = document.createElement("option");
        opt.value = m.id;
        opt.textContent = `${m.nome} (${m.id})`;
        mSel.appendChild(opt);
      });
    }

    // Populate Prior Form Select
    const prevSel = el("add_prev_form_select");
    if (prevSel) {
      prevSel.innerHTML = `<option value="">${state.language === "en" ? "— No prior form required —" : "— Nenhuma forma prévia exigida —"}</option>`;
      const allForms = getAllCatalogForms();
      allForms.forEach((f) => {
        const opt = document.createElement("option");
        opt.value = f.qualifiedId;
        opt.textContent = `${f.nome} (${f.qualifiedId})`;
        prevSel.appendChild(opt);
      });
    }

    // Auto-slug sync and defaults
    const idInp = el("add_id");
    const nomeInp = el("add_nome");
    if (idInp) {
      idInp.value = "";
      idInp.dataset.userEdited = "";
      idInp.oninput = () => {
        idInp.dataset.userEdited = "true";
      };
    }
    if (nomeInp) {
      nomeInp.value = "";
      nomeInp.oninput = (e) => {
        if (idInp && !idInp.dataset.userEdited) {
          idInp.value = e.target.value
            .toLowerCase()
            .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]+/g, "_")
            .replace(/^_+|_+$/g, "");
        }
      };
    }

    el("add_tp").value = "500000";
    el("add_lvl").value = "1";
    el("add_addon").value = "Dragon Mine Z (Core)";
    el("add_mult_str").value = "2.5";
    el("add_mult_pwr").value = "2.5";
    el("add_mult_def").value = "2.5";
    el("add_mult_skp").value = "2.5";
    el("add_cor_aura").value = "#FFD700";
    el("add_cor_cabelo").value = "#FFE89E";

    // Translate modal elements dynamically
    document.querySelectorAll("#addFormModal [data-i18n]").forEach((elem) => {
      const k = elem.getAttribute("data-i18n");
      if (k) elem.textContent = t(k);
    });

    updateAddFormAuraPreview();
    updateAddFormBpPreview();
    updateAddFormTpPreview();

    openModal("addFormModal");
  }

  async function handleConfirmAddForm() {
    const escopo = el("add_escopo").value;
    const raca = el("add_raca").value;
    const arvore = el("add_arvore").value;
    const formId = el("add_id").value.trim().toLowerCase();
    const nome = el("add_nome").value.trim();

    if (!formId) {
      showToast(state.language === "en" ? "Form ID is required!" : "ID da forma é obrigatório!", true);
      return;
    }

    const chosenMasterId = el("add_mestre_select") ? el("add_mestre_select").value.trim() : "";
    const mOpt = el("add_mestre_select") && el("add_mestre_select").selectedOptions[0];
    const chosenMasterName = (mOpt && chosenMasterId) ? mOpt.textContent.split("(")[0].trim() : "";
    const chosenSaga = el("add_saga_select") ? el("add_saga_select").value.trim() : "";
    const chosenPrevForm = el("add_prev_form_select") ? el("add_prev_form_select").value.trim() : "";

    const payload = {
      escopo,
      raca,
      arvore,
      grupo: arvore,
      id: formId,
      nome: nome || formId,
      custo_tp_numerico: parseInt(el("add_tp").value, 10) || 0,
      nivel_habilidade: parseInt(el("add_lvl").value, 10) || 1,
      addon_origem: el("add_addon").value.trim() || "Dragon Mine Z (Core)",
      comprar_no_mestre: Boolean(chosenMasterId),
      mestre: chosenMasterId,
      mestre_nome: chosenMasterName,
      multiplicadores_detalhados: {
        forca_str: parseFloat(el("add_mult_str").value) || 2.5,
        poder_ki_pwr: parseFloat(el("add_mult_pwr").value) || 2.5,
        defesa_def: parseFloat(el("add_mult_def").value) || 2.5,
        golpe_skp: parseFloat(el("add_mult_skp").value) || 2.5,
      },
      requisitos: {
        nivel_dmz_minimo: 1,
        nivel_requisito: 0,
        saga: chosenSaga || null,
        forma_previa: chosenPrevForm || null,
        incompativel_com: [],
      },
      visual: {
        cor_aura: el("add_cor_aura").value.trim(),
        cor_cabelo: el("add_cor_cabelo").value.trim(),
      },
    };

    try {
      const data = await apiPost("/api/form/add", payload);
      closeModal("addFormModal");
      applyServerState(data);
      const targetKey = escopo === "universal" ? `universal:${arvore}:${formId}` : `raca:${raca}:${arvore}:${formId}`;
      selectFormRow(targetKey);
      showToast(state.language === "en" ? "Transformation created! Press Ctrl+Z to undo." : "Transformação criada! Pressione Ctrl+Z para desfazer.");
    } catch (err) {
      showToast(err.message, true);
    }
  }

  // Delete Form Modal logic
  function openDeleteFormModal() {
    const sel = findSelectedRow();
    if (!sel) return;
    const f = sel.form;
    const isEn = state.language === "en";
    el("deleteModalDesc").textContent = isEn
      ? `Are you sure you want to permanently delete '${f.nome}' (${f.id}) from ${sel.racaNome}?`
      : `Tem certeza de que deseja remover permanentemente '${f.nome}' (${f.id}) de ${sel.racaNome}?`;
    openModal("deleteFormModal");
  }

  async function handleConfirmDeleteForm() {
    const sel = findSelectedRow();
    if (!sel) return;
    const payload = {
      escopo: sel.escopo,
      raca: sel.raca,
      arvore: sel.arvore,
      grupo: sel.arvore,
      id: sel.form.id,
    };
    try {
      const data = await apiPost("/api/form/delete", payload);
      closeModal("deleteFormModal");
      applyServerState(data);
      showToast(state.language === "en" ? "Transformation deleted! Press Ctrl+Z to undo." : "Transformação removida! Pressione Ctrl+Z para desfazer.");
    } catch (err) {
      showToast(err.message, true);
    }
  }

  // Addons Manager Modal logic
  async function openAddonsModal(force = false) {
    openModal("addonsModal");
    const loadState = el("addonsLoadingState");
    const contentState = el("addonsContentState");
    if (loadState) loadState.style.display = "flex";
    if (contentState) contentState.style.display = "none";

    try {
      const data = await apiGet(force ? "/api/addons?force=1" : "/api/addons");
      state.addonsList = data.addons || [];
      renderAddonsCards();
      if (loadState) loadState.style.display = "none";
      if (contentState) contentState.style.display = "flex";
    } catch (err) {
      if (loadState) loadState.style.display = "none";
      showToast(err.message, true);
    }
  }

  function renderAddonsCards() {
    const container = el("addonsCardList");
    if (!container) return;
    container.innerHTML = "";

    const allAddons = state.addonsList || [];
    const activeCount = allAddons.filter((a) => a.enabled).length;
    const disabledCount = allAddons.filter((a) => !a.enabled).length;

    if (el("addonsCountBadge")) el("addonsCountBadge").textContent = `${allAddons.length} Addons`;
    if (el("addonCountAll")) el("addonCountAll").textContent = String(allAddons.length);
    if (el("addonCountActive")) el("addonCountActive").textContent = String(activeCount);
    if (el("addonCountDisabled")) el("addonCountDisabled").textContent = String(disabledCount);

    const q = (state.addonFilterText || "").toLowerCase();
    const tab = state.addonActiveTab || "all";

    const filtered = allAddons.filter((add) => {
      if (tab === "active" && !add.enabled) return false;
      if (tab === "disabled" && add.enabled) return false;
      if (q) {
        const hay = `${add.display_name} ${add.mod_id} ${add.authors} ${add.filename} ${add.description}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:32px 16px; color:var(--text-muted); background:rgba(15,23,42,0.4); border-radius:var(--radius-md); border:1px dashed var(--border-default);">
          <div style="font-size:28px; margin-bottom:8px;">🧩</div>
          <div style="font-size:13px; font-weight:600; color:#CBD5E1;">${state.language === "en" ? "No addons found matching filters." : "Nenhum addon encontrado para os filtros selecionados."}</div>
        </div>
      `;
      return;
    }

    filtered.forEach((add) => {
      const card = document.createElement("div");
      card.className = add.enabled ? "addon-card" : "addon-card disabled";
      const isChecked = add.enabled ? " checked" : "";
      const formsCount = (add.contributed_forms || []).length;
      const formsBadge = formsCount > 0
        ? `<span class="badge badge-addon" style="font-size:10px;">⚡ ${formsCount} ${state.language === "en" ? "Forms" : "Formas"}</span>`
        : "";

      card.innerHTML = `
        <div class="addon-card-left">
          <label class="switch-toggle" style="margin-right:4px;">
            <input type="checkbox" class="addon-toggle-chk" data-file="${escapeHtml(add.filename)}"${isChecked}>
            <span class="switch-slider"></span>
          </label>
          <div class="addon-card-info">
            <div class="addon-card-title">
              <span>${escapeHtml(add.display_name)}</span>
              <span class="badge" style="background:rgba(255,255,255,0.08); color:#CBD5E1; font-size:10.5px;">v${escapeHtml(add.version)}</span>
              <span class="badge" style="background:rgba(56,189,248,0.12); color:#38BDF8; font-size:10.5px;">${add.size_mb} MB</span>
              ${formsBadge}
            </div>
            ${add.description ? `<div class="addon-card-desc">${escapeHtml(add.description)}</div>` : ''}
            <div class="addon-card-meta">
              <span>👤 ${escapeHtml(add.authors || "Community")}</span>
              <span style="font-family:var(--font-mono); color:#67E8F9;">📄 ${escapeHtml(add.filename)}</span>
            </div>
          </div>
        </div>
        <div>
          <span class="addon-status-pill ${add.enabled ? 'active' : 'disabled'}">
            ${add.enabled ? '● ' + t('addon_enabled') : '○ ' + t('addon_disabled')}
          </span>
        </div>
      `;
      container.appendChild(card);
    });

    container.querySelectorAll(".addon-toggle-chk").forEach((chk) => {
      chk.addEventListener("change", async () => {
        const fname = chk.getAttribute("data-file");
        const enVal = chk.checked;
        try {
          const res = await apiPost("/api/addons/toggle", { filename: fname, enabled: enVal });
          showToast(enVal ? `Addon ${fname} ativado!` : `Addon ${fname} desativado!`);
          state.addonsList = res.addons || [];
          renderAddonsCards();
        } catch (err) {
          chk.checked = !enVal;
          showToast(err.message, true);
        }
      });
    });
  }

  // Keyboard Shortcuts
  window.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && !e.shiftKey) {
      e.preventDefault();
      if (state.canUndo) apiPost("/api/undo").then(applyServerState).catch((err) => showToast(err.message, true));
    } else if (
      ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") ||
      ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "z")
    ) {
      e.preventDefault();
      if (state.canRedo) apiPost("/api/redo").then(applyServerState).catch((err) => showToast(err.message, true));
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
      e.preventDefault();
      apiPost("/api/save-json").then((data) => {
        applyServerState(data);
        showToast(state.language === "en" ? "Saved to JSON!" : "Salvo no JSON!");
      }).catch((err) => showToast(err.message, true));
    } else if (e.key === "Escape") {
      closeAllModals();
    }
  });

  async function loadDetectedLocations() {
    const container = el("detectedChipsContainer");
    const countBadge = el("detectedCountLabel");
    if (!container) return;
    try {
      const data = await apiPost("/api/detect-locations");
      const modpacks = data.detected_modpacks || [];
      const jsons = data.detected_jsons || [];
      const total = modpacks.length + jsons.length;
      if (countBadge) countBadge.textContent = `${total} encontrados`;

      container.innerHTML = "";
      if (total === 0) {
        container.innerHTML = `<div style="font-size:11.5px; color:var(--text-muted);">${state.language === "en" ? "No standard locations detected automatically. Use Browse buttons or paste the path." : "Nenhum local padrão detectado automaticamente. Use os botões Procurar ou cole o caminho."}</div>`;
        return;
      }

      modpacks.forEach((p) => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = "btn btn-emerald";
        item.style.cssText = "justify-content:flex-start; text-align:left; height:auto; padding:6px 10px; font-size:11.5px; border-radius:6px; width:100%; word-break:break-all;";
        const label = p.replace(/\\/g, "/").split("/").slice(-3).join("/");
        item.innerHTML = `📁 <strong>Usar Modpack:</strong> ${escapeHtml(label)} <span style="font-size:10px; opacity:0.8; margin-left:auto;">(Clique para selecionar)</span>`;
        item.addEventListener("click", () => {
          el("inpModpackPath").value = p;
          showToast(state.language === "en" ? `Selected: ${label}` : `Selecionado: ${label}`);
        });
        container.appendChild(item);
      });

      jsons.forEach((j) => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = "btn btn-cyan";
        item.style.cssText = "justify-content:flex-start; text-align:left; height:auto; padding:6px 10px; font-size:11.5px; border-radius:6px; width:100%; word-break:break-all;";
        const fileName = j.replace(/\\/g, "/").split("/").pop();
        item.innerHTML = `📄 <strong>Usar JSON:</strong> ${escapeHtml(fileName)} <span style="font-size:10px; opacity:0.8; margin-left:auto;">(Clique para selecionar)</span>`;
        item.addEventListener("click", () => {
          el("inpJsonPath").value = j;
          showToast(state.language === "en" ? `Selected: ${fileName}` : `Selecionado: ${fileName}`);
        });
        container.appendChild(item);
      });

      // Auto pre-fill if both fields are currently empty
      if (!el("inpModpackPath").value.trim() && modpacks.length > 0) {
        el("inpModpackPath").value = modpacks[0];
      }
      if (!el("inpJsonPath").value.trim() && jsons.length > 0) {
        el("inpJsonPath").value = jsons[0];
      }
    } catch (err) {
      container.innerHTML = `<div style="font-size:11.5px; color:var(--accent-rose);">${escapeHtml(err.message)}</div>`;
    }
  }

  // Setup Event Listeners
  function setupEvents() {
    // Backdrop click-to-close for all modals
    document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
      backdrop.addEventListener("click", (e) => {
        if (e.target === backdrop) {
          closeModal(backdrop.id);
        }
      });
    });

    el("btnLangToggle").addEventListener("click", () => {
      setLanguage(state.language === "pt" ? "en" : "pt");
    });

    el("btnOpenAddForm").addEventListener("click", openAddFormModal);
    el("btnCancelAddForm").addEventListener("click", () => closeModal("addFormModal"));
    el("btnConfirmAddForm").addEventListener("click", handleConfirmAddForm);

    el("btnDeleteForm").addEventListener("click", openDeleteFormModal);
    el("btnCancelDelete").addEventListener("click", () => closeModal("deleteFormModal"));
    el("btnConfirmDelete").addEventListener("click", handleConfirmDeleteForm);

    el("btnOpenAddons").addEventListener("click", openAddonsModal);
    el("btnCloseAddons").addEventListener("click", () => closeModal("addonsModal"));

    el("btnApplyForm").addEventListener("click", handleApplyForm);

    el("btnUndo").addEventListener("click", () => {
      apiPost("/api/undo").then((data) => {
        applyServerState(data);
        showToast(state.language === "en" ? "Action undone (Ctrl+Z)" : "Ação desfeita (Ctrl+Z)");
      }).catch((err) => showToast(err.message, true));
    });
    el("btnRedo").addEventListener("click", () => {
      apiPost("/api/redo").then((data) => {
        applyServerState(data);
        showToast(state.language === "en" ? "Action redone (Ctrl+Y)" : "Ação refeita (Ctrl+Y)");
      }).catch((err) => showToast(err.message, true));
    });

    el("btnSaveJson").addEventListener("click", () => {
      apiPost("/api/save-json").then((data) => {
        applyServerState(data);
        const savedList = (data.json_salvos || []).map((p) => p.replace(/\\/g, "/").split("/").pop());
        const info = savedList.length > 0 ? ` (${savedList.join(", ")})` : "";
        showToast(
          state.language === "en"
            ? `Saved to JSON!${info}`
            : `JSON salvo com sucesso!${info}`
        );
      }).catch((err) => showToast(err.message, true));
    });

    el("btnApplyModpack").addEventListener("click", () => {
      apiPost("/api/apply-modpack").then((data) => {
        applyServerState(data);
        showToast(state.language === "en" ? "Saved and applied to Modpack configs with backup!" : "Salvo e aplicado direto nas configs do Modpack com backup!");
      }).catch((err) => showToast(err.message, true));
    });

    el("btnReloadModpack").addEventListener("click", () => {
      apiPost("/api/reload", { source: state.source }).then((data) => {
        applyServerState(data);
        showToast(
          state.language === "en"
            ? "Modpack reloaded successfully!"
            : "Modpack recarregado com sucesso!"
        );
      }).catch((err) => showToast(err.message, true));
    });

    // Settings Modal
    el("btnOpenSettings").addEventListener("click", async () => {
      el("inpModpackPath").value = state.dmzConfigDir || "";
      el("inpJsonPath").value = state.desktopJson || "";
      openModal("settingsModal");
      await loadDetectedLocations();
    });
    el("btnCloseSettings").addEventListener("click", () => closeModal("settingsModal"));

    el("inpModpackPath").addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/^["']+|["']+$/g, "").trim();
    });
    el("inpJsonPath").addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/^["']+|["']+$/g, "").trim();
    });

    el("btnBrowseFolder").addEventListener("click", async () => {
      try {
        const res = await apiPost("/api/browse-folder");
        const chosen = res.path || res.selected_path || "";
        if (chosen) {
          el("inpModpackPath").value = chosen;
          showToast(state.language === "en" ? `Folder selected: ${chosen}` : `Pasta selecionada: ${chosen}`);
        }
      } catch (err) { showToast(err.message, true); }
    });
    el("btnBrowseJson").addEventListener("click", async () => {
      try {
        const res = await apiPost("/api/browse-json");
        const chosen = res.path || res.selected_path || "";
        if (chosen) {
          el("inpJsonPath").value = chosen;
          showToast(state.language === "en" ? `JSON selected: ${chosen}` : `JSON selecionado: ${chosen}`);
        }
      } catch (err) { showToast(err.message, true); }
    });
    el("btnResetDefaultPath").addEventListener("click", () => {
      el("inpModpackPath").value = "";
      el("inpJsonPath").value = "";
    });
    el("btnSaveSettings").addEventListener("click", async () => {
      const dmzVal = el("inpModpackPath").value.replace(/^["']+|["']+$/g, "").trim();
      const jsonVal = el("inpJsonPath").value.replace(/^["']+|["']+$/g, "").trim();
      try {
        const data = await apiPost("/api/settings", {
          dmz_config_dir: dmzVal,
          desktop_json_path: jsonVal,
          clear_paths: !dmzVal && !jsonVal,
        });
        closeModal("settingsModal");
        applyServerState(data);
        showToast(state.language === "en" ? "Settings saved and modpack loaded!" : "Configurações salvas e Modpack carregado com sucesso!");
      } catch (err) {
        showToast(err.message, true);
      }
    });

    // Batch Modal
    el("btnOpenBatch").addEventListener("click", () => openModal("batchModal"));
    el("btnCloseBatch").addEventListener("click", () => closeModal("batchModal"));
    el("btnConfirmBatch").addEventListener("click", async () => {
      const scopeVal = el("batchScopeSelect").value;
      const target_scope = { tipo: scopeVal };
      if (scopeVal === "current") {
        if (state.navScope.startsWith("race:")) {
          target_scope.tipo = state.selectedTree === "all" ? "raca" : "arvore";
          target_scope.raca = state.navScope.slice(5);
          target_scope.arvore = state.selectedTree;
        } else if (state.navScope === "universal") {
          target_scope.tipo = "universal";
          target_scope.grupo = state.selectedTree;
        } else {
          target_scope.tipo = "tudo";
        }
      }
      try {
        const data = await apiPost("/api/batch-scale", {
          campo: el("batchFieldSelect").value,
          fator: parseFloat(el("batchFactorInput").value),
          escopo: target_scope,
        });
        closeModal("batchModal");
        applyServerState(data);
        showToast(state.language === "en" ? "Batch scale applied!" : "Escala em lote aplicada!");
      } catch (err) {
        showToast(err.message, true);
      }
    });

    document.querySelectorAll("[data-batch-factor]").forEach((btn) => {
      btn.addEventListener("click", () => {
        el("batchFactorInput").value = btn.getAttribute("data-batch-factor");
      });
    });

    // Color pickers & Live Aura Visualizer
    el("vis_aura").addEventListener("input", updateAuraLivePreview);
    el("vis_hair").addEventListener("input", updateAuraLivePreview);
    el("vis_aura_picker").addEventListener("input", (e) => {
      el("vis_aura").value = e.target.value.toUpperCase();
      updateAuraLivePreview();
    });
    el("vis_hair_picker").addEventListener("input", (e) => {
      el("vis_hair").value = e.target.value.toUpperCase();
      updateAuraLivePreview();
    });

    // Preset color chips
    document.querySelectorAll(".btn-preset-color").forEach((btn) => {
      btn.addEventListener("click", () => {
        const aura = btn.getAttribute("data-aura");
        const hair = btn.getAttribute("data-hair");
        if (aura) {
          el("vis_aura").value = aura;
          el("vis_aura_picker").value = aura;
        }
        if (hair) {
          el("vis_hair").value = hair;
          el("vis_hair_picker").value = hair;
        }
        updateAuraLivePreview();
      });
    });

    // Sagas selection sync
    const reqSagaSelect = el("req_saga_select");
    const reqSagaInp = el("req_saga");
    if (reqSagaSelect && reqSagaInp) {
      reqSagaSelect.addEventListener("change", (e) => {
        reqSagaInp.value = e.target.value;
      });
      reqSagaInp.addEventListener("input", (e) => {
        populateSagasSelect(e.target.value);
      });
    }

    // Prior form selection sync
    const reqPrevSelect = el("req_prev_form_select");
    const reqPrevInp = el("req_prev_form");
    if (reqPrevSelect && reqPrevInp) {
      reqPrevSelect.addEventListener("change", (e) => {
        reqPrevInp.value = e.target.value;
      });
      reqPrevInp.addEventListener("input", (e) => {
        populatePrevFormSelect(e.target.value);
      });
    }

    // Incompatible forms selector, tags & shortcuts
    const reqIncompatSelect = el("req_incompatible_select");
    if (reqIncompatSelect) {
      reqIncompatSelect.addEventListener("change", (e) => {
        if (e.target.value) {
          addIncompatibleForm(e.target.value);
        }
      });
    }

    const reqIncompatInp = el("req_incompatible");
    if (reqIncompatInp) {
      reqIncompatInp.addEventListener("input", (e) => {
        const list = e.target.value.split(",").map((s) => s.trim()).filter(Boolean);
        renderIncompatibleTags(list);
      });
    }

    document.querySelectorAll(".btn-incompat-quick").forEach((btn) => {
      btn.addEventListener("click", () => {
        const formId = btn.getAttribute("data-form");
        if (formId) addIncompatibleForm(formId);
      });
    });

    // Close button for Add Form Modal
    const btnCloseAddFormX = el("btnCloseAddFormX");
    if (btnCloseAddFormX) {
      btnCloseAddFormX.addEventListener("click", () => closeModal("addFormModal"));
    }

    // Live Visualizer inside Add Form Modal
    const addAuraInp = el("add_cor_aura");
    const addHairInp = el("add_cor_cabelo");
    const addAuraPicker = el("add_cor_aura_picker");
    const addHairPicker = el("add_cor_cabelo_picker");

    if (addAuraInp) addAuraInp.addEventListener("input", updateAddFormAuraPreview);
    if (addHairInp) addHairInp.addEventListener("input", updateAddFormAuraPreview);

    if (addAuraPicker && addAuraInp) {
      addAuraPicker.addEventListener("input", (e) => {
        addAuraInp.value = e.target.value.toUpperCase();
        updateAddFormAuraPreview();
      });
    }
    if (addHairPicker && addHairInp) {
      addHairPicker.addEventListener("input", (e) => {
        addHairInp.value = e.target.value.toUpperCase();
        updateAddFormAuraPreview();
      });
    }

    document.querySelectorAll(".btn-add-preset-color").forEach((btn) => {
      btn.addEventListener("click", () => {
        const aura = btn.getAttribute("data-aura");
        const hair = btn.getAttribute("data-hair");
        if (aura && addAuraInp) addAuraInp.value = aura;
        if (hair && addHairInp) addHairInp.value = hair;
        updateAddFormAuraPreview();
      });
    });

    // Add Form TP presets and live preview
    const addTpInp = el("add_tp");
    if (addTpInp) {
      addTpInp.addEventListener("input", updateAddFormTpPreview);
    }
    document.querySelectorAll(".btn-preset-add-tp").forEach((btn) => {
      btn.addEventListener("click", () => {
        const val = btn.getAttribute("data-tp");
        if (addTpInp && val !== null) {
          addTpInp.value = val;
          updateAddFormTpPreview();
        }
      });
    });

    // Add Form BP multipliers & preview
    ["add_mult_str", "add_mult_pwr", "add_mult_def", "add_mult_skp"].forEach((id) => {
      const input = el(id);
      if (input) input.addEventListener("input", updateAddFormBpPreview);
    });

    document.querySelectorAll(".btn-preset-add-bp").forEach((btn) => {
      btn.addEventListener("click", () => {
        const factor = parseFloat(btn.getAttribute("data-bpmult"));
        if (!factor) return;
        ["add_mult_str", "add_mult_pwr", "add_mult_def", "add_mult_skp"].forEach((id) => {
          const inp = el(id);
          if (inp) {
            const v = parseFloat(inp.value) || 1.0;
            inp.value = (Math.round(v * factor * 100) / 100).toFixed(2);
          }
        });
        updateAddFormBpPreview();
      });
    });

    // Master purchase & selection sync
    const chkBuyMaster = el("chkBuyMaster");
    const inpMasterSelect = el("inpMasterSelect");
    const inpMasterBadge = el("inpMasterBadge");
    if (chkBuyMaster && inpMasterSelect) {
      chkBuyMaster.addEventListener("change", (e) => {
        inpMasterSelect.disabled = !e.target.checked;
        if (inpMasterBadge) {
          if (!e.target.checked) {
            inpMasterBadge.textContent = "—";
          } else if (inpMasterSelect.selectedOptions[0]) {
            inpMasterBadge.textContent = inpMasterSelect.value
              ? `🥋 ${inpMasterSelect.selectedOptions[0].textContent.split("(")[0].trim()}`
              : "—";
          }
        }
      });
      inpMasterSelect.addEventListener("change", (e) => {
        if (inpMasterBadge) {
          inpMasterBadge.textContent = e.target.value && e.target.selectedOptions[0]
            ? `🥋 ${e.target.selectedOptions[0].textContent.split("(")[0].trim()}`
            : "—";
        }
      });
    }

    // Addons Modal toolbar controls & filter tabs
    const btnOpenModsFolder = el("btnOpenModsFolder");
    if (btnOpenModsFolder) {
      btnOpenModsFolder.addEventListener("click", async () => {
        try {
          const res = await apiPost("/api/addons/open-folder");
          showToast(res.message || (state.language === "en" ? "Mods folder opened!" : "Pasta de mods aberta!"));
        } catch (err) {
          showToast(err.message, true);
        }
      });
    }

    const btnReloadAddons = el("btnReloadAddons");
    if (btnReloadAddons) {
      btnReloadAddons.addEventListener("click", () => openAddonsModal(true));
    }

    const addonSearchInput = el("addonSearchInput");
    if (addonSearchInput) {
      addonSearchInput.addEventListener("input", (e) => {
        state.addonFilterText = e.target.value;
        renderAddonsCards();
      });
    }

    document.querySelectorAll(".filter-tab-btn").forEach((tabBtn) => {
      tabBtn.addEventListener("click", () => {
        document.querySelectorAll(".filter-tab-btn").forEach((b) => b.classList.remove("active"));
        tabBtn.classList.add("active");
        state.addonActiveTab = tabBtn.getAttribute("data-tab") || "all";
        renderAddonsCards();
      });
    });

    // Search and filter inputs
    el("raceSearchInput").addEventListener("input", (e) => {
      state.raceFilterText = e.target.value;
      renderSidebar();
    });
    el("mainSearchInput").addEventListener("input", (e) => {
      state.searchText = e.target.value;
      rebuildAndRenderTable();
    });
    el("addonFilterSelect").addEventListener("change", (e) => {
      state.addonFilter = e.target.value;
      rebuildAndRenderTable();
    });
    el("quickFilterSelect").addEventListener("change", (e) => {
      state.quickFilter = e.target.value;
      rebuildAndRenderTable();
    });
    el("sortSelect").addEventListener("change", (e) => {
      state.sortBy = e.target.value;
      rebuildAndRenderTable();
    });

    // TP and BP live input listeners
    el("inpTp").addEventListener("input", updateInspectorPreviews);
    el("mult_str").addEventListener("input", updateInspectorPreviews);
    el("mult_pwr").addEventListener("input", updateInspectorPreviews);

    document.querySelectorAll("[data-tp-preset]").forEach((btn) => {
      btn.addEventListener("click", () => {
        el("inpTp").value = btn.getAttribute("data-tp-preset");
        updateInspectorPreviews();
      });
    });

    document.querySelectorAll("[data-tp-mult]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mult = parseFloat(btn.getAttribute("data-tp-mult"));
        const cur = parseInt(el("inpTp").value, 10);
        if (cur > 0) {
          el("inpTp").value = Math.max(1, Math.round(cur * mult));
          updateInspectorPreviews();
        }
      });
    });

    document.querySelectorAll("[data-bp-mult]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const factor = parseFloat(btn.getAttribute("data-bp-mult"));
        ["mult_str", "mult_pwr", "mult_def", "mult_skp"].forEach((id) => {
          const inp = el(id);
          const v = parseFloat(inp.value) || 1.0;
          inp.value = (Math.round(v * factor * 1000) / 1000).toFixed(2);
        });
        updateInspectorPreviews();
      });
    });
  }

  // Initialization
  async function init() {
    setupEvents();
    setLanguage(state.language);
    try {
      const data = await apiGet("/api/state");
      applyServerState(data);
    } catch (err) {
      showToast(err.message, true);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
