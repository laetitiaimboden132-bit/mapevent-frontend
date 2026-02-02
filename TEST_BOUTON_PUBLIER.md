# Test du bouton Publier

## Test 1 : Vérifier si le bouton existe

Copiez-collez ce code dans la console (F12) :

```javascript
console.log('=== TEST 1 : Existence du bouton ===');
const btn = document.getElementById("map-publish-btn");
if (btn) {
  console.log('✅ Bouton trouvé !');
  console.log('Parent:', btn.parentElement?.tagName);
  console.log('Visible:', btn.offsetParent !== null);
} else {
  console.log('❌ Bouton NON trouvé');
}
```

## Test 2 : Vérifier la position

```javascript
console.log('=== TEST 2 : Position ===');
const btn = document.getElementById("map-publish-btn");
if (btn) {
  const rect = btn.getBoundingClientRect();
  console.log('Position:', {
    x: rect.x,
    y: rect.y,
    width: rect.width,
    height: rect.height,
    visible: rect.width > 0 && rect.height > 0
  });
  console.log('Dans la fenêtre:', rect.x >= 0 && rect.y >= 0 && rect.x < window.innerWidth && rect.y < window.innerHeight);
}
```

## Test 3 : Forcer l'affichage

```javascript
console.log('=== TEST 3 : Forcer l\'affichage ===');
const btn = document.getElementById("map-publish-btn");
if (btn) {
  btn.style.display = 'block';
  btn.style.visibility = 'visible';
  btn.style.opacity = '1';
  btn.style.zIndex = '9999';
  btn.style.position = 'fixed';
  btn.style.top = '80px';
  btn.style.right = '20px';
  console.log('✅ Styles forcés');
}
```

## Test 4 : Tester le clic

```javascript
console.log('=== TEST 4 : Test clic ===');
const btn = document.getElementById("map-publish-btn");
if (btn) {
  btn.onclick = function() {
    console.log('✅ Clic détecté via onclick');
    if (typeof openPublishModal === 'function') {
      openPublishModal();
    } else {
      console.error('❌ openPublishModal n\'existe pas');
    }
  };
  console.log('✅ onclick défini');
  
  // Tester le clic
  btn.click();
}
```
