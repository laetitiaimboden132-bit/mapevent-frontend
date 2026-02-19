// ============================================================
// filters.js
// Filtre explorateur multi-colonnes (toggleLeftPanel, loadExplorerTree, applyExplorerFilter, toggleCategory)
// Extrait de map_logic.js (lignes 8746-10170)
// ============================================================

// FILTRE EXPLORATEUR "LEADER ONE" – MULTI-COLONNES + DATES
// ============================================
let explorerOpen = false;
let explorerPath = [];
let selectedCategories = [];
let explorerTree = null;

// filtres dates (mode event)
let timeFilter = null; // null | 'range' (les boutons rapides ajoutent maintenant à selectedDates)
let dateRangeStart = null;
let dateRangeEnd = null;
let selectedDates = []; // Pour cumuler : ['today', 'tomorrow', 'weekend', etc.]

// surcharge toggleLeftPanel
function toggleLeftPanel() {
  explorerOpen = !explorerOpen;
  const panel = document.getElementById("left-panel");
  if (!explorerOpen) {
    panel.style.display = "none";
    return;
  }
  // Ouvrir le panneau et charger l'arbre correspondant au mode actuel
  panel.style.display = "block";
  console.log(`🔍 Ouverture du filtre pour le mode: ${currentMode}`);
  loadExplorerTree(); // Charge automatiquement le bon arbre selon currentMode
}

// charger l'arbre depuis /trees/*.json
function loadExplorerTree() {
  let file = "";
  if (currentMode === "event") file = "trees/events_tree.json";
  if (currentMode === "booking") file = "trees/booking_tree.json";
  if (currentMode === "service") file = "trees/service_tree.json";

  console.log(`🔍 Chargement de l'arbre depuis : ${file}`);
  fetch(file)
    .then(r => {
      console.log(`📡 Réponse fetch : ${r.status} ${r.statusText} pour ${file}`);
      if (!r.ok) {
        throw new Error(`HTTP ${r.status} - ${r.statusText}`);
      }
      return r.json();
    })
    .then(json => {
      console.log(`✅ Arbre chargé avec succès :`, Object.keys(json));
      // Normaliser la structure selon le mode
      if (json.Events) {
        // events_tree.json : { "Events": { "Music": {...}, ... } }
        explorerTree = json.Events;
      } else if (json.categories && json.categories.children) {
        // booking_tree.json / service_tree.json : { "categories": { "name": "...", "children": [...] } }
        // Convertir en structure compatible { "NomCategorie": {...}, ... }
        explorerTree = normalizeTreeFromChildren(json.categories.children);
      } else if (json.categories) {
        explorerTree = json.categories;
      } else {
        explorerTree = json;
      }

      explorerPath = [];
      buildCategoryMappingFromTree(explorerTree);
      renderExplorer();
      renderCategoryChips();
    })
    .catch(err => {
      console.error("❌ Erreur chargement arbre :", err);
      console.error("   Fichier tenté :", file);
      const panel = document.getElementById("left-panel");
      panel.innerHTML = `
        <div style='padding:20px;font-size:13px;color:#f87171;text-align:center;'>
          <div style='font-size:48px;margin-bottom:12px;'>⚠️</div>
          <div style='font-weight:600;margin-bottom:8px;'>Impossible de charger les catégories</div>
          <div style='font-size:11px;color:var(--ui-text-muted);margin-bottom:12px;'>
            Fichier : ${file}<br>
            Erreur : ${err.message}
          </div>
          <button onclick="loadExplorerTree()" style='padding:8px 16px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;'>
            🔄 Réessayer
          </button>
        </div>
      `;
    });
}

// Convertit un tableau de { name, children } en objet { name: children_ou_liste }
function normalizeTreeFromChildren(children) {
  if (!Array.isArray(children)) return children;
  
  const result = {};
  children.forEach(item => {
    if (typeof item === "string") {
      // C'est une feuille
      return;
    }
    if (item.name) {
      if (item.children && item.children.length > 0) {
        // Vérifier si les enfants sont des objets ou des strings
        const firstChild = item.children[0];
        if (typeof firstChild === "string" || (firstChild && !firstChild.children)) {
          // Les enfants sont des feuilles (strings ou objets sans children)
          result[item.name] = item.children.map(c => typeof c === "string" ? c : c.name);
        } else {
          // Les enfants ont eux-mêmes des enfants
          result[item.name] = normalizeTreeFromChildren(item.children);
        }
      } else {
        // Pas d'enfants, c'est une catégorie finale
        result[item.name] = [];
      }
    }
  });
  return result;
}

