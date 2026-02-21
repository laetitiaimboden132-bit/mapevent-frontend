// ============================================================
// account.js
// Compte utilisateur complet (openAccountModal, openSubscriptionModal, openAboutModal, editProfile)
// Extrait de map_logic.js (lignes 23221-26855)
// ============================================================

function getSubscriptionTabContent() {
  const currentSub = currentUser.subscription || "free";
  return `
    <div style="padding:16px;">
      <p style="text-align:center;color:var(--ui-text-muted);margin-bottom:20px;font-size:12px;">
        Choisissez votre formule selon vos besoins !
      </p>
      <div style="margin-bottom:16px;">
        <div style="font-size:13px;font-weight:600;color:#00ffc3;margin-bottom:8px;text-align:center;">🎉 Pour les utilisateurs</div>
        <div style="display:grid;gap:10px;margin-bottom:16px;">
          <div style="padding:14px;border-radius:12px;border:2px solid #22c55e;background:rgba(34,197,94,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'events-explorer' ? 'box-shadow:0 0 15px rgba(34,197,94,0.3);' : ''}" onclick="selectPlan('events-explorer')">
            ${currentSub === 'events-explorer' ? '<div style="position:absolute;top:0;right:0;background:#22c55e;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#22c55e;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">POPULAIRE</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🌱 Events Explorer</span>
              <span style="color:#22c55e;font-weight:700;font-size:14px;">CHF 5.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li><strong>10 alertes</strong> + <strong>10 alarmes</strong></li>
              <li><strong>Agenda 50 places</strong> (vs 20 gratuit)</li>
              <li>Sons booking illimités</li>
            </ul>
          </div>
          <div style="padding:14px;border-radius:12px;border:2px solid #3b82f6;background:rgba(59,130,246,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'events-alerts-pro' ? 'box-shadow:0 0 15px rgba(59,130,246,0.3);' : ''}" onclick="selectPlan('events-alerts-pro')">
            ${currentSub === 'events-alerts-pro' ? '<div style="position:absolute;top:0;right:0;background:#3b82f6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#3b82f6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ALERTES</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🔔 Alertes Pro</span>
              <span style="color:#3b82f6;font-weight:700;font-size:14px;">CHF 10.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li>Tout Explorer + <strong>200 alertes</strong> push + email</li>
              <li><strong>Agenda 200 places</strong></li>
            </ul>
          </div>
        </div>
      </div>
      <div style="margin-bottom:16px;">
        <div style="font-size:13px;font-weight:600;color:#a78bfa;margin-bottom:8px;text-align:center;">🎤 Pour les professionnels</div>
        <div style="display:grid;gap:10px;margin-bottom:16px;">
          <div style="padding:14px;border-radius:12px;border:2px solid #8b5cf6;background:rgba(139,92,246,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'service-pro' ? 'box-shadow:0 0 15px rgba(139,92,246,0.3);' : ''}" onclick="selectPlan('service-pro')">
            ${currentSub === 'service-pro' ? '<div style="position:absolute;top:0;right:0;background:#8b5cf6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : ''}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">💼 Service Pro</span>
              <span style="color:#8b5cf6;font-weight:700;font-size:14px;">CHF 10.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li><strong>Contacts illimités</strong> + <strong>Badge Pro</strong></li>
              <li>Support prioritaire</li>
            </ul>
          </div>
          <div style="padding:14px;border-radius:12px;border:2px solid #a78bfa;background:rgba(167,139,250,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'service-ultra' ? 'box-shadow:0 0 15px rgba(167,139,250,0.3);' : ''}" onclick="selectPlan('service-ultra')">
            ${currentSub === 'service-ultra' ? '<div style="position:absolute;top:0;right:0;background:#a78bfa;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#a78bfa;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ULTRA</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🚀 Service Ultra</span>
              <span style="color:#a78bfa;font-weight:700;font-size:14px;">CHF 18.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li>Tout Pro + <strong>API</strong> + <strong>Stats avancées</strong></li>
              <li><strong>5 events OR gratuits/mois</strong></li>
            </ul>
          </div>
        </div>
      </div>
      <div style="margin-bottom:16px;">
        <div style="padding:16px;border-radius:12px;border:2px solid #ffd700;background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(255,215,0,0.05));cursor:pointer;position:relative;overflow:hidden;${currentSub === 'full-premium' ? 'box-shadow:0 0 20px rgba(255,215,0,0.4);' : ''}" onclick="selectPlan('full-premium')">
          ${currentSub === 'full-premium' ? '<div style="position:absolute;top:0;right:0;background:#ffd700;color:#000;padding:2px 12px;font-size:10px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#ffd700;color:#000;padding:2px 12px;font-size:10px;font-weight:700;border-bottom-left-radius:8px;">TOP</div>'}
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-weight:700;font-size:16px;">👑 Full Premium</span>
            <span style="color:#ffd700;font-weight:700;font-size:16px;">CHF 25.–/mois</span>
          </div>
          <ul style="margin:0;padding-left:20px;font-size:12px;color:var(--ui-text-muted);line-height:1.8;">
            <li><strong>Tout inclus</strong> : Alertes Pro + Service Ultra</li>
            <li><strong>Agenda 250</strong> + <strong>Alertes 250</strong> + <strong>Alarmes 250</strong></li>
            <li><strong>API complet</strong> + Support 24/7</li>
          </ul>
        </div>
      </div>
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:12px;">
        <div style="font-size:12px;font-weight:600;color:#22c55e;margin-bottom:6px;">🌍 70% de vos paiements vont à la Mission Planète</div>
        <div style="font-size:11px;color:var(--ui-text-muted);">Achat de forêts, filtres CO2, protection des océans...</div>
      </div>
    </div>
  `;
}

function openSubscriptionModal() {
  const currentSub = currentUser.subscription || "free";
  const maxAgenda = getAgendaLimit();
  const maxAlerts = getAlertLimit();
  const alertText = maxAlerts === Infinity ? "∞" : maxAlerts;
  
  const html = `
    <div style="padding:10px;max-height:90vh;overflow-y:auto;">
      <h2 style="margin:0 0 16px;font-size:18px;text-align:center;">💎 Abonnements</h2>
      <p style="text-align:center;color:var(--ui-text-muted);margin-bottom:20px;font-size:12px;">
        Choisissez votre formule selon vos besoins !
      </p>
      
      <div style="margin-bottom:16px;">
        <div style="font-size:13px;font-weight:600;color:#00ffc3;margin-bottom:8px;text-align:center;">🎉 Pour les utilisateurs d'événements</div>
        <div style="display:grid;gap:10px;margin-bottom:16px;">
          <div style="padding:14px;border-radius:12px;border:2px solid ${currentSub === 'events-explorer' ? '#22c55e' : '#22c55e'};background:rgba(34,197,94,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'events-explorer' ? 'box-shadow:0 0 15px rgba(34,197,94,0.3);' : ''}" onclick="selectPlan('events-explorer')">
            ${currentSub === 'events-explorer' ? '<div style="position:absolute;top:0;right:0;background:#22c55e;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#22c55e;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">POPULAIRE</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🌱 Events Explorer</span>
              <span style="color:#22c55e;font-weight:700;font-size:14px;">CHF 5.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li><strong>10 alertes personnalisées/mois</strong></li>
              <li><strong>10 alarmes</strong></li>
              <li>Notifications instantanées</li>
              <li><strong>Agenda 50 places</strong> (vs 20 gratuit)</li>
              <li>Écoute des sons booking illimités</li>
            </ul>
          </div>
          
          <div style="padding:14px;border-radius:12px;border:2px solid ${currentSub === 'events-alerts-pro' ? '#3b82f6' : '#3b82f6'};background:rgba(59,130,246,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'events-alerts-pro' ? 'box-shadow:0 0 15px rgba(59,130,246,0.3);' : ''}" onclick="selectPlan('events-alerts-pro')">
            ${currentSub === 'events-alerts-pro' ? '<div style="position:absolute;top:0;right:0;background:#3b82f6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#3b82f6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ALERTES</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🔔 Events Alertes Pro</span>
              <span style="color:#3b82f6;font-weight:700;font-size:14px;">CHF 10.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li><strong>Tout de Events Explorer +</strong></li>
              <li><strong>Alertes jusqu'à 200</strong> avec notifications push + email</li>
              <li><strong>Agenda jusqu'à 200 places</strong></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div style="margin-bottom:16px;">
        <div style="font-size:13px;font-weight:600;color:#a78bfa;margin-bottom:8px;text-align:center;">🎤 Pour les professionnels</div>
        <div style="display:grid;gap:10px;margin-bottom:16px;">
          <div style="padding:14px;border-radius:12px;border:2px solid ${currentSub === 'service-pro' ? '#8b5cf6' : '#8b5cf6'};background:rgba(139,92,246,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'service-pro' ? 'box-shadow:0 0 15px rgba(139,92,246,0.3);' : ''}" onclick="selectPlan('service-pro')">
            ${currentSub === 'service-pro' ? '<div style="position:absolute;top:0;right:0;background:#8b5cf6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : ''}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">💼 Service Pro</span>
              <span style="color:#8b5cf6;font-weight:700;font-size:14px;">CHF 10.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li><strong>Tout de Events Explorer</strong></li>
              <li><strong>Contacts illimités</strong> - voit toutes les infos directement</li>
              <li><strong>Badge Pro</strong> visible sur avatar</li>
              <li>Support prioritaire</li>
            </ul>
          </div>
          
          <div style="padding:14px;border-radius:12px;border:2px solid ${currentSub === 'service-ultra' ? '#a78bfa' : '#a78bfa'};background:rgba(167,139,250,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'service-ultra' ? 'box-shadow:0 0 15px rgba(167,139,250,0.3);' : ''}" onclick="selectPlan('service-ultra')">
            ${currentSub === 'service-ultra' ? '<div style="position:absolute;top:0;right:0;background:#a78bfa;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#a78bfa;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ULTRA</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🚀 Service Ultra</span>
              <span style="color:#a78bfa;font-weight:700;font-size:14px;">CHF 18.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li>Tout de Pro +</li>
              <li><strong>Accès API</strong> pour développeurs</li>
              <li><strong>Ajout automatique d'events</strong> pour organisateurs</li>
              <li>Contacts infos illimités</li>
              <li><strong>Statistiques avancées</strong></li>
              <li><strong>5 events gratuits / mois placés OR</strong></li>
              <li>Support 24/7</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;font-weight:600;color:#ffd700;margin-bottom:8px;text-align:center;">⭐ Tout compris</div>
        <div style="padding:16px;border-radius:12px;border:2px solid ${currentSub === 'full-premium' ? '#ffd700' : '#ffd700'};background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(255,215,0,0.05));cursor:pointer;position:relative;overflow:hidden;${currentSub === 'full-premium' ? 'box-shadow:0 0 20px rgba(255,215,0,0.4);' : ''}" onclick="selectPlan('full-premium')">
          ${currentSub === 'full-premium' ? '<div style="position:absolute;top:0;right:0;background:#ffd700;color:#000;padding:2px 12px;font-size:10px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#ffd700;color:#000;padding:2px 12px;font-size:10px;font-weight:700;border-bottom-left-radius:8px;">TOP</div>'}
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-weight:700;font-size:16px;">👑 Full Premium</span>
            <span style="color:#ffd700;font-weight:700;font-size:16px;">CHF 25.–/mois</span>
          </div>
          <ul style="margin:0;padding-left:20px;font-size:12px;color:var(--ui-text-muted);line-height:1.8;">
            <li><strong>Tout de Events Alertes Pro, Tout de Service Ultra</strong></li>
            <li><strong>Agenda 250 places</strong></li>
            <li><strong>Alertes 250</strong> avec notifications push + email</li>
            <li><strong>Alarmes 250 places</strong></li>
            <li><strong>Contacts illimités</strong> partout</li>
            <li><strong>Accès API complet</strong> et facilité pour poser tous les events</li>
            <li><strong>Statistiques ultras avancées</strong></li>
            <li>Support 24/7 prioritaire</li>
          </ul>
        </div>
      </div>
      
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:12px;margin-bottom:20px;">
        <div style="font-size:12px;font-weight:600;color:#22c55e;margin-bottom:6px;">🌍 70% de vos paiements vont à la Mission Planète</div>
        <div style="font-size:11px;color:var(--ui-text-muted);">Achat de forêts, filtres CO2, protection des océans...</div>
      </div>
      
      
      
      <button onclick="closePublishModal()" style="width:100%;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;margin-top:16px;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
}

function createAlert() {
  const category = document.getElementById("alert-category").value;
  const city = document.getElementById("alert-city").value;
  
  if (!category) {
    showNotification("⚠️ Veuillez sélectionner une catégorie", "warning");
    return;
  }
  
  // Vérifier la limite selon l'abonnement
  const maxAlerts = getAlertLimit();
  if (maxAlerts === 0) {
    showNotification("⚠️ Les alertes nécessitent un abonnement Events Explorer ou supérieur", "warning");
    openSubscriptionModal();
    return;
  }
  
  if (maxAlerts !== Infinity && currentUser.alerts.length >= maxAlerts) {
    showNotification(`⚠️ Limite atteinte (${maxAlerts} alertes) ! Passez à Events Alertes Pro pour des alertes illimitées.`, "warning");
    openSubscriptionModal();
    return;
  }
  
  currentUser.alerts.push({ category, city, createdAt: new Date().toISOString() });
  showNotification("🔔 Alerte créée ! Vous serez notifié des nouveaux événements et changements.", "success");
  openSubscriptionModal(); // Rafraîchir
}

function removeAlert(index) {
  currentUser.alerts.splice(index, 1);
  showNotification("🔕 Alerte supprimée", "info");
  openSubscriptionModal(); // Rafraîchir
}

function selectPlan(plan) {
  if (plan === 'free') {
    currentUser.subscription = "free";
    showNotification("✅ Plan gratuit actif", "info");
    updateSubscriptionBadge();
    openSubscriptionModal();
  } else if (plan === 'events-explorer') {
    openPremiumPaymentModal('events-explorer', 5);
  } else if (plan === 'events-alerts-pro') {
    openPremiumPaymentModal('events-alerts-pro', 10);
  } else if (plan === 'service-pro') {
    openPremiumPaymentModal('service-pro', 10);
  } else if (plan === 'service-ultra') {
    openPremiumPaymentModal('service-ultra', 18);
  } else if (plan === 'full-premium') {
    openPremiumPaymentModal('full-premium', 25);
  }
}

function openPremiumPaymentModal(plan = 'full-premium', price = 25) {
  const planInfo = {
    'events-explorer': { emoji: '🌱', name: 'Events Explorer', color: '#22c55e', bg: 'rgba(34,197,94,0.2)' },
    'events-alerts-pro': { emoji: '🔔', name: 'Events Alertes Pro', color: '#3b82f6', bg: 'rgba(59,130,246,0.2)' },
    'service-pro': { emoji: '💼', name: 'Service Pro', color: '#8b5cf6', bg: 'rgba(139,92,246,0.2)' },
    'service-ultra': { emoji: '🚀', name: 'Service Ultra', color: '#a78bfa', bg: 'rgba(167,139,250,0.2)' },
    'full-premium': { emoji: '👑', name: 'Full Premium', color: '#ffd700', bg: 'rgba(255,215,0,0.2)' },
    // Anciens noms pour compatibilité
    'events-alerts': { emoji: '🔔', name: 'Events Alertes Pro', color: '#3b82f6', bg: 'rgba(59,130,246,0.2)' },
    'booking-pro': { emoji: '💼', name: 'Service Pro', color: '#8b5cf6', bg: 'rgba(139,92,246,0.2)' },
    'booking-ultra': { emoji: '🚀', name: 'Service Ultra', color: '#a78bfa', bg: 'rgba(167,139,250,0.2)' },
    'full': { emoji: '👑', name: 'Full Premium', color: '#ffd700', bg: 'rgba(255,215,0,0.2)' },
    explorer: { emoji: '🌱', name: 'Explorer', color: '#22c55e', bg: 'rgba(34,197,94,0.2)' },
    pro: { emoji: '💼', name: 'Pro', color: '#8b5cf6', bg: 'rgba(139,92,246,0.2)' },
    premium: { emoji: '⭐', name: 'Premium', color: '#ffd700', bg: 'rgba(255,215,0,0.2)' }
  };
  
  const info = planInfo[plan] || planInfo.full;
  
  const html = `
    <div style="padding:10px;text-align:center;">
      <div style="font-size:48px;margin-bottom:16px;">${info.emoji}</div>
      <h2 style="margin:0 0 10px;font-size:20px;">Passer en ${info.name}</h2>
      <p style="color:var(--ui-text-muted);margin-bottom:20px;">
        Débloquez toutes les fonctionnalités ${info.name} !
      </p>
      
      <div style="background:linear-gradient(135deg,${info.bg},transparent);border:2px solid ${info.color};border-radius:16px;padding:20px;margin-bottom:20px;">
        <div style="font-size:32px;font-weight:800;color:${info.color};">CHF ${price.toFixed(2)}</div>
        <div style="font-size:12px;color:var(--ui-text-muted);">par mois • Sans engagement</div>
      </div>
      
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:12px;margin-bottom:20px;">
        <div style="font-size:12px;font-weight:600;color:#22c55e;margin-bottom:4px;">🌍 70% → Mission Planète</div>
        <div style="font-size:11px;color:var(--ui-text-muted);">Votre contribution sauve la Terre</div>
      </div>
      
        <button onclick="processSubscriptionPayment('${plan}', ${price})" style="width:100%;padding:14px;border-radius:999px;border:none;background:linear-gradient(135deg,${info.color},${info.color}dd);color:${plan === 'premium' ? '#1f2937' : '#fff'};font-weight:700;cursor:pointer;font-size:16px;box-shadow:0 8px 24px ${info.color}66;">
          💳 Payer CHF ${price.toFixed(2)}/mois
        </button>
      
      <button onclick="openSubscriptionModal()" style="width:100%;margin-top:10px;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;">
        Retour
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
}

