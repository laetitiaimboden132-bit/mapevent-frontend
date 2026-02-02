(function() {
    console.log("🛠️ Patch de secours MapEvent activé...");

    function patchAction() {
        // 1. On cherche spécifiquement le lien qui contient "Publier"
        const topbarItems = document.querySelectorAll('.topbar-item');
        let btnPublier = Array.from(topbarItems).find(el => el.textContent.includes("Publier"));

        if (btnPublier) {
            console.log("✅ Bouton Publier trouvé !");
            
            // On écrase l'ancien onclick qui bugge
            btnPublier.onclick = null; 
            
            btnPublier.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log("🚀 Clic forcé !");

                // 2. On affiche le formulaire (dans ton HTML c'est la section 'publish-section')
                const section = document.querySelector('.publish-section');
                if (section) {
                    section.style.display = 'block';
                    section.style.visibility = 'visible';
                    section.style.zIndex = '2000';
                    console.log("✨ Formulaire affiché !");
                } else {
                    console.error("❌ Impossible de trouver la 'publish-section'");
                }
            });
        }
    }

    // On lance le patch après 1 seconde pour être sûr que map_logic a fini de charger
    setTimeout(patchAction, 1000);
})();