function renderExplorer() {
  const panel = document.getElementById("left-panel");
  panel.style.width = "480px";
  panel.style.maxHeight = "calc(100vh - 100px)";
  panel.style.overflow = "hidden";
  panel.style.display = "block";

  const dateControls =
    currentMode === "event"
      ? `
      <div style="margin-bottom:10px;font-size:11px;color:var(--ui-text-muted);">
        📅 Filtrer par date (cumulable) :
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">
        <label class="date-checkbox-label ${selectedDates.includes('today') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('today') ? 'checked' : ''} onchange="toggleDateFilter('today')">
          Aujourd'hui
        </label>
        <label class="date-checkbox-label ${selectedDates.includes('tomorrow') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('tomorrow') ? 'checked' : ''} onchange="toggleDateFilter('tomorrow')">
          Demain
        </label>
        <label class="date-checkbox-label ${selectedDates.includes('weekend') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('weekend') ? 'checked' : ''} onchange="toggleDateFilter('weekend')">
          Ce week-end
        </label>
        <label class="date-checkbox-label ${selectedDates.includes('week') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('week') ? 'checked' : ''} onchange="toggleDateFilter('week')">
          Cette semaine
        </label>
        <label class="date-checkbox-label ${selectedDates.includes('month') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('month') ? 'checked' : ''} onchange="toggleDateFilter('month')">
          Ce mois
        </label>
      </div>
      
      <div style="margin-bottom:12px;padding:10px;background:rgba(0,255,195,0.03);border-radius:10px;">
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:8px;">📆 Ou sélectionner une période :</div>
        <div style="display:flex;gap:10px;align-items:center;">
          <div style="flex:1;">
            <label style="font-size:10px;color:var(--ui-text-muted);">Du</label>
            <input type="date" id="date-range-start" style="width:100%;padding:8px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;cursor:pointer;">
          </div>
          <div style="color:var(--ui-text-muted);font-size:16px;">→</div>
          <div style="flex:1;">
            <label style="font-size:10px;color:var(--ui-text-muted);">Au</label>
            <input type="date" id="date-range-end" style="width:100%;padding:8px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;cursor:pointer;">
          </div>
        </div>
        <div id="date-range-display" style="font-size:11px;color:#00ffc3;text-align:center;min-height:16px;margin-top:6px;"></div>
      </div>
    `
      : "";

  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
      <div style="font-size:15px;font-weight:700;">Filtrer – ${currentMode}</div>
      <button onclick="closeLeftPanel()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px 8px;border-radius:6px;transition:all 0.15s;" onmouseover="this.style.background='rgba(255,255,255,0.1)';this.style.color='#fff'" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)'">✕</button>
    </div>
    <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:10px;">Choisissez les catégories à filtrer. Le filtre affiche uniquement les events correspondant à ces catégories.</div>

    ${dateControls}

    <div id="explorer-selected" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;"></div>

    <div id="explorer-columns"
      style="
        display:flex;
        gap:12px;
        overflow-x:auto;
        padding-bottom:6px;
        margin-bottom:8px;
        max-height:300px;
      ">
    </div>

    <button onclick="resetExplorerFilter()" class="pill small" style="margin-top:6px;">
      🔄 Réinitialiser tout
    </button>
  `;

  renderSelectedTags();
  buildExplorerColumns();

  if (currentMode === "event") {
    setupDateRangePicker();
  }
}

// Fermer le panneau filtre
function closeLeftPanel() {
  explorerOpen = false;
  const panel = document.getElementById("left-panel");
  if (panel) panel.style.display = "none";
}

// Toggle un filtre de date (cumulable)
function toggleDateFilter(dateType) {
  if (selectedDates.includes(dateType)) {
    selectedDates = selectedDates.filter(d => d !== dateType);
        } else {
    selectedDates.push(dateType);
  }
  // Rafraîchir l'affichage des checkboxes
  renderExplorer();
  applyExplorerFilter();
}

// Gestion du sélecteur de plage de dates
function setupDateRangePicker() {
  const startInput = document.getElementById("date-range-start");
  const endInput = document.getElementById("date-range-end");
  const display = document.getElementById("date-range-display");
  
  if (!startInput || !endInput) return;
  
  // Initialiser avec les valeurs existantes
  if (dateRangeStart) startInput.value = dateRangeStart;
  if (dateRangeEnd) endInput.value = dateRangeEnd;
  
  updateDateRangeDisplay();
  
  startInput.addEventListener("change", () => {
    dateRangeStart = startInput.value || null;
    // Si pas de date de fin, mettre la même que le début
    if (dateRangeStart && !dateRangeEnd) {
      dateRangeEnd = dateRangeStart;
      endInput.value = dateRangeEnd;
    }
    // Si date début > date fin, ajuster
    if (dateRangeStart && dateRangeEnd && dateRangeStart > dateRangeEnd) {
      dateRangeEnd = dateRangeStart;
      endInput.value = dateRangeEnd;
    }
    timeFilter = (dateRangeStart || dateRangeEnd) ? "range" : null;
    updateDateRangeDisplay();
        applyExplorerFilter();
      });
  
  endInput.addEventListener("change", () => {
    dateRangeEnd = endInput.value || null;
    // Si pas de date de début, mettre la même que la fin
    if (dateRangeEnd && !dateRangeStart) {
      dateRangeStart = dateRangeEnd;
      startInput.value = dateRangeStart;
    }
    // Si date fin < date début, ajuster
    if (dateRangeStart && dateRangeEnd && dateRangeEnd < dateRangeStart) {
      dateRangeStart = dateRangeEnd;
      startInput.value = dateRangeStart;
    }
    timeFilter = (dateRangeStart || dateRangeEnd) ? "range" : null;
    updateDateRangeDisplay();
    applyExplorerFilter();
  });
}

function updateDateRangeDisplay() {
  const display = document.getElementById("date-range-display");
  if (!display) return;
  
  if (dateRangeStart && dateRangeEnd) {
    const start = new Date(dateRangeStart);
    const end = new Date(dateRangeEnd);
    const days = Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1;
    
    const formatDate = (d) => d.toLocaleDateString("fr-CH", { day: "2-digit", month: "short" });
    
    if (dateRangeStart === dateRangeEnd) {
      display.textContent = `📍 ${formatDate(start)} (1 jour)`;
    } else {
      display.textContent = `📍 ${formatDate(start)} → ${formatDate(end)} (${days} jours)`;
    }
  } else {
    display.textContent = "";
  }
}

function renderSelectedTags() {
  const box = document.getElementById("explorer-selected");
  if (!box) return;
  box.innerHTML = selectedCategories.length > 0 ? `<span style="font-size:11px;color:var(--ui-text-muted);align-self:center;margin-right:6px;">${selectedCategories.length}</span>` : "";

  selectedCategories.forEach(cat => {
    const safe = escapeHtml(cat);
    box.innerHTML += `
      <div style="
        background:#00ffc3;
        color:#000;
        padding:4px 10px;
        border-radius:999px;
        font-size:12px;
        display:flex;
        align-items:center;
        gap:6px;
      ">
        ${safe}
        <span style="cursor:pointer;font-weight:700;" onclick="removeSelectedCategory('${safe}')">×</span>
      </div>
    `;
  });
}

function removeSelectedCategory(cat) {
  selectedCategories = selectedCategories.filter(c => c !== cat);
  
  // Synchroniser avec les checkboxes dans l'explorateur
  renderExplorer(); // Re-render pour décocher les cases
  renderSelectedTags(); // Mettre à jour les tags
  
  applyExplorerFilter();
  renderCategoryChips();
}

function resetExplorerFilter() {
  selectedCategories = [];
  explorerPath = [];
  timeFilter = null;
  dateRangeStart = null;
  dateRangeEnd = null;
  selectedDates = [];
  filteredData = null; // null = afficher TOUS les points
  renderExplorer();
  renderCategoryChips();
  // IMPORTANT : refreshMarkers et refreshListView utilisent getActiveData() qui retourne filteredData || getCurrentData()
  // Donc si filteredData est null, tous les points sont affichés
  refreshMarkers();
  refreshListView();
  showNotification("🔄 Filtres réinitialisés - Tous les points affichés", "info");
}

function buildExplorerColumns() {
  const colBox = document.getElementById("explorer-columns");
  if (!colBox || !explorerTree) return;
  colBox.innerHTML = "";

  let node = explorerTree;
  buildColumn(colBox, node, 0);

  explorerPath.forEach((step, i) => {
    node = findNode(node, step);
    if (node) buildColumn(colBox, node, i + 1);
  });
}

function findNode(obj, name) {
  if (!obj) return null;
  if (Array.isArray(obj)) return null;

  for (const key in obj) {
    if (key === name) return obj[key];
  }
  return null;
}

function buildColumn(colBox, node, level) {
  const isMob = window.innerWidth <= 768;
  const div = document.createElement("div");
  div.style.minWidth = "200px";
  div.style.maxWidth = "200px";
  div.style.background = "rgba(2,6,23,0.85)";
  div.style.border = "1px solid rgba(0,255,195,0.25)";
  div.style.borderRadius = "10px";
  div.style.padding = "8px";
  div.style.color = "var(--ui-text-main)";
  div.style.fontSize = isMob ? "14px" : "13px";
  div.style.maxHeight = "280px";
  div.style.overflowY = "auto";

  let html = "";

  if (Array.isArray(node)) {
    // Feuilles (catégories finales)
    node.forEach(item => {
      const safe = escapeHtml(item);
      const isChecked = selectedCategories.includes(item);
      html += `
        <label style="display:flex;align-items:center;gap:8px;padding:${isMob ? '7px' : '6px'};cursor:pointer;border-radius:6px;transition:background 0.15s;"
             onmouseover="this.style.background='rgba(0,255,195,0.12)'"
               onmouseout="this.style.background='transparent'"
               onclick="event.stopPropagation()">
          <input type="checkbox" 
                 ${isChecked ? 'checked' : ''} 
                 onchange="toggleCategory('${safe}', event); event.stopPropagation();"
                 onclick="event.stopPropagation()"
                 style="width:${isMob ? '18' : '16'}px;height:${isMob ? '18' : '16'}px;accent-color:#00ffc3;cursor:pointer;">
          <span style="flex:1;font-size:${isMob ? '14' : '12'}px;">${safe}</span>
        </label>
      `;
    });
  } else {
    // Dossiers (catégories avec sous-catégories)
    for (const key in node) {
      const safeKey = escapeHtml(key);
      const isChecked = selectedCategories.includes(key);
      const hasChildren = node[key] && (Array.isArray(node[key]) ? node[key].length > 0 : Object.keys(node[key]).length > 0);
      
      html += `
        <div style="display:flex;align-items:center;gap:6px;padding:${isMob ? '7px' : '6px'};border-radius:6px;transition:background 0.15s;"
             onmouseover="this.style.background='rgba(0,255,195,0.12)'"
             onmouseout="this.style.background='transparent'"
             onclick="event.stopPropagation()">
          <input type="checkbox" 
                 ${isChecked ? 'checked' : ''} 
                 onchange="toggleCategory('${safeKey}', event); event.stopPropagation();"
                 onclick="event.stopPropagation()"
                 style="width:${isMob ? '18' : '16'}px;height:${isMob ? '18' : '16'}px;accent-color:#00ffc3;cursor:pointer;">
          <div style="flex:1;display:flex;align-items:center;justify-content:space-between;cursor:pointer;"
             onclick="openNextLevel('${safeKey}', ${level})">
            <span style="font-size:${isMob ? '14' : '12'}px;font-weight:500;">📁 ${safeKey}</span>
            ${hasChildren ? '<span style="color:#00ffc3;font-size:14px;">›</span>' : ''}
          </div>
        </div>
      `;
    }
  }

  div.innerHTML = html;
  colBox.appendChild(div);
}

// Chips catégories scrollables (mobile)
function renderCategoryChips() {
  const container = document.getElementById("category-chips-inner");
  if (!container) return;
  const topCats = explorerTree ? Object.keys(explorerTree) : [];
  if (topCats.length === 0) return;
  const emoji = (c) => c.includes("Musique") || c.includes("Music") ? "🎵" : c.includes("Sport") ? "⚽" : c.includes("Culture") ? "🎭" : c.includes("DJ") ? "🎧" : c.includes("Live") ? "🎤" : "📌";
  container.innerHTML = topCats.map(cat => {
    const isActive = selectedCategories.includes(cat);
    return `<button type="button" class="category-chip" data-cat="${cat.replace(/"/g, '&quot;')}" onclick="event.stopPropagation();toggleCategory('${cat.replace(/'/g, "\\'")}', event);renderCategoryChips();if(navigator.vibrate)navigator.vibrate(10);" style="flex-shrink:0;padding:6px 14px;border-radius:999px;border:1.5px solid ${isActive ? '#22c55e' : 'rgba(148,163,184,0.25)'};background:${isActive ? 'rgba(34,197,94,0.2)' : 'rgba(255,255,255,0.06)'};color:${isActive ? '#22c55e' : '#cbd5e1'};font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;scroll-snap-align:start;transition:all .2s;">${emoji(cat)} ${cat}</button>`;
  }).join("");
}
window.renderCategoryChips = renderCategoryChips;