async function processSubscriptionPayment(plan = 'full-premium', price = 25) {
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  try {
    showNotification("💳 Redirection vers le paiement...", "info");
    
    // Créer une session Stripe Checkout pour abonnement
    const response = await fetch(`${window.API_BASE_URL}/payments/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        paymentType: 'subscription',
        plan: plan,
        amount: price,
        currency: 'CHF',
        email: currentUser.email
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Erreur lors de la création de la session');
    }
    
    const { sessionId, publicKey } = await response.json();
    
    // Initialiser Stripe si pas encore fait
    if (!stripe && publicKey) {
      initStripe(publicKey);
    }
    
    if (!stripe) {
      throw new Error('Stripe non disponible');
    }
    
    // Rediriger vers Stripe Checkout
    const result = await stripe.redirectToCheckout({ sessionId });
    
    if (result.error) {
      showNotification(`❌ Erreur : ${result.error.message}`, "error");
    }
  } catch (error) {
    console.error('Erreur abonnement:', error);
    showNotification(`❌ Erreur lors de l'abonnement : ${error.message}`, "error");
  }
}

// Fonction de compatibilité (fallback si Stripe échoue)
function simulatePremiumPayment(plan = 'full-premium', price = 25) {
  processSubscriptionPayment(plan, price).catch(() => {
    // Fallback : simulation locale si l'API échoue
    currentUser.subscription = plan;
    currentUser.agendaLimit = getAgendaLimit();
    currentUser.alertLimit = getAlertLimit();
    updateSubscriptionBadge();
    
    const planNames = {
      'events-explorer': '🌱 Events Explorer',
      'events-alerts-pro': '🔔 Events Alertes Pro',
      'service-pro': '💼 Service Pro',
      'service-ultra': '🚀 Service Ultra',
      'full-premium': '👑 Full Premium',
      'events-alerts': '🔔 Events Alertes Pro',
      'booking-pro': '💼 Service Pro',
      'booking-ultra': '🚀 Service Ultra',
      'full': '👑 Full Premium',
      explorer: '🌱 Explorer',
      pro: '💼 Pro',
      premium: '⭐ Premium'
    };
    
    const planName = planNames[plan] || 'Premium';
    playPaymentSound();
    showNotification(`💎 Abonnement simulé (mode démo) : ${planName}`, "info");
    closePublishModal();
    openSubscriptionModal();
  });
}

// ============================================
// MODAL "À PROPOS" - CLIC SUR LOGO MAPEVENT
// ============================================
function openAboutModal() {
  // Récupérer la date de dernière connexion
  const lastLogin = currentUser.lastLoginAt ? new Date(currentUser.lastLoginAt).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }) : 'Première visite';
  
  const html = `
    <div style="padding:24px;max-width:600px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <!-- Header avec logo -->
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:48px;margin-bottom:12px;">🗺️</div>
        <h2 style="margin:0;font-size:28px;font-weight:800;background:linear-gradient(90deg,#00ffc3,#3b82f6);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;">MAP EVENT</h2>
        <p style="color:var(--ui-text-muted);margin-top:8px;font-size:14px;">La plateforme événementielle mondiale</p>
      </div>
      
      <!-- Contact -->
      <div style="background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:16px;padding:16px;margin-bottom:20px;text-align:center;">
        <div style="font-size:14px;font-weight:600;color:#00ffc3;margin-bottom:8px;">📧 Contact</div>
        <a href="mailto:${MAPEVENT_CONTACT_EMAIL}" style="color:#3b82f6;font-size:16px;font-weight:600;text-decoration:none;">${MAPEVENT_CONTACT_EMAIL}</a>
      </div>
      
      <!-- État actuel -->
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:16px;padding:16px;margin-bottom:20px;">
        <div style="font-size:14px;font-weight:700;color:#22c55e;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
          <span>✅</span> Fonctionnalités disponibles
        </div>
        <ul style="margin:0;padding-left:20px;color:var(--ui-text-main);font-size:13px;line-height:1.8;">
          <li><strong>Carte interactive</strong> - 3 modes : Events, Booking, Services</li>
          <li><strong>Filtres avancés</strong> - Par catégorie, date, distance</li>
          <li><strong>Popups détaillées</strong> - Infos complètes sur chaque point</li>
          <li><strong>Comptes utilisateurs</strong> - Inscription, connexion, profil avec avatar</li>
          <li><strong>Favoris & Agenda</strong> - Sauvegardez vos événements préférés</li>
          <li><strong>Likes & Commentaires</strong> - Interagissez avec la communauté</li>
          <li><strong>Signalements</strong> - Signalez les contenus inappropriés</li>
          <li><strong>Paiements Stripe</strong> - Abonnements et boosts sécurisés</li>
          <li><strong>Multi-langues</strong> - FR, EN, ES, ZH, HI</li>
          <li><strong>Mode sombre</strong> - Design premium adaptatif</li>
        </ul>
      </div>
      
      <!-- Prochaines fonctionnalités -->
      <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:16px;padding:16px;margin-bottom:20px;">
        <div style="font-size:14px;font-weight:700;color:#3b82f6;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
          <span>🚀</span> Prochaines étapes
        </div>
        <ul style="margin:0;padding-left:20px;color:var(--ui-text-main);font-size:13px;line-height:1.8;">
          <li><strong>106 langues</strong> - Traduction automatique mondiale</li>
          <li><strong>Safe Social</strong> - Réseau social sécurisé et bienveillant</li>
          <li><strong>Messagerie</strong> - Discutez avec vos amis</li>
          <li><strong>Groupes</strong> - Créez des groupes comme WhatsApp</li>
          <li><strong>Invitations</strong> - Invitez vos amis aux événements</li>
          <li><strong>Localisation live</strong> - Retrouvez vos amis sur place</li>
          <li><strong>Last Minute Tickets</strong> - Revente de billets sécurisée</li>
          <li><strong>Transport partagé</strong> - Covoiturage vers les events</li>
          <li><strong>Quêtes & Gamification</strong> - Gagnez des récompenses</li>
          <li><strong>Scraping 200+ events/pays</strong> - Données automatiques</li>
        </ul>
      </div>
      
      <!-- Dernière connexion -->
      ${currentUser.isLoggedIn ? `
        <div style="background:rgba(148,163,184,0.1);border:1px solid rgba(148,163,184,0.3);border-radius:16px;padding:16px;margin-bottom:20px;text-align:center;">
          <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:4px;">Dernière connexion</div>
          <div style="font-size:14px;font-weight:600;color:var(--ui-text-main);">${lastLogin}</div>
        </div>
      ` : `
        <div style="background:rgba(0,255,195,0.05);border:2px solid rgba(0,255,195,0.4);border-radius:16px;padding:20px;margin-bottom:20px;text-align:center;">
          <div style="font-size:15px;font-weight:700;color:#00ffc3;margin-bottom:12px;">👋 Bienvenue sur MapEvent !</div>
          <button onclick="closePublishModal();setTimeout(function(){if(typeof window.openAuthModal==='function'){window.openAuthModal('register');}else if(typeof window.showProRegisterForm==='function'){window.showProRegisterForm();}else if(typeof window.openRegisterModal==='function'){window.openRegisterModal();}},300);" style="width:100%;padding:14px 24px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:16px;cursor:pointer;box-shadow:0 4px 20px rgba(0,255,195,0.4);" id="register-modal-btn">
            Créer un compte
          </button>
        </div>
      `}
      
      <!-- Version -->
      <div style="text-align:center;color:var(--ui-text-muted);font-size:11px;margin-bottom:16px;">
        Version 1.0.0 • Décembre 2024 • Made with ❤️ in Switzerland
      </div>
      
      <!-- Bouton fermer -->
      <button onclick="closePublishModal()" style="width:100%;padding:14px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;font-size:14px;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
}

// ============================================
// MODAL D'ANNONCE - POINTS TEST
// ============================================
// openTestAnnouncementModal supprimé - plus de points test

// ============================================
// SYSTÈME D'AMIS ET MESSAGERIE
// ============================================

// Données des utilisateurs simulés (pour la démo)
let allUsers = [];

// Initialiser des utilisateurs de démo
function initDemoUsers() {
  if (allUsers.length > 0) return;
  
  const demoNames = [
    "Alex_DJ", "Sophie_Techno", "Marco_Festivals", "Julie_Dance", "Thomas_Music",
    "Emma_Events", "Lucas_Party", "Léa_Vibes", "Hugo_Sound", "Camille_Beat",
    "Nathan_Bass", "Chloé_Electro", "Arthur_Rave", "Manon_House", "Théo_Groove"
  ];
  
  allUsers = demoNames.map((name, i) => {
    const avatar = AVAILABLE_AVATARS[i % AVAILABLE_AVATARS.length];
    return {
      id: `demo_user_${i + 1}`,
      name: name,
      avatar: avatar.emoji,
      avatarId: avatar.id,
      avatarDescription: `Fan de ${['techno', 'house', 'festivals', 'concerts', 'musique'][i % 5]}`,
      isOnline: Math.random() > 0.5,
      lastSeen: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString()
    };
  });
}

// Ouvrir le modal des amis
function openFriendsModal() {
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  initDemoUsers();
  
  const friendsList = currentUser.friends || [];
  const friendRequests = currentUser.friendRequests || [];
  
  // Trouver les infos des amis
  const friendsInfo = friendsList.map(friendId => {
    return allUsers.find(u => u.id === friendId) || { id: friendId, name: 'Utilisateur', avatar: '👤' };
  });
  
  const html = `
    <div style="padding:20px;max-width:550px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:40px;margin-bottom:8px;">👥</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Mes Amis</h2>
        <p style="color:var(--ui-text-muted);margin-top:6px;font-size:13px;">${friendsList.length} ami(s)</p>
      </div>
      
      <!-- Demandes d'amis en attente -->
      ${friendRequests.length > 0 ? `
        <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:14px;margin-bottom:16px;">
          <div style="font-size:13px;font-weight:600;color:#f59e0b;margin-bottom:10px;">📬 Demandes en attente (${friendRequests.length})</div>
          ${friendRequests.map(req => `
            <div style="display:flex;align-items:center;gap:10px;padding:10px;background:rgba(15,23,42,0.5);border-radius:10px;margin-bottom:8px;">
              <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:20px;">${req.fromUserAvatar || '👤'}</div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:14px;color:#fff;">${escapeHtml(req.fromUserName)}</div>
                <div style="font-size:11px;color:var(--ui-text-muted);">${new Date(req.date).toLocaleDateString('fr-FR')}</div>
              </div>
              <button onclick="acceptFriendRequest('${req.fromUserId}')" style="padding:6px 12px;border-radius:8px;border:none;background:#22c55e;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">✓</button>
              <button onclick="declineFriendRequest('${req.fromUserId}')" style="padding:6px 12px;border-radius:8px;border:none;background:#ef4444;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">✗</button>
            </div>
          `).join('')}
        </div>
      ` : ''}
      
      <!-- Rechercher des amis -->
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:13px;font-weight:600;color:#fff;margin-bottom:8px;">🔍 Rechercher des utilisateurs</label>
        <input type="text" id="search-friends-input" placeholder="Nom d'utilisateur..." 
               onkeyup="searchUsers(this.value)"
               style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
        <div id="search-friends-results" style="margin-top:10px;"></div>
      </div>
      
      <!-- Liste des amis -->
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:10px;">👫 Mes amis</div>
        ${friendsInfo.length > 0 ? friendsInfo.map(friend => `
          <div style="display:flex;align-items:center;gap:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;margin-bottom:8px;border:1px solid var(--ui-card-border);">
            <div style="position:relative;">
              <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;">${friend.avatar}</div>
              <div style="position:absolute;bottom:2px;right:2px;width:12px;height:12px;border-radius:50%;background:${friend.isOnline ? '#22c55e' : '#6b7280'};border:2px solid var(--ui-card-bg);"></div>
            </div>
            <div style="flex:1;">
              <div style="font-weight:600;font-size:14px;color:#fff;">${escapeHtml(friend.name)}</div>
              <div style="font-size:11px;color:var(--ui-text-muted);">${friend.avatarDescription || ''}</div>
            </div>
            <button onclick="openChatWith('${friend.id}')" style="padding:8px 14px;border-radius:8px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-size:12px;font-weight:600;cursor:pointer;">💬 Chat</button>
            <button onclick="removeFriend('${friend.id}')" style="padding:8px 10px;border-radius:8px;border:1px solid rgba(239,68,68,0.5);background:transparent;color:#ef4444;font-size:12px;cursor:pointer;">🗑️</button>
          </div>
        `).join('') : `
          <div style="text-align:center;padding:30px;color:var(--ui-text-muted);">
            <div style="font-size:32px;margin-bottom:8px;">🔍</div>
            <p>Vous n'avez pas encore d'amis.<br>Recherchez des utilisateurs ci-dessus !</p>
          </div>
        `}
      </div>
      
      <button onclick="closePublishModal()" style="width:100%;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
}

// Ouvrir le modal des groupes
function openGroupsModal() {
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  // Récupérer les groupes de l'utilisateur (simulation)
  const userGroups = currentUser.groups || [];
  const registeredCountry = currentUser.registeredCountry || "CH";
  
  const html = `
    <div style="padding:20px;max-width:600px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:40px;margin-bottom:8px;">👥</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Groupes</h2>
      </div>
      
      <!-- Sections principales -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
        <!-- Canaux par pays -->
        <div onclick="changeGroupCountry()" style="padding:20px;background:rgba(0,255,195,0.1);border:2px solid rgba(0,255,195,0.3);border-radius:12px;cursor:pointer;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">🌍</div>
          <div style="font-weight:600;color:#00ffc3;margin-bottom:4px;">Par Pays</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">${registeredCountry}</div>
        </div>
        
        <!-- Catégories MapEvent -->
        <div onclick="openGroupChannel('category', 'events')" style="padding:20px;background:rgba(59,130,246,0.1);border:2px solid rgba(59,130,246,0.3);border-radius:12px;cursor:pointer;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">📅</div>
          <div style="font-weight:600;color:#3b82f6;margin-bottom:4px;">Events</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">Discussion</div>
        </div>
      </div>
      
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
        <div onclick="openGroupChannel('category', 'booking')" style="padding:20px;background:rgba(139,92,246,0.1);border:2px solid rgba(139,92,246,0.3);border-radius:12px;cursor:pointer;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">🎵</div>
          <div style="font-weight:600;color:#8b5cf6;margin-bottom:4px;">Booking</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">Discussion</div>
        </div>
        
        <div onclick="openGroupChannel('category', 'services')" style="padding:20px;background:rgba(245,158,11,0.1);border:2px solid rgba(245,158,11,0.3);border-radius:12px;cursor:pointer;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">💼</div>
          <div style="font-weight:600;color:#f59e0b;margin-bottom:4px;">Services</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">Discussion</div>
        </div>
      </div>
      
      <!-- Vos groupes -->
        <div style="margin-bottom:20px;">
        <div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:10px;">👥 Vos groupes</div>
        ${userGroups.length > 0 ? userGroups.map(group => `
          <div onclick="openGroupChannel('custom', '${group.id}')" style="display:flex;align-items:center;gap:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;margin-bottom:8px;border:1px solid var(--ui-card-border);cursor:pointer;">
              <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;">${group.emoji || '👥'}</div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:14px;color:#fff;">${escapeHtml(group.name)}</div>
                <div style="font-size:11px;color:var(--ui-text-muted);">${group.memberCount || 0} membres</div>
              </div>
            </div>
        `).join('') : `
          <div style="text-align:center;padding:30px;color:var(--ui-text-muted);">
            <div style="font-size:32px;margin-bottom:8px;">🔍</div>
            <p>Vous n'avez pas encore de groupes.<br>Créez-en un ci-dessous !</p>
        </div>
        `}
      </div>
      
      <!-- Créer un groupe -->
      <div onclick="createGroup()" style="padding:20px;background:linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2));border:2px dashed rgba(0,255,195,0.5);border-radius:12px;cursor:pointer;text-align:center;margin-bottom:20px;">
        <div style="font-size:40px;margin-bottom:8px;">➕</div>
        <div style="font-weight:700;color:#00ffc3;font-size:16px;">Créer un groupe</div>
      </div>
      
      <button onclick="closePublishModal()" style="width:100%;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
}

// Mettre à jour la fonction globale avec l'implémentation complète
// Cette assignation remplace le stub défini plus tôt
window.openGroupsModal = openGroupsModal;

// Rechercher des utilisateurs
function searchUsers(query) {
  const resultsContainer = document.getElementById("search-friends-results");
  if (!resultsContainer) return;
  
  if (!query || query.length < 2) {
    resultsContainer.innerHTML = '';
    return;
  }
  
  initDemoUsers();
  
  const results = allUsers.filter(u => 
    u.name.toLowerCase().includes(query.toLowerCase()) && 
    u.id !== currentUser.id &&
    !currentUser.friends.includes(u.id)
  ).slice(0, 5);
  
  if (results.length === 0) {
    resultsContainer.innerHTML = '<div style="color:var(--ui-text-muted);font-size:12px;padding:10px;">Aucun utilisateur trouvé</div>';
    return;
  }
  
  resultsContainer.innerHTML = results.map(user => `
    <div style="display:flex;align-items:center;gap:10px;padding:10px;background:rgba(0,255,195,0.05);border-radius:10px;margin-bottom:6px;border:1px solid rgba(0,255,195,0.2);">
      <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:18px;">${user.avatar}</div>
      <div style="flex:1;">
        <div style="font-weight:600;font-size:13px;color:#fff;">${escapeHtml(user.name)}</div>
        <div style="font-size:10px;color:var(--ui-text-muted);">${user.isOnline ? '🟢 En ligne' : '⚫ Hors ligne'}</div>
      </div>
      <button onclick="sendFriendRequest('${user.id}', '${escapeHtml(user.name)}', '${user.avatar}')" style="padding:6px 12px;border-radius:8px;border:none;background:#00ffc3;color:#000;font-size:11px;font-weight:600;cursor:pointer;">+ Ajouter</button>
    </div>
  `).join('');
}

// Envoyer une demande d'ami
function sendFriendRequest(userId, userName, userAvatar) {
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  if (!currentUser.sentRequests) currentUser.sentRequests = [];
  
  if (currentUser.sentRequests.includes(userId)) {
    showNotification("⏳ Demande déjà envoyée", "info");
    return;
  }
  
  if (currentUser.friends.includes(userId)) {
    showNotification("✅ Déjà ami avec cet utilisateur", "info");
    return;
  }
  
  currentUser.sentRequests.push(userId);
  
  // Simuler l'ajout d'une demande côté destinataire (pour la démo, on accepte automatiquement)
  setTimeout(() => {
    if (!currentUser.friends.includes(userId)) {
      currentUser.friends.push(userId);
      currentUser.sentRequests = currentUser.sentRequests.filter(id => id !== userId);
      showNotification(`🎉 ${userName} a accepté votre demande d'ami !`, "success");
      saveUserData();
    }
  }, 2000);
  
  showNotification(`📤 Demande envoyée à ${userName}`, "success");
  saveUserData();
  openFriendsModal(); // Rafraîchir
}

// Accepter une demande d'ami
function acceptFriendRequest(fromUserId) {
  if (!currentUser.friendRequests) return;
  
  const request = currentUser.friendRequests.find(r => r.fromUserId === fromUserId);
  if (!request) return;
  
  // Ajouter comme ami
  if (!currentUser.friends.includes(fromUserId)) {
    currentUser.friends.push(fromUserId);
  }
  
  // Retirer de la liste des demandes
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.fromUserId !== fromUserId);
  
  showNotification(`🎉 Vous êtes maintenant ami avec ${request.fromUserName} !`, "success");
  saveUserData();
  openFriendsModal(); // Rafraîchir
}

// Refuser une demande d'ami
function declineFriendRequest(fromUserId) {
  if (!currentUser.friendRequests) return;
  
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.fromUserId !== fromUserId);
  
  showNotification("❌ Demande refusée", "info");
  saveUserData();
  openFriendsModal(); // Rafraîchir
}

// Retirer un ami
function removeFriend(friendId) {
  if (!confirm("Voulez-vous vraiment retirer cet ami ?")) return;
  
  currentUser.friends = currentUser.friends.filter(id => id !== friendId);
  
  showNotification("👋 Ami retiré", "info");
  saveUserData();
  openFriendsModal(); // Rafraîchir
}

