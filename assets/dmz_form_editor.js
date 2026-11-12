(() => {
  "use strict";

  const csrfToken = document.body.dataset.csrfToken || "";

  // State Management
  const state = {
    catalog: null,
    source: "modpack",
    language: localStorage.getItem("kiforge_lang") || "pt",
    dirty: false,
    canUndo: false,
    canRedo: false,
    modpackAvailable: true,
    dmzConfigDir: "",
    desktopJson: "",
    defaultDmzConfigDir: "",
    selectedRace: "all",
    selectedTree: "all",
    selectedFormKey: null,
    activeForm: null,
    activeTab: "stats",
    stagingDock: [],
    stagingOpen: false,
    drainSimRunning: false,
    drainSimTimer: null,
    simCurrentKi: 6500,
    simCurrentStm: 1500,
    simCurrentHp: 3200,
    simMaxKi: 6500,
    simMaxStm: 1500,
    simMaxHp: 3200,
    baseAttributes: {
      str: 100,
      def: 100,
      spd: 100,
      pwr: 100,
      skp: 100,
      ene: 100,
    },
    addonsList: [],
    three: {
      scene: null,
      camera: null,
      renderer: null,
      controls: null,
      characterGroup: null,
      bodyMeshes: {},
      cloakMeshes: {},
      hairGroup: null,
      lightningGroup: null,
      auraGroup: null,
      autoRotate: false,
      auraVisible: true,
    },
  };
  window.state = state;

  const el = (id) => document.getElementById(id);

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function showToast(msg, isError = false) {
    const item = document.createElement("div");
    item.className = isError ? "toast error" : "toast";
    item.textContent = msg;
    const container = el("toastContainer") || document.body;
    container.appendChild(item);
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

  // ==================== THREE.JS MINECRAFT VOXEL RIG ====================

  function createMinecraftSkinCanvas(skinColor = "#FFDBAC", eye1 = "#00FFCC", eye2 = "#00FFCC", hairColor = "#FFE600", noBrows = false) {
    const canvas = document.createElement("canvas");
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext("2d");

    // Base background
    ctx.fillStyle = "#1E293B";
    ctx.fillRect(0, 0, 64, 64);

    // Head Front Face: (8..15, 8..15)
    ctx.fillStyle = skinColor;
    ctx.fillRect(8, 8, 8, 8); // Face front

    // Eyes (2x1 each)
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(9, 12, 2, 1); // Left sclera
    ctx.fillRect(13, 12, 2, 1); // Right sclera

    ctx.fillStyle = eye1;
    ctx.fillRect(9, 12, 1, 1); // Left pupil
    ctx.fillStyle = eye2;
    ctx.fillRect(14, 12, 1, 1); // Right pupil

    // Eyebrows (if not SSJ3)
    if (!noBrows) {
      ctx.fillStyle = hairColor;
      ctx.fillRect(9, 11, 2, 1);
      ctx.fillRect(13, 11, 2, 1);
    }

    // Mouth / Smirk
    ctx.fillStyle = "#8D5B4C";
    ctx.fillRect(11, 14, 2, 1);

    // Torso Front (20..27, 20..31): Orange martial arts Gi with blue undershirt
    ctx.fillStyle = "#F97316"; // Orange Gi
    ctx.fillRect(20, 20, 8, 12);
    ctx.fillStyle = "#0284C7"; // Blue chest V-neck
    ctx.fillRect(23, 20, 2, 4);
    ctx.fillStyle = "#0284C7"; // Blue belt
    ctx.fillRect(20, 28, 8, 2);

    // Arms Front: (44..47, 20..31) and (36..39, 52..63)
    // Blue wristbands & skin
    ctx.fillStyle = skinColor;
    ctx.fillRect(44, 20, 4, 8);
    ctx.fillStyle = "#0284C7"; // Wristbands
    ctx.fillRect(44, 28, 4, 4);

    ctx.fillStyle = skinColor;
    ctx.fillRect(36, 52, 4, 8);
    ctx.fillStyle = "#0284C7"; // Wristbands
    ctx.fillRect(36, 60, 4, 4);

    // Legs Front: (4..7, 20..31) and (20..23, 52..63)
    // Orange pants + blue boots
    ctx.fillStyle = "#F97316";
    ctx.fillRect(4, 20, 4, 8);
    ctx.fillStyle = "#0284C7"; // Boots
    ctx.fillRect(4, 28, 4, 4);

    ctx.fillStyle = "#F97316";
    ctx.fillRect(20, 52, 4, 8);
    ctx.fillStyle = "#0284C7"; // Boots
    ctx.fillRect(20, 60, 4, 4);

    return canvas;
  }

  function initThreePreview() {
    const wrap = el("threeCanvasWrap");
    if (!wrap || typeof THREE === "undefined") return;

    wrap.innerHTML = "";
    const width = wrap.clientWidth || 400;
    const height = wrap.clientHeight || 330;

    const scene = new THREE.Scene();
    scene.background = null; // transparent

    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(0, 16, 44);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    wrap.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 15, 0);
    controls.maxDistance = 80;
    controls.minDistance = 15;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight1.position.set(20, 40, 30);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 0.5);
    dirLight2.position.set(-20, 20, -30);
    scene.add(dirLight2);

    // Root Character Group
    const characterGroup = new THREE.Group();
    scene.add(characterGroup);

    // Build Minecraft Rig (Head 8x8x8, Torso 8x12x4, Arms 4x12x4, Legs 4x12x4)
    const bodyMeshes = {};
    const cloakMeshes = {};

    const initialCanvas = createMinecraftSkinCanvas();
    const skinTexture = new THREE.CanvasTexture(initialCanvas);
    skinTexture.magFilter = THREE.NearestFilter;
    skinTexture.minFilter = THREE.NearestFilter;

    const baseMaterial = new THREE.MeshLambertMaterial({
      map: skinTexture,
    });

    const createLimb = (name, geom, pos, pivot = null) => {
      const mesh = new THREE.Mesh(geom, baseMaterial);
      mesh.position.set(pos.x, pos.y, pos.z);
      characterGroup.add(mesh);
      bodyMeshes[name] = mesh;

      // Cloak (Manto de Ki) layer scaled ~1.06x
      const cloakMat = new THREE.MeshBasicMaterial({
        color: 0xffe600,
        transparent: true,
        opacity: 0.45,
        depthWrite: false,
        side: THREE.DoubleSide,
      });
      const cloakMesh = new THREE.Mesh(geom.clone(), cloakMat);
      cloakMesh.scale.set(1.06, 1.06, 1.06);
      mesh.add(cloakMesh);
      cloakMeshes[name] = cloakMesh;

      return mesh;
    };

    // Rig geometry & positions
    // Head: 8x8x8 at Y=24
    createLimb("head", new THREE.BoxGeometry(8, 8, 8), { x: 0, y: 24, z: 0 });
    // Torso: 8x12x4 at Y=14
    createLimb("torso", new THREE.BoxGeometry(8, 12, 4), { x: 0, y: 14, z: 0 });
    // Right Arm: 4x12x4 at X=-6, Y=14
    createLimb("arm_r", new THREE.BoxGeometry(4, 12, 4), { x: -6, y: 14, z: 0 });
    // Left Arm: 4x12x4 at X=6, Y=14
    createLimb("arm_l", new THREE.BoxGeometry(4, 12, 4), { x: 6, y: 14, z: 0 });
    // Right Leg: 4x12x4 at X=-2, Y=2
    createLimb("leg_r", new THREE.BoxGeometry(4, 12, 4), { x: -2, y: 2, z: 0 });
    // Left Leg: 4x12x4 at X=2, Y=2
    createLimb("leg_l", new THREE.BoxGeometry(4, 12, 4), { x: 2, y: 2, z: 0 });

    // Hair Group (attached to head)
    const hairGroup = new THREE.Group();
    bodyMeshes.head.add(hairGroup);

    // Lightning Sparks Group
    const lightningGroup = new THREE.Group();
    characterGroup.add(lightningGroup);

    // Wave Aura Group (Soft upward particles/planes - NO solid cylinders)
    const auraGroup = new THREE.Group();
    characterGroup.add(auraGroup);

    // Generate 24 soft floating aura flame planes
    const auraPlaneGeom = new THREE.PlaneGeometry(3, 8);
    for (let i = 0; i < 24; i++) {
      const angle = (i / 24) * Math.PI * 2;
      const radius = 6 + Math.random() * 4;
      const auraMat = new THREE.MeshBasicMaterial({
        color: 0xffe600,
        transparent: true,
        opacity: 0.25,
        depthWrite: false,
        side: THREE.DoubleSide,
      });
      const p = new THREE.Mesh(auraPlaneGeom, auraMat);
      p.position.set(Math.cos(angle) * radius, Math.random() * 26, Math.sin(angle) * radius);
      p.rotation.y = angle + Math.PI / 2;
      p.userData = { speed: 0.12 + Math.random() * 0.15, initialY: p.position.y };
      auraGroup.add(p);
    }

    state.three = {
      scene,
      camera,
      renderer,
      controls,
      characterGroup,
      bodyMeshes,
      cloakMeshes,
      hairGroup,
      lightningGroup,
      auraGroup,
      skinTexture,
      autoRotate: false,
      auraVisible: true,
    };

    // Animation Loop
    let clock = new THREE.Clock();
    let sparkTimer = 0;

    function animate() {
      requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      if (state.three.autoRotate) {
        characterGroup.rotation.y += delta * 0.8;
      }

      // Gentle martial arts breathing idle animation
      const breath = Math.sin(time * 3) * 0.02;
      bodyMeshes.torso.scale.set(1 + breath, 1 + breath, 1 + breath);
      bodyMeshes.arm_r.rotation.z = Math.sin(time * 3) * 0.04 - 0.08;
      bodyMeshes.arm_l.rotation.z = -Math.sin(time * 3) * 0.04 + 0.08;

      // Cloak pulsating glow (senoidal)
      const cloakPulse = 0.35 + 0.2 * Math.sin(time * 6);
      Object.values(cloakMeshes).forEach((m) => {
        if (m.material) {
          m.material.opacity = state.three.auraVisible ? cloakPulse : 0;
        }
      });

      // Aura wave ascending
      if (state.three.auraVisible) {
        auraGroup.children.forEach((p) => {
          p.position.y += p.userData.speed;
          if (p.position.y > 32) {
            p.position.y = 0;
          }
          p.material.opacity = 0.25 * (1 - p.position.y / 32);
        });
      } else {
        auraGroup.children.forEach((p) => (p.material.opacity = 0));
      }

      // Lightning Jitter Animation (SSJ2/SSJ3 Sparks FX)
      sparkTimer += delta;
      if (sparkTimer > 0.08) {
        sparkTimer = 0;
        updateLightningSparks();
      }

      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // Window Resize Handler
    window.addEventListener("resize", () => {
      if (!wrap || !renderer || !camera) return;
      const w = wrap.clientWidth;
      const h = wrap.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });
  }

  function updateThreeHair(hairType = "base", hairHex = "#FFE600", secondaryHairHex = "") {
    const { hairGroup } = state.three;
    if (!hairGroup || typeof THREE === "undefined") return;

    // Clear existing hair meshes
    while (hairGroup.children.length > 0) {
      hairGroup.remove(hairGroup.children[0]);
    }

    const hairColor = new THREE.Color(hairHex || "#FFE600");
    const secColor = secondaryHairHex ? new THREE.Color(secondaryHairHex) : hairColor;

    const hairMat = new THREE.MeshLambertMaterial({ color: hairColor });
    const secHairMat = new THREE.MeshLambertMaterial({ color: secColor });

    const createHairBlock = (w, h, d, x, y, z, rx = 0, ry = 0, rz = 0, mat = hairMat) => {
      const geom = new THREE.BoxGeometry(w, h, d);
      const mesh = new THREE.Mesh(geom, mat);
      mesh.position.set(x, y, z);
      mesh.rotation.set(rx, ry, rz);
      hairGroup.add(mesh);
      return mesh;
    };

    switch (hairType.toLowerCase()) {
      case "ssj1":
        // Base hair cap
        createHairBlock(8.4, 2, 8.4, 0, 3.5, 0);
        // 5 upward spikes
        createHairBlock(3, 7, 3, 0, 7, 0, -0.1, 0, 0);
        createHairBlock(2.5, 6, 2.5, -3, 6, -1, 0.1, 0, -0.2);
        createHairBlock(2.5, 6, 2.5, 3, 6, -1, 0.1, 0, 0.2);
        createHairBlock(2.2, 5, 2.2, -2, 5.5, 2, -0.2, 0, -0.15, secHairMat);
        createHairBlock(2.2, 5, 2.2, 2, 5.5, 2, -0.2, 0, 0.15);
        // Front bangs
        createHairBlock(1.5, 3.5, 1, -1.5, 2, 4.3, 0.1, 0, -0.1);
        break;

      case "ssj2":
        // Sharper, higher spikes + lightning bang
        createHairBlock(8.4, 2, 8.4, 0, 3.5, 0);
        createHairBlock(2.8, 9, 2.8, 0, 8, -1, -0.15, 0, 0);
        createHairBlock(2.4, 8, 2.4, -3.5, 7.5, -1, 0.1, 0, -0.3);
        createHairBlock(2.4, 8, 2.4, 3.5, 7.5, -1, 0.1, 0, 0.3);
        createHairBlock(2.2, 7, 2.2, -2.5, 7, 2, -0.25, 0, -0.2);
        createHairBlock(2.2, 7, 2.2, 2.5, 7, 2, -0.25, 0, 0.2);
        // Iconic thin SSJ2 forehead bang
        createHairBlock(0.8, 4.5, 1, 0.8, 1.5, 4.3, 0.1, 0, 0.15, secHairMat);
        break;

      case "ssj3":
        // Long cascading hair reaching waist down the back
        createHairBlock(8.4, 3, 8.4, 0, 3.5, 0);
        createHairBlock(3.5, 8, 3.5, 0, 7.5, -1, -0.1, 0, 0);
        createHairBlock(3, 7, 3, -3, 6.5, 0, 0.1, 0, -0.2);
        createHairBlock(3, 7, 3, 3, 6.5, 0, 0.1, 0, 0.2);
        // Massive back mane (down to Y = -14)
        createHairBlock(8, 14, 4, 0, -2, -5, 0.15, 0, 0);
        createHairBlock(6, 12, 3, 0, -9, -6, 0.2, 0, 0, secHairMat);
        break;

      case "ssj4":
        // Wild shaggy hair + chest fur
        createHairBlock(8.6, 4, 8.6, 0, 3, 0);
        createHairBlock(3, 7, 3, -2, 6.5, -2, 0.2, 0, -0.2);
        createHairBlock(3, 7, 3, 2, 6.5, -2, 0.2, 0, 0.2);
        createHairBlock(9, 10, 3, 0, -1, -4.5, 0.1, 0, 0);
        // Side bangs framing face
        createHairBlock(1.8, 5, 1.5, -4.2, 0, 3, 0.1, 0, 0);
        createHairBlock(1.8, 5, 1.5, 4.2, 0, 3, 0.1, 0, 0);
        break;

      case "beast":
        // Ultra-tall vertical spikes (Gohan Beast)
        createHairBlock(8.4, 3, 8.4, 0, 3.5, 0);
        createHairBlock(3.2, 14, 3.2, 0, 10.5, -1.5, -0.15, 0, 0);
        createHairBlock(2.8, 12, 2.8, -3.2, 9.5, -1, 0.1, 0, -0.25);
        createHairBlock(2.8, 12, 2.8, 3.2, 9.5, -1, 0.1, 0, 0.25);
        createHairBlock(1, 5, 1, 1, 1.5, 4.4, 0.1, 0, 0.1);
        break;

      case "namekian":
        // Bald head + antennas
        createHairBlock(8.2, 2, 8.2, 0, 3.5, 0, 0, 0, 0, hairMat);
        createHairBlock(0.6, 3.5, 0.6, -1.8, 5, 3.5, 0.4, 0, -0.2);
        createHairBlock(0.6, 3.5, 0.6, 1.8, 5, 3.5, 0.4, 0, 0.2);
        break;

      case "demon":
        // Cold Demon / Frieza Horns
        createHairBlock(8.4, 2, 8.4, 0, 3.5, 0);
        createHairBlock(1.5, 5, 1.5, -4.5, 5.5, 0, 0, 0, -0.6);
        createHairBlock(1.5, 5, 1.5, 4.5, 5.5, 0, 0, 0, 0.6);
        break;

      case "bald":
        // Minimal smooth cap
        createHairBlock(8.1, 1, 8.1, 0, 3.5, 0);
        break;

      case "base":
      default:
        // Goku base messy spikes
        createHairBlock(8.4, 3, 8.4, 0, 3.2, 0);
        createHairBlock(2.5, 4, 2.5, -3, 4.5, -2, 0.1, 0, -0.2);
        createHairBlock(2.5, 4, 2.5, 3, 4.5, -2, 0.1, 0, 0.2);
        createHairBlock(2, 3.5, 2, 0, 4.5, -2, -0.1, 0, 0);
        createHairBlock(1.5, 3, 1, -1.5, 2, 4.3, 0.1, 0, -0.1);
        break;
    }
  }

  function updateLightningSparks() {
    const { lightningGroup } = state.three;
    if (!lightningGroup || typeof THREE === "undefined") return;

    while (lightningGroup.children.length > 0) {
      lightningGroup.remove(lightningGroup.children[0]);
    }

    const enabled = el("visLightningToggle")?.checked;
    if (!enabled || !state.three.auraVisible) return;

    const hex = el("visLightningHex")?.value || "#38BDF8";
    const lineMat = new THREE.LineBasicMaterial({
      color: new THREE.Color(hex),
      linewidth: 2,
    });

    const numArcs = 5;
    for (let i = 0; i < numArcs; i++) {
      const points = [];
      let curX = (Math.random() - 0.5) * 16;
      let curY = Math.random() * 28;
      let curZ = (Math.random() - 0.5) * 12;

      points.push(new THREE.Vector3(curX, curY, curZ));
      const segments = 4 + Math.floor(Math.random() * 3);
      for (let s = 0; s < segments; s++) {
        curX += (Math.random() - 0.5) * 6;
        curY += (Math.random() - 0.3) * 6;
        curZ += (Math.random() - 0.5) * 6;
        points.push(new THREE.Vector3(curX, curY, curZ));
      }

      const geom = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(geom, lineMat);
      lightningGroup.add(line);
    }
  }

  function updateThreeColorsAndTexture() {
    const { bodyMeshes, cloakMeshes, auraGroup } = state.three;
    if (!bodyMeshes.head || typeof THREE === "undefined") return;

    const auraHex = el("visAuraHex")?.value || "#FFE600";
    const hairHex = el("visHairHex")?.value || "#FFE600";
    const secHairHex = el("visSecondaryHairHex")?.value || "";
    const skinHex = el("visSkinHex")?.value || "#FFDBAC";
    const eye1Hex = el("visEye1Hex")?.value || "#00FFCC";
    const eye2Hex = el("visEye2Hex")?.value || "#00FFCC";
    const hairType = el("visHairType")?.value || "base";
    const modelScale = parseFloat(el("visModelScale")?.value || "1.0");

    // Scale character group
    state.three.characterGroup.scale.set(modelScale, modelScale, modelScale);

    // Update Minecraft skin canvas & texture
    const newCanvas = createMinecraftSkinCanvas(skinHex, eye1Hex, eye2Hex, hairHex, hairType === "ssj3");
    if (state.three.skinTexture) {
      state.three.skinTexture.image = newCanvas;
      state.three.skinTexture.needsUpdate = true;
    }

    // Update Cloak (Manto de Ki) colors
    const cloakColor = new THREE.Color(el("visCloakHex")?.value || auraHex);
    Object.values(cloakMeshes).forEach((m) => {
      if (m.material) {
        m.material.color = cloakColor;
      }
    });

    // Update Aura Wave particle colors
    const auraColor = new THREE.Color(auraHex);
    if (auraGroup) {
      auraGroup.children.forEach((p) => {
        if (p.material) p.material.color = auraColor;
      });
    }

    // Update 3D Hair blocks
    updateThreeHair(hairType, hairHex, secHairHex);
  }

  // ==================== REAL STATS & BARS CALCULATOR ====================

  function recalculateStatsAndBars() {
    if (!state.activeForm || !state.catalog) return;

    const rKey = state.activeForm.raca || state.selectedRace;
    const raceObj = state.catalog.racas?.[rKey] || {};
    const raceStats = raceObj.stats || {};

    const mults = {
      forca_str: parseFloat(el("mult_str")?.value || "1.0"),
      poder_ki_pwr: parseFloat(el("mult_pwr")?.value || "1.0"),
      defesa_def: parseFloat(el("mult_def")?.value || "1.0"),
      golpe_skp: parseFloat(el("mult_skp")?.value || "1.0"),
      velocidade_spd: parseFloat(el("mult_spd")?.value || "1.0"),
      velocidade_ataque: parseFloat(el("mult_atk_spd")?.value || "1.0"),
      estamina_stm: parseFloat(el("mult_stm")?.value || "1.0"),
      vitalidade_vit: parseFloat(el("mult_vit")?.value || "1.0"),
      energia_ene: parseFloat(el("mult_ene")?.value || "1.0"),
    };

    const attrs = {
      str: parseInt(el("attrStr")?.value || "100", 10),
      def: parseInt(el("attrDef")?.value || "100", 10),
      spd: parseInt(el("attrSpd")?.value || "100", 10),
      pwr: parseInt(el("attrPwr")?.value || "100", 10),
      skp: parseInt(el("attrSkp")?.value || "100", 10),
      ene: parseInt(el("attrEne")?.value || "100", 10),
    };

    // Update final multiplied attribute values
    el("finalStrVal").textContent = (attrs.str * mults.forca_str).toFixed(1);
    el("finalDefVal").textContent = (attrs.def * mults.defesa_def).toFixed(1);
    el("finalSpdVal").textContent = (attrs.spd * mults.velocidade_spd).toFixed(1);
    el("finalPwrVal").textContent = (attrs.pwr * mults.poder_ki_pwr).toFixed(1);
    el("finalSkpVal").textContent = (attrs.skp * mults.golpe_skp).toFixed(1);
    el("finalEneVal").textContent = (attrs.ene * mults.energia_ene).toFixed(1);

    // Compute real max HP, KI, STM using formula
    const scaling = raceStats.statScaling || {};
    const vitScaling = parseFloat(scaling.VIT_scaling || "1.0");
    const eneScaling = parseFloat(scaling.ENE_scaling || "1.0");
    const defScaling = parseFloat(scaling.DEF_scaling || scaling.STM_scaling || "1.0");

    const maxHp = Math.max(100, Math.floor(100.0 + attrs.str * vitScaling * mults.vitalidade_vit * 30.0));
    const maxKi = Math.max(100, Math.floor(100.0 + attrs.ene * eneScaling * mults.energia_ene * 50.0));
    const maxStm = Math.max(100, Math.floor(100.0 + attrs.def * defScaling * mults.estamina_stm * 20.0));

    state.simMaxHp = maxHp;
    state.simMaxKi = maxKi;
    state.simMaxStm = maxStm;

    if (!state.drainSimRunning) {
      state.simCurrentHp = maxHp;
      state.simCurrentKi = maxKi;
      state.simCurrentStm = maxStm;
    }

    updateBarsDOM();

    // Drains & Autonomy
    const drKi = parseFloat(el("dr_ki")?.value || "0.0");
    const drStm = parseFloat(el("dr_stm")?.value || "0.0");
    const drHp = parseFloat(el("dr_hp")?.value || "0.0");

    el("drainRateInfo").textContent = `-${drKi.toFixed(1)} Ki/s · -${drStm.toFixed(1)} STM/s`;

    let autonomySec = Infinity;
    if (drKi > 0) autonomySec = Math.min(autonomySec, maxKi / drKi);
    if (drStm > 0) autonomySec = Math.min(autonomySec, maxStm / drStm);

    if (autonomySec === Infinity) {
      el("autonomyBadge").textContent = "⏱️ Autonomia: ∞";
    } else {
      const mins = Math.floor(autonomySec / 60);
      const secs = Math.floor(autonomySec % 60);
      el("autonomyBadge").textContent = `⏱️ Autonomia: ${mins}m ${secs}s`;
    }
  }
  window.recalculateStatsAndBars = recalculateStatsAndBars;

  function updateBarsDOM() {
    const hpPct = Math.max(0, Math.min(100, (state.simCurrentHp / state.simMaxHp) * 100));
    const kiPct = Math.max(0, Math.min(100, (state.simCurrentKi / state.simMaxKi) * 100));
    const stmPct = Math.max(0, Math.min(100, (state.simCurrentStm / state.simMaxStm) * 100));

    el("barHpFill").style.width = `${hpPct}%`;
    el("barKiFill").style.width = `${kiPct}%`;
    el("barStmFill").style.width = `${stmPct}%`;

    el("barHpVal").textContent = `${state.simCurrentHp.toLocaleString("pt-BR")} / ${state.simMaxHp.toLocaleString("pt-BR")}`;
    el("barKiVal").textContent = `${state.simCurrentKi.toLocaleString("pt-BR")} / ${state.simMaxKi.toLocaleString("pt-BR")}`;
    el("barStmVal").textContent = `${state.simCurrentStm.toLocaleString("pt-BR")} / ${state.simMaxStm.toLocaleString("pt-BR")}`;
  }

  function toggleDrainSimulation() {
    const btn = el("btnDrainSimPlay");
    if (state.drainSimRunning) {
      // Pause
      clearInterval(state.drainSimTimer);
      state.drainSimRunning = false;
      btn.textContent = "▶";
      btn.classList.remove("active");
    } else {
      // Start
      state.drainSimRunning = true;
      btn.textContent = "⏸";
      btn.classList.add("active");

      state.drainSimTimer = setInterval(() => {
        const drKi = parseFloat(el("dr_ki")?.value || "0.0");
        const drStm = parseFloat(el("dr_stm")?.value || "0.0");
        const drHp = parseFloat(el("dr_hp")?.value || "0.0");

        state.simCurrentKi = Math.max(0, state.simCurrentKi - drKi);
        state.simCurrentStm = Math.max(0, state.simCurrentStm - drStm);
        state.simCurrentHp = Math.max(0, state.simCurrentHp - drHp);

        updateBarsDOM();

        if (state.simCurrentKi <= 0 && state.simCurrentStm <= 0) {
          toggleDrainSimulation(); // auto-pause when exhausted
        }
      }, 1000);
    }
  }

  function resetDrainSimulation() {
    if (state.drainSimRunning) {
      toggleDrainSimulation();
    }
    state.simCurrentHp = state.simMaxHp;
    state.simCurrentKi = state.simMaxKi;
    state.simCurrentStm = state.simMaxStm;
    updateBarsDOM();
  }

  // ==================== ACCORDION TREE & FORM SELECTION ====================

  function renderRaceDropdown() {
    const sel = el("raceSelectDropdown");
    if (!sel || !state.catalog) return;

    const currentVal = sel.value || state.selectedRace;
    sel.innerHTML = "";

    const optAll = document.createElement("option");
    optAll.value = "all";
    optAll.textContent = "Todas as Raças";
    sel.appendChild(optAll);

    // 100% dynamic from catalog.racas
    const races = Object.values(state.catalog.racas || {}).sort((a, b) =>
      String(a.nome_exibicao).localeCompare(String(b.nome_exibicao))
    );

    races.forEach((r) => {
      const opt = document.createElement("option");
      opt.value = r.id_raca;
      opt.textContent = `${r.nome_exibicao} (${r.total_formas || 0})`;
      sel.appendChild(opt);
    });

    const optUniv = document.createElement("option");
    optUniv.value = "universal";
    optUniv.textContent = "Formas Universais & Stack";
    sel.appendChild(optUniv);

    if (Array.from(sel.options).some((o) => o.value === currentVal)) {
      sel.value = currentVal;
    } else {
      sel.value = "all";
      state.selectedRace = "all";
    }
  }

  function renderTreeAccordion() {
    const container = el("treeAccordionList");
    if (!container || !state.catalog) return;

    container.innerHTML = "";
    const filterText = (el("treeSearchInput")?.value || "").trim().toLowerCase();

    const selectedRaceKey = el("raceSelectDropdown")?.value || "all";

    const groupsToRender = [];

    if (selectedRaceKey === "all" || selectedRaceKey !== "universal") {
      Object.entries(state.catalog.racas || {}).forEach(([rKey, rObj]) => {
        if (selectedRaceKey !== "all" && selectedRaceKey !== rKey) return;
        Object.entries(rObj.arvores_de_transformacao || {}).forEach(([tKey, tObj]) => {
          groupsToRender.push({
            type: "race",
            raceKey: rKey,
            raceName: rObj.nome_exibicao,
            treeKey: tKey,
            treeObj: tObj,
          });
        });
      });
    }

    if (selectedRaceKey === "all" || selectedRaceKey === "universal") {
      Object.entries(state.catalog.formas_universais_e_stack || {}).forEach(([gKey, gObj]) => {
        groupsToRender.push({
          type: "universal",
          raceKey: "universal",
          raceName: "Universal",
          treeKey: gKey,
          treeObj: gObj,
        });
      });
    }

    if (groupsToRender.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-muted); font-size:12px;">Nenhuma transformação encontrada neste filtro.</div>`;
      return;
    }

    groupsToRender.forEach((grp) => {
      const forms = grp.treeObj.formas || [];
      const matchingForms = forms.filter((f) => {
        if (!filterText) return true;
        const hay = `${f.id} ${f.nome} ${grp.treeKey} ${grp.raceName}`.toLowerCase();
        return hay.includes(filterText);
      });

      if (filterText && matchingForms.length === 0) return;

      const groupCard = document.createElement("div");
      groupCard.className = "tree-group";

      const header = document.createElement("div");
      header.className = "tree-group-header";
      header.innerHTML = `
        <div class="tree-group-title">
          <span class="tree-group-arrow">▼</span>
          <span>📁 ${escapeHtml(grp.treeObj.arquivo || `${grp.treeKey}.json`)}</span>
          <span class="badge" style="background:#1E293B; font-size:9.5px;">${forms.length}</span>
        </div>
        <span class="text-xs text-muted">${escapeHtml(grp.raceName)}</span>
      `;

      header.addEventListener("click", () => {
        groupCard.classList.toggle("collapsed");
      });

      const stageList = document.createElement("div");
      stageList.className = "tree-stage-list";

      matchingForms.forEach((f, idx) => {
        const itemKey = `${grp.raceKey}::${grp.treeKey}::${f.id}`;
        const isSelected = state.selectedFormKey === itemKey;

        const stageRow = document.createElement("div");
        stageRow.className = "tree-stage-item" + (isSelected ? " selected" : "");
        stageRow.draggable = true;

        const tier = f.tier || "1";
        const tierClass = `tier-${Math.min(10, Math.max(1, parseInt(tier, 10)))}`;

        stageRow.innerHTML = `
          <div class="stage-item-left">
            <span class="stage-item-drag" title="Arraste para reorganizar">⋮⋮</span>
            <span class="badge badge-tp" style="font-size:9px; padding:1px 4px;">#${f.nivel_habilidade || idx + 1}</span>
            <span class="stage-item-name">${escapeHtml(f.nome || f.id)}</span>
          </div>
          <span class="tier-badge ${tierClass}">T${tier}</span>
        `;

        stageRow.addEventListener("click", (e) => {
          e.stopPropagation();
          selectForm(grp.raceKey, grp.treeKey, f.id);
        });

        stageList.appendChild(stageRow);
      });

      groupCard.appendChild(header);
      groupCard.appendChild(stageList);
      container.appendChild(groupCard);
    });
  }

  function selectForm(raceKey, treeKey, formId) {
    if (!state.catalog) return;

    let targetForm = null;
    let targetTreeObj = null;

    if (raceKey === "universal") {
      const grp = state.catalog.formas_universais_e_stack?.[treeKey];
      if (grp) {
        targetTreeObj = grp;
        targetForm = (grp.formas || []).find((f) => f.id === formId);
      }
    } else {
      const r = state.catalog.racas?.[raceKey];
      if (r) {
        const t = r.arvores_de_transformacao?.[treeKey];
        if (t) {
          targetTreeObj = t;
          targetForm = (t.formas || []).find((f) => f.id === formId);
        }
      }
    }

    if (!targetForm) return;

    state.selectedRace = raceKey;
    state.selectedTree = treeKey;
    state.selectedFormKey = `${raceKey}::${treeKey}::${formId}`;
    state.activeForm = targetForm;

    // Highlight row in accordion
    document.querySelectorAll(".tree-stage-item").forEach((el) => {
      el.classList.remove("selected");
    });
    renderTreeAccordion();

    // Populate Right Inspector
    populateInspector(targetForm, raceKey, treeKey, targetTreeObj);

    // Update 3D Preview
    updateThreeColorsAndTexture();

    // Recalculate Stats & Bars
    recalculateStatsAndBars();
  }

  function populateInspector(form, raceKey, treeKey, treeObj) {
    el("inspectorEmpty").style.display = "none";
    el("inspectorContent").style.display = "flex";

    el("inspTitle").textContent = form.nome || form.id;
    el("inspSub").textContent = `${raceKey} · ${treeKey} · ${form.id}`;

    const tier = form.tier || "1";
    const tierClass = `tier-${Math.min(10, Math.max(1, parseInt(tier, 10)))}`;
    el("inspTierBadge").className = `tier-badge ${tierClass}`;
    el("inspTierBadge").textContent = `Tier ${tier}`;
    if (el("inspTierDetail")) {
      el("inspTierDetail").className = `tier-badge ${tierClass}`;
      el("inspTierDetail").textContent = `Tier ${tier}`;
    }

    el("inspAddonBadge").textContent = form.addon_origem || "Core";

    // Populate stage quick select
    const stageSel = el("stageQuickSelect");
    stageSel.innerHTML = "";
    (treeObj.formas || []).forEach((sf) => {
      const opt = document.createElement("option");
      opt.value = sf.id;
      opt.textContent = `Nível ${sf.nivel_habilidade || 1}: ${sf.nome || sf.id}`;
      if (sf.id === form.id) opt.selected = true;
      stageSel.appendChild(opt);
    });

    // Tab 1: Stats & Drains
    el("inpTp").value = form.custo_tp_numerico ?? 0;
    el("inpSkillLvl").value = form.nivel_habilidade ?? 1;
    el("chkBuyMaster").checked = Boolean(form.comprar_no_mestre);

    // Master dropdown
    const mSel = el("inpMasterSelect");
    mSel.innerHTML = `<option value="">— Nenhum mestre vinculado —</option>`;
    (state.catalog.opcoes_mestres || []).forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = m.nome;
      if (form.mestre && form.mestre.toLowerCase() === m.id.toLowerCase()) {
        opt.selected = true;
      }
      mSel.appendChild(opt);
    });

    const mults = form.multiplicadores_detalhados || {};
    el("mult_str").value = mults.forca_str ?? 1.0;
    el("mult_pwr").value = mults.poder_ki_pwr ?? 1.0;
    el("mult_def").value = mults.defesa_def ?? 1.0;
    el("mult_skp").value = mults.golpe_skp ?? 1.0;
    el("mult_spd").value = mults.velocidade_spd ?? 1.0;
    el("mult_atk_spd").value = mults.velocidade_ataque ?? 1.0;
    el("mult_stm").value = mults.estamina_stm ?? 1.0;
    el("mult_vit").value = mults.vitalidade_vit ?? 1.0;
    el("mult_ene").value = mults.energia_ene ?? 1.0;

    const drenos = form.drenos || {};
    el("dr_ki").value = drenos.energia_ki ?? 0.0;
    el("dr_stm").value = drenos.estamina ?? 0.0;
    el("dr_hp").value = drenos.vida ?? 0.0;
    el("dr_stm_hit").value = drenos.mult_estamina_golpe ?? 1.0;
    el("dr_stack_mult").value = drenos.mult_dreno_stack ?? 2.0;
    el("chkStackable").checked = Boolean(drenos.acumulavel);

    const mst = form.maestria || {};
    el("mst_max").value = mst.maestria_maxima ?? 100;
    el("mst_instant").value = mst.maestria_transf_instantanea ?? 40;
    el("mst_hit_dealt").value = mst.ganho_golpe_dado ?? 0.025;
    el("mst_hit_rcv").value = mst.ganho_dano_recebido ?? 0.025;
    el("mst_passive").value = mst.ganho_passivo_5s ?? 0.01;
    el("mst_cost_mult").value = mst.mult_custo_maestria_max ?? 0.75;
    el("mst_stat_mult").value = mst.mult_status_maestria_max ?? 1.0;

    // Tab 2: Visual & FX Studio
    const vis = form.visual || {};
    el("visHairType").value = vis.tipo_cabelo || "base";
    el("visModelType").value = vis.tipo_modelo || "player";
    el("visModelScale").value = vis.escala ?? 1.0;
    el("visEmissiveToggle").checked = Boolean(vis.brilho_emissivo);

    const auraHex = vis.cor_aura || "#FFE600";
    el("visAuraHex").value = auraHex;
    el("visAuraColorPicker").value = auraHex.startsWith("#") && auraHex.length === 7 ? auraHex : "#FFE600";

    const hairHex = vis.cor_cabelo || "#FFE600";
    el("visHairHex").value = hairHex;
    el("visHairColorPicker").value = hairHex.startsWith("#") && hairHex.length === 7 ? hairHex : "#FFE600";

    const secHairHex = vis.cor_cabelo_secundaria || "";
    el("visSecondaryHairHex").value = secHairHex;
    el("visSecondaryHairColorPicker").value = secHairHex.startsWith("#") && secHairHex.length === 7 ? secHairHex : "#FFF275";

    const skinHex = vis.cor_pele || "#FFDBAC";
    el("visSkinHex").value = skinHex;
    el("visSkinColorPicker").value = skinHex.startsWith("#") && skinHex.length === 7 ? skinHex : "#FFDBAC";

    const eye1Hex = vis.cor_olho_1 || "#00FFCC";
    el("visEye1Hex").value = eye1Hex;
    el("visEye1ColorPicker").value = eye1Hex.startsWith("#") && eye1Hex.length === 7 ? eye1Hex : "#00FFCC";

    const eye2Hex = vis.cor_olho_2 || "#00FFCC";
    el("visEye2Hex").value = eye2Hex;
    el("visEye2ColorPicker").value = eye2Hex.startsWith("#") && eye2Hex.length === 7 ? eye2Hex : "#00FFCC";

    const raios = vis.raios || {};
    el("visLightningToggle").checked = Boolean(raios.ativado);
    el("visLightningHex").value = raios.cor || "#38BDF8";
    el("visLightningColorPicker").value = (raios.cor && raios.cor.startsWith("#") && raios.cor.length === 7) ? raios.cor : "#38BDF8";

    const manto = vis.manto || {};
    el("visCloakToggle").checked = Boolean(manto.ativado);
    el("visCloakHex").value = manto.cor || auraHex;
    el("visCloakColorPicker").value = (manto.cor && manto.cor.startsWith("#") && manto.cor.length === 7) ? manto.cor : "#A78BFA";
    el("visCloakOpacity").value = manto.opacidade ?? 0.45;

    // Tab 3: Sagas & Requisitos
    const reqs = form.requisitos || {};
    el("req_dmz_lvl").value = reqs.nivel_dmz_minimo ?? 1;
    el("req_lvl_req").value = reqs.nivel_requisito ?? 0;

    // Saga select
    const sagaSel = el("req_saga_select");
    sagaSel.innerHTML = `<option value="">— Nenhuma saga exigida —</option>`;
    (state.catalog.opcoes_sagas || []).forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s.id;
      opt.textContent = `${s.categoria}: ${s.nome}`;
      if (reqs.saga && reqs.saga.toLowerCase() === s.id.toLowerCase()) {
        opt.selected = true;
      }
      sagaSel.appendChild(opt);
    });
    el("req_saga").value = reqs.saga || "";

    // Prior form select
    const prevSel = el("req_prev_form_select");
    prevSel.innerHTML = `<option value="">— Nenhuma forma prévia exigida —</option>`;
    (treeObj.formas || []).forEach((pf) => {
      if (pf.id !== form.id) {
        const opt = document.createElement("option");
        opt.value = pf.id;
        opt.textContent = pf.nome || pf.id;
        if (reqs.forma_previa === pf.id) opt.selected = true;
        prevSel.appendChild(opt);
      }
    });
    el("req_prev_form").value = reqs.forma_previa || "";

    // Incompatible tags
    renderIncompatibleTags(reqs.incompativel_com || []);
  }

  function renderIncompatibleTags(incompList) {
    const container = el("incompatibleTagsContainer");
    container.innerHTML = "";
    incompList.forEach((id) => {
      const tag = document.createElement("span");
      tag.className = "badge";
      tag.style.background = "rgba(244,63,94,0.2)";
      tag.style.border = "1px solid rgba(244,63,94,0.4)";
      tag.style.color = "#FDA4AF";
      tag.style.display = "inline-flex";
      tag.style.alignItems = "center";
      tag.style.gap = "4px";
      tag.innerHTML = `<span>${escapeHtml(id)}</span><button type="button" style="background:transparent; border:none; color:#FDA4AF; cursor:pointer; font-size:10px;">✕</button>`;

      tag.querySelector("button").addEventListener("click", () => {
        const nextList = incompList.filter((x) => x !== id);
        saveFieldChange("requisitos", "incompativel_com", nextList);
        renderIncompatibleTags(nextList);
      });
      container.appendChild(tag);
    });
  }

  // ==================== TWO-WAY DATA BINDING ====================

  function bindInputEvents() {
    // Stage Quick Nav Dropdown
    el("stageQuickSelect")?.addEventListener("change", (e) => {
      selectForm(state.selectedRace, state.selectedTree, e.target.value);
    });

    // Tabs Switcher
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));

        btn.classList.add("active");
        const tab = btn.dataset.tab;
        state.activeTab = tab;
        if (tab === "stats") el("tabPanelStats")?.classList.add("active");
        if (tab === "visual") el("tabPanelVisual")?.classList.add("active");
        if (tab === "reqs") el("tabPanelReqs")?.classList.add("active");
      });
    });

    // Inputs change listeners for Tab 1 (Stats & Drains)
    const statsInputs = [
      "inpTp", "inpSkillLvl", "chkBuyMaster", "inpMasterSelect",
      "mult_str", "mult_pwr", "mult_def", "mult_skp", "mult_spd", "mult_atk_spd",
      "mult_stm", "mult_vit", "mult_ene", "dr_ki", "dr_stm", "dr_hp", "dr_stm_hit",
      "dr_stack_mult", "chkStackable", "mst_max", "mst_instant", "mst_hit_dealt",
      "mst_hit_rcv", "mst_passive", "mst_cost_mult", "mst_stat_mult",
    ];

    statsInputs.forEach((id) => {
      const inputEl = el(id);
      if (!inputEl) return;
      inputEl.addEventListener("input", () => {
        syncActiveFormFromDOM();
        recalculateStatsAndBars();
      });
      inputEl.addEventListener("change", () => {
        persistFormUpdateToServer();
      });
    });

    // Base attributes inputs (Column 2)
    ["attrStr", "attrDef", "attrSpd", "attrPwr", "attrSkp", "attrEne"].forEach((id) => {
      el(id)?.addEventListener("input", recalculateStatsAndBars);
    });

    // Color Pickers <-> Hex Inputs 2-Way Sync
    const colorPairs = [
      ["visAuraColorPicker", "visAuraHex"],
      ["visHairColorPicker", "visHairHex"],
      ["visSecondaryHairColorPicker", "visSecondaryHairHex"],
      ["visSkinColorPicker", "visSkinHex"],
      ["visEye1ColorPicker", "visEye1Hex"],
      ["visEye2ColorPicker", "visEye2Hex"],
      ["visLightningColorPicker", "visLightningHex"],
      ["visCloakColorPicker", "visCloakHex"],
    ];

    colorPairs.forEach(([pickerId, hexId]) => {
      const picker = el(pickerId);
      const hexInput = el(hexId);
      if (!picker || !hexInput) return;

      picker.addEventListener("input", () => {
        hexInput.value = picker.value.toUpperCase();
        syncActiveFormFromDOM();
        updateThreeColorsAndTexture();
      });

      picker.addEventListener("change", persistFormUpdateToServer);

      hexInput.addEventListener("input", () => {
        let val = hexInput.value.trim();
        if (!val.startsWith("#") && /^[0-9A-Fa-f]{6}$/.test(val)) {
          val = "#" + val;
        }
        if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
          picker.value = val;
        }
        syncActiveFormFromDOM();
        updateThreeColorsAndTexture();
      });

      hexInput.addEventListener("change", persistFormUpdateToServer);
    });

    // Visual model selects & checkboxes
    ["visHairType", "visModelType", "visModelScale", "visEmissiveToggle", "visLightningToggle", "visCloakToggle", "visCloakOpacity"].forEach((id) => {
      const elem = el(id);
      if (!elem) return;
      elem.addEventListener("input", () => {
        syncActiveFormFromDOM();
        updateThreeColorsAndTexture();
      });
      elem.addEventListener("change", persistFormUpdateToServer);
    });

    // Presets DB Buttons
    document.querySelectorAll(".btn-color-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        applyDragonBallPreset(btn.dataset.preset);
      });
    });

    // Sagas & Requisitos inputs
    el("req_saga_select")?.addEventListener("change", (e) => {
      el("req_saga").value = e.target.value;
      syncActiveFormFromDOM();
      persistFormUpdateToServer();
    });

    el("req_prev_form_select")?.addEventListener("change", (e) => {
      el("req_prev_form").value = e.target.value;
      syncActiveFormFromDOM();
      persistFormUpdateToServer();
    });

    // Drain simulator buttons
    el("btnDrainSimPlay")?.addEventListener("click", toggleDrainSimulation);
    el("btnDrainSimReset")?.addEventListener("click", resetDrainSimulation);

    // 3D Viewport Controls
    el("btnThreeRotate")?.addEventListener("click", () => {
      state.three.autoRotate = !state.three.autoRotate;
      el("btnThreeRotate").classList.toggle("active", state.three.autoRotate);
    });

    el("btnThreeFront")?.addEventListener("click", () => {
      state.three.camera.position.set(0, 16, 44);
      state.three.controls.target.set(0, 15, 0);
    });

    el("btnThreeBack")?.addEventListener("click", () => {
      state.three.camera.position.set(0, 16, -44);
      state.three.controls.target.set(0, 15, 0);
    });

    el("btnThreeZoomIn")?.addEventListener("click", () => {
      state.three.camera.position.multiplyScalar(0.85);
    });

    el("btnThreeZoomOut")?.addEventListener("click", () => {
      state.three.camera.position.multiplyScalar(1.15);
    });

    el("btnThreeReset")?.addEventListener("click", () => {
      state.three.camera.position.set(0, 16, 44);
      state.three.controls.target.set(0, 15, 0);
      state.three.characterGroup.rotation.set(0, 0, 0);
    });

    el("btnThreeAuraToggle")?.addEventListener("click", () => {
      state.three.auraVisible = !state.three.auraVisible;
      el("btnThreeAuraToggle").classList.toggle("active", state.three.auraVisible);
      el("btnThreeAuraToggle").textContent = state.three.auraVisible ? "✨ Aura: ON" : "Aura: OFF";
    });

    // Staging Dock Toggle
    el("btnToggleStagingDock")?.addEventListener("click", () => {
      state.stagingOpen = !state.stagingOpen;
      el("stagingDockDrawer").style.display = state.stagingOpen ? "flex" : "none";
      el("stagingToggleIcon").textContent = state.stagingOpen ? "▲" : "▼";
    });

    // Stage Cloning / Auto-Scaling
    el("btnDuplicateStage")?.addEventListener("click", handleCloneStage);
    el("btnAutoScaleStage")?.addEventListener("click", handleAutoScaleStage);
    el("btnDeleteForm")?.addEventListener("click", handleDeleteForm);
  }

  function applyDragonBallPreset(presetKey) {
    if (!presetKey) return;
    const presets = {
      ssj: { aura: "#FFE600", hair: "#FFE600", hairType: "ssj1", sparks: false, cloak: false },
      ssj2: { aura: "#FFE600", hair: "#FFE600", hairType: "ssj2", sparks: true, sparkColor: "#38BDF8", cloak: false },
      ssj3: { aura: "#FFE600", hair: "#FFE600", hairType: "ssj3", sparks: true, sparkColor: "#FFE600", cloak: false },
      ssj4: { aura: "#EF4444", hair: "#000000", hairType: "ssj4", sparks: false, cloak: true, cloakColor: "#DC2626" },
      god: { aura: "#F43F5E", hair: "#F43F5E", hairType: "base", sparks: false, cloak: true, cloakColor: "#FB7185" },
      blue: { aura: "#0EA5E9", hair: "#0EA5E9", hairType: "ssj1", sparks: false, cloak: true, cloakColor: "#38BDF8" },
      rose: { aura: "#EC4899", hair: "#F472B6", hairType: "ssj1", sparks: false, cloak: true, cloakColor: "#F472B6" },
      ui: { aura: "#E2E8F0", hair: "#F8FAFC", hairType: "base", sparks: false, cloak: true, cloakColor: "#E2E8F0" },
      ue: { aura: "#A855F7", hair: "#9333EA", hairType: "ssj2", sparks: true, sparkColor: "#C084FC", cloak: true, cloakColor: "#7E22CE" },
      beast: { aura: "#A855F7", hair: "#E2E8F0", hairType: "beast", sparks: true, sparkColor: "#C084FC", cloak: true, cloakColor: "#A855F7" },
      legendary: { aura: "#22C55E", hair: "#4ADE80", hairType: "ssj1", sparks: true, sparkColor: "#22C55E", cloak: true, cloakColor: "#16A34A" },
    };

    const p = presets[presetKey];
    if (!p) return;

    el("visAuraHex").value = p.aura;
    el("visAuraColorPicker").value = p.aura;
    el("visHairHex").value = p.hair;
    el("visHairColorPicker").value = p.hair;
    el("visHairType").value = p.hairType;
    el("visLightningToggle").checked = p.sparks;
    if (p.sparkColor) {
      el("visLightningHex").value = p.sparkColor;
      el("visLightningColorPicker").value = p.sparkColor;
    }
    el("visCloakToggle").checked = p.cloak;
    if (p.cloakColor) {
      el("visCloakHex").value = p.cloakColor;
      el("visCloakColorPicker").value = p.cloakColor;
    }

    syncActiveFormFromDOM();
    updateThreeColorsAndTexture();
    persistFormUpdateToServer();
    showToast(`Preset Dragon Ball '${presetKey.toUpperCase()}' aplicado!`);
  }

  function syncActiveFormFromDOM() {
    if (!state.activeForm) return;

    state.activeForm.custo_tp_numerico = parseInt(el("inpTp")?.value || "0", 10);
    state.activeForm.nivel_habilidade = parseInt(el("inpSkillLvl")?.value || "1", 10);
    state.activeForm.comprar_no_mestre = Boolean(el("chkBuyMaster")?.checked);
    state.activeForm.mestre = el("inpMasterSelect")?.value || "";

    state.activeForm.multiplicadores_detalhados = {
      forca_str: parseFloat(el("mult_str")?.value || "1.0"),
      poder_ki_pwr: parseFloat(el("mult_pwr")?.value || "1.0"),
      defesa_def: parseFloat(el("mult_def")?.value || "1.0"),
      golpe_skp: parseFloat(el("mult_skp")?.value || "1.0"),
      velocidade_spd: parseFloat(el("mult_spd")?.value || "1.0"),
      velocidade_ataque: parseFloat(el("mult_atk_spd")?.value || "1.0"),
      estamina_stm: parseFloat(el("mult_stm")?.value || "1.0"),
      vitalidade_vit: parseFloat(el("mult_vit")?.value || "1.0"),
      energia_ene: parseFloat(el("mult_ene")?.value || "1.0"),
    };

    state.activeForm.drenos = {
      energia_ki: parseFloat(el("dr_ki")?.value || "0.0"),
      estamina: parseFloat(el("dr_stm")?.value || "0.0"),
      vida: parseFloat(el("dr_hp")?.value || "0.0"),
      mult_estamina_golpe: parseFloat(el("dr_stm_hit")?.value || "1.0"),
      acumulavel: Boolean(el("chkStackable")?.checked),
      mult_dreno_stack: parseFloat(el("dr_stack_mult")?.value || "2.0"),
    };

    state.activeForm.maestria = {
      maestria_maxima: parseFloat(el("mst_max")?.value || "100"),
      maestria_transf_instantanea: parseFloat(el("mst_instant")?.value || "40"),
      ganho_golpe_dado: parseFloat(el("mst_hit_dealt")?.value || "0.025"),
      ganho_dano_recebido: parseFloat(el("mst_hit_rcv")?.value || "0.025"),
      ganho_passivo_5s: parseFloat(el("mst_passive")?.value || "0.01"),
      mult_custo_maestria_max: parseFloat(el("mst_cost_mult")?.value || "0.75"),
      mult_status_maestria_max: parseFloat(el("mst_stat_mult")?.value || "1.0"),
    };

    state.activeForm.visual = {
      ...(state.activeForm.visual || {}),
      cor_aura: el("visAuraHex")?.value || "#FFE600",
      cor_cabelo: el("visHairHex")?.value || "#FFE600",
      cor_cabelo_secundaria: el("visSecondaryHairHex")?.value || "",
      tipo_cabelo: el("visHairType")?.value || "base",
      tipo_modelo: el("visModelType")?.value || "player",
      escala: parseFloat(el("visModelScale")?.value || "1.0"),
      brilho_emissivo: Boolean(el("visEmissiveToggle")?.checked),
      cor_pele: el("visSkinHex")?.value || "#FFDBAC",
      cor_olho_1: el("visEye1Hex")?.value || "#00FFCC",
      cor_olho_2: el("visEye2Hex")?.value || "#00FFCC",
      raios: {
        ativado: Boolean(el("visLightningToggle")?.checked),
        cor: el("visLightningHex")?.value || "#38BDF8",
      },
      manto: {
        ativado: Boolean(el("visCloakToggle")?.checked),
        cor: el("visCloakHex")?.value || "#FFE600",
        opacidade: parseFloat(el("visCloakOpacity")?.value || "0.45"),
      },
    };

    state.activeForm.requisitos = {
      ...(state.activeForm.requisitos || {}),
      nivel_dmz_minimo: parseInt(el("req_dmz_lvl")?.value || "1", 10),
      nivel_requisito: parseInt(el("req_lvl_req")?.value || "0", 10),
      saga: el("req_saga")?.value || "",
      forma_previa: el("req_prev_form")?.value || "",
    };

    state.dirty = true;
    el("statusDirtyPill").style.display = "inline-block";
  }

  let saveDebounceTimer = null;
  function persistFormUpdateToServer() {
    clearTimeout(saveDebounceTimer);
    saveDebounceTimer = setTimeout(async () => {
      if (!state.activeForm) return;
      try {
        const payload = {
          chave_forma: state.selectedFormKey,
          raca: state.selectedRace,
          arvore: state.selectedTree,
          id: state.activeForm.id,
          forma: state.activeForm,
        };
        const res = await apiPost("/api/update-form", payload);
        applyServerState(res);
      } catch (err) {
        showToast(`Erro ao salvar forma: ${err.message}`, true);
      }
    }, 400);
  }

  async function handleCloneStage() {
    if (!state.activeForm) return;
    try {
      const res = await apiPost("/api/form/duplicate", {
        race: state.selectedRace,
        tree: state.selectedTree,
        form_id: state.activeForm.id,
      });
      applyServerState(res);
      showToast("Estágio clonado com sucesso!");
    } catch (err) {
      showToast(`Erro ao clonar: ${err.message}`, true);
    }
  }

  async function handleAutoScaleStage() {
    if (!state.selectedTree) return;
    if (!confirm("Deseja aplicar escala automática (+15% mult / +10% drain) em todos os estágios deste grupo?")) return;
    try {
      const res = await apiPost("/api/form/auto-scale", {
        race: state.selectedRace,
        tree: state.selectedTree,
        mult_step_pct: 15.0,
        drain_step_pct: 10.0,
      });
      applyServerState(res);
      showToast("Escala automática aplicada na árvore!");
    } catch (err) {
      showToast(`Erro na escala: ${err.message}`, true);
    }
  }

  async function handleDeleteForm() {
    if (!state.activeForm) return;
    if (!confirm(`Tem certeza que deseja excluir '${state.activeForm.nome || state.activeForm.id}'? (Você pode desfazer com Ctrl+Z)`)) return;
    try {
      const res = await apiPost("/api/form/delete", {
        chave_forma: state.selectedFormKey,
        raca: state.selectedRace,
        arvore: state.selectedTree,
        id: state.activeForm.id,
      });
      applyServerState(res);
      showToast("Forma excluída!");
    } catch (err) {
      showToast(`Erro ao excluir: ${err.message}`, true);
    }
  }

  // ==================== STAGING DOCK & IMPORT/EXPORT ====================

  function renderStagingDock() {
    const list = el("stagingDockList");
    const countBadge = el("stagingBadgeCount");
    if (!list || !countBadge) return;

    countBadge.textContent = state.stagingDock.length;
    list.innerHTML = "";

    if (state.stagingDock.length === 0) {
      list.innerHTML = `<div style="text-align:center; padding:10px; color:var(--text-muted); font-size:11px;">A Gaveta de Importados está vazia.</div>`;
      return;
    }

    state.stagingDock.forEach((item, idx) => {
      const card = document.createElement("div");
      card.className = "staging-item-card";

      const hint = item.origin_hint ? `[${item.origin_hint.race || "?"} / ${item.origin_hint.tree || "?"}]` : "";
      card.innerHTML = `
        <div>
          <span style="font-weight:700; color:#38BDF8;">${escapeHtml(item.nome || item.id)}</span>
          <span class="text-xs text-muted" style="margin-left:6px;">${escapeHtml(hint)}</span>
        </div>
        <div style="display:flex; gap:6px;">
          <button class="btn btn-xs btn-cyan" data-action="allocate">Alocar ➔</button>
          <button class="btn btn-xs btn-danger" data-action="remove">✕</button>
        </div>
      `;

      card.querySelector('[data-action="allocate"]').addEventListener("click", () => {
        handleAllocateStagingItem(idx, item);
      });

      card.querySelector('[data-action="remove"]').addEventListener("click", async () => {
        try {
          const res = await apiPost("/api/staging/remove", { item_index: idx });
          state.stagingDock = res.staging_dock || [];
          renderStagingDock();
          showToast("Item removido da Gaveta!");
        } catch (err) {
          showToast(`Erro: ${err.message}`, true);
        }
      });

      list.appendChild(card);
    });
  }

  async function handleAllocateStagingItem(idx, item) {
    const rKey = prompt("Informe o ID da Raça de destino:", item.origin_hint?.race || "saiyan");
    if (!rKey) return;
    const tKey = prompt("Informe o ID da Árvore / Grupo de destino:", item.origin_hint?.tree || "customforms");
    if (!tKey) return;

    try {
      const res = await apiPost("/api/staging/allocate", {
        item_index: idx,
        race: rKey,
        tree: tKey,
        collision_policy: "rename",
      });
      applyServerState(res);
      showToast("Forma alocada na árvore com sucesso!");
    } catch (err) {
      showToast(`Erro ao alocar: ${err.message}`, true);
    }
  }

  // ==================== MODAIS: WIZARD, DIFF, REORDER, EXPORT ====================

  function bindModals() {
    // Open Wizard
    const openWz = () => {
      populateWizardOptions();
      el("wizardModal").style.display = "flex";
      setWizardStep(1);
    };
    el("btnOpenAddForm")?.addEventListener("click", openWz);
    el("btnWizardNewForm")?.addEventListener("click", openWz);

    el("btnCloseWizardHeader")?.addEventListener("click", () => (el("wizardModal").style.display = "none"));
    el("btnWizardCancel")?.addEventListener("click", () => (el("wizardModal").style.display = "none"));

    // Wizard Step Navigation
    let currentStep = 1;
    function setWizardStep(s) {
      currentStep = s;
      document.querySelectorAll(".wizard-step-node").forEach((n) => {
        const stepNum = parseInt(n.dataset.step, 10);
        n.classList.toggle("active", stepNum <= currentStep);
      });
      document.querySelectorAll(".wz-step-panel").forEach((p, idx) => {
        p.classList.toggle("active", idx + 1 === currentStep);
      });
      el("btnWizardPrev").style.visibility = currentStep > 1 ? "visible" : "hidden";
      el("btnWizardNext").style.display = currentStep < 4 ? "inline-block" : "none";
      el("btnWizardFinish").style.display = currentStep === 4 ? "inline-block" : "none";
    }

    el("btnWizardPrev")?.addEventListener("click", () => setWizardStep(currentStep - 1));
    el("btnWizardNext")?.addEventListener("click", () => setWizardStep(currentStep + 1));

    el("btnWizardFinish")?.addEventListener("click", async () => {
      const race = el("wzRaceSelect").value;
      const tree = el("wzTreeSelect").value;
      const id = el("wzFormId").value.trim().toLowerCase();
      const name = el("wzFormName").value.trim();

      if (!id || !name) {
        showToast("Preencha ID e Nome da forma!", true);
        return;
      }

      const payload = {
        raca: race,
        arvore: tree,
        id: id,
        nome: name,
        custo_tp: parseInt(el("wzTpCost").value || "0", 10),
        nivel_habilidade: parseInt(el("wzSkillSlot").value || "1", 10),
        multiplicadores_detalhados: {
          forca_str: parseFloat(el("wzStr").value || "1.0"),
          poder_ki_pwr: parseFloat(el("wzPwr").value || "1.0"),
          defesa_def: parseFloat(el("wzDef").value || "1.0"),
          golpe_skp: parseFloat(el("wzSkp").value || "1.0"),
          velocidade_spd: parseFloat(el("wzSpd").value || "1.0"),
          velocidade_ataque: parseFloat(el("wzAtkSpd").value || "1.0"),
        },
        drenos: {
          energia_ki: parseFloat(el("wzDrainKi").value || "0.0"),
          estamina: parseFloat(el("wzDrainStm").value || "0.0"),
          vida: parseFloat(el("wzDrainHp").value || "0.0"),
        },
        visual: {
          tipo_cabelo: el("wzHairType").value,
          cor_aura: el("wzAuraColor").value,
          cor_cabelo: el("wzHairColor").value,
          raios: { ativado: el("wzSparks").checked },
        },
        requisitos: {
          nivel_dmz_minimo: parseInt(el("wzDmzLvl").value || "1", 10),
          saga: el("wzSagaSelect").value,
          forma_previa: el("wzPrevSelect").value,
        },
      };

      try {
        const res = await apiPost("/api/form/add", payload);
        el("wizardModal").style.display = "none";
        applyServerState(res);
        selectForm(race, tree, id);
        showToast("Nova transformação criada com sucesso!");
      } catch (err) {
        showToast(`Erro ao criar: ${err.message}`, true);
      }
    });

    // Diff Visual Modal
    el("btnApplyModpack")?.addEventListener("click", async () => {
      try {
        const diffRes = await apiGet("/api/diff");
        renderDiffTable(diffRes.diff);
        el("diffModal").style.display = "flex";
      } catch (err) {
        showToast(`Erro ao calcular diff: ${err.message}`, true);
      }
    });

    el("btnCloseDiffHeader")?.addEventListener("click", () => (el("diffModal").style.display = "none"));
    el("btnCancelDiff")?.addEventListener("click", () => (el("diffModal").style.display = "none"));

    el("btnConfirmApplyModpack")?.addEventListener("click", async () => {
      try {
        const res = await apiPost("/api/apply-modpack", {});
        el("diffModal").style.display = "none";
        applyServerState(res);
        showToast(`Sucesso! ${res.arquivos_atualizados} arquivos gravados no Modpack com backup .zip!`);
      } catch (err) {
        showToast(`Erro ao aplicar: ${err.message}`, true);
      }
    });

    // Reorder Modal
    el("btnOpenReorderModal")?.addEventListener("click", () => {
      populateReorderList();
      el("reorderModal").style.display = "flex";
    });
    el("btnCloseReorderHeader")?.addEventListener("click", () => (el("reorderModal").style.display = "none"));
    el("btnCancelReorder")?.addEventListener("click", () => (el("reorderModal").style.display = "none"));
    el("btnApplyReorder")?.addEventListener("click", handleApplyReorder);

    // Export Modal
    el("btnExportSelective")?.addEventListener("click", () => {
      populateExportSelectionTree();
      el("exportModal").style.display = "flex";
    });
    el("btnCloseExportHeader")?.addEventListener("click", () => (el("exportModal").style.display = "none"));
    el("btnCopyExportClipboard")?.addEventListener("click", handleCopyExport);
    el("btnSaveExportJson")?.addEventListener("click", handleSaveExportFile);

    // Import Staging
    el("btnImportStaging")?.addEventListener("click", handleImportStagingPrompt);

    // Backups Folder
    el("btnOpenBackupsFolder")?.addEventListener("click", openBackupsFolder);
    el("btnOpenBackupsDirSettings")?.addEventListener("click", openBackupsFolder);

    // Settings Modal
    el("btnOpenSettings")?.addEventListener("click", () => (el("settingsModal").style.display = "flex"));
    el("btnHeaderCloseSettings")?.addEventListener("click", () => (el("settingsModal").style.display = "none"));
    el("btnCloseSettings")?.addEventListener("click", () => (el("settingsModal").style.display = "none"));
    el("btnBrowseFolder")?.addEventListener("click", async () => {
      const res = await apiPost("/api/browse-folder", {});
      if (res.path) el("inpModpackPath").value = res.path;
    });
    el("btnBrowseJson")?.addEventListener("click", async () => {
      const res = await apiPost("/api/browse-json", {});
      if (res.path) el("inpJsonPath").value = res.path;
    });
    el("btnSaveSettings")?.addEventListener("click", async () => {
      try {
        const res = await apiPost("/api/settings", {
          dmz_config_dir: el("inpModpackPath").value,
          desktop_json_path: el("inpJsonPath").value,
        });
        el("settingsModal").style.display = "none";
        applyServerState(res);
        showToast("Pastas atualizadas e catalog recarregado!");
      } catch (err) {
        showToast(`Erro: ${err.message}`, true);
      }
    });

    // Addons Modal
    el("btnOpenAddons")?.addEventListener("click", async () => {
      el("addonsModal").style.display = "flex";
      await reloadAddonsTable();
    });
    el("btnHeaderCloseAddons")?.addEventListener("click", () => (el("addonsModal").style.display = "none"));
    el("btnCloseAddons")?.addEventListener("click", () => (el("addonsModal").style.display = "none"));
    el("btnOpenModsFolder")?.addEventListener("click", () => apiPost("/api/addons/open-folder", {}));
    el("btnReloadAddons")?.addEventListener("click", () => reloadAddonsTable(true));

    // Batch Balancing Modal
    el("btnOpenBatch")?.addEventListener("click", () => (el("batchModal").style.display = "flex"));
    el("btnHeaderCloseBatch")?.addEventListener("click", () => (el("batchModal").style.display = "none"));
    el("btnCloseBatch")?.addEventListener("click", () => (el("batchModal").style.display = "none"));

    // Canonical Balance Button
    el("btnCanonicalBalance")?.addEventListener("click", async () => {
      if (!confirm("Deseja aplicar o balanceamento canônico em todas as raças?")) return;
      try {
        const res = await apiPost("/api/canonical-balance", {});
        applyServerState(res);
        showToast("Balanceamento canônico aplicado em todas as raças!");
      } catch (err) {
        showToast(`Erro: ${err.message}`, true);
      }
    });

    // Undo / Redo
    el("btnUndo")?.addEventListener("click", async () => {
      const res = await apiPost("/api/undo", {});
      applyServerState(res);
    });
    el("btnRedo")?.addEventListener("click", async () => {
      const res = await apiPost("/api/redo", {});
      applyServerState(res);
    });

    // Save JSON Only
    el("btnSaveJson")?.addEventListener("click", async () => {
      try {
        const res = await apiPost("/api/save-json", {});
        applyServerState(res);
        showToast("Catálogo salvo no JSON!");
      } catch (err) {
        showToast(`Erro ao salvar JSON: ${err.message}`, true);
      }
    });

    // Reload Modpack
    el("btnReloadModpack")?.addEventListener("click", async () => {
      try {
        const res = await apiPost("/api/reload", { source: "modpack" });
        applyServerState(res);
        showToast("Modpack recarregado do disco!");
      } catch (err) {
        showToast(`Erro ao recarregar: ${err.message}`, true);
      }
    });
  }

  function populateWizardOptions() {
    const rSel = el("wzRaceSelect");
    const rSelect = rSel;
    if (rSelect) {
      if (state.selectedRace === "universal") {
        rSelect.disabled = true;
      } else {
        rSelect.disabled = false;
      }
    }
    rSel.innerHTML = "";
    Object.values(state.catalog.racas || {}).forEach((r) => {
      const opt = document.createElement("option");
      opt.value = r.id_raca;
      opt.textContent = r.nome_exibicao;
      rSel.appendChild(opt);
    });

    const updateTrees = () => {
      const rKey = rSel.value;
      const tSel = el("wzTreeSelect");
      tSel.innerHTML = "";
      const rObj = state.catalog.racas?.[rKey];
      if (rObj) {
        Object.keys(rObj.arvores_de_transformacao || {}).forEach((tKey) => {
          const opt = document.createElement("option");
          opt.value = tKey;
          opt.textContent = tKey;
          tSel.appendChild(opt);
        });
      }
    };
    rSel.onchange = updateTrees;
    updateTrees();

    // Sagas dropdown
    const sSel = el("wzSagaSelect");
    sSel.innerHTML = `<option value="">— Nenhuma saga exigida —</option>`;
    (state.catalog.opcoes_sagas || []).forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s.id;
      opt.textContent = `${s.categoria}: ${s.nome}`;
      sSel.appendChild(opt);
    });
  }

  function renderDiffTable(diff) {
    const tbody = el("diffTableBody");
    tbody.innerHTML = "";

    const added = diff.added || [];
    const modified = diff.modified || [];
    const deleted = diff.deleted || [];

    const total = added.length + modified.length + deleted.length;
    el("diffStatsCount").textContent = `${total} alterações detectadas: ${added.length} novas, ${modified.length} modificadas, ${deleted.length} excluídas`;

    if (total === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:20px; color:var(--text-muted);">Nenhuma alteração detectada em relação ao modpack lido do disco.</td></tr>`;
      return;
    }

    modified.forEach((item) => {
      const row = document.createElement("tr");
      row.className = "diff-row-modified";
      const changesHtml = (item.changes || []).map((c) => {
        return `<div><b style="color:#94A3B8;">${escapeHtml(c.field)}:</b> <span style="color:#FDA4AF; text-decoration:line-through;">${escapeHtml(JSON.stringify(c.old_value))}</span> ➔ <span style="color:#34D399; font-weight:700;">${escapeHtml(JSON.stringify(c.new_value))}</span></div>`;
      }).join("");

      row.innerHTML = `
        <td><span class="badge" style="background:#0284C7; color:#FFF;">Modificada</span></td>
        <td><b>${escapeHtml(item.form_name || item.form_id)}</b></td>
        <td>${escapeHtml(item.race)} / ${escapeHtml(item.tree)}</td>
        <td style="font-size:11px;">${changesHtml}</td>
      `;
      tbody.appendChild(row);
    });

    added.forEach((item) => {
      const row = document.createElement("tr");
      row.className = "diff-row-added";
      row.innerHTML = `
        <td><span class="badge" style="background:#10B981; color:#FFF;">Nova Forma</span></td>
        <td><b>${escapeHtml(item.form_name || item.form_id)}</b></td>
        <td>${escapeHtml(item.race)} / ${escapeHtml(item.tree)}</td>
        <td style="color:#34D399;">Forma adicionada na sessão</td>
      `;
      tbody.appendChild(row);
    });

    deleted.forEach((item) => {
      const row = document.createElement("tr");
      row.className = "diff-row-deleted";
      row.innerHTML = `
        <td><span class="badge" style="background:#F43F5E; color:#FFF;">Excluída</span></td>
        <td><b>${escapeHtml(item.form_name || item.form_id)}</b></td>
        <td>${escapeHtml(item.race)} / ${escapeHtml(item.tree)}</td>
        <td style="color:#FDA4AF;">Forma removida na sessão</td>
      `;
      tbody.appendChild(row);
    });
  }

  function populateReorderList() {
    const list = el("reorderList");
    list.innerHTML = "";
    if (!state.selectedTree || !state.catalog) return;

    let forms = [];
    if (state.selectedRace === "universal") {
      forms = state.catalog.formas_universais_e_stack?.[state.selectedTree]?.formas || [];
    } else {
      forms = state.catalog.racas?.[state.selectedRace]?.arvores_de_transformacao?.[state.selectedTree]?.formas || [];
    }

    forms.forEach((f, idx) => {
      const row = document.createElement("div");
      row.className = "reorder-item-row";
      row.dataset.formId = f.id;
      row.innerHTML = `
        <div>
          <span style="font-weight:700; color:#38BDF8; margin-right:8px;">#${f.nivel_habilidade || idx + 1}</span>
          <span>${escapeHtml(f.nome || f.id)}</span>
        </div>
        <div style="display:flex; gap:4px;">
          <button class="btn btn-xs" data-dir="up" ${idx === 0 ? "disabled" : ""}>⬆️</button>
          <button class="btn btn-xs" data-dir="down" ${idx === forms.length - 1 ? "disabled" : ""}>⬇️</button>
        </div>
      `;

      row.querySelector('[data-dir="up"]').addEventListener("click", () => {
        if (idx > 0) {
          const item = row;
          item.parentNode.insertBefore(item, item.previousElementSibling);
        }
      });

      row.querySelector('[data-dir="down"]').addEventListener("click", () => {
        if (row.nextElementSibling) {
          row.parentNode.insertBefore(row.nextElementSibling, row);
        }
      });

      list.appendChild(row);
    });
  }

  async function handleApplyReorder() {
    const list = el("reorderList");
    const newOrder = Array.from(list.children).map((c) => c.dataset.formId);
    const updateSkills = el("chkReorderSequentialSkill").checked;

    try {
      const res = await apiPost("/api/form/reorder", {
        race: state.selectedRace,
        tree: state.selectedTree,
        new_order: newOrder,
        update_skill_levels: updateSkills,
      });
      el("reorderModal").style.display = "none";
      applyServerState(res);
      showToast("Nova ordem salva com sucesso!");
    } catch (err) {
      showToast(`Erro ao reordenar: ${err.message}`, true);
    }
  }

  function populateExportSelectionTree() {
    const container = el("exportSelectionTree");
    container.innerHTML = "";

    Object.entries(state.catalog.racas || {}).forEach(([rKey, rObj]) => {
      const rBox = document.createElement("div");
      rBox.style.marginBottom = "6px";
      rBox.innerHTML = `
        <label style="display:flex; align-items:center; gap:6px; font-weight:700; cursor:pointer;">
          <input type="checkbox" class="export-race-chk" data-race="${rKey}" checked />
          <span>${escapeHtml(rObj.nome_exibicao)} (${rObj.total_formas || 0} formas)</span>
        </label>
      `;
      container.appendChild(rBox);
    });
  }

  async function handleCopyExport() {
    const selections = [];
    document.querySelectorAll(".export-race-chk:checked").forEach((chk) => {
      selections.push({ race: chk.dataset.race });
    });

    try {
      const res = await apiPost("/api/export/selective", { selections });
      if (res.package_json) {
        await navigator.clipboard.writeText(res.package_json);
        showToast("Pacote JSON copiado para a Área de Transferência!");
        el("exportModal").style.display = "none";
      }
    } catch (err) {
      showToast(`Erro ao exportar: ${err.message}`, true);
    }
  }

  async function handleSaveExportFile() {
    const selections = [];
    document.querySelectorAll(".export-race-chk:checked").forEach((chk) => {
      selections.push({ race: chk.dataset.race });
    });

    try {
      const res = await apiPost("/api/export/selective", { selections });
      const blob = new Blob([res.package_json], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `kiforge_export_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("Arquivo JSON exportado!");
      el("exportModal").style.display = "none";
    } catch (err) {
      showToast(`Erro ao exportar arquivo: ${err.message}`, true);
    }
  }

  async function handleImportStagingPrompt() {
    let raw = "";
    try {
      raw = await navigator.clipboard.readText();
    } catch {
      raw = prompt("Cole o JSON da transformação ou pacote exportado aqui:");
    }
    if (!raw) return;

    try {
      const res = await apiPost("/api/staging/import", { raw_text: raw });
      state.stagingDock = res.staging_dock || [];
      renderStagingDock();
      state.stagingOpen = true;
      el("stagingDockDrawer").style.display = "flex";
      showToast(`${res.imported_count} transformação(ões) importada(s) para a Gaveta!`);
    } catch (err) {
      showToast(`Erro ao importar: ${err.message}`, true);
    }
  }

  async function openBackupsFolder() {
    try {
      const res = await apiPost("/api/backups/open-folder", {});
      if (res.ok) {
        showToast(`Pasta de backups aberta: ${res.path}`);
      } else {
        showToast(`Pasta de backups em: ${res.path}`);
      }
    } catch (err) {
      showToast(`Erro ao abrir backups: ${err.message}`, true);
    }
  }

  async function reloadAddonsTable(force = false) {
    const tbody = el("addonsTableBody");
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:15px; color:var(--text-muted);">Escanear pasta mods...</td></tr>`;
    try {
      const res = await apiGet(`/api/addons?force=${force ? "1" : "0"}`);
      const addons = res.addons || [];
      tbody.innerHTML = "";

      if (addons.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:15px; color:var(--text-muted);">Nenhum mod DMZ encontrado na pasta mods.</td></tr>`;
        return;
      }

      addons.forEach((add) => {
        const row = document.createElement("tr");
        const statusBadge = add.enabled
          ? `<span class="badge" style="background:#10B981; color:#FFF;">Ativado</span>`
          : `<span class="badge" style="background:#64748B; color:#FFF;">Desativado (.disabled)</span>`;

        row.innerHTML = `
          <td>${statusBadge}</td>
          <td><b>${escapeHtml(add.display_name)}</b></td>
          <td>${escapeHtml(add.version)}</td>
          <td>${escapeHtml(add.authors)}</td>
          <td style="font-family:var(--font-mono); font-size:11px;">${escapeHtml(add.filename)}</td>
          <td>${add.size_mb} MB</td>
        `;

        row.style.cursor = "pointer";
        row.title = "Clique para alternar (ativar/desativar)";
        row.addEventListener("click", async () => {
          try {
            await apiPost("/api/addons/toggle", {
              filename: add.filename,
              enabled: !add.enabled,
            });
            await reloadAddonsTable(true);
            showToast(`Mod '${add.display_name}' ${!add.enabled ? "ativado" : "desativado"}!`);
          } catch (err) {
            showToast(`Erro ao alternar mod: ${err.message}`, true);
          }
        });

        tbody.appendChild(row);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:15px; color:#F43F5E;">Erro: ${escapeHtml(err.message)}</td></tr>`;
    }
  }

  // ==================== INITIALIZATION & STATE LOAD ====================

  function applyServerState(data) {
    if (!data) return;
    state.catalog = data.catalog || state.catalog;
    if (data.source) state.source = data.source;
    state.dirty = Boolean(data.dirty);
    state.canUndo = Boolean(data.can_undo);
    state.canRedo = Boolean(data.can_redo);
    state.stagingDock = data.staging_dock || state.stagingDock;
    state.dmzConfigDir = data.dmz_config_dir || state.dmzConfigDir;
    state.desktopJson = data.desktop_json || state.desktopJson;

    // Update Topbar
    el("statusDirtyPill").style.display = state.dirty ? "inline-block" : "none";
    el("btnUndo").disabled = !state.canUndo;
    el("btnRedo").disabled = !state.canRedo;

    const sourcePill = el("statusSourcePill");
    if (state.source === "modpack") {
      sourcePill.className = "status-pill modpack";
      sourcePill.textContent = "Modpack Conectado";
    } else {
      sourcePill.className = "status-pill json";
      sourcePill.textContent = "Arquivo JSON";
    }

    el("statusCounts").textContent = `${state.catalog.total_racas || 0} raças · ${state.catalog.total_transformacoes || 0} transformações`;
    el("statusPathInfo").textContent = state.dmzConfigDir ? state.dmzConfigDir.split(/[\\/]/).slice(-3).join("/") : "";

    // Render Components
    renderRaceDropdown();
    renderTreeAccordion();
    renderStagingDock();

    // Auto-select first form if none selected
    if (!state.selectedFormKey) {
      const firstRace = Object.values(state.catalog.racas || {})[0];
      if (firstRace) {
        const firstTreeKey = Object.keys(firstRace.arvores_de_transformacao || {})[0];
        const firstTree = firstRace.arvores_de_transformacao?.[firstTreeKey];
        if (firstTree && firstTree.formas && firstTree.formas.length > 0) {
          selectForm(firstRace.id_raca, firstTreeKey, firstTree.formas[0].id);
        }
      }
    }
  }

  // Bootstrapping
  window.addEventListener("DOMContentLoaded", async () => {
    try {
      initThreePreview();
      bindInputEvents();
      bindModals();

      // Keyboard shortcuts
      window.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key === "z") {
          e.preventDefault();
          if (state.canUndo) el("btnUndo")?.click();
        } else if (e.ctrlKey && e.key === "y") {
          e.preventDefault();
          if (state.canRedo) el("btnRedo")?.click();
        } else if (e.ctrlKey && e.key === "s") {
          e.preventDefault();
          el("btnSaveJson")?.click();
        }
      });

      // Fetch state
      const stateData = await apiGet("/api/state");
      applyServerState(stateData);
    } catch (err) {
      console.error("Erro na inicialização:", err);
      showToast(`Erro ao carregar estado: ${err.message}`, true);
    }
  });
})();