// Toggle une catégorie (cocher/décocher)
function toggleCategory(cat, event) {
  console.log('[CATEGORY] toggleCategory appelé avec:', cat);
  
  // ⚠️⚠️⚠️ EMPÊCHER la propagation pour ne pas fermer le modal
  if (event) {
    event.stopPropagation();
    event.stopImmediatePropagation();
  }
  
  // ⚠️⚠️⚠️ Si le modal Publier est ouvert, remplir le champ catégorie au lieu de filtrer
  const publishModal = document.getElementById("publish-modal-backdrop");
  const categoryInput = document.getElementById("pub-main-category");
  
  console.log('[CATEGORY] publishModal:', !!publishModal);
  console.log('[CATEGORY] categoryInput:', !!categoryInput);
  
  // Vérifier si le modal est visible (via style ou computed style)
  const styleDisplay = publishModal?.style?.display;
  const computedDisplay = publishModal ? getComputedStyle(publishModal).display : 'none';
  const attrStyle = publishModal?.getAttribute('style');
  
  console.log('[CATEGORY] styleDisplay:', styleDisplay);
  console.log('[CATEGORY] computedDisplay:', computedDisplay);
  console.log('[CATEGORY] attrStyle includes flex:', attrStyle?.includes('display: flex'));
  
  const isModalVisible = publishModal && (
    styleDisplay === "flex" || 
    computedDisplay === "flex" ||
    attrStyle?.includes('display: flex')
  );
  
  console.log('[CATEGORY] isModalVisible:', isModalVisible);
  
  if (isModalVisible && categoryInput) {
    // Mode publication : remplir le champ catégorie
    categoryInput.value = cat;
    console.log('[PUBLISH] ✅ Catégorie insérée dans le formulaire:', cat);
    
    // ⚠️⚠️⚠️ FORCER les couleurs pour visibilité
    categoryInput.style.background = '#0f172a';
    categoryInput.style.color = '#00ffc3';
    categoryInput.style.webkitTextFillColor = '#00ffc3';
    categoryInput.style.borderColor = '#00ffc3';
    
    // Effet visuel flash puis retour à normal
    setTimeout(() => {
      categoryInput.style.borderColor = '#334155';
    }, 500);
    
    return; // Ne pas filtrer la carte
  }
  
  // Mode normal : toggle le filtre (illimité)
  if (selectedCategories.includes(cat)) {
    selectedCategories = selectedCategories.filter(c => c !== cat);
  } else {
    selectedCategories.push(cat);
  }
  renderSelectedTags();
  applyExplorerFilter();
  renderCategoryChips();
}

function openNextLevel(key, level) {
  explorerPath = explorerPath.slice(0, level);
  explorerPath.push(key);
  renderExplorer();
  
  // Scroll automatique vers la droite pour suivre la navigation
  setTimeout(() => {
    const colBox = document.getElementById("explorer-columns");
    if (colBox) {
      colBox.scrollTo({
        left: colBox.scrollWidth,
        behavior: 'smooth'
      });
    }
  }, 100);
}

function selectLeafCategory(cat, event) {
  // ⚠️⚠️⚠️ EMPÊCHER la propagation pour ne pas fermer le modal
  if (event) {
    event.stopPropagation();
    event.stopImmediatePropagation();
  }
  
  // ⚠️⚠️⚠️ Si le modal Publier est ouvert, remplir le champ catégorie au lieu de filtrer
  const publishModal = document.getElementById("publish-modal-backdrop");
  const categoryInput = document.getElementById("pub-main-category");
  
  // Vérifier si le modal est visible
  const isModalVisible = publishModal && (
    publishModal.style.display === "flex" || 
    getComputedStyle(publishModal).display === "flex" ||
    publishModal.getAttribute('style')?.includes('display: flex')
  );
  
  if (isModalVisible && categoryInput) {
    // Mode publication : remplir le champ catégorie
    categoryInput.value = cat;
    console.log('[PUBLISH] ✅ Catégorie insérée dans le formulaire:', cat);
    
    // ⚠️⚠️⚠️ FORCER les couleurs pour visibilité
    categoryInput.style.background = '#0f172a';
    categoryInput.style.color = '#00ffc3';
    categoryInput.style.webkitTextFillColor = '#00ffc3';
    categoryInput.style.borderColor = '#00ffc3';
    
    setTimeout(() => {
      categoryInput.style.borderColor = '#334155';
    }, 500);
    
    return; // Ne pas filtrer la carte
  }
  
  // Mode normal
  if (!selectedCategories.includes(cat)) {
    selectedCategories.push(cat);
  }
  applyExplorerFilter();
}

