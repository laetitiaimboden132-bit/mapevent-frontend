// ============================================================
// translations.js - Système de traduction multi-provider (Google/DeepL/Azure/Libre), auto-traduction, cache
// Extrait de map_logic.js pour meilleure lisibilité
// ============================================================

//    - Les catégories sont traduites (via dictionnaire)
//    - L'interface est traduite (via `translations`)
//
// 5. OPTIMISATIONS :
//    - Cache agressif des traductions (éviter les appels répétés)
//    - Traduction lazy (seulement ce qui est visible)
//    - Préchargement des traductions courantes
//    - Support des langues RTL (arabe, hébreu)
//
// ============================================
// DICTIONNAIRE DE TRADUCTIONS COMPLET (déplacé au début du fichier)
// ============================================
// Ce dictionnaire a été déplacé après la déclaration de currentLanguage pour éviter les erreurs d'initialisation
// L'ancienne déclaration a été supprimée - voir ligne 55 pour la nouvelle déclaration

// ============================================
// API DE TRADUCTION - INTÉGRATION
// ============================================
//
// 🎯 MEILLEURES APIs DE TRADUCTION (avec liens) :
//

// Initialisation du dictionnaire de traductions complet
// NOTE: Cette section a été supprimée car les traductions sont déjà définies ailleurs dans le fichier
// (voir lignes 219-431 pour la structure complète et correcte)
if (typeof window !== 'undefined') {
  window.translations = window.translations || { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
}

// NOTE: Section de traductions mal formée supprimée (lignes 12663-12860)
// Les traductions sont déjà définies correctement ailleurs dans le fichier (lignes 219-431)

// ============================================
// API DE TRADUCTION - INTÉGRATION
// ============================================
//
// 🎯 MEILLEURES APIs DE TRADUCTION (avec liens) :
//
// 1. GOOGLE CLOUD TRANSLATE API (RECOMMANDÉ - Meilleure qualité)
//    📍 Lien : https://cloud.google.com/translate/docs/setup
//    💰 Prix : 20$/million de caractères (gratuit jusqu'à 500k/mois)
//    ✅ Avantages : Meilleure qualité, support 100+ langues, très rapide
//    ✅ Paiement : Carte bancaire, Twint via Stripe
//    📝 Documentation : https://cloud.google.com/translate/docs/reference/rest/v2/translate
//
// 2. DEEPL API (EXCELLENTE QUALITÉ - Spécialisé européen)
// ============================================
// API DE TRADUCTION - INTÉGRATION
// ============================================
//
// 🎯 MEILLEURES APIs DE TRADUCTION (avec liens) :
//
// 1. GOOGLE CLOUD TRANSLATE API (RECOMMANDÉ - Meilleure qualité)
//    📍 Lien : https://cloud.google.com/translate/docs/setup
//    💰 Prix : 20$/million de caractères (gratuit jusqu'à 500k/mois)
//    ✅ Avantages : Meilleure qualité, support 100+ langues, très rapide
//    ✅ Paiement : Carte bancaire, Twint via Stripe
//    📝 Documentation : https://cloud.google.com/translate/docs/reference/rest/v2/translate
//
// 2. DEEPL API (EXCELLENTE QUALITÉ - Spécialisé européen)
//    📍 Lien : https://www.deepl.com/fr/pro-api
//    💰 Prix : 25€/million de caractères (gratuit jusqu'à 500k/mois)
//    ✅ Avantages : Meilleure qualité pour langues européennes, très naturel
//    ✅ Paiement : Carte bancaire, PayPal, Twint via Stripe
//    📝 Documentation : https://www.deepl.com/fr/docs-api
//
// 3. AZURE TRANSLATOR (Microsoft - Bon compromis)
//    📍 Lien : https://azure.microsoft.com/fr-fr/services/cognitive-services/translator/
//    💰 Prix : 10$/million de caractères (gratuit jusqu'à 2M/mois)
//    ✅ Avantages : Bon prix, bonne qualité, intégration facile
//    ✅ Paiement : Carte bancaire, Twint via Stripe
//    📝 Documentation : https://docs.microsoft.com/fr-fr/azure/cognitive-services/translator/
//
// 4. LIBRETRANSLATE (GRATUIT - Open Source)
//    📍 Lien : https://libretranslate.com/
//    💰 Prix : GRATUIT (ou self-hosted)
//    ⚠️ Avantages : Gratuit, open source
//    ⚠️ Inconvénients : Qualité moindre, limité en langues
//    📝 Documentation : https://github.com/LibreTranslate/LibreTranslate
//
// 💡 RECOMMANDATION : Utiliser GOOGLE CLOUD TRANSLATE pour la production
//    → Meilleure qualité mondiale
//    → Support de toutes les langues
//    → Très fiable et rapide
//    → Paiement flexible (Twint via Stripe)
//
// 🔧 CONFIGURATION :
//    1. Créer un compte Google Cloud : https://console.cloud.google.com/
//    2. Activer l'API Translate : https://console.cloud.google.com/apis/library/translate.googleapis.com
//    3. Créer une clé API : https://console.cloud.google.com/apis/credentials
//    4. Configurer le paiement (Twint via Stripe accepté)
//    5. Mettre la clé dans les variables d'environnement (NE JAMAIS la commiter!)
//
// Cache pour les traductions de contenu (évite les appels répétés)
const contentTranslationCache = {};

// ============================================
// SYSTÈME INTELLIGENT MULTI-PROVIDER DE TRADUCTION
// ============================================
// Stratégie #1 Mondial : Utiliser plusieurs providers selon la région/langue
// pour optimiser qualité, coûts et vitesse

// Configuration des providers de traduction
const TRANSLATION_PROVIDERS = {
  google: {
    name: "Google Cloud Translate",
    apiKey: "", // À configurer
    endpoint: "https://translation.googleapis.com/language/translate/v2",
    regions: ["global"], // Toutes les régions
    languages: ["all"], // Toutes les langues
    quality: "excellent",
    speed: "very_fast",
    cost: "medium",
    priority: 1 // Priorité pour l'Europe et langues principales
  },
  deepl: {
    name: "DeepL API",
    apiKey: "", // À configurer
    endpoint: "https://api-free.deepl.com/v2/translate",
    regions: ["europe", "americas"], // Spécialisé Europe/Amériques
    languages: ["en", "fr", "de", "es", "it", "pt", "ru", "pl", "nl", "ja", "zh"],
    quality: "excellent", // Meilleure qualité pour langues européennes
    speed: "fast",
    cost: "medium",
    priority: 2 // Priorité pour langues européennes
  },
  azure: {
    name: "Azure Translator",
    apiKey: "", // À configurer
    endpoint: "https://api.cognitive.microsofttranslator.com/translate",
    regions: ["global"],
    languages: ["all"],
    quality: "very_good",
    speed: "fast",
    cost: "low", // Meilleur rapport qualité/prix
    priority: 3 // Fallback économique
  },
  libretranslate: {
    name: "LibreTranslate",
    apiKey: "", // Optionnel (gratuit)
    endpoint: "https://libretranslate.com/translate",
    regions: ["global"],
    languages: ["en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja"],
    quality: "good",
    speed: "medium",
    cost: "free",
    priority: 4 // Fallback gratuit
  }
};

// Mapping intelligent région/langue → provider optimal
const INTELLIGENT_PROVIDER_MAPPING = {
  // Europe → DeepL (meilleure qualité) ou Google (fallback)
  "europe": {
    primary: "deepl",
    fallback: "google",
    languages: ["fr", "en", "de", "es", "it", "pt", "ru", "pl", "nl", "cs", "sk", "hu", "ro", "bg", "hr", "sl", "et", "lv", "lt", "fi", "sv", "da", "no", "is", "ga", "mt", "el"]
  },
  // Amériques → Google (meilleure couverture) ou DeepL
  "americas": {
    primary: "google",
    fallback: "deepl",
    languages: ["en", "es", "pt", "fr"]
  },
  // Asie → Google (meilleure couverture langues asiatiques)
  "asia": {
    primary: "google",
    fallback: "azure",
    languages: ["zh", "ja", "ko", "hi", "th", "vi", "id", "ms", "tl", "my", "km", "lo"]
  },
  // Afrique → Google (meilleure couverture)
  "africa": {
    primary: "google",
    fallback: "azure",
    languages: ["ar", "sw", "am", "zu", "xh", "af", "yo", "ig", "ha", "fr", "en", "pt"]
  },
  // Moyen-Orient → Google (meilleure couverture arabe)
  "middle_east": {
    primary: "google",
    fallback: "azure",
    languages: ["ar", "he", "fa", "tr", "ku"]
  },
  // Océanie → Google ou DeepL
  "oceania": {
    primary: "google",
    fallback: "deepl",
    languages: ["en", "fr", "mi", "haw"]
  }
};

// Fonction intelligente pour sélectionner le meilleur provider
function getBestProviderForTranslation(sourceLang, targetLang, region = null) {
  // Si région spécifiée, utiliser le mapping intelligent
  if (region && INTELLIGENT_PROVIDER_MAPPING[region]) {
    const mapping = INTELLIGENT_PROVIDER_MAPPING[region];
    const provider = TRANSLATION_PROVIDERS[mapping.primary];
    
    // Vérifier si le provider supporte la langue
    if (provider && (provider.languages.includes(targetLang) || provider.languages.includes("all"))) {
      if (provider.apiKey) return mapping.primary;
    }
    
    // Fallback
    const fallbackProvider = TRANSLATION_PROVIDERS[mapping.fallback];
    if (fallbackProvider && fallbackProvider.apiKey) {
      return mapping.fallback;
    }
  }
  
  // Détection automatique de la région selon la langue
  let detectedRegion = "global";
  
  // Langues européennes → Europe
  if (["fr", "de", "es", "it", "pt", "ru", "pl", "nl", "cs", "sk", "hu", "ro", "bg", "hr", "sl", "et", "lv", "lt", "fi", "sv", "da", "no"].includes(targetLang)) {
    detectedRegion = "europe";
  }
  // Langues asiatiques → Asie
  else if (["zh", "ja", "ko", "hi", "th", "vi", "id", "ms", "tl", "my", "km", "lo"].includes(targetLang)) {
    detectedRegion = "asia";
  }
  // Langues arabes → Moyen-Orient
  else if (["ar", "he", "fa"].includes(targetLang)) {
    detectedRegion = "middle_east";
  }
  
  // Utiliser le mapping détecté
  if (INTELLIGENT_PROVIDER_MAPPING[detectedRegion]) {
    const mapping = INTELLIGENT_PROVIDER_MAPPING[detectedRegion];
    const provider = TRANSLATION_PROVIDERS[mapping.primary];
    
    if (provider && provider.apiKey && (provider.languages.includes(targetLang) || provider.languages.includes("all"))) {
      return mapping.primary;
    }
    
    const fallbackProvider = TRANSLATION_PROVIDERS[mapping.fallback];
    if (fallbackProvider && fallbackProvider.apiKey) {
      return mapping.fallback;
    }
  }
  
  // Fallback final : Google (si disponible) ou Azure ou LibreTranslate
  if (TRANSLATION_PROVIDERS.google.apiKey) return "google";
  if (TRANSLATION_PROVIDERS.azure.apiKey) return "azure";
  if (TRANSLATION_PROVIDERS.libretranslate.apiKey) return "libretranslate";
  
  return null; // Aucun provider disponible
}

// Configuration globale (pour compatibilité)
const TRANSLATION_API_CONFIG = {
  provider: "auto", // "auto" = sélection intelligente
  apiKey: "", // Déprécié, utiliser TRANSLATION_PROVIDERS
  cacheEnabled: true,
  cacheMaxSize: 10000
};

// ============================================
// TRADUCTION AUTOMATIQUE COMPLÈTE - IA
// ============================================
// Fonction pour traduire automatiquement TOUT le contenu d'un item
// (titre, description, catégories, etc.) - Utilisée par l'IA
async function translateItemContentAuto(item, targetLang = currentLanguage) {
  if (!item || targetLang === "fr") return item; // Pas besoin de traduire si déjà en français
  
  const translated = { ...item };
  
  // Traduire le titre
  if (item.title) {
    translated.title = await translateContent(item.title, "auto", targetLang);
  }
  if (item.name) {
    translated.name = await translateContent(item.name, "auto", targetLang);
  }
  
  // Traduire la description
  if (item.description) {
    translated.description = await translateContent(item.description, "auto", targetLang);
  }
  
  // Traduire les catégories (si ce sont des strings)
  if (item.categories && Array.isArray(item.categories)) {
    translated.categories = await Promise.all(
      item.categories.map(cat => translateContent(cat, "auto", targetLang))
    );
  }
  
  // Traduire le nom de l'organisateur/artiste/entreprise
  if (item.organizer) {
    translated.organizer = await translateContent(item.organizer, "auto", targetLang);
  }
  if (item.artist) {
    translated.artist = await translateContent(item.artist, "auto", targetLang);
  }
  if (item.company) {
    translated.company = await translateContent(item.company, "auto", targetLang);
  }
  
  // Mettre en cache les traductions
  const cacheKey = `item_${item.id}_${targetLang}`;
  localStorage.setItem(cacheKey, JSON.stringify(translated));
  
  return translated;
}

// Version synchrone qui utilise le cache (pour affichage immédiat)
function getTranslatedItemSync(item, targetLang = currentLanguage) {
  if (!item || targetLang === "fr") return item;
  
  // Vérifier le cache
  const cacheKey = `item_${item.id}_${targetLang}`;
  const cached = localStorage.getItem(cacheKey);
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch (e) {
      console.warn("Erreur parsing cache traduction", e);
    }
  }
  
  // Si pas en cache, retourner l'original et lancer la traduction en arrière-plan
  translateItemContentAuto(item, targetLang).then(translated => {
    // Mettre à jour les popups si elles sont ouvertes
    refreshMarkers();
  });
  
  return item; // Retourner l'original en attendant
}

// Fonction pour traduire le contenu d'un événement (titre, description)
// Utilise le système intelligent multi-provider avec fallback automatique
async function translateContent(text, sourceLang = "auto", targetLang = currentLanguage, region = null) {
  if (!text || targetLang === sourceLang) return text;
  
  // Vérifier le cache
  const cacheKey = `${text}|${sourceLang}|${targetLang}`;
  if (TRANSLATION_API_CONFIG.cacheEnabled && contentTranslationCache[cacheKey]) {
    return contentTranslationCache[cacheKey];
  }
  
  // Sélectionner le meilleur provider intelligemment
  const provider = getBestProviderForTranslation(sourceLang, targetLang, region);
  
  if (!provider) {
    console.warn("⚠️ Aucun provider de traduction disponible. Retour du texte original.");
    return text;
  }
  
  try {
    let translated = text;
    let lastError = null;
    
    // Essayer le provider principal
    try {
      switch (provider) {
        case "google":
          translated = await translateWithGoogle(text, sourceLang, targetLang);
          break;
        case "deepl":
          translated = await translateWithDeepL(text, sourceLang, targetLang);
          break;
        case "azure":
          translated = await translateWithAzure(text, sourceLang, targetLang);
          break;
        case "libretranslate":
          translated = await translateWithLibreTranslate(text, sourceLang, targetLang);
          break;
        default:
          throw new Error("Provider inconnu");
      }
    } catch (error) {
      lastError = error;
      console.warn(`⚠️ Erreur avec ${provider}, tentative fallback...`, error);
      
      // Fallback automatique : essayer les autres providers
      const fallbackProviders = ["google", "azure", "libretranslate"].filter(p => p !== provider);
      
      for (const fallbackProvider of fallbackProviders) {
        const fallback = TRANSLATION_PROVIDERS[fallbackProvider];
        if (!fallback || !fallback.apiKey) continue;
        
        try {
          switch (fallbackProvider) {
            case "google":
              translated = await translateWithGoogle(text, sourceLang, targetLang);
              break;
            case "azure":
              translated = await translateWithAzure(text, sourceLang, targetLang);
              break;
            case "libretranslate":
              translated = await translateWithLibreTranslate(text, sourceLang, targetLang);
              break;
          }
          
          console.log(`✅ Traduction réussie avec fallback ${fallbackProvider}`);
          break; // Succès avec le fallback
        } catch (fallbackError) {
          console.warn(`❌ Fallback ${fallbackProvider} échoué`, fallbackError);
          continue; // Essayer le suivant
        }
      }
      
      // Si tous les fallbacks ont échoué
      if (translated === text && lastError) {
        throw lastError;
      }
    }
    
    // Mettre en cache
    if (TRANSLATION_API_CONFIG.cacheEnabled && translated !== text) {
      // Limiter la taille du cache
      const keys = Object.keys(contentTranslationCache);
      if (keys.length >= TRANSLATION_API_CONFIG.cacheMaxSize) {
        delete contentTranslationCache[keys[0]]; // Supprimer la plus ancienne
      }
      contentTranslationCache[cacheKey] = translated;
    }
    
    return translated;
  } catch (error) {
    console.error("❌ Erreur traduction finale:", error);
    return text; // Retourner le texte original en cas d'erreur
  }
}

// Fonction pour traduire avec Google Cloud Translate
async function translateWithGoogle(text, sourceLang, targetLang) {
  const apiKey = TRANSLATION_PROVIDERS.google.apiKey;
  if (!apiKey) throw new Error("Clé API Google non configurée");
  
  const response = await fetch(
    `${TRANSLATION_PROVIDERS.google.endpoint}?key=${apiKey}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        q: text,
        source: sourceLang === "auto" ? "" : sourceLang,
        target: targetLang,
        format: "text"
      })
    }
  );
  
  if (!response.ok) throw new Error("Erreur Google Translate API");
  
  const data = await response.json();
  return data.data.translations[0].translatedText;
}

// Fonction pour traduire avec DeepL
async function translateWithDeepL(text, sourceLang, targetLang) {
  const apiKey = TRANSLATION_PROVIDERS.deepl.apiKey;
  if (!apiKey) throw new Error("Clé API DeepL non configurée");
  
  const response = await fetch(
    TRANSLATION_PROVIDERS.deepl.endpoint,
    {
      method: "POST",
      headers: {
        "Authorization": `DeepL-Auth-Key ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: [text],
        source_lang: sourceLang === "auto" ? null : sourceLang.toUpperCase(),
        target_lang: targetLang.toUpperCase()
      })
    }
  );
  
  if (!response.ok) throw new Error("Erreur DeepL API");
  
  const data = await response.json();
  return data.translations[0].text;
}

