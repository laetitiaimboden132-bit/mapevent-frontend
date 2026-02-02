# Test direct de la fonction

Copiez-collez ce code dans la console (F12) :

```javascript
// Test 1 : Vérifier si la fonction existe
console.log('1. openPublishModal existe:', typeof openPublishModal);
console.log('2. openPublishModal:', openPublishModal);

// Test 2 : Vérifier currentUser
console.log('3. currentUser:', currentUser);
console.log('4. currentUser.isLoggedIn:', currentUser?.isLoggedIn);

// Test 3 : Appeler la fonction avec try/catch
try {
  console.log('5. Appel openPublishModal...');
  openPublishModal();
  console.log('6. openPublishModal appelé sans erreur');
} catch (e) {
  console.error('7. ERREUR:', e);
}

// Test 4 : Vérifier les éléments du modal
setTimeout(() => {
  const backdrop = document.getElementById("publish-modal-backdrop");
  const inner = document.getElementById("publish-modal-inner");
  console.log('8. backdrop:', backdrop);
  console.log('9. inner:', inner);
  if (backdrop) {
    console.log('10. backdrop display:', getComputedStyle(backdrop).display);
  }
}, 500);
```