function setTimeFilter(mode) {
  // Cette fonction est gardée pour compatibilité mais on utilise maintenant toggleDateFilter
  timeFilter = mode;
  applyExplorerFilter();
}

// Alias scrapers → termes arbre (variations de nom, langues, formats utilisés par les scrapers)
const SCRAPER_ALIASES = {
  // ============ MUSIC ============
  "musique": "music", "electro": "electronic", "electro / dj": "electronic",
  "music > electro": "electronic", "musique > electro": "electronic", "musique > electronic": "electronic",
  "concert": "music", "spectacle musical": "music", "music > live concert": "music", "music > concert": "music",
  "musique > concert": "music", "music > festival": "music",
  "rock / pop": "rock", "music > rock / pop": "rock",
  "jazz / blues": "jazz", "jazz & blues": "jazz", "music > jazz & blues": "jazz",
  "classique / baroque": "classique", "musique > classique / baroque": "classique",
  "punk": "punk rock", "musique > punk": "punk rock",
  "hip hop": "hip-hop", "hip-hop": "hip-hop", "musique > hip-hop": "hip-hop",
  "afrobeats": "afro / afrobeats", "music > urban > afrobeats": "afro / afrobeats",
  "rave": "electronic", "open air": "festival musique", "soirée": "electronic",
  "musique > rock": "rock", "musique > jazz": "jazz", "musique > blues": "blues",
  "musique > funk": "funk", "musique > soul": "soul", "musique > pop": "pop",
  "musique > folk": "folk", "musique > flamenco": "folk", "musique > reggae": "reggae",
  "musique > metal": "metal", "musique > opéra": "opéra", "musique > rap": "rap",
  "musique > trap": "trap", "musique > classique": "classique",
  "musique > festival": "festival musique", "music > autre": "music",
  // ============ CULTURE ============
  "art et culture": "culture", "art": "expositions", "arts": "expositions",
  "exposition": "expositions", "expo": "expositions",
  "culture > exposition": "expositions", "culture > exposition / art": "expositions",
  "art > exhibition": "expositions", "art et culture > exposition": "expositions",
  "culture > photographie": "expositions",
  "culture > arts": "expositions",
  "conférence": "conférences & rencontres", "conférences": "conférences & rencontres",
  "culture > conférence": "conférences & rencontres", "culture > conference": "conférences & rencontres",
  "education > conference": "conférences & rencontres",
  "visite": "visites & patrimoine", "patrimoine": "visites & patrimoine",
  "histoire": "visites & patrimoine", "visite guidée": "visites & patrimoine", "musée": "visites & patrimoine",
  "culture > visite": "visites & patrimoine", "culture > visite guidée": "visites & patrimoine",
  "culture > musée": "visites & patrimoine", "culture > patrimoine": "visites & patrimoine",
  "littérature": "littérature & conte", "conte": "littérature & conte", "lecture": "littérature & conte",
  "culture > littérature": "littérature & conte", "culture > conte": "littérature & conte",
  "cinéma": "cinéma & projections", "cinema": "cinéma & projections", "film": "cinéma & projections",
  "culture > cinéma": "cinéma & projections", "culture > cinema": "cinéma & projections",
  "cinema & film": "cinéma & projections",
  "culture > humour": "humour",
  "culture > marionnettes": "famille & enfants",
  // ============ ATELIERS ============
  "atelier": "ateliers", "workshop": "ateliers", "workshops": "ateliers", "stage": "ateliers",
  "culture > workshops": "ateliers", "culture > atelier": "ateliers",
  "education > workshop": "ateliers", "éducation > atelier": "ateliers",
  "atelier / workshop": "ateliers",
  // ============ ARTS VIVANTS ============
  "spectacle": "théâtre", "théatre": "théâtre", "theatre": "théâtre", "spectacles": "théâtre",
  "culture > théâtre": "théâtre", "culture > theatre / spectacle": "théâtre",
  "spectacle > théâtre": "théâtre", "culture > spectacle": "théâtre", "culture > spectacles": "théâtre",
  "art et culture > spectacle": "théâtre",
  "theater & performance > theater": "théâtre", "theater & performance > dance": "danse",
  "theater & performance > comedy": "humour",
  "spectacle > humour": "humour", "spectacle > cirque": "cirque",
  "humour": "humour", "improvisation": "théâtre", "stand-up": "humour",
  "arts vivants > theatre > improvisation": "théâtre",
  "arts vivants > theatre > stand-up": "humour",
  "danse": "danse", "ballet": "danse classique / ballet",
  "culture > danse": "danse", "culture > cirque": "cirque", "cirque": "cirque",
  // ============ FOOD ============
  "dégustation": "dégustations", "gastronomie": "dégustations",
  "gastronomie > dégustation": "dégustations", "gastronomie > gastronomie": "dégustations",
  "gastronomie > dégustation vin": "dégustation vin", "gastronomie > vin": "dégustation vin",
  "gastronomie > dégustation bière": "dégustation bière",
  "gastronomie > marché": "food & drinks",
  "food & drink > wine & beer": "dégustations",
  "vin": "dégustation vin", "bière": "dégustation bière",
  "food and drinks": "food & drinks", "food": "food & drinks",
  // ============ FESTIVALS ============
  "festival": "festivals & grandes fêtes", "foire": "festivals & grandes fêtes", "salon": "festivals & grandes fêtes",
  "community > festival": "festivals & grandes fêtes", "culture > festival": "festivals & grandes fêtes",
  "art et culture > festival": "festivals & grandes fêtes",
  "foire > marché": "défilés & fêtes",
  // ============ LOISIRS ============
  "loisirs": "loisirs & animation", "animation": "loisirs & animation",
  "brocante": "défilés & fêtes", "marché": "défilés & fêtes", "carnaval": "défilés & fêtes",
  "fête": "défilés & fêtes", "fêtes": "défilés & fêtes",
  "marché & brocante": "défilés & fêtes", "marché > brocante": "défilés & fêtes",
  "parade": "défilés & fêtes", "défilé": "défilés & fêtes",
  "fete / carnaval": "défilés & fêtes",
  "loisirs & animation > defiles & fetes > carnaval": "défilés & fêtes",
  "tradition > folklore": "défilés & fêtes", "tradition & folklore": "défilés & fêtes",
  // ============ NATURE ============
  "nature": "nature & plein air", "plein air": "nature & plein air", "balade": "nature & plein air",
  "randonnée": "nature & plein air", "nature > plein air": "nature & plein air",
  "nature > randonnées": "nature & plein air", "nature > jardin": "nature & plein air",
  "nature & outdoor": "nature & plein air",
  // ============ FAMILLE ============
  "famille": "famille & enfants", "enfants": "famille & enfants", "enfant": "famille & enfants",
  "famille / enfants": "famille & enfants", "famille > enfants": "famille & enfants",
  "famille > activités": "famille & enfants", "famille & enfants > activites": "famille & enfants",
  "family & kids": "famille & enfants",
  // ============ SPORT ============
  "sports": "sport", "sport > autre": "sport",
  "sport > randonnée": "terrestre", "sport > cyclisme": "terrestre",
  "sport > natation": "aquatique", "sport > football": "terrestre",
  "sport > hockey": "glisse", "sport > basketball": "terrestre",
  "sport > course à pied": "terrestre", "sport > terrestre > course a pied": "terrestre",
  "course à pied": "terrestre",
  // ============ BIEN-ÊTRE ============
  "yoga": "bien-être", "méditation": "bien-être", "sophrologie": "bien-être",
  "yoga & bien-être": "bien-être", "wellness": "bien-être",
  // ============ BUSINESS ============
  "networking": "business & communauté", "business": "business & communauté",
  "business & networking": "business & communauté",
  "technologie": "business & communauté", "technology": "business & communauté",
  // ============ GÉNÉRIQUES ============
  "événement": "culture", "evenement": "culture", "divers": "culture",
  "divertissement": "loisirs & animation",
  "culture": "culture"
};

