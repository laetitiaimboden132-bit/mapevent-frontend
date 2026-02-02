// ============================================
// TEST ADRESSES MONDIALES - VERSION CONSOLE
// ============================================
// Copiez-collez TOUT ce script dans la console (F12)

(function() {
  console.clear();
  console.log('%c🌍 ===== TEST ADRESSES MONDIALES =====', 'font-size: 18px; font-weight: bold; color: #00ffc3;');
  console.log('');
  
  // Fonction de test automatique
  window.testAddressSearch = async function(query) {
    console.log(`\n🔍 Test de recherche pour: "${query}"`);
    try {
      const userLanguage = navigator.language || navigator.userLanguage || 'fr';
      const langCode = userLanguage.split('-')[0];
      
      console.log(`🌍 Langue détectée: ${langCode}`);
      
      const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=10&addressdetails=1&accept-language=${langCode},en`;
      console.log(`📡 URL: ${url.substring(0, 100)}...`);
      
      const response = await fetch(url, {
        headers: {
          'Accept-Language': `${langCode},en,fr`,
          'User-Agent': 'MapEvent/1.0'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const results = await response.json();
      console.log(`✅ ${results.length} résultat(s) trouvé(s):`);
      
      if (results.length === 0) {
        console.warn('⚠️ Aucune adresse trouvée');
        return [];
      }
      
      results.forEach((result, index) => {
        const country = result.address?.country_code?.toUpperCase() || 'N/A';
        const city = result.address?.city || result.address?.town || result.address?.village || 'N/A';
        console.log(`\n  ${index + 1}. ${result.display_name}`);
        console.log(`     📍 Coordonnées: ${result.lat}, ${result.lon}`);
        console.log(`     🌍 Pays: ${country}`);
        console.log(`     🏙️ Ville: ${city}`);
        console.log(`     📮 Code postal: ${result.address?.postcode || 'N/A'}`);
      });
      
      return results;
    } catch (error) {
      console.error('❌ Erreur:', error);
      return null;
    }
  };
  
  // Liste d'adresses de test
  const testAddresses = {
    'Afrique': ['Lagos, Nigeria', 'Cairo, Egypt', 'Nairobi, Kenya', 'Cape Town, South Africa'],
    'Asie': ['Tokyo, Japan', 'Mumbai, India', 'Bangkok, Thailand', 'Seoul, South Korea'],
    'Amériques': ['São Paulo, Brazil', 'Mexico City, Mexico', 'Buenos Aires, Argentina'],
    'Océanie': ['Sydney, Australia', 'Auckland, New Zealand'],
    'Europe': ['Paris, France', 'Berlin, Germany', 'Madrid, Spain'],
    'Moyen-Orient': ['Dubai, UAE', 'Riyadh, Saudi Arabia', 'Tel Aviv, Israel']
  };
  
  console.log('%c📋 ADRESSES DE TEST PAR RÉGION:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  Object.keys(testAddresses).forEach(region => {
    console.log(`\n${region}:`);
    testAddresses[region].forEach(addr => {
      console.log(`  - ${addr}`);
    });
  });
  
  console.log('');
  console.log('%c🧪 COMMANDES DE TEST:', 'font-weight: bold; color: #f59e0b; font-size: 14px;');
  console.log('%c  testAddressSearch("Lagos, Nigeria")', 'color: #00ffc3;');
  console.log('%c  testAddressSearch("Tokyo, Japan")', 'color: #00ffc3;');
  console.log('%c  testAddressSearch("São Paulo, Brazil")', 'color: #00ffc3;');
  console.log('%c  testAddressSearch("Sydney, Australia")', 'color: #00ffc3;');
  console.log('%c  testAddressSearch("Dubai, UAE")', 'color: #00ffc3;');
  
  console.log('');
  console.log('%c✅ Fonction testAddressSearch() créée et prête à l\'emploi!', 'font-weight: bold; color: #22c55e;');
  console.log('');
  
  // Test automatique d'une adresse
  console.log('%c🚀 Test automatique avec "Lagos, Nigeria"...', 'font-weight: bold; color: #3b82f6;');
  testAddressSearch("Lagos, Nigeria");
  
  return {
    testFunction: window.testAddressSearch,
    testAddresses
  };
})();
