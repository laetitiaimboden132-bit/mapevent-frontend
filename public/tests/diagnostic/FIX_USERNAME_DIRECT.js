(function() {
  let usernameFromForm = null;
  try {
    const pendingData = localStorage.getItem('pendingRegisterDataForGoogle');
    if (pendingData) {
      const parsed = JSON.parse(pendingData);
      if (parsed.username && parsed.username !== 'null' && parsed.username !== '' && !parsed.username.includes('@')) {
        usernameFromForm = parsed.username;
        console.log('✅ Username trouvé:', usernameFromForm);
      }
    }
  } catch(e) {
    console.error('❌ Erreur:', e);
  }
  
  if (!usernameFromForm) {
    try {
      const pendingData = sessionStorage.getItem('pendingRegisterDataForGoogle');
      if (pendingData) {
        const parsed = JSON.parse(pendingData);
        if (parsed.username && parsed.username !== 'null' && parsed.username !== '' && !parsed.username.includes('@')) {
          usernameFromForm = parsed.username;
          console.log('✅ Username trouvé dans sessionStorage:', usernameFromForm);
        }
      }
    } catch(e) {
      console.error('❌ Erreur:', e);
    }
  }
  
  if (!usernameFromForm) {
    console.log('❌ Aucun username trouvé');
    return;
  }
  
  if (window.currentUser) {
    window.currentUser.username = usernameFromForm;
    console.log('✅ window.currentUser.username mis à jour:', window.currentUser.username);
  } else {
    console.log('❌ window.currentUser n\'existe pas');
    return;
  }
  
  try {
    const currentUserLS = localStorage.getItem('currentUser');
    if (currentUserLS) {
      const parsed = JSON.parse(currentUserLS);
      parsed.username = usernameFromForm;
      localStorage.setItem('currentUser', JSON.stringify(parsed));
      console.log('✅ localStorage mis à jour');
    }
  } catch(e) {
    console.error('❌ Erreur sauvegarde:', e);
  }
  
  const accountName = document.getElementById('account-name');
  if (accountName) {
    accountName.textContent = usernameFromForm;
    console.log('✅ Bloc compte mis à jour:', usernameFromForm);
  } else {
    console.log('❌ account-name non trouvé');
  }
  
  console.log('%c✅ Username corrigé !', 'color: #22c55e; font-weight: bold;');
})();