// Construit le mapping complet depuis l'arbre : chaque terme → [lui-même, parent, grand-parent, ...]
let categoryMappingCache = {};
function buildCategoryMappingFromTree(tree, parentPath = []) {
  if (!tree) return;
  const out = {};
  function walk(node, path) {
    if (!node) return;
    if (Array.isArray(node)) {
      node.forEach(item => {
        const name = (typeof item === 'string' ? item : item.name || '').toLowerCase();
        if (!name) return;
        const fullPath = [...path, name];
        if (!out[name]) out[name] = new Set();
        fullPath.forEach(p => out[name].add(p));
      });
      return;
    }
    for (const key in node) {
      const keyLower = key.toLowerCase();
      const fullPath = [...path, keyLower];
      if (!out[keyLower]) out[keyLower] = new Set();
      fullPath.forEach(p => out[keyLower].add(p));
      walk(node[key], fullPath);
    }
  }
  walk(tree, []);
  categoryMappingCache = {};
  for (const k in out) {
    categoryMappingCache[k] = Array.from(out[k]);
  }
}

// Retourne les parties de catégories effectives pour le matching filtre
// Utilise l'arbre (hiérarchie) + alias scrapers pour TOUTES les catégories
function getEffectiveCategoryParts(item) {
  const itemCats = (item.categories || []).map(c => c.toLowerCase());
  const itemMainCat = (item.mainCategory || "").toLowerCase();
  const parts = new Set();
  
  function addPart(p) { if (p && p.length > 0) parts.add(p.trim()); }
  
  itemCats.forEach(cat => {
    addPart(cat);
    cat.split(/\s*>\s*/).forEach(part => addPart(part));
    cat.split('>').forEach(part => addPart(part));
  });
  addPart(itemMainCat);
  
  const toAdd = new Set();
  parts.forEach(p => {
    const resolved = SCRAPER_ALIASES[p] || p;
    if (categoryMappingCache[resolved]) {
      categoryMappingCache[resolved].forEach(e => toAdd.add(e.toLowerCase()));
    } else if (categoryMappingCache[p]) {
      categoryMappingCache[p].forEach(e => toAdd.add(e.toLowerCase()));
    } else {
      toAdd.add(resolved);
      toAdd.add(p);
    }
  });
  toAdd.forEach(x => parts.add(x));
  return parts;
}

let applyExplorerFilterRaf = 0;
let _allEventsLoaded = false;
let _allEventsLoading = false;

// Charger TOUS les events pour que le filtre fonctionne à n'importe quel zoom
async function loadAllEventsForFilter() {
  if (_allEventsLoaded || _allEventsLoading) return;
  _allEventsLoading = true;
  console.log('[FILTER] Chargement de TOUS les events pour le filtre...');
  
  try {
    const r = await fetch(`${window.API_BASE_URL}/events/viewport?zoom=10&south=-90&north=90&west=-180&east=180`);
    if (!r.ok) { _allEventsLoading = false; return; }
    const data = await r.json();
    if (data.type !== 'events' || !data.k || !data.d) { _allEventsLoading = false; return; }
    
    const keys = data.k;
    let newCount = 0;
    data.d.forEach(row => {
      const obj = {};
      for (let i = 0; i < keys.length; i++) {
        if (row[i] !== null && row[i] !== undefined) obj[keys[i]] = row[i];
      }
      if (loadedEventIds.has(obj.id)) return;
      loadedEventIds.add(obj.id);
      
      const event = {
        ...obj, type: 'event',
        lat: obj.latitude, lng: obj.longitude,
        startDate: obj.date ? new Date(obj.date + (obj.time ? 'T' + obj.time : '')) : null,
        endDate: obj.end_date ? new Date(obj.end_date) : null,
        address: obj.location || '', boost: '1.-', likes: 0, favorites: 0, participations: 0
      };
      if (typeof event.lat !== 'number' || typeof event.lng !== 'number' || isNaN(event.lat) || isNaN(event.lng)) return;
      eventsData.push(event);
      newCount++;
    });
    
    if (newCount > 0) {
      window.eventsData = eventsData;
      console.log(`[FILTER] +${newCount} events chargés (total: ${eventsData.length})`);
    }
    _allEventsLoaded = true;
  } catch (e) {
    console.warn('[FILTER] Erreur chargement complet:', e);
  }
  _allEventsLoading = false;
}