// Fonction pour traduire avec Azure Translator
async function translateWithAzure(text, sourceLang, targetLang) {
  const apiKey = TRANSLATION_PROVIDERS.azure.apiKey;
  if (!apiKey) throw new Error("Clé API Azure non configurée");
  
  const endpoint = TRANSLATION_PROVIDERS.azure.endpoint;
  const location = "global"; // ou la région de ta ressource Azure
  
  const response = await fetch(
    `${endpoint}?api-version=3.0&from=${sourceLang === "auto" ? "" : sourceLang}&to=${targetLang}`,
    {
      method: "POST",
      headers: {
        "Ocp-Apim-Subscription-Key": apiKey,
        "Ocp-Apim-Subscription-Region": location,
        "Content-Type": "application/json",
      },
      body: JSON.stringify([{ text }])
    }
  );
  
  if (!response.ok) throw new Error("Erreur Azure Translator API");
  
  const data = await response.json();
  return data[0].translations[0].text;
}

// Fonction pour traduire avec LibreTranslate (gratuit)
async function translateWithLibreTranslate(text, sourceLang, targetLang) {
  const response = await fetch(
    `https://libretranslate.com/translate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        q: text,
        source: sourceLang === "auto" ? "auto" : sourceLang,
        target: targetLang,
        format: "text"
      })
    }
  );
  
  if (!response.ok) throw new Error("Erreur LibreTranslate API");
  
  const data = await response.json();
  return data.translatedText;
}

// ============================================
// FONCTION POUR L'IA : TRADUIRE AUTOMATIQUEMENT LES POINTS
// ============================================
//
// Cette fonction permet à l'IA de traduire automatiquement les événements
// qu'elle insère depuis le bout du monde dans toutes les langues supportées
//
async function translateItemForAI(item, targetLanguages = ["fr", "en", "es", "zh", "hi"]) {
  if (!item || !TRANSLATION_API_CONFIG.apiKey) {
    console.warn("⚠️ Impossible de traduire : clé API manquante");
    return item;
  }
  
  // Détecter la langue source du contenu
  const sourceLang = detectLanguage(item.title || item.description || "");
  
  // Créer un objet de traductions
  if (!item.translations) item.translations = {};
  
  // Traduire dans chaque langue cible
  for (const targetLang of targetLanguages) {
    if (targetLang === sourceLang) continue; // Pas besoin de traduire dans la même langue
    
    try {
      // Traduire le titre
      if (item.title) {
        const titleKey = `title_${targetLang}`;
        if (!item.translations[titleKey]) {
          item.translations[titleKey] = await translateContent(item.title, sourceLang, targetLang);
        }
      }
      
      // Traduire la description
      if (item.description) {
        const descKey = `description_${targetLang}`;
        if (!item.translations[descKey]) {
          item.translations[descKey] = await translateContent(item.description, sourceLang, targetLang);
        }
      }
      
      // Traduire les catégories (via dictionnaire si possible, sinon API)
      if (item.categories && item.categories.length > 0) {
        const catKey = `categories_${targetLang}`;
        if (!item.translations[catKey]) {
          item.translations[catKey] = await Promise.all(
            item.categories.map(cat => translateContent(cat, sourceLang, targetLang))
          );
        }
      }
      
      console.log(`✅ Traduit en ${targetLang.toUpperCase()}: ${item.title || item.name}`);
    } catch (error) {
      console.error(`❌ Erreur traduction en ${targetLang}:`, error);
    }
  }
  
  return item;
}

// Fonction simple de détection de langue (basique)
function detectLanguage(text) {
  if (!text) return "en";
  
  // Détection basique par patterns
  const patterns = {
    fr: /[àâäéèêëïîôùûüÿç]/i,
    es: /[ñáéíóúü¿¡]/i,
    zh: /[\u4e00-\u9fff]/,
    hi: /[\u0900-\u097f]/,
    ar: /[\u0600-\u06ff]/,
    ja: /[\u3040-\u309f\u30a0-\u30ff]/,
    ko: /[\uac00-\ud7a3]/
  };
  
  for (const [lang, pattern] of Object.entries(patterns)) {
    if (pattern.test(text)) return lang;
  }
  
  return "en"; // Par défaut anglais
}

// Fonction pour obtenir le contenu traduit d'un item
function getTranslatedContent(item, field, lang = currentLanguage) {
  if (!item.translations) return item[field] || "";
  
  const key = `${field}_${lang}`;
  return item.translations[key] || item[field] || "";
}

// Fonction pour traduire un commentaire (avec bouton de traduction si différent de la langue actuelle)
function translateComment(comment, commentLang = "auto") {
  if (!comment) return "";
  
  // Protection contre les erreurs TDZ - utiliser directement window.t()
  // Si le commentaire est déjà dans la langue actuelle, pas besoin de traduire
  if (commentLang === currentLanguage || commentLang === "auto") {
    return comment;
  }
  
  // Sinon, afficher le commentaire original + bouton de traduction
  return `
    <div class="comment-translation-wrapper" data-original="${escapeHtml(comment)}" data-lang="${commentLang}">
      <div class="comment-original" style="margin-bottom:4px;">${escapeHtml(comment)}</div>
      <button onclick="translateThisComment(this)" style="background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);color:#00ffc3;padding:2px 8px;border-radius:4px;font-size:10px;cursor:pointer;">
        🌍 ${window.t("translate")}
      </button>
      <div class="comment-translated" style="display:none;margin-top:4px;padding:4px;background:rgba(0,255,195,0.05);border-left:2px solid #00ffc3;font-size:11px;"></div>
    </div>
  `;
}

// Fonction pour traduire un commentaire spécifique
async function translateThisComment(button) {
  // Protection contre les erreurs TDZ - utiliser directement window.t()
  
  const wrapper = button.closest(".comment-translation-wrapper");
  if (!wrapper) return;
  
  const original = wrapper.dataset.original;
  const sourceLang = wrapper.dataset.lang || "auto";
  const translatedDiv = wrapper.querySelector(".comment-translated");
  
  if (translatedDiv.style.display === "block") {
    translatedDiv.style.display = "none";
    button.textContent = `🌍 ${window.t("translate")}`;
    return;
  }
  
  button.textContent = `${window.t("loading")}...`;
  
  try {
    const translated = await translateContent(original, sourceLang, currentLanguage);
    translatedDiv.innerHTML = escapeHtml(translated);
    translatedDiv.style.display = "block";
    button.textContent = `🌍 ${window.t("hide_translation")}`;
  } catch (error) {
    console.error("Erreur traduction:", error);
    button.textContent = `🌍 ${window.t("translate")}`;
    showNotification(window.t("translation_error"), "error");
  }
}

// Fonction pour changer de langue
const LANG_FLAGS = { fr: "🇫🇷", en: "🇬🇧", es: "🇪🇸", zh: "🇨🇳", hi: "🇮🇳", de: "🇩🇪", it: "🇮🇹", pt: "🇵🇹", ru: "🇷🇺", ar: "🇸🇦", ja: "🇯🇵", ko: "🇰🇷", nl: "🇳🇱", tr: "🇹🇷", pl: "🇵🇱", vi: "🇻🇳", id: "🇮🇩", th: "🇹🇭", uk: "🇺🇦", sv: "🇸🇪", no: "🇳🇴", da: "🇩🇰", fi: "🇫🇮", el: "🇬🇷", he: "🇮🇱", ro: "🇷🇴", ms: "🇲🇾", cs: "🇨🇿", hu: "🇭🇺", sk: "🇸🇰", bg: "🇧🇬", hr: "🇭🇷", sr: "🇷🇸", lt: "🇱🇹", lv: "🇱🇻", et: "🇪🇪", sl: "🇸🇮", ta: "🇮🇳", bn: "🇧🇩", ur: "🇵🇰", fa: "🇮🇷", mr: "🇮🇳", sw: "🇰🇪", am: "🇪🇹", af: "🇿🇦", ca: "🇪🇸", pa: "🇮🇳", tl: "🇵🇭", my: "🇲🇲", ne: "🇳🇵", is: "🇮🇸", sq: "🇦🇱", mk: "🇲🇰", bs: "🇧🇦", gl: "🇪🇸", cy: "🇬🇧", ka: "🇬🇪", hy: "🇦🇲", az: "🇦🇿", kk: "🇰🇿", uz: "🇺🇿", ml: "🇮🇳", te: "🇮🇳", gu: "🇮🇳", kn: "🇮🇳", si: "🇱🇰", eu: "🇪🇸", mn: "🇲🇳", ga: "🇮🇪", lb: "🇱🇺", mt: "🇲🇹", yo: "🇳🇬", ha: "🇳🇬", ig: "🇳🇬", so: "🇸🇴", rw: "🇷🇼", mg: "🇲🇬", wo: "🇸🇳", st: "🇱🇸", tn: "🇧🇼", xh: "🇿🇦", zu: "🇿🇦", km: "🇰🇭", lo: "🇱🇦", sd: "🇵🇰", ps: "🇦🇫", ky: "🇰🇬", tk: "🇹🇲", tg: "🇹🇯", br: "🇫🇷", gd: "🇬🇧", fy: "🇳🇱", ku: "🇮🇶", ht: "🇭🇹", jv: "🇮🇩", su: "🇮🇩", ny: "🇲🇼", om: "🇪🇹", ti: "🇪🇷", dv: "🇲🇻", bo: "🇨🇳", dz: "🇧🇹", or: "🇮🇳", as: "🇮🇳", kmr: "🇹🇷", ckb: "🇮🇶" };
const LANG_CODES = { fr: "FR", en: "EN", es: "ES", zh: "ZH", hi: "HI", de: "DE", it: "IT", pt: "PT", ru: "RU", ar: "AR", ja: "JA", ko: "KO", nl: "NL", tr: "TR", pl: "PL", vi: "VI", id: "ID", th: "TH", uk: "UK", sv: "SV", no: "NO", da: "DA", fi: "FI", el: "EL", he: "HE", ro: "RO", ms: "MS", cs: "CS", hu: "HU", sk: "SK", bg: "BG", hr: "HR", sr: "SR", lt: "LT", lv: "LV", et: "ET", sl: "SL", ta: "TA", bn: "BN", ur: "UR", fa: "FA", mr: "MR", sw: "SW", am: "AM", af: "AF", ca: "CA", pa: "PA", tl: "TL", my: "MY", ne: "NE", is: "IS", sq: "SQ", mk: "MK", bs: "BS", gl: "GL", cy: "CY", ka: "KA", hy: "HY", az: "AZ", kk: "KK", uz: "UZ", ml: "ML", te: "TE", gu: "GU", kn: "KN", si: "SI", eu: "EU", mn: "MN", ga: "GA", lb: "LB", mt: "MT", yo: "YO", ha: "HA", ig: "IG", so: "SO", rw: "RW", mg: "MG", wo: "WO", st: "ST", tn: "TN", xh: "XH", zu: "ZU", km: "KM", lo: "LO", sd: "SD", ps: "PS", ky: "KY", tk: "TK", tg: "TG", br: "BR", gd: "GD", fy: "FY", ku: "KU", ht: "HT", jv: "JV", su: "SU", ny: "NY", om: "OM", ti: "TI", dv: "DV", bo: "BO", dz: "DZ", or: "OR", as: "AS", kmr: "KU", ckb: "KU" };

function setLanguage(lang) {
  if (!SUPPORTED_LANGUAGES.includes(lang)) return;
  
  currentLanguage = lang;
  localStorage.setItem("mapEventLanguage", lang);
  
  const flagEl = document.getElementById("current-lang-flag");
  const codeEl = document.getElementById("current-lang-code");
  
  if (flagEl) flagEl.textContent = LANG_FLAGS[lang] || "🌍";
  if (codeEl) codeEl.textContent = LANG_CODES[lang] || lang.toUpperCase();
  
  SUPPORTED_LANGUAGES.forEach(l => {
    const check = document.getElementById(`lang-check-${l}`);
    if (check) check.style.display = l === lang ? "block" : "none";
  });
  
  // Fermer le menu
  const menu = document.getElementById("language-menu");
  if (menu) menu.style.display = "none";
  
  // Re-traduire l'interface (à implémenter complètement plus tard)
  updateUITranslations();
  
  showNotification(`🌍 Langue changée : ${LANG_FLAGS[lang] || "🌍"} ${LANG_CODES[lang] || lang.toUpperCase()}`, "success");
}

// Fonction pour mettre à jour les traductions de l'UI (TOUT LE SITE)
function updateUITranslations() {
  // CRITIQUE: S'assurer que window.translations est complètement initialisé AVANT d'utiliser t()
  if (typeof window === 'undefined' || !window.translations || typeof window.translations !== 'object') {
    window.translations = {};
  }
  SUPPORTED_LANGUAGES.forEach(lang => {
    if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
      window.translations[lang] = window.translations[lang] || {};
    }
  });
  // NE JAMAIS redéfinir window.t ici - utiliser la version globale sécurisée
  // window.t est déjà défini au début du fichier et ne doit jamais être redéfini
  
  // 1. Topbar - Boutons principaux
  const filterBtn = document.querySelector('button[onclick="toggleLeftPanel()"]');
  if (filterBtn) filterBtn.textContent = `🔍 ${window.t("filter")}`;
  
  const listBtn = document.querySelector('button[onclick="toggleListView()"]');
  if (listBtn) listBtn.textContent = `📋 ${window.t("list")}`;
  
  // 2. Boutons de navigation
  const agendaBtn = document.querySelector('button[onclick="openAgendaModal()"]');
  if (agendaBtn) agendaBtn.textContent = `📅 ${window.t("agenda")}`;
  
  const alertsBtn = document.querySelector('button[onclick="openSubscriptionModal()"]');
  const alertsLabel = document.getElementById("subscription-label");
  if (alertsLabel) {
    alertsLabel.textContent = "ABOS";
    alertsLabel.innerHTML = "ABOS"; // Double vérification avec innerHTML
  }
  
  // ⚠️ Ne pas écraser le contenu du bouton compte - mettre à jour seulement le span account-name
  const accountNameSpan = document.getElementById("account-name");
  if (accountNameSpan) {
    accountNameSpan.textContent = window.t("account");
  }
  
  const cartBtn = document.getElementById("cart-btn");
  if (cartBtn) {
    const count = cartBtn.querySelector("#cart-count");
    cartBtn.innerHTML = `🛒 ${window.t("cart")}`;
    if (count) cartBtn.appendChild(count);
  }
  
  // 3. Champ de recherche de ville (IMPORTANT!)
  const searchInput = document.getElementById("map-search-input");
  if (searchInput) {
    searchInput.placeholder = window.t("search_city");
  }
  
  // 4. Bouton Publier
  const publishBtn = document.getElementById("map-publish-btn");
  if (publishBtn) publishBtn.textContent = window.t("publish");
  
  // 5. FILTRES - Traduire les labels de dates dans l'explorer
  setTimeout(() => {
    const explorerPanel = document.getElementById("left-panel");
    if (explorerPanel) {
      // Traduire "Filtrer par date"
      const dateFilterText = Array.from(explorerPanel.querySelectorAll('div')).find(d => 
        d.textContent.includes("Filtrer par date") || d.textContent.includes("Filter by date")
      );
      if (dateFilterText) {
        dateFilterText.textContent = `📅 ${window.t("filter_by_date")} (${window.t("cumulative") || "cumulable"})`;
      }
      
      // Traduire "Ou sélectionner une période"
      const periodText = Array.from(explorerPanel.querySelectorAll('div')).find(d => 
        d.textContent.includes("Ou sélectionner") || d.textContent.includes("Or select")
      );
      if (periodText) {
        periodText.textContent = `📆 ${window.t("select_period")}`;
      }
    }
  }, 100);
  
  // 6. Rafraîchir les marqueurs pour mettre à jour les popups
  // CRITIQUE: Ne pas appeler refreshMarkers() immédiatement car cela peut créer une boucle infinie
  // Attendre que tout soit initialisé avant de rafraîchir
  // DÉSACTIVÉ temporairement pour éviter les boucles infinies
  // setTimeout(() => {
  //   try {
  //     refreshMarkers();
  //     refreshListView();
  //   } catch (e) {
  //     // Ne pas logger pour éviter les milliers de messages
  //   }
  // }, 500);
  
  // 8. Rafraîchir les modals si ouvertes
  if (document.getElementById("publish-modal-backdrop")?.style.display === "flex") {
    const modalInner = document.getElementById("publish-modal-inner");
    if (modalInner) {
      const content = modalInner.innerHTML;
      if (content.includes("Mon Agenda") || content.includes("My agenda") || content.includes("Mi agenda")) {
        openAgendaModal();
      } else if (content.includes("Abonnements") || content.includes("Subscriptions")) {
        openSubscriptionModal();
      } else if (content.includes("Mon compte") || content.includes("My account")) {
        openAccountModal();
      }
    }
  }
  
  console.log(`✅ Traduction complète terminée en ${currentLanguage.toUpperCase()}`);
}

// Fonction pour ouvrir/fermer le menu de langue
function toggleLanguageMenu() {
  const menu = document.getElementById("language-menu");
  if (!menu) return;
  
  const isOpen = menu.style.display === "block";
  menu.style.display = isOpen ? "none" : "block";
  
  // Fermer si on clique ailleurs
  if (!isOpen) {
    setTimeout(() => {
      document.addEventListener("click", function closeMenu(e) {
        if (!menu.contains(e.target) && !e.target.closest("#language-selector")) {
          menu.style.display = "none";
          document.removeEventListener("click", closeMenu);
        }
      });
    }, 100);
  }
}

// Détecter la langue de l'utilisateur (smartphone = langue du téléphone, desktop = langue du navigateur)
function detectUserLanguage() {
  const saved = localStorage.getItem("mapEventLanguage");
  if (saved && SUPPORTED_LANGUAGES.includes(saved)) return saved;
  const nav = (typeof navigator !== 'undefined' && (navigator.language || navigator.userLanguage)) ? (navigator.language || navigator.userLanguage) : "";
  const browser = nav.split("-")[0].toLowerCase();
  if (SUPPORTED_LANGUAGES.includes(browser)) return browser;
  // Correspondances courantes (navigator peut renvoyer pt-BR, zh-CN, etc.)
  const map = { "pt": "pt", "zh": "zh", "nb": "no", "nn": "no", "he": "he", "uk": "uk", "el": "el", "sv": "sv", "da": "da", "fi": "fi", "ro": "ro", "cs": "cs", "hu": "hu", "sk": "sk", "pl": "pl", "tr": "tr", "ru": "ru", "ar": "ar", "ja": "ja", "ko": "ko", "th": "th", "vi": "vi", "id": "id", "ms": "ms", "nl": "nl", "de": "de", "it": "it", "es": "es", "fr": "fr", "en": "en", "hi": "hi", "bg": "bg", "hr": "hr", "sr": "sr", "lt": "lt", "lv": "lv", "et": "et", "sl": "sl", "ta": "ta", "bn": "bn", "ur": "ur", "fa": "fa", "mr": "mr", "sw": "sw", "am": "am", "af": "af", "ca": "ca", "pa": "pa", "tl": "tl", "my": "my", "ne": "ne", "is": "is", "sq": "sq", "mk": "mk", "bs": "bs", "gl": "gl", "cy": "cy", "ka": "ka", "hy": "hy", "az": "az", "kk": "kk", "uz": "uz", "ml": "ml", "te": "te", "gu": "gu", "kn": "kn", "si": "si", "eu": "eu", "mn": "mn", "ga": "ga", "lb": "lb", "mt": "mt", "yo": "yo", "ha": "ha", "ig": "ig", "so": "so", "rw": "rw", "mg": "mg", "wo": "wo", "st": "st", "tn": "tn", "xh": "xh", "zu": "zu", "km": "km", "lo": "lo", "sd": "sd", "ps": "ps", "ky": "ky", "tk": "tk", "tg": "tg", "br": "br", "gd": "gd", "fy": "fy", "ku": "ku", "ckb": "ckb", "kmr": "kmr", "ht": "ht", "jv": "jv", "su": "su", "ny": "ny", "om": "om", "ti": "ti", "dv": "dv", "bo": "bo", "dz": "dz", "or": "or", "as": "as" };
  return map[browser] || "en";
}

// Charger la langue sauvegardée ou détectée au démarrage (smartphone + desktop)
function initLanguage() {
  // CRITIQUE: S'assurer que window.translations est complètement initialisé AVANT updateUITranslations()
  if (typeof window === 'undefined' || !window.translations || typeof window.translations !== 'object') {
    window.translations = { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
  }
  SUPPORTED_LANGUAGES.forEach(lang => {
    if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
      window.translations[lang] = window.translations[lang] || {};
    }
  });
  
  // Priorité : 1) langue sauvegardée, 2) langue du navigateur/téléphone, 3) anglais
  currentLanguage = detectUserLanguage();
  localStorage.setItem("mapEventLanguage", currentLanguage);
  updateUITranslations();
  console.log("🌍 Langue : " + (currentLanguage === "fr" ? "français (défaut)" : currentLanguage.toUpperCase() + " (détectée ou sauvegardée)"));
}

// Exports
window.toggleLanguageMenu = toggleLanguageMenu;
window.setLanguage = setLanguage;
window.translateThisComment = translateThisComment;
window.openItemFromAgenda = openItemFromAgenda;
window.selectSuggestion = selectSuggestion;
window.highlightSuggestion = highlightSuggestion;

// Mettre à jour le badge abonnement dans la topbar
function updateSubscriptionBadge() {
  if (!isLoggedIn()) {
    const badge = document.getElementById("subscription-badge");
    if (badge) {
      const label = document.getElementById("subscription-label");
      if (label) label.textContent = "ABOS";
    }
    return;
  }
  
  const badge = document.getElementById("subscription-badge");
  const label = document.getElementById("subscription-label");
  if (!badge || !label) return;
  
  const sub = currentUser.subscription || "free";
  
  // TOUJOURS afficher "ABOS" peu importe l'abonnement - FORCER IMMÉDIATEMENT
  label.textContent = "ABOS";
  label.innerHTML = "ABOS"; // Double vérification avec innerHTML
  
  // Plans Full Premium
  if (sub === "full-premium" || sub === "full") {
    badge.style.background = "linear-gradient(135deg,rgba(255,215,0,0.3),rgba(255,215,0,0.1))";
    badge.style.borderColor = "rgba(255,215,0,0.6)";
    label.style.color = "#ffd700";
  }
  // Plans Service Ultra
  else if (sub === "service-ultra" || sub === "booking-ultra") {
    badge.style.background = "linear-gradient(135deg,rgba(167,139,250,0.3),rgba(139,92,246,0.2))";
    badge.style.borderColor = "rgba(167,139,250,0.6)";
    label.style.color = "#a78bfa";
  }
  // Plans Service Pro
  else if (sub === "service-pro" || sub === "booking-pro" || sub === "pro") {
    badge.style.background = "linear-gradient(135deg,rgba(139,92,246,0.3),rgba(59,130,246,0.2))";
    badge.style.borderColor = "rgba(139,92,246,0.6)";
    label.style.color = "#a78bfa";
  }
  // Plans Events Alertes Pro
  else if (sub === "events-alerts-pro" || sub === "events-alerts") {
    badge.style.background = "linear-gradient(135deg,rgba(59,130,246,0.3),rgba(37,99,235,0.2))";
    badge.style.borderColor = "rgba(59,130,246,0.6)";
    label.style.color = "#3b82f6";
  }
  // Plans Events Explorer
  else if (sub === "events-explorer" || sub === "explorer") {
    badge.style.background = "linear-gradient(135deg,rgba(34,197,94,0.3),rgba(16,185,129,0.2))";
    badge.style.borderColor = "rgba(34,197,94,0.6)";
    label.style.color = "#22c55e";
  }
  // Ancien premium (compatibilité)
  else if (sub === "premium") {
    badge.style.background = "linear-gradient(135deg,rgba(255,215,0,0.3),rgba(255,215,0,0.1))";
    badge.style.borderColor = "rgba(255,215,0,0.6)";
    label.style.color = "#ffd700";
  }
  // Gratuit
  else {
    badge.style.background = "linear-gradient(135deg,rgba(139,92,246,0.2),rgba(59,130,246,0.1))";
    badge.style.borderColor = "rgba(139,92,246,0.4)";
    label.style.color = "#a78bfa";
  }
}

// ============================================
// MISSION ÉCOLOGIQUE - SAUVER LA TERRE 🌍
// ============================================
function openEcoMissionModal() {
  const html = `
    <div style="padding:16px;text-align:center;">
      <div style="font-size:60px;margin-bottom:16px;">🌍</div>
      <h2 style="margin:0 0 12px;font-size:22px;background:linear-gradient(90deg,#22c55e,#10b981);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;">
        Notre Mission : Sauver la Planète
      </h2>
      
      <p style="font-size:14px;color:var(--ui-text-main);line-height:1.6;margin-bottom:20px;">
        <strong>Map Event</strong> n'est pas qu'une plateforme d'événements.<br>
        C'est un projet engagé pour l'environnement.
      </p>
      
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:16px;margin-bottom:20px;text-align:left;">
        <div style="font-size:14px;font-weight:600;color:#22c55e;margin-bottom:12px;">💚 Où vont vos contributions ?</div>
        <ul style="margin:0;padding-left:20px;font-size:13px;color:var(--ui-text-main);line-height:1.8;">
          <li><strong>🌳 Achat de terrains forestiers</strong> – Protection des écosystèmes</li>
          <li><strong>🏭 Filtres CO2 pour entreprises</strong> – Offerts aux plus gros pollueurs</li>
          <li><strong>🌊 Nettoyage des océans</strong> – Partenariats avec Ocean Cleanup</li>
          <li><strong>☀️ Énergie renouvelable</strong> – Financement de projets solaires</li>
          <li><strong>🐝 Protection de la biodiversité</strong> – Ruches urbaines & réserves</li>
          <li><strong>🎓 Éducation environnementale</strong> – Sensibilisation des jeunes</li>
        </ul>
      </div>
      
      <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-bottom:20px;">
        <div style="font-size:14px;font-weight:600;color:#3b82f6;margin-bottom:8px;">📊 Répartition de nos revenus</div>
        <div style="display:flex;justify-content:center;gap:20px;font-size:12px;color:var(--ui-text-main);">
          <div><strong style="color:#22c55e;font-size:24px;">70%</strong><br>Mission Planète</div>
          <div><strong style="color:#f59e0b;font-size:24px;">20%</strong><br>Développement</div>
          <div><strong style="color:#8b5cf6;font-size:24px;">10%</strong><br>Équipe</div>
        </div>
      </div>
      
      <div style="font-size:13px;color:var(--ui-text-muted);margin-bottom:16px;">
        Chaque paiement sur Map Event contribue directement à ces actions.<br>
        <strong>Ensemble, on peut faire la différence.</strong> 🌱
      </div>
      
      <div style="display:flex;gap:8px;margin-bottom:12px;">
        <button onclick="makeDonation(5)" style="flex:1;padding:12px;border-radius:12px;border:none;cursor:pointer;font-weight:600;background:rgba(34,197,94,0.2);color:#22c55e;font-size:14px;">
          🌱 5 CHF
        </button>
        <button onclick="makeDonation(10)" style="flex:1;padding:12px;border-radius:12px;border:none;cursor:pointer;font-weight:600;background:rgba(34,197,94,0.3);color:#22c55e;font-size:14px;">
          🌳 10 CHF
        </button>
        <button onclick="makeDonation(25)" style="flex:1;padding:12px;border-radius:12px;border:none;cursor:pointer;font-weight:600;background:rgba(34,197,94,0.4);color:#22c55e;font-size:14px;">
          🌲 25 CHF
        </button>
      </div>
      
      <button onclick="makeDonation(0)" style="width:100%;padding:14px;border-radius:999px;border:none;cursor:pointer;font-weight:700;font-size:15px;background:linear-gradient(135deg,#22c55e,#10b981);color:white;box-shadow:0 8px 24px rgba(34,197,94,0.4);">
        💚 Faire un don personnalisé
      </button>
      
      <button onclick="closePublishModal()" style="width:100%;margin-top:12px;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-muted);cursor:pointer;font-size:12px;">
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

function makeDonation(amount) {
  if (amount === 0) {
    const customAmount = prompt("Montant de votre don (CHF) :");
    if (customAmount && !isNaN(customAmount) && parseFloat(customAmount) > 0) {
      amount = parseFloat(customAmount);
    } else {
      return;
    }
  }
  
  showNotification(`🌍 Merci pour votre don de ${amount} CHF ! La Terre vous remercie 💚`, "success");
  closePublishModal();
  
  // Afficher un message de remerciement après
  setTimeout(() => {
    showNotification("🌳 Votre contribution sera utilisée pour protéger notre planète.", "info");
  }, 2000);
}

// ============================================
// SYSTÈME D'ALERTES ET D'ALARMES - LEADER MONDIAL
// ============================================

// API_BASE_URL est maintenant défini en haut du fichier

// Fonction pour charger l'utilisateur depuis /api/user/me (source de vérité)
async function loadCurrentUserFromAPI() {
  try {
    // LOG: API_BASE_URL utilisé
    console.log('[AUTH] API_BASE_URL:', window.API_BASE_URL);
    
    const accessToken = getAuthToken();
    const refreshToken = getRefreshToken();
    
    if (!accessToken) {
      console.log('[AUTH] Pas de token');
      localStorage.removeItem('currentUser');
      sessionStorage.removeItem('currentUser');
      currentUser = getDefaultUser();
      return null;
    }
    
    // LOG: Tentative /api/user/me
    console.log('[AUTH] Appel GET /api/user/me...');
    
    // Appeler /api/user/me avec le token
    const response = await fetch(`${window.API_BASE_URL}/user/me`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    // LOG: Status /api/user/me
    console.log('[AUTH] GET /api/user/me - Status:', response.status, response.statusText);
    
    if (response.ok) {
      const data = await response.json();
      const user = data.user;
      
      // IMPORTANT: Normaliser la source d'avatar avec priorité claire
      // Priorité: profile_photo_url > profilePhoto > avatarUrl > avatar > emoji
      const avatarUrl = user.profile_photo_url || user.profilePhoto || user.avatarUrl || user.avatar || null;
      
      // Mettre à jour currentUser avec les données du serveur (source de vérité)
      // Exclure agenda du spread car il sera chargé séparément par loadAgendaFromBackend()
      const { agenda: _apiAgenda, ...userWithoutAgenda } = user;
      const existingAgenda = currentUser?.agenda || [];
      
      currentUser = {
        ...userWithoutAgenda,
        isLoggedIn: true,
        accessToken: accessToken,
        refreshToken: refreshToken,
        // Normaliser avatar avec priorité
        avatarUrl: avatarUrl, // Champ unifié
        profilePhoto: avatarUrl, // Alias
        profile_photo_url: avatarUrl, // Alias
        avatar: avatarUrl || '👤', // Fallback emoji
        // Préserver l'agenda existant en attendant le chargement complet par loadAgendaFromBackend()
        agenda: (_apiAgenda && Array.isArray(_apiAgenda) && _apiAgenda.length > 0) ? _apiAgenda : existingAgenda
      };
      
      // NE PAS sauvegarder currentUser dans localStorage (trop volumineux, cause quota exceeded)
      // Les tokens sont déjà stockés séparément, le profil est chargé depuis l'API à chaque fois
      console.log('[AUTH] Utilisateur charge depuis /api/user/me:', user.email);
      console.log('[AVATAR] Avatar normalise:', avatarUrl ? avatarUrl.substring(0, 50) + '...' : 'null (emoji)');
      
      // Mettre à jour l'UI immédiatement après chargement
      if (typeof updateAccountBlockLegitimately === 'function') {
        setTimeout(() => updateAccountBlockLegitimately(), 100);
      }
      
      return currentUser;
    } else if (response.status === 401) {
      // Token expiré, tenter refresh
      console.log('[AUTH] Token expire (401), tentative refresh...');
      
      if (!refreshToken) {
        console.log('[AUTH] Pas de refresh token');
        localStorage.removeItem('currentUser');
        sessionStorage.removeItem('currentUser');
        currentUser = getDefaultUser();
        return null;
      }
      
      // LOG: Tentative /api/auth/refresh
      console.log('[AUTH] Appel POST /api/auth/refresh...');
      
      // Appeler /api/auth/refresh
      const refreshResponse = await fetch(`${window.API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refreshToken: refreshToken })
      });
      
      // LOG: Status refresh
      console.log('[AUTH] POST /api/auth/refresh - Status:', refreshResponse.status, refreshResponse.statusText);
      
      if (refreshResponse.ok) {
        const refreshData = await refreshResponse.json();
        const newAccessToken = refreshData.accessToken;
        
        // Sauvegarder le nouveau token
        localStorage.setItem('accessToken', newAccessToken);
        console.log('[AUTH] Nouveau accessToken obtenu');
        
        // Réessayer /api/user/me avec le nouveau token
        console.log('[AUTH] Retry GET /api/user/me avec nouveau token...');
        const retryResponse = await fetch(`${window.API_BASE_URL}/user/me`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${newAccessToken}`
          }
        });
        
        // LOG: Status retry /api/user/me
        console.log('[AUTH] Retry GET /api/user/me - Status:', retryResponse.status, retryResponse.statusText);
        
        if (retryResponse.ok) {
          const retryData = await retryResponse.json();
          const user = retryData.user;
          
          // IMPORTANT: Normaliser avatar avec priorité claire
          const avatarUrl = user.profile_photo_url || user.profilePhoto || user.avatarUrl || user.avatar || null;
          
          // Exclure agenda du spread car chargé séparément par loadAgendaFromBackend()
          const { agenda: _retryAgenda, ...retryUserWithoutAgenda } = user;
          const retryExistingAgenda = currentUser?.agenda || [];
          
          currentUser = {
            ...retryUserWithoutAgenda,
            isLoggedIn: true,
            accessToken: newAccessToken,
            refreshToken: refreshToken,
            avatarUrl: avatarUrl, // Champ unifié
            profilePhoto: avatarUrl, // Alias
            profile_photo_url: avatarUrl, // Alias
            avatar: avatarUrl || '👤', // Fallback emoji
            agenda: (_retryAgenda && Array.isArray(_retryAgenda) && _retryAgenda.length > 0) ? _retryAgenda : retryExistingAgenda
          };
          
          // NE PAS stocker currentUser dans localStorage (cause quota exceeded)
          console.log('[AUTH] Utilisateur charge apres refresh:', user.email);
          console.log('[AVATAR] Avatar normalise apres refresh:', avatarUrl ? avatarUrl.substring(0, 50) + '...' : 'null (emoji)');
          
          // Mettre à jour l'UI immédiatement après refresh
          if (typeof updateAccountBlockLegitimately === 'function') {
            setTimeout(() => updateAccountBlockLegitimately(), 100);
          }
          
          return currentUser;
        } else {
          console.log('[AUTH] Retry /api/user/me echoue:', retryResponse.status);
        }
      } else {
        console.log('[AUTH] Refresh echoue:', refreshResponse.status);
      }
      
      // Refresh échoué - tokens conservés
      console.log('[AUTH] Refresh echoue');
      localStorage.removeItem('currentUser');
      sessionStorage.removeItem('currentUser');
      currentUser = getDefaultUser();
      return null;
    } else {
      // Autre erreur
      console.error('[AUTH] Erreur chargement utilisateur:', response.status);
      return null;
    }
  } catch (error) {
    console.error('[AUTH] Erreur lors du chargement utilisateur:', error);
    return null;
  }
}