// Ouvrir le chat avec un ami
function openChatWith(friendId) {
  initDemoUsers();
  const friend = allUsers.find(u => u.id === friendId) || { id: friendId, name: 'Utilisateur', avatar: '👤' };
  
  // Récupérer les messages existants
  const conversationKey = [currentUser.id, friendId].sort().join(':');
  if (!window.conversations) window.conversations = {};
  if (!window.conversations[conversationKey]) {
    window.conversations[conversationKey] = [
      { from: friendId, text: "Salut ! 👋", time: new Date(Date.now() - 3600000).toISOString() },
      { from: currentUser.id, text: "Hey ! Comment ça va ?", time: new Date(Date.now() - 3500000).toISOString() },
      { from: friendId, text: "Super bien, tu vas à la soirée ce weekend ?", time: new Date(Date.now() - 3400000).toISOString() }
    ];
  }
  
  const messages = window.conversations[conversationKey] || [];
  
  const html = `
    <div style="display:flex;flex-direction:column;height:70vh;max-width:500px;margin:0 auto;">
      <!-- Header -->
      <div style="display:flex;align-items:center;gap:12px;padding:16px;border-bottom:1px solid var(--ui-card-border);">
        <button onclick="openFriendsModal()" style="width:36px;height:36px;border-radius:50%;border:none;background:rgba(15,23,42,0.9);color:#fff;cursor:pointer;font-size:16px;">←</button>
        <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:22px;">${friend.avatar}</div>
        <div style="flex:1;">
          <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(friend.name)}</div>
          <div style="font-size:11px;color:${friend.isOnline ? '#22c55e' : 'var(--ui-text-muted)'};">${friend.isOnline ? '🟢 En ligne' : 'Hors ligne'}</div>
        </div>
        <button onclick="openReportModal('user', '${friendId}')" style="padding:8px;border-radius:8px;border:1px solid rgba(239,68,68,0.3);background:transparent;color:#ef4444;font-size:12px;cursor:pointer;">🚨</button>
      </div>
      
      <!-- Messages -->
      <div id="chat-messages" style="flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;">
        ${messages.map(msg => `
          <div style="display:flex;${msg.from === currentUser.id ? 'justify-content:flex-end;' : 'justify-content:flex-start;'}">
            <div style="max-width:75%;padding:10px 14px;border-radius:16px;${msg.from === currentUser.id ? 'background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;border-bottom-right-radius:4px;' : 'background:rgba(15,23,42,0.9);color:#fff;border-bottom-left-radius:4px;'}">
              <div style="font-size:14px;">${escapeHtml(msg.text)}</div>
              <div style="font-size:10px;opacity:0.7;margin-top:4px;text-align:right;">${new Date(msg.time).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
          </div>
        `).join('')}
      </div>
      
      <!-- Input -->
      <div style="padding:16px;border-top:1px solid var(--ui-card-border);display:flex;gap:10px;">
        <input type="text" id="chat-input" placeholder="Votre message..." 
               onkeypress="if(event.key==='Enter')sendChatMessage('${friendId}')"
               style="flex:1;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
        <button onclick="sendChatMessage('${friendId}')" style="width:48px;height:48px;border-radius:50%;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;cursor:pointer;font-size:20px;">➤</button>
      </div>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  
  // Scroll to bottom
  setTimeout(() => {
    const chatMessages = document.getElementById("chat-messages");
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
  }, 100);
}

// Envoyer un message
function sendChatMessage(friendId) {
  const input = document.getElementById("chat-input");
  if (!input || !input.value.trim()) return;
  
  const conversationKey = [currentUser.id, friendId].sort().join(':');
  if (!window.conversations) window.conversations = {};
  if (!window.conversations[conversationKey]) window.conversations[conversationKey] = [];
  
  window.conversations[conversationKey].push({
    from: currentUser.id,
    text: input.value.trim(),
    time: new Date().toISOString()
  });
  
  // Simuler une réponse automatique (pour la démo)
  setTimeout(() => {
    const autoResponses = [
      "Super ! 🎉",
      "Ah cool !",
      "On se retrouve là-bas ?",
      "J'ai hâte !",
      "Trop bien 👍",
      "À bientôt !"
    ];
    window.conversations[conversationKey].push({
      from: friendId,
      text: autoResponses[Math.floor(Math.random() * autoResponses.length)],
      time: new Date().toISOString()
    });
    openChatWith(friendId); // Rafraîchir
  }, 1500);
  
  openChatWith(friendId); // Rafraîchir immédiatement pour montrer notre message
}

// Sauvegarder les données utilisateur
function saveUserData() {
  try {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (e) {
    console.error('Erreur sauvegarde:', e);
  }
}

// Exposer saveUser globalement pour compatibilité
window.saveUser = saveUserData;

// Récupérer les amis qui participent à un événement
function getFriendsParticipatingToEvent(eventId) {
  if (!currentUser.isLoggedIn || !currentUser.friends || currentUser.friends.length === 0) {
    return [];
  }
  
  initDemoUsers();
  
  // Simuler que certains amis participent à des événements (pour la démo)
  // Dans la vraie implémentation, cela viendrait du backend
  const friendsParticipating = [];
  
  currentUser.friends.forEach(friendId => {
    // Simuler une participation aléatoire basée sur l'ID de l'événement
    const hashCode = (str) => {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }
      return Math.abs(hash);
    };
    
    const combinedHash = hashCode(`${friendId}:${eventId}`);
    const participates = combinedHash % 5 === 0; // ~20% de chance de participer
    
    if (participates) {
      const friend = allUsers.find(u => u.id === friendId);
      if (friend) {
        friendsParticipating.push({
          id: friend.id,
          name: friend.name,
          avatar: friend.avatar
        });
      }
    }
  });
  
  return friendsParticipating;
}

// Charger l'utilisateur sauvegardé au démarrage
// REMOVED: loadSavedUser() est maintenant dans auth.js et exposé via window.loadSavedUser

// Fonctions helper pour le modal compte
function acceptFriendRequest(requestId) {
  const request = currentUser.friendRequests?.find(r => r.id === requestId);
  if (!request) return;
  
  // Ajouter aux amis
  if (!currentUser.friends) currentUser.friends = [];
  currentUser.friends.push({
    id: request.fromUserId,
    name: request.fromUserName,
    avatar: request.fromUserAvatar,
    username: request.username
  });
  
  // Retirer de la liste des demandes
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.id !== requestId);
  
  // Sauvegarder
  localStorage.setItem('currentUser', JSON.stringify(currentUser));
  showNotification(`✅ ${request.fromUserName} ajouté(e) à vos amis !`, 'success');
  
  // Rafraîchir le modal
  showAccountModalTab('amis');
}

function rejectFriendRequest(requestId) {
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.id !== requestId);
  localStorage.setItem('currentUser', JSON.stringify(currentUser));
  showNotification('Demande d\'ami refusée', 'info');
  showAccountModalTab('amis');
}

function openUserProfile(userId) {
  showNotification('Profil utilisateur à venir', 'info');
  // TODO: Implémenter l'ouverture du profil utilisateur
}

function openGroupDetails(groupId) {
  showNotification('Détails du groupe à venir', 'info');
  // TODO: Implémenter l'ouverture des détails du groupe
}

// ============================================
// COMPTE UTILISATEUR COMPLET - DESIGN PREMIUM
// ============================================
// Variable pour gérer l'onglet actif du modal Compte
let accountModalActiveTab = 'agenda';

function openAccountModal() {
  console.log('[ACCOUNT MODAL] openAccountModal appelée', {
    currentUser: currentUser ? { isLoggedIn: currentUser.isLoggedIn, email: currentUser.email } : null,
    getUserDisplayName: typeof getUserDisplayName,
    getUserAvatar: typeof getUserAvatar,
    windowGetUserDisplayName: typeof window.getUserDisplayName,
    windowGetUserAvatar: typeof window.getUserAvatar
  });
  
  if (!currentUser || !currentUser.isLoggedIn) {
    console.log('[ACCOUNT MODAL] Utilisateur non connecté, ouverture modal login');
    openAuthModal('login');
    return;
  }
  
  let backdrop = document.getElementById('publish-modal-backdrop');
  let modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.id = 'publish-modal-backdrop';
      backdrop.style.cssText = 'position:fixed!important;inset:0!important;background:rgba(0,0,0,0.8)!important;z-index:99999!important;display:flex!important;align-items:center!important;justify-content:center!important;visibility:visible!important;opacity:1!important;padding:40px!important;box-sizing:border-box!important;';
      backdrop.onclick = function(e) {
        if (e.target === backdrop) closePublishModal();
      };
      document.body.appendChild(backdrop);
    }
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'publish-modal-inner';
      modal.style.cssText = 'background:#1e293b!important;border-radius:20px!important;padding:0!important;max-width:600px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;';
      if (backdrop) backdrop.appendChild(modal);
    }
  }
  if (!backdrop || !modal) {
    console.error('[ACCOUNT MODAL] Impossible de créer les éléments modal');
    return;
  }
  
  // Obtenir le nom d'affichage (utiliser window.getUserDisplayName si disponible)
  const getUserDisplayNameFunc = window.getUserDisplayName || getUserDisplayName;
  const getUserAvatarFunc = window.getUserAvatar || getUserAvatar;
  
  if (typeof getUserDisplayNameFunc !== 'function') {
    console.error('[ACCOUNT MODAL] getUserDisplayName n\'est pas une fonction');
    return;
  }
  if (typeof getUserAvatarFunc !== 'function') {
    console.error('[ACCOUNT MODAL] getUserAvatar n\'est pas une fonction');
    return;
  }
  
  // FORCER l'utilisation du username, jamais l'email
  // DEBUG: Vérifier les données de currentUser AVANT traitement
  console.log('[ACCOUNT MODAL] currentUser AVANT traitement:', JSON.stringify({
    username: currentUser.username,
    email: currentUser.email,
    name: currentUser.name,
    profile_photo_url: currentUser.profile_photo_url ? currentUser.profile_photo_url.substring(0, 50) + '...' : null,
    profilePhoto: currentUser.profilePhoto ? currentUser.profilePhoto.substring(0, 50) + '...' : null,
    isLoggedIn: currentUser.isLoggedIn
  }));
  
  let displayName = currentUser.username || currentUser.name || 'Compte';
  if (!displayName || displayName === currentUser.email || displayName.includes('@')) {
    // Si c'est l'email ou vide, utiliser le username ou "Compte"
    displayName = currentUser.username || 'Compte';
  }
  
  // Si toujours pas de username, essayer de le récupérer depuis le storage
  if (!displayName || displayName === 'Compte') {
    try {
      const storedUser = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
      if (storedUser) {
        const parsed = JSON.parse(storedUser);
        displayName = parsed.username || parsed.name || 'Compte';
        console.log('[ACCOUNT MODAL] Username récupéré depuis storage:', displayName);
        // Mettre à jour currentUser avec les données du storage
        if (parsed.username && !currentUser.username) {
          currentUser.username = parsed.username;
        }
        if (parsed.profile_photo_url && !currentUser.profile_photo_url) {
          currentUser.profile_photo_url = parsed.profile_photo_url;
        }
      }
    } catch (e) {
      console.warn('[ACCOUNT MODAL] Erreur récupération storage:', e);
    }
  }
  
  // Nettoyer le nom (enlever caractères spéciaux) - utiliser une fonction locale si cleanAccountText n'est pas disponible
  if (typeof cleanAccountText === 'function') {
    displayName = cleanAccountText(displayName) || 'Compte';
  } else {
    // Fallback : nettoyer manuellement
    displayName = displayName.replace(/[<>]/g, '').trim() || 'Compte';
  }
  
  const avatar = getUserAvatarFunc();
  
  console.log('[ACCOUNT MODAL] displayName final:', displayName, 'avatar:', avatar ? avatar.substring(0, 50) + '...' : 'null', 'currentUser.username:', currentUser.username);
  
  // Fonction pour créer un avatar avec initiales (style Facebook)
  function getInitialsAvatar(name) {
    if (!name || name === "Compte") return "👤";
    const parts = name.trim().split(/\s+/);
    let initials = "";
    if (parts.length >= 2) {
      initials = (parts[0][0] || "").toUpperCase() + (parts[parts.length - 1][0] || "").toUpperCase();
    } else if (parts.length === 1) {
      initials = parts[0].substring(0, 2).toUpperCase();
    }
    if (!initials) return "👤";
    
    // Couleur de fond basée sur le nom (pour avoir toujours la même couleur pour le même nom)
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
      '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52BE80'
    ];
    const colorIndex = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
    const bgColor = colors[colorIndex];
    
    return `<div style="width:100%;height:100%;border-radius:50%;background:${bgColor};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:32px;text-transform:uppercase;">${initials}</div>`;
  }
  
  // Créer un avatar avec la première lettre du nom (comme Facebook) si pas de photo
  let avatarDisplay;
  
  // DEBUG: Vérifier toutes les sources possibles de l'avatar
  console.log('[ACCOUNT MODAL] Avatar check - TOUTES les sources:', {
    avatar: avatar ? avatar.substring(0, 50) + '...' : 'null',
    profile_photo_url: currentUser.profile_photo_url ? currentUser.profile_photo_url.substring(0, 50) + '...' : 'null',
    profilePhoto: currentUser.profilePhoto ? currentUser.profilePhoto.substring(0, 50) + '...' : 'null',
    isHttp: avatar && avatar.startsWith('http'),
    isData: avatar && avatar.startsWith('data:image'),
    avatarLength: avatar ? avatar.length : 0
  });
  
  // Essayer de récupérer l'avatar depuis currentUser si pas trouvé dans avatar
  let finalAvatar = avatar;
  if ((!finalAvatar || finalAvatar === "👤") && currentUser.profile_photo_url) {
    finalAvatar = currentUser.profile_photo_url;
    console.log('[ACCOUNT MODAL] Avatar récupéré depuis currentUser.profile_photo_url');
  }
  if ((!finalAvatar || finalAvatar === "👤") && currentUser.profilePhoto) {
    finalAvatar = currentUser.profilePhoto;
    console.log('[ACCOUNT MODAL] Avatar récupéré depuis currentUser.profilePhoto');
  }
  
  if (finalAvatar && finalAvatar !== "👤" && (finalAvatar.startsWith('http') || finalAvatar.startsWith('data:image'))) {
    // Utiliser directement l'URL - échapper seulement les guillemets doubles pour l'attribut HTML
    const safeAvatar = finalAvatar.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    // Obtenir les initiales et la couleur pour le fallback
    const initials = getInitials(displayName);
    const bgColor = getInitialsColor(displayName);
    // Créer un conteneur avec l'image et un fallback caché
    avatarDisplay = `<div style="position:relative;width:100%;height:100%;"><img src="${safeAvatar}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;position:absolute;top:0;left:0;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';" /><div style="display:none;width:100%;height:100%;border-radius:50%;background:${bgColor};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:32px;text-transform:uppercase;position:absolute;top:0;left:0;">${initials}</div></div>`;
    console.log('[ACCOUNT MODAL] Avatar URL utilisée:', safeAvatar.substring(0, 100) + '...');
  } else {
    // Si pas de photo, afficher les initiales (comme Facebook)
    console.log('[ACCOUNT MODAL] Pas de photo valide, utilisation initiales pour:', displayName);
    avatarDisplay = getInitialsAvatar(displayName);
  }
  
  // Fonction helper pour obtenir les initiales
  function getInitials(name) {
    if (!name || name === "Compte") return "👤";
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] || "").toUpperCase() + (parts[parts.length - 1][0] || "").toUpperCase();
    } else if (parts.length === 1) {
      return parts[0].substring(0, 2).toUpperCase();
    }
    return "👤";
  }
  
  // Fonction helper pour obtenir la couleur
  function getInitialsColor(name) {
    if (!name || name === "Compte") return '#4ECDC4';
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
      '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52BE80'
    ];
    const colorIndex = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
    return colors[colorIndex];
  }
  
  console.log('[ACCOUNT MODAL] Données préparées', { 
    displayName, 
    avatar: avatar ? avatar.substring(0, 50) + '...' : 'null',
    avatarDisplay: avatarDisplay ? avatarDisplay.substring(0, 100) + '...' : 'null',
    currentUser: currentUser ? {
      username: currentUser.username,
      email: currentUser.email,
      profile_photo_url: currentUser.profile_photo_url ? currentUser.profile_photo_url.substring(0, 50) + '...' : 'null',
      profilePhoto: currentUser.profilePhoto ? currentUser.profilePhoto.substring(0, 50) + '...' : 'null'
    } : null
  });
  
  // FORCER l'affichage du nom d'utilisateur - ne jamais utiliser l'email
  const finalDisplayName = displayName && displayName !== 'Compte' && !displayName.includes('@') ? displayName : (currentUser.username || 'Compte');
  console.log('[ACCOUNT MODAL] finalDisplayName:', finalDisplayName, 'displayName original:', displayName);
  
  const html = `
    <div style="padding:40px;max-width:600px;margin:0 auto;text-align:center;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closePublishModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <!-- En-tête avec avatar et nom -->
      <div style="margin-bottom:32px;">
        <div style="width:80px;height:80px;border-radius:50%;margin:0 auto 16px;background:rgba(0,255,195,0.1);border:3px solid rgba(0,255,195,0.3);display:flex;align-items:center;justify-content:center;font-size:40px;overflow:hidden;">
          ${avatarDisplay}
        </div>
        <h2 style="margin:0;font-size:24px;font-weight:700;color:#fff;" id="account-modal-display-name">${escapeHtml(finalDisplayName)}</h2>
        <p style="margin:8px 0 0;font-size:13px;color:var(--ui-text-muted);">${currentUser.email || ''}</p>
      </div>
      
      <!-- Blocs cliquables - OUVERTURE FENÊTRES EXTERNES -->
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:24px;">
        <div onclick="closePublishModal();setTimeout(() => openAgendaModal(), 300);" style="padding:24px;border-radius:16px;background:rgba(15,23,42,0.5);border:2px solid rgba(255,255,255,0.1);cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';this.style.transform='translateY(-2px)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';this.style.transform='translateY(0)';">
          <div style="font-size:32px;margin-bottom:8px;">📅</div>
          <div style="font-weight:600;font-size:14px;color:#fff;">Agenda</div>
        </div>
        
        <div onclick="openAccountWindow('amis')" style="padding:24px;border-radius:16px;background:rgba(15,23,42,0.5);border:2px solid rgba(255,255,255,0.1);cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';this.style.transform='translateY(-2px)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';this.style.transform='translateY(0)';">
          <div style="font-size:32px;margin-bottom:8px;">👥</div>
          <div style="font-weight:600;font-size:14px;color:#fff;">Amis</div>
        </div>
        
        <div onclick="openAccountWindow('notifications')" style="padding:24px;border-radius:16px;background:rgba(15,23,42,0.5);border:2px solid rgba(255,255,255,0.1);cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';this.style.transform='translateY(-2px)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';this.style.transform='translateY(0)';">
          <div style="font-size:32px;margin-bottom:8px;">🔔</div>
          <div style="font-weight:600;font-size:14px;color:#fff;">Notifications</div>
        </div>
        
        <div onclick="openAccountWindow('parametres')" style="padding:24px;border-radius:16px;background:rgba(15,23,42,0.5);border:2px solid rgba(255,255,255,0.1);cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';this.style.transform='translateY(-2px)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';this.style.transform='translateY(0)';">
          <div style="font-size:32px;margin-bottom:8px;">⚙️</div>
          <div style="font-weight:600;font-size:14px;color:#fff;">Paramètres</div>
        </div>
        
        <div onclick="openAccountWindow('profil')" style="padding:24px;border-radius:16px;background:rgba(15,23,42,0.5);border:2px solid rgba(255,255,255,0.1);cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';this.style.transform='translateY(-2px)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';this.style.transform='translateY(0)';">
          <div style="font-size:32px;margin-bottom:8px;">👤</div>
          <div style="font-weight:600;font-size:14px;color:#fff;">Profil</div>
        </div>
        
        <div onclick="event.stopPropagation(); openAccountWindow('modifier-profil')" style="padding:24px;border-radius:16px;background:rgba(15,23,42,0.5);border:2px solid rgba(255,255,255,0.1);cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';this.style.transform='translateY(-2px)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';this.style.transform='translateY(0)';">
          <div style="font-size:32px;margin-bottom:8px;">✏️</div>
          <div style="font-weight:600;font-size:14px;color:#fff;">Modifier mon profil</div>
        </div>
        
        <div onclick="event.stopPropagation(); openAccountWindow('mes-annonces')" style="padding:24px;border-radius:16px;background:rgba(15,23,42,0.5);border:2px solid rgba(139,92,246,0.3);cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(139,92,246,0.6)';this.style.background='rgba(139,92,246,0.15)';this.style.transform='translateY(-2px)';" onmouseout="this.style.borderColor='rgba(139,92,246,0.3)';this.style.background='rgba(15,23,42,0.5)';this.style.transform='translateY(0)';">
          <div style="font-size:32px;margin-bottom:8px;">📢</div>
          <div style="font-weight:600;font-size:14px;color:#fff;">Mes annonces</div>
        </div>
        
        <div onclick="closePublishModal();setTimeout(() => openMapFriendModal(), 300);" style="padding:24px;border-radius:16px;background:rgba(15,23,42,0.5);border:2px solid rgba(59,130,246,0.3);cursor:pointer;transition:all 0.3s;grid-column:span 2;" onmouseover="this.style.borderColor='rgba(59,130,246,0.6)';this.style.background='rgba(59,130,246,0.15)';this.style.transform='translateY(-2px)';" onmouseout="this.style.borderColor='rgba(59,130,246,0.3)';this.style.background='rgba(15,23,42,0.5)';this.style.transform='translateY(0)';">
          <div style="font-size:32px;margin-bottom:8px;">🌐</div>
          <div style="font-weight:600;font-size:14px;color:#fff;">Map Friend</div>
          <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Fil social - Partage d'events et messages</div>
        </div>
      </div>
      
      <!-- Zone de contenu - Option "Rester connecté" -->
      <div id="account-block-content" style="min-height:120px;padding:20px;border-radius:16px;background:rgba(15,23,42,0.3);border:1px solid rgba(255,255,255,0.1);">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:16px;border-radius:12px;background:rgba(0,255,195,0.05);border:1px solid rgba(0,255,195,0.2);">
          <div style="display:flex;align-items:center;gap:12px;">
            <div style="font-size:24px;">🔐</div>
            <div>
              <div style="font-weight:600;font-size:14px;color:#fff;margin-bottom:4px;">Rester connecté pour la prochaine fois</div>
              <div style="font-size:12px;color:var(--ui-text-muted);">Vous serez automatiquement reconnecté</div>
            </div>
          </div>
          <label style="position:relative;display:inline-block;width:48px;height:24px;cursor:pointer;">
            <input type="checkbox" id="account-remember-me-toggle" style="opacity:0;width:0;height:0;" />
            <span id="account-remember-me-slider" style="position:absolute;top:0;left:0;right:0;bottom:0;background-color:rgba(255,255,255,0.2);border-radius:24px;transition:all 0.3s;"></span>
            <span id="account-remember-me-knob" style="position:absolute;top:2px;left:2px;width:20px;height:20px;background-color:#fff;border-radius:50%;transition:all 0.3s;box-shadow:0 2px 4px rgba(0,0,0,0.2);"></span>
          </label>
        </div>
      </div>
      
      <!-- Bouton Installation PWA (visible uniquement sur mobile) -->
      <button id="account-pwa-install-btn" style="display:none;width:100%;margin-top:24px;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#667eea,#764ba2);color:white;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.opacity='0.9';" onmouseout="this.style.opacity='1';">
        📱 Installer l'app mobile
      </button>
      
      <!-- Blocs supplémentaires pour mobile (cachés sur desktop) -->
      <div id="account-mobile-extras" style="display:none;margin-top:16px;padding-top:16px;border-top:1px solid rgba(148,163,184,0.2);">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;text-transform:uppercase;letter-spacing:1px;">Plus d'options</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
          <button onclick="openSubscriptionView()" style="padding:12px;border-radius:10px;border:1px solid rgba(148,163,184,0.3);background:rgba(255,255,255,0.05);color:var(--ui-text-main);cursor:pointer;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:4px;">
            <span style="font-size:18px;">💎</span>
            <span>Abos</span>
          </button>
          <button onclick="openProximityAlertsView()" style="padding:12px;border-radius:10px;border:1px solid rgba(148,163,184,0.3);background:rgba(255,255,255,0.05);color:var(--ui-text-main);cursor:pointer;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:4px;">
            <span style="font-size:18px;">🔔</span>
            <span>Alertes</span>
          </button>
          <button onclick="openCartModal()" style="padding:12px;border-radius:10px;border:1px solid rgba(148,163,184,0.3);background:rgba(255,255,255,0.05);color:var(--ui-text-main);cursor:pointer;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:4px;">
            <span style="font-size:18px;">🛒</span>
            <span>Panier</span>
          </button>
          <button onclick="openEcoMissionModal()" style="padding:12px;border-radius:10px;border:1px solid rgba(148,163,184,0.3);background:rgba(255,255,255,0.05);color:var(--ui-text-main);cursor:pointer;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:4px;">
            <span style="font-size:18px;">🌍</span>
            <span>Sauver la Terre</span>
          </button>
        </div>
      </div>
      
      <button id="account-logout-btn" style="width:100%;margin-top:24px;padding:12px;border-radius:12px;border:2px solid rgba(239,68,68,0.3);background:rgba(239,68,68,0.1);color:#ef4444;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.borderColor='rgba(239,68,68,0.5)';" onmouseout="this.style.background='rgba(239,68,68,0.1)';this.style.borderColor='rgba(239,68,68,0.3)';">
        Se déconnecter
      </button>
      
      <button id="account-delete-btn" style="width:100%;margin-top:12px;padding:12px;border-radius:12px;border:2px solid rgba(239,68,68,0.2);background:transparent;color:var(--ui-text-muted);font-weight:500;font-size:13px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.color='#ef4444';this.style.borderColor='rgba(239,68,68,0.4)';" onmouseout="this.style.color='var(--ui-text-muted)';this.style.borderColor='rgba(239,68,68,0.2)';">
        🗑️ Supprimer mon compte
      </button>
    </div>
  `;
  
  modal.innerHTML = html;
  modal.style.display = 'block';
  modal.style.visibility = 'visible';
  modal.style.opacity = '1';
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.opacity = '1';
  backdrop.style.zIndex = '9999';
  
  // ⚠️⚠️⚠️ CRITIQUE : Attacher les event listeners après injection HTML (CSP)
  setTimeout(() => {
    const logoutBtn = document.getElementById('account-logout-btn');
    const deleteBtn = document.getElementById('account-delete-btn');
    const rememberMeToggle = document.getElementById('account-remember-me-toggle');
    const rememberMeSlider = document.getElementById('account-remember-me-slider');
    const rememberMeKnob = document.getElementById('account-remember-me-knob');
    const pwaInstallBtn = document.getElementById('account-pwa-install-btn');
    const mobileExtras = document.getElementById('account-mobile-extras');
    
    // Afficher les éléments mobile si on est sur mobile
    const isMobile = window.innerWidth <= 768;
    if (isMobile) {
      // Afficher les extras mobile (abos, alertes, panier, etc.)
      if (mobileExtras) {
        mobileExtras.style.display = 'block';
      }
      
      // Afficher le bouton d'installation PWA si disponible
      if (pwaInstallBtn && (window.pwaInstallPrompt || !window.isPWAInstalled)) {
        pwaInstallBtn.style.display = 'block';
        pwaInstallBtn.addEventListener('click', () => {
          if (typeof window.installPWA === 'function') {
            window.installPWA();
          }
        });
      }
    }
    
    // Initialiser le toggle "Rester connecté" avec la valeur actuelle
    const currentRememberMe = localStorage.getItem('rememberMe') === 'true';
    if (rememberMeToggle) {
      rememberMeToggle.checked = currentRememberMe;
      updateRememberMeToggleUI(currentRememberMe, rememberMeSlider, rememberMeKnob);
    }
    
    // Event listener pour le toggle "Rester connecté"
    if (rememberMeToggle) {
      rememberMeToggle.addEventListener('change', (e) => {
        const checked = e.target.checked;
        localStorage.setItem('rememberMe', checked ? 'true' : 'false');
        updateRememberMeToggleUI(checked, rememberMeSlider, rememberMeKnob);
        console.log('[ACCOUNT MODAL] "Rester connecté" changé:', checked);
        if (typeof showNotification === 'function') {
          showNotification(checked ? '✅ Vous serez reconnecté automatiquement' : 'ℹ️ Vous devrez vous reconnecter à la prochaine visite', 'info');
        }
      });
    }
    
    // Fonction helper pour mettre à jour l'UI du toggle
    function updateRememberMeToggleUI(checked, slider, knob) {
      if (slider && knob) {
        if (checked) {
          slider.style.backgroundColor = 'rgba(0,255,195,0.5)';
          knob.style.transform = 'translateX(24px)';
          knob.style.backgroundColor = '#00ffc3';
        } else {
          slider.style.backgroundColor = 'rgba(255,255,255,0.2)';
          knob.style.transform = 'translateX(0)';
          knob.style.backgroundColor = '#fff';
        }
      }
    }
    
    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('[ACCOUNT MODAL] Bouton "Se déconnecter" cliqué');
        // ⚠️⚠️⚠️ FLUX STANDARD : Déconnexion simple (sans demander "rester connecté")
        // La valeur du toggle est déjà sauvegardée dans localStorage
        if (typeof window.logout === 'function') {
          window.logout();
        } else if (typeof window.performLogout === 'function') {
          // Utiliser la valeur actuelle du toggle pour la déconnexion
          const rememberMeValue = rememberMeToggle ? rememberMeToggle.checked : false;
          console.log('[ACCOUNT MODAL] Déconnexion avec rememberMe:', rememberMeValue);
          
          // ⚠️⚠️⚠️ DÉCONNEXION COMPLÈTE : Rafraîchir la page pour réinitialiser tout
          if (!rememberMeValue) {
            console.log('[ACCOUNT MODAL] ✅ Déconnexion complète - Rafraîchissement de la page');
            window.performLogout(false);
            // Attendre un peu pour que la déconnexion se termine, puis rafraîchir
            setTimeout(() => {
              window.location.reload();
            }, 300);
          } else {
            // Déconnexion avec "rester connecté" activé - pas de rafraîchissement
            window.performLogout(true);
          }
        } else {
          console.error('[ACCOUNT MODAL] ❌ Fonction logout non trouvée');
          alert('Erreur: fonction de déconnexion non disponible');
        }
      }, { capture: true });
    }
    
    if (deleteBtn) {
      deleteBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('[ACCOUNT MODAL] Bouton "Supprimer mon compte" cliqué');
        if (typeof showDeleteAccountConfirmation === 'function') {
          showDeleteAccountConfirmation();
        } else {
          console.error('[ACCOUNT MODAL] ❌ Fonction showDeleteAccountConfirmation non trouvée');
        }
      }, { capture: true });
    }
    
    console.log('[ACCOUNT MODAL] ✅ Event listeners attachés', { logoutBtn: !!logoutBtn, deleteBtn: !!deleteBtn, rememberMeToggle: !!rememberMeToggle });
  }, 100);
  
  console.log('[ACCOUNT MODAL] Modal affiché', {
    backdropDisplay: backdrop.style.display,
    modalDisplay: modal.style.display,
    htmlLength: html.length,
    backdropComputed: window.getComputedStyle(backdrop).display,
    modalComputed: window.getComputedStyle(modal).display
  });
}

// Fonction pour afficher la confirmation de suppression de compte
function showDeleteAccountConfirmation() {
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) return;
  
  const html = `
    <div style="padding:40px;max-width:500px;margin:0 auto;text-align:center;">
      <div style="font-size:64px;margin-bottom:20px;">⚠️</div>
      <h2 style="margin:0 0 16px;font-size:24px;font-weight:700;color:#fff;">Supprimer mon compte</h2>
      <p style="margin:0 0 24px;font-size:14px;color:var(--ui-text-muted);line-height:1.6;">
        Cette action est <strong style="color:#ef4444;">irréversible</strong>. Toutes vos données seront définitivement supprimées :
      </p>
      <ul style="text-align:left;margin:0 0 24px;padding-left:20px;color:var(--ui-text-muted);font-size:13px;line-height:2;">
        <li>Votre profil et vos informations personnelles</li>
        <li>Tous vos événements créés</li>
        <li>Vos avis et commentaires</li>
        <li>Vos favoris et participations</li>
        <li>Vos alertes et notifications</li>
      </ul>
      <p style="margin:0 0 24px;font-size:13px;color:var(--ui-text-muted);">
        Êtes-vous sûr de vouloir continuer ?
      </p>
      <div style="display:flex;gap:12px;">
        <button onclick="closePublishModal();" style="flex:1;padding:12px;border-radius:12px;border:2px solid rgba(255,255,255,0.2);background:transparent;color:#fff;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.4)';this.style.background='rgba(255,255,255,0.1)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.2)';this.style.background='transparent';">
          Annuler
        </button>
        <button onclick="confirmDeleteAccount();" style="flex:1;padding:12px;border-radius:12px;border:none;background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff;font-weight:700;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.transform='scale(1.02)';this.style.boxShadow='0 4px 12px rgba(239,68,68,0.4)';" onmouseout="this.style.transform='scale(1)';this.style.boxShadow='none';">
          Oui, supprimer
        </button>
      </div>
    </div>
  `;
  
  modal.innerHTML = html;
}

// Fonction pour confirmer et exécuter la suppression du compte
async function confirmDeleteAccount() {
  if (!currentUser || !currentUser.isLoggedIn) {
    showNotification('❌ Vous devez être connecté pour supprimer votre compte', 'error');
    return;
  }
  
  // Demander une confirmation finale
  const finalConfirm = confirm('⚠️ DERNIÈRE CONFIRMATION\n\nCette action supprimera définitivement votre compte et toutes vos données.\n\nCette action est IRRÉVERSIBLE.\n\nVoulez-vous vraiment continuer ?');
  
  if (!finalConfirm) {
    return;
  }
  
  try {
    showNotification('🗑️ Suppression du compte en cours...', 'info');
    
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
    if (!token) {
      showNotification('❌ Token d\'authentification manquant', 'error');
      return;
    }
    
    const response = await fetch(`${window.API_BASE_URL}/user/account`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        confirm: true
      })
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      if (result.code === 'CONFIRMATION_REQUIRED') {
        showNotification('❌ Confirmation requise pour supprimer le compte', 'error');
      } else {
        showNotification(`❌ Erreur: ${result.error || 'Impossible de supprimer le compte'}`, 'error');
      }
      return;
    }
    
    // Suppression réussie - tout supprimer (compte n'existe plus)
    showNotification('✅ Compte supprimé avec succès', 'success');
    
    localStorage.removeItem('currentUser');
    sessionStorage.removeItem('currentUser');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('rememberMe');
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('rememberMe');
    
    currentUser = getDefaultUser();
    currentUser = null;
    
    // Fermer le modal
    closePublishModal();
    
    // Recharger la page après 2 secondes
    setTimeout(() => {
      window.location.reload();
    }, 2000);
    
  } catch (error) {
    console.error('Erreur suppression compte:', error);
    showNotification('❌ Erreur lors de la suppression du compte. Veuillez réessayer.', 'error');
  }
}

// Fonction pour ouvrir une fenêtre externe pour chaque bloc
function openAccountWindow(blockType) {
  console.log('[ACCOUNT WINDOW] Ouverture fenêtre pour:', blockType);
  
  // ⚠️⚠️⚠️ CRITIQUE : Ne pas fermer le modal si c'est pour modifier-profil
  // Car openEditProfileModal a besoin que le modal soit ouvert
  if (blockType !== 'modifier-profil') {
    closePublishModal();
  }
  
  // Créer une nouvelle fenêtre avec le contenu du bloc
  const windowFeatures = 'width=600,height=700,scrollbars=yes,resizable=yes';
  const windowName = `account_${blockType}_${Date.now()}`;
  
  // Créer le HTML pour la fenêtre
  let windowContent = '';
  
  if (blockType === 'agenda') {
    const agendaItems = (currentUser.agenda || []).map(key => {
      const [type, id] = key.split(":");
      const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
      return data.find(i => i.id === parseInt(id));
    }).filter(Boolean);
    
    windowContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Mon Agenda - MapEvent</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 20px; }
          h1 { margin: 0 0 20px; font-size: 24px; }
        </style>
      </head>
      <body>
        <h1>📅 Mon Agenda</h1>
        ${agendaItems.length === 0 ? '<p>Votre agenda est vide</p>' : agendaItems.map(item => `<div style="padding:12px;margin-bottom:8px;background:rgba(15,23,42,0.5);border-radius:8px;">${escapeHtml(item.title || item.name || 'Sans titre')}</div>`).join('')}
      </body>
      </html>
    `;
  } else if (blockType === 'amis') {
    openFriendsModal();
    return;
  } else if (blockType === 'notifications') {
    openNotificationsModal();
    return;
  } else if (blockType === 'modifier-profil') {
    // ⚠️⚠️⚠️ CRITIQUE : Pour modifier-profil, afficher le formulaire dans le modal au lieu d'une nouvelle fenêtre
    console.log('[ACCOUNT WINDOW] modifier-profil détecté - Affichage dans modal au lieu de nouvelle fenêtre');
    
    // Essayer d'abord showAccountBlockContent (affiche dans le modal)
    if (typeof showAccountBlockContent === 'function') {
      console.log('[ACCOUNT WINDOW] Utilisation showAccountBlockContent pour modifier-profil');
      showAccountBlockContent('modifier-profil');
      return; // Ne pas ouvrir de nouvelle fenêtre
    }
    
    // Fallback : ouvrir le formulaire d'édition complet
    if (typeof window.openEditProfileModal === 'function') {
      console.log('[ACCOUNT WINDOW] Utilisation window.openEditProfileModal (fallback)');
      window.openEditProfileModal();
      return;
    } else if (typeof openEditProfileModal === 'function') {
      console.log('[ACCOUNT WINDOW] Utilisation openEditProfileModal (fallback)');
      openEditProfileModal();
      return;
    } else {
      console.error('[ACCOUNT WINDOW] ❌ Aucune fonction disponible pour modifier-profil');
      showNotification('⚠️ Fonctionnalité en cours de développement', 'info');
      return;
    }
  } else if (blockType === 'mes-annonces') {
    // ✅ MES ANNONCES - Afficher dans un modal
    console.log('[ACCOUNT WINDOW] mes-annonces détecté - Ouverture du modal Mes annonces');
    showMesAnnoncesModal();
    return;
  } else {
    // Pour les autres blocs, utiliser showAccountBlockContent dans une nouvelle fenêtre
    windowContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${blockType} - MapEvent</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 20px; }
        </style>
      </head>
      <body>
        <p>Fonctionnalité à venir</p>
      </body>
      </html>
    `;
  }
  
  try {
    const newWindow = window.open('', windowName, windowFeatures);
    if (newWindow) {
      newWindow.document.write(windowContent);
      newWindow.document.close();
      console.log('[ACCOUNT WINDOW] Fenêtre ouverte avec succès:', windowName);
    } else {
      console.error('[ACCOUNT WINDOW] Échec ouverture fenêtre - popup bloquée?');
      alert('Veuillez autoriser les popups pour cette fonctionnalité');
    }
  } catch (e) {
    console.error('[ACCOUNT WINDOW] Erreur ouverture fenêtre:', e);
    alert('Erreur lors de l\'ouverture de la fenêtre: ' + e.message);
  }
}

// Fonction pour demander "rester connecté" avant déconnexion
function askRememberMeBeforeLogout() {
  console.log('[LOGOUT] Demande "rester connecté" avant déconnexion');
  
  // Trouver le modal pour afficher la question (NE PAS FERMER AVANT)
  const modal = document.getElementById('publish-modal-inner');
  const backdrop = document.getElementById('publish-modal-backdrop');
  
  if (!modal || !backdrop) {
    console.error('[LOGOUT] Modal non trouvé, déconnexion directe');
    if (typeof window.logout === 'function') {
      window.logout();
    }
    return;
  }
  
  const rememberMeHtml = `
    <div style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
      <!-- Bouton X pour fermer -->
      <button onclick="closePublishModal();" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <div style="font-size:48px;margin-bottom:24px;">👋</div>
      <h2 style="margin:0 0 16px;font-size:24px;font-weight:700;color:#fff;">Voulez-vous rester connecté ?</h2>
      <p style="margin:0 0 32px;font-size:14px;color:var(--ui-text-muted);line-height:1.6;">
        Si vous choisissez "Oui", vous resterez connecté pour la prochaine fois.<br>
        Si vous choisissez "Non", vous devrez vous reconnecter à chaque visite.
      </p>
      
      <div style="display:flex;gap:12px;justify-content:center;">
        <button id="logout-yes-btn" style="flex:1;padding:14px;border-radius:12px;border:2px solid rgba(34,197,94,0.5);background:rgba(34,197,94,0.1);color:#22c55e;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.background='rgba(34,197,94,0.2)';this.style.borderColor='rgba(34,197,94,0.7)';" onmouseout="this.style.background='rgba(34,197,94,0.1)';this.style.borderColor='rgba(34,197,94,0.5)';">
          Oui, rester connecté
        </button>
        <button id="logout-no-btn" style="flex:1;padding:14px;border-radius:12px;border:2px solid rgba(239,68,68,0.5);background:rgba(239,68,68,0.1);color:#ef4444;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.borderColor='rgba(239,68,68,0.7)';" onmouseout="this.style.background='rgba(239,68,68,0.1)';this.style.borderColor='rgba(239,68,68,0.5)';">
          Non, me déconnecter
        </button>
      </div>
      
      <button onclick="closePublishModal();" style="margin-top:16px;padding:10px 20px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:transparent;color:var(--ui-text-muted);font-weight:500;font-size:13px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.background='rgba(255,255,255,0.1)';" onmouseout="this.style.background='transparent';">
        Annuler
      </button>
    </div>
  `;
  
  // Injecter le HTML dans le modal
  modal.innerHTML = rememberMeHtml;
  
  // FORCER l'affichage du modal
  modal.style.display = 'block';
  modal.style.visibility = 'visible';
  modal.style.opacity = '1';
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.opacity = '1';
  backdrop.style.zIndex = '9999';
  
  // Attacher les event listeners aux boutons immédiatement après injection
  // Utiliser requestAnimationFrame pour garantir que le DOM est prêt
  requestAnimationFrame(() => {
    const yesBtn = document.getElementById('logout-yes-btn');
    const noBtn = document.getElementById('logout-no-btn');
    
    console.log('[LOGOUT] Recherche boutons:', { yesBtn: !!yesBtn, noBtn: !!noBtn });
    
    if (yesBtn) {
      // Supprimer l'ancien listener s'il existe en clonant le bouton
      const newYesBtn = yesBtn.cloneNode(true);
      yesBtn.parentNode.replaceChild(newYesBtn, yesBtn);
      newYesBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('[LOGOUT] ✅ Bouton "Oui" cliqué');
        if (typeof window.confirmLogoutWithRememberMe === 'function') {
          window.confirmLogoutWithRememberMe(true);
        } else if (typeof confirmLogoutWithRememberMe === 'function') {
          confirmLogoutWithRememberMe(true);
        } else {
          console.error('[LOGOUT] ❌ confirmLogoutWithRememberMe non trouvé');
        }
      });
      console.log('[LOGOUT] ✅ Event listener attaché au bouton "Oui"');
    } else {
      console.error('[LOGOUT] ❌ Bouton "Oui" non trouvé dans le DOM');
    }
    
    if (noBtn) {
      // Supprimer l'ancien listener s'il existe en clonant le bouton
      const newNoBtn = noBtn.cloneNode(true);
      noBtn.parentNode.replaceChild(newNoBtn, noBtn);
      newNoBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('[LOGOUT] ✅ Bouton "Non" cliqué');
        if (typeof window.confirmLogoutWithRememberMe === 'function') {
          window.confirmLogoutWithRememberMe(false);
        } else if (typeof confirmLogoutWithRememberMe === 'function') {
          confirmLogoutWithRememberMe(false);
        } else {
          console.error('[LOGOUT] ❌ confirmLogoutWithRememberMe non trouvé');
        }
      });
      console.log('[LOGOUT] ✅ Event listener attaché au bouton "Non"');
    } else {
      console.error('[LOGOUT] ❌ Bouton "Non" non trouvé dans le DOM');
    }
    
    console.log('[LOGOUT] ✅ Modal "rester connecté" affiché, boutons attachés');
  });
}

// Fonction pour confirmer la déconnexion avec choix "rester connecté"
function confirmLogoutWithRememberMe(rememberMe) {
  console.log('[LOGOUT] Confirmation déconnexion, rememberMe:', rememberMe);
  
  // Sauvegarder le choix "rester connecté" AVANT déconnexion
  try {
    if (rememberMe) {
      // Garder les tokens dans localStorage pour la prochaine fois
      const accessToken = localStorage.getItem('access_token') || localStorage.getItem('accessToken') || sessionStorage.getItem('access_token') || sessionStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refresh_token') || localStorage.getItem('refreshToken') || sessionStorage.getItem('refresh_token') || sessionStorage.getItem('refreshToken');
      if (accessToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken || '');
        localStorage.setItem('rememberMe', 'true');
        console.log('[LOGOUT] Tokens sauvegardés dans localStorage pour la prochaine fois');
      }
    } else {
      // Tokens JAMAIS supprimés - règle: toujours conserver
      localStorage.setItem('rememberMe', 'true');
      console.log('[LOGOUT] Tokens conservés');
    }
  } catch (e) {
    console.warn('[LOGOUT] Erreur sauvegarde tokens:', e);
  }
  
  // Fermer le modal
  if (typeof closePublishModal === 'function') {
    closePublishModal();
  }
  
  // Déconnecter l'utilisateur
  if (typeof window.logout === 'function') {
    window.logout();
  } else if (typeof logout === 'function') {
    logout();
  } else {
    console.error('[LOGOUT] Fonction logout non trouvée');
    // Fallback : nettoyer manuellement
    if (typeof window !== 'undefined' && window.currentUser) {
      window.currentUser.isLoggedIn = false;
    }
    localStorage.removeItem('currentUser');
    sessionStorage.removeItem('currentUser');
  }
  
  // Mettre à jour l'UI pour remettre tout comme avant la connexion
  setTimeout(() => {
    if (typeof window.updateAccountBlockLegitimately === 'function') {
      window.updateAccountBlockLegitimately();
    }
    if (typeof updateAuthButtons === 'function') {
      updateAuthButtons();
    }
  }, 100);
  
  // Afficher une notification
  setTimeout(() => {
    if (typeof showNotification === 'function') {
      showNotification(rememberMe ? '👋 Vous resterez connecté pour la prochaine fois' : '👋 À bientôt ! Vous devrez vous reconnecter à la prochaine visite', 'info');
    }
  }, 200);
}

// Exposer les fonctions globalement
window.openAccountWindow = openAccountWindow;
window.askRememberMeBeforeLogout = askRememberMeBeforeLogout;
window.confirmLogoutWithRememberMe = confirmLogoutWithRememberMe;

// ✅ MODAL "MES ANNONCES" - Affiche les annonces de l'utilisateur (avec API backend)
async function showMesAnnoncesModal() {
  const modal = document.getElementById('publish-modal-inner');
  const backdrop = document.getElementById('publish-modal-backdrop');
  
  if (!modal || !backdrop) {
    console.error('[MES ANNONCES] Modal non trouvé');
    return;
  }
  
  // Afficher le loader
  modal.innerHTML = '<div style="padding:60px;text-align:center;"><div style="font-size:48px;margin-bottom:16px;">⏳</div><p style="color:var(--ui-text-muted);">Chargement...</p></div>';
  modal.style.display = 'block';
  modal.style.visibility = 'visible';
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.zIndex = '9999';
  
  // Récupérer les annonces depuis l'API backend ET les données locales
  const userAnnonces = [];
  const userId = currentUser ? (currentUser.id || currentUser.cognitoSub) : null;
  const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('accessToken');
  
  // Charger depuis l'API backend
  if (token) {
    try {
      const response = await fetch(window.API_BASE_URL + '/user/events', {
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const events = await response.json();
        events.forEach(e => {
          // Ajouter à userAnnonces pour l'affichage dans la modal
          userAnnonces.push({
            id: e.id, title: e.title, location: e.location, lat: e.latitude, lng: e.longitude,
            date: e.date, status: e.status || 'active', type: 'event', emoji: '📅'
          });
          
          // ⚠️ CRITIQUE : Ajouter aussi à eventsData si pas déjà présent
          // Cela permet à focusOnMapItem de trouver l'événement pour "Voir"
          if (!eventsData.find(ev => ev.id === e.id)) {
            eventsData.push({
              id: e.id,
              type: 'event',
              title: e.title,
              description: e.description || '',
              location: e.location,
              address: e.location,
              lat: e.latitude,
              lng: e.longitude,
              startDate: e.date ? new Date(e.date + (e.time ? 'T' + e.time : '')) : null,
              endDate: e.end_date ? new Date(e.end_date + (e.end_time ? 'T' + e.end_time : '')) : null,
              status: e.status || 'active',
              creator_id: e.creator_id,
              image_url: e.image_url,
              categories: e.categories || [],
              boost: '1.-',
              likes: 0,
              favorites: 0,
              participations: 0
            });
            console.log('[MES ANNONCES] Événement ajouté à eventsData:', e.id, e.title);
          }
        });
        // Rafraîchir les marqueurs pour afficher les nouveaux événements sur la carte
        if (events.length > 0) {
          refreshMarkers();
        }
      }
    } catch (err) { console.warn('[MES ANNONCES] API error:', err); }
  }
  
  // Chercher aussi dans les données locales (fallback + bookings/services)
  eventsData.filter(e => e.userId === userId || e.createdBy === userId || e.creator_id === userId).forEach(e => {
    if (!userAnnonces.find(a => a.id === e.id && a.type === 'event')) {
      userAnnonces.push({ id: e.id, title: e.title || e.name, location: e.location || e.address, lat: e.lat, lng: e.lng, status: e.status || 'active', type: 'event', emoji: '📅' });
    }
  });
  bookingsData.filter(b => b.userId === userId || b.createdBy === userId).forEach(b => {
    userAnnonces.push({ id: b.id, title: b.title || b.name, location: b.location || b.address, lat: b.lat, lng: b.lng, status: 'active', type: 'booking', emoji: '🏨' });
  });
  servicesData.filter(s => s.userId === userId || s.createdBy === userId).forEach(s => {
    userAnnonces.push({ id: s.id, title: s.title || s.name, location: s.location || s.address, lat: s.lat, lng: s.lng, status: 'active', type: 'service', emoji: '🔧' });
  });
  
  const statusLabels = {
    'active': { label: 'Actif', color: '#22c55e', bg: 'rgba(34,197,94,0.15)' },
    'cancelled': { label: 'Annulé', color: '#ef4444', bg: 'rgba(239,68,68,0.15)' },
    'postponed': { label: 'Reporté', color: '#f59e0b', bg: 'rgba(245,158,11,0.15)' }
  };
  
  var html = '<div style="padding:24px;max-width:600px;margin:0 auto;position:relative;">' +
    '<button id="mes-annonces-back-btn" style="position:absolute;top:16px;left:16px;background:rgba(255,255,255,0.1);border:none;color:#fff;font-size:14px;cursor:pointer;padding:8px 16px;border-radius:8px;">← Retour</button>' +
    '<button id="mes-annonces-close-btn" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;">✕</button>' +
    '<h2 style="text-align:center;margin:0 0 24px;font-size:24px;color:#fff;">📢 Mes annonces</h2>';
  
  if (userAnnonces.length === 0) {
    html += '<div style="text-align:center;padding:40px;color:var(--ui-text-muted);"><div style="font-size:48px;margin-bottom:16px;">📭</div><p>Vous n\'avez pas encore d\'annonces</p><button id="mes-annonces-publish-btn" style="margin-top:16px;padding:12px 24px;border-radius:12px;border:none;background:#00ffc3;color:#000;font-weight:600;cursor:pointer;">+ Publier une annonce</button></div>';
  } else {
    html += '<div id="mes-annonces-list" style="display:flex;flex-direction:column;gap:16px;">';
    userAnnonces.forEach(item => {
      const st = statusLabels[item.status] || statusLabels['active'];
      html += '<div class="annonce-item" data-type="' + item.type + '" data-id="' + item.id + '" data-status="' + item.status + '" style="padding:16px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.1);">' +
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;cursor:pointer;" class="annonce-header">' +
          '<div style="font-size:28px;">' + item.emoji + '</div>' +
          '<div style="flex:1;"><div style="font-weight:600;font-size:15px;color:#fff;">' + escapeHtml(item.title || 'Sans titre') + '</div><div style="font-size:12px;color:var(--ui-text-muted);">' + escapeHtml(item.location || '') + '</div></div>' +
          '<span style="padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;background:' + st.bg + ';color:' + st.color + ';">' + st.label + '</span>' +
        '</div>' +
        // Première ligne de boutons
        '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;">' +
          '<button class="annonce-btn-view" data-id="' + item.id + '" data-type="' + item.type + '" style="flex:1;min-width:60px;padding:10px;border-radius:8px;border:1px solid rgba(0,255,195,0.4);background:rgba(0,255,195,0.1);color:#00ffc3;font-size:12px;font-weight:600;cursor:pointer;">📍 Voir</button>' +
          '<button class="annonce-btn-edit" data-id="' + item.id + '" data-type="' + item.type + '" style="flex:1;min-width:60px;padding:10px;border-radius:8px;border:1px solid rgba(59,130,246,0.4);background:rgba(59,130,246,0.1);color:#3b82f6;font-size:12px;font-weight:600;cursor:pointer;">✏️ Modifier</button>' +
        '</div>' +
        // Deuxième ligne - Statuts
        '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
          (item.status === 'active' ? '<button class="annonce-btn-cancel" data-id="' + item.id + '" data-type="' + item.type + '" style="flex:1;min-width:60px;padding:10px;border-radius:8px;border:1px solid rgba(239,68,68,0.4);background:rgba(239,68,68,0.1);color:#ef4444;font-size:12px;font-weight:600;cursor:pointer;">❌ Annuler</button>' : '') +
          (item.status === 'active' ? '<button class="annonce-btn-postpone" data-id="' + item.id + '" data-type="' + item.type + '" style="flex:1;min-width:60px;padding:10px;border-radius:8px;border:1px solid rgba(245,158,11,0.4);background:rgba(245,158,11,0.1);color:#f59e0b;font-size:12px;font-weight:600;cursor:pointer;">⏸️ Reporter</button>' : '') +
          (item.status === 'cancelled' || item.status === 'postponed' ? '<button class="annonce-btn-reactivate" data-id="' + item.id + '" data-type="' + item.type + '" style="flex:1;min-width:60px;padding:10px;border-radius:8px;border:1px solid rgba(34,197,94,0.4);background:rgba(34,197,94,0.1);color:#22c55e;font-size:12px;font-weight:600;cursor:pointer;">✅ Réactiver</button>' : '') +
          '<button class="annonce-btn-delete" data-id="' + item.id + '" data-type="' + item.type + '" style="flex:1;min-width:60px;padding:10px;border-radius:8px;border:1px solid rgba(127,29,29,0.4);background:rgba(127,29,29,0.1);color:#dc2626;font-size:12px;font-weight:600;cursor:pointer;">🗑️ Supprimer</button>' +
        '</div></div>';
    });
    html += '</div>';
  }
  html += '</div>';
  modal.innerHTML = html;
  
  setTimeout(() => {
    document.getElementById('mes-annonces-back-btn')?.addEventListener('click', () => openAccountModal());
    document.getElementById('mes-annonces-close-btn')?.addEventListener('click', () => closePublishModal());
    document.getElementById('mes-annonces-publish-btn')?.addEventListener('click', () => { closePublishModal(); setTimeout(() => openPublishModal(), 200); });
    document.querySelectorAll('.annonce-btn-view').forEach(btn => btn.addEventListener('click', function() { closePublishModal(); focusOnMapItem(this.dataset.type, parseInt(this.dataset.id)); }));
    document.querySelectorAll('.annonce-btn-edit').forEach(btn => btn.addEventListener('click', function() { openEditEventModal(this.dataset.type, parseInt(this.dataset.id)); }));
    document.querySelectorAll('.annonce-btn-cancel').forEach(btn => btn.addEventListener('click', function() { updateEventStatus(parseInt(this.dataset.id), 'cancelled', this.dataset.type); }));
    document.querySelectorAll('.annonce-btn-postpone').forEach(btn => btn.addEventListener('click', function() { updateEventStatus(parseInt(this.dataset.id), 'postponed', this.dataset.type); }));
    document.querySelectorAll('.annonce-btn-reactivate').forEach(btn => btn.addEventListener('click', function() { updateEventStatus(parseInt(this.dataset.id), 'active', this.dataset.type); }));
    document.querySelectorAll('.annonce-btn-delete').forEach(btn => btn.addEventListener('click', function() { confirmDeleteEvent(parseInt(this.dataset.id), this.dataset.type); }));
    document.querySelectorAll('.annonce-header').forEach(h => h.addEventListener('click', function() { const p = this.closest('.annonce-item'); closePublishModal(); focusOnMapItem(p.dataset.type, parseInt(p.dataset.id)); }));
  }, 50);
}

// Mettre à jour le statut d'un événement (annuler/reporter/réactiver)
async function updateEventStatus(eventId, newStatus, itemType = 'event') {
  const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('accessToken');
  if (!token) { showNotification('❌ Vous devez être connecté', 'error'); return; }
  try {
    const endpoint = itemType === 'event' ? 'events' : itemType === 'booking' ? 'bookings' : 'services';
    const response = await fetch(window.API_BASE_URL + '/' + endpoint + '/' + eventId + '/status', {
      method: 'PATCH',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (response.ok) {
      const messages = {
        'cancelled': '❌ Annonce annulée',
        'postponed': '⏸️ Annonce reportée',
        'active': '✅ Annonce réactivée'
      };
      showNotification(messages[newStatus] || '✅ Statut mis à jour', 'success');
      await loadEventsFromBackend();
      showMesAnnoncesModal();
    } else {
      const err = await response.json();
      showNotification('❌ ' + (err.error || 'Erreur'), 'error');
    }
  } catch (err) {
    showNotification('❌ Erreur de connexion', 'error');
  }
}

// Ouvrir le formulaire de modification d'une annonce (formulaire dédié)
function openEditEventModal(itemType, itemId) {
  // Récupérer les données de l'item
  const dataArray = itemType === 'event' ? eventsData : itemType === 'booking' ? bookingsData : servicesData;
  const item = dataArray.find(i => i.id === parseInt(itemId));
  
  if (!item) {
    showNotification('❌ Annonce introuvable', 'error');
    return;
  }
  
  // Stocker les données de l'item à modifier
  window.editingItem = { ...item, mode: itemType, id: itemId };
  
  const modal = document.getElementById('publish-modal-inner');
  const backdrop = document.getElementById('publish-modal-backdrop');
  if (!modal || !backdrop) return;
  
  // Images de statut
  const statusImages = {
    active: '/assets/event_overlays/eventdefault.jpg',
    cancelled: '/assets/event_overlays/Event canceled.jpeg',
    postponed: '/assets/event_overlays/postponed.jpeg',
    completed: '/assets/event_overlays/completed.jpeg'
  };
  
  const currentStatus = item.status || 'active';
  
  // Construire le formulaire de modification
  const html = `
    <div style="padding:24px;max-width:550px;margin:0 auto;position:relative;">
      <button id="edit-back-btn" style="position:absolute;top:16px;left:16px;background:rgba(255,255,255,0.1);border:none;color:#fff;font-size:14px;cursor:pointer;padding:8px 16px;border-radius:8px;">← Retour</button>
      <button id="edit-close-btn" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;">✕</button>
      
      <h2 style="text-align:center;margin:40px 0 24px;font-size:22px;color:#fff;">✏️ Modifier l'annonce</h2>
      
      <!-- Informations de base -->
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;">Titre *</label>
        <input type="text" id="edit-title" value="${escapeHtml(item.title || item.name || '')}" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#fff;font-size:14px;">
      </div>
      
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;">Description</label>
        <textarea id="edit-description" rows="3" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#fff;font-size:14px;resize:vertical;">${escapeHtml(item.description || '')}</textarea>
      </div>
      
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;">Adresse *</label>
        <input type="text" id="edit-address" value="${escapeHtml(item.address || item.location || '')}" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#fff;font-size:14px;">
      </div>
      
      <div style="display:flex;gap:12px;margin-bottom:16px;">
        <div style="flex:1;">
          <label style="display:block;font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;">Email</label>
          <input type="email" id="edit-email" value="${escapeHtml(item.email || '')}" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#fff;font-size:14px;">
        </div>
        <div style="flex:1;">
          <label style="display:block;font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;">Téléphone</label>
          <input type="tel" id="edit-phone" value="${escapeHtml(item.phone || '')}" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#fff;font-size:14px;">
        </div>
      </div>
      
      ${itemType === 'event' ? `
      <div style="display:flex;gap:12px;margin-bottom:16px;">
        <div style="flex:1;">
          <label style="display:block;font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;">Date/Heure début</label>
          <input type="datetime-local" id="edit-start" value="${item.startDate || ''}" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#fff;font-size:14px;">
        </div>
        <div style="flex:1;">
          <label style="display:block;font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;">Date/Heure fin</label>
          <input type="datetime-local" id="edit-end" value="${item.endDate || ''}" style="width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#fff;font-size:14px;">
        </div>
      </div>
      ` : ''}
      
      <!-- Changement de statut avec images -->
      <div style="margin:24px 0;padding:16px;background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.1);border-radius:12px;">
        <h3 style="margin:0 0 16px;font-size:14px;color:#00ffc3;">📌 Statut de l'annonce</h3>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
          <label style="cursor:pointer;text-align:center;">
            <input type="radio" name="edit-status" value="active" ${currentStatus === 'active' ? 'checked' : ''} style="display:none;">
            <div class="status-option" style="padding:8px;border-radius:10px;border:2px solid ${currentStatus === 'active' ? '#22c55e' : 'transparent'};background:${currentStatus === 'active' ? 'rgba(34,197,94,0.1)' : 'rgba(0,0,0,0.2)'};">
              <img src="${statusImages.active}" alt="Actif" style="width:100%;height:60px;object-fit:cover;border-radius:6px;margin-bottom:6px;">
              <div style="font-size:11px;font-weight:600;color:#22c55e;">✅ Actif</div>
            </div>
          </label>
          <label style="cursor:pointer;text-align:center;">
            <input type="radio" name="edit-status" value="postponed" ${currentStatus === 'postponed' ? 'checked' : ''} style="display:none;">
            <div class="status-option" style="padding:8px;border-radius:10px;border:2px solid ${currentStatus === 'postponed' ? '#f59e0b' : 'transparent'};background:${currentStatus === 'postponed' ? 'rgba(245,158,11,0.1)' : 'rgba(0,0,0,0.2)'};">
              <img src="${statusImages.postponed}" alt="Reporté" style="width:100%;height:60px;object-fit:cover;border-radius:6px;margin-bottom:6px;">
              <div style="font-size:11px;font-weight:600;color:#f59e0b;">⏸️ Reporté</div>
            </div>
          </label>
          <label style="cursor:pointer;text-align:center;">
            <input type="radio" name="edit-status" value="cancelled" ${currentStatus === 'cancelled' ? 'checked' : ''} style="display:none;">
            <div class="status-option" style="padding:8px;border-radius:10px;border:2px solid ${currentStatus === 'cancelled' ? '#ef4444' : 'transparent'};background:${currentStatus === 'cancelled' ? 'rgba(239,68,68,0.1)' : 'rgba(0,0,0,0.2)'};">
              <img src="${statusImages.cancelled}" alt="Annulé" style="width:100%;height:60px;object-fit:cover;border-radius:6px;margin-bottom:6px;">
              <div style="font-size:11px;font-weight:600;color:#ef4444;">❌ Annulé</div>
            </div>
          </label>
        </div>
      </div>
      
      <!-- Boutons d'action -->
      <div style="display:flex;gap:12px;margin-top:24px;">
        <button id="edit-save-btn" style="flex:2;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#00d4a0);color:#000;font-size:15px;font-weight:700;cursor:pointer;">
          💾 Enregistrer les modifications
        </button>
        <button id="edit-delete-btn" style="flex:1;padding:14px;border-radius:12px;border:1px solid rgba(239,68,68,0.4);background:rgba(239,68,68,0.1);color:#ef4444;font-size:14px;font-weight:600;cursor:pointer;">
          🗑️ Supprimer
        </button>
      </div>
    </div>
  `;
  
  modal.innerHTML = html;
  modal.style.display = 'block';
  backdrop.style.display = 'flex';
  backdrop.style.zIndex = '9999';
  
  // Attacher les event listeners
  setTimeout(() => {
    document.getElementById('edit-back-btn')?.addEventListener('click', () => showMesAnnoncesModal());
    document.getElementById('edit-close-btn')?.addEventListener('click', () => { window.editingItem = null; closePublishModal(); });
    document.getElementById('edit-save-btn')?.addEventListener('click', () => saveEditedEvent(itemType, itemId));
    document.getElementById('edit-delete-btn')?.addEventListener('click', () => confirmDeleteEvent(itemId, itemType));
    
    // Mettre à jour les styles des options de statut au clic
    document.querySelectorAll('input[name="edit-status"]').forEach(radio => {
      radio.addEventListener('change', function() {
        document.querySelectorAll('.status-option').forEach(opt => {
          opt.style.border = '2px solid transparent';
          opt.style.background = 'rgba(0,0,0,0.2)';
        });
        const selected = this.closest('label').querySelector('.status-option');
        const colors = { active: '#22c55e', postponed: '#f59e0b', cancelled: '#ef4444' };
        selected.style.border = `2px solid ${colors[this.value]}`;
        selected.style.background = `rgba(${this.value === 'active' ? '34,197,94' : this.value === 'postponed' ? '245,158,11' : '239,68,68'},0.1)`;
      });
    });
  }, 100);
}

// Sauvegarder les modifications d'une annonce
async function saveEditedEvent(itemType, itemId) {
  const title = document.getElementById('edit-title')?.value.trim();
  const description = document.getElementById('edit-description')?.value.trim();
  const address = document.getElementById('edit-address')?.value.trim();
  const email = document.getElementById('edit-email')?.value.trim();
  const phone = document.getElementById('edit-phone')?.value.trim();
  const startDate = document.getElementById('edit-start')?.value;
  const endDate = document.getElementById('edit-end')?.value;
  const newStatus = document.querySelector('input[name="edit-status"]:checked')?.value || 'active';
  
  if (!title || !address) {
    showNotification('⚠️ Le titre et l\'adresse sont obligatoires', 'warning');
    return;
  }
  
  showNotification('⏳ Enregistrement...', 'info');
  
  try {
    const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('accessToken');
    const endpoint = itemType === 'event' ? 'events' : itemType === 'booking' ? 'bookings' : 'services';
    
    const updateData = {
      title, description, location: address, address, email, phone, status: newStatus
    };
    
    if (itemType === 'event') {
      if (startDate) {
        updateData.date = startDate.split('T')[0];
        updateData.time = startDate.split('T')[1];
      }
      if (endDate) {
        updateData.end_date = endDate.split('T')[0];
        updateData.end_time = endDate.split('T')[1];
      }
    }
    
    const response = await fetch(`${window.API_BASE_URL}/${endpoint}/${itemId}`, {
      method: 'PUT',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });
    
    if (response.ok) {
      // Mettre à jour localement
      const dataArray = itemType === 'event' ? eventsData : itemType === 'booking' ? bookingsData : servicesData;
      const index = dataArray.findIndex(i => i.id === parseInt(itemId));
      if (index !== -1) {
        dataArray[index] = { ...dataArray[index], ...updateData, title, name: title };
      }
      
      window.editingItem = null;
      refreshMarkers();
      playPaymentSound();
      showNotification('✅ Modifications enregistrées !', 'success');
      
      setTimeout(() => showMesAnnoncesModal(), 500);
    } else {
      const err = await response.json();
      showNotification('❌ Erreur: ' + (err.error || 'Impossible de modifier'), 'error');
    }
  } catch (error) {
    console.error('Erreur modification:', error);
    showNotification('❌ Erreur de connexion', 'error');
  }
}

// Confirmation de suppression
function confirmDeleteEvent(itemId, itemType) {
  const modal = document.getElementById('publish-modal-inner');
  if (!modal) return;
  
  modal.innerHTML = `
    <div style="padding:40px;text-align:center;max-width:400px;margin:0 auto;">
      <div style="font-size:64px;margin-bottom:20px;">🗑️</div>
      <h2 style="color:#fff;margin-bottom:16px;">Supprimer cette annonce ?</h2>
      <p style="color:var(--ui-text-muted);margin-bottom:24px;">Cette action est irréversible. L'annonce sera définitivement supprimée.</p>
      <div style="display:flex;gap:12px;justify-content:center;">
        <button id="delete-cancel-btn" style="padding:12px 24px;border-radius:12px;border:1px solid rgba(255,255,255,0.2);background:transparent;color:#fff;font-weight:600;cursor:pointer;">Annuler</button>
        <button id="delete-confirm-btn" style="padding:12px 24px;border-radius:12px;border:none;background:#dc2626;color:#fff;font-weight:600;cursor:pointer;">🗑️ Supprimer</button>
      </div>
    </div>
  `;
  
  document.getElementById('delete-cancel-btn')?.addEventListener('click', () => showMesAnnoncesModal());
  document.getElementById('delete-confirm-btn')?.addEventListener('click', () => deleteEvent(itemId, itemType));
}

// Supprimer une annonce
async function deleteEvent(itemId, itemType) {
  const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('accessToken');
  if (!token) { showNotification('❌ Vous devez être connecté', 'error'); return; }
  
  try {
    const endpoint = itemType === 'event' ? 'events' : itemType === 'booking' ? 'bookings' : 'services';
    const response = await fetch(window.API_BASE_URL + '/' + endpoint + '/' + itemId, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token }
    });
    
    if (response.ok) {
      showNotification('🗑️ Annonce supprimée', 'success');
      
      // Supprimer localement aussi
      if (itemType === 'event') {
        eventsData = eventsData.filter(e => e.id !== itemId);
        window.eventsData = eventsData;
      } else if (itemType === 'booking') {
        bookingsData = bookingsData.filter(b => b.id !== itemId);
        window.bookingsData = bookingsData;
      } else if (itemType === 'service') {
        servicesData = servicesData.filter(s => s.id !== itemId);
        window.servicesData = servicesData;
      }
      
      refreshMarkers();
      showMesAnnoncesModal();
    } else {
      const err = await response.json();
      showNotification('❌ ' + (err.error || 'Erreur de suppression'), 'error');
      showMesAnnoncesModal();
    }
  } catch (err) {
    console.error('Erreur suppression:', err);
    showNotification('❌ Erreur de connexion', 'error');
    showMesAnnoncesModal();
  }
}

// Fonction pour centrer la map sur un item et ouvrir sa popup
function focusOnMapItem(type, id) {
  var data = type === 'event' ? eventsData : type === 'booking' ? bookingsData : servicesData;
  var item = data.find(function(i) { return i.id === parseInt(id); });
  
  if (item && item.lat && item.lng) {
    // Changer le mode si nécessaire
    if (currentMode !== type) {
      setMode(type);
    }
    
    // Centrer la carte
    if (map) {
      map.setView([item.lat, item.lng], 16);
    }
    
    // Ouvrir la popup de l'item après un court délai
    setTimeout(function() {
      if (typeof openEventCard === 'function') {
        openEventCard(item);
      }
    }, 500);
    
    showNotification('📍 ' + (item.title || item.name), 'info');
  } else {
    showNotification('❌ Impossible de localiser cette annonce', 'error');
  }
}

// Fonction pour afficher le contenu d'un bloc
function showAccountBlockContent(blockType) {
  console.log('[ACCOUNT BLOCK] showAccountBlockContent appelé avec blockType:', blockType);
  
  // ⚠️⚠️⚠️ CRITIQUE : Pour modifier-profil, utiliser directement openEditProfileModal
  if (blockType === 'modifier-profil') {
    console.log('[ACCOUNT BLOCK] modifier-profil détecté - Utilisation directe openEditProfileModal');
    if (typeof window.openEditProfileModal === 'function') {
      window.openEditProfileModal();
      return;
    } else if (typeof openEditProfileModal === 'function') {
      openEditProfileModal();
      return;
    } else {
      console.error('[ACCOUNT BLOCK] ❌ openEditProfileModal non disponible');
      if (typeof showNotification === 'function') {
        showNotification('⚠️ Fonctionnalité en cours de développement', 'info');
      }
      return;
    }
  }
  
  const contentDiv = document.getElementById('account-block-content');
  if (!contentDiv) {
    console.error('[ACCOUNT BLOCK] ❌ account-block-content non trouvé!');
    return;
  }
  console.log('[ACCOUNT BLOCK] ✅ account-block-content trouvé');
  
  let content = '';
  
  if (blockType === 'agenda') {
    const agendaItems = (currentUser.agenda || []).map(key => {
      const [type, id] = key.split(":");
      const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
      return data.find(i => i.id === parseInt(id));
    }).filter(Boolean);
    
    content = `
      <div style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h3 style="margin:0;font-size:18px;font-weight:700;color:#fff;">📅 Mon Agenda</h3>
          <button onclick="openAccountModal()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px;">✕</button>
        </div>
        ${agendaItems.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">📭</div>
            <p>Votre agenda est vide</p>
            <p style="font-size:12px;margin-top:8px;">Ajoutez des événements depuis la carte !</p>
          </div>
        ` : `
          <div style="display:flex;flex-direction:column;gap:12px;">
            ${agendaItems.slice(0, 10).map(item => {
              const imgTag = buildMainImageTag(item, item.title || item.name || "");
              return `
                <div onclick="openPopupFromList('${item.type}', ${item.id}); closePublishModal();" style="display:flex;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
                  <div style="width:80px;height:80px;border-radius:8px;overflow:hidden;flex-shrink:0;">
                    ${imgTag}
                  </div>
                  <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;font-size:14px;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(item.title || item.name || 'Sans titre')}</div>
                    <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:4px;">${getCategoryEmoji(item)} ${item.category || 'Autre'}</div>
                    ${item.startDate ? `<div style="font-size:11px;color:var(--ui-text-muted);">📅 ${formatDate(item.startDate)}</div>` : ''}
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `}
      </div>
    `;
  } else if (blockType === 'amis') {
    const friends = currentUser.friends || [];
    const friendRequests = currentUser.friendRequests || [];
    
    content = `
      <div style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h3 style="margin:0;font-size:18px;font-weight:700;color:#fff;">👥 Mes Amis</h3>
          <button onclick="openAccountModal()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px;">✕</button>
        </div>
        ${friendRequests.length > 0 ? `
          <div style="margin-bottom:20px;">
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;font-weight:600;">🔔 Demandes en attente (${friendRequests.length})</div>
            <div style="display:flex;flex-direction:column;gap:8px;">
              ${friendRequests.slice(0, 5).map(req => `
                <div style="display:flex;align-items:center;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);">
                  <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:20px;">${req.avatar || '👤'}</div>
                  <div style="flex:1;">
                    <div style="font-weight:600;font-size:14px;">${escapeHtml(req.name || 'Utilisateur')}</div>
                    <div style="font-size:11px;color:var(--ui-text-muted);">${req.username || ''}</div>
                  </div>
                  <div style="display:flex;gap:8px;">
                    <button onclick="acceptFriendRequest(${req.id})" style="padding:6px 12px;border-radius:8px;border:none;background:#22c55e;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">✓</button>
                    <button onclick="rejectFriendRequest(${req.id})" style="padding:6px 12px;border-radius:8px;border:none;background:#ef4444;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">✕</button>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
        ${friends.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">👥</div>
            <p>Vous n'avez pas encore d'amis</p>
            <p style="font-size:12px;margin-top:8px;">Ajoutez des amis pour partager vos événements !</p>
          </div>
        ` : `
          <div style="display:flex;flex-direction:column;gap:8px;">
            ${friends.slice(0, 20).map(friend => `
              <div style="display:flex;align-items:center;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;" onmouseover="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
                <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:20px;">${friend.avatar || '👤'}</div>
                <div style="flex:1;">
                  <div style="font-weight:600;font-size:14px;">${escapeHtml(friend.name || friend.username || 'Ami')}</div>
                  <div style="font-size:11px;color:var(--ui-text-muted);">${friend.username || ''}</div>
                </div>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    `;
  } else if (blockType === 'parametres') {
    content = `
      <div style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h3 style="margin:0;font-size:18px;font-weight:700;color:#fff;">⚙️ Paramètres</h3>
          <button onclick="openAccountModal()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px;">✕</button>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px;">
          <button onclick="openUserProfile()" style="padding:14px;border-radius:12px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:#fff;font-weight:600;font-size:14px;cursor:pointer;text-align:left;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
            👤 Modifier mon profil
          </button>
          <button onclick="showNotification('Fonctionnalité à venir', 'info')" style="padding:14px;border-radius:12px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:#fff;font-weight:600;font-size:14px;cursor:pointer;text-align:left;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
            🔔 Notifications
          </button>
          <button onclick="showNotification('Fonctionnalité à venir', 'info')" style="padding:14px;border-radius:12px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:#fff;font-weight:600;font-size:14px;cursor:pointer;text-align:left;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.1)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
            🔒 Confidentialité
          </button>
        </div>
      </div>
    `;
  } else if (blockType === 'profil') {
    content = `
      <div style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h3 style="margin:0;font-size:18px;font-weight:700;color:#fff;">👤 Mon Profil</h3>
          <button onclick="openAccountModal()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px;">✕</button>
        </div>
        <div style="display:flex;flex-direction:column;gap:16px;">
          <div>
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Nom d'utilisateur</div>
            <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(currentUser.username || 'Non défini')}</div>
          </div>
          <div>
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Email</div>
            <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(currentUser.email || 'Non défini')}</div>
          </div>
          ${currentUser.firstName || currentUser.lastName ? `
            <div>
              <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Nom complet</div>
              <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml((currentUser.firstName || '') + ' ' + (currentUser.lastName || ''))}</div>
            </div>
          ` : ''}
          <button onclick="openUserProfile()" style="padding:14px;border-radius:12px;border:2px solid rgba(0,255,195,0.5);background:rgba(0,255,195,0.1);color:#00ffc3;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.background='rgba(0,255,195,0.2)';" onmouseout="this.style.background='rgba(0,255,195,0.1)';">
            ✏️ Modifier mon profil
          </button>
        </div>
      </div>
    `;
  } else if (blockType === 'modifier-profil') {
    // Afficher TOUTES les données du profil
    const addresses = currentUser.addresses || [];
    const mainAddress = addresses.length > 0 ? addresses[0] : (currentUser.postalAddress ? { label: currentUser.postalAddress } : null);
    
    content = `
      <div style="padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <h3 style="margin:0;font-size:18px;font-weight:700;color:#fff;">✏️ Modifier mon profil</h3>
          <button onclick="openAccountModal()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px;">✕</button>
        </div>
        <div style="display:flex;flex-direction:column;gap:16px;">
          <div>
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Nom d'utilisateur</div>
            <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(currentUser.username || 'Non défini')}</div>
          </div>
          <div>
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Email</div>
            <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(currentUser.email || 'Non défini')}</div>
          </div>
          ${currentUser.firstName ? `
            <div>
              <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Prénom</div>
              <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(currentUser.firstName)}</div>
            </div>
          ` : ''}
          ${currentUser.lastName ? `
            <div>
              <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Nom</div>
              <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(currentUser.lastName)}</div>
            </div>
          ` : ''}
          ${mainAddress ? `
            <div>
              <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Adresse postale</div>
              <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(mainAddress.label || mainAddress)}</div>
            </div>
          ` : ''}
          ${currentUser.profile_photo_url ? `
            <div>
              <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">Photo de profil</div>
              <div style="width:80px;height:80px;border-radius:50%;overflow:hidden;border:2px solid rgba(0,255,195,0.3);">
                <img src="${currentUser.profile_photo_url}" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none';" />
              </div>
            </div>
          ` : ''}
          <button onclick="if(typeof window.openEditProfileModal === 'function') { window.openEditProfileModal(); } else if(typeof openEditProfileModal === 'function') { openEditProfileModal(); } else { showNotification('Fonctionnalité à venir', 'info'); }" style="width:100%;padding:14px;border-radius:12px;border:2px solid rgba(0,255,195,0.5);background:rgba(0,255,195,0.1);color:#00ffc3;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.background='rgba(0,255,195,0.2)';" onmouseout="this.style.background='rgba(0,255,195,0.1)';">
            ✏️ Modifier mes informations
          </button>
        </div>
      </div>
    `;
  }
  
  if (content) {
    contentDiv.innerHTML = content;
  }
}

// Exposer les fonctions globalement
window.openAccountModal = openAccountModal;
window.showAccountBlockContent = showAccountBlockContent;

function showAccountModalTab(tab) {
  accountModalActiveTab = tab;
  
  // Calculer les statistiques
  const memberSince = currentUser.createdAt ? new Date(currentUser.createdAt).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' }) : 'Déc. 2024';
  const totalEvents = eventsData.length;
  const alertsCount = currentUser.alerts?.length || 0;
  const notificationsCount = (currentUser.friendRequests?.length || 0) + (currentUser.pendingStatusNotifications?.length || 0);
  
  // Initialiser les propriétés si elles sont undefined
  if (!currentUser.likes) currentUser.likes = [];
  if (!currentUser.agenda) currentUser.agenda = [];
  if (!currentUser.participating) currentUser.participating = [];
  if (!currentUser.favorites) currentUser.favorites = [];
  if (!currentUser.friendRequests) currentUser.friendRequests = [];
  
  // Déterminer le niveau et les badges
  const activityScore = (currentUser.likes.length || 0) + (currentUser.agenda.length || 0) * 2 + (currentUser.participating.length || 0) * 3;
  const level = activityScore > 50 ? 'Expert' : activityScore > 20 ? 'Actif' : activityScore > 5 ? 'Découvreur' : 'Nouveau';
  const levelColor = activityScore > 50 ? '#ffd700' : activityScore > 20 ? '#8b5cf6' : activityScore > 5 ? '#3b82f6' : '#6b7280';
  const levelEmoji = activityScore > 50 ? '🏆' : activityScore > 20 ? '⭐' : activityScore > 5 ? '🌱' : '👋';
  
  // Badges gagnés
  const badges = [];
  if ((currentUser.likes?.length || 0) >= 1) badges.push({ emoji: '❤️', name: 'Premier like' });
  if ((currentUser.agenda?.length || 0) >= 5) badges.push({ emoji: '📅', name: '5 événements' });
  if ((currentUser.participating?.length || 0) >= 1) badges.push({ emoji: '🎉', name: 'Participant' });
  if (currentUser.subscription !== 'free') badges.push({ emoji: '💎', name: 'Premium' });
  if (alertsCount >= 3) badges.push({ emoji: '🔔', name: 'Alerté' });
  
  // Plan d'abonnement actuel
  const planNames = {
    'free': { name: 'Gratuit', color: '#6b7280', emoji: '🆓' },
    'events-explorer': { name: 'Events Explorer', color: '#22c55e', emoji: '🌱' },
    'events-alerts-pro': { name: 'Events Alerts Pro', color: '#3b82f6', emoji: '🔔' },
    'service-pro': { name: 'Service Pro', color: '#8b5cf6', emoji: '💼' },
    'service-ultra': { name: 'Service Ultra', color: '#a78bfa', emoji: '🚀' },
    'full-premium': { name: 'Full Premium', color: '#ffd700', emoji: '👑' }
  };
  const currentPlan = planNames[currentUser.subscription] || planNames.free;
  
  // Avatar à afficher (photo de profil ou emoji)
  // PRIORITÉ: profile_photo_url > profilePhoto > avatarUrl > avatar
  const avatarUrl = currentUser.profile_photo_url || currentUser.profilePhoto || currentUser.avatarUrl || currentUser.avatar;
  const avatarDisplay = (avatarUrl && (avatarUrl.startsWith('http') || avatarUrl.startsWith('data:image')))
    ? `<img src="${avatarUrl}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.parentElement.innerHTML='${currentUser.avatar || '👤'}';" />`
    : (avatarUrl || currentUser.avatar || "👤");
  
  // Contenu des onglets
  let tabContent = '';
  
  if (tab === 'agenda') {
    const agendaItems = (currentUser.agenda || []).map(key => {
      const [type, id] = key.split(":");
      const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
      const item = data.find(i => i.id === parseInt(id));
      // ⚠️ CRITIQUE : S'assurer que item.type est défini
      if (item && !item.type) {
        item.type = type;
      }
      return item;
    }).filter(Boolean);
    
    tabContent = `
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px;font-size:18px;font-weight:700;">📅 Mon Agenda</h3>
        ${agendaItems.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">📭</div>
            <p>Votre agenda est vide</p>
            <p style="font-size:12px;margin-top:8px;">Ajoutez des événements depuis la carte !</p>
          </div>
        ` : `
          <div style="display:flex;flex-direction:column;gap:12px;">
            ${agendaItems.slice(0, 10).map(item => {
              const imgTag = buildMainImageTag(item, item.title || item.name || "");
              const itemType = item.type || 'event';
              return `
                <div onclick="openPopupFromList('${itemType}', ${item.id}); closePublishModal();" style="display:flex;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
                  <div style="width:80px;height:80px;border-radius:8px;overflow:hidden;flex-shrink:0;">
                    ${imgTag}
                  </div>
                  <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;font-size:14px;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(item.title || item.name || 'Sans titre')}</div>
                    <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:4px;">${getCategoryEmoji(item)} ${item.category || 'Autre'}</div>
                    ${item.startDate ? `<div style="font-size:11px;color:var(--ui-text-muted);">📅 ${formatDate(item.startDate)}</div>` : ''}
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `}
      </div>
    `;
  } else if (tab === 'groupes') {
    const groups = currentUser.groups || [];
    tabContent = `
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px;font-size:18px;font-weight:700;">👥 Mes Groupes</h3>
        ${groups.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">👥</div>
            <p>Vous n'êtes dans aucun groupe</p>
            <button onclick="openGroupsModal()" style="margin-top:16px;padding:12px 24px;border-radius:999px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;cursor:pointer;">Créer un groupe</button>
          </div>
        ` : `
          <div style="display:flex;flex-direction:column;gap:12px;">
            ${groups.map(group => `
              <div onclick="openGroupDetails(${group.id})" style="display:flex;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;">
                <div style="width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;">${group.emoji || '👥'}</div>
                <div style="flex:1;">
                  <div style="font-weight:600;font-size:14px;">${escapeHtml(group.name || 'Groupe sans nom')}</div>
                  <div style="font-size:12px;color:var(--ui-text-muted);">${group.members?.length || 0} membres</div>
                </div>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    `;
  } else if (tab === 'amis') {
    // Chargement dynamique depuis l'API - afficher un placeholder, puis charger async
    tabContent = `
      <div style="padding:16px;" id="friends-tab-content">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
          <h3 style="margin:0;font-size:18px;font-weight:700;">Mes Amis</h3>
                  </div>
        
        <!-- Recherche d'amis -->
        <div style="margin-bottom:16px;">
                  <div style="display:flex;gap:8px;">
            <div style="flex:1;position:relative;">
              <input id="friend-search-input" type="text" placeholder="Rechercher un utilisateur..." 
                style="width:100%;padding:10px 12px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:#e4e6eb;font-size:14px;" 
                oninput="searchFriendsDebounced(this.value)">
              <div id="friend-search-results" style="position:absolute;top:100%;left:0;right:0;z-index:100;background:#1e293b;border-radius:0 0 12px 12px;border:1px solid rgba(255,255,255,0.1);display:none;max-height:200px;overflow-y:auto;"></div>
                  </div>
                </div>
            </div>
        
        <!-- Demandes en attente -->
        <div id="friend-requests-section" style="display:none;margin-bottom:20px;">
          <div style="font-size:12px;color:#94a3b8;margin-bottom:12px;font-weight:600;">Demandes en attente</div>
          <div id="friend-requests-list" style="display:flex;flex-direction:column;gap:8px;"></div>
          </div>
        
        <!-- Liste des amis -->
        <div id="friends-list-section">
          <div style="text-align:center;padding:20px;color:#94a3b8;">Chargement...</div>
          </div>
      </div>
    `;
    // Charger les amis après le rendu
    setTimeout(() => loadFriendsTab(), 50);
  } else if (tab === 'notifications') {
    const notifications = [
      ...(currentUser.pendingStatusNotifications || []).map(n => ({...n, type: 'status'})),
      ...(currentUser.friendRequests || []).map(n => ({...n, type: 'friend'})),
    ].sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    
    tabContent = `
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px;font-size:18px;font-weight:700;">🔔 Notifications</h3>
        ${notifications.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">🔔</div>
            <p>Aucune notification</p>
          </div>
        ` : `
          <div style="display:flex;flex-direction:column;gap:8px;">
            ${notifications.slice(0, 20).map(notif => `
              <div style="display:flex;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);">
                <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">
                  ${notif.type === 'status' ? '📊' : notif.type === 'friend' ? '👥' : '🔔'}
                </div>
                <div style="flex:1;">
                  <div style="font-size:13px;color:var(--ui-text-main);line-height:1.4;">${escapeHtml(notif.message || 'Nouvelle notification')}</div>
                  <div style="font-size:11px;color:var(--ui-text-muted);margin-top:4px;">${formatTime(notif.timestamp || Date.now())}</div>
                </div>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    `;
  } else if (tab === 'alertes') {
    closePublishModal();
    setTimeout(() => { if (typeof openProximityAlertsView === 'function') openProximityAlertsView(); }, 300);
    return;
  } else if (tab === 'panier') {
    closePublishModal();
    setTimeout(() => { if (typeof openCartModal === 'function') openCartModal(); }, 300);
    return;
  } else if (tab === 'abos') {
    tabContent = getSubscriptionTabContent();
  } else if (tab === 'privacy') {
    // Initialiser les valeurs de confidentialité par défaut si non définies
    const profilePublic = currentUser.profile_public !== undefined ? currentUser.profile_public : false;
    const showName = currentUser.show_name !== undefined ? currentUser.show_name : false;
    const showPhoto = currentUser.show_photo !== undefined ? currentUser.show_photo : false;
    const showCityCountryOnly = currentUser.show_city_country_only !== undefined ? currentUser.show_city_country_only : false;
    
    tabContent = `
      <div style="padding:16px;">
        <div style="margin-bottom:20px;padding:12px;background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:12px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span style="font-size:20px;">🔒</span>
            <div style="font-weight:700;font-size:14px;color:#00ffc3;">Compte privé (par défaut)</div>
          </div>
          <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.5;">
            Vos données personnelles (email, adresse complète) ne sont <strong>jamais</strong> affichées publiquement. 
            Vous pouvez choisir de rendre certains éléments de votre profil visibles via les options ci-dessous.
          </div>
        </div>
        
        <h3 style="margin:0 0 16px;font-size:16px;font-weight:700;">Visibilité du profil</h3>
        
        <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:20px;">
          <label style="display:flex;align-items:start;justify-content:space-between;padding:14px;background:rgba(15,23,42,0.5);border-radius:10px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.borderColor='var(--ui-card-border)'">
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="font-size:18px;">🌐</span>
                <span style="font-weight:600;font-size:14px;">Rendre mon profil visible</span>
              </div>
              <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.4;">
                Si activé, votre profil peut être découvert par d'autres utilisateurs. Vos données sensibles (email, adresse complète) restent toujours privées.
              </div>
            </div>
            <input type="checkbox" id="privacy-profile-public" ${profilePublic ? 'checked' : ''} onchange="togglePrivacySetting('profile_public', this.checked)" style="width:20px;height:20px;margin-left:12px;accent-color:#00ffc3;cursor:pointer;">
          </label>
          
          <label style="display:flex;align-items:start;justify-content:space-between;padding:14px;background:rgba(15,23,42,0.5);border-radius:10px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.borderColor='var(--ui-card-border)'">
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="font-size:18px;">👤</span>
                <span style="font-weight:600;font-size:14px;">Afficher mon nom</span>
              </div>
              <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.4;">
                Permet d'afficher votre nom d'utilisateur ou votre nom complet sur votre profil public.
              </div>
            </div>
            <input type="checkbox" id="privacy-show-name" ${showName ? 'checked' : ''} onchange="togglePrivacySetting('show_name', this.checked)" style="width:20px;height:20px;margin-left:12px;accent-color:#00ffc3;cursor:pointer;">
          </label>
          
          <label style="display:flex;align-items:start;justify-content:space-between;padding:14px;background:rgba(15,23,42,0.5);border-radius:10px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.borderColor='var(--ui-card-border)'">
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="font-size:18px;">📸</span>
                <span style="font-weight:600;font-size:14px;">Afficher ma photo</span>
              </div>
              <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.4;">
                Permet d'afficher votre photo de profil sur votre profil public.
              </div>
            </div>
            <input type="checkbox" id="privacy-show-photo" ${showPhoto ? 'checked' : ''} onchange="togglePrivacySetting('show_photo', this.checked)" style="width:20px;height:20px;margin-left:12px;accent-color:#00ffc3;cursor:pointer;">
          </label>
          
          <label style="display:flex;align-items:start;justify-content:space-between;padding:14px;background:rgba(15,23,42,0.5);border-radius:10px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.borderColor='var(--ui-card-border)'">
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="font-size:18px;">📍</span>
                <span style="font-weight:600;font-size:14px;">Afficher ville/pays uniquement</span>
              </div>
              <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.4;">
                Permet d'afficher uniquement votre ville et pays (sans adresse complète) sur votre profil public.
              </div>
            </div>
            <input type="checkbox" id="privacy-show-city-country" ${showCityCountryOnly ? 'checked' : ''} onchange="togglePrivacySetting('show_city_country_only', this.checked)" style="width:20px;height:20px;margin-left:12px;accent-color:#00ffc3;cursor:pointer;">
          </label>
        </div>
        
        <div style="padding:12px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:10px;margin-top:20px;">
          <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.5;">
            <strong style="color:#ef4444;">⚠️ Important :</strong> Votre email et votre adresse postale complète ne sont <strong>jamais</strong> affichés publiquement, même si vous activez ces options.
          </div>
        </div>
      </div>
    `;
  }
  
  const html = `
    <div style="padding:0;max-width:500px;margin:0 auto;">
      <!-- Header avec avatar et infos -->
      <div style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0f172a 100%);padding:20px;border-radius:16px 16px 0 0;position:relative;">
        <div style="display:flex;align-items:center;gap:16px;">
          <div style="position:relative;">
            <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;border:2px solid rgba(255,255,255,0.2);overflow:hidden;" data-account-avatar="true">
              ${avatarDisplay}
            </div>
            <div style="position:absolute;bottom:-2px;right:-2px;width:20px;height:20px;background:${levelColor};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;border:2px solid #0f172a;">
              ${levelEmoji}
            </div>
          </div>
          <div style="flex:1;">
            <div style="font-size:18px;font-weight:800;color:#fff;margin-bottom:2px;">${currentUser.username || currentUser.name || 'Utilisateur'}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.6);margin-bottom:4px;">${currentUser.email || ''}</div>
            ${(currentUser.address_city || currentUser.address_country_code) && currentUser.show_city_country_only ? `
              <div style="font-size:11px;color:rgba(255,255,255,0.5);display:flex;align-items:center;gap:4px;">
                <span>📍</span>
                <span>${currentUser.address_city || ''}${currentUser.address_city && currentUser.address_country_code ? ', ' : ''}${currentUser.address_country_code || ''}</span>
              </div>
            ` : ''}
          </div>
        </div>
      </div>
      
      <!-- Onglets style Facebook -->
      <div style="display:flex;background:var(--ui-card-bg);border-top:1px solid var(--ui-card-border);border-bottom:1px solid var(--ui-card-border);">
        <button onclick="closePublishModal();setTimeout(() => openAgendaModal(), 300);" style="flex:1;padding:14px;border:none;background:${tab === 'agenda' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'agenda' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'agenda' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'agenda' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          📅 Agenda
        </button>
        <button onclick="showAccountModalTab('groupes')" style="flex:1;padding:14px;border:none;background:${tab === 'groupes' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'groupes' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'groupes' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'groupes' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          👥 Groupes
        </button>
        <button onclick="showAccountModalTab('amis')" style="flex:1;padding:14px;border:none;background:${tab === 'amis' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'amis' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'amis' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'amis' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;position:relative;">
          👥 Amis
          ${(currentUser.friendRequests?.length || 0) > 0 ? `<span style="position:absolute;top:8px;right:8px;width:16px;height:16px;background:#ef4444;border-radius:50%;font-size:9px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;">${currentUser.friendRequests.length}</span>` : ''}
        </button>
        <button onclick="showAccountModalTab('notifications')" style="flex:1;padding:14px;border:none;background:${tab === 'notifications' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'notifications' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'notifications' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'notifications' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;position:relative;">
          🔔 Notifs
          ${notificationsCount > 0 ? `<span style="position:absolute;top:8px;right:8px;width:16px;height:16px;background:#ef4444;border-radius:50%;font-size:9px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;">${notificationsCount}</span>` : ''}
        </button>
        <button onclick="showAccountModalTab('mapfriend')" style="flex:1;padding:14px;border:none;background:${tab === 'mapfriend' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'mapfriend' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'mapfriend' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'mapfriend' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          🌍 Map Friend
        </button>
        <button onclick="showAccountModalTab('alertes')" style="flex:1;padding:14px;border:none;background:${tab === 'alertes' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'alertes' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'alertes' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'alertes' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          🔔 Alertes
        </button>
        <button onclick="showAccountModalTab('panier')" style="flex:1;padding:14px;border:none;background:${tab === 'panier' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'panier' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'panier' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'panier' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          🛒 Panier
        </button>
        <button onclick="showAccountModalTab('abos')" style="flex:1;padding:14px;border:none;background:${tab === 'abos' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'abos' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'abos' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'abos' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          💎 Abos
        </button>
        <button onclick="showAccountModalTab('privacy')" style="flex:1;padding:14px;border:none;background:${tab === 'privacy' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'privacy' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'privacy' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'privacy' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          🔒 Confidentialité
        </button>
      </div>
      
      <!-- Contenu de l'onglet -->
      <div style="max-height:calc(80vh - 200px);overflow-y:auto;">
        ${tabContent}
      </div>
      
      <!-- Footer avec actions -->
      <div style="padding:12px 16px;background:var(--ui-card-bg);border-top:1px solid var(--ui-card-border);border-radius:0 0 16px 16px;display:flex;flex-direction:column;gap:8px;">
        <div style="display:flex;gap:8px;">
          <button onclick="openEditProfileModal()" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(0,255,195,0.3);background:rgba(0,255,195,0.1);color:#00ffc3;cursor:pointer;font-size:12px;font-weight:600;">✏️ Modifier profil</button>
          <button onclick="openSettingsModal()" style="flex:1;padding:10px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">⚙️ Paramètres</button>
        </div>
        <div style="display:flex;gap:8px;">
          <button onclick="logout()" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(239,68,68,0.3);background:rgba(239,68,68,0.1);color:#ef4444;cursor:pointer;font-size:12px;">🚪 Déconnexion</button>
          <button onclick="closePublishModal()" style="flex:1;padding:10px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-muted);cursor:pointer;font-size:12px;">Fermer</button>
        </div>
      </div>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
}

// Modal Paramètres
function openSettingsModal() {
  const html = `
    <div style="padding:20px;max-width:400px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
        <h2 style="margin:0;font-size:20px;display:flex;align-items:center;gap:10px;">⚙️ Paramètres</h2>
        <button onclick="closePublishModal()" style="background:none;border:none;font-size:24px;cursor:pointer;color:var(--ui-text-muted);">✕</button>
      </div>
      
      <!-- Notifications -->
      <div style="margin-bottom:20px;">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;font-weight:600;">🔔 NOTIFICATIONS</div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <label style="display:flex;align-items:center;justify-content:space-between;padding:12px;background:rgba(15,23,42,0.5);border-radius:10px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:10px;">
              <span>📧</span>
              <span style="font-size:14px;">Notifications par email</span>
            </div>
            <input type="checkbox" ${currentUser.notificationPreferences?.email ? 'checked' : ''} onchange="toggleNotification('email')" style="width:20px;height:20px;">
          </label>
          <label style="display:flex;align-items:center;justify-content:space-between;padding:12px;background:rgba(15,23,42,0.5);border-radius:10px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:10px;">
              <span>📱</span>
              <span style="font-size:14px;">Notifications SMS</span>
            </div>
            <input type="checkbox" ${currentUser.notificationPreferences?.sms ? 'checked' : ''} onchange="toggleNotification('sms')" style="width:20px;height:20px;">
          </label>
        </div>
      </div>
      
      <!-- Thème -->
      <div style="margin-bottom:20px;">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;font-weight:600;">🎨 APPARENCE</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
          <button onclick="openColorPickerModal()" style="padding:16px;border-radius:12px;border:1px solid var(--ui-card-border);background:linear-gradient(135deg,#1e293b,#0f172a);color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            <div style="font-size:20px;margin-bottom:4px;">🎨</div>
            Couleurs
          </button>
          <button onclick="cycleMapTheme()" style="padding:16px;border-radius:12px;border:1px solid var(--ui-card-border);background:linear-gradient(135deg,#1e293b,#0f172a);color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            <div style="font-size:20px;margin-bottom:4px;">🗺️</div>
            Thème carte
          </button>
          <button onclick="showNotification('🌍 Langue à venir', 'info')" style="padding:16px;border-radius:12px;border:1px solid var(--ui-card-border);background:linear-gradient(135deg,#1e293b,#0f172a);color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            <div style="font-size:20px;margin-bottom:4px;">🌍</div>
            Langue
          </button>
        </div>
      </div>
      
      <!-- Confidentialité - Ce qui est visible publiquement -->
      <div style="margin-bottom:20px;">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;font-weight:600;">🔒 CONFIDENTIALITÉ</div>
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:12px;">Choisissez ce qui est visible par les autres utilisateurs</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          <!-- Toujours visibles (non modifiables) -->
          <div style="padding:10px 12px;background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.2);border-radius:8px;display:flex;align-items:center;justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>👤</span>
              <span style="font-size:13px;">Nom + Avatar</span>
            </div>
            <span style="font-size:11px;color:#00ffc3;font-weight:600;">Toujours visible</span>
          </div>
          
          <!-- Options modifiables -->
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📝</span>
              <span style="font-size:13px;">Ma bio / description</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showBio !== false ? 'checked' : ''} onchange="togglePrivacy('showBio')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📧</span>
              <span style="font-size:13px;">Mon email</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showEmail ? 'checked' : ''} onchange="togglePrivacy('showEmail')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📍</span>
              <span style="font-size:13px;">Mes adresses</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showAddresses ? 'checked' : ''} onchange="togglePrivacy('showAddresses')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>❤️</span>
              <span style="font-size:13px;">Mes favoris</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showFavorites !== false ? 'checked' : ''} onchange="togglePrivacy('showFavorites')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📅</span>
              <span style="font-size:13px;">Mon agenda</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showAgenda !== false ? 'checked' : ''} onchange="togglePrivacy('showAgenda')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>🎉</span>
              <span style="font-size:13px;">Mes participations</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showParticipating !== false ? 'checked' : ''} onchange="togglePrivacy('showParticipating')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>👥</span>
              <span style="font-size:13px;">Mes amis</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showFriends !== false ? 'checked' : ''} onchange="togglePrivacy('showFriends')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📊</span>
              <span style="font-size:13px;">Mes statistiques</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showActivity !== false ? 'checked' : ''} onchange="togglePrivacy('showActivity')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
        </div>
      </div>
      
      <!-- Compte -->
      <div style="margin-bottom:20px;">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;font-weight:600;">👤 COMPTE</div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <button onclick="showNotification('📧 Modification email à venir', 'info')" style="padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;text-align:left;display:flex;align-items:center;gap:10px;font-size:14px;">
            <span>📧</span> Modifier mon email
          </button>
          <button onclick="showNotification('🔒 Modification mot de passe à venir', 'info')" style="padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;text-align:left;display:flex;align-items:center;gap:10px;font-size:14px;">
            <span>🔒</span> Modifier mon mot de passe
          </button>
          <button onclick="showNotification('🗑️ Suppression compte à venir', 'info')" style="padding:12px;border-radius:10px;border:1px solid rgba(239,68,68,0.3);background:rgba(239,68,68,0.05);color:#ef4444;cursor:pointer;text-align:left;display:flex;align-items:center;gap:10px;font-size:14px;">
            <span>🗑️</span> Supprimer mon compte
          </button>
        </div>
      </div>
      
      <button onclick="openAccountModal()" style="width:100%;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;">
        ← Retour au compte
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
}