const FILTER_ALIASES = {
  // ============ MUSIC ============
  "electronic": ["electro", "musique > electronic", "music > electronic"],
  "electro": ["electronic"],
  "music": ["musique", "concert", "musique > concert"],
  "musique": ["music", "concert"],
  "concert": ["musique", "music"],
  "techno": ["music > electronic > techno"],
  "house": ["music > electronic > house"],
  "trance": ["music > electronic > trance"],
  "drum & bass": ["dnb", "d&b", "drum and bass"],
  "rock": ["musique > rock", "rock / metal"],
  "metal": ["musique > metal"],
  "jazz": ["musique > jazz", "jazz / soul / funk"],
  "blues": ["musique > blues"],
  "funk": ["musique > funk"],
  "soul": ["musique > soul"],
  "pop": ["musique > pop", "pop / variété"],
  "folk": ["musique > folk", "folk / acoustic"],
  "classique": ["musique > classique"],
  "rap": ["musique > rap", "hip-hop"],
  "hip-hop": ["rap", "musique > hip-hop"],
  "reggae": ["musique > reggae", "reggae / ska / world"],
  // ============ CULTURE ============
  "théâtre": ["spectacle", "théatre", "theatre", "spectacles", "spectacle > théâtre", "culture > théâtre"],
  "spectacle": ["théâtre", "theatre", "spectacles"],
  "theatre": ["théâtre", "spectacle"],
  "expositions": ["exposition", "expo", "galerie", "vernissage", "culture > exposition", "art > exhibition"],
  "exposition": ["expositions"],
  "culture": ["conférence", "conférences & rencontres", "arts vivants", "exposition", "expositions", "cinéma", "littérature", "atelier", "ateliers", "événement", "divertissement"],
  "conférences & rencontres": ["conférence", "conférences", "débat", "séminaire", "culture > conférence"],
  "conférence": ["conférences & rencontres"],
  "cinéma & projections": ["cinéma", "cinema", "film", "projection", "cinema & film"],
  "cinéma": ["cinéma & projections", "cinema & film"],
  "littérature & conte": ["littérature", "conte", "lecture", "culture > littérature"],
  "littérature": ["littérature & conte"],
  "visites & patrimoine": ["visite", "patrimoine", "musée", "histoire", "culture > visite"],
  "visite": ["visites & patrimoine"],
  "humour": ["stand-up", "one-man show", "sketch", "improvisation comique", "spectacle > humour"],
  // ============ ATELIERS ============
  "ateliers": ["atelier", "workshops", "workshop", "stage", "culture > workshops", "culture > atelier", "éducation > atelier"],
  "atelier": ["ateliers", "workshops"],
  "workshops": ["ateliers", "atelier"],
  // ============ SPORT ============
  "sport": ["sports"],
  "terrestre": ["sport terrestre", "sport", "sports"], "sport terrestre": ["terrestre"],
  "aquatique": ["sport aquatique"], "sport aquatique": ["aquatique"],
  "glisse": ["ski", "snowboard", "patinage", "hockey", "luge"],
  // ============ FOOD ============
  "food & drinks": ["dégustation", "dégustations", "restauration", "gastronomie", "food"],
  "dégustations": ["dégustation", "gastronomie", "gastronomie > dégustation"],
  "gastronomie": ["dégustations", "food & drinks"],
  // ============ LOISIRS ============
  "loisirs & animation": ["loisirs", "animation", "divertissement"],
  "défilés & fêtes": ["fête", "fêtes", "brocante", "marché", "carnaval", "défilé", "marché & brocante", "parade"],
  "fête": ["défilés & fêtes"], "marché": ["défilés & fêtes", "brocante", "marché & brocante"],
  "brocante": ["marché & brocante", "défilés & fêtes", "marché"],
  // ============ FESTIVALS ============
  "festivals & grandes fêtes": ["festival", "festivals", "foire", "salon", "community > festival"],
  "festival": ["festivals & grandes fêtes"], "foire": ["festivals & grandes fêtes"],
  // ============ FAMILLE ============
  "famille & enfants": ["famille", "enfants", "enfant", "famille / enfants", "family & kids"],
  "famille": ["famille & enfants"], "enfants": ["famille & enfants"],
  // ============ NATURE ============
  "nature & plein air": ["nature", "plein air", "randonnée", "balade", "nature & outdoor"],
  "nature": ["nature & plein air"],
  // ============ BIEN-ÊTRE ============
  "bien-être": ["yoga", "méditation", "sophrologie", "spa", "yoga & bien-être", "wellness"],
  "yoga": ["bien-être", "yoga & bien-être"], "yoga & bien-être": ["bien-être", "yoga"],
  // ============ BUSINESS ============
  "business & communauté": ["business", "networking", "business & networking", "technologie", "technology"],
  "business & networking": ["business & communauté"],
  // ============ GÉNÉRIQUES ============
  "événement": ["culture", "loisirs & animation"],
  "divertissement": ["loisirs & animation"]
};

function applyExplorerFilter() {
  renderSelectedTags();
  if (applyExplorerFilterRaf) cancelAnimationFrame(applyExplorerFilterRaf);

  // CRITIQUE : quand un filtre est activé, basculer de geoCircles vers markersLayer
  if (typeof geoCirclesLayer !== 'undefined' && geoCirclesLayer) {
    geoCirclesLayer.clearLayers();
  }
  if (markersLayer && map && !map.hasLayer(markersLayer)) {
    markersLayer.addTo(map);
  }

  const lowerCats = selectedCategories.map(c => c.toLowerCase());

  if (lowerCats.length === 0 && !timeFilter && !dateRangeStart && !dateRangeEnd && selectedDates.length === 0) {
    filteredData = null;
    isRefreshingMarkers = false;
    refreshMarkers();
    refreshListView();
    return;
  }

  // Si un filtre catégorie est actif, charger TOUS les events (pour voir de loin)
  if (lowerCats.length > 0 && !_allEventsLoaded) {
    loadAllEventsForFilter().then(() => {
      _applyFilterCore(lowerCats);
    });
    // En attendant, appliquer sur ce qu'on a déjà
    _applyFilterCore(lowerCats);
    return;
  }

  _applyFilterCore(lowerCats);
}

function _applyFilterCore(lowerCats) {
  const base = getCurrentData();
  console.log(`[FILTER] ${lowerCats.length} catégories, base: ${base.length} items`);

  let allowedCategories = new Set();
  
  if (lowerCats.length > 0 && explorerTree) {
    lowerCats.forEach(selectedCat => {
      allowedCategories.add(selectedCat);
      const descendants = findCategoryDescendants(selectedCat, explorerTree);
      descendants.forEach(d => allowedCategories.add(d));
      (FILTER_ALIASES[selectedCat] || []).forEach(a => {
        allowedCategories.add(a);
        const aliasDesc = findCategoryDescendants(a, explorerTree);
        aliasDesc.forEach(d => allowedCategories.add(d));
      });
    });
  }

  filteredData = base.filter(item => {
    let catOk = true;
    if (lowerCats.length > 0) {
      const itemCatParts = getEffectiveCategoryParts(item);
      catOk = Array.from(itemCatParts).some(cat => allowedCategories.has(cat));
    }
    let dateOk = true;
    if (item.type === "event") {
      dateOk = eventMatchesTimeFilter(item);
    }
    return catOk && dateOk;
  });

  console.log(`[FILTER] Résultat: ${filteredData.length}/${base.length} passent le filtre`);

  isRefreshingMarkers = false;
  refreshMarkers();
  refreshListView();
}

// Trouve la catégorie cible + tous ses descendants dans l'arbre (hiérarchie stricte)
// Electronic → techno, house, trance, acid techno, etc. | Techno → acid techno, detroit techno, etc. | Reggae → reggae seul
function findCategoryDescendants(targetCat, tree) {
  const results = new Set();
  
  function searchNode(node, found = false) {
    if (!node) return;
    
    if (Array.isArray(node)) {
      if (found) {
        node.forEach(item => {
          const name = (typeof item === 'string' ? item : item.name || '').toLowerCase();
          if (name) results.add(name);
        });
      } else {
        // Cible peut être une feuille dans un array (ex: "Reggae" dans ["Reggae","Dub","Ska"])
        const idx = node.findIndex(item => {
          const name = (typeof item === 'string' ? item : item.name || '').toLowerCase();
          return name === targetCat;
        });
        if (idx >= 0) {
          const name = (typeof node[idx] === 'string' ? node[idx] : node[idx].name || '').toLowerCase();
          results.add(name); // feuille = pas de descendants, juste elle-même
        }
      }
      return;
    }
    
    for (const key in node) {
      const keyLower = key.toLowerCase();
      if (keyLower === targetCat || found) {
        results.add(keyLower);
        searchNode(node[key], true);
      } else {
        searchNode(node[key], false);
      }
    }
  }
  
  searchNode(tree);
  return results;
}