// --- CONFIGURATION STRIPE ---
// Note: La clé publique sera récupérée depuis le backend lors de la création de la session
let stripe = null;
let stripePublicKey = null;

// Initialiser Stripe (sera fait après récupération de la clé publique)
function initStripe(publicKey) {
  if (!publicKey) {
    console.warn('⚠️ Clé publique Stripe manquante');
    return;
  }
  
  // Charger Stripe.js à la demande si pas encore chargé
  if (typeof Stripe === 'undefined') {
    console.log('⏳ Chargement de Stripe.js à la demande...');
    if (typeof window.loadStripe === 'function') {
      window.loadStripe().then(() => {
      if (typeof Stripe !== 'undefined') {
          try {
        stripe = Stripe(publicKey);
        stripePublicKey = publicKey;
            console.log('✅ Stripe initialisé (chargé à la demande)');
          } catch (error) {
            console.error('❌ Erreur initialisation Stripe:', error);
          }
      } else {
          console.error('❌ Stripe.js toujours non disponible après chargement');
      }
      });
    } else {
      console.error('❌ loadStripe non disponible');
    }
    return;
  }
  
  try {
    stripe = Stripe(publicKey);
    stripePublicKey = publicKey;
    console.log('✅ Stripe initialisé avec succès');
  } catch (error) {
    console.error('❌ Erreur initialisation Stripe:', error);
  }
}

