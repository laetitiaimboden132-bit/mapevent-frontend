// ============================================================
// list-view.js
// Vue Liste fullscreen (refreshListView, buildEventCard, buildBookingCard, calculateDistance, city search)
// Extrait de map_logic.js (lignes 7500-8744)
// ============================================================

// CALCUL DE DISTANCE (formule de Haversine)
// ============================================
function calculateDistance(lat1, lng1, lat2, lng2) {
  // Formule de Haversine pour calculer la distance entre deux points GPS
  const R = 6371; // Rayon de la Terre en km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c; // Distance en km
  
  // Vérification de sécurité
  if (isNaN(distance) || !isFinite(distance) || distance < 0) {
    console.warn(`Distance invalide calculée: ${distance} pour (${lat1},${lng1}) -> (${lat2},${lng2})`);
    return Infinity; // Retourner Infinity plutôt que null pour le tri
  }
  
  return distance;
}

// ============================================
// VUE LISTE (fullscreen) – tri
// ============================================
function refreshListView() {
  const listView = document.getElementById("list-view");
  if (!listView) return;

  if (!listViewOpen) {
    listView.style.display = "none";
    return;
  }

  const base = getActiveData();
  
  // ============================================
  // LOGIQUE DE TRI SIMPLE ET CLAIRE
  // ============================================
  
  let data;
  
  // Vérifier que selectedCityForSorting existe et a des coordonnées valides
  const hasValidCity = selectedCityForSorting && 
                       selectedCityForSorting.lat !== null && 
                       selectedCityForSorting.lat !== undefined &&
                       selectedCityForSorting.lng !== null && 
                       selectedCityForSorting.lng !== undefined &&
                       !isNaN(parseFloat(selectedCityForSorting.lat)) &&
                       !isNaN(parseFloat(selectedCityForSorting.lng));
  
  // LOG TRÈS VISIBLE POUR DÉBOGUER
  console.log(`\n\n\n========================================`);
  console.log(`🚀 REFRESH LIST VIEW - TRI PAR DISTANCE`);
  console.log(`========================================`);
  console.log(`Ville sélectionnée: ${selectedCityForSorting ? selectedCityForSorting.name : 'AUCUNE'}`);
  console.log(`hasValidCity: ${hasValidCity}`);
  console.log(`Nombre d'items à trier: ${base.length}`);
  console.log(`========================================\n\n\n`);
  
  if (hasValidCity) {
    // ============================================
    // MODE 1 : VILLE SÉLECTIONNÉE → TRIER PAR DISTANCE + CATÉGORIES + BOOSTS
    // Ordre de priorité : 1) DISTANCE (priorité absolue), 2) Catégories, 3) Boost, 4) Platinum rank
    // ============================================
    
    console.log(`\n🎯 ===== TRI PAR DISTANCE (PRIORITÉ ABSOLUE) + CATÉGORIES + BOOSTS =====`);
    console.log(`Ville: ${selectedCityForSorting.name}`);
    console.log(`Coordonnées: lat=${selectedCityForSorting.lat}, lng=${selectedCityForSorting.lng}`);
    console.log(`Total items à trier: ${base.length}`);
    
    const boostOrder = { platinum: 1, gold: 2, silver: 3, bronze: 4, basic: 5 };
    
    // ÉTAPE 1 : Calculer la distance pour CHAQUE item
    const cityLat = parseFloat(selectedCityForSorting.lat);
    const cityLng = parseFloat(selectedCityForSorting.lng);
    
    console.log(`🔍 Vérification coordonnées: lat=${cityLat}, lng=${cityLng}, isNaN(lat)=${isNaN(cityLat)}, isNaN(lng)=${isNaN(cityLng)}`);
    console.log(`🔍 Type de lat: ${typeof selectedCityForSorting.lat}, Type de lng: ${typeof selectedCityForSorting.lng}`);
    
    if (isNaN(cityLat) || isNaN(cityLng)) {
      console.error(`❌ Coordonnées ville invalides ! selectedCityForSorting:`, selectedCityForSorting);
      console.error(`❌ Valeurs brutes: lat="${selectedCityForSorting.lat}", lng="${selectedCityForSorting.lng}"`);
      data = base.slice(0, 200);
    } else {
      // Calculer la distance pour tous les items
      // IMPORTANT: S'assurer que chaque item a un champ 'type' pour l'affichage
      const itemsWithDistance = base.map((item) => {
        let distance = Infinity;
        
        if (item.lat && item.lng) {
          const itemLat = parseFloat(item.lat);
          const itemLng = parseFloat(item.lng);
          
          if (!isNaN(itemLat) && !isNaN(itemLng)) {
            const calculatedDistance = calculateDistance(cityLat, cityLng, itemLat, itemLng);
            if (!isNaN(calculatedDistance) && isFinite(calculatedDistance) && calculatedDistance >= 0) {
              distance = calculatedDistance;
            }
          }
        }
        
        // S'assurer que l'item a un champ 'type' pour l'affichage
        // Déterminer le type basé sur les propriétés de l'item
        let itemType = item.type;
        if (!itemType) {
          if (item.title && item.date) {
            itemType = 'event';
          } else if (item.name && (item.soundLinks || item.audioLinks)) {
            itemType = 'booking';
          } else if (item.name) {
            itemType = 'service';
          }
        }
        
        return { ...item, _distance: distance, type: itemType || item.type || 'event' };
      });
      
      // ÉTAPE 2 : Séparer les items avec distance valide de ceux sans distance
      // PRIORITÉ ABSOLUE : 1) DISTANCE, 2) Catégories, 3) Boost, 4) Platinum rank
      console.log(`🔄 Début du tri de ${itemsWithDistance.length} items...`);
      
      // Vérifier quelques distances calculées
      const sampleDistances = itemsWithDistance.slice(0, 5).map(item => ({
        city: item.city || item.title || item.name || 'N/A',
        distance: item._distance !== undefined && isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity',
        lat: item.lat,
        lng: item.lng
      }));
      console.log(`📊 EXEMPLE DE DISTANCES CALCULÉES (5 premiers):`, sampleDistances);
      
      // SÉPARER : Items avec distance valide vs items sans distance
      const itemsWithValidDistance = itemsWithDistance.filter(item => isFinite(item._distance));
      const itemsWithoutDistance = itemsWithDistance.filter(item => !isFinite(item._distance));
      
      console.log(`✅ ${itemsWithValidDistance.length} items avec distance valide`);
      console.log(`⚠️ ${itemsWithoutDistance.length} items sans distance`);
      
      // Vérifier que les items avec distance valide ont bien des distances différentes
      if (itemsWithValidDistance.length >= 2) {
        const distances = itemsWithValidDistance.map(item => item._distance).sort((a, b) => a - b);
        console.log(`📊 DISTANCES MIN/MAX: ${distances[0].toFixed(2)}km (min) à ${distances[distances.length - 1].toFixed(2)}km (max)`);
      }
      
      // Vérifier quelques distances avant le tri
      const sampleDistancesBeforeSort = itemsWithValidDistance.slice(0, 5).map(item => ({
        city: item.city || 'N/A',
        distance: item._distance.toFixed(2),
        boost: item.boost || 'basic'
      }));
      console.log(`📊 AVANT TRI - 5 premiers avec distance:`, sampleDistancesBeforeSort);
      
      // VÉRIFICATION SPÉCIFIQUE : Monthey vs Genève pour Sierre
      const monthey = itemsWithValidDistance.find(item => item.city && item.city.toLowerCase().includes('monthey'));
      const geneve = itemsWithValidDistance.find(item => item.city && item.city.toLowerCase().includes('genève'));
      if (monthey && geneve) {
        console.log(`\n🔍 VÉRIFICATION DISTANCES:`);
        console.log(`   Monthey: ${monthey._distance.toFixed(2)}km (lat:${monthey.lat}, lng:${monthey.lng})`);
        console.log(`   Genève: ${geneve._distance.toFixed(2)}km (lat:${geneve.lat}, lng:${geneve.lng})`);
        console.log(`   Ville sélectionnée: ${selectedCityForSorting.name} (lat:${cityLat}, lng:${cityLng})`);
        if (monthey._distance > geneve._distance) {
          console.error(`   ❌ PROBLÈME: Monthey (${monthey._distance.toFixed(2)}km) est PLUS LOIN que Genève (${geneve._distance.toFixed(2)}km) !`);
        } else {
          console.log(`   ✅ CORRECT: Monthey (${monthey._distance.toFixed(2)}km) est plus proche que Genève (${geneve._distance.toFixed(2)}km)`);
        }
      }
      
      // VÉRIFICATION SPÉCIFIQUE : Sion vs Zurich pour Sierre
      const sion = itemsWithValidDistance.find(item => item.city && item.city.toLowerCase().includes('sion'));
      const zurich = itemsWithValidDistance.find(item => item.city && item.city.toLowerCase().includes('zurich'));
      if (sion && zurich) {
        console.log(`\n🔍 VÉRIFICATION DISTANCES SION vs ZURICH:`);
        console.log(`   Sion: ${sion._distance.toFixed(2)}km (lat:${sion.lat}, lng:${sion.lng})`);
        console.log(`   Zurich: ${zurich._distance.toFixed(2)}km (lat:${zurich.lat}, lng:${zurich.lng})`);
        console.log(`   Ville sélectionnée: ${selectedCityForSorting.name} (lat:${cityLat}, lng:${cityLng})`);
        if (sion._distance > zurich._distance) {
          console.error(`   ❌ PROBLÈME CRITIQUE: Sion (${sion._distance.toFixed(2)}km) est PLUS LOIN que Zurich (${zurich._distance.toFixed(2)}km) !`);
          console.error(`   Cela ne devrait JAMAIS arriver car Sion est à ~10km de Sierre et Zurich à ~200km !`);
        } else {
          console.log(`   ✅ CORRECT: Sion (${sion._distance.toFixed(2)}km) est plus proche que Zurich (${zurich._distance.toFixed(2)}km)`);
        }
      }
      
      // TRIER UNIQUEMENT les items avec distance valide
      // PRIORITÉ ABSOLUE : DISTANCE d'abord, puis catégories, puis boost
      console.log(`🔍 ORDRE DE PRIORITÉ: 1) DISTANCE (absolue), 2) CATÉGORIES, 3) BOOST`);
      
      // TRI SIMPLIFIÉ : DISTANCE UNIQUEMENT - PRIORITÉ ABSOLUE
      // La distance est TOUJOURS le premier critère, sans aucune exception
      itemsWithValidDistance.sort((a, b) => {
        const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
        const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
        
        // PRIORITÉ ABSOLUE : Distance uniquement
        // Si les distances sont différentes, trier par distance SEULEMENT
        if (distA !== distB) {
          return distA - distB;
        }
        
        // Seulement si les distances sont EXACTEMENT identiques (très rare), utiliser les autres critères
        // 2. Catégories sélectionnées (si filtre actif) - utilise getEffectiveCategoryParts + descendants pour cohérence avec le filtre
        if (selectedCategories.length > 0 && explorerTree) {
          const allowed = new Set(selectedCategories.map(sc => sc.toLowerCase()));
          selectedCategories.forEach(sc => {
            (findCategoryDescendants(sc.toLowerCase(), explorerTree) || []).forEach(d => allowed.add(d));
          });
          const matchA = Array.from(getEffectiveCategoryParts(a)).some(p => allowed.has(p));
          const matchB = Array.from(getEffectiveCategoryParts(b)).some(p => allowed.has(p));
          if (matchA && !matchB) return -1;
          if (!matchA && matchB) return 1;
        }
        
        // 3. Boost (platinum > gold > silver > bronze > basic)
        const boostA = boostOrder[a.boost || "basic"] || 99;
        const boostB = boostOrder[b.boost || "basic"] || 99;
        if (boostA !== boostB) return boostA - boostB;
        
        // 4. Platinum rank
        if (a.boost === "platinum" && b.boost === "platinum") {
          const rankA = a.platinumRank || 10;
          const rankB = b.platinumRank || 10;
          if (rankA !== rankB) return rankA - rankB;
        }
        
        return 0;
      });
      
      // RECONSTITUER : Items avec distance triés + items sans distance à la fin
      const sortedItems = [...itemsWithValidDistance, ...itemsWithoutDistance];
      
      // Vérifier quelques distances après le tri
      const sampleDistancesAfterSort = sortedItems.slice(0, 5).map(item => ({
        city: item.city || 'N/A',
        distance: isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity',
        boost: item.boost || 'basic'
      }));
      console.log(`📊 APRÈS TRI - 5 premiers:`, sampleDistancesAfterSort);
      
      // VÉRIFICATION SPÉCIFIQUE APRÈS TRI : Monthey vs Genève
      const montheyAfter = sortedItems.find(item => item.city && item.city.toLowerCase().includes('monthey'));
      const geneveAfter = sortedItems.find(item => item.city && item.city.toLowerCase().includes('genève'));
      if (montheyAfter && geneveAfter) {
        const montheyIndex = sortedItems.indexOf(montheyAfter);
        const geneveIndex = sortedItems.indexOf(geneveAfter);
        console.log(`\n🔍 VÉRIFICATION APRÈS TRI:`);
        console.log(`   Monthey: position ${montheyIndex + 1}, distance ${montheyAfter._distance.toFixed(2)}km`);
        console.log(`   Genève: position ${geneveIndex + 1}, distance ${geneveAfter._distance.toFixed(2)}km`);
        if (montheyIndex > geneveIndex && montheyAfter._distance < geneveAfter._distance) {
          console.error(`   ❌ ERREUR DE TRI: Monthey (${montheyAfter._distance.toFixed(2)}km) est APRÈS Genève (${geneveAfter._distance.toFixed(2)}km) alors qu'il devrait être AVANT !`);
        } else if (montheyIndex < geneveIndex) {
          console.log(`   ✅ CORRECT: Monthey est AVANT Genève dans le tri`);
        }
      }
      
      // VÉRIFICATION SPÉCIFIQUE APRÈS TRI : Sion vs Zurich
      const sionAfter = sortedItems.find(item => item.city && item.city.toLowerCase().includes('sion'));
      const zurichAfter = sortedItems.find(item => item.city && item.city.toLowerCase().includes('zurich'));
      if (sionAfter && zurichAfter) {
        const sionIndex = sortedItems.indexOf(sionAfter);
        const zurichIndex = sortedItems.indexOf(zurichAfter);
        console.log(`\n🔍 VÉRIFICATION APRÈS TRI SION vs ZURICH:`);
        console.log(`   Sion: position ${sionIndex + 1}, distance ${sionAfter._distance.toFixed(2)}km`);
        console.log(`   Zurich: position ${zurichIndex + 1}, distance ${zurichAfter._distance.toFixed(2)}km`);
        if (sionIndex > zurichIndex && sionAfter._distance < zurichAfter._distance) {
          console.error(`   ❌ ERREUR CRITIQUE DE TRI: Sion (${sionAfter._distance.toFixed(2)}km) est APRÈS Zurich (${zurichAfter._distance.toFixed(2)}km) alors qu'il devrait être AVANT !`);
          console.error(`   Le tri ne fonctionne PAS correctement !`);
        } else if (sionIndex < zurichIndex) {
          console.log(`   ✅ CORRECT: Sion est AVANT Zurich dans le tri`);
        }
      }
      
      console.log(`✅ Tri terminé - ${sortedItems.length} items triés`);
      
      // VÉRIFICATION : S'assurer que le tri par distance est correct dans itemsWithValidDistance
      if (itemsWithValidDistance.length >= 2) {
        let triCorrect = true;
        for (let i = 0; i < itemsWithValidDistance.length - 1; i++) {
          const current = itemsWithValidDistance[i];
          const next = itemsWithValidDistance[i + 1];
          if (current._distance > next._distance) {
            triCorrect = false;
            console.error(`❌ ERREUR DE TRI: Item ${i} (${current._distance.toFixed(2)}km) est APRÈS item ${i+1} (${next._distance.toFixed(2)}km) !`);
            console.error(`   Item ${i}: ${current.city || current.title} - ${current._distance.toFixed(2)}km`);
            console.error(`   Item ${i+1}: ${next.city || next.title} - ${next._distance.toFixed(2)}km`);
            break;
          }
        }
        if (triCorrect) {
          console.log(`✅ VÉRIFICATION: Le tri par distance est CORRECT - tous les items sont triés par distance croissante`);
        }
      }
      
      // UTILISER DIRECTEMENT sortedItems (qui contient itemsWithValidDistance trié + itemsWithoutDistance)
      // FORCER LE TRI PAR DISTANCE UNIQUEMENT - PRIORITÉ ABSOLUE
      data = sortedItems.slice(0, 200);
      
      // FORCER LE TRI PAR DISTANCE - PRIORITÉ ABSOLUE (aucune exception)
      console.log(`\n🔧 FORCER TRI PAR DISTANCE (PRIORITÉ ABSOLUE) sur data - ${data.length} items`);
      data.sort((a, b) => {
        const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
        const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
        // DISTANCE UNIQUEMENT - AUCUN AUTRE CRITÈRE
        return distA - distB;
      });
      
      // VÉRIFICATION CRITIQUE : S'assurer que data est bien trié AVANT l'affichage
      console.log(`\n🎯 VÉRIFICATION APRÈS TRI FORCÉ - data contient ${data.length} items`);
      if (data.length >= 5) {
        console.log(`🔍 5 PREMIERS ITEMS DANS data APRÈS TRI FORCÉ:`);
        for (let i = 0; i < 5; i++) {
          const item = data[i];
          const dist = item._distance !== undefined && isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity';
          console.log(`   ${i + 1}. ${item.city || item.title || item.name || 'N/A'} - ${dist}km`);
        }
        
        // Vérifier que le tri est correct
        let triCorrect = true;
        for (let i = 0; i < Math.min(10, data.length - 1); i++) {
          const current = data[i];
          const next = data[i + 1];
          const distCurrent = current._distance !== undefined && isFinite(current._distance) ? current._distance : Infinity;
          const distNext = next._distance !== undefined && isFinite(next._distance) ? next._distance : Infinity;
          if (distCurrent > distNext) {
            triCorrect = false;
            console.error(`   ❌ ERREUR: Item ${i} (${distCurrent.toFixed(2)}km) est APRÈS item ${i+1} (${distNext.toFixed(2)}km) !`);
            break;
          }
        }
        if (triCorrect) {
          console.log(`   ✅ data est correctement trié par distance (PRIORITÉ ABSOLUE)`);
        } else {
          console.error(`   ❌ ERREUR CRITIQUE: Le tri ne fonctionne PAS !`);
        }
      }
      
      // VÉRIFICATION FINALE : Vérifier que data contient bien les données triées
      console.log(`\n🎯 VÉRIFICATION FINALE - data contient ${data.length} items`);
      const montheyInData = data.find(item => item.city && item.city.toLowerCase().includes('monthey'));
      const geneveInData = data.find(item => item.city && item.city.toLowerCase().includes('genève'));
      if (montheyInData && geneveInData) {
        const montheyPosInData = data.indexOf(montheyInData) + 1;
        const genevePosInData = data.indexOf(geneveInData) + 1;
        console.log(`   Monthey dans data: position ${montheyPosInData}, distance ${montheyInData._distance.toFixed(2)}km`);
        console.log(`   Genève dans data: position ${genevePosInData}, distance ${geneveInData._distance.toFixed(2)}km`);
        if (montheyPosInData > genevePosInData && montheyInData._distance < geneveInData._distance) {
          console.error(`   ❌ ERREUR CRITIQUE: Monthey est APRÈS Genève dans data alors qu'il devrait être AVANT !`);
        } else {
          console.log(`   ✅ data est correctement trié`);
        }
      }
      
      // VÉRIFICATION FINALE : Sion vs Zurich dans data
      const sionInData = data.find(item => item.city && item.city.toLowerCase().includes('sion'));
      const zurichInData = data.find(item => item.city && item.city.toLowerCase().includes('zurich'));
      if (sionInData && zurichInData) {
        const sionPosInData = data.indexOf(sionInData) + 1;
        const zurichPosInData = data.indexOf(zurichInData) + 1;
        console.log(`\n🎯 VÉRIFICATION FINALE SION vs ZURICH dans data:`);
        const sionDist = sionInData._distance !== undefined && isFinite(sionInData._distance) ? sionInData._distance : Infinity;
        const zurichDist = zurichInData._distance !== undefined && isFinite(zurichInData._distance) ? zurichInData._distance : Infinity;
        console.log(`   Sion dans data: position ${sionPosInData}, distance ${sionDist.toFixed(2)}km`);
        console.log(`   Zurich dans data: position ${zurichPosInData}, distance ${zurichDist.toFixed(2)}km`);
        if (sionPosInData > zurichPosInData && sionDist < zurichDist) {
          console.error(`   ❌ ERREUR CRITIQUE: Sion est APRÈS Zurich dans data alors qu'il devrait être AVANT !`);
          console.error(`   Le problème est dans la variable data utilisée pour l'affichage !`);
          console.error(`   FORCER LE TRI MANUEL IMMÉDIATEMENT`);
          // FORCER le tri manuel
          data.sort((a, b) => {
            const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
            const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
            return distA - distB;
          });
          console.log(`   ✅ Tri manuel appliqué - ${data.length} items triés`);
        } else if (sionPosInData < zurichPosInData) {
          console.log(`   ✅ CORRECT: Sion est AVANT Zurich dans data`);
        }
      }
      
      // VÉRIFICATION CRITIQUE FINALE : Vérifier que les 5 premiers items sont bien triés par distance
      if (data.length >= 5) {
        console.log(`\n🔍 VÉRIFICATION FINALE DES 5 PREMIERS ITEMS:`);
        let triCorrect = true;
        for (let i = 0; i < Math.min(5, data.length); i++) {
          const item = data[i];
          const dist = item._distance !== undefined && isFinite(item._distance) ? item._distance : Infinity;
          console.log(`   ${i + 1}. ${item.city || item.title || item.name || 'N/A'} - ${dist !== Infinity ? dist.toFixed(2) + 'km' : 'Infinity'}`);
          
          // Vérifier que l'item suivant n'est pas plus proche
          if (i < data.length - 1) {
            const next = data[i + 1];
            const nextDist = next._distance !== undefined && isFinite(next._distance) ? next._distance : Infinity;
            if (dist > nextDist) {
              triCorrect = false;
              console.error(`   ❌ ERREUR: Item ${i} (${dist.toFixed(2)}km) est APRÈS item ${i+1} (${nextDist.toFixed(2)}km) !`);
            }
          }
        }
        
        if (!triCorrect) {
          console.error(`   ❌ LE TRI EST INCORRECT - FORCER LE TRI MANUEL AVANT AFFICHAGE`);
          data.sort((a, b) => {
            const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
            const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
            return distA - distB;
          });
          console.log(`   ✅ Tri manuel appliqué AVANT AFFICHAGE - ${data.length} items triés`);
          
          // Réafficher les 5 premiers après le tri
          console.log(`\n🔍 APRÈS TRI MANUEL - 5 PREMIERS:`);
          for (let i = 0; i < Math.min(5, data.length); i++) {
            const item = data[i];
            const dist = item._distance !== undefined && isFinite(item._distance) ? item._distance : Infinity;
            console.log(`   ${i + 1}. ${item.city || item.title || item.name || 'N/A'} - ${dist !== Infinity ? dist.toFixed(2) + 'km' : 'Infinity'}`);
          }
        } else {
          console.log(`   ✅ Le tri est CORRECT - tous les items sont triés par distance croissante`);
        }
      }
    
      // Logs détaillés
      console.log(`✅ ${itemsWithValidDistance.length} items avec distance calculée`);
      console.log(`⚠️ ${itemsWithDistance.length - itemsWithValidDistance.length} items sans distance`);
      
      if (itemsWithValidDistance.length > 0) {
        console.log(`\n📋 TOP 20 (tri: DISTANCE → CATÉGORIES → BOOSTS) :`);
        data.slice(0, 20).forEach((item, index) => {
          const cityName = (item.city || 'N/A').padEnd(20);
          const distance = isFinite(item._distance) ? item._distance.toFixed(2).padStart(8) : 'N/A'.padStart(8);
          const boost = (item.boost || 'basic').padEnd(10);
          const title = (item.title || item.name || 'N/A').substring(0, 30);
          console.log(`   ${(index + 1).toString().padStart(2)}. ${cityName} ${distance}km  ${boost}  "${title}"`);
        });
        
        // Vérification spécifique pour Sion et Zurich si on cherche Sierre
        if (selectedCityForSorting.name.toLowerCase().includes('sierre') || selectedCityForSorting.name.toLowerCase().includes('sion')) {
          const sion = itemsWithDistance.find(d => d.city && d.city.toLowerCase().includes('sion'));
          const zurich = itemsWithDistance.find(d => d.city && d.city.toLowerCase().includes('zurich'));
          
          console.log(`\n🔍 VÉRIFICATION SPÉCIFIQUE:`);
          if (sion) {
            const sionPos = itemsWithDistance.indexOf(sion) + 1;
            console.log(`   ✅ SION: ${sion._distance.toFixed(2)}km (position ${sionPos})`);
          }
          if (zurich) {
            const zurichPos = itemsWithDistance.indexOf(zurich) + 1;
            console.log(`   ✅ ZURICH: ${zurich._distance.toFixed(2)}km (position ${zurichPos})`);
          }
          
          if (sion && zurich) {
            if (sion._distance < zurich._distance) {
              console.log(`   ✅ TRI CORRECT: Sion (${sion._distance.toFixed(2)}km) est AVANT Zurich (${zurich._distance.toFixed(2)}km)`);
            } else {
              console.error(`   ❌ ERREUR: Sion (${sion._distance.toFixed(2)}km) est APRÈS Zurich (${zurich._distance.toFixed(2)}km) !`);
            }
          }
        }
      }
      
      console.log(`\n📊 Liste finale: ${data.length} items`);
      
      // Vérification finale : Afficher les 5 premiers avec leurs distances
      console.log(`\n🔍 VÉRIFICATION FINALE - 5 PREMIERS ITEMS:`);
      data.slice(0, 5).forEach((item, index) => {
        const dist = isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity';
        console.log(`   ${index + 1}. ${item.city || 'N/A'} - ${dist}km - boost:${item.boost || 'basic'}`);
      });
    }
  } else {
    // ============================================
    // MODE 2 : AUCUNE VILLE SÉLECTIONNÉE → TRIER PAR BOOST ET CATÉGORIES
    // ============================================
    
    const boostOrder = { platinum: 1, gold: 2, silver: 3, bronze: 4, basic: 5 };
    
    data = base
      .slice()
      .sort((a, b) => {
        // 1. Catégories sélectionnées (si filtre actif) - utilise getEffectiveCategoryParts + descendants pour cohérence avec le filtre
        if (selectedCategories.length > 0 && explorerTree) {
          const allowed2 = new Set(selectedCategories.map(sc => sc.toLowerCase()));
          selectedCategories.forEach(sc => {
            (findCategoryDescendants(sc.toLowerCase(), explorerTree) || []).forEach(d => allowed2.add(d));
          });
          const matchA = Array.from(getEffectiveCategoryParts(a)).some(p => allowed2.has(p));
          const matchB = Array.from(getEffectiveCategoryParts(b)).some(p => allowed2.has(p));
          if (matchA && !matchB) return -1;
          if (!matchA && matchB) return 1;
        }
        
        // 2. Boost (platinum > gold > silver > bronze > basic)
        const boostA = boostOrder[a.boost || "basic"] || 99;
        const boostB = boostOrder[b.boost || "basic"] || 99;
        if (boostA !== boostB) return boostA - boostB;
        
        // 3. Platinum rank (si les deux sont platinum)
        if (a.boost === "platinum" && b.boost === "platinum") {
          const rankA = a.platinumRank || 10;
          const rankB = b.platinumRank || 10;
          if (rankA !== rankB) return rankA - rankB;
        }
        
        return 0;
      })
      .slice(0, 200);
  }

  // Le tri est déjà fait dans le bloc ci-dessus, pas besoin de vérification supplémentaire

  // Valeur actuelle de la recherche
  const currentSearchValue = listSearchCity || "";

  listView.style.display = "block";
  listView.innerHTML = `
    <div class="list-header" style="display:flex;flex-direction:column;gap:12px;padding:16px;background:var(--ui-card-bg);border-bottom:1px solid var(--ui-card-border);">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div style="flex:1;">
          <div style="font-size:16px;font-weight:700;margin-bottom:4px;">📋 Résultats (${data.length}/${Math.min(base.length, 200)}${base.length > 200 ? ' (limite: 200 max)' : ''}) – ${currentMode.toUpperCase()}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">Cliquer sur un élément pour ouvrir la popup complète.${base.length > 200 ? ' Affichage limité à 200 résultats maximum.' : ''}</div>
        </div>
        <button onclick="toggleListView()" style="padding:8px 12px;border-radius:8px;background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.4);color:#ef4444;font-size:12px;cursor:pointer;">✕ Fermer</button>
      </div>
      
      <!-- Barre de recherche ville/région -->
      <div style="position:relative;">
        <div style="display:flex;align-items:center;gap:8px;">
          <div style="flex:1;position:relative;">
            <input type="text" 
                   id="city-search-input"
                   placeholder="🔍 Rechercher une ville ou région..."
                   value="${escapeHtml(currentSearchValue)}"
                   oninput="onCitySearchInput(this.value)"
                   onfocus="showCitySuggestions()"
                   style="width:100%;padding:12px 16px;padding-right:40px;border-radius:12px;border:2px solid var(--ui-card-border);background:rgba(0,0,0,0.3);color:var(--ui-text-main);font-size:14px;outline:none;transition:all 0.2s;"
                   onfocus="this.style.borderColor='#00ffc3'"
                   onblur="setTimeout(() => { this.style.borderColor='var(--ui-card-border)'; hideCitySuggestions(); }, 200)">
            ${currentSearchValue ? `
              <button onclick="clearCitySearch()" 
                      style="position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--ui-text-muted);font-size:18px;cursor:pointer;padding:4px;"
                      title="Effacer">✕</button>
            ` : ''}
          </div>
        </div>
        <div id="city-suggestions" style="display:none;position:absolute;top:100%;left:0;right:0;background:var(--ui-card-bg);border:1px solid var(--ui-card-border);border-radius:12px;margin-top:4px;max-height:250px;overflow-y:auto;z-index:100;box-shadow:0 10px 30px rgba(0,0,0,0.4);"></div>
      </div>
      
      ${selectedCityForSorting ? `
        <div style="display:flex;align-items:center;gap:10px;padding:12px 16px;background:linear-gradient(135deg,rgba(0,255,195,0.2),rgba(34,197,94,0.15));border:2px solid rgba(0,255,195,0.4);border-radius:10px;">
          <span style="font-size:18px;">📍</span>
          <div style="flex:1;">
            <div style="font-size:13px;color:var(--ui-text-muted);margin-bottom:2px;">Tri par proximité activé</div>
            <div style="font-size:15px;font-weight:700;color:#00ffc3;">
              ${escapeHtml(selectedCityForSorting.fullName || selectedCityForSorting.name)}
              ${selectedCityForSorting.countryCode ? getFlagEmoji(selectedCityForSorting.countryCode) : ''}
            </div>
          </div>
          <button onclick="clearCitySearch()" style="padding:6px 12px;background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.4);border-radius:6px;color:#ef4444;font-size:12px;font-weight:600;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.3)'" onmouseout="this.style.background='rgba(239,68,68,0.2)'">✕ Réinitialiser</button>
        </div>
      ` : ''}
    </div>

    <div class="list-grid" style="display:grid;grid-template-columns: repeat(auto-fill,minmax(280px,1fr));gap:12px;padding:16px;max-height:calc(100vh - 200px);overflow-y:auto;">
      ${
        (() => {
          // FORCER LE TRI PAR DISTANCE AVANT L'AFFICHAGE si une ville est sélectionnée
          // PRIORITÉ ABSOLUE : Distance uniquement - AUCUNE EXCEPTION
          if (selectedCityForSorting && selectedCityForSorting.lat && selectedCityForSorting.lng) {
            console.log(`\n\n\n========================================`);
            console.log(`🔧 FORCER TRI PAR DISTANCE (PRIORITÉ ABSOLUE)`);
            console.log(`========================================`);
            console.log(`Nombre d'items: ${data.length}`);
            console.log(`Ville sélectionnée: ${selectedCityForSorting.name}`);
            console.log(`Coordonnées: lat=${selectedCityForSorting.lat}, lng=${selectedCityForSorting.lng}`);
            
            // Vérifier que les items ont bien des distances calculées
            const itemsWithDist = data.filter(item => item._distance !== undefined && isFinite(item._distance));
            const itemsWithoutDist = data.filter(item => !item._distance || !isFinite(item._distance));
            console.log(`   Items avec distance: ${itemsWithDist.length}, sans distance: ${itemsWithoutDist.length}`);
            
            // Créer une copie et trier UNIQUEMENT par distance
            const sortedData = [...data].sort((a, b) => {
              const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
              const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
              // Distance est la PRIORITÉ ABSOLUE - pas d'autre critère
              const result = distA - distB;
              return result;
            });
            
            // Vérifier les 10 premiers pour confirmer le tri
            console.log(`\n🔍 10 PREMIERS APRÈS TRI PAR DISTANCE (PRIORITÉ ABSOLUE):`);
            for (let i = 0; i < Math.min(10, sortedData.length); i++) {
              const item = sortedData[i];
              const dist = item._distance !== undefined && isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity';
              const city = item.city || item.title || item.name || 'N/A';
              console.log(`   ${i + 1}. ${city} - ${dist}km`);
            }
            
            // Vérification finale : s'assurer que le tri est correct
            let triCorrect = true;
            for (let i = 0; i < Math.min(10, sortedData.length - 1); i++) {
              const current = sortedData[i];
              const next = sortedData[i + 1];
              const distCurrent = current._distance !== undefined && isFinite(current._distance) ? current._distance : Infinity;
              const distNext = next._distance !== undefined && isFinite(next._distance) ? next._distance : Infinity;
              if (distCurrent > distNext) {
                triCorrect = false;
                console.error(`\n❌ ERREUR CRITIQUE: Item ${i} (${distCurrent.toFixed(2)}km) est APRÈS item ${i+1} (${distNext.toFixed(2)}km) !`);
                console.error(`   Item ${i}: ${current.city || current.title || current.name}`);
                console.error(`   Item ${i+1}: ${next.city || next.title || next.name}`);
              }
            }
            if (triCorrect) {
              console.log(`\n✅ TRI CORRECT - Les items sont triés par distance croissante`);
              console.log(`========================================\n\n\n`);
            } else {
              console.error(`\n❌ ERREUR CRITIQUE: Le tri ne fonctionne PAS !`);
              console.error(`========================================\n\n\n`);
            }
            
            return sortedData;
          }
          return data;
        })().map(item => {
            if (item.type === "event") {
              return buildEventCard(item, item._distance);
            }
            if (item.type === "booking") {
              return buildBookingCard(item, item._distance);
            }
            if (item.type === "service") {
              return buildServiceCard(item, item._distance);
            }
            return "";
          })
          .join("") ||
        "<div style='color:var(--ui-text-muted);padding:20px;text-align:center;'>Aucun résultat</div>"
      }
    </div>
  `;

  listView.querySelectorAll("[data-type][data-id]").forEach(card => {
    card.addEventListener("click", () => {
      const type = card.dataset.type;
      const id = card.dataset.id;
      openPopupFromList(type, id);
    });
  });
  
  // Vérifier les alertes de proximité après le rafraîchissement de la liste
  if (currentUser && currentUser.isLoggedIn) {
    checkProximityAlerts();
  }
  
  // Nettoyer les événements passés (sauf organisateurs)
  cleanExpiredEvents();
  
  // Mode découverte
  refreshDiscoveryCarousel();
}

// Cartes style Airbnb pour la liste
function buildEventCard(ev, distance = null) {
  const imgTag = buildMainImageTag(ev, ev.title || "");
  const borderColor = getBoostColor(ev.boost);
  const emoji = getCategoryEmoji(ev);
  const isLiked = currentUser.likes.includes(`event:${ev.id}`);
  
  // Badge boost
  const boostBadge = ev.boost && ev.boost !== "basic" ? `
    <div style="position:absolute;top:8px;right:8px;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:700;z-index:6;
      ${ev.boost === 'platinum' ? 'background:linear-gradient(135deg,#e5e4e2,#fff);color:#1f2937;' : ''}
      ${ev.boost === 'gold' ? 'background:linear-gradient(135deg,#ffd700,#ffed4a);color:#1f2937;' : ''}
      ${ev.boost === 'silver' ? 'background:linear-gradient(135deg,#c0c0c0,#e5e5e5);color:#1f2937;' : ''}
      ${ev.boost === 'bronze' ? 'background:linear-gradient(135deg,#cd7f32,#daa06d);color:#fff;' : ''}
    ">
      ${ev.boost === 'platinum' ? '👑 TOP' : ev.boost === 'gold' ? '🥇' : ev.boost === 'silver' ? '🥈' : '🥉'}
    </div>
  ` : '';
  
  // Badge distance (afficher seulement si distance valide)
  const distanceBadge = (distance !== null && distance !== undefined && isFinite(distance) && distance !== Infinity) ? `
    <div style="position:absolute;top:8px;left:8px;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:600;background:rgba(0,0,0,0.7);color:#fff;backdrop-filter:blur(4px);z-index:5;">
      📍 ${distance < 1 ? Math.round(distance * 1000) + 'm' : distance.toFixed(1) + 'km'}
    </div>
  ` : '';

  return `
    <div data-type="event" data-id="${ev.id}" class="event-card" onclick="openPopupFromList('event', ${ev.id})" style="
      border:3px solid ${borderColor};
      border-radius:16px;
      background:var(--ui-card-bg);
      overflow:hidden;
      cursor:pointer;
      transition:all 0.2s ease;
      box-shadow:0 4px 20px rgba(0,0,0,0.2);
      position:relative;
    ">
      <div style="position:relative;height:160px;overflow:hidden;">
        ${imgTag}
        ${distanceBadge}
        ${boostBadge}
        <button onclick="event.stopPropagation();onAction('like','event',${ev.id})" style="position:absolute;top:8px;${distanceBadge ? 'left:50px;' : 'left:8px;'}width:32px;height:32px;border-radius:50%;border:none;background:rgba(0,0,0,0.5);color:${isLiked ? '#ef4444' : '#fff'};cursor:pointer;font-size:16px;z-index:7;">
          ${isLiked ? '❤️' : '🤍'}
        </button>
        ${ev.status && ev.status !== 'OK' ? `<div style="position:absolute;bottom:0;left:0;right:0;padding:6px;background:${ev.status === 'COMPLET' ? 'rgba(234,179,8,0.9)' : 'rgba(239,68,68,0.9)'};color:#fff;font-size:11px;font-weight:700;text-align:center;">${ev.status}</div>` : ''}
      </div>
      <div style="padding:12px;">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
          <span style="font-size:18px;">${emoji}</span>
          <span style="font-size:11px;color:var(--ui-text-muted);">${(ev.categories || []).join(" • ")}</span>
          ${ev.verified ? '<span style="font-size:10px;color:#3b82f6;">✓</span>' : ''}
        </div>
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;line-height:1.3;">${escapeHtml(ev.title || "")}</div>
        <div style="font-size:12px;color:#00ffc3;margin-bottom:4px;">
          📅 ${formatEventDateRange(ev.startDate, ev.endDate)}
        </div>
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:8px;">
          📍 ${escapeHtml(ev.city || "")}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--ui-text-muted);">
          <span>❤️ ${ev.likes || 0} • 👥 ${ev.participants || 0}</span>
          ${ev.isAI ? '<span style="color:#facc15;">🤖 IA</span>' : ''}
        </div>
      </div>
    </div>
  `;
}

function buildBookingCard(b, distance = null) {
  const imgTag = buildMainImageTag(b, b.name || "");
  const borderColor = getBoostColor(b.boost);
  const emoji = getCategoryEmoji(b);
  const isLiked = currentUser.likes.includes(`booking:${b.id}`);
  
  // Badge distance (afficher seulement si distance valide)
  const distanceBadge = (distance !== null && distance !== undefined && isFinite(distance) && distance !== Infinity) ? `
    <div style="position:absolute;top:8px;left:8px;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:600;background:rgba(0,0,0,0.7);color:#fff;backdrop-filter:blur(4px);z-index:5;">
      📍 ${distance < 1 ? Math.round(distance * 1000) + 'm' : distance.toFixed(1) + 'km'}
    </div>
  ` : '';

  return `
    <div data-type="booking" data-id="${b.id}" class="event-card" onclick="openPopupFromList('booking', ${b.id})" style="
      border:3px solid ${borderColor};
      border-radius:16px;
      background:var(--ui-card-bg);
      overflow:hidden;
      cursor:pointer;
      transition:all 0.2s ease;
      box-shadow:0 4px 20px rgba(0,0,0,0.2);
      position:relative;
    ">
      <div style="position:relative;height:160px;overflow:hidden;">
        ${imgTag}
        ${distanceBadge}
        <button onclick="event.stopPropagation();onAction('like','booking',${b.id})" style="position:absolute;top:8px;${distanceBadge ? 'left:50px;' : 'left:8px;'}width:32px;height:32px;border-radius:50%;border:none;background:rgba(0,0,0,0.5);color:${isLiked ? '#ef4444' : '#fff'};cursor:pointer;font-size:16px;z-index:7;">
          ${isLiked ? '❤️' : '🤍'}
        </button>
        ${b.level && b.level !== 'Non détecté' ? `<div style="position:absolute;bottom:8px;right:8px;padding:4px 10px;border-radius:999px;font-size:10px;font-weight:600;background:rgba(139,92,246,0.9);color:#fff;">${b.level}</div>` : ''}
      </div>
      <div style="padding:12px;">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
          <span style="font-size:18px;">${emoji}</span>
          <span style="font-size:11px;color:var(--ui-text-muted);">${(b.categories || []).join(" • ")}</span>
          ${b.verified ? '<span style="font-size:10px;color:#3b82f6;">✓</span>' : ''}
        </div>
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;">${escapeHtml(b.name || "")}</div>
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:4px;">
          📍 ${escapeHtml(b.city || "")}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;">
          <span style="color:var(--ui-text-muted);">⭐ ${b.rating || '—'}/5</span>
          ${(b.soundLinks && b.soundLinks.length > 0) || (b.audioLinks && b.audioLinks.length > 0) ? '<span style="color:#a78bfa;">🎵 Audio</span>' : '<span style="color:#ef4444;">⚠️ Pas d\'audio</span>'}
        </div>
      </div>
    </div>
  `;
}

function buildServiceCard(s, distance = null) {
  const imgTag = buildMainImageTag(s, s.name || "");
  const borderColor = getBoostColor(s.boost);
  const emoji = getCategoryEmoji(s);
  const isLiked = currentUser.likes.includes(`service:${s.id}`);
  
  // Badge distance (afficher seulement si distance valide)
  const distanceBadge = (distance !== null && distance !== undefined && isFinite(distance) && distance !== Infinity) ? `
    <div style="position:absolute;top:8px;left:8px;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:600;background:rgba(0,0,0,0.7);color:#fff;backdrop-filter:blur(4px);z-index:5;">
      📍 ${distance < 1 ? Math.round(distance * 1000) + 'm' : distance.toFixed(1) + 'km'}
    </div>
  ` : '';

  return `
    <div data-type="service" data-id="${s.id}" class="event-card" onclick="openPopupFromList('service', ${s.id})" style="
      border:3px solid ${borderColor};
      border-radius:16px;
      background:var(--ui-card-bg);
      overflow:hidden;
      cursor:pointer;
      transition:all 0.2s ease;
      box-shadow:0 4px 20px rgba(0,0,0,0.2);
      position:relative;
    ">
      <div style="position:relative;height:160px;overflow:hidden;">
        ${imgTag}
        ${distanceBadge}
        <button onclick="event.stopPropagation();onAction('like','service',${s.id})" style="position:absolute;top:8px;${distanceBadge ? 'left:50px;' : 'left:8px;'}width:32px;height:32px;border-radius:50%;border:none;background:rgba(0,0,0,0.5);color:${isLiked ? '#ef4444' : '#fff'};cursor:pointer;font-size:16px;z-index:7;">
          ${isLiked ? '❤️' : '🤍'}
        </button>
      </div>
      <div style="padding:12px;">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
          <span style="font-size:18px;">${emoji}</span>
          <span style="font-size:11px;color:var(--ui-text-muted);">${(s.categories || []).join(" • ")}</span>
          ${s.verified ? '<span style="font-size:10px;color:#3b82f6;">✓</span>' : ''}
        </div>
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;">${escapeHtml(s.name || "")}</div>
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:4px;">
          📍 ${escapeHtml(s.city || "")}, Suisse
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;">
          <span style="color:var(--ui-text-muted);">⭐ ${s.rating || '—'}/5</span>
          <span style="color:var(--ui-text-muted);">❤️ ${s.likes || 0}</span>
        </div>
      </div>
    </div>
  `;
}

function openPopupFromList(type, id) {
  const item = getItemById(type, id);
  if (!item) {
    showNotification("⚠️ Item introuvable", "error");
    return;
  }
  
  // Préserver l'audio en cours - ne couper le son que quand on clique sur un autre play
  let persistentContainer = document.getElementById("audio-persistent-container");
  if (!persistentContainer) {
    persistentContainer = document.createElement("div");
    persistentContainer.id = "audio-persistent-container";
    persistentContainer.style.cssText = "position:fixed;bottom:70px;left:10px;width:1px;height:1px;overflow:hidden;pointer-events:none;opacity:0.01;z-index:99998;";
    document.body.insertBefore(persistentContainer, document.body.firstChild);
  }
  let backdrop = document.getElementById("popup-modal-backdrop");
  const scope = backdrop || document;
  Array.from(scope.querySelectorAll('audio[id^="booking-audio-"], audio[id^="event-audio-"]')).forEach(a => {
    if (!a.paused && a.readyState >= 2) {
      try { persistentContainer.appendChild(a); } catch (_) {}
    }
  });
  
  // Construire le HTML de la popup
  let popupHtml = "";
  if (type === "event") {
    popupHtml = buildEventPopup(item);
  } else if (type === "booking") {
    popupHtml = buildBookingPopup(item);
  } else if (type === "service") {
    popupHtml = buildServicePopup(item);
  }
  
  // Afficher dans une modal avec overlay - EN MODE LISTE, même taille que sur la map (380px exactement)
  // La popup doit être exactement la même que sur la map, avec toutes les actions
  // IMPORTANT: La bordure doit s'aligner PARFAITEMENT avec l'image - PAS DE PADDING, PAS DE MARGIN
  const modalHtml = `
    <div style="position:relative;width:380px;max-height:85vh;overflow:hidden;background:var(--ui-card-bg);border-radius:16px;border:1px solid var(--ui-card-border);margin:20px;box-shadow:0 20px 60px rgba(0,0,0,0.5);display:flex;flex-direction:column;padding:0;box-sizing:border-box;">
      <button onclick="closePopupModal()" style="position:absolute;top:12px;right:12px;width:36px;height:36px;border-radius:50%;border:none;background:rgba(0,0,0,0.6);color:#fff;cursor:pointer;font-size:20px;z-index:1001;display:flex;align-items:center;justify-content:center;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.8)'" onmouseout="this.style.background='rgba(0,0,0,0.6)'">✕</button>
      <div style="flex:1;overflow-y:auto;scrollbar-width:none;width:100%;margin:0;padding:0;box-sizing:border-box;">
        ${popupHtml}
      </div>
    </div>
  `;
  
  // Créer ou réutiliser le backdrop - EN MODE LISTE, devant la liste (z-index élevé)
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "popup-modal-backdrop";
    // z-index très élevé pour être devant la liste (qui est à z-index normal)
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.75);display:flex;align-items:center;justify-content:center;z-index:99999;backdrop-filter:blur(2px);padding-top:40px;padding-bottom:40px;box-sizing:border-box;";
    backdrop.onclick = (e) => {
      if (e.target === backdrop) closePopupModal();
    };
    document.body.appendChild(backdrop);
  }
  
  backdrop.innerHTML = modalHtml;
  backdrop.style.display = "flex";
  
  // Marquer qu'on est en mode liste pour le retour
  backdrop.dataset.fromList = "true";
  
  // Centrer la map sur l'item si possible
  if (map && item.lat && item.lng) {
    map.setView([item.lat, item.lng], Math.max(map.getZoom(), 13));
  }
}

function closePopupModal() {
  if (window._popupBottomSheetCleanup) {
    window._popupBottomSheetCleanup();
    window._popupBottomSheetCleanup = null;
  }
  // Réinitialiser la navigation par emplacement
  currentLocationGroup = null;
  currentLocationIndex = 0;
  document.body.style.overflow = '';
  const modal = document.getElementById("popup-modal");
  if (modal) {
    modal.remove();
  }
  const backdrop = document.getElementById("popup-modal-backdrop");
  if (backdrop) {
    backdrop.style.display = "none";
    // Si on était en mode liste, s'assurer que la liste reste ouverte
    if (backdrop.dataset.fromList === "true" && listViewOpen) {
      // La liste reste ouverte automatiquement car listViewOpen est toujours true
      backdrop.dataset.fromList = "false";
    }
  }
  
  // Recentrer la map sur le marqueur qu'on venait de consulter
  if (currentPopupMarker && map) {
    try {
      const latlng = currentPopupMarker.getLatLng();
      // Zoomer assez proche pour voir le point immédiatement
      map.setView(latlng, Math.max(map.getZoom(), 16), { animate: true, duration: 0.3 });
    } catch(e) {
      console.warn('Erreur recentrage map:', e);
    }
    currentPopupMarker = null;
  }
  
  // Réactiver COMPLÈTEMENT les événements Leaflet
  if (map) {
    try {
      map.scrollWheelZoom.enable();
      map.dragging.enable();
      map.touchZoom.enable();
      map.doubleClickZoom.enable();
      // Réactiver les événements au niveau du conteneur de la map
      const mapContainer = map.getContainer();
      if (mapContainer) {
        mapContainer.style.pointerEvents = 'auto';
      }
    } catch(e) {
      console.warn('Erreur réactivation Leaflet:', e);
    }
  }
}

// Variable pour stocker la recherche de ville
let listSearchCity = "";

// Sélectionner une ville pour le tri par distance
function selectCityForSorting(cityName) {
  if (!cityName || cityName === "") {
    selectedCityForSorting = null;
    listSearchCity = "";
  } else {
    const allCities = [...SWISS_CITIES, ...FRENCH_CITIES];
    selectedCityForSorting = allCities.find(c => c.name === cityName) || null;
    if (selectedCityForSorting) {
      listSearchCity = selectedCityForSorting.name;
    }
  }
  
  // Rafraîchir la liste avec le nouveau tri
  if (listViewOpen) {
    refreshListView();
  }
  
  // Rafraîchir aussi les marqueurs sur la map
  refreshMarkers();
}

// Recherche de ville avec autocomplétion - MONDIALE via Nominatim API
let searchTimeout = null;

function onCitySearchInput(value) {
  listSearchCity = value;
  
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (!suggestionsDiv) return;
  
  if (!value || value.length < 2) {
    suggestionsDiv.style.display = "none";
    if (!value) {
      selectedCityForSorting = null;
      refreshListView();
    }
    return;
  }
  
  // Annuler la recherche précédente
  if (searchTimeout) clearTimeout(searchTimeout);
  
  // Afficher un loading
  suggestionsDiv.innerHTML = `
    <div style="padding:16px;text-align:center;color:var(--ui-text-muted);">
      <span style="animation:pulse-subtle 1s infinite;">🔍 Recherche...</span>
    </div>
  `;
  suggestionsDiv.style.display = "block";
  
  // Attendre 300ms avant de lancer la recherche (debounce)
  searchTimeout = setTimeout(() => {
    searchCityGlobal(value);
  }, 300);
}

// Recherche mondiale via Nominatim (OpenStreetMap)
async function searchCityGlobal(query) {
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (!suggestionsDiv) return;
  
  // D'abord chercher dans les villes locales (Suisse/France)
  const allLocalCities = [...SWISS_CITIES, ...FRENCH_CITIES];
  const searchLower = query.toLowerCase();
  const localMatches = allLocalCities.filter(city => 
    city.name.toLowerCase().includes(searchLower) ||
    (city.region && city.region.toLowerCase().includes(searchLower))
  ).slice(0, 5);
  
  // Ensuite chercher via API Nominatim pour le reste du monde
  let globalMatches = [];
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=8&addressdetails=1&featuretype=city`,
      { headers: { 'Accept-Language': 'fr' } }
    );
    const results = await response.json();
    
    globalMatches = results
      .filter(r => r.type === 'city' || r.type === 'town' || r.type === 'village' || r.class === 'place')
      .map(r => ({
        name: r.address?.city || r.address?.town || r.address?.village || r.name,
        lat: parseFloat(r.lat),
        lng: parseFloat(r.lon),
        region: r.address?.state || r.address?.county || '',
        country: r.address?.country || '',
        countryCode: r.address?.country_code?.toUpperCase() || ''
      }))
      .filter(c => c.name); // Filtrer les résultats sans nom
  } catch (error) {
    console.warn('Erreur recherche Nominatim:', error);
  }
  
  // Combiner les résultats (locaux en premier)
  // Marquer les villes locales pour les distinguer
  const localMatchesMarked = localMatches.map(c => ({ ...c, isLocal: true, country: c.country || 'Suisse', countryCode: c.countryCode || 'CH' }));
  const globalMatchesMarked = globalMatches.map(c => ({ ...c, isLocal: false }));
  const allMatches = [...localMatchesMarked, ...globalMatchesMarked].slice(0, 10);
  
  if (allMatches.length === 0) {
    suggestionsDiv.innerHTML = `
      <div style="padding:16px;color:var(--ui-text-muted);text-align:center;">
        <div style="font-size:24px;margin-bottom:8px;">🌍</div>
        <div style="font-size:13px;">Aucune ville trouvée pour "<strong>${escapeHtml(query)}</strong>"</div>
        <div style="font-size:11px;margin-top:4px;">Essayez un autre nom ou une orthographe différente</div>
      </div>
    `;
    suggestionsDiv.style.display = "block";
    return;
  }
  
  // Afficher les suggestions avec pays/région bien visible
  suggestionsDiv.innerHTML = allMatches.map((city, index) => {
    const locationText = city.isLocal 
      ? `${city.region || city.canton || ''}${city.region && city.canton ? ' (' + city.canton + ')' : city.canton ? ' (' + city.canton + ')' : ''}, ${city.country || 'Suisse'}`
      : `${city.region ? escapeHtml(city.region) + ', ' : ''}${escapeHtml(city.country || '')}`;
    
    return `
    <div onclick="selectCityFromSearch(${index})" 
         data-city-index="${index}"
         style="padding:14px 16px;cursor:pointer;display:flex;align-items:center;gap:12px;transition:all 0.15s;border-bottom:1px solid var(--ui-card-border);"
         onmouseover="this.style.background='rgba(0,255,195,0.15)';this.style.borderLeft='3px solid #00ffc3'"
         onmouseout="this.style.background='transparent';this.style.borderLeft='none'">
      <span style="font-size:20px;">📍</span>
      <div style="flex:1;min-width:0;">
        <div style="font-weight:700;color:var(--ui-text-main);font-size:15px;margin-bottom:4px;">${escapeHtml(city.name)}</div>
        <div style="font-size:12px;color:var(--ui-text-muted);display:flex;align-items:center;gap:6px;">
          <span>${locationText}</span>
          ${city.isLocal ? '<span style="padding:2px 6px;background:rgba(0,255,195,0.2);border-radius:4px;font-size:10px;color:#00ffc3;">Local</span>' : ''}
        </div>
      </div>
      <span style="font-size:20px;flex-shrink:0;">${getFlagEmoji(city.countryCode || (city.isLocal ? 'CH' : ''))}</span>
    </div>
  `;
  }).join('');
  
  // Stocker les résultats pour la sélection
  window._citySearchResults = allMatches;
  suggestionsDiv.style.display = "block";
}