function eventMatchesTimeFilter(ev) {
  // Si aucun filtre de date actif, tout passe
  if (selectedDates.length === 0 && !dateRangeStart && !dateRangeEnd) return true;
  if (!ev.startDate) return true;

  const evStart = new Date(ev.startDate);
  if (isNaN(evStart.getTime())) return true;

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Filtre par plage de dates personnalisée
  if (dateRangeStart || dateRangeEnd) {
    const evDate = new Date(ev.startDate);
    evDate.setHours(0, 0, 0, 0);
    
    if (dateRangeStart && dateRangeEnd) {
      const rangeStart = new Date(dateRangeStart + "T00:00:00");
      const rangeEnd = new Date(dateRangeEnd + "T23:59:59");
      if (evDate >= rangeStart && evDate <= rangeEnd) return true;
    } else if (dateRangeStart) {
      const rangeStart = new Date(dateRangeStart + "T00:00:00");
      if (evDate >= rangeStart) return true;
    } else if (dateRangeEnd) {
      const rangeEnd = new Date(dateRangeEnd + "T23:59:59");
      if (evDate <= rangeEnd) return true;
    }
    // Si seulement plage active et pas de match, retourner false
    if (selectedDates.length === 0) return false;
  }

  // Vérifier les filtres de dates cumulés (OR entre eux)
  if (selectedDates.length > 0) {
    return selectedDates.some(filter => matchesDateFilter(evStart, filter, today));
  }

  return true;
}

// Vérifie si une date correspond à un filtre spécifique
function matchesDateFilter(evStart, filter, today) {
  if (filter === "today") {
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    return evStart >= today && evStart < tomorrow;
  }

  if (filter === "tomorrow") {
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    const after = new Date(tomorrow);
    after.setDate(tomorrow.getDate() + 1);
    return evStart >= tomorrow && evStart < after;
  }

  if (filter === "weekend") {
    const wd = today.getDay();
    const sat = new Date(today);
    sat.setDate(today.getDate() + ((6 - wd + 7) % 7));
    sat.setHours(0, 0, 0, 0);
    const mon = new Date(sat);
    mon.setDate(sat.getDate() + 2);
    mon.setHours(0, 0, 0, 0);
    return evStart >= sat && evStart < mon;
  }

  if (filter === "week") {
    const js = today.getDay() || 7;
    const monday = new Date(today);
    monday.setDate(today.getDate() - (js - 1));
    monday.setHours(0, 0, 0, 0);
    const nextMonday = new Date(monday);
    nextMonday.setDate(monday.getDate() + 7);
    return evStart >= monday && evStart < nextMonday;
  }

  if (filter === "month") {
    const m0 = new Date(today.getFullYear(), today.getMonth(), 1);
    const m1 = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    return evStart >= m0 && evStart < m1;
  }

  return false;
}

// ============================================
// UI : Recherche ville, changement mode, thème
// ============================================

// Variables pour l'autocomplétion
let autocompleteTimeout = null;
let currentSuggestions = [];
let selectedSuggestionIndex = -1;

// Fonction pour créer le dropdown d'autocomplétion
function createAutocompleteDropdown() {
  const container = document.getElementById("map-search-container");
  if (!container) return null;
  
  let dropdown = document.getElementById("city-autocomplete-dropdown");
  if (!dropdown) {
    dropdown = document.createElement("div");
    dropdown.id = "city-autocomplete-dropdown";
    dropdown.style.cssText = `
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      margin-top: 4px;
      background: rgba(15, 23, 42, 0.98);
      border: 1px solid var(--ui-card-border);
      border-radius: 12px;
      max-height: 300px;
      overflow-y: auto;
      z-index: 1000;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      display: none;
    `;
    container.style.position = "relative";
    container.appendChild(dropdown);
  }
  return dropdown;
}