// Stripe.js est chargé à la demande (lazy-load) - pas de vérification au démarrage

// État des alertes
let alertsViewOpen = false;
let alertsScrollPosition = 0;
let selectedAlertId = null;
let alarmsViewOpen = false;

// Variables pour les alarmes
let currentUserAlarms = []; // [{alertId, eventId, favoriteId, favoriteName, favoriteMode, timeBefore: {value, unit}, createdAt}]
let alarmsForAgenda = []; // Même structure pour l'agenda

// ============================================
// DÉTECTION AUTOMATIQUE DES FAVORIS DANS LES ÉVÉNEMENTS
// ============================================

// Vérifier si des favoris apparaissent dans de nouveaux événements
async function checkFavoritesInNewEvents(newEvents) {
  if (!currentUser.isLoggedIn || !currentUser.favorites || currentUser.favorites.length === 0) {
    return;
  }

  const maxAlerts = getAlertLimit();
  if (maxAlerts === 0) return; // Pas d'alertes pour les utilisateurs gratuits

  const newAlerts = [];

  // Pour chaque nouvel événement
  newEvents.forEach(event => {
    if (!event || !event.title) return;

    const eventTitle = (event.title || '').toLowerCase();
    const eventDescription = (event.description || '').toLowerCase();
    const eventLocation = (event.location || event.city || '').toLowerCase();

    // Pour chaque favori de l'utilisateur
    currentUser.favorites.forEach(favorite => {
      if (!favorite || !favorite.name) return;

      const favoriteName = favorite.name.toLowerCase();
      
      // Vérifier si le nom du favori apparaît dans le titre, description ou location
      const foundInTitle = eventTitle.includes(favoriteName);
      const foundInDescription = eventDescription.includes(favoriteName);
      const foundInLocation = eventLocation.includes(favoriteName);

      if (foundInTitle || foundInDescription || foundInLocation) {
        // Vérifier si l'alerte existe déjà
        const alertExists = currentUser.alerts.some(a => 
          a.eventId === event.id.toString() && 
          a.favoriteId === favorite.id &&
          a.status !== 'deleted'
        );

        if (!alertExists) {
          // ✅ NOUVEAU : Vérifier la distance entre l'utilisateur et l'événement
          // L'alerte n'est créée que si l'événement est à moins de 75 km d'au moins une adresse de l'utilisateur
          if (!event.lat || !event.lng) {
            // Si l'événement n'a pas de coordonnées, on ne peut pas calculer la distance
            // On ne crée pas l'alerte
            return;
          }

          // Vérifier si l'utilisateur a au moins une adresse définie
          if (!currentUser.addresses || currentUser.addresses.length === 0) {
            // Si l'utilisateur n'a pas d'adresse, on ne crée pas l'alerte
            console.log('⚠️ Aucune adresse utilisateur définie - alerte non créée');
            return;
          }

          // Vérifier la distance pour chaque adresse de l'utilisateur
          let distanceToUser = null;
          let closestAddress = null;
          
          for (const address of currentUser.addresses) {
            if (address.lat && address.lng) {
              const distance = calculateDistance(
                address.lat, address.lng,
                event.lat, event.lng
              );
              
              // Si l'événement est à moins de 75 km de cette adresse
              if (distance <= 75) {
                if (!distanceToUser || distance < distanceToUser) {
                  distanceToUser = distance;
                  closestAddress = address;
                }
              }
            }
          }

          // ✅ Condition : L'alerte n'est créée que si l'événement est à moins de 75 km d'au moins une adresse
          if (distanceToUser === null || distanceToUser > 75) {
            console.log(`⚠️ Événement trop loin (${distanceToUser ? distanceToUser + ' km' : 'distance inconnue'} > 75 km) - alerte non créée`);
            return;
          }

          // Calculer la distance entre le favori et l'événement (pour affichage)
          let distanceToFavorite = null;
          if (favorite.lat && favorite.lng) {
            distanceToFavorite = calculateDistance(
              event.lat, event.lng,
              favorite.lat, favorite.lng
            );
          }

          // Vérifier la limite d'alertes pour déterminer si elle doit être floutée
          const alertLimit = getAlertLimit();
          const activeAlerts = currentUser.alerts.filter(a => a.status !== 'deleted' && !a.isBlurred);
          const isBlurred = alertLimit !== Infinity && activeAlerts.length >= alertLimit;

          const alert = {
            id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            eventId: event.id.toString(),
            favoriteId: favorite.id,
            favoriteName: favorite.name,
            favoriteMode: favorite.mode || favorite.type || 'event',
            distance: distanceToFavorite, // Distance entre favori et événement
            distanceToUser: distanceToUser, // Distance entre utilisateur et événement
            closestAddress: closestAddress ? (closestAddress.address || closestAddress.city) : null,
            status: 'new',
            isBlurred: isBlurred, // ✅ Alerte floutée si limite atteinte
            creationDate: new Date().toISOString(),
            eventTitle: event.title,
            eventDate: event.startDate || event.date
          };

          newAlerts.push(alert);
          
          // Si l'alerte est floutée, supprimer les alarmes correspondantes (elles n'existent pas encore, mais on prépare)
          // Les alarmes seront supprimées automatiquement quand elles seront créées pour une alerte floutée
        }
      }
    });
  });

  // Ajouter les nouvelles alertes
  if (newAlerts.length > 0) {
    // Sauvegarder dans le backend
    for (const alert of newAlerts) {
      try {
        const response = await fetch(`${window.API_BASE_URL}/user/alerts`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId: currentUser.id.toString(),
            alert: alert
          })
        });

        if (response.ok) {
          currentUser.alerts.push(alert);
        }
      } catch (error) {
        console.error('Erreur création alerte:', error);
      }
    }

    // Afficher la fenêtre popup au login si l'utilisateur vient de se connecter
    if (currentUser && currentUser.isLoggedIn) {
      showAlertsLoginPopup(newAlerts);
    }
  }
}

// Calculer la distance entre deux points (formule de Haversine)
// Fonction calculateDistance déjà définie plus haut (ligne 2753)
// Cette fonction utilise la signature: calculateDistance(lat1, lng1, lat2, lng2)

// ============================================
// FENÊTRE POPUP D'ALERTES AU LOGIN
// ============================================

function showAlertsLoginPopup(newAlerts) {
  if (!newAlerts || newAlerts.length === 0) return;

  const html = `
    <div style="position:relative;width:100%;max-width:500px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;border:2px solid #3b82f6;box-shadow:0 20px 60px rgba(59,130,246,0.3);overflow:hidden;">
      <div style="background:linear-gradient(135deg,#3b82f6,#2563eb);padding:20px;text-align:center;">
        <div style="font-size:32px;margin-bottom:8px;">🔔</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Nouvelles Alertes</h2>
        <p style="margin:8px 0 0;font-size:14px;color:rgba(255,255,255,0.9);">Vos favoris apparaissent dans de nouveaux événements !</p>
      </div>
      
      <div style="padding:20px;max-height:400px;overflow-y:auto;">
        ${newAlerts.map(alert => `
          <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-bottom:12px;">
            <div style="display:flex;align-items:start;gap:12px;">
              <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#2563eb);display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">
                ${getFavoriteEmoji(alert.favoriteMode)}
              </div>
              <div style="flex:1;">
                <div style="font-weight:700;font-size:16px;margin-bottom:4px;color:#fff;">
                  ${escapeHtml(alert.favoriteName)}
                </div>
                <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-bottom:6px;">
                  apparaît dans l'événement
                </div>
                <div style="font-weight:600;font-size:14px;color:#00ffc3;margin-bottom:4px;">
                  ${escapeHtml(alert.eventTitle)}
                </div>
                ${alert.distanceToUser ? `<div style="font-size:12px;color:rgba(255,255,255,0.6);">📍 À ${alert.distanceToUser} km de chez vous</div>` : alert.distance ? `<div style="font-size:12px;color:rgba(255,255,255,0.6);">📍 À ${alert.distance} km</div>` : ''}
              </div>
            </div>
          </div>
        `).join('')}
        
        <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-top:16px;text-align:center;">
          <div style="font-size:14px;color:rgba(255,255,255,0.8);">
            💡 Toutes vos alertes sont disponibles dans le bloc <strong style="color:#3b82f6;">Alertes</strong>
          </div>
        </div>
      </div>
      
      <div style="padding:20px;border-top:1px solid rgba(255,255,255,0.1);display:flex;gap:12px;">
        <button onclick="closeAlertsLoginPopup()" style="flex:1;padding:14px;border-radius:12px;border:none;background:rgba(255,255,255,0.1);color:#fff;font-weight:600;cursor:pointer;transition:all 0.2s;">
          Fermer
        </button>
        <button onclick="closeAlertsLoginPopupAndOpenAlerts()" style="flex:1;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;transition:all 0.2s;">
          OK, j'ai compris
        </button>
      </div>
    </div>
  `;

  // Créer ou réutiliser le backdrop
  let backdrop = document.getElementById("alerts-login-popup-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "alerts-login-popup-backdrop";
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.95);display:flex;align-items:center;justify-content:center;z-index:2000;backdrop-filter:blur(10px);";
    backdrop.onclick = (e) => {
      if (e.target === backdrop) closeAlertsLoginPopup();
    };
    document.body.appendChild(backdrop);
  }
  
  backdrop.innerHTML = html;
  backdrop.style.display = "flex";
}

function closeAlertsLoginPopup() {
  const backdrop = document.getElementById("alerts-login-popup-backdrop");
  if (backdrop) {
    backdrop.style.display = "none";
  }
}

function closeAlertsLoginPopupAndOpenAlerts() {
  closeAlertsLoginPopup();
  setTimeout(() => {
    openAlertsView();
  }, 300);
}

// Afficher les notifications de changement de statut pour les événements où l'utilisateur a participé
function showStatusChangeNotifications() {
  if (!currentUser.isLoggedIn || !currentUser.pendingStatusNotifications || currentUser.pendingStatusNotifications.length === 0) {
    return;
  }
  
  // Filtrer les notifications qui concernent des événements toujours dans participating
  const validNotifications = currentUser.pendingStatusNotifications.filter(notif => {
    const key = `event:${notif.eventId}`;
    return currentUser.participating.includes(key);
  });
  
  if (validNotifications.length === 0) {
    // Nettoyer les notifications obsolètes
    currentUser.pendingStatusNotifications = [];
    saveUser();
    return;
  }
  
  // Afficher la première notification
  const notification = validNotifications[0];
  const event = eventsData.find(e => e.id === notification.eventId);
  if (!event) {
    // Supprimer la notification si l'événement n'existe plus
    currentUser.pendingStatusNotifications = currentUser.pendingStatusNotifications.filter(n => n.eventId !== notification.eventId);
    saveUser();
    return;
  }
  
  // Créer la fenêtre de notification
  let backdrop = document.getElementById("status-change-notification-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "status-change-notification-backdrop";
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.75);display:flex;align-items:center;justify-content:center;z-index:99999;backdrop-filter:blur(2px);padding-top:40px;padding-bottom:40px;box-sizing:border-box;";
    document.body.appendChild(backdrop);
  }
  
  const statusEmoji = notification.status === 'REPORTÉ' || notification.status === 'REPORTE' ? '📅' :
                     notification.status === 'ANNULE' || notification.status === 'ANNULÉ' ? '❌' :
                     notification.status === 'COMPLET' || notification.status === 'SOLDOUT' ? '🔒' : '⚠️';
  
  const statusColor = notification.status === 'REPORTÉ' || notification.status === 'REPORTE' ? '#3b82f6' :
                      notification.status === 'ANNULE' || notification.status === 'ANNULÉ' ? '#ef4444' :
                      notification.status === 'COMPLET' || notification.status === 'SOLDOUT' ? '#f59e0b' : '#ef4444';
  
  backdrop.innerHTML = `
    <div style="position:relative;width:100%;max-width:500px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;border:2px solid ${statusColor};box-shadow:0 20px 60px rgba(0,0,0,0.5);overflow:hidden;">
      <button onclick="closeStatusChangeNotification(${notification.eventId})" style="position:absolute;top:12px;right:12px;width:36px;height:36px;border-radius:50%;border:none;background:rgba(255,255,255,0.1);color:#fff;cursor:pointer;font-size:20px;z-index:1001;display:flex;align-items:center;justify-content:center;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.8)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">✕</button>
      
      <div style="background:linear-gradient(135deg,${statusColor},${statusColor}dd);padding:20px;text-align:center;">
        <div style="font-size:48px;margin-bottom:8px;">${statusEmoji}</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Changement d'événement</h2>
        <p style="margin:8px 0 0;font-size:14px;color:rgba(255,255,255,0.9);">L'événement auquel vous participez a changé</p>
      </div>
      
      <div style="padding:24px;">
        <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:16px;margin-bottom:20px;">
          <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:8px;">${escapeHtml(event.title)}</div>
          <div style="font-size:14px;color:var(--ui-text-muted);margin-bottom:12px;">${escapeHtml(event.address || '')}</div>
          <div style="padding:8px 12px;background:rgba(239,68,68,0.2);border-radius:8px;display:inline-block;">
            <span style="font-size:13px;font-weight:600;color:#ef4444;">⚠️ Événement ${notification.statusText}</span>
          </div>
        </div>
        
        <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-bottom:20px;">
          <div style="font-size:13px;font-weight:600;color:#3b82f6;margin-bottom:8px;">💡 Que souhaitez-vous faire ?</div>
          <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.6;">
            Vous pouvez ajouter cette annonce dans le bloc <strong style="color:#3b82f6;">ABOS</strong> pour recevoir des alertes sur les changements futurs.
          </div>
        </div>
        
        <div style="display:flex;gap:10px;">
          <button onclick="closeStatusChangeNotification(${notification.eventId})" style="flex:1;padding:12px;border-radius:12px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-weight:600;cursor:pointer;transition:all 0.2s;">
            Fermer
          </button>
          <button onclick="addEventToAlertsFromNotification(${notification.eventId})" style="flex:1;padding:12px;border-radius:12px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;transition:all 0.2s;">
            Ajouter aux alertes
          </button>
        </div>
      </div>
    </div>
  `;
  
  backdrop.style.display = "flex";
}

function closeStatusChangeNotification(eventId) {
  // Supprimer la notification de la liste
  currentUser.pendingStatusNotifications = currentUser.pendingStatusNotifications.filter(n => n.eventId !== eventId);
  saveUser();
  
  // Fermer la fenêtre
  const backdrop = document.getElementById("status-change-notification-backdrop");
  if (backdrop) {
    backdrop.style.display = "none";
  }
  
  // Afficher la notification suivante s'il y en a
  setTimeout(() => {
    showStatusChangeNotifications();
  }, 300);
}

// Ajouter une alerte pour un événement depuis l'agenda
function addEventAlert(eventId) {
  const event = eventsData.find(e => e.id === eventId);
  if (!event) {
    showNotification("⚠️ Événement introuvable", "warning");
    return;
  }
  
  if (!currentUser || !currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour ajouter des alertes", "warning");
    openLoginModal();
    return;
  }
  
  // Vérifier la limite d'alertes
  const maxAlerts = getAlertLimit();
  if (maxAlerts === 0) {
    showNotification("⚠️ Les alertes nécessitent un abonnement Events Explorer ou supérieur", "warning");
    openSubscriptionModal();
    return;
  }
  
  if (currentUser.alerts && currentUser.alerts.length >= maxAlerts) {
    showNotification(`⚠️ Limite atteinte (${maxAlerts} alertes) ! Passez à Events Alertes Pro pour des alertes illimitées.`, "warning");
    openSubscriptionModal();
    return;
  }
  
  // Vérifier si l'alerte existe déjà
  const existingAlert = currentUser.alerts?.find(a => a.eventId === eventId && a.status !== 'deleted');
  if (existingAlert) {
    showNotification("ℹ️ Cet événement est déjà dans vos alertes", "info");
    return;
  }
  
  // Créer l'alerte
  if (!currentUser.alerts) currentUser.alerts = [];
  currentUser.alerts.push({
    id: Date.now(),
    eventId: eventId,
    type: 'event',
    category: event.category,
    city: event.city,
    createdAt: new Date().toISOString(),
    status: 'active'
  });
  
  saveUser();
  showNotification(`✅ Alerte ajoutée pour "${event.title}"`, "success");
  
  // Rafraîchir la vue agenda si elle est ouverte
  if (agendaMiniWindowOpen) {
    showAgendaMiniWindow();
  }
}

function addEventToAlertsFromNotification(eventId) {
  const event = eventsData.find(e => e.id === eventId);
  if (!event) return;
  
  // Utiliser la fonction addEventAlert
  addEventAlert(eventId);
  closeStatusChangeNotification(eventId);
  setTimeout(() => {
    openSubscriptionModal();
    showNotification("💡 Vous pouvez créer une alerte dans le bloc ABOS pour cet événement", "info");
  }, 300);
}

function getFavoriteEmoji(mode) {
  const emojis = {
    'event': '🎉',
    'booking': '🎤',
    'service': '⚙️',
    'avatar': '👤'
  };
  return emojis[mode] || '⭐';
}

// ============================================
// ============================================
// SYSTÈME D'ALERTES DE PROXIMITÉ (rayon 70km)
// ============================================

let proximityAlertsViewOpen = false;

