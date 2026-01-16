// Script simple - Copiez-collez TOUT dans la console (F12)

async function testerSendGrid() {
  var API_BASE = window.API_BASE_URL || "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api";
  var testEmail = prompt("Entrez votre adresse email pour le test:");
  
  if (!testEmail) {
    console.log("❌ Test annulé");
    return;
  }
  
  console.log("============================================================");
  console.log("🧪 TEST SENDGRID");
  console.log("============================================================");
  console.log("📧 Email de test: " + testEmail);
  console.log("🌐 API Base: " + API_BASE);
  console.log("");
  
  try {
    console.log("🔄 Appel de l'API...");
    var response = await fetch(API_BASE + "/user/send-verification-code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: testEmail,
        username: "Test User"
      })
    });
    
    console.log("📡 Code HTTP: " + response.status);
    console.log("📡 Status OK: " + response.ok);
    console.log("");
    
    var responseText = await response.text();
    console.log("📥 Réponse brute:", responseText);
    console.log("");
    
    var data = null;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      console.error("❌ Impossible de parser la réponse JSON:", e);
      console.error("Réponse brute:", responseText);
      alert("❌ Réponse invalide du serveur. Vérifiez la console.");
      return;
    }
    
    console.log("📦 Données parsées:", data);
    console.log("");
    
    if (response.ok) {
      console.log("✅ Réponse OK du serveur");
      console.log("   Success:", data.success);
      console.log("   Message:", data.message);
      console.log("   Dev Mode:", data.dev_mode);
      console.log("");
      
      if (data.dev_mode === true || (data.message && data.message.indexOf("mode développement") !== -1)) {
        console.log("⚠️ ⚠️ ⚠️ MODE DÉVELOPPEMENT DÉTECTÉ ⚠️ ⚠️ ⚠️");
        console.log("");
        console.log("❌ L'email n'a PAS été envoyé réellement");
        console.log("📝 Raison probable: SENDGRID_API_KEY non configurée");
        console.log("");
        console.log("🔧 ACTIONS À FAIRE:");
        console.log("   1. Vérifiez les variables d'environnement Lambda dans AWS Console");
        console.log("   2. Vérifiez que SENDGRID_API_KEY est bien configurée");
        console.log("   3. Vérifiez que la clé API SendGrid est valide");
        console.log("   4. Consultez les logs CloudWatch pour plus de détails");
        alert("⚠️ MODE DÉVELOPPEMENT - Email NON envoyé\nSENDGRID_API_KEY probablement non configurée");
      } else {
        console.log("✅ ✅ ✅ EMAIL ENVOYÉ AVEC SUCCÈS! ✅ ✅ ✅");
        console.log("");
        console.log("📬 Vérifiez votre boîte email: " + testEmail);
        console.log("📬 Vérifiez aussi les SPAMS/Junk");
        alert("✅ Email envoyé! Vérifiez " + testEmail + " (et les spams)");
      }
      
      if (data.code) {
        console.log("");
        console.log("🔐 🔐 🔐 CODE DE VÉRIFICATION (DEV): " + data.code + " 🔐 🔐 🔐");
        alert("CODE DEV: " + data.code);
      }
    } else {
      console.error("❌ ERREUR du serveur");
      console.error("   Code HTTP: " + response.status);
      console.error("   Erreur:", data.error || data.message || "Erreur inconnue");
      console.error("   Données complètes:", data);
      console.log("");
      console.log("📝 VÉRIFICATIONS:");
      console.log("   1. Vérifiez que Lambda est accessible");
      console.log("   2. Vérifiez les logs CloudWatch");
      console.log("   3. Vérifiez la configuration SendGrid");
      alert("❌ Erreur " + response.status + ": " + (data.error || data.message || "Erreur inconnue"));
    }
  } catch (error) {
    console.error("❌ ❌ ❌ EXCEPTION ❌ ❌ ❌");
    console.error("   Type:", error.name);
    console.error("   Message:", error.message);
    console.error("   Stack:", error.stack);
    console.log("");
    console.log("📝 VÉRIFICATIONS:");
    console.log("   1. Vérifiez votre connexion internet");
    console.log("   2. Vérifiez que l'API est accessible");
    alert("❌ Erreur réseau: " + error.message);
  }
  
  console.log("");
  console.log("============================================================");
  console.log("FIN DU TEST");
  console.log("============================================================");
}

// Exécuter automatiquement
testerSendGrid();