// Fonction pour rechercher des suggestions de villes
async function searchCitySuggestions(query) {
  if (!query || query.length < 2) {
    const dropdown = document.getElementById("city-autocomplete-dropdown");
    if (dropdown) dropdown.style.display = "none";
    return;
  }
  
  try {
    const encodedQuery = encodeURIComponent(query);
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodedQuery}&format=json&limit=8&addressdetails=1&accept-language=${currentLanguage}`,
      {
        headers: {
          'User-Agent': 'MapEventAI/1.0'
        }
      }
    );
    
    if (!response.ok) throw new Error("Erreur API");
    
    const data = await response.json();
    currentSuggestions = data;
    displaySuggestions(data);
  } catch (error) {
    console.error("Erreur autocomplétion:", error);
    const dropdown = document.getElementById("city-autocomplete-dropdown");
    if (dropdown) dropdown.style.display = "none";
  }
}

// Fonction pour afficher les suggestions
function displaySuggestions(suggestions) {
  const dropdown = createAutocompleteDropdown();
  if (!dropdown) return;
  
  if (suggestions.length === 0) {
    dropdown.style.display = "none";
    return;
  }
  
  dropdown.innerHTML = suggestions.map((suggestion, index) => {
    const displayName = suggestion.display_name.split(',').slice(0, 3).join(','); // Limiter à 3 parties
    return `
      <div 
        class="suggestion-item" 
        data-index="${index}"
        onclick="selectSuggestion(${index})"
        onmouseover="highlightSuggestion(${index})"
        style="
          padding: 12px 16px;
          cursor: pointer;
          border-bottom: 1px solid rgba(255,255,255,0.05);
          transition: all 0.2s;
          ${index === selectedSuggestionIndex ? 'background: rgba(0,255,195,0.15);' : ''}
        "
        onmouseenter="this.style.background='rgba(0,255,195,0.1)'"
        onmouseleave="this.style.background='${index === selectedSuggestionIndex ? 'rgba(0,255,195,0.15)' : 'transparent'}'"
      >
        <div style="font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 4px;">
          ${escapeHtml(displayName)}
        </div>
        <div style="font-size: 11px; color: var(--ui-text-muted);">
          ${suggestion.address?.country || ''} ${suggestion.address?.state ? '• ' + suggestion.address.state : ''}
        </div>
      </div>
    `;
  }).join('');
  
  dropdown.style.display = "block";
  selectedSuggestionIndex = -1;
}

// Fonction pour sélectionner une suggestion
function selectSuggestion(index) {
  if (index < 0 || index >= currentSuggestions.length) return;
  
  const suggestion = currentSuggestions[index];
  const searchInput = document.getElementById("map-search-input");
  
  if (searchInput) {
    searchInput.value = suggestion.display_name.split(',')[0]; // Nom de la ville
  }
  
  // Fermer le dropdown
  const dropdown = document.getElementById("city-autocomplete-dropdown");
  if (dropdown) dropdown.style.display = "none";
  
  // Rechercher la ville
  onSearchCity(suggestion.display_name.split(',')[0]);
}

// Fonction pour mettre en surbrillance une suggestion (navigation clavier)
function highlightSuggestion(index) {
  selectedSuggestionIndex = index;
  const items = document.querySelectorAll('.suggestion-item');
  items.forEach((item, i) => {
    item.style.background = i === index ? 'rgba(0,255,195,0.15)' : 'transparent';
  });
}

function initUI() {
  const search = document.getElementById("map-search-input");
  if (search) {
    // Autocomplétion lors de la saisie
    search.addEventListener("input", e => {
      const query = e.target.value.trim();
      
      // Annuler le timeout précédent
      if (autocompleteTimeout) {
        clearTimeout(autocompleteTimeout);
      }
      
      // Attendre 300ms avant de rechercher (debounce)
      autocompleteTimeout = setTimeout(() => {
        searchCitySuggestions(query);
      }, 300);
    });
    
    // Navigation clavier dans les suggestions
    search.addEventListener("keydown", e => {
      const dropdown = document.getElementById("city-autocomplete-dropdown");
      const isVisible = dropdown && dropdown.style.display !== "none";
      
      if (e.key === "ArrowDown" && isVisible) {
        e.preventDefault();
        selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, currentSuggestions.length - 1);
        highlightSuggestion(selectedSuggestionIndex);
        const items = dropdown.querySelectorAll('.suggestion-item');
        if (items[selectedSuggestionIndex]) {
          items[selectedSuggestionIndex].scrollIntoView({ block: 'nearest' });
        }
      } else if (e.key === "ArrowUp" && isVisible) {
        e.preventDefault();
        selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
        if (selectedSuggestionIndex >= 0) {
          highlightSuggestion(selectedSuggestionIndex);
          const items = dropdown.querySelectorAll('.suggestion-item');
          if (items[selectedSuggestionIndex]) {
            items[selectedSuggestionIndex].scrollIntoView({ block: 'nearest' });
          }
        }
      } else if (e.key === "Enter") {
        if (isVisible && selectedSuggestionIndex >= 0) {
          e.preventDefault();
          selectSuggestion(selectedSuggestionIndex);
        } else {
          onSearchCity(search.value);
        }
      } else if (e.key === "Escape") {
        if (dropdown) dropdown.style.display = "none";
      }
    });
    
    // Fermer le dropdown si on clique ailleurs
    document.addEventListener("click", (e) => {
      const dropdown = document.getElementById("city-autocomplete-dropdown");
      const container = document.getElementById("map-search-container");
      if (dropdown && container && !container.contains(e.target)) {
        dropdown.style.display = "none";
      }
    });
  }
}

function switchMode(mode) {
  if (!["event", "booking", "service"].includes(mode)) return;
  
  console.log(`🔄 Changement de mode : ${currentMode} → ${mode}`);
  
  // FERMER LE FILTRE SI OUVERT (l'utilisateur devra le rouvrir)
  const panel = document.getElementById("left-panel");
  if (panel && panel.style.display === "block") {
    panel.style.display = "none";
    explorerOpen = false;
    console.log(`🔒 Filtre fermé automatiquement lors du changement de mode`);
  }
  
  // SUPPRIMER TOUS LES MARQUEURS ET CLUSTERS AVANT DE CHANGER DE MODE
  if (markersLayer) {
    markersLayer.clearLayers();
    markerMap = {};
    console.log(`🗑️ Tous les marqueurs supprimés`);
  }
  // Supprimer aussi les cercles de clusters géographiques (events zoom faible)
  if (typeof geoCirclesLayer !== 'undefined' && geoCirclesLayer) {
    geoCirclesLayer.clearLayers();
    console.log(`🗑️ Cercles de clusters supprimés`);
  }
  // Reset le viewport key pour forcer un reload quand on revient en mode event
  lastViewportKey = '';
  
  // Ré-ajouter markersLayer à la map si absent (loadViewportData le retire en mode clusters)
  if (markersLayer && map && !map.hasLayer(markersLayer)) {
    markersLayer.addTo(map);
  }
  
  currentMode = mode;
  
  
  // FORCER l'affichage de TOUS les points (pas de filtre) - CRITIQUE !
  filteredData = null;
  selectedCategories = [];
  timeFilter = null;
  exactDateStr = null;
  dateRangeStart = null;
  dateRangeEnd = null;
  selectedDates = [];

  document.querySelectorAll(".mode-btn").forEach(btn => {
    const txt = btn.textContent.trim().toLowerCase();
    const key =
      txt.includes("event") ? "event" :
      txt.includes("booking") ? "booking" :
      txt.includes("service") ? "service" : "";
    btn.classList.toggle("active", key === mode);
  });

  // S'assurer que les points sont générés pour le nouveau mode
  ensureDemoPoints();
  
  // FORCER l'affichage immédiat - PAS DE FILTRE
  filteredData = null; // S'assurer qu'on affiche TOUS les points
  selectedCategories = []; // Réinitialiser les catégories
  
  // Afficher immédiatement - pas de délai
  refreshMarkers();
  refreshListView();
}

function toggleListView() {
  listViewOpen = !listViewOpen;
  console.log(`📋 Liste ${listViewOpen ? 'ouverte' : 'fermée'}`);
  if (selectedCityForSorting) {
    console.log(`📍 Ville sélectionnée pour tri: ${selectedCityForSorting.name} (lat:${selectedCityForSorting.lat}, lng:${selectedCityForSorting.lng})`);
  }
  refreshListView();
}

async function onSearchCity(query) {
  if (!query) return;
  const queryLower = query.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
  
  showNotification(`${window.t("searching")} "${query}"...`, "info");
  
  // 1. Chercher dans SWISS_CITIES (base de données locale)
  const cityMatch = SWISS_CITIES.find(city => {
    const cityName = city.name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    return cityName.includes(queryLower) || queryLower.includes(cityName);
  });
  
  if (cityMatch) {
    map.setView([cityMatch.lat, cityMatch.lng], 12);
    showNotification(`📍 ${cityMatch.name} ${window.t("city_found")}`, "success");
    return;
  }
  
  // 2. Chercher dans les données actuelles
  const all = [...eventsData, ...bookingsData, ...servicesData];
  const found = all.find(it => {
    const cityName = (it.city || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    return cityName.includes(queryLower) || queryLower.includes(cityName);
  });
  
  if (found) {
    map.setView([found.lat, found.lng], 12);
    showNotification(`📍 ${found.city} ${window.t("city_found")}`, "success");
    return;
  }
  
  // 3. Recherche mondiale via Nominatim (OpenStreetMap) - GRATUIT et mondial
  try {
    const encodedQuery = encodeURIComponent(query);
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodedQuery}&format=json&limit=1&addressdetails=1`,
      {
        headers: {
          'User-Agent': 'MapEventAI/1.0' // Requis par Nominatim
        }
      }
    );
    
    if (!response.ok) throw new Error("Erreur API");
    
    const data = await response.json();
    
    if (data && data.length > 0) {
      const result = data[0];
      const lat = parseFloat(result.lat);
      const lng = parseFloat(result.lon);
      const displayName = result.display_name.split(',')[0]; // Nom de la ville
      
      map.setView([lat, lng], 12);
      showNotification(`📍 ${displayName} ${window.t("city_found")}`, "success");
    } else {
      showNotification(`⚠️ ${window.t("city_not_found")} "${query}". ${window.t("try_again")}`, "warning");
    }
  } catch (error) {
    console.error("Erreur recherche ville:", error);
    showNotification(`⚠️ ${window.t("error")} ${window.t("try_again")}`, "error");
  }
}