function toggleNotification(type) {
  if (!currentUser.notificationPreferences) {
    currentUser.notificationPreferences = { email: true, sms: false };
  }
  currentUser.notificationPreferences[type] = !currentUser.notificationPreferences[type];
  saveUserData();
  showNotification(`${type === 'email' ? '📧' : '📱'} Notifications ${type} ${currentUser.notificationPreferences[type] ? 'activées' : 'désactivées'}`, 'success');
}

// Basculer une option de confidentialité
// Modal Modifier le profil
function openEditProfileModal() {
  // Construire la valeur de l'adresse de manière sécurisée
  let addressValue = '';
  try {
    if (currentUser.postalAddress) {
      if (typeof currentUser.postalAddress === 'object' && currentUser.postalAddress !== null) {
        const parts = [];
        if (currentUser.postalAddress.address) parts.push(currentUser.postalAddress.address);
        if (currentUser.postalAddress.city) parts.push(currentUser.postalAddress.city);
        if (currentUser.postalAddress.zip) parts.push(currentUser.postalAddress.zip);
        addressValue = parts.join(', ');
      } else if (typeof currentUser.postalAddress === 'string') {
        addressValue = currentUser.postalAddress;
      }
    }
  } catch (e) {
    console.warn('Erreur construction adresse:', e);
    addressValue = '';
  }
  
  const html = `
    <div style="padding:24px;max-width:500px;margin:0 auto;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
        <h2 style="margin:0;font-size:22px;font-weight:800;color:#fff;display:flex;align-items:center;gap:10px;">
          <span>✏️</span> Modifier mon profil
        </h2>
        <button onclick="openAccountModal()" style="background:none;border:none;font-size:24px;cursor:pointer;color:var(--ui-text-muted);transition:color 0.2s;" onmouseover="this.style.color='#fff';" onmouseout="this.style.color='var(--ui-text-muted)';">✕</button>
      </div>
      
      <!-- Photo de profil -->
      <div style="margin-bottom:24px;text-align:center;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:12px;">📸 Photo de profil</label>
        <div style="position:relative;display:inline-block;">
          <div id="edit-profile-photo-preview" style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:32px;border:3px solid rgba(255,255,255,0.2);overflow:hidden;margin:0 auto;position:relative;">
            ${(() => {
              // PRIORITÉ: profile_photo_url > profilePhoto > avatarUrl > avatar
              const avatarUrl = currentUser.profile_photo_url || currentUser.profilePhoto || currentUser.avatarUrl || currentUser.avatar;
              if (avatarUrl && (avatarUrl.startsWith('http') || avatarUrl.startsWith('data:image'))) {
                const safeUrl = avatarUrl.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
                return `<img src="${safeUrl}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;position:absolute;top:0;left:0;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';" /><div style="display:none;width:100%;height:100%;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);align-items:center;justify-content:center;font-size:32px;position:absolute;top:0;left:0;">👤</div>`;
              }
              return '<div style="width:100%;height:100%;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:32px;">👤</div>';
            })()}
          </div>
          <input type="file" id="edit-profile-photo-input" accept="image/*" style="display:none;" onchange="handleEditProfilePhoto(event)">
          <button onclick="document.getElementById('edit-profile-photo-input').click()" style="margin-top:12px;padding:8px 16px;border-radius:8px;border:2px solid rgba(0,255,195,0.3);background:rgba(0,255,195,0.1);color:#00ffc3;font-weight:600;font-size:13px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.background='rgba(0,255,195,0.2)';this.style.borderColor='rgba(0,255,195,0.5)';" onmouseout="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.3)';">
            📷 Changer la photo
          </button>
        </div>
      </div>
      
      <!-- Nom d'utilisateur -->
      <div style="margin-bottom:20px;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">👤 Nom d'utilisateur</label>
        <input type="text" id="edit-profile-username" value="${escapeHtml(currentUser.username || '')}" placeholder="Votre nom d'utilisateur" maxlength="20" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
        <div style="font-size:11px;color:var(--ui-text-muted);margin-top:4px;">Ce nom sera visible par tous les utilisateurs</div>
      </div>
      
      <!-- Adresse postale -->
      <div style="margin-bottom:24px;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📍 Adresse postale</label>
        <input type="text" id="edit-profile-address" value="${escapeHtml(addressValue)}" placeholder="Rue, Ville, Code postal" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
      </div>
      
      <!-- Boutons -->
      <div style="display:flex;gap:12px;">
        <button onclick="saveProfileChanges()" style="flex:1;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(0,255,195,0.3)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none';">
          💾 Enregistrer
        </button>
        <button onclick="openAccountModal()" style="flex:1;padding:14px;border-radius:12px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:15px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
          Annuler
        </button>
      </div>
    </div>
  `;
  
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que le modal est ouvert avant d'injecter le HTML
  const modal = document.getElementById("publish-modal-inner");
  const backdrop = document.getElementById("publish-modal-backdrop");
  
  if (!modal || !backdrop) {
    console.error('[EDIT PROFILE] ❌ Modal non trouvé');
    if (typeof showNotification === 'function') {
      showNotification('⚠️ Erreur: Modal non trouvé', 'error');
    }
    return;
  }
  
  // Forcer l'ouverture du modal
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.opacity = '1';
  backdrop.style.zIndex = '9999';
  modal.style.display = 'block';
  modal.style.visibility = 'visible';
  modal.style.opacity = '1';
  
  // Injecter le HTML
  modal.innerHTML = html;
  
  console.log('[EDIT PROFILE] ✅ Formulaire de modification affiché');
  
  // ⚠️⚠️⚠️ CRITIQUE : Empêcher la fermeture du modal pendant l'injection
  // Attendre un peu pour que le HTML soit complètement injecté
  setTimeout(() => {
    // Réattacher les event listeners après l'injection
    const closeBtn = modal.querySelector('.modal-close-btn, [onclick*="closePublishModal"]');
    if (closeBtn) {
      closeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        e.preventDefault();
        closePublishModal(e);
      });
    }
  }, 100);
}