// Vérifier les alertes de proximité basées sur les likes et les adresses
function checkProximityAlerts() {
  if (!currentUser.isLoggedIn || !currentUser.addresses || currentUser.addresses.length === 0) {
    currentUser.proximityAlerts = [];
    updateProximityAlertsBadge();
    return;
  }
  
  const alerts = [];
  const likedItems = currentUser.likes || [];
  
  // Parcourir tous les items likés
  likedItems.forEach(likeKey => {
    const [type, idStr] = likeKey.split(':');
    const id = parseInt(idStr);
    
    let item = null;
    if (type === 'event') {
      item = eventsData.find(e => e.id === id);
    } else if (type === 'booking') {
      item = bookingsData.find(b => b.id === id);
    } else if (type === 'service') {
      item = servicesData.find(s => s.id === id);
    }
    
    if (!item) return;
    
    // CAS 1: Item liké directement (event, booking, service)
    if (item.lat && item.lng) {
      currentUser.addresses.forEach((address, addrIndex) => {
        if (!address.lat || !address.lng) return;
        
        const distance = calculateDistance(address.lat, address.lng, item.lat, item.lng);
        
        if (distance <= 70) {
          const existingAlert = alerts.find(a => 
            a.itemId === id && a.itemType === type && a.addressIndex === addrIndex && a.alertType === 'direct'
          );
          
          if (!existingAlert) {
            const typeEmoji = type === 'event' ? '🎉' : type === 'booking' ? '🎤' : '🔧';
            const typeName = type === 'event' ? 'Événement' : type === 'booking' ? 'Booking' : 'Service';
            
            alerts.push({
              id: `proximity-${type}-${id}-${addrIndex}-direct-${Date.now()}`,
              itemId: id,
              itemType: type,
              itemTitle: item.title || item.name || 'Sans titre',
              itemCity: item.city || '',
              itemLat: item.lat,
              itemLng: item.lng,
              addressIndex: addrIndex,
              address: address.address || address.city || 'Adresse inconnue',
              distance: Math.round(distance * 10) / 10,
              emoji: typeEmoji,
              typeName: typeName,
              alertType: 'direct', // Item liké directement
              timestamp: new Date().toISOString()
            });
          }
        }
      });
    }
    
    // CAS 2: Booking (artiste) liké apparaît dans un événement
    if (type === 'booking' && item.lat && item.lng) {
      eventsData.forEach(event => {
        if (!event.lat || !event.lng) return;
        
        // Vérifier si l'événement référence ce booking (par ID, nom, ou organisateur)
        const eventReferencesBooking = 
          event.bookingIds?.includes(id) ||
          event.bookings?.some(b => b.id === id || b.name === item.name) ||
          event.organizerId === id ||
          (event.organizer && event.organizer.toLowerCase().includes((item.name || '').toLowerCase()));
        
        if (eventReferencesBooking) {
          currentUser.addresses.forEach((address, addrIndex) => {
            if (!address.lat || !address.lng) return;
            
            const distance = calculateDistance(address.lat, address.lng, event.lat, event.lng);
            
            if (distance <= 70) {
              const existingAlert = alerts.find(a => 
                a.eventId === event.id && a.likedItemId === id && a.likedItemType === 'booking' && a.addressIndex === addrIndex && a.alertType === 'artist_in_event'
              );
              
              if (!existingAlert) {
                alerts.push({
                  id: `proximity-event-${event.id}-booking-${id}-${addrIndex}-${Date.now()}`,
                  eventId: event.id,
                  eventTitle: event.title || 'Sans titre',
                  eventCity: event.city || '',
                  eventLat: event.lat,
                  eventLng: event.lng,
                  likedItemId: id,
                  likedItemType: 'booking',
                  likedItemTitle: item.name || 'Artiste',
                  addressIndex: addrIndex,
                  address: address.address || address.city || 'Adresse inconnue',
                  distance: Math.round(distance * 10) / 10,
                  emoji: '🎤',
                  typeName: 'Artiste dans événement',
                  alertType: 'artist_in_event',
                  message: `${item.name || 'Artiste'} se produit dans "${event.title || 'Événement'}"`,
                  timestamp: new Date().toISOString()
                });
              }
            }
          });
        }
      });
    }
    
    // CAS 3: Service liké apparaît dans un événement
    if (type === 'service' && item.lat && item.lng) {
      eventsData.forEach(event => {
        if (!event.lat || !event.lng) return;
        
        const eventReferencesService = 
          event.serviceIds?.includes(id) ||
          event.services?.some(s => s.id === id || s.name === item.name) ||
          (event.description && event.description.toLowerCase().includes((item.name || '').toLowerCase()));
        
        if (eventReferencesService) {
          currentUser.addresses.forEach((address, addrIndex) => {
            if (!address.lat || !address.lng) return;
            
            const distance = calculateDistance(address.lat, address.lng, event.lat, event.lng);
            
            if (distance <= 70) {
              const existingAlert = alerts.find(a => 
                a.eventId === event.id && a.likedItemId === id && a.likedItemType === 'service' && a.addressIndex === addrIndex && a.alertType === 'service_in_event'
              );
              
              if (!existingAlert) {
                alerts.push({
                  id: `proximity-event-${event.id}-service-${id}-${addrIndex}-${Date.now()}`,
                  eventId: event.id,
                  eventTitle: event.title || 'Sans titre',
                  eventCity: event.city || '',
                  eventLat: event.lat,
                  eventLng: event.lng,
                  likedItemId: id,
                  likedItemType: 'service',
                  likedItemTitle: item.name || 'Service',
                  addressIndex: addrIndex,
                  address: address.address || address.city || 'Adresse inconnue',
                  distance: Math.round(distance * 10) / 10,
                  emoji: '🔧',
                  typeName: 'Service dans événement',
                  alertType: 'service_in_event',
                  message: `${item.name || 'Service'} est utilisé dans "${event.title || 'Événement'}"`,
                  timestamp: new Date().toISOString()
                });
              }
            }
          });
        }
      });
    }
  });
  
  // Trier par distance (plus proche en premier)
  alerts.sort((a, b) => a.distance - b.distance);
  
  currentUser.proximityAlerts = alerts;
  updateProximityAlertsBadge();
  saveUser();
}

// Mettre à jour le badge de notifications
function updateProximityAlertsBadge() {
  const alertsCount = currentUser.proximityAlerts?.length || 0;
  const badge = document.getElementById("alerts-count");
  if (badge) {
    if (alertsCount > 0) {
      badge.textContent = alertsCount > 99 ? '99+' : alertsCount;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }
}

// Fonction pour ouvrir les alertes sociales (alertes de proximité)
function openSocialAlertsModal() {
  if (!currentUser || !currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour voir vos alertes", "warning");
    openLoginModal();
    return;
  }
  // Ouvrir la vue des alertes de proximité (qui inclut les alertes sociales)
  openProximityAlertsView();
}
window.openSocialAlertsModal = openSocialAlertsModal;

// Ouvrir la vue des alertes de proximité
function openProximityAlertsView() {
  proximityAlertsViewOpen = true;
  refreshProximityAlertsView();
  
  // Si pas d'alertes, expliquer comment ça marche
  if (!currentUser || !currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour recevoir des alertes", "warning");
    openLoginModal();
    proximityAlertsViewOpen = false;
    return;
  }
}

// Fermer la vue des alertes de proximité
function closeProximityAlertsView() {
  proximityAlertsViewOpen = false;
  const alertsView = document.getElementById("proximity-alerts-view");
  if (alertsView) {
    alertsView.style.display = "none";
  }
}

// Rafraîchir la vue des alertes de proximité
function refreshProximityAlertsView() {
  let alertsView = document.getElementById("proximity-alerts-view");
  if (!alertsView) {
    alertsView = document.createElement("div");
    alertsView.id = "proximity-alerts-view";
    alertsView.style.cssText = "position:fixed;inset:0;z-index:1500;display:none;background:rgba(0,0,0,0.8);backdrop-filter:blur(4px);";
    document.body.appendChild(alertsView);
  }
  
  if (!proximityAlertsViewOpen) {
    alertsView.style.display = "none";
    return;
  }
  
  const alerts = currentUser.proximityAlerts || [];
  
  alertsView.innerHTML = `
    <div style="position:relative;width:100%;max-width:800px;height:100%;background:var(--ui-card-bg);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;margin:20px auto;">
      <!-- Header -->
      <div style="padding:20px;border-bottom:1px solid var(--ui-card-border);background:linear-gradient(135deg,#0f172a,#1e293b);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <div>
            <h2 style="margin:0;font-size:24px;font-weight:700;color:#fff;">🔔 Alertes de proximité</h2>
            <p style="margin:4px 0 0;font-size:13px;color:rgba(255,255,255,0.7);">${alerts.length} alerte${alerts.length > 1 ? 's' : ''} dans un rayon de 70 km</p>
          </div>
          <button onclick="closeProximityAlertsView()" style="width:40px;height:40px;border-radius:50%;border:none;background:rgba(255,255,255,0.1);color:#fff;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center;">✕</button>
        </div>
        
        <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:10px;padding:12px;">
          <div style="font-size:12px;color:#3b82f6;line-height:1.6;">
            💡 Vous recevez des alertes quand un <strong>booking, service, organisateur ou événement</strong> que vous avez <strong>liké</strong> se trouve à moins de <strong>70 km</strong> de l'une de vos adresses.
          </div>
        </div>
      </div>
      
      <!-- Liste des alertes -->
      <div style="flex:1;overflow-y:auto;padding:20px;">
        ${alerts.length === 0 ? `
          <div style="text-align:center;padding:40px 20px;color:var(--ui-text-muted);">
            <div style="font-size:64px;margin-bottom:16px;">🔔</div>
            <h3 style="font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;">Comment fonctionnent les alertes ?</h3>
            <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin:20px 0;text-align:left;">
              <p style="font-size:14px;color:#fff;margin:0 0 12px 0;line-height:1.6;">
                <strong style="color:#3b82f6;">1. Ajoutez des favoris</strong><br>
                Likez des événements, bookings, services ou organisateurs qui vous intéressent.
              </p>
              <p style="font-size:14px;color:#fff;margin:0 0 12px 0;line-height:1.6;">
                <strong style="color:#3b82f6;">2. Configurez vos adresses</strong><br>
                Ajoutez jusqu'à 2 adresses dans votre profil pour définir votre zone de proximité.
              </p>
              <p style="font-size:14px;color:#fff;margin:0;line-height:1.6;">
                <strong style="color:#3b82f6;">3. Recevez des alertes</strong><br>
                Quand un favori se trouve à moins de 70 km d'une de vos adresses, vous recevez une alerte ici !
              </p>
            </div>
            <p style="font-size:13px;margin:16px 0 0;color:var(--ui-text-muted);">Les alertes apparaîtront ici quand vos favoris seront à proximité</p>
          </div>
        ` : `
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;">
            ${alerts.map(alert => `
              <div onclick="openItemFromProximityAlert('${alert.itemType}', ${alert.itemId})" style="background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);border-radius:12px;padding:16px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.borderColor='#3b82f6';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='var(--ui-card-border)';this.style.transform='translateY(0)'">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                  <span style="font-size:24px;">${alert.emoji}</span>
                  <div style="flex:1;">
                    <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:4px;">${escapeHtml(alert.itemTitle)}</div>
                    <div style="font-size:12px;color:var(--ui-text-muted);">${alert.typeName}</div>
                  </div>
                </div>
                <div style="background:rgba(59,130,246,0.1);border-radius:8px;padding:8px;margin-bottom:8px;">
                  <div style="font-size:12px;color:#3b82f6;font-weight:600;">📍 À ${alert.distance} km</div>
                  <div style="font-size:11px;color:var(--ui-text-muted);margin-top:4px;">de ${escapeHtml(alert.address)}</div>
                </div>
                <div style="font-size:11px;color:var(--ui-text-muted);">
                  📍 ${escapeHtml(alert.itemCity)}
                </div>
                <button onclick="event.stopPropagation();removeProximityAlert('${alert.id}')" style="margin-top:12px;width:100%;padding:8px;border-radius:8px;border:1px solid rgba(239,68,68,0.5);background:rgba(239,68,68,0.1);color:#ef4444;cursor:pointer;font-size:12px;font-weight:600;">
                  ✕ Marquer comme lue
                </button>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    </div>
  `;
  
  alertsView.style.display = "flex";
}

// Ouvrir un item depuis une alerte de proximité
function openItemFromProximityAlert(type, id) {
  closeProximityAlertsView();
  setTimeout(() => {
    openPopupFromList(type, id);
  }, 300);
}

// Supprimer une alerte de proximité
function removeProximityAlert(alertId) {
  currentUser.proximityAlerts = currentUser.proximityAlerts.filter(a => a.id !== alertId);
  saveUser();
  updateProximityAlertsBadge();
  refreshProximityAlertsView();
}

// Exposer les fonctions d'alertes de proximité globalement
window.openProximityAlertsView = openProximityAlertsView;
window.closeProximityAlertsView = closeProximityAlertsView;
window.removeProximityAlert = removeProximityAlert;
window.openItemFromProximityAlert = openItemFromProximityAlert;

// BLOC ALERTES - INTERFACE SIMILAIRE À EVENT LIST
// ============================================

function openAlertsView() {
  alertsViewOpen = true;
  refreshAlertsView();
}

function closeAlertsView() {
  alertsViewOpen = false;
  const alertsView = document.getElementById("alerts-view");
  if (alertsView) {
    alertsView.style.display = "none";
  }
}

function refreshAlertsView() {
  const alertsView = document.getElementById("alerts-view");
  if (!alertsView) {
    // Créer le bloc Alertes s'il n'existe pas
    createAlertsViewElement();
    return;
  }

  if (!alertsViewOpen) {
    alertsView.style.display = "none";
    return;
  }

  // Filtrer les alertes actives (non supprimées)
  const activeAlerts = currentUser.alerts.filter(a => a.status !== 'deleted');
  const visibleAlerts = activeAlerts.filter(a => !a.isBlurred);
  const blurredAlerts = activeAlerts.filter(a => a.isBlurred);
  const alertLimit = getAlertLimit();
  
  // Trier par date de création (plus récentes en premier)
  activeAlerts.sort((a, b) => new Date(b.creationDate) - new Date(a.creationDate));
  
  // Afficher un message si limite atteinte
  const limitMessage = alertLimit !== Infinity && visibleAlerts.length >= alertLimit
    ? `<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:12px;margin-bottom:16px;text-align:center;">
         <div style="font-weight:700;font-size:14px;color:#ef4444;margin-bottom:4px;">⚠️ Limite atteinte (${visibleAlerts.length}/${alertLimit})</div>
         <div style="font-size:12px;color:rgba(255,255,255,0.7);">Les nouvelles alertes seront floutées. Effacez une alerte pour en afficher une nouvelle.</div>
       </div>`
    : '';

  alertsView.style.display = "block";
  alertsView.innerHTML = `
    <div style="position:relative;width:100%;height:100%;background:var(--ui-card-bg);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;">
      <!-- Header -->
      <div style="padding:20px;border-bottom:1px solid var(--ui-card-border);background:linear-gradient(135deg,#0f172a,#1e293b);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <div>
            <h2 style="margin:0;font-size:24px;font-weight:700;color:#fff;">🔔 Mes Alertes</h2>
            <p style="margin:4px 0 0;font-size:13px;color:rgba(255,255,255,0.7);">${visibleAlerts.length} visible${visibleAlerts.length > 1 ? 's' : ''}${blurredAlerts.length > 0 ? ` • ${blurredAlerts.length} floutée${blurredAlerts.length > 1 ? 's' : ''}` : ''}</p>
          </div>
          <button onclick="closeAlertsView()" style="width:40px;height:40px;border-radius:50%;border:none;background:rgba(255,255,255,0.1);color:#fff;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center;">✕</button>
        </div>
        
        <!-- Bouton Ajouter Alarme -->
        <button onclick="openAddAlarmModal('alerts')" style="width:100%;padding:12px;border-radius:12px;border:2px solid #3b82f6;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;font-size:14px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:12px;">
          <span>⏰</span>
          <span>Ajouter alarme</span>
        </button>
        
        ${limitMessage}
      </div>
      
      <!-- Info alertes gratuites -->
      <div style="margin:12px 20px 0;padding:12px 16px;background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(34,197,94,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:10px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:20px;">🆓</span>
          <div>
            <div style="font-size:13px;font-weight:600;color:#00ffc3;">Alertes de statut : GRATUITES & ILLIMITÉES</div>
            <div style="font-size:11px;color:var(--ui-text-muted);">Annulation, complet, reporté... Vous serez toujours informé gratuitement pour vos événements en agenda.</div>
          </div>
        </div>
      </div>
      
      <!-- Liste des alertes -->
      <div id="alerts-list-container" style="flex:1;overflow-y:auto;padding:20px;">
        ${activeAlerts.length === 0 ? `
          <div style="text-align:center;padding:40px 20px;color:var(--ui-text-muted);">
            <div style="font-size:64px;margin-bottom:16px;">🔔</div>
            <p style="font-size:16px;margin:0;">Les alertes arriveront ici</p>
            <p style="font-size:13px;margin:8px 0 0;color:var(--ui-text-muted);">selon vos likes et votre agenda</p>
            <p style="font-size:12px;margin:16px 0 0;padding:10px;background:rgba(0,255,195,0.1);border-radius:8px;color:#00ffc3;">
              💚 Si un event de votre agenda est annulé, complet ou reporté,<br>vous recevrez une alerte <strong>gratuite et illimitée</strong> !
            </p>
          </div>
        ` : `
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;">
            ${activeAlerts.map((alert, index) => buildAlertCard(alert, index)).join('')}
          </div>
        `}
      </div>
    </div>
  `;

  // Restaurer la position de scroll
  const container = document.getElementById("alerts-list-container");
  if (container && alertsScrollPosition > 0) {
    container.scrollTop = alertsScrollPosition;
  }

  // Restaurer la sélection
  if (selectedAlertId) {
    const selectedCard = alertsView.querySelector(`[data-alert-id="${selectedAlertId}"]`);
    if (selectedCard) {
      selectedCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
}

function createAlertsViewElement() {
  let alertsView = document.getElementById("alerts-view");
  if (!alertsView) {
    alertsView = document.createElement("div");
    alertsView.id = "alerts-view";
    alertsView.style.cssText = "position:fixed;inset:0;z-index:1500;display:none;";
    document.body.appendChild(alertsView);
  }
  refreshAlertsView();
}

function buildAlertCard(alert, index) {
  const event = eventsData.find(e => e.id.toString() === alert.eventId);
  const isNew = alert.status === 'new';
  const isBlurred = alert.isBlurred || false;
  const hasAlarm = currentUserAlarms.some(a => a.alertId === alert.id && !isBlurred);
  const alertLimit = getAlertLimit();
  const activeAlerts = currentUser.alerts.filter(a => a.status !== 'deleted' && !a.isBlurred);
  const canDelete = isBlurred || (alertLimit !== Infinity && activeAlerts.length > alertLimit);
  
  return `
    <div data-alert-id="${alert.id}" class="alert-card" style="
      border:2px solid ${isBlurred ? '#ef4444' : isNew ? '#3b82f6' : 'var(--ui-card-border)'};
      border-radius:16px;
      background:${isBlurred ? 'rgba(239,68,68,0.1)' : isNew ? 'rgba(59,130,246,0.1)' : 'var(--ui-card-bg)'};
      overflow:hidden;
      cursor:${isBlurred ? 'default' : 'pointer'};
      transition:all 0.2s ease;
      box-shadow:0 4px 20px rgba(0,0,0,0.2);
      position:relative;
      filter:${isBlurred ? 'blur(3px)' : 'none'};
      opacity:${isBlurred ? '0.6' : '1'};
    " ${!isBlurred ? `onclick="openEventFromAlert('${alert.eventId}', '${alert.id}')"` : ''}>
      ${isNew && !isBlurred ? '<div style="position:absolute;top:8px;right:8px;width:12px;height:12px;border-radius:50%;background:#3b82f6;box-shadow:0 0 8px rgba(59,130,246,0.8);"></div>' : ''}
      ${isBlurred ? '<div style="position:absolute;top:8px;right:8px;width:32px;height:32px;border-radius:50%;background:rgba(239,68,68,0.9);display:flex;align-items:center;justify-content:center;font-size:16px;color:#fff;box-shadow:0 2px 8px rgba(239,68,68,0.4);">🔒</div>' : ''}
      ${hasAlarm && !isBlurred ? '<div style="position:absolute;top:8px;left:8px;width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#f59e0b,#d97706);display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 2px 8px rgba(245,158,11,0.4);">⏰</div>' : ''}
      
      <div style="padding:16px;position:relative;">
        ${isBlurred ? `
          <div style="position:absolute;inset:0;background:rgba(0,0,0,0.3);border-radius:12px;display:flex;align-items:center;justify-content:center;z-index:10;">
            <div style="text-align:center;padding:20px;">
              <div style="font-size:32px;margin-bottom:8px;">🔒</div>
              <div style="font-weight:700;font-size:14px;color:#fff;margin-bottom:4px;">Alerte floutée</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.8);">Limite atteinte (${activeAlerts.length}/${alertLimit})</div>
              <div style="font-size:11px;color:rgba(255,255,255,0.6);margin-top:8px;">Effacez une alerte pour afficher celle-ci</div>
            </div>
          </div>
        ` : ''}
        
        <div style="display:flex;align-items:start;gap:12px;margin-bottom:12px;">
          <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#3b82f6,#2563eb);display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">
            ${getFavoriteEmoji(alert.favoriteMode)}
          </div>
          <div style="flex:1;">
            <div style="font-weight:700;font-size:15px;margin-bottom:4px;color:#fff;">
              ${escapeHtml(alert.favoriteName)}
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,0.6);">
              ${alert.favoriteMode === 'event' ? 'Événement' : alert.favoriteMode === 'booking' ? 'Booking' : alert.favoriteMode === 'service' ? 'Service' : 'Avatar'}
            </div>
          </div>
          ${canDelete ? `
            <button onclick="event.stopPropagation();deleteAlertWithWarning('${alert.id}')" style="width:32px;height:32px;border-radius:50%;border:none;background:rgba(239,68,68,0.2);color:#ef4444;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;flex-shrink:0;" title="Supprimer l'alerte">
              🗑️
            </button>
          ` : ''}
        </div>
        
        <div style="background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:8px;padding:12px;margin-bottom:12px;">
          <div style="font-size:11px;color:rgba(0,255,195,0.8);margin-bottom:4px;text-transform:uppercase;font-weight:600;">Apparaît dans</div>
          <div style="font-weight:600;font-size:14px;color:#00ffc3;margin-bottom:4px;">
            ${escapeHtml(alert.eventTitle || 'Événement')}
          </div>
          ${alert.eventDate ? `<div style="font-size:12px;color:rgba(0,255,195,0.7);">📅 ${formatEventDateRange(alert.eventDate, alert.eventDate)}</div>` : ''}
        </div>
        
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--ui-text-muted);">
          ${alert.distanceToUser ? `<span>📍 ${alert.distanceToUser} km de chez vous</span>` : alert.distance ? `<span>📍 ${alert.distance} km</span>` : '<span></span>'}
          <span>${new Date(alert.creationDate).toLocaleDateString('fr-CH', {day:'2-digit', month:'2-digit'})}</span>
        </div>
      </div>
    </div>
  `;
}

function openEventFromAlert(eventId, alertId) {
  selectedAlertId = alertId;
  
  // Sauvegarder la position de scroll
  const container = document.getElementById("alerts-list-container");
  if (container) {
    alertsScrollPosition = container.scrollTop;
  }
  
  // Trouver l'événement
  const event = eventsData.find(e => e.id.toString() === eventId);
  if (!event) {
    showNotification("⚠️ Événement introuvable", "error");
    return;
  }
  
  // Marquer l'alerte comme vue
  markAlertAsSeen(alertId);
  
  // Ouvrir la popup de l'événement
  openPopupFromList('event', parseInt(eventId));
  
  // Quand on ferme la popup, revenir aux alertes
  setTimeout(() => {
    const backdrop = document.getElementById("popup-modal-backdrop");
    if (backdrop) {
      const originalClose = backdrop.onclick;
      backdrop.onclick = (e) => {
        if (e.target === backdrop) {
          closePopupModal();
          setTimeout(() => {
            refreshAlertsView();
          }, 300);
        }
      };
    }
  }, 100);
}

function markAlertAsSeen(alertId) {
  const alert = currentUser.alerts.find(a => a.id === alertId);
  if (alert && alert.status === 'new') {
    alert.status = 'seen';
    alert.seenAt = new Date().toISOString();
    
    // Sauvegarder dans le backend
    fetch(`${window.API_BASE_URL}/user/alerts/seen`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        alertId: alertId
      })
    }).catch(err => console.error('Erreur marquage alerte vue:', err));
  }
}

function deleteAlertWithWarning(alertId) {
  const alert = currentUser.alerts.find(a => a.id === alertId);
  if (!alert) return;
  
  const isBlurred = alert.isBlurred || false;
  const alertLimit = getAlertLimit();
  const activeAlerts = currentUser.alerts.filter(a => a.status !== 'deleted' && !a.isBlurred);
  
  // Avertissement si alerte floutée
  if (isBlurred) {
    const confirmMessage = `⚠️ Attention : Cette alerte est floutée.\n\n` +
      `Limite atteinte (${activeAlerts.length}/${alertLimit}).\n\n` +
      `Notez bien les informations avant d'effacer, car vous ne pourrez plus les voir !\n\n` +
      `Voulez-vous vraiment supprimer cette alerte ?`;
    
    if (!confirm(confirmMessage)) {
      return;
    }
  }
  
  // Supprimer l'alerte
  alert.status = 'deleted';
  
  // Supprimer les alarmes associées
  currentUserAlarms = currentUserAlarms.filter(a => a.alertId !== alertId);
  
  // Sauvegarder dans le backend
  fetch(`${window.API_BASE_URL}/user/alerts`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userId: currentUser.id.toString(),
      alertId: alertId
    })
  }).catch(err => console.error('Erreur suppression alerte:', err));
  
  // Si l'alerte était floutée, vérifier s'il faut déflouter d'autres alertes
  if (isBlurred && alertLimit !== Infinity) {
    const remainingBlurred = currentUser.alerts.filter(a => a.status !== 'deleted' && a.isBlurred);
    if (remainingBlurred.length > 0 && activeAlerts.length < alertLimit) {
      // Déflouter la première alerte floutée
      const toUnblur = remainingBlurred[0];
      toUnblur.isBlurred = false;
      showNotification(`✅ Alerte "${toUnblur.eventTitle}" est maintenant visible !`, "success");
    }
  }
  
  refreshAlertsView();
  showNotification("✅ Alerte supprimée", "success");
}