// Obtenir le drapeau emoji d'un pays
function getFlagEmoji(countryCode) {
  if (!countryCode || countryCode.length !== 2) return '🌍';
  const codePoints = countryCode
    .toUpperCase()
    .split('')
    .map(char => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

window.getFlagEmoji = getFlagEmoji;

// Sélectionner une ville depuis les résultats de recherche
function selectCityFromSearch(index) {
  const city = window._citySearchResults?.[index];
  if (!city) {
    console.warn('Aucune ville trouvée à l\'index', index);
    return;
  }
  
  // Construire le nom complet avec pays/région pour l'affichage
  const fullName = city.isLocal 
    ? `${city.name}, ${city.region || city.canton || ''}, ${city.country || 'Suisse'}`
    : `${city.name}, ${city.region ? city.region + ', ' : ''}${city.country || ''}`;
  
  // Vérifier que la ville a bien des coordonnées
  if (!city.lat || !city.lng || isNaN(city.lat) || isNaN(city.lng)) {
    console.error(`❌ ERREUR: La ville "${city.name}" n'a pas de coordonnées valides!`, city);
    showNotification(`❌ Erreur: Coordonnées manquantes pour ${city.name}`, 'error');
    return;
  }
  
  // Stocker la ville sélectionnée avec toutes ses infos
  selectedCityForSorting = {
    name: city.name,
    lat: parseFloat(city.lat),
    lng: parseFloat(city.lng),
    region: city.region || city.canton || '',
    country: city.country || (city.isLocal ? 'Suisse' : ''),
    countryCode: city.countryCode || (city.isLocal ? 'CH' : ''),
    fullName: fullName
  };
  
  // Vérifier que les coordonnées sont valides après conversion
  if (isNaN(selectedCityForSorting.lat) || isNaN(selectedCityForSorting.lng)) {
    console.error(`❌ ERREUR: Coordonnées invalides après conversion!`, selectedCityForSorting);
    showNotification(`❌ Erreur: Coordonnées invalides pour ${city.name}`, 'error');
    return;
  }
  
  // Mettre à jour le texte de recherche avec le nom complet
  listSearchCity = fullName;
  
  // Cacher les suggestions
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (suggestionsDiv) suggestionsDiv.style.display = "none";
  
  // Mettre à jour l'input avec le nom complet
  const input = document.getElementById("city-search-input");
  if (input) input.value = fullName;
  
  console.log(`✅ Ville sélectionnée pour tri: ${city.name}`);
  console.log(`   Coordonnées: lat=${selectedCityForSorting.lat}, lng=${selectedCityForSorting.lng}`);
  console.log(`   Objet complet:`, selectedCityForSorting);
  
  console.log(`✅ Ville sélectionnée pour tri: ${city.name}`);
  console.log(`   Coordonnées: lat=${selectedCityForSorting.lat}, lng=${selectedCityForSorting.lng}`);
  console.log(`   Objet complet:`, selectedCityForSorting);
  console.log(`   listViewOpen: ${listViewOpen}`);
  
  // FORCER le rafraîchissement de la liste avec le nouveau tri (même si la liste n'est pas encore ouverte)
  // La liste sera triée correctement quand elle s'ouvrira
  if (listViewOpen) {
    console.log(`🔄 Rafraîchissement de la liste avec tri par distance...`);
    refreshListView();
  } else {
    console.log(`ℹ️ Liste non ouverte, le tri sera appliqué à l'ouverture`);
  }
  
  // Rafraîchir aussi les marqueurs sur la map
  refreshMarkers();
  
  // Centrer la map sur la ville sélectionnée
  if (map && selectedCityForSorting.lat && selectedCityForSorting.lng) {
    map.setView([selectedCityForSorting.lat, selectedCityForSorting.lng], 10);
    showNotification(`📍 Tri par proximité: ${city.name}`, 'success');
  }
}

window.selectCityFromSearch = selectCityFromSearch;

window.searchCityGlobal = searchCityGlobal;
window.selectCityFromSearch = selectCityFromSearch;

function selectCityFromSuggestion(cityName) {
  const allCities = [...SWISS_CITIES, ...FRENCH_CITIES];
  const city = allCities.find(c => c.name === cityName);
  
  if (city) {
    selectedCityForSorting = city;
    listSearchCity = city.name;
    
    // Cacher les suggestions
    const suggestionsDiv = document.getElementById("city-suggestions");
    if (suggestionsDiv) suggestionsDiv.style.display = "none";
    
    // Mettre à jour l'input
    const input = document.getElementById("city-search-input");
    if (input) input.value = city.name;
    
    // Rafraîchir la liste
    refreshListView();
  }
}

function showCitySuggestions() {
  const input = document.getElementById("city-search-input");
  if (input && input.value.length >= 2) {
    onCitySearchInput(input.value);
  }
}

function hideCitySuggestions() {
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (suggestionsDiv) {
    setTimeout(() => { suggestionsDiv.style.display = "none"; }, 200);
  }
}

function clearCitySearch() {
  listSearchCity = "";
  selectedCityForSorting = null;
  
  const input = document.getElementById("city-search-input");
  if (input) input.value = "";
  
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (suggestionsDiv) suggestionsDiv.style.display = "none";
  
  refreshListView();
}

// Exposer les nouvelles fonctions
window.onCitySearchInput = onCitySearchInput;
window.selectCityFromSuggestion = selectCityFromSuggestion;
window.showCitySuggestions = showCitySuggestions;
window.hideCitySuggestions = hideCitySuggestions;
window.clearCitySearch = clearCitySearch;

