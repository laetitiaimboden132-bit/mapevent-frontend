// Version finale - Copiez TOUT dans la console (F12)

(function() {
  var API_BASE = window.API_BASE_URL || "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api";
  
  console.log("========================================");
  console.log("TEST SENDGRID");
  console.log("========================================");
  
  var email = prompt("Entrez votre email de test:");
  if (!email) {
    console.log("Test annule");
    return;
  }
  
  console.log("Email:", email);
  console.log("API:", API_BASE);
  console.log("Envoi en cours...");
  
  fetch(API_BASE + "/user/send-verification-code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: email,
      username: "Test User"
    })
  })
  .then(function(response) {
    console.log("Code HTTP:", response.status);
    return response.text();
  })
  .then(function(text) {
    console.log("Reponse brute:", text);
    var data = JSON.parse(text);
    console.log("Donnees:", data);
    
    if (data.dev_mode === true || (data.message && data.message.indexOf("mode") !== -1)) {
      console.log("MODE DEV - Email NON envoye");
      alert("MODE DEV - SendGrid non configure");
    } else {
      console.log("EMAIL ENVOYE!");
      alert("Email envoye a " + email);
    }
    
    if (data.code) {
      console.log("CODE DEV:", data.code);
      alert("CODE: " + data.code);
    }
  })
  .catch(function(error) {
    console.error("ERREUR:", error);
    alert("Erreur: " + error.message);
  });
})();