// Gérer le changement de photo de profil
function handleEditProfilePhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  if (!file.type.startsWith('image/')) {
    showNotification("⚠️ Veuillez sélectionner une image", "warning");
    return;
  }
  
  const reader = new FileReader();
  reader.onload = function(e) {
    const photoUrl = e.target.result;
    const preview = document.getElementById('edit-profile-photo-preview');
    if (preview) {
      preview.innerHTML = `<img src="${photoUrl}" style="width:100%;height:100%;object-fit:cover;" />`;
    }
    // Stocker temporairement pour la sauvegarde
    window.tempProfilePhoto = photoUrl;
  };
  reader.readAsDataURL(file);
}

// Sauvegarder les modifications du profil - AVEC VALIDATION GOOGLE/EMAIL
async function saveProfileChanges() {
  const username = document.getElementById('edit-profile-username')?.value.trim();
  const address = document.getElementById('edit-profile-address')?.value.trim();
  const photo = window.tempProfilePhoto || currentUser.profile_photo_url || currentUser.profilePhoto;
  
  if (!username || username.length < 3) {
    showNotification("⚠️ Le nom d'utilisateur doit contenir au moins 3 caractères", "warning");
    return;
  }
  
  // Sauvegarder directement les modifications
  window.pendingProfileChanges = {
    username: username,
    postalAddress: address,
    photo: photo
  };
  
  // Appliquer directement sans confirmation Google/Email
  await applyProfileChanges();
}