// ============================================
// SYSTÈME D'ALARMES
// ============================================

function openAddAlarmModal(context) {
  // context = 'alerts' ou 'agenda'
  const items = context === 'alerts' 
    ? currentUser.alerts.filter(a => a.status !== 'deleted')
    : currentUser.agenda.map(key => {
        const [type, id] = key.split(':');
        const data = type === 'event' ? eventsData : type === 'booking' ? bookingsData : servicesData;
        const item = data.find(i => i.id === parseInt(id));
        if (item && type === 'event') {
          return {
            id: `agenda-${key}`,
            eventId: id,
            eventTitle: item.title,
            eventDate: item.startDate || item.date,
            type: 'agenda'
          };
        }
        return null;
      }).filter(Boolean);

  if (items.length === 0) {
    showNotification("⚠️ Aucun élément disponible pour ajouter une alarme", "warning");
    return;
  }

  const selectedItems = [];
  const maxSelections = 3;

  const html = `
    <div style="position:relative;width:100%;max-width:600px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;border:2px solid #f59e0b;box-shadow:0 20px 60px rgba(245,158,11,0.3);overflow:hidden;">
      <div style="background:linear-gradient(135deg,#f59e0b,#d97706);padding:20px;text-align:center;">
        <div style="font-size:32px;margin-bottom:8px;">⏰</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Ajouter une alarme</h2>
        <p style="margin:8px 0 0;font-size:14px;color:rgba(255,255,255,0.9);">Sélectionnez jusqu'à ${maxSelections} élément${maxSelections > 1 ? 's' : ''}</p>
      </div>
      
      <div style="padding:20px;max-height:400px;overflow-y:auto;">
        <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;">Sélectionner des éléments :</div>
        <div style="display:grid;gap:8px;">
          ${items.map(item => {
            const itemId = item.id || `item-${item.eventId}`;
            const isSelected = selectedItems.includes(itemId);
            return `
              <div data-item-id="${itemId}" onclick="toggleAlarmItemSelection('${itemId}', '${context}')" style="
                padding:12px;
                border-radius:12px;
                border:2px solid ${isSelected ? '#f59e0b' : 'rgba(255,255,255,0.1)'};
                background:${isSelected ? 'rgba(245,158,11,0.2)' : 'rgba(255,255,255,0.05)'};
                cursor:pointer;
                transition:all 0.2s;
                display:flex;
                align-items:center;
                gap:12px;
              ">
                <div style="width:24px;height:24px;border-radius:50%;border:2px solid ${isSelected ? '#f59e0b' : 'rgba(255,255,255,0.3)'};background:${isSelected ? '#f59e0b' : 'transparent'};display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                  ${isSelected ? '✓' : ''}
                </div>
                <div style="flex:1;">
                  <div style="font-weight:600;font-size:14px;color:#fff;">
                    ${escapeHtml(item.eventTitle || item.favoriteName || 'Élément')}
                  </div>
                  ${item.eventDate ? `<div style="font-size:12px;color:rgba(255,255,255,0.6);">📅 ${formatEventDateRange(item.eventDate, item.eventDate)}</div>` : ''}
                </div>
              </div>
            `;
          }).join('')}
        </div>
        
        <div style="margin-top:20px;padding:16px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:12px;">
          <div style="font-size:14px;font-weight:600;color:#f59e0b;margin-bottom:12px;">Configuration de l'alarme :</div>
          
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
            <div>
              <label style="display:block;font-size:12px;color:rgba(255,255,255,0.7);margin-bottom:6px;">Temps avant</label>
              <input type="number" id="alarm-time-value" min="1" value="1" style="width:100%;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:#fff;font-size:14px;">
            </div>
            <div>
              <label style="display:block;font-size:12px;color:rgba(255,255,255,0.7);margin-bottom:6px;">Unité</label>
              <select id="alarm-time-unit" style="width:100%;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:#fff;font-size:14px;">
                <option value="hours">Heures</option>
                <option value="days" selected>Jours</option>
                <option value="weeks">Semaines</option>
              </select>
            </div>
          </div>
          
          <div style="font-size:12px;color:rgba(255,255,255,0.6);">
            Exemple : 1 jour avant = l'alarme sonnera 1 jour avant l'événement
          </div>
        </div>
      </div>
      
      <div style="padding:20px;border-top:1px solid rgba(255,255,255,0.1);display:flex;gap:12px;">
        <button onclick="closeAddAlarmModal()" style="flex:1;padding:14px;border-radius:12px;border:none;background:rgba(255,255,255,0.1);color:#fff;font-weight:600;cursor:pointer;">Annuler</button>
        <button onclick="saveAlarm('${context}')" style="flex:1;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;font-weight:600;cursor:pointer;">
          Enregistrer (${selectedItems.length}/${maxSelections})
        </button>
      </div>
    </div>
  `;

  // Créer ou réutiliser le backdrop
  let backdrop = document.getElementById("add-alarm-modal-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "add-alarm-modal-backdrop";
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.95);display:flex;align-items:center;justify-content:center;z-index:2000;backdrop-filter:blur(10px);";
    backdrop.onclick = (e) => {
      if (e.target === backdrop) closeAddAlarmModal();
    };
    document.body.appendChild(backdrop);
  }
  
  backdrop.innerHTML = html;
  backdrop.style.display = "flex";
  
  // Stocker le contexte et les items sélectionnés
  backdrop.dataset.context = context;
  backdrop.dataset.selectedItems = JSON.stringify([]);
}

function toggleAlarmItemSelection(itemId, context) {
  const backdrop = document.getElementById("add-alarm-modal-backdrop");
  if (!backdrop) return;
  
  const selectedItems = JSON.parse(backdrop.dataset.selectedItems || '[]');
  const maxSelections = 3;
  
  const index = selectedItems.indexOf(itemId);
  if (index > -1) {
    selectedItems.splice(index, 1);
  } else {
    if (selectedItems.length >= maxSelections) {
      showNotification(`⚠️ Maximum ${maxSelections} sélections autorisées`, "warning");
      return;
    }
    selectedItems.push(itemId);
  }
  
  backdrop.dataset.selectedItems = JSON.stringify(selectedItems);
  
  // Mettre à jour l'affichage
  const item = backdrop.querySelector(`[data-item-id="${itemId}"]`);
  if (item) {
    const isSelected = selectedItems.includes(itemId);
    item.style.border = `2px solid ${isSelected ? '#f59e0b' : 'rgba(255,255,255,0.1)'}`;
    item.style.background = isSelected ? 'rgba(245,158,11,0.2)' : 'rgba(255,255,255,0.05)';
    const checkbox = item.querySelector('div:first-child');
    if (checkbox) {
      checkbox.style.border = `2px solid ${isSelected ? '#f59e0b' : 'rgba(255,255,255,0.3)'}`;
      checkbox.style.background = isSelected ? '#f59e0b' : 'transparent';
      checkbox.innerHTML = isSelected ? '✓' : '';
    }
  }
  
  // Mettre à jour le bouton
  const saveBtn = backdrop.querySelector('button:last-child');
  if (saveBtn) {
    saveBtn.innerHTML = `Enregistrer (${selectedItems.length}/${maxSelections})`;
    saveBtn.disabled = selectedItems.length === 0;
    saveBtn.style.opacity = selectedItems.length === 0 ? '0.5' : '1';
  }
}

