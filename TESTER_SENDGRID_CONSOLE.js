// Script JavaScript à copier-coller dans la console du navigateur (F12)
// Pour tester l'envoi d'email SendGrid via l'API

console.log("============================================================");
console.log("🧪 TEST SENDGRID - CONSOLE NAVIGATEUR");
console.log("============================================================");
console.log("");

// Fonction de test
async function testerSendGrid() {
  const API_BASE = window.API_BASE_URL || "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api";
  
  // Demander l'email de test
  const testEmail = prompt("Entrez votre adresse email pour le test:");
  
  if (!testEmail) {
    console.log("❌ Test annulé");
    return;
  }
  
  console.log("📧 Envoi d'un code de vérification à: " + testEmail);
  console.log("");
  
  const body = {
    email: testEmail,
    username: "Test User"
  };
  
  try {
    const response = await fetch(API_BASE + "/user/send-verification-code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });
    
    if (response.ok) {
      const data = await response.json();
      
      console.log("✅ Réponse du serveur:");
      console.log("   Success:", data.success);
      console.log("   Message:", data.message);
      console.log("");
      
      if (data.dev_mode === true || (data.message && data.message.indexOf("mode développement") !== -1)) {
        console.log("⚠️  MODE DÉVELOPPEMENT DÉTECTÉ");
        console.log("   L'email n'a PAS été envoyé réellement");
        console.log("   Raison probable: SENDGRID_API_KEY non configurée ou invalide");
        console.log("");
        console.log("📝 ACTIONS À FAIRE:");
        console.log("   1. Vérifiez les variables d'environnement Lambda");
        console.log("   2. Vérifiez que SENDGRID_API_KEY est configurée");
        console.log("   3. Vérifiez que la clé API SendGrid est valide");
        console.log("   4. Consultez les logs CloudWatch pour plus de détails");
      } else {
        console.log("✅ EMAIL ENVOYÉ AVEC SUCCÈS!");
        console.log("   Vérifiez votre boîte email: " + testEmail);
        console.log("   (Vérifiez aussi les spams)");
      }
      
      if (data.code) {
        console.log("");
        console.log("🔐 CODE DE VÉRIFICATION (DEV): " + data.code);
        alert("CODE DEV: " + data.code);
      }
      
    } else {
      const errorText = await response.text();
      let errorData = { error: "Erreur inconnue" };
      
      try {
        errorData = JSON.parse(errorText);
      } catch (e) {
        errorData = { error: errorText };
      }
      
      console.log("❌ ERREUR lors du test:");
      console.log("   Code HTTP:", response.status);
      console.log("   Erreur:", errorData.error || errorData.message || errorText);
      console.log("");
      console.log("📝 VÉRIFICATIONS À FAIRE:");
      console.log("   1. Vérifiez que Lambda est accessible");
      console.log("   2. Vérifiez les logs CloudWatch");
      console.log("   3. Vérifiez la configuration SendGrid dans Lambda");
      
      alert("❌ Erreur: " + (errorData.error || errorData.message || "Erreur inconnue"));
    }
    
  } catch (error) {
    console.error("❌ EXCEPTION lors du test:", error);
    console.error("   Type:", error.name);
    console.error("   Message:", error.message);
    console.error("");
    console.log("📝 VÉRIFICATIONS À FAIRE:");
    console.log("   1. Vérifiez votre connexion internet");
    console.log("   2. Vérifiez que l'API est accessible");
    console.log("   3. Vérifiez la console pour plus de détails");
    
    alert("❌ Erreur réseau: " + error.message);
  }
  
  console.log("");
  console.log("============================================================");
  console.log("FIN DU TEST");
  console.log("============================================================");
}

// Exécuter le test
console.log("🚀 Démarrage du test...");
console.log("");
testerSendGrid();