// Afficher le choix de validation pour les modifications de profil
function showProfileVerificationChoice() {
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    showNotification("⚠️ Erreur d'affichage", "warning");
    return;
  }
  
  modal.innerHTML = `
    <div style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
      <button onclick="openEditProfileModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <div style="margin-bottom:32px;">
        <div style="font-size:64px;margin-bottom:16px;">🔐</div>
        <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Confirmer les modifications</h2>
        <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Choisissez votre méthode de vérification</p>
      </div>
      
      <div style="display:flex;flex-direction:column;gap:12px;">
        <button onclick="confirmProfileChangesWithGoogle()" style="width:100%;padding:16px;border-radius:12px;border:2px solid rgba(0,255,195,0.3);background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1));color:var(--ui-text-main);font-weight:600;font-size:15px;cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:12px;" onmouseover="this.style.borderColor='rgba(0,255,195,0.6)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2))';" onmouseout="this.style.borderColor='rgba(0,255,195,0.3)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1))';">
          <span>🔵</span> Confirmer avec Google
        </button>
        <button onclick="confirmProfileChangesWithEmail()" style="width:100%;padding:16px;border-radius:12px;border:2px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:var(--ui-text-main);font-weight:600;font-size:15px;cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:12px;" onmouseover="this.style.borderColor='rgba(255,255,255,0.4)';this.style.background='rgba(255,255,255,0.1)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.2)';this.style.background='rgba(255,255,255,0.05)';">
          <span>📧</span> Confirmer par email
        </button>
      </div>
    </div>
  `;
}

