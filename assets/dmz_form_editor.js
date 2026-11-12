(() => {
  "use strict";

  const csrfToken = document.body.dataset.csrfToken || "";

  // =========================================================================
  // DICIONÁRIO BILINGUE (PT-BR / EN-US)
  // =========================================================================
  const I18N = {
    pt: {
      app_title: "KiForge: DMZ Form Studio",
      modpack_connected: "Modpack Conectado",
      unsaved_changes: "Alterações não salvas",
      btn_config_folder: "⚙️ Pasta Config",
      btn_undo: "↶ Desfazer",
      btn_redo: "↷ Refazer",
      btn_batch: "⚡ Escala em Lote",
      btn_reload: "↻ Ler Modpack",
      btn_apply: "💾 SALVAR NO MODPACK",
      btn_health_check: "🛡️ Health Check",
      btn_diff: "🔍 Revisar Diff",
      btn_backups: "📂 Abrir Backups",
      btn_addons: "🧩 Addons & Mods",
      lbl_select_race: "Raça Selecionada:",
      filter_tree_search: "🔍 Filtrar transformações...",
      opt_all_addons: "Todos Mods",
      race_tree_title: "ÁRVORE DA RAÇA",
      btn_wizard_add: "✨ + Nova Forma (Wizard)",
      btn_reorder_order: "⇅ Reorganizar Ordem",
      btn_import_mold: "📥 Importar Molde (JSON)",
      btn_export_mold: "📤 Exportar Molde (JSON)",
      staging_drawer_title: "GAVETA DE IMPORTADOS",
      staging_empty: "Nenhum item na gaveta. Importe moldes JSON externos para armazená-los aqui antes de alocar.",
      viewport_hint: "Gire com botão esquerdo · Zoom com scroll · Mova com botão direito",
      lbl_status_multipliers: "STATUS MULTIPLICADORES (BP)",
      sim_autonomy_idle: "Autonomia Estimada: ~∞ (Dreno Inativo)",
      btn_clone_stage: "+ Clonar Estágio",
      btn_delete_stage: "🗑️ Excluir",
      btn_reorder_stages: "⇅ Ordem",
      btn_auto_scale: "⚡ Auto-Balancear",
      tab_multipliers: "📊 Multiplicadores & Dreno",
      tab_visual: "🎨 Visual & FX Studio",
      tab_sagas: "📜 Sagas & Requisitos",
      sec_economy: "1. Economia de TP & Desbloqueio",
      lbl_tp_cost: "Custo de TP (-1 = Priceless, 0 = Inato)",
      lbl_skill_slot: "Nível na Habilidade (Slot)",
      sec_multipliers: "2. Multiplicadores de Status (BP)",
      lbl_str: "Força (STR)",
      lbl_def: "Defesa (DEF)",
      lbl_spd: "Velocidade (SPD)",
      lbl_pwr: "Poder Ki (PWR)",
      lbl_skp: "Golpe Especial (SKP)",
      lbl_ene: "Energia Máx (ENE)",
      lbl_scale_all: "Escalar Todos:",
      sec_drains: "3. Drenos por Segundo & Combate",
      lbl_drain_ki: "Dreno Ki (/s)",
      lbl_drain_stm: "Dreno Stamina (/s)",
      lbl_drain_hp: "Dreno Vida (/s)",
      lbl_mastery_rate: "Taxa Ganho de Maestria (/min)",
      lbl_mastery_reduction: "Redução Dreno na Maestria (%)",
      sec_hair_model: "1. Modelo de Cabelo & Corpo",
      lbl_hair_model: "Estilo do Cabelo",
      lbl_hair_scale: "Escala do Cabelo",
      lbl_hair_color: "Cor do Cabelo (Hex)",
      lbl_eye_color: "Cor dos Olhos (Hex)",
      quick_palettes: "Paleta Rápida de Formas:",
      sec_ki_cloak: "2. Manto de Ki (Estilo Kurama / Cloak)",
      lbl_cloak_style: "Estilo do Manto",
      lbl_cloak_opacity: "Opacidade:",
      lbl_cloak_inner: "Cor Interna (Hex)",
      lbl_cloak_border: "Cor da Borda (Hex)",
      sec_sparks_aura: "3. Raios Elétricos (Sparks) & Aura Externa",
      lbl_enable_sparks: "Raios Elétricos (Sparks)",
      lbl_sparks_intensity: "Intensidade dos Raios",
      lbl_aura_type: "Tipo de Aura Externa",
      lbl_aura_color: "Cor da Aura (Hex)",
      sec_sagas: "1. Vínculo com Sagas do DMZ",
      lbl_saga_req: "Saga Obrigatória para Desbloqueio",
      lbl_prev_form: "Forma Pré-requisito (ID Obrigatório Anterior)",
      sec_flags: "2. Flags Especiais & Restrições",
      chk_is_divine: "Forma de Ki Divino (Requer treinamento com Whis / Beerus)",
      chk_prevent_kaioken: "Não acumula com Kaioken (Impossível Stack)",
      chk_requires_mastery: "Exige 100% de Maestria na forma anterior",
      chk_bypass_god: "Permite ativar sem nível de Ki Divino desbloqueado",
      wizard_title: "✨ Assistente de Criação: Nova Forma DMZ",
      wizard_sub: "Crie transformações completas com grupos, sub-formas, multiplicadores e efeitos visuais sem corromper o modpack.",
      lbl_wiz_race: "Raça de Destino",
      lbl_wiz_group: "Nome do Grupo / Arquivo .json",
      lbl_wiz_stage_name: "Nome do 1º Estágio",
      lbl_wiz_stage_id: "ID Interno do Estágio",
      lbl_wiz_preset: "Preset de Poder Inicial",
      lbl_wiz_hair_color: "Cor do Cabelo",
      lbl_wiz_aura_color: "Cor da Aura",
      btn_wiz_create: "✨ Criar Forma e Abrir no Editor",
      reorder_title: "⇅ Reorganizar Ordem das Transformações",
      chk_sequential_levels: "Atualizar unlockOnSkillLevel sequencialmente (1, 2, 3...)",
      hint_sequential_levels: "Desmarque caso queira manter saltos manuais de nível (ex: nível 1, 5, 10).",
      btn_save_order: "✓ Salvar Nova Ordem",
      diff_title: "🔍 Revisar Alterações (Diff Antes de Salvar)",
      diff_sub: "Comparação detalhada entre o modpack original e as edições realizadas na sessão atual.",
      diff_clean: "Nenhuma alteração detectada. Seu estado de trabalho está sincronizado com o modpack.",
      export_title: "📤 Exportar Molde de Transformações",
      lbl_export_scope: "Escopo da Exportação",
      btn_do_export: "Exportar JSON",
      import_title: "📥 Importar Molde de Transformações",
      lbl_select_mold_file: "Selecione o arquivo .json do Molde",
      chk_import_staging: "Enviar para a Gaveta de Importados (Seguro - Fora da Árvore)",
      btn_do_import: "Importar Molde",
      allocate_title: "📦 Alocar Forma na Árvore da Raça",
      lbl_alloc_race: "Raça de Destino",
      lbl_alloc_conflict: "Modo de Resolução de Conflito",
      btn_do_allocate: "Alocar na Árvore",
      health_title: "Relatório de Integridade das Transformações & Sagas",
      autoscale_title: "⚡ Auto-Balancear Escala dos Estágios",
      lbl_scale_bp_percent: "Acréscimo de BP (%) por estágio",
      lbl_scale_drain_percent: "Acréscimo de Dreno (%) por estágio",
      settings_title: "⚙️ Selecionar Pasta do Modpack ou Arquivo JSON",
      settings_desc: "Selecione onde está a pasta config/dragonminez do seu Modpack e/ou o arquivo .json de transformações.",
      lbl_modpack_path: "Pasta do Modpack / Config DragonMineZ",
      btn_browse_folder: "📂 Procurar Pasta...",
      lbl_json_path: "Arquivo .JSON de Molde (Opcional)",
      btn_browse_json: "📄 Procurar JSON...",
      btn_save_settings: "Salvar e Carregar",
      modal_addons_title: "🧩 Gerenciador de Addons & Mods do DMZ",
      btn_open_mods: "📁 Pasta Mods",
      btn_reload_mods: "🔄 Recarregar",
      batch_studio_title: "⚡ Balanceamento em Lote Avançado",
      lbl_batch_race: "Raça / Escopo",
      btn_apply_batch: "⚡ Aplicar em Lote",
      btn_cancel: "Cancelar",
      btn_close: "Fechar"
    },
    en: {
      app_title: "KiForge: DMZ Form Studio",
      modpack_connected: "Modpack Connected",
      unsaved_changes: "Unsaved Changes",
      btn_config_folder: "⚙️ Config Folder",
      btn_undo: "↶ Undo",
      btn_redo: "↷ Redo",
      btn_batch: "⚡ Batch Scale",
      btn_reload: "↻ Reload Modpack",
      btn_apply: "💾 SAVE TO MODPACK",
      btn_health_check: "🛡️ Health Check",
      btn_diff: "🔍 Review Diff",
      btn_backups: "📂 Open Backups",
      btn_addons: "🧩 Addons & Mods",
      lbl_select_race: "Selected Race:",
      filter_tree_search: "🔍 Filter transformations...",
      opt_all_addons: "All Mods",
      race_tree_title: "RACE TREE",
      btn_wizard_add: "✨ + New Form (Wizard)",
      btn_reorder_order: "⇅ Reorder Tree",
      btn_import_mold: "📥 Import Mold (JSON)",
      btn_export_mold: "📤 Export Mold (JSON)",
      staging_drawer_title: "STAGING DOCK (UNALLOCATED)",
      staging_empty: "No items in staging dock. Import external JSON molds to store them here before allocating to a race tree.",
      viewport_hint: "Rotate with Left Click · Zoom with Scroll · Pan with Right Click",
      lbl_status_multipliers: "STATUS MULTIPLIERS (BP)",
      sim_autonomy_idle: "Estimated Autonomy: ~∞ (Drain Inactive)",
      btn_clone_stage: "+ Clone Stage",
      btn_delete_stage: "🗑️ Delete",
      btn_reorder_stages: "⇅ Order",
      btn_auto_scale: "⚡ Auto-Balance",
      tab_multipliers: "📊 Multipliers & Drain",
      tab_visual: "🎨 Visual & FX Studio",
      tab_sagas: "📜 Sagas & Requirements",
      sec_economy: "1. TP Economy & Unlock",
      lbl_tp_cost: "TP Cost (-1 = Priceless, 0 = Innate)",
      lbl_skill_slot: "Skill Level (Slot)",
      sec_multipliers: "2. Status Multipliers (BP)",
      lbl_str: "Strength (STR)",
      lbl_def: "Defense (DEF)",
      lbl_spd: "Speed (SPD)",
      lbl_pwr: "Ki Power (PWR)",
      lbl_skp: "Skill Power (SKP)",
      lbl_ene: "Max Energy (ENE)",
      lbl_scale_all: "Scale All:",
      sec_drains: "3. Drains per Second & Combat",
      lbl_drain_ki: "Ki Drain (/s)",
      lbl_drain_stm: "Stamina Drain (/s)",
      lbl_drain_hp: "Health Drain (/s)",
      lbl_mastery_rate: "Mastery Gain Rate (/min)",
      lbl_mastery_reduction: "Drain Reduction at Max (%)",
      sec_hair_model: "1. Hair Model & Body",
      lbl_hair_model: "Hair Style",
      lbl_hair_scale: "Hair Scale",
      lbl_hair_color: "Hair Color (Hex)",
      lbl_eye_color: "Eye Color (Hex)",
      quick_palettes: "Quick Form Palettes:",
      sec_ki_cloak: "2. Ki Cloak (Kurama Style / Cloak)",
      lbl_cloak_style: "Cloak Style",
      lbl_cloak_opacity: "Opacity:",
      lbl_cloak_inner: "Inner Color (Hex)",
      lbl_cloak_border: "Border Color (Hex)",
      sec_sparks_aura: "3. Electric Sparks & External Aura",
      lbl_enable_sparks: "Electric Sparks",
      lbl_sparks_intensity: "Sparks Intensity",
      lbl_aura_type: "External Aura Type",
      lbl_aura_color: "Aura Color (Hex)",
      sec_sagas: "1. DMZ Sagas Requirement",
      lbl_saga_req: "Required Saga for Unlock",
      lbl_prev_form: "Prerequisite Form (Required Previous ID)",
      sec_flags: "2. Special Flags & Restrictions",
      chk_is_divine: "Divine Ki Form (Requires training with Whis / Beerus)",
      chk_prevent_kaioken: "Cannot stack with Kaioken (No Stack)",
      chk_requires_mastery: "Requires 100% Mastery in previous form",
      chk_bypass_god: "Allows activation without God Ki unlocked",
      wizard_title: "✨ Creation Wizard: New DMZ Form",
      wizard_sub: "Create complete transformations with groups, sub-forms, multipliers and visual effects without corrupting the modpack.",
      lbl_wiz_race: "Target Race",
      lbl_wiz_group: "Group Name / .json File",
      lbl_wiz_stage_name: "1st Stage Name",
      lbl_wiz_stage_id: "Stage Internal ID",
      lbl_wiz_preset: "Initial Power Preset",
      lbl_wiz_hair_color: "Hair Color",
      lbl_wiz_aura_color: "Aura Color",
      btn_wiz_create: "✨ Create Form and Open in Editor",
      reorder_title: "⇅ Reorder Transformation Hierarchy",
      chk_sequential_levels: "Update unlockOnSkillLevel sequentially (1, 2, 3...)",
      hint_sequential_levels: "Uncheck if you want to keep manual level jumps (e.g. level 1, 5, 10).",
      btn_save_order: "✓ Save New Order",
      diff_title: "🔍 Review Changes (Diff Before Save)",
      diff_sub: "Detailed comparison between original modpack and edits made in the current session.",
      diff_clean: "No changes detected. Your working state is in sync with the modpack.",
      export_title: "📤 Export Transformation Mold",
      lbl_export_scope: "Export Scope",
      btn_do_export: "Export JSON",
      import_title: "📥 Import Transformation Mold",
      lbl_select_mold_file: "Select Mold .json File",
      chk_import_staging: "Send to Staging Dock (Safe - Outside Tree)",
      btn_do_import: "Import Mold",
      allocate_title: "📦 Allocate Form into Race Tree",
      lbl_alloc_race: "Target Race",
      lbl_alloc_conflict: "Conflict Resolution Mode",
      btn_do_allocate: "Allocate to Tree",
      health_title: "Transformations & Sagas Integrity Report",
      autoscale_title: "⚡ Auto-Balance Stage Scale",
      lbl_scale_bp_percent: "BP Increase (%) per stage",
      lbl_scale_drain_percent: "Drain Increase (%) per stage",
      settings_title: "⚙️ Select Modpack Folder or JSON File",
      settings_desc: "Select where config/dragonminez is located in your Modpack and/or your mold .json file.",
      lbl_modpack_path: "Modpack Folder / Config DragonMineZ",
      btn_browse_folder: "📂 Browse Folder...",
      lbl_json_path: "Mold .JSON File (Optional)",
      btn_browse_json: "📄 Browse JSON...",
      btn_save_settings: "Save and Load",
      modal_addons_title: "🧩 DMZ Addons & Mods Manager",
      btn_open_mods: "📁 Mods Folder",
      btn_reload_mods: "🔄 Reload",
      batch_studio_title: "⚡ Advanced Batch Balancing",
      lbl_batch_race: "Race / Scope",
      btn_apply_batch: "⚡ Apply in Batch",
      btn_cancel: "Cancel",
      btn_close: "Close"
    }
  };

  let currentLang = "pt";

  function setLanguage(lang) {
    currentLang = lang;
    const dict = I18N[lang] || I18N.pt;
    document.querySelectorAll("[data-i18n]").forEach((elem) => {
      const key = elem.getAttribute("data-i18n");
      if (dict[key]) elem.textContent = dict[key];
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((elem) => {
      const key = elem.getAttribute("data-i18n-placeholder");
      if (dict[key]) elem.placeholder = dict[key];
    });
    const btn = document.getElementById("btnLangToggle");
    if (btn) btn.textContent = lang === "pt" ? "🌐 EN" : "🌐 PT";
  }

  // Disables race selector when scope is universal
  function updateRaceSelectorState(scope) {
    const rSelect = document.getElementById("raceSelect");
    if (rSelect) {
      if (scope === "universal") {
        rSelect.disabled = true;
      } else {
        rSelect.disabled = false;
      }
    }
  }

  // =========================================================================
  // API HELPER & TOASTS
  // =========================================================================
  async function fetchJson(url, options = {}) {
    options.headers = options.headers || {};
    if (csrfToken) options.headers["X-CSRF-Token"] = csrfToken;
    const res = await fetch(url, options);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    return res.json();
  }

  function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(8px)";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // =========================================================================
  // ESTADO GLOBAL DO STUDIO
  // =========================================================================
  const state = {
    catalog: null,
    selectedRace: "saiyan",
    selectedGroupKey: null,
    selectedStageId: null,
    staging: [],
    isDirty: false,
    expandedGroups: new Set(),
    simulation: {
      running: false,
      intervalId: null,
      maxHp: 100,
      currentHp: 100,
      maxKi: 10000,
      currentKi: 10000,
      maxStm: 5000,
      currentStm: 5000,
      kiDrain: 0,
      stmDrain: 0,
      hpDrain: 0
    }
  };

  // =========================================================================
  // THREE.JS 3D PEDESTAL VIEWPORT
  // =========================================================================
  let scene, camera, renderer, controls;
  let characterRig = {}, hairMeshGroup, cloakMeshGroup, sparksGroup, auraMesh;

  function initThreeViewport() {
    const container = document.getElementById("threeCanvasContainer");
    if (!container || !window.THREE) return;

    const width = container.clientWidth || 360;
    const height = container.clientHeight || 280;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.set(0, 1.6, 4.2);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    container.innerHTML = "";
    container.appendChild(renderer.domElement);

    if (window.THREE.OrbitControls) {
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.target.set(0, 1.1, 0);
      controls.minDistance = 2.0;
      controls.maxDistance = 7.0;
      controls.maxPolarAngle = Math.PI / 2 + 0.1;
    }

    // Iluminação
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xfffaed, 1.2);
    keyLight.position.set(2, 4, 3);
    scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(0x06b6d4, 0.7);
    rimLight.position.set(-2, 2, -2);
    scene.add(rimLight);

    // Grid no Chão (Pedestal)
    const grid = new THREE.GridHelper(4, 16, 0x06b6d4, 0x1e293b);
    grid.position.y = 0;
    scene.add(grid);

    buildMinecraftCharacterRig();
    buildAuraAndEffects();

    // Loop de Animação
    function animate() {
      requestAnimationFrame(animate);
      if (controls) controls.update();

      // Animação sutil de respiração do rig
      const time = performance.now() * 0.002;
      if (characterRig.torso) {
        characterRig.torso.position.y = 0.95 + Math.sin(time * 2) * 0.015;
      }

      // Animação de pulso do Manto de Ki
      if (cloakMeshGroup && cloakMeshGroup.visible) {
        const pulse = 1.0 + Math.sin(time * 6) * 0.03;
        cloakMeshGroup.scale.set(pulse, pulse, pulse);
      }

      // Animação dos Raios Elétricos (Sparks)
      if (sparksGroup && sparksGroup.visible) {
        if (Math.random() < 0.35) {
          updateSparksGeometry();
        }
      }

      // Rotação da Aura
      if (auraMesh && auraMesh.visible) {
        auraMesh.rotation.y += 0.02;
      }

      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener("resize", () => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });
  }

  // Constrói o Rig Humanóide estilo Minecraft Steve
  function buildMinecraftCharacterRig() {
    const skinMaterial = new THREE.MeshStandardMaterial({ color: 0xd4a373, roughness: 0.7 });
    const clothesMaterial = new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.6 }); // Gi Laranja
    const pantsMaterial = new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.6 }); // Calça Azul

    // Tronco (Torso)
    const torsoGeo = new THREE.BoxGeometry(0.5, 0.75, 0.25);
    const torso = new THREE.Mesh(torsoGeo, clothesMaterial);
    torso.position.set(0, 0.95, 0);
    scene.add(torso);
    characterRig.torso = torso;

    // Cabeça (Head)
    const headGeo = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const head = new THREE.Mesh(headGeo, skinMaterial);
    head.position.set(0, 0.625, 0);
    torso.add(head);
    characterRig.head = head;

    // Braços (Arms)
    const armGeo = new THREE.BoxGeometry(0.25, 0.75, 0.25);
    const leftArm = new THREE.Mesh(armGeo, skinMaterial);
    leftArm.position.set(0.375, 0, 0);
    torso.add(leftArm);
    characterRig.leftArm = leftArm;

    const rightArm = new THREE.Mesh(armGeo, skinMaterial);
    rightArm.position.set(-0.375, 0, 0);
    torso.add(rightArm);
    characterRig.rightArm = rightArm;

    // Pernas (Legs)
    const legGeo = new THREE.BoxGeometry(0.25, 0.75, 0.25);
    const leftLeg = new THREE.Mesh(legGeo, pantsMaterial);
    leftLeg.position.set(0.125, 0.375, 0);
    scene.add(leftLeg);
    characterRig.leftLeg = leftLeg;

    const rightLeg = new THREE.Mesh(legGeo, pantsMaterial);
    rightLeg.position.set(-0.125, 0.375, 0);
    scene.add(rightLeg);
    characterRig.rightLeg = rightLeg;

    // Grupo de Cabelo (preso à cabeça)
    hairMeshGroup = new THREE.Group();
    head.add(hairMeshGroup);

    // Grupo do Manto de Ki (Kurama Cloak)
    cloakMeshGroup = new THREE.Group();
    cloakMeshGroup.visible = false;
    torso.add(cloakMeshGroup);

    buildCloakShell();
    updateHairModel("ssj2", "#FFE690", 1.05);
  }

  // Gera o Manto de Ki Translúcido colado ao corpo
  function buildCloakShell() {
    const cloakMat = new THREE.MeshStandardMaterial({
      color: 0xff3300,
      emissive: 0xff6600,
      emissiveIntensity: 0.8,
      transparent: true,
      opacity: 0.75,
      roughness: 0.3
    });

    const bodyShell = new THREE.Mesh(new THREE.BoxGeometry(0.58, 0.82, 0.32), cloakMat);
    cloakMeshGroup.add(bodyShell);

    const headShell = new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.56, 0.56), cloakMat);
    headShell.position.set(0, 0.625, 0);
    cloakMeshGroup.add(headShell);
  }

  // Gera Geometrias Procedurais de Cabelo Dragon Ball
  function updateHairModel(style, hexColor, scale = 1.05) {
    if (!hairMeshGroup) return;
    hairMeshGroup.clear();

    const colorVal = parseInt(hexColor.replace("#", ""), 16) || 0xffe690;
    const hairMat = new THREE.MeshStandardMaterial({
      color: colorVal,
      roughness: 0.4,
      emissive: colorVal,
      emissiveIntensity: 0.25
    });

    if (style === "bald") return;

    if (style === "ssj1" || style === "ssj2") {
      const spikeGeo = new THREE.ConeGeometry(0.12 * scale, 0.45 * scale, 4);
      // Espigões voltados para cima
      const s1 = new THREE.Mesh(spikeGeo, hairMat);
      s1.position.set(0, 0.4, -0.05);
      s1.rotation.x = -0.3;
      hairMeshGroup.add(s1);

      const s2 = new THREE.Mesh(spikeGeo, hairMat);
      s2.position.set(0.18, 0.35, 0.05);
      s2.rotation.z = -0.4;
      hairMeshGroup.add(s2);

      const s3 = new THREE.Mesh(spikeGeo, hairMat);
      s3.position.set(-0.18, 0.35, 0.05);
      s3.rotation.z = 0.4;
      hairMeshGroup.add(s3);

      if (style === "ssj2") {
        // Mecha pontuda na testa característica de SSJ2
        const bang = new THREE.Mesh(new THREE.ConeGeometry(0.08 * scale, 0.35 * scale, 4), hairMat);
        bang.position.set(-0.08, 0.1, 0.28);
        bang.rotation.x = 2.4;
        hairMeshGroup.add(bang);
      }
    } else if (style === "ssj3") {
      // Juba Longa até as costas
      for (let i = 0; i < 7; i++) {
        const spike = new THREE.Mesh(new THREE.ConeGeometry(0.14 * scale, 0.8 * scale, 4), hairMat);
        spike.position.set((i % 3 - 1) * 0.15, 0.3 - (i * 0.1), -0.28);
        spike.rotation.x = -0.6;
        hairMeshGroup.add(spike);
      }
    } else if (style === "beast") {
      // Espigão Gigante do Beast
      const giant = new THREE.Mesh(new THREE.ConeGeometry(0.18 * scale, 0.95 * scale, 4), hairMat);
      giant.position.set(0, 0.65, -0.1);
      giant.rotation.x = -0.25;
      hairMeshGroup.add(giant);
    } else {
      // Base / Cabelo Padrão
      const cap = new THREE.Mesh(new THREE.BoxGeometry(0.54, 0.2, 0.54), hairMat);
      cap.position.set(0, 0.26, 0);
      hairMeshGroup.add(cap);
    }
  }

  // Efeitos de Raios (Sparks) e Aura
  function buildAuraAndEffects() {
    // Raios Elétricos
    sparksGroup = new THREE.Group();
    scene.add(sparksGroup);

    // Cilindro da Aura
    const auraGeo = new THREE.CylinderGeometry(0.7, 0.9, 1.8, 16, 1, true);
    const auraMat = new THREE.MeshBasicMaterial({
      color: 0xffcc00,
      transparent: true,
      opacity: 0.35,
      side: THREE.DoubleSide
    });
    auraMesh = new THREE.Mesh(auraGeo, auraMat);
    auraMesh.position.set(0, 0.9, 0);
    scene.add(auraMesh);
  }

  function updateSparksGeometry() {
    if (!sparksGroup) return;
    sparksGroup.clear();

    const colorHex = document.getElementById("inpSparksColor")?.value || "#44AAFF";
    const colorVal = parseInt(colorHex.replace("#", ""), 16) || 0x44aaff;
    const lineMat = new THREE.LineBasicMaterial({ color: colorVal, linewidth: 2 });

    for (let i = 0; i < 4; i++) {
      const points = [];
      let startX = (Math.random() - 0.5) * 0.8;
      let startY = 0.5 + Math.random() * 1.2;
      let startZ = (Math.random() - 0.5) * 0.8;
      points.push(new THREE.Vector3(startX, startY, startZ));

      for (let j = 0; j < 3; j++) {
        startX += (Math.random() - 0.5) * 0.3;
        startY += (Math.random() - 0.5) * 0.3;
        startZ += (Math.random() - 0.5) * 0.3;
        points.push(new THREE.Vector3(startX, startY, startZ));
      }

      const geo = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geo, lineMat);
      sparksGroup.add(line);
    }
  }

  // =========================================================================
  // SIMULAÇÃO DE DRENO EM TEMPO REAL (BOTÃO DE PLAY VERDE)
  // =========================================================================
  function initSimulationController() {
    const playBtn = document.getElementById("btnPlaySimulation");
    if (!playBtn) return;

    playBtn.addEventListener("click", () => {
      toggleSimulation();
    });
  }

  function toggleSimulation() {
    const sim = state.simulation;
    const playBtn = document.getElementById("btnPlaySimulation");
    const playIcon = document.getElementById("simPlayIcon");

    if (sim.running) {
      // Pausar
      sim.running = false;
      clearInterval(sim.intervalId);
      if (playBtn) playBtn.classList.remove("active");
      if (playIcon) playIcon.textContent = "▶";
      updateAutonomyDisplay();
    } else {
      // Iniciar Simulação
      sim.running = true;
      if (playBtn) playBtn.classList.add("active");
      if (playIcon) playIcon.textContent = "⏸";

      // Pega os drenos configurados no formulário
      sim.kiDrain = parseFloat(document.getElementById("inpDrainKi")?.value) || 0;
      sim.stmDrain = parseFloat(document.getElementById("inpDrainStm")?.value) || 0;
      sim.hpDrain = parseFloat(document.getElementById("inpDrainHp")?.value) || 0;

      // Executa tick a cada 100ms
      sim.intervalId = setInterval(() => {
        // Reduz Ki e Stamina proporcional ao tick de 0.1s
        sim.currentKi = Math.max(0, sim.currentKi - (sim.kiDrain * 0.1));
        sim.currentStm = Math.max(0, sim.currentStm - (sim.stmDrain * 0.1));
        if (sim.hpDrain > 0) {
          sim.currentHp = Math.max(0, sim.currentHp - (sim.hpDrain * 0.1));
        }

        updateBarsDisplay();
        updateAutonomyDisplay();

        // Se Ki ou Stamina esgotarem, pausa automaticamente
        if (sim.currentKi <= 0 || sim.currentStm <= 0) {
          toggleSimulation();
          showToast(currentLang === "pt" ? "⚠️ Ki/Stamina esgotados! Forma cancelada por exaustão." : "⚠️ Ki/Stamina depleted! Form cancelled due to exhaustion.", "error");
        }
      }, 100);
    }
  }

  function updateBarsDisplay() {
    const sim = state.simulation;
    const kiPct = Math.max(0, Math.min(100, (sim.currentKi / sim.maxKi) * 100));
    const stmPct = Math.max(0, Math.min(100, (sim.currentStm / sim.maxStm) * 100));
    const hpPct = Math.max(0, Math.min(100, (sim.currentHp / sim.maxHp) * 100));

    const barKi = document.getElementById("barKiFill");
    const barStm = document.getElementById("barStmFill");
    const barHp = document.getElementById("barHpFill");

    if (barKi) barKi.style.width = `${kiPct}%`;
    if (barStm) barStm.style.width = `${stmPct}%`;
    if (barHp) barHp.style.width = `${hpPct}%`;

    const textKi = document.getElementById("barKiText");
    const textStm = document.getElementById("barStmText");
    const textHp = document.getElementById("barHpText");

    if (textKi) textKi.textContent = `${Math.round(sim.currentKi)} / ${sim.maxKi}`;
    if (textStm) textStm.textContent = `${Math.round(sim.currentStm)} / ${sim.maxStm}`;
    if (textHp) textHp.textContent = `${Math.round(hpPct)}%`;
  }

  function updateAutonomyDisplay() {
    const sim = state.simulation;
    const autonomyElem = document.getElementById("simAutonomyText");
    const ratesElem = document.getElementById("simDrainRates");

    if (ratesElem) {
      ratesElem.textContent = `Ki: -${sim.kiDrain}/s · STM: -${sim.stmDrain}/s`;
    }

    if (!sim.running || (sim.kiDrain <= 0 && sim.stmDrain <= 0)) {
      if (autonomyElem) {
        autonomyElem.textContent = currentLang === "pt" ? "Autonomia Estimada: ~∞ (Dreno Inativo)" : "Estimated Autonomy: ~∞ (Drain Inactive)";
      }
      return;
    }

    const kiSeconds = sim.kiDrain > 0 ? sim.currentKi / sim.kiDrain : 999999;
    const stmSeconds = sim.stmDrain > 0 ? sim.currentStm / sim.stmDrain : 999999;
    const minSec = Math.min(kiSeconds, stmSeconds);

    if (autonomyElem) {
      autonomyElem.textContent = currentLang === "pt" 
        ? `Autonomia Restante: ~${Math.round(minSec)}s (${minSec === kiSeconds ? "Ki" : "Stamina"})`
        : `Remaining Autonomy: ~${Math.round(minSec)}s (${minSec === kiSeconds ? "Ki" : "Stamina"})`;
    }
  }

  // =========================================================================
  // CARREGAMENTO DO CATÁLOGO & ÁRVORE DE FORMAS
  // =========================================================================
  async function loadStudioState() {
    try {
      const data = await fetchJson("/api/state");
      state.catalog = data.catalog || {};
      state.staging = data.staging || [];
      state.isDirty = !!data.dirty;

      updateStatusPills(data);
      renderRaceAccordion();
      renderStagingDrawer();

      // Seleciona a primeira forma da raça atual caso nada esteja selecionado
      selectFirstAvailableStage();
    } catch (err) {
      console.error("Falha ao carregar estado:", err);
      showToast("Erro ao conectar com modpack / backend: " + err.message, "error");
    }
  }

  // =========================================================================
  // ADAPTADOR UNIVERSAL DE ESTRUTURA DO CATÁLOGO (DMZ / PYTHON CORE)
  // =========================================================================
  function getRacesMap() {
    if (!state.catalog) return {};
    return state.catalog.racas || state.catalog.races || {};
  }

  function getRaceTrees(raceKey) {
    if (!state.catalog) return {};
    if (raceKey === "global") {
      const u = state.catalog.formas_universais_e_stack || {};
      return u.arvores_de_transformacao || u.forms || {};
    }
    const races = getRacesMap();
    const r = races[raceKey] || {};
    return r.arvores_de_transformacao || r.forms || {};
  }

  function getTreeFormsList(treeData) {
    if (!treeData) return [];
    if (Array.isArray(treeData.formas)) return treeData.formas;
    if (Array.isArray(treeData.forms)) return treeData.forms;
    if (typeof treeData.forms === "object") {
      return Object.keys(treeData.forms).map((k) => ({ id: k, ...treeData.forms[k] }));
    }
    if (typeof treeData.formas === "object") {
      return Object.keys(treeData.formas).map((k) => ({ id: k, ...treeData.formas[k] }));
    }
    return [];
  }

  function updateStatusPills(data) {
    const sourcePill = document.getElementById("statusSourcePill");
    const countsPill = document.getElementById("statusCounts");
    const dirtyPill = document.getElementById("statusDirtyPill");

    if (sourcePill) {
      sourcePill.textContent = data.modpack_path ? (currentLang === "pt" ? "Modpack Conectado" : "Modpack Connected") : (currentLang === "pt" ? "Modo Molde JSON" : "Mold JSON Mode");
    }
    if (countsPill) {
      const racesMap = getRacesMap();
      const numRaces = Object.keys(racesMap).length;
      let numForms = state.catalog.total_transformacoes || 0;
      if (!numForms) {
        Object.keys(racesMap).forEach((rk) => {
          const trees = getRaceTrees(rk);
          Object.values(trees).forEach((t) => {
            numForms += getTreeFormsList(t).length;
          });
        });
      }
      countsPill.textContent = currentLang === "pt" ? `${numRaces} raças · ${numForms} transformações` : `${numRaces} races · ${numForms} transformations`;
    }
    if (dirtyPill) {
      dirtyPill.style.display = state.isDirty ? "inline-block" : "none";
    }
  }

  // Renderiza a Árvore de Transformações em Acordeão na Coluna 1
  function renderRaceAccordion() {
    const container = document.getElementById("raceAccordion");
    if (!container) return;

    const raceKey = state.selectedRace;
    const trees = getRaceTrees(raceKey);
    const treeKeys = Object.keys(trees);

    const titleElem = document.getElementById("currentRaceTreeTitle");
    if (titleElem) {
      const raceName = raceKey.replace(/_/g, " ").toUpperCase();
      titleElem.textContent = `${currentLang === "pt" ? "ÁRVORE DA RAÇA" : "RACE TREE"} (${raceName})`;
    }

    const statsElem = document.getElementById("treeStatsInfo");
    if (statsElem) {
      statsElem.textContent = `${treeKeys.length} ${currentLang === "pt" ? "grupos" : "groups"}`;
    }

    let totalForms = 0;
    treeKeys.forEach((k) => {
      totalForms += getTreeFormsList(trees[k]).length;
    });

    const badgeElem = document.getElementById("raceFormsCountBadge");
    if (badgeElem) badgeElem.textContent = `${totalForms} ${currentLang === "pt" ? "formas" : "forms"}`;

    if (treeKeys.length === 0) {
      container.innerHTML = `<div class="accordion-loading"><span>${currentLang === "pt" ? "Nenhum grupo de transformação nesta raça." : "No transformation groups in this race."}</span></div>`;
      return;
    }

    container.innerHTML = "";

    treeKeys.forEach((groupKey) => {
      const treeData = trees[groupKey];
      const formsList = getTreeFormsList(treeData);
      const isExpanded = state.expandedGroups.has(groupKey);

      const card = document.createElement("div");
      card.className = `acc-group-card ${isExpanded ? "expanded" : ""}`;

      // Header do Grupo
      const header = document.createElement("div");
      header.className = "acc-group-header";
      header.innerHTML = `
        <div class="acc-group-title">
          <span class="acc-group-chevron">▶</span>
          <span>📁 ${treeData.arquivo || groupKey}</span>
        </div>
        <span class="badge badge-bp">(${formsList.length})</span>
      `;
      header.addEventListener("click", () => {
        if (state.expandedGroups.has(groupKey)) {
          state.expandedGroups.delete(groupKey);
        } else {
          state.expandedGroups.add(groupKey);
        }
        renderRaceAccordion();
      });

      card.appendChild(header);

      // Lista de Estágios (Sub-Formas)
      if (isExpanded) {
        const stagesList = document.createElement("div");
        stagesList.className = "acc-stages-list";

        formsList.forEach((stage) => {
          const stageId = stage.id;
          const isSelected = (state.selectedGroupKey === groupKey && state.selectedStageId === stageId);

          const item = document.createElement("div");
          item.className = `acc-stage-item ${isSelected ? "selected" : ""}`;
          item.innerHTML = `
            <div class="acc-stage-left">
              <span class="acc-stage-icon">⚡</span>
              <span>${stage.nome || stage.name || stageId}</span>
              ${isSelected ? '<span class="acc-stage-selected-dot"></span>' : ""}
            </div>
            <span class="badge badge-tp">Lv. ${stage.nivel_habilidade ?? stage.unlockOnSkillLevel ?? 1}</span>
          `;

          item.addEventListener("click", (e) => {
            e.stopPropagation();
            selectStage(groupKey, stageId);
          });

          stagesList.appendChild(item);
        });

        card.appendChild(stagesList);
      }

      container.appendChild(card);
    });
  }

  // Seleciona uma sub-forma e carrega seus dados no editor e no 3D
  function selectStage(groupKey, stageId) {
    state.selectedGroupKey = groupKey;
    state.selectedStageId = stageId;

    renderRaceAccordion();
    loadStageIntoEditor(groupKey, stageId);
  }

  function selectFirstAvailableStage() {
    const trees = getRaceTrees(state.selectedRace);
    const firstGroupKey = Object.keys(trees)[0];
    if (firstGroupKey) {
      state.expandedGroups.add(firstGroupKey);
      const forms = getTreeFormsList(trees[firstGroupKey]);
      if (forms.length > 0) {
        selectStage(firstGroupKey, forms[0].id);
        return;
      }
    }
  }

  // Preenche os campos do formulário na Coluna 3
  function loadStageIntoEditor(groupKey, stageId) {
    const trees = getRaceTrees(state.selectedRace);
    const treeData = trees[groupKey] || {};
    const forms = getTreeFormsList(treeData);
    const stage = forms.find((f) => f.id === stageId) || {};

    const mults = stage.multiplicadores_detalhados || {};
    const drains = stage.drenos || {};
    const visual = stage.visual || {};
    const reqs = stage.requisitos || {};

    // Banner da Forma
    const bannerTitle = document.getElementById("editorActiveFormTitle");
    const bannerMeta = document.getElementById("editorActiveFormMeta");
    if (bannerTitle) bannerTitle.textContent = `${treeData.arquivo || groupKey} -> [${stage.nome || stage.name || stageId}]`;
    if (bannerMeta) bannerMeta.textContent = `${state.selectedRace} · ${treeData.arquivo || groupKey} · ${stageId}`;

    const viewportBadge = document.getElementById("viewportFormBadge");
    if (viewportBadge) viewportBadge.textContent = stage.nome || stage.name || stageId;

    // Aba 1: Multiplicadores & Dreno
    setVal("inpTp", stage.custo_tp_numerico ?? stage.tpCost ?? 0);
    setVal("inpSkillLvl", stage.nivel_habilidade ?? stage.unlockOnSkillLevel ?? 1);
    setVal("inpMultStr", mults.forca_str ?? stage.strength ?? 1.0);
    setVal("inpMultDef", mults.defesa_def ?? stage.defense ?? 1.0);
    setVal("inpMultSpd", mults.velocidade_spd ?? stage.speed ?? 1.0);
    setVal("inpMultPwr", mults.poder_ki_pwr ?? stage.power ?? 1.0);
    setVal("inpMultSkp", mults.golpe_skp ?? stage.skillPower ?? 1.0);
    setVal("inpMultEne", mults.energia_ene ?? stage.energy ?? 1.0);

    setVal("inpDrainKi", drains.energia_ki ?? stage.kiDrain ?? 0);
    setVal("inpDrainStm", drains.estamina ?? stage.staminaDrain ?? 0);
    setVal("inpDrainHp", drains.vida ?? stage.healthDrain ?? 0);
    setVal("inpMasteryGain", stage.maestria?.taxa_ganho ?? stage.masteryRate ?? 1.0);
    setVal("inpMasteryReduction", stage.maestria?.reducao_dreno ?? stage.masteryDrainReduction ?? 50);

    // Atualiza os Cards de Status na Coluna 2
    updateStatusCards(stage, mults, drains);

    // Aba 2: Visual & FX Studio
    const hairStyle = visual.modelo_cabelo || stage.hairStyle || "ssj2";
    const hairColor = visual.cor_cabelo || stage.hairColor || "#FFE690";
    const auraColor = visual.cor_aura || stage.auraColor || "#FFD700";
    const eyeColor = visual.cor_olhos || stage.eyeColor || "#00EEFF";
    const hairScale = visual.escala_cabelo || stage.hairScale || 1.05;

    setVal("selHairModel", hairStyle);
    setVal("inpHairScale", hairScale);
    setVal("inpHairColor", hairColor);
    setVal("inpHairColorPicker", hairColor);
    setVal("inpEyeColor", eyeColor);
    setVal("inpEyeColorPicker", eyeColor);
    setVal("inpAuraColor", auraColor);
    setVal("inpAuraColorPicker", auraColor);

    // Manto de Ki
    const cloakChk = document.getElementById("chkEnableCloak");
    if (cloakChk) cloakChk.checked = !!(visual.manto_ki || stage.enableCloak);
    if (cloakMeshGroup) cloakMeshGroup.visible = !!(visual.manto_ki || stage.enableCloak);

    // Atualiza o Rig 3D
    updateHairModel(hairStyle, hairColor, hairScale);

    // Aba 3: Sagas
    setVal("selSagaReq", reqs.saga || stage.requiredSaga || "none");
    setVal("inpPreviousForm", reqs.forma_previa || stage.previousForm || "");
  }

  function setVal(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val;
  }

  // Atualiza os 6 Cards de Status na Coluna 2
  function updateStatusCards(stage, mults = {}, drains = {}) {
    const setText = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = `${parseFloat(val || 1.0).toFixed(1)}x`;
    };

    const str = mults.forca_str ?? stage.strength ?? 1.0;
    const def = mults.defesa_def ?? stage.defense ?? 1.0;
    const spd = mults.velocidade_spd ?? stage.speed ?? 1.0;
    const pwr = mults.poder_ki_pwr ?? stage.power ?? 1.0;
    const skp = mults.golpe_skp ?? stage.skillPower ?? 1.0;
    const ene = mults.energia_ene ?? stage.energy ?? 1.0;

    setText("statValStr", str);
    setText("statValDef", def);
    setText("statValSpd", spd);
    setText("statValPwr", pwr);
    setText("statValSkp", skp);
    setText("statValEne", ene);

    const bpSum = str + def + spd + pwr + skp + ene;
    const sumBadge = document.getElementById("previewBpSum");
    if (sumBadge) sumBadge.textContent = `Soma: ${bpSum.toFixed(1)}x`;

    const tp = stage.custo_tp_numerico ?? stage.tpCost ?? 0;
    const tpBadge = document.getElementById("previewTpBadge");
    if (tpBadge) tpBadge.textContent = `${tp} TP`;

    const kiDr = drains.energia_ki ?? stage.kiDrain ?? 0;
    const stmDr = drains.estamina ?? stage.staminaDrain ?? 0;
    const drainBadge = document.getElementById("previewDrainSum");
    if (drainBadge) drainBadge.textContent = `Dreno: ${(kiDr + stmDr).toFixed(2)}/s`;
  }

  // Renderiza a Gaveta de Importados (Staging Dock)
  function renderStagingDrawer() {
    const list = document.getElementById("stagingItemsList");
    const badge = document.getElementById("stagingBadge");
    if (!list) return;

    if (badge) badge.textContent = `${currentLang === "pt" ? "Fora da Árvore" : "Unallocated"}: ${state.staging.length} ${currentLang === "pt" ? "itens" : "items"}`;

    if (state.staging.length === 0) {
      list.innerHTML = `<div class="staging-empty-note">${currentLang === "pt" ? "Nenhum item na gaveta. Importe moldes JSON externos para armazená-los aqui antes de alocar." : "No items in staging dock. Import JSON molds to store them here before allocating."}</div>`;
      return;
    }

    list.innerHTML = "";
    state.staging.forEach((item, idx) => {
      const card = document.createElement("div");
      card.className = "staging-item-card";
      card.innerHTML = `
        <div style="display:flex; align-items:center; gap:6px;">
          <span class="badge ${item.kind === 'group' ? 'badge-bp' : 'badge-tp'}">[${item.kind === 'group' ? 'Grupo' : 'Sub'}]</span>
          <span style="font-weight:600; color:var(--text-primary);">${item.name || item.id}</span>
        </div>
        <div style="display:flex; gap:4px;">
          <button type="button" class="btn btn-sm btn-cyan" onclick="window.kiforgeOpenAllocate(${idx})">${currentLang === "pt" ? "Alocar →" : "Allocate →"}</button>
          <button type="button" class="btn btn-sm btn-danger" onclick="window.kiforgeDeleteStaging(${idx})">🗑️</button>
        </div>
      `;
      list.appendChild(card);
    });
  }

  // =========================================================================
  // MODAIS E AÇÕES
  // =========================================================================
  function initModals() {
    // Alternar Gaveta de Importados
    const stagingHeader = document.getElementById("stagingDrawerHeader");
    const stagingBody = document.getElementById("stagingDrawerBody");
    const stagingDrawer = document.getElementById("stagingDrawer");
    if (stagingHeader && stagingBody && stagingDrawer) {
      stagingHeader.addEventListener("click", () => {
        const isOpen = stagingDrawer.classList.toggle("open");
        stagingBody.style.display = isOpen ? "block" : "none";
      });
    }

    // Abas do Editor
    const tabBtns = document.querySelectorAll(".editor-tabs-nav .tab-btn");
    tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        tabBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const tab = btn.dataset.tab;
        document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
        const targetPanel = document.getElementById(`panel${tab.charAt(0).toUpperCase() + tab.slice(1)}`);
        if (targetPanel) targetPanel.classList.add("active");
      });
    });

    // Idioma
    const langBtn = document.getElementById("btnLangToggle");
    if (langBtn) {
      langBtn.addEventListener("click", () => {
        setLanguage(currentLang === "pt" ? "en" : "pt");
      });
    }

    // Seletor de Raça
    const raceSel = document.getElementById("raceSelect");
    if (raceSel) {
      raceSel.addEventListener("change", () => {
        state.selectedRace = raceSel.value;
        renderRaceAccordion();
        selectFirstAvailableStage();
      });
    }

    // Modal Wizard (+ Nova Forma)
    bindModal("btnOpenWizard", "modalWizard", "btnCloseWizard", "btnCancelWizard");
    const confirmWiz = document.getElementById("btnConfirmWizard");
    if (confirmWiz) {
      confirmWiz.addEventListener("click", async () => {
        const payload = {
          race: document.getElementById("wizRace")?.value || "saiyan",
          group_name: document.getElementById("wizGroupName")?.value || "nova_forma.json",
          stage_name: document.getElementById("wizStageName")?.value || "Nova Transformação",
          stage_id: document.getElementById("wizStageId")?.value || "nova_forma_1",
          power_preset: document.getElementById("wizPresetPower")?.value || "mid",
          hair_color: document.getElementById("wizHairColor")?.value || "#FFE690",
          aura_color: document.getElementById("wizAuraColor")?.value || "#FFD700"
        };
        try {
          const res = await fetchJson("/api/wizard/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          document.getElementById("modalWizard").classList.remove("active");
          showToast(res.message || "Forma criada com sucesso!", "success");
          await loadStudioState();
          state.selectedRace = payload.race;
          if (raceSel) raceSel.value = payload.race;
          selectStage(payload.group_name, payload.stage_id);
        } catch (err) {
          showToast("Erro ao criar forma: " + err.message, "error");
        }
      });
    }

    // Modal Diff
    bindModal("btnOpenDiff", "modalDiff", "btnCloseDiff", "btnDismissDiff");
    const btnDiff = document.getElementById("btnOpenDiff");
    if (btnDiff) {
      btnDiff.addEventListener("click", async () => {
        try {
          const diffData = await fetchJson("/api/diff");
          renderDiffModal(diffData);
        } catch (err) {
          showToast("Erro ao calcular diff: " + err.message, "error");
        }
      });
    }

    // Modal Exportar
    bindModal("btnOpenExport", "modalExport", "btnCloseExport", "btnCancelExport");
    const confirmExport = document.getElementById("btnConfirmExport");
    if (confirmExport) {
      confirmExport.addEventListener("click", async () => {
        const scope = document.getElementById("exportScopeSelect")?.value || "full";
        try {
          const res = await fetchJson("/api/export/selective", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              scope: scope,
              race: state.selectedRace,
              group: state.selectedGroupKey,
              stage: state.selectedStageId
            })
          });
          document.getElementById("modalExport").classList.remove("active");
          showToast(res.message || "Molde exportado com sucesso!", "success");
        } catch (err) {
          showToast("Erro ao exportar molde: " + err.message, "error");
        }
      });
    }

    // Abrir Backups
    const btnBackups = document.getElementById("btnOpenBackups");
    if (btnBackups) {
      btnBackups.addEventListener("click", async () => {
        try {
          const res = await fetchJson("/api/backups/open", { method: "POST" });
          showToast(res.message || "Pasta de backups aberta no Windows Explorer", "info");
        } catch (err) {
          showToast("Erro ao abrir pasta de backups: " + err.message, "error");
        }
      });
    }

    // Salvar e Aplicar no Modpack
    const btnApply = document.getElementById("btnApplyModpack");
    if (btnApply) {
      btnApply.addEventListener("click", async () => {
        try {
          const res = await fetchJson("/api/apply", { method: "POST" });
          showToast(res.message || "Salvo e aplicado no modpack com backup zip!", "success");
          await loadStudioState();
        } catch (err) {
          showToast("Erro ao salvar no modpack: " + err.message, "error");
        }
      });
    }

    // Recarregar Modpack
    const btnReload = document.getElementById("btnReloadModpack");
    if (btnReload) {
      btnReload.addEventListener("click", async () => {
        try {
          await fetchJson("/api/reload", { method: "POST" });
          showToast("Modpack recarregado do disco!", "info");
          await loadStudioState();
        } catch (err) {
          showToast("Erro ao recarregar: " + err.message, "error");
        }
      });
    }

    // Live Color Pickers Binding
    bindColorPicker("inpHairColor", "inpHairColorPicker", (hex) => {
      updateHairModel(document.getElementById("selHairModel")?.value, hex);
    });
    bindColorPicker("inpSparksColor", "inpSparksColorPicker", () => {
      updateSparksGeometry();
    });
  }

  function bindModal(openBtnId, modalId, closeBtnId, cancelBtnId) {
    const openBtn = document.getElementById(openBtnId);
    const modal = document.getElementById(modalId);
    const closeBtn = document.getElementById(closeBtnId);
    const cancelBtn = document.getElementById(cancelBtnId);

    if (openBtn && modal) {
      openBtn.addEventListener("click", () => modal.classList.add("active"));
    }
    if (closeBtn && modal) {
      closeBtn.addEventListener("click", () => modal.classList.remove("active"));
    }
    if (cancelBtn && modal) {
      cancelBtn.addEventListener("click", () => modal.classList.remove("active"));
    }
  }

  function bindColorPicker(textId, pickerId, onChange) {
    const text = document.getElementById(textId);
    const picker = document.getElementById(pickerId);
    if (!text || !picker) return;

    picker.addEventListener("input", () => {
      text.value = picker.value.toUpperCase();
      if (onChange) onChange(picker.value);
    });
    text.addEventListener("input", () => {
      if (/^#[0-9A-Fa-f]{6}$/.test(text.value)) {
        picker.value = text.value;
        if (onChange) onChange(text.value);
      }
    });
  }

  function renderDiffModal(diffData) {
    const container = document.getElementById("diffDetailsContainer");
    if (!container) return;
    const added = diffData.added || [];
    const modified = diffData.modified || [];
    const deleted = diffData.deleted || [];

    document.getElementById("diffAddedBadge").textContent = `+${added.length} Adicionadas`;
    document.getElementById("diffModifiedBadge").textContent = `~${modified.length} Modificadas`;
    document.getElementById("diffDeletedBadge").textContent = `-${deleted.length} Removidas`;

    if (added.length === 0 && modified.length === 0 && deleted.length === 0) {
      container.innerHTML = `<div class="diff-empty-note">${currentLang === "pt" ? "Nenhuma alteração detectada." : "No changes detected."}</div>`;
      return;
    }

    container.innerHTML = "";
    modified.forEach((m) => {
      const card = document.createElement("div");
      card.className = "diff-card modified";
      card.innerHTML = `<strong>~ ${m.form_id || m.name}</strong> (${m.race || 'Global'})<br/><span style="font-size:11px; color:var(--text-muted);">${m.details || 'Atributos alterados'}</span>`;
      container.appendChild(card);
    });
  }

  // =========================================================================
  // INICIALIZAÇÃO GERAL AO CARREGAR O DOM
  // =========================================================================
  window.addEventListener("DOMContentLoaded", () => {
    initThreeViewport();
    initSimulationController();
    initModals();
    loadStudioState();
    setLanguage("pt");
  });
})();
