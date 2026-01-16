// ============================================
// TEST ADRESSES MONDIALES
// ============================================
// Copiez ce script dans la console pour tester les adresses du monde entier

(function() {
  console.clear();
  console.log('%c🌍 ===== TEST ADRESSES MONDIALES =====', 'font-size: 18px; font-weight: bold; color: #00ffc3;');
  console.log('');
  
  // Liste d'adresses de test pour différents pays
  const testAddresses = {
    'Afrique': [
      'Lagos, Nigeria',
      'Cairo, Egypt',
      'Nairobi, Kenya',
      'Cape Town, South Africa',
      'Dakar, Senegal',
      'Kigali, Rwanda',
      'Accra, Ghana'
    ],
    'Asie': [
      'Tokyo, Japan',
      'Mumbai, India',
      'Bangkok, Thailand',
      'Seoul, South Korea',
      'Jakarta, Indonesia',
      'Manila, Philippines',
      'Ho Chi Minh City, Vietnam'
    ],
    'Amériques': [
      'São Paulo, Brazil',
      'Mexico City, Mexico',
      'Buenos Aires, Argentina',
      'Lima, Peru',
      'Bogotá, Colombia',
      'Montreal, Canada',
      'Santiago, Chile'
    ],
    'Océanie': [
      'Sydney, Australia',
      'Auckland, New Zealand',
      'Suva, Fiji',
      'Port Moresby, Papua New Guinea'
    ],
    'Europe': [
      'Paris, France',
      'Berlin, Germany',
      'Madrid, Spain',
      'Rome, Italy',
      'London, United Kingdom',
      'Amsterdam, Netherlands',
      'Warsaw, Poland'
    ],
    'Moyen-Orient': [
      'Dubai, United Arab Emirates',
      'Riyadh, Saudi Arabia',
      'Tel Aviv, Israel',
      'Istanbul, Turkey',
      'Beirut, Lebanon'
    ]
  };
  
  console.log('%c📋 ADRESSES DE TEST PAR RÉGION:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  Object.keys(testAddresses).forEach(region => {
    console.log(`\n${region}:`);
    testAddresses[region].forEach(addr => {
      console.log(`  - ${addr}`);
    });
  });
  
  console.log('');
  console.log('%c🧪 COMMENT TESTER:', 'font-weight: bold; color: #f59e0b; font-size: 14px;');
  console.log('%c  1. Ouvrez le formulaire d\'inscription', 'color: #00ffc3;');
  console.log('  2. Cliquez sur le champ "Adresse postale"');
  console.log('  3. Tapez une des adresses ci-dessus');
  console.log('  4. Vérifiez que les suggestions apparaissent');
  console.log('  5. Sélectionnez une adresse');
  console.log('  6. Vérifiez que les coordonnées sont correctes');
  console.log('');
  console.log('%c  Pour tester manuellement avec Nominatim:', 'color: #00ffc3;');
  console.log('    const query = "Lagos, Nigeria";');
  console.log('    const response = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5&addressdetails=1&accept-language=fr,en`);');
  console.log('    const results = await response.json();');
  console.log('    console.log("Résultats:", results);');
  console.log('');
  console.log('%c  Pour tester la détection de langue:', 'color: #00ffc3;');
  console.log('    const lang = navigator.language || navigator.userLanguage || "fr";');
  console.log('    console.log("Langue détectée:", lang);');
  console.log('    console.log("Code langue:", lang.split("-")[0]);');
  
  console.log('');
  console.log('%c✅ ===== FIN DU GUIDE DE TEST =====', 'font-size: 18px; font-weight: bold; color: #22c55e;');
  console.log('');
  
  // Fonction de test automatique
  window.testAddressSearch = async function(query) {
    console.log(`\n🔍 Test de recherche pour: "${query}"`);
    try {
      const userLanguage = navigator.language || navigator.userLanguage || 'fr';
      const langCode = userLanguage.split('-')[0];
      
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5&addressdetails=1&accept-language=${langCode},en`,
        {
          headers: {
            'Accept-Language': `${langCode},en,fr`,
            'User-Agent': 'MapEvent/1.0'
          }
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const results = await response.json();
      console.log(`✅ ${results.length} résultat(s) trouvé(s):`);
      results.forEach((result, index) => {
        console.log(`  ${index + 1}. ${result.display_name}`);
        console.log(`     Coordonnées: ${result.lat}, ${result.lon}`);
        console.log(`     Pays: ${result.address?.country_code?.toUpperCase() || 'N/A'}`);
      });
      
      return results;
    } catch (error) {
      console.error('❌ Erreur:', error);
      return null;
    }
  };
  
  console.log('%c💡 Fonction de test créée:', 'font-weight: bold; color: #3b82f6;');
  console.log('  Utilisez: testAddressSearch("Lagos, Nigeria")');
  console.log('  Ou: testAddressSearch("Tokyo, Japan")');
  console.log('');
  
  return {
    testAddresses,
    testFunction: window.testAddressSearch
  };
})();