// Confirmer les modifications avec Google
async function confirmProfileChangesWithGoogle() {
  if (!window.pendingProfileChanges) {
    showNotification("⚠️ Aucune modification en attente", "warning");
    return;
  }
  
  // Démarrer la connexion Google
  if (typeof window.startGoogleLogin === 'function') {
    window.isUpdatingProfile = true;
    window.startGoogleLogin();
  } else {
    showNotification("⚠️ Erreur de connexion Google", "warning");
  }
}

// Confirmer les modifications avec Email
async function confirmProfileChangesWithEmail() {
  if (!window.pendingProfileChanges) {
    showNotification("⚠️ Aucune modification en attente", "warning");
    return;
  }
  
  // Envoyer un email de vérification
  try {
    const response = await fetch(`${window.API_BASE_URL || '/api'}/user/send-profile-verification-link`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: currentUser.email,
        changes: window.pendingProfileChanges
      })
    });
    
    if (response.ok) {
      showNotification("✅ Email de vérification envoyé ! Vérifiez votre boîte mail.", "success");
      openAccountModal();
    } else {
      showNotification("⚠️ Erreur lors de l'envoi de l'email", "warning");
    }
  } catch (error) {
    console.error('Erreur envoi email:', error);
    showNotification("⚠️ Erreur lors de l'envoi de l'email", "warning");
  }
}

