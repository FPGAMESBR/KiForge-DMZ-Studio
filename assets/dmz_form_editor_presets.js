(() => {
  "use strict";

  const el = (id) => document.getElementById(id);

  function buildFormLookup(catalog, currentRaceKey) {
    const byRef = new Map();
    const raceItems = [];
    const univItems = [];
    const usedIncompRefs = new Set();

    if (!catalog) return { byRef, raceItems, univItems, extraItems: [] };

    Object.entries(catalog.formas_universais_e_stack || {}).forEach(([gKey, gObj]) => {
      (gObj.formas || []).forEach((f) => {
        const ref = `${gKey}.${f.id}`;
        const label = `${f.nome} [${ref}]`;
        byRef.set(ref, label);
        univItems.push({ ref, label });
        ((f.requisitos && f.requisitos.incompativel_com) || []).forEach((x) =>
          usedIncompRefs.add(x)
        );
      });
    });

    Object.entries(catalog.racas || {}).forEach(([rKey, rObj]) => {
      Object.entries(rObj.arvores_de_transformacao || {}).forEach(([tKey, tObj]) => {
        (tObj.formas || []).forEach((f) => {
          const ref = `${tKey}.${f.id}`;
          const label = `${f.nome} [${ref}]`;
          if (!byRef.has(ref) || rKey === currentRaceKey) {
            byRef.set(ref, label);
          }
          if (rKey === currentRaceKey) {
            byRef.set(f.id, `${f.nome} [${f.id}]`);
            raceItems.push({ ref, id: f.id, label });
          }
          ((f.requisitos && f.requisitos.incompativel_com) || []).forEach((x) =>
            usedIncompRefs.add(x)
          );
        });
      });
    });

    const raceRefSet = new Set(raceItems.map((i) => i.ref));
    const univRefSet = new Set(univItems.map((i) => i.ref));
    const extraItems = [];
    Array.from(usedIncompRefs)
      .sort()
      .forEach((ref) => {
        if (!raceRefSet.has(ref) && !univRefSet.has(ref)) {
          extraItems.push({ ref, label: byRef.get(ref) || ref });
        }
      });

    return { byRef, raceItems, univItems, extraItems };
  }

  function parseCsvList(raw) {
    return String(raw || "")
      .split(",")
      .map((x) => x.trim())
      .filter(Boolean);
  }

  function renderTagPills(containerId, values, byRef, isIncomp, emptyText, onRemove) {
    const box = el(containerId);
    box.textContent = "";
    if (!values.length) {
      const span = document.createElement("span");
      span.className = "tag-empty";
      span.textContent = emptyText;
      box.appendChild(span);
      return;
    }

    values.forEach((val) => {
      const pill = document.createElement("span");
      pill.className = isIncomp ? "tag-pill incomp" : "tag-pill";
      const txt = document.createElement("span");
      txt.textContent = byRef.get(val) || val;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.title = "Remover";
      btn.textContent = "×";
      btn.addEventListener("click", () => onRemove(val));
      pill.appendChild(txt);
      pill.appendChild(btn);
      box.appendChild(pill);
    });
  }

  function appendOptGroup(selectEl, title, items, skipSelfRef) {
    const valid = items.filter((it) => it.ref !== skipSelfRef);
    if (!valid.length) return;
    const grp = document.createElement("optgroup");
    grp.label = title;
    valid.forEach((it) => {
      const opt = document.createElement("option");
      opt.value = it.ref;
      opt.textContent = it.label;
      grp.appendChild(opt);
    });
    selectEl.appendChild(grp);
  }

  function populateSagaQuestsSelect(sagaObj, selectedVal) {
    const wrap = el("sagaQuestWrap");
    const qSel = el("selSagaQuest");
    qSel.textContent = "";
    if (!sagaObj) {
      wrap.style.display = "none";
      return;
    }
    wrap.style.display = "flex";
    (sagaObj.quests || []).forEach((q) => {
      const opt = document.createElement("option");
      opt.value = q.valor;
      const star = q.usado ? " ★" : "";
      opt.textContent =
        q.numero > 0
          ? `Cap. ${q.numero} — ${q.titulo}${star} (${q.valor})`
          : `${q.titulo} (${q.valor})`;
      qSel.appendChild(opt);
    });
    if (selectedVal && Array.from(qSel.options).some((o) => o.value === selectedVal)) {
      qSel.value = selectedVal;
    } else if (qSel.options.length > 0) {
      const preferred = (sagaObj.quests || []).find((q) => q.usado) || sagaObj.quests[0];
      qSel.value = preferred.valor;
    }
  }

  function syncCard5Presets(catalog, row, markDirty) {
    if (!catalog || !row) return;
    const sagas = catalog.opcoes_sagas || [];
    const sagaMap = new Map(sagas.map((s) => [s.id, s]));

    // 1. Populate Saga Group Select
    const sGroupSel = el("selSagaGroup");
    sGroupSel.textContent = "";
    const freeOpt = document.createElement("option");
    freeOpt.value = "";
    freeOpt.textContent = "🔓 Sem Saga — Desbloqueio Livre";
    sGroupSel.appendChild(freeOpt);

    sagas.forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s.id;
      opt.textContent = `${s.nome} [${s.id}]`;
      sGroupSel.appendChild(opt);
    });

    const curSaga = String((row.form.requisitos && row.form.requisitos.saga) || "").trim();
    el("rq_saga").value = curSaga;
    if (!curSaga) {
      sGroupSel.value = "";
      populateSagaQuestsSelect(null, "");
    } else {
      const sagaId = curSaga.includes(":") ? curSaga.split(":", 1)[0] : curSaga;
      if (!sagaMap.has(sagaId)) {
        const customObj = {
          id: sagaId,
          nome: `Personalizada (${sagaId})`,
          quests: [{ valor: curSaga, numero: 0, titulo: curSaga, usado: true }],
        };
        sagaMap.set(sagaId, customObj);
        const opt = document.createElement("option");
        opt.value = sagaId;
        opt.textContent = customObj.nome;
        sGroupSel.appendChild(opt);
      }
      sGroupSel.value = sagaId;
      populateSagaQuestsSelect(sagaMap.get(sagaId), curSaga);
    }

    sGroupSel.onchange = () => {
      const chosenGroup = sGroupSel.value;
      if (!chosenGroup) {
        el("rq_saga").value = "";
        populateSagaQuestsSelect(null, "");
      } else {
        const sObj = sagaMap.get(chosenGroup);
        populateSagaQuestsSelect(sObj, "");
        el("rq_saga").value = el("selSagaQuest").value;
      }
      markDirty();
    };

    el("selSagaQuest").onchange = () => {
      el("rq_saga").value = el("selSagaQuest").value;
      markDirty();
    };

    // 2. Populate Prev Form & Incompatible Form Presets
    const selfRef = `${row.arvore}.${row.form.id}`;
    const lookup = buildFormLookup(catalog, row.raca);

    const prevSel = el("selPrevFormPreset");
    prevSel.textContent = "";
    const pPlaceholder = document.createElement("option");
    pPlaceholder.value = "";
    pPlaceholder.textContent = "+ Escolher forma prévia na lista...";
    prevSel.appendChild(pPlaceholder);
    if (row.escopo === "raca") {
      appendOptGroup(prevSel, `Formas de ${row.racaNome}`, lookup.raceItems, selfRef);
    }
    appendOptGroup(prevSel, "Formas Universais / Stack", lookup.univItems, selfRef);

    const incompSel = el("selIncompFormPreset");
    incompSel.textContent = "";
    const iPlaceholder = document.createElement("option");
    iPlaceholder.value = "";
    iPlaceholder.textContent = "+ Adicionar forma incompatível da lista...";
    incompSel.appendChild(iPlaceholder);
    appendOptGroup(incompSel, "Formas Universais / Stack", lookup.univItems, selfRef);
    if (row.escopo === "raca") {
      appendOptGroup(incompSel, `Formas de ${row.racaNome}`, lookup.raceItems, selfRef);
    }
    appendOptGroup(incompSel, "Outras Formas do Modpack", lookup.extraItems, selfRef);

    const refreshPrevPills = () => {
      const vals = parseCsvList(el("rq_prev").value);
      renderTagPills(
        "prevFormTags",
        vals,
        lookup.byRef,
        false,
        "🔓 Nenhuma forma prévia exigida",
        (rem) => {
          el("rq_prev").value = vals.filter((x) => x !== rem).join(",");
          refreshPrevPills();
          markDirty();
        }
      );
    };

    const refreshIncompPills = () => {
      const vals = parseCsvList(el("rq_incomp").value);
      renderTagPills(
        "incompFormTags",
        vals,
        lookup.byRef,
        true,
        "🔓 Nenhuma incompatibilidade definida",
        (rem) => {
          el("rq_incomp").value = vals.filter((x) => x !== rem).join(", ");
          refreshIncompPills();
          markDirty();
        }
      );
    };

    prevSel.onchange = () => {
      const v = prevSel.value;
      if (!v) return;
      const cur = parseCsvList(el("rq_prev").value);
      if (!cur.includes(v)) {
        el("rq_prev").value = [...cur, v].join(",");
        refreshPrevPills();
        markDirty();
      }
      prevSel.value = "";
    };

    incompSel.onchange = () => {
      const v = incompSel.value;
      if (!v) return;
      const cur = parseCsvList(el("rq_incomp").value);
      if (!cur.includes(v)) {
        el("rq_incomp").value = [...cur, v].join(", ");
        refreshIncompPills();
        markDirty();
      }
      incompSel.value = "";
    };

    el("btnClearPrevForm").onclick = () => {
      el("rq_prev").value = "";
      refreshPrevPills();
      markDirty();
    };

    el("btnClearIncomp").onclick = () => {
      el("rq_incomp").value = "";
      refreshIncompPills();
      markDirty();
    };

    el("btnClearSaga").onclick = () => {
      el("rq_saga").value = "";
      sGroupSel.value = "";
      populateSagaQuestsSelect(null, "");
      markDirty();
    };

    refreshPrevPills();
    refreshIncompPills();
  }

  function wireSettingsModal({ getMeta, apiPost, onStateLoaded, showToast, commitPending }) {
    el("btnOpenSettings").addEventListener("click", () => {
      const meta = getMeta();
      el("inpModpackPath").value = meta.dmzConfigDir || "";
      el("inpJsonPath").value = meta.desktopJson || "";
      el("settingsModal").classList.add("open");
    });

    el("btnCloseSettings").addEventListener("click", () => {
      el("settingsModal").classList.remove("open");
    });

    el("btnBrowseFolder").addEventListener("click", async () => {
      try {
        const res = await apiPost("/api/browse-folder", {});
        if (res.selected_path) {
          el("inpModpackPath").value = res.selected_path;
        }
      } catch (err) {
        showToast(err.message, true);
      }
    });

    if (el("btnBrowseJson")) {
      el("btnBrowseJson").addEventListener("click", async () => {
        try {
          const res = await apiPost("/api/browse-json", {});
          if (res.selected_path) {
            el("inpJsonPath").value = res.selected_path;
          }
        } catch (err) {
          showToast(err.message, true);
        }
      });
    }

    el("btnResetDefaultPath").addEventListener("click", async () => {
      el("inpModpackPath").value = "";
      el("inpJsonPath").value = "";
      try {
        const data = await apiPost("/api/settings", { clear_paths: true });
        onStateLoaded(data);
        showToast("Caminhos limpos! Os campos estão em branco.");
      } catch (err) {
        showToast(err.message, true);
      }
    });

    el("btnSaveSettings").addEventListener("click", async () => {
      try {
        await commitPending();
        const dmzPath = el("inpModpackPath").value.trim();
        const jsonPath = el("inpJsonPath").value.trim();
        const data = await apiPost("/api/settings", {
          dmz_config_dir: dmzPath,
          desktop_json_path: jsonPath,
        });
        el("settingsModal").classList.remove("open");
        onStateLoaded(data);
        const targetLabel = data.dmz_config_dir || data.desktop_json || "Configuração";
        showToast(`Carregado com sucesso: ${targetLabel}`);
      } catch (err) {
        showToast(err.message, true);
      }
    });
  }

  window.DMZPresets = {
    syncCard5Presets,
    wireSettingsModal,
  };
})();