function saveAlarm(context) {
  const backdrop = document.getElementById("add-alarm-modal-backdrop");
  if (!backdrop) return;
  
  const selectedItems = JSON.parse(backdrop.dataset.selectedItems || '[]');
  if (selectedItems.length === 0) {
    showNotification("⚠️ Veuillez sélectionner au moins un élément", "warning");
    return;
  }
  
  const timeValue = parseInt(document.getElementById("alarm-time-value").value) || 1;
  const timeUnit = document.getElementById("alarm-time-unit").value;
  
  // Créer les alarmes
  const items = context === 'alerts' 
    ? currentUser.alerts.filter(a => a.status !== 'deleted')
    : currentUser.agenda.map(key => {
        const [type, id] = key.split(':');
        const data = type === 'event' ? eventsData : type === 'booking' ? bookingsData : servicesData;
        const item = data.find(i => i.id === parseInt(id));
        if (item && type === 'event') {
          return {
            id: `agenda-${key}`,
            alertId: `agenda-${key}`,
            eventId: id,
            eventTitle: item.title,
            eventDate: item.startDate || item.date,
            type: 'agenda'
          };
        }
        return null;
      }).filter(Boolean);
  
  selectedItems.forEach(itemId => {
    const item = items.find(i => (i.id || `item-${i.eventId}`) === itemId);
    if (item) {
      // ✅ Vérifier si l'alerte correspondante est floutée (pour les alertes)
      if (context === 'alerts') {
        const alert = currentUser.alerts.find(a => a.id === (item.id || item.alertId));
        if (alert && alert.isBlurred) {
          showNotification("⚠️ Impossible d'ajouter une alarme à une alerte floutée. Effacez une alerte pour la rendre visible.", "warning");
          return;
        }
      }
      
      const alarm = {
        id: `alarm-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        alertId: item.id || item.alertId || `agenda-${item.eventId}`,
        eventId: item.eventId || item.id,
        favoriteId: item.favoriteId,
        favoriteName: item.favoriteName || item.eventTitle,
        favoriteMode: item.favoriteMode || 'event',
        timeBefore: {
          value: timeValue,
          unit: timeUnit
        },
        notificationMethod: currentUser.notificationPreferences.email && currentUser.notificationPreferences.sms ? 'both' : 
                           currentUser.notificationPreferences.email ? 'email' : 
                           currentUser.notificationPreferences.sms ? 'sms' : 'email',
        createdAt: new Date().toISOString()
      };
      
      if (context === 'alerts') {
        currentUserAlarms.push(alarm);
      } else {
        alarmsForAgenda.push(alarm);
      }
    }
  });
  
  showNotification(`✅ ${selectedItems.length} alarme${selectedItems.length > 1 ? 's' : ''} ajoutée${selectedItems.length > 1 ? 's' : ''} !`, "success");
  closeAddAlarmModal();
  
  if (context === 'alerts') {
    refreshAlertsView();
  } else {
    // Rafraîchir la vue agenda si elle existe
    if (typeof refreshAgendaView === 'function') {
      refreshAgendaView();
    }
  }
}

function closeAddAlarmModal() {
  const backdrop = document.getElementById("add-alarm-modal-backdrop");
  if (backdrop) {
    backdrop.style.display = "none";
  }
}

// ============================================
// VÉRIFICATION ET DÉCLENCHEMENT DES ALARMES
// ============================================

// Stocker les alarmes déjà déclenchées pour éviter les doublons
let triggeredAlarms = new Set();

function checkAndTriggerAlarms() {
  if (!isLoggedIn()) return;
  
  const now = new Date();
  const allAlarms = [...currentUserAlarms, ...alarmsForAgenda];
  
  allAlarms.forEach(alarm => {
    // Vérifier si l'alarme a déjà été déclenchée
    if (triggeredAlarms.has(alarm.id)) return;
    
    // Trouver l'événement associé
    const event = eventsData.find(e => e.id.toString() === alarm.eventId);
    if (!event) return;
    
    // Obtenir la date de l'événement
    const eventDate = new Date(event.startDate || event.date);
    if (isNaN(eventDate.getTime())) return; // Date invalide
    
    // Calculer le temps avant l'événement
    const timeDiff = eventDate.getTime() - now.getTime();
    const timeDiffMs = timeDiff;
    
    // Convertir le timeBefore en millisecondes
    let timeBeforeMs = 0;
    const { value, unit } = alarm.timeBefore || { value: 1, unit: 'days' };
    
    switch(unit) {
      case 'hours':
        timeBeforeMs = value * 60 * 60 * 1000;
        break;
      case 'days':
        timeBeforeMs = value * 24 * 60 * 60 * 1000;
        break;
      case 'weeks':
        timeBeforeMs = value * 7 * 24 * 60 * 60 * 1000;
        break;
      default:
        timeBeforeMs = value * 24 * 60 * 60 * 1000; // Par défaut en jours
    }
    
    // Vérifier si on est dans la fenêtre de déclenchement (entre timeBefore et timeBefore - 1h)
    // Cela permet d'éviter de déclencher plusieurs fois la même alarme
    const oneHourMs = 60 * 60 * 1000;
    const isInWindow = timeDiffMs <= timeBeforeMs && timeDiffMs > (timeBeforeMs - oneHourMs);
    
    if (isInWindow) {
      triggerAlarm(alarm, event);
      triggeredAlarms.add(alarm.id);
    }
  });
}

function triggerAlarm(alarm, event) {
  const { notificationMethod } = alarm;
  
  // Préparer le message
  const eventTitle = event.title || 'Événement';
  const eventDate = new Date(event.startDate || event.date);
  const dateStr = eventDate.toLocaleDateString('fr-CH', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  
  const favoriteName = alarm.favoriteName || 'Votre favori';
  const { value, unit } = alarm.timeBefore || { value: 1, unit: 'days' };
  const unitText = unit === 'hours' ? 'heure(s)' : unit === 'days' ? 'jour(s)' : 'semaine(s)';
  
  const message = `⏰ Alarme : ${favoriteName} apparaît dans "${eventTitle}"\n\n` +
    `📅 Date : ${dateStr}\n` +
    `📍 Lieu : ${event.location || event.city || 'Lieu à confirmer'}\n\n` +
    `Cette alarme a été configurée pour ${value} ${unitText} avant l'événement.`;
  
  // Envoyer les notifications selon les préférences
  if (notificationMethod === 'email' || notificationMethod === 'both') {
    sendEmailNotification(currentUser.email, `Alarme MapEventAI : ${eventTitle}`, message);
    currentUser.emailNotifications++;
  }
  
  if (notificationMethod === 'sms' || notificationMethod === 'both') {
    if (canSendSMS()) {
      sendSMSNotification(currentUser.phone || '', message);
      updateSmsCount();
      currentUser.smsNotifications++;
    } else {
      // Si limite SMS atteinte, envoyer par email à la place
      if (!currentUser.notificationPreferences.email) {
        showNotification(`⚠️ Limite SMS atteinte. Alarme envoyée par email.`, "warning");
      }
      sendEmailNotification(currentUser.email, `Alarme MapEventAI : ${eventTitle}`, message);
      currentUser.emailNotifications++;
    }
  }
  
  // Afficher une notification dans l'interface
  showNotification(`⏰ Alarme : ${eventTitle} dans ${value} ${unitText} !`, "info");
  
  // Notification push pour smartphone (si l'utilisateur a autorisé)
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(`⏰ Alarme MapEvent`, {
      body: `${favoriteName} apparaît dans "${eventTitle}"\n${dateStr}\n📍 ${event.location || event.city || 'Lieu à confirmer'}`,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: `alarm-${alarm.id}`,
      requireInteraction: false,
      silent: false
    });
  } else if ('Notification' in window && Notification.permission === 'default') {
    // Demander la permission pour les notifications push
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        new Notification(`⏰ Alarme MapEvent`, {
          body: `${favoriteName} apparaît dans "${eventTitle}"\n${dateStr}\n📍 ${event.location || event.city || 'Lieu à confirmer'}`,
          icon: '/favicon.ico',
          badge: '/favicon.ico',
          tag: `alarm-${alarm.id}`,
          requireInteraction: false,
          silent: false
        });
      }
    });
  }
  
  // Sauvegarder les préférences mises à jour
  try {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (e) {
    console.error('Erreur sauvegarde utilisateur:', e);
  }
}

// Simuler l'envoi d'email (à remplacer par un vrai service d'email)
function sendEmailNotification(email, subject, message) {
  console.log(`📧 Email envoyé à ${email}`);
  console.log(`Sujet: ${subject}`);
  console.log(`Message: ${message}`);
  
  // TODO: Intégrer un service d'email (SendGrid, AWS SES, etc.)
  // Pour l'instant, on simule juste
}

// Simuler l'envoi de SMS (à remplacer par un vrai service SMS)
function sendSMSNotification(phone, message) {
  console.log(`📱 SMS envoyé à ${phone}`);
  console.log(`Message: ${message}`);
  
  // TODO: Intégrer un service SMS (Twilio, AWS SNS, etc.)
  // Pour l'instant, on simule juste
}

function updateSmsCount() {
  const limit = getSMSLimit();
  
  // Réinitialiser le compteur au début du mois
  const now = new Date();
  const lastReset = new Date(currentUser.smsResetDate || 0);
  const isNewMonth = now.getMonth() !== lastReset.getMonth() || now.getFullYear() !== lastReset.getFullYear();
  
  if (isNewMonth) {
    currentUser.smsNotifications = 0;
    currentUser.smsResetDate = now.toISOString();
  }
  
  // Vérifier si la limite est atteinte
  if (limit !== Infinity && currentUser.smsNotifications >= limit) {
    // Désactiver les notifications SMS si la limite est atteinte
    if (currentUser.notificationPreferences.sms) {
      currentUser.notificationPreferences.sms = false;
      showNotification(`⚠️ Limite SMS mensuelle atteinte (${limit}). Les alarmes seront envoyées par email uniquement.`, "warning");
    }
  }
  
  // Sauvegarder
  try {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (e) {
    console.error('Erreur sauvegarde compteur SMS:', e);
  }
}

// Vérifier les alarmes périodiquement (toutes les heures)
function startAlarmChecker() {
  // Vérifier immédiatement
  checkAndTriggerAlarms();
  
  // Puis toutes les heures
  setInterval(() => {
    checkAndTriggerAlarms();
  }, 60 * 60 * 1000); // 1 heure
}

// Démarrer le vérificateur d'alarmes au chargement
// ET charger l'utilisateur depuis /api/user/me (source de vérité)
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    // PRIORITÉ 1: Charger l'utilisateur depuis /api/user/me (source de vérité)
    // Ne pas faire confiance à localStorage.currentUser
    loadCurrentUserFromAPI().then(user => {
      if (user) {
        console.log('[AUTH] Utilisateur chargé au démarrage depuis /api/user/me:', user.email);
        // Mettre à jour le bloc compte
        if (typeof updateAccountBlockLegitimately === 'function') {
          setTimeout(() => updateAccountBlockLegitimately(), 100);
        }
        
        // IMPORTANT: Ne JAMAIS afficher l'onboarding après reconnexion
        // L'onboarding est demandé UNIQUEMENT lors de la première création de compte (dans performRegister)
        // Après déconnexion/reconnexion, on charge simplement le profil depuis /user/me
        console.log('[AUTH] Utilisateur reconnexion - pas d\'onboarding (uniquement a la creation de compte)');
      } else {
        console.log('[AUTH] Aucun utilisateur chargé');
        localStorage.removeItem('currentUser');
        sessionStorage.removeItem('currentUser');
        currentUser = getDefaultUser();
      }
    }).catch(error => {
      console.error('[AUTH] Erreur lors du chargement utilisateur au démarrage:', error);
    });
    
    // PRIORITÉ 2: Démarrer le vérificateur d'alarmes
    setTimeout(() => {
      startAlarmChecker();
    }, 5000); // Attendre 5 secondes après le chargement
  });
}

// ============================================
// INTÉGRATION DANS LE CHARGEMENT DES ÉVÉNEMENTS
// ============================================

// Modifier la fonction de chargement des événements pour appeler checkFavoritesInNewEvents
// Cette fonction doit être appelée après chaque chargement d'événements depuis le backend

// ============================================
// CHARGEMENT DES DONNÉES DEPUIS LE BACKEND
// ============================================

// Charger les favoris depuis le backend
async function loadFavoritesFromBackend() {
  if (!currentUser || !currentUser.isLoggedIn) return;
  
  try {
    const response = await fetch(`${window.API_BASE_URL}/user/favorites?userId=${currentUser.id}`);
    if (response.ok) {
      const data = await response.json();
      if (data.success && data.favorites) {
        currentUser.favorites = data.favorites;
      }
    }
  } catch (error) {
    console.error('Erreur chargement favoris:', error);
  }
}

// Charger les alertes depuis le backend
async function loadAlertsFromBackend() {
  if (!currentUser || !currentUser.isLoggedIn) return;
  
  try {
    const response = await fetch(`${window.API_BASE_URL}/user/alerts?userId=${currentUser.id}`);
    if (response.ok) {
      const data = await response.json();
      if (data.success && data.alerts) {
        currentUser.alerts = data.alerts;
      }
    }
  } catch (error) {
    console.error('Erreur chargement alertes:', error);
  }
}

// Charger l'agenda depuis le backend (persistant en base)
async function loadAgendaFromBackend() {
  if (!currentUser || !currentUser.isLoggedIn) return;
  
  try {
    // Utiliser le token JWT pour identifier l'utilisateur de manière fiable
    const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    const userId = currentUser.id || currentUser.email || '';
    
    const response = await fetch(`${window.API_BASE_URL}/user/agenda?userId=${userId}`, { headers });
    if (response.ok) {
      const data = await response.json();
      if (data.agenda && Array.isArray(data.agenda)) {
        currentUser.agenda = data.agenda;
        // Sauvegarder aussi en localStorage comme backup
        try { localStorage.setItem('user_agenda_backup', JSON.stringify(data.agenda)); } catch(e) {}
        console.log('[AGENDA] ' + data.agenda.length + ' elements charges depuis la base');
      }
    } else {
      console.warn('[AGENDA] API retourne', response.status, '- tentative localStorage');
      // Fallback localStorage
      try {
        const backup = localStorage.getItem('user_agenda_backup');
        if (backup) {
          currentUser.agenda = JSON.parse(backup);
          console.log('[AGENDA] ' + currentUser.agenda.length + ' elements restaures depuis localStorage');
        }
      } catch(e) {}
    }
  } catch (error) {
    console.error('[AGENDA] Erreur chargement:', error);
    // Fallback localStorage
    try {
      const backup = localStorage.getItem('user_agenda_backup');
      if (backup) {
        currentUser.agenda = JSON.parse(backup);
        console.log('[AGENDA] Fallback localStorage:', currentUser.agenda.length, 'elements');
      }
    } catch(e) {}
  }
}

// =====================================================
// 🌍 VIEWPORT PROGRESSIF - Chargement par zone visible
// =====================================================

// Debounce handler quand la carte bouge/zoome
function onViewportChange() {
  clearTimeout(viewportFetchTimeout);
  viewportFetchTimeout = setTimeout(() => {
    loadViewportData();
  }, 400); // 400ms debounce pour éviter les appels en rafale
}

// Charger les données adaptées au zoom et viewport actuels
async function loadViewportData() {
  if (!map) return;
  
  // Ne charger les données viewport que pour le mode events
  // Pour booking/services, on utilise refreshMarkers() qui respecte currentMode
  if (typeof currentMode !== 'undefined' && currentMode !== 'event') {
    return;
  }
  
  const zoom = map.getZoom();
  const bounds = map.getBounds();
  const south = bounds.getSouth();
  const north = bounds.getNorth();
  const west = bounds.getWest();
  const east = bounds.getEast();
  
  // Clé unique pour ce viewport (évite les re-fetch inutiles)
  const viewportKey = `${zoom}-${south.toFixed(2)}-${north.toFixed(2)}-${west.toFixed(2)}-${east.toFixed(2)}`;
  if (viewportKey === lastViewportKey) return;
  lastViewportKey = viewportKey;
  
  const params = new URLSearchParams({
    zoom: zoom,
    south: south.toFixed(4),
    north: north.toFixed(4),
    west: west.toFixed(4),
    east: east.toFixed(4)
  });
  
  try {
    const response = await fetch(`${window.API_BASE_URL}/events/viewport?${params}`);
    if (!response.ok) {
      console.warn('[VIEWPORT] Erreur API:', response.status);
      return;
    }
    const data = await response.json();
    
    // RE-VÉRIFIER le mode après le fetch async (l'utilisateur a pu changer de mode pendant le fetch)
    if (typeof currentMode !== 'undefined' && currentMode !== 'event') {
      console.log('[VIEWPORT] Mode changé pendant le fetch, abandon');
      return;
    }
    
    // Vérifier si un filtre est actif côté client
    const hasActiveFilter = (selectedCategories && selectedCategories.length > 0) || 
                            timeFilter || dateRangeStart || dateRangeEnd || 
                            (selectedDates && selectedDates.length > 0);
    
    if (data.type === 'clusters') {
      if (hasActiveFilter) {
        // FILTRE ACTIF + ZOOM FAIBLE : ne PAS afficher les clusters serveur (ils ignorent le filtre)
        // Garder markersLayer visible - le MarkerClusterGroup de Leaflet regroupera
        // automatiquement les marqueurs filtrés avec les bons chiffres
        geoCirclesLayer.clearLayers();
        if (markersLayer && !map.hasLayer(markersLayer)) {
          markersLayer.addTo(map);
        }
        console.log('[VIEWPORT] Filtre actif → clusters serveur ignorés, MarkerClusterGroup utilisé');
      } else {
        // PAS DE FILTRE : comportement normal - afficher les cercles de comptage serveur
        showGeoClusters(data.data);
        // Cacher le layer de marqueurs individuels
        if (markersLayer && map.hasLayer(markersLayer)) {
          map.removeLayer(markersLayer);
        }
      }
    } else if (data.type === 'events') {
      // MODE DÉTAILLÉ: afficher les events réels
      geoCirclesLayer.clearLayers();
      // Afficher le layer de marqueurs
      if (markersLayer && !map.hasLayer(markersLayer)) {
        markersLayer.addTo(map);
      }
      // Ajouter les nouveaux events (sans dupliquer)
      addViewportEvents(data);
    }
      } catch (e) {
    console.warn('[VIEWPORT] Erreur:', e);
  }
}

// Afficher les cercles agrégés (zoom faible) - UNIQUEMENT en mode event
function showGeoClusters(clusters) {
  geoCirclesLayer.clearLayers();
  
  // Ne JAMAIS afficher les clusters events en mode booking ou service
  if (typeof currentMode !== 'undefined' && currentMode !== 'event') {
    return;
  }
  
  const theme = getThemeMarkerColors ? getThemeMarkerColors() : {accent: '#FF6B35', border: 'rgba(255,255,255,0.5)'};
  const t = UI_THEMES && typeof uiThemeIndex !== "undefined" ? UI_THEMES[uiThemeIndex] : null;
  // Utiliser gradient custom si disponible, sinon couleur accent
  const customGrad = theme.gradient ? buildMarkerGradient(theme.gradient, 135) : null;
  const accentColor = customGrad || theme.accent || '#FF6B35';
  const geoBorderColor = theme.border || 'rgba(255,255,255,0.5)';
  
  clusters.forEach(([lat, lng, count]) => {
    // Taille COMPACTE - petits cercles discrets qui ne masquent pas la carte
    // Min 22px, max 36px - proportionnel au log du nombre d'events
    const radius = Math.max(11, Math.min(18, 8 + Math.log10(count + 1) * 3));
    
    // Formater le nombre (ex: 12345 -> "12K")
    let label;
    if (count >= 10000) {
      label = Math.round(count / 1000) + 'K';
    } else if (count >= 1000) {
      label = (count / 1000).toFixed(1) + 'K';
    } else {
      label = count.toString();
    }
    
    // Créer un DivIcon compact - ne masque pas les noms de villes
    const size = radius * 2;
    const icon = L.divIcon({
      html: `<div style="
        background: ${accentColor};
        opacity: 0.85;
        border-radius: 50%;
        width: ${size}px;
        height: ${size}px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: ${size < 26 ? 9 : size < 32 ? 10 : 11}px;
        color: #fff;
        text-shadow: 0 1px 1px rgba(0,0,0,0.6);
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        border: 1.5px solid ${geoBorderColor};
        cursor: pointer;
        transition: transform 0.15s;
      " onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">${label}</div>`,
      className: 'geo-cluster-icon',
      iconSize: L.point(size, size),
      iconAnchor: L.point(size / 2, size / 2)
    });
    
    const marker = L.marker([lat, lng], { icon: icon });
    
    // Au clic: zoomer vers cette zone
    marker.on('click', function() {
      const targetZoom = Math.min(map.getZoom() + 3, VIEWPORT_ZOOM_THRESHOLD);
      map.setView([lat, lng], targetZoom, { animate: true });
    });
    
    geoCirclesLayer.addLayer(marker);
  });
  
  console.log(`[VIEWPORT] 🌍 ${clusters.length} cercles agrégés affichés (zoom ${map.getZoom()})`);
}