// Appliquer les modifications après validation
async function applyProfileChanges() {
  if (!window.pendingProfileChanges) return;
  
  const { username, postalAddress, photo } = window.pendingProfileChanges;
  
  // Mettre à jour currentUser
  currentUser.username = username;
  currentUser.postalAddress = postalAddress;
  if (photo) {
    currentUser.profile_photo_url = photo;
    currentUser.profilePhoto = photo;
  }
  
  // Sauvegarder dans localStorage
  try {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (e) {
    try { sessionStorage.setItem('currentUser', JSON.stringify(currentUser)); } catch (e2) {}
  }
  
  // Mettre à jour le backend
  if (currentUser.isLoggedIn && currentUser.id) {
    try {
      const response = await fetch(`${window.API_BASE_URL || '/api'}/user/profile`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken') || ''}`
        },
        body: JSON.stringify({
          userId: currentUser.id,
          username: username,
          postalAddress: postalAddress,
          profilePhoto: photo
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.user) {
          currentUser = { ...currentUser, ...data.user };
          try {
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
          } catch (e) {
            try { sessionStorage.setItem('currentUser', JSON.stringify(currentUser)); } catch (e2) {}
          }
        }
      }
    } catch (error) {
      console.warn('Erreur sauvegarde profil backend:', error);
    }
  }
  
  // Nettoyer
  window.pendingProfileChanges = null;
  window.isUpdatingProfile = false;
  
  showNotification("✅ Profil modifié avec succès !", "success");
  openAccountModal();
  
  // Mettre à jour l'affichage
  if (typeof window.updateAccountBlock === 'function') {
    window.updateAccountBlock();
  }
}

// Exposer les fonctions globalement pour les onclick
// Exposer les fonctions globalement pour les onclick
window.openEditProfileModal = openEditProfileModal;
window.handleEditProfilePhoto = handleEditProfilePhoto;
window.saveProfileChanges = saveProfileChanges;

// Vérifier que les fonctions sont bien exposées
console.log('✅ Fonctions profil exposées:', {
  openEditProfileModal: typeof window.openEditProfileModal,
  handleEditProfilePhoto: typeof window.handleEditProfilePhoto,
  saveProfileChanges: typeof window.saveProfileChanges
});

function togglePrivacy(setting) {
  if (!currentUser.privacySettings) {
    currentUser.privacySettings = {
      showName: true,
      showAvatar: true,
      showBio: true,
      showEmail: false,
      showAddresses: false,
      showFavorites: true,
      showAgenda: true,
      showParticipating: true,
      showFriends: true,
      showActivity: true
    };
  }
  
  currentUser.privacySettings[setting] = !currentUser.privacySettings[setting];
  saveUserData();
  
  const labels = {
    showBio: 'Bio',
    showEmail: 'Email',
    showAddresses: 'Adresses',
    showFavorites: 'Favoris',
    showAgenda: 'Agenda',
    showParticipating: 'Participations',
    showFriends: 'Amis',
    showActivity: 'Statistiques'
  };
  
  showNotification(
    `${currentUser.privacySettings[setting] ? '👁️ Visible' : '🔒 Masqué'}: ${labels[setting] || setting}`, 
    'success'
  );
}

window.togglePrivacy = togglePrivacy;

function openFavoritesModal() {
  // Utiliser currentUser.favorites au lieu de currentUser.likes
  const favorites = currentUser.favorites.map(fav => {
    const type = fav.mode || fav.type;
    const id = parseInt(fav.id);
    const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
    const item = data.find(i => i.id === id);
    if (item) {
      return { ...item, favoriteId: fav.id };
    }
    return null;
  }).filter(Boolean);

  const html = `
    <div style="padding:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h2 style="margin:0;font-size:18px;">❤️ Mes Favoris</h2>
        <button onclick="closePublishModal()" style="background:none;border:none;font-size:20px;cursor:pointer;color:var(--ui-text-muted);">✕</button>
      </div>
      
      ${favorites.length === 0 ? `
        <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
          <div style="font-size:48px;margin-bottom:16px;">💔</div>
          <p>Aucun favori pour le moment</p>
        </div>
      ` : `
        <div style="margin-bottom:12px;font-size:12px;color:var(--ui-text-muted);text-align:center;">
          ${favorites.length} ${favorites.length === 1 ? 'favori' : 'favoris'}
        </div>
        <div id="favorites-list-container" style="max-height:calc(80vh - 180px);overflow-y:auto;">
          ${favorites.slice(0, 20).map(item => `
            <div style="display:flex;gap:12px;padding:12px;border-radius:12px;margin-bottom:8px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;" onclick="focusOnItem('${item.type}', ${item.id})">
              <div style="width:60px;height:60px;border-radius:8px;background:linear-gradient(135deg,#ef4444,#f97316);display:flex;align-items:center;justify-content:center;font-size:24px;">
                ${getCategoryEmoji(item)}
              </div>
              <div style="flex:1;">
                <div style="font-weight:600;margin-bottom:4px;">${escapeHtml(item.title || item.name)}</div>
                <div style="font-size:12px;color:var(--ui-text-muted);">${item.city}</div>
              </div>
            </div>
          `).join('')}
        </div>
        ${favorites.length > 20 ? `
          <div style="text-align:center;margin-top:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:8px;border:1px solid var(--ui-card-border);">
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">
              Affichage de 20 sur ${favorites.length} favoris
            </div>
            <button onclick="loadMoreFavorites()" style="padding:8px 16px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">
              Afficher plus (${Math.min(20, favorites.length - 20)} suivants)
            </button>
          </div>
        ` : ''}
      `}
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
  
  // Stocker les favoris complets pour la pagination
  window.favoritesFull = favorites;
  window.favoritesDisplayed = 20;
}

function loadMoreFavorites() {
  if (!window.favoritesFull) return;
  const container = document.getElementById("favorites-list-container");
  if (!container) return;
  
  const start = window.favoritesDisplayed;
  const end = Math.min(start + 20, window.favoritesFull.length);
  const newItems = window.favoritesFull.slice(start, end);
  
  newItems.forEach(item => {
    const itemHtml = `
      <div style="display:flex;gap:12px;padding:12px;border-radius:12px;margin-bottom:8px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;" onclick="focusOnItem('${item.type}', ${item.id})">
        <div style="width:60px;height:60px;border-radius:8px;background:linear-gradient(135deg,#ef4444,#f97316);display:flex;align-items:center;justify-content:center;font-size:24px;">
          ${getCategoryEmoji(item)}
        </div>
        <div style="flex:1;">
          <div style="font-weight:600;margin-bottom:4px;">${escapeHtml(item.title || item.name)}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">${item.city}</div>
        </div>
      </div>
    `;
    container.insertAdjacentHTML('beforeend', itemHtml);
  });
  
  window.favoritesDisplayed = end;
  
  // Mettre à jour le bouton "Afficher plus"
  const moreButton = container.nextElementSibling?.querySelector('button');
  if (moreButton) {
    const remaining = window.favoritesFull.length - end;
    if (remaining > 0) {
      moreButton.textContent = `Afficher plus (${Math.min(20, remaining)} suivants)`;
    } else {
      moreButton.parentElement.remove();
    }
  }
}

function focusOnItem(type, id) {
  closePublishModal();
  const key = `${type}:${id}`;
  const marker = markerMap[key];
  if (marker && map) {
    map.setView(marker.getLatLng(), 14);
    setTimeout(() => marker.openPopup(), 300);
  }
}

// REMOVED: logout() est maintenant dans auth.js et exposé via window.logout

// ============================================
// UTILITAIRES
// ============================================
function formatEventDateRange(startIso, endIso, isScraped = false) {
  // Date obligatoire - référence: js/core/utils.js
  if (!startIso || !endIso) return "";
  const s = new Date(startIso);
  const e = new Date(endIso);

  const optD = { day: "2-digit", month: "2-digit" };
  const optT = { hour: "2-digit", minute: "2-digit" };

  const sd = s.toLocaleDateString("fr-CH", optD);
  const ed = e.toLocaleDateString("fr-CH", optD);
  
  // Pour les événements scrapés, on affiche --:-- à la place de l'heure
  if (isScraped) {
    if (sd === ed) return `${sd} --:-- – --:--`;
    return `${sd} --:-- – ${ed} --:--`;
  }
  
  const st = s.toLocaleTimeString("fr-CH", optT);
  const et = e.toLocaleTimeString("fr-CH", optT);

  if (sd === ed) return `${sd} ${st}–${et}`;
  return `${sd} ${st} – ${ed} ${et}`;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Retirer tous les numéros de téléphone des descriptions (bookings, services)
function stripPhoneNumbers(text) {
  if (!text) return "";
  return String(text)
    .replace(/📞\s*[^\n|]*/g, '')
    .replace(/☎\s*[^\n|]*/g, '')
    .replace(/📱\s*[^\n|]*[\d\s\.\-\(\)]{7,}[^\n|]*/g, '')
    .replace(/(?:Tel|Tél|Téléphone|Phone|Tel\.|Tél\.)\s*[:.]?\s*[\+]?[\d\s\.\-\(\)]{7,}/gi, '')
    .replace(/(?:Mobile|Portable|Cell)\s*[:.]?\s*[\+]?[\d\s\.\-\(\)]{7,}/gi, '')
    .replace(/(?:\+\d{1,3}[\s\.\-]?)?\(?\d{2,4}\)?[\s\.\-]?\d{2,4}[\s\.\-]?\d{2,4}[\s\.\-]?\d{0,4}/g, (m) => {
      const d = m.replace(/\D/g, '');
      return d.length >= 8 ? '' : m;
    })
    .replace(/\d{2}[\s\.\-]?\d{2}[\s\.\-]?\d{2}[\s\.\-]?\d{2}[\s\.\-]?\d{2}/g, '')
    .replace(/\b0\d[\s\.\-]?\d{2}[\s\.\-]?\d{2}[\s\.\-]?\d{2}[\s\.\-]?\d{2}\b/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

// ============================================
// DRAG & DROP PANNEAU FILTRE
// ============================================
function initDragDropPanel() {
  const panel = document.getElementById("left-panel");
  if (!panel) return;
  
  let isDragging = false;
  let startX, startY, startLeft, startTop;
  
  panel.addEventListener("mousedown", (e) => {
    // Ne drag que si on clique sur l'en-tête
    if (e.target.closest("#explorer-columns") || e.target.closest("input") || e.target.closest("button")) {
      return;
    }
    
    isDragging = true;
    panel.classList.add("dragging");
    
    startX = e.clientX;
    startY = e.clientY;
    startLeft = panel.offsetLeft;
    startTop = panel.offsetTop;
    
    e.preventDefault();
  });
  
  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    
    panel.style.left = (startLeft + dx) + "px";
    panel.style.top = (startTop + dy) + "px";
  });
  
  document.addEventListener("mouseup", () => {
    isDragging = false;
    panel.classList.remove("dragging");
  });
}

