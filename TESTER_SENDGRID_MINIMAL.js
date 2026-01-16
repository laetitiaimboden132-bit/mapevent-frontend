var API_BASE = window.API_BASE_URL || "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api";
var email = prompt("Email de test:");
if (email) {
  fetch(API_BASE + "/user/send-verification-code", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email: email, username: "Test User"})
  })
  .then(function(r) { return r.text(); })
  .then(function(t) {
    console.log("Reponse:", t);
    var d = JSON.parse(t);
    console.log("Donnees:", d);
    if (d.dev_mode) console.log("MODE DEV");
    if (d.code) console.log("CODE:", d.code);
  })
  .catch(function(e) { console.error("Erreur:", e); });
}
