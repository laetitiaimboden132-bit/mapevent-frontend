var API_BASE = window.API_BASE_URL || "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api";
var email = prompt("Email de test:");
if (!email) {
  console.log("Test annule");
} else {
  console.log("Envoi a: " + email);
  fetch(API_BASE + "/user/send-verification-code", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email: email, username: "Test User"})
  })
  .then(function(response) {
    console.log("Code HTTP: " + response.status);
    return response.text();
  })
  .then(function(text) {
    console.log("Reponse: " + text);
    try {
      var data = JSON.parse(text);
      console.log("Donnees:", data);
      if (data.dev_mode === true) {
        console.log("MODE DEV - Email NON envoye");
      } else if (data.message && data.message.indexOf("mode") !== -1) {
        console.log("MODE DEV - Email NON envoye");
      } else {
        console.log("EMAIL ENVOYE!");
      }
      if (data.code) {
        console.log("CODE DEV: " + data.code);
      }
    } catch (e) {
      console.error("Erreur parse JSON:", e);
      console.error("Texte brut:", text);
    }
  })
  .catch(function(error) {
    console.error("ERREUR:", error);
  });
}