// Ajouter les events du viewport au layer de marqueurs (incrémental, sans tout effacer)
function addViewportEvents(data) {
  if (!data.k || !data.d) return;
  
  const keys = data.k;
  let newCount = 0;
  
  data.d.forEach(row => {
    // Décoder le format compact
    const obj = {};
    for (let i = 0; i < keys.length; i++) {
      if (row[i] !== null && row[i] !== undefined) {
        obj[keys[i]] = row[i];
      }
    }
    
    // Skip si déjà chargé
    if (loadedEventIds.has(obj.id)) return;
    loadedEventIds.add(obj.id);
    
    // Construire l'objet event complet
    const event = {
      ...obj,
      type: 'event',
      lat: obj.latitude,
      lng: obj.longitude,
      startDate: obj.date ? new Date(obj.date + (obj.time ? 'T' + obj.time : '')) : null,
      endDate: obj.end_date ? new Date(obj.end_date) : null,
      address: obj.location || '',
      boost: '1.-',
      likes: 0,
      favorites: 0,
      participations: 0
    };
    
    // Vérifier lat/lng valides
    if (typeof event.lat !== 'number' || typeof event.lng !== 'number' || isNaN(event.lat) || isNaN(event.lng)) return;
    
    // Ajouter à eventsData (pour la recherche, les filtres, etc.)
    eventsData.push(event);
    
    // Vérifier si cet event passe le filtre actif avant de créer un marqueur
    let shouldAddMarker = true;
    if (selectedCategories && selectedCategories.length > 0) {
      // Filtre catégories actif → vérifier si l'event match
      const lowerCats = selectedCategories.map(c => c.toLowerCase());
      const itemCatParts = getEffectiveCategoryParts(event);
      
      // Construire les catégories autorisées (avec descendants et alias) - utilise FILTER_ALIASES global
      const allowed = new Set();
      lowerCats.forEach(sc => {
        allowed.add(sc);
        if (explorerTree) {
          findCategoryDescendants(sc, explorerTree).forEach(d => allowed.add(d));
        }
        (FILTER_ALIASES[sc] || []).forEach(a => {
          allowed.add(a);
          if (explorerTree) findCategoryDescendants(a, explorerTree).forEach(d => allowed.add(d));
        });
      });
      
      shouldAddMarker = Array.from(itemCatParts).some(cat => allowed.has(cat));
    }
    
    // Créer et ajouter le marqueur directement (incrémental, sans refreshMarkers)
    if (shouldAddMarker) {
      try {
        const icon = buildMarkerIcon(event);
        const marker = L.marker([event.lat, event.lng], { icon });
        marker.bindPopup('', { maxWidth: 360 });
        marker.on('popupopen', function() {
          marker.closePopup();
          currentPopupMarker = marker;
          const popupContent = buildPopupHtml(event);
          openPopupModal(popupContent, event);
        });
        markersLayer.addLayer(marker);
        markerMap[`event:${event.id}`] = marker;
        newCount++;
      } catch (err) {
        // Silencieux - erreur de marqueur individuel
      }
    }
  });
  
  if (newCount > 0) {
    window.eventsData = eventsData;
    // Mettre à jour la liste si visible
    if (typeof refreshListView === 'function') refreshListView();
    console.log(`[VIEWPORT] 📍 +${newCount} events ajoutés sur carte (total eventsData: ${eventsData.length})`);
  }
}

// Charger les événements depuis le backend et vérifier les favoris
async function loadEventsFromBackend() {
  // MODE VIEWPORT PROGRESSIF: déléguer au chargement par viewport
  // Cette fonction est gardée pour compatibilité (appelée après login, changement de statut, etc.)
  // Elle force un rechargement du viewport actuel
  console.log('[EVENTS] 🔄 loadEventsFromBackend → rechargement viewport');
  lastViewportKey = ''; // Forcer le re-fetch
  await loadViewportData();
}

// Charger les bookings depuis le backend
async function loadBookingsFromBackend() {
  try {
    const response = await fetch(`${window.API_BASE_URL}/bookings`);
    if (!response.ok) {
      console.warn('[BOOKINGS] Erreur API:', response.status);
      return;
    }
    
    const rawBookings = await response.json();
    const bookingsList = Array.isArray(rawBookings) ? rawBookings : (rawBookings.bookings || []);
    
    if (bookingsList.length === 0) {
      console.log('[BOOKINGS] Aucun booking trouvé dans le backend');
      return;
    }
    
    // Mapping catégorie -> image dans le dossier event/
    const bookingCategoryImageMap = {
      'musique > electro': 'electronic.jpg',
      'musique > techno': 'techno.jpg',
      'musique > house': 'house.jpg',
      'musique > trance': 'Trance.jpeg',
      'musique > jazz': 'jazzsoulfunk.jpg',
      'musique > blues': 'jazzsoulfunk.jpg',
      'musique > rock': 'rock.jpg',
      'musique > metal': 'metal.jpg',
      'musique > punk': 'punkrock.jpg',
      'musique > hip-hop': 'hiphop.jpg',
      'musique > hip-hop/rap': 'hiphop.jpg',
      'musique > rap': 'rap.jpg',
      'musique > reggae': 'reggae.jpg',
      'musique > soul': 'jazzsoulfunk.jpg',
      'musique > soul/funk': 'jazzsoulfunk.jpg',
      'musique > funk': 'jazzsoulfunk.jpg',
      'musique > pop': 'PopVariété.jpg',
      'musique > folk': 'folk.jpg',
      'musique > classique': 'opéra.jpg',
      'musique > world': 'world.jpg',
      'musique > latin': 'latin.jpg',
      'musique > r&b': 'RnB.jpg',
      'musique > concert': 'live musique.jpg',
      'musique > chanson': 'PopVariété.jpg',
      'musique > dnb': 'Drum&Bass.jpg',
      'musique > drum & bass': 'Drum&Bass.jpg',
      'performers': 'performers.png',
      'vj & visuels': 'VJ.jpg',
      'mcs & animateurs': 'bookingdefault.jpg',
      'live acts': 'LiveActs.jpg',
    };
    
    // Transformer les bookings API en format frontend
    const backendBookings = bookingsList.map(b => {
      // Catégories : peut être un string JSON ou un array
      let cats = b.categories || [];
      if (typeof cats === 'string') {
        try { cats = JSON.parse(cats); } catch(e) { cats = [cats]; }
      }
      if (!Array.isArray(cats)) cats = [cats];
      
      const desc = b.description || '';
      
      // Extraire les URLs audio depuis la description (format: "🔊 Audio: https://...")
      let audioUrls = [];
      const audioMatches = desc.matchAll(/🔊\s*Audio:\s*(https?:\/\/[^\s|]+)/g);
      for (const m of audioMatches) {
        audioUrls.push(m[1]);
      }
      
      // Extraire le lien source (publication originale) depuis la description
      let sourceUrl = b.source_url || null;
      const sourceMatch = desc.match(/🔗\s*Source:\s*(https?:\/\/[^\s|]+)/);
      if (sourceMatch) sourceUrl = sourceMatch[1];
      
      // Extraire les URLs cover depuis la description (format: "🖼️ Cover: https://...")
      let coverUrl = null;
      const coverMatch = desc.match(/🖼️\s*Cover:\s*(https?:\/\/[^\s|]+)/);
      if (coverMatch) {
        coverUrl = coverMatch[1];
      }
      
      // Nettoyer la description (retirer les URLs audio/cover/source + numéros de téléphone)
      let cleanDesc = desc
        .replace(/\s*\|\s*🔊\s*Audio:\s*https?:\/\/[^\s|]+/g, '')
        .replace(/\s*\|\s*🖼️\s*Cover:\s*https?:\/\/[^\s|]+/g, '')
        .replace(/\s*\|\s*🔗\s*Source:\s*https?:\/\/[^\s|]+/g, '')
        // Supprimer les numéros de téléphone (formats: +41 xx xxx xx xx, 0xx xxx xx xx, 07x.xxx.xx.xx, etc.)
        .replace(/📞\s*[^|\n]*/g, '')
        .replace(/☎\s*[^|\n]*/g, '')
        .replace(/(?:Tel|Tél|Téléphone|Phone|Tel\.|Tél\.)\s*[:.]?\s*[\+]?[\d\s\.\-\(\)]{7,}/gi, '')
        .replace(/(?:\+\d{1,3}[\s\.\-]?)?\(?\d{2,4}\)?[\s\.\-]?\d{2,4}[\s\.\-]?\d{2,4}[\s\.\-]?\d{0,4}/g, (match) => {
          // Ne supprimer que si ça ressemble vraiment à un numéro de téléphone (min 10 chiffres)
          const digits = match.replace(/\D/g, '');
          return digits.length >= 10 ? '' : match;
        })
        .replace(/\s{2,}/g, ' ')
        .trim();
      
      // Trouver la bonne image basée sur la catégorie
      let categoryImage = null;
      for (const cat of cats) {
        const catLower = (cat || '').toLowerCase();
        if (bookingCategoryImageMap[catLower]) {
          // Utiliser le dossier event/ pour les images musicales
          const imgFile = bookingCategoryImageMap[catLower];
          const folder = ['performers.png', 'VJ.jpg', 'LiveActs.jpg', 'bookingdefault.jpg'].includes(imgFile) ? 'booking' : 'event';
          categoryImage = `/assets/category_images/${folder}/${imgFile}`;
          break;
        }
      }
      // Fallback: image musicale générique
      if (!categoryImage) {
        categoryImage = '/assets/category_images/event/music.jpg';
      }
      
      return {
        id: b.id,
        type: 'booking',
        name: b.title || b.name || '',
        title: b.title || b.name || '',
        description: cleanDesc,
        city: b.city || '',
        address: b.location || b.address || '',
        lat: parseFloat(b.latitude) || parseFloat(b.lat) || null,
        lng: parseFloat(b.longitude) || parseFloat(b.lng) || null,
        categories: cats,
        mainCategory: cats[0] || 'Musique',
        categoryImage: null,
        // Image: cover Audius ou image par catégorie
        imageUrl: coverUrl || categoryImage,
        boost: b.boost || 'basic',
        soundLinks: audioUrls.length > 0 ? audioUrls : (b.sound_links || []),
        email: b.email || '',
        website: b.website || '',
        sourceUrl: sourceUrl,
        source_url: sourceUrl,
        validation_status: b.validation_status || 'scraped',
        isAI: false,
        verified: false,
        likes: b.likes || 0,
        rating: b.rating || '0'
      };
    }).filter(b => {
      // Filtrer : GPS valide ET au moins un son
      if (!b.lat || !b.lng || isNaN(b.lat) || isNaN(b.lng)) return false;
      if (!b.soundLinks || b.soundLinks.length === 0) return false;
      return true;
    });
    
    // Filtrer les doublons
    const existingIds = new Set(bookingsData.map(b => b.id));
    const newBookings = backendBookings.filter(b => !existingIds.has(b.id));
    
    if (newBookings.length > 0) {
      bookingsData.push(...newBookings);
      window.bookingsData = bookingsData;
      console.log(`✅ ${newBookings.length} bookings chargés (avec audio, marqueurs orange)`);
      
      // Rafraîchir si on est en mode booking
      if (currentMode === 'booking') {
        refreshMarkers();
        refreshListView();
      }
    }
  } catch (error) {
    console.error('[BOOKINGS] Erreur chargement:', error);
  }
}

// Charger les services depuis le backend
async function loadServicesFromBackend() {
  try {
    const response = await fetch(`${window.API_BASE_URL}/services`);
    if (!response.ok) {
      console.warn('[SERVICES] Erreur API:', response.status);
      return;
    }
    
    const rawServices = await response.json();
    const servicesList = Array.isArray(rawServices) ? rawServices : (rawServices.services || []);
    
    if (servicesList.length === 0) {
      console.log('[SERVICES] Aucun service trouvé dans le backend');
      return;
    }
    
    // Transformer les services API en format frontend
    const backendServices = servicesList.map(s => {
      let cats = s.categories || [];
      if (typeof cats === 'string') {
        try { cats = JSON.parse(cats); } catch(e) { cats = [cats]; }
      }
      if (!Array.isArray(cats)) cats = [cats];
      
      return {
        id: s.id,
        type: 'service',
        name: s.name || '',
        title: s.name || '',
        description: s.description || '',
        address: s.location || '',
        location: s.location || '',
        lat: parseFloat(s.latitude) || parseFloat(s.lat) || null,
        lng: parseFloat(s.longitude) || parseFloat(s.lng) || null,
        categories: cats,
        mainCategory: cats[0] || 'Prestataires & Logistique',
        boost: '1.-',
        likes: s.likes_count || 0,
        favorites: s.favorites_count || 0,
        isAI: false,
        verified: false,
        created_at: s.created_at
      };
    }).filter(s => s.lat && s.lng && !isNaN(s.lat) && !isNaN(s.lng));
    
    // Filtrer les doublons
    const existingIds = new Set(servicesData.map(s => s.id));
    const newServices = backendServices.filter(s => !existingIds.has(s.id));
    
    if (newServices.length > 0) {
      servicesData.push(...newServices);
      window.servicesData = servicesData;
      console.log(`✅ ${newServices.length} services chargés depuis le backend`);
      
      // Rafraîchir si on est en mode service
      if (currentMode === 'service') {
        refreshMarkers();
        refreshListView();
      }
    }
  } catch (error) {
    console.error('[SERVICES] Erreur chargement:', error);
  }
}

// Parser une date française (ex: "5 Avr. 2026" + "08:30:00")
function parseFrenchDate(dateStr, timeStr) {
  if (!dateStr) return null;
  
  const months = {
    'janv.': '01', 'févr.': '02', 'mars': '03', 'avr.': '04',
    'mai': '05', 'juin': '06', 'juil.': '07', 'août': '08',
    'sept.': '09', 'oct.': '10', 'nov.': '11', 'déc.': '12'
  };
  
  // Parser "5 Avr. 2026"
  const parts = dateStr.trim().split(' ');
  if (parts.length !== 3) return null;
  
  const day = parts[0].padStart(2, '0');
  const month = months[parts[1].toLowerCase()] || '01';
  const year = parts[2];
  
  // Parser l'heure "08:30:00"
  const time = timeStr ? timeStr.substring(0, 5) : '00:00';
  
  return `${year}-${month}-${day}T${time}:00`;
}

// Charger toutes les données utilisateur au login
async function loadUserDataOnLogin() {
  // 1. Charger l'utilisateur depuis /api/user/me (source de vérité)
  const user = await loadCurrentUserFromAPI().catch(err => {
    console.error('[AUTH] Erreur chargement utilisateur au démarrage:', err);
    return null;
  });
  
  if (user) {
    console.log('[AUTH] Utilisateur chargé depuis /api/user/me:', user.email);
    if (typeof window.updateAccountBlock === 'function') {
      setTimeout(() => window.updateAccountBlock(), 100);
    }
  } else {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      try {
        const parsed = JSON.parse(savedUser);
        if (parsed.addresses && parsed.addresses.length > 0) {
          currentUser.addresses = parsed.addresses || [];
        }
      } catch (e) {
        console.error('Erreur chargement adresses:', e);
      }
    }
  }
  
  loadUserLocationFromStorage();
  
  if (!currentUser.location || !currentUser.location.lat || !currentUser.location.lng) {
    requestUserLocation().catch(() => console.log('Géolocalisation refusée ou indisponible'));
  }
  
  // Charger agenda, favoris, alertes depuis la base (persistant)
  if (currentUser && currentUser.isLoggedIn) {
    await loadAgendaFromBackend();
    await loadFavoritesFromBackend();
    await loadAlertsFromBackend();
    
    // Charger le theme custom depuis la BDD
    try {
      const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
      if (token) {
        const themeResp = await fetch(`${window.API_BASE_URL}/user/theme`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (themeResp.ok) {
          const themeConfig = await themeResp.json();
          if (themeConfig && themeConfig.markerColors) {
            window.customThemeConfig = themeConfig;
            applyCustomColors();
            console.log('[THEME] Theme custom charge depuis la BDD');
          }
        }
      }
    } catch (e) {
      console.warn('[THEME] Erreur chargement theme:', e);
    }
    
    if (typeof refreshMarkers === 'function') refreshMarkers();
    if (typeof refreshListView === 'function') refreshListView();
  }
  
  await loadEventsFromBackend();
  
  // Afficher la popup d'alertes si il y en a de nouvelles
  // CORRECTION: Vérifier que currentUser.alerts existe avant d'utiliser filter
  if (currentUser && currentUser.alerts && Array.isArray(currentUser.alerts)) {
    const newAlerts = currentUser.alerts.filter(a => a.status === 'new');
    if (newAlerts.length > 0) {
      setTimeout(() => {
        showAlertsLoginPopup(newAlerts);
      }, 1000);
    }
  } else {
    // Initialiser alerts si undefined
    if (currentUser && !currentUser.alerts) {
      currentUser.alerts = [];
    }
  }
}

// ============================================
// GÉOLOCALISATION UTILISATEUR
// ============================================

// Obtenir la position de l'utilisateur (géolocalisation)
function getUserLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Géolocalisation non supportée'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          city: null // Peut être rempli avec une API de géocodage inverse
        };
        
        // Sauvegarder dans currentUser
        if (currentUser) {
          currentUser.location = location;
        }
        
        // Sauvegarder dans localStorage
        try {
          localStorage.setItem('userLocation', JSON.stringify(location));
        } catch (e) {
          console.error('Erreur sauvegarde position:', e);
        }
        
        resolve(location);
      },
      (error) => {
        console.error('Erreur géolocalisation:', error);
        reject(error);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // Cache de 5 minutes
      }
    );
  });
}

// Définir manuellement la position de l'utilisateur (par ville ou coordonnées)
function setUserLocation(lat, lng, city = null) {
  if (currentUser) {
    currentUser.location = {
      lat: lat,
      lng: lng,
      city: city
    };
    
    // Sauvegarder dans localStorage
    try {
      localStorage.setItem('userLocation', JSON.stringify(currentUser.location));
    } catch (e) {
      console.error('Erreur sauvegarde position:', e);
    }
    
    showNotification('📍 Position mise à jour', 'success');
  }
}

// Charger la position depuis localStorage
function loadUserLocationFromStorage() {
  try {
    const saved = localStorage.getItem('userLocation');
    if (saved) {
      const location = JSON.parse(saved);
      if (currentUser) {
        currentUser.location = location;
      }
      return location;
    }
  } catch (e) {
    console.error('Erreur chargement position:', e);
  }
  return null;
}

// Demander la géolocalisation à l'utilisateur
async function requestUserLocation() {
  try {
    const location = await getUserLocation();
    showNotification('📍 Position obtenue avec succès', 'success');
    return location;
  } catch (error) {
    showNotification('⚠️ Impossible d\'obtenir votre position. Vous pouvez la définir manuellement dans les paramètres.', 'warning');
    return null;
  }
}

// ============================================
// INTÉGRATION DANS L'AGENDA
// ============================================

// Modifier openAgendaModal pour ajouter le bouton "Ajouter alarme"
// Cette fonction doit être modifiée pour inclure le système d'alarmes

// ============================================
// EXPOSITION GLOBALE EXPLICITE DES FONCTIONS D'AUTHENTIFICATION
// ============================================
// Garantir que les fonctions sont disponibles globalement à la fin du chargement
// Ces assignations sont critiques pour que les boutons/links HTML puissent les appeler

// Fonction helper pour exposer de manière robuste
(function exposeAuthFunctions() {
  // Vérifier que window existe
  if (typeof window === 'undefined') {
    console.error('[AUTH] window n\'est pas disponible');
    return;
  }
  
  // REMOVED: Les fonctions AUTH sont maintenant dans auth.js et exposées globalement
  // Vérification que les fonctions sont bien chargées depuis auth.js
