# 📖 EXPLICATION : Fonctionnalité "PARTICIPER"

## 🎯 Qu'est-ce que "Participer" ?

La fonctionnalité **"Participer"** permet à un utilisateur de s'inscrire à un événement. C'est l'équivalent d'un bouton "Je participe" ou "S'inscrire" sur un événement.

---

## 🔄 Comment ça fonctionne ?

### 1️⃣ **Dans l'interface utilisateur**

Quand un utilisateur clique sur le bouton **"🎟️ Participer"** dans la popup d'un événement :

```1325:1327:public/map_logic.js
      <button onclick="onAction('participate', 'event', ${ev.id})" class="pill small btn-main" style="flex:1;">
        ${currentUser.participating.includes('event:'+ev.id) ? '✅ ' + (t("registered") || "Inscrit") : '🎟️ ' + t("participate")}
      </button>
```

- **Avant le clic** : Le bouton affiche "🎟️ Participer"
- **Après le clic** : Le bouton affiche "✅ Inscrit"

---

### 2️⃣ **Dans le frontend (JavaScript)**

Quand l'utilisateur clique, la fonction `toggleParticipation()` est appelée :

```3508:3525:public/map_logic.js
// Toggle Participation
function toggleParticipation(type, id) {
  const key = `${type}:${id}`;
  const index = currentUser.participating.indexOf(key);
  
  if (index > -1) {
    currentUser.participating.splice(index, 1);
    showNotification("🚫 Participation annulée", "info");
  } else {
    currentUser.participating.push(key);
    // Ajouter aussi à l'agenda automatiquement
    if (!currentUser.agenda.includes(key)) {
      currentUser.agenda.push(key);
    }
    showNotification("✅ Participation confirmée ! Ajouté à votre agenda.", "success");
  }
  
  refreshMarkers();
}
```

**Ce qui se passe :**
- ✅ **Si l'utilisateur n'est PAS inscrit** :
  - L'événement est ajouté à `currentUser.participating[]`
  - L'événement est **automatiquement ajouté à l'agenda** aussi
  - Notification : "✅ Participation confirmée ! Ajouté à votre agenda."
  - Un appel API est fait vers `/api/user/participate` avec `action: "add"`

- ❌ **Si l'utilisateur EST déjà inscrit** :
  - L'événement est retiré de `currentUser.participating[]`
  - Notification : "🚫 Participation annulée"
  - Un appel API est fait vers `/api/user/participate` avec `action: "remove"`

---

### 3️⃣ **Dans le backend (API)**

L'endpoint `/api/user/participate` reçoit la requête :

```458:500:lambda-package/backend/main.py
    @app.route('/api/user/participate', methods=['POST'])
    def user_participate():
        """Gère la participation des utilisateurs aux événements."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_id = data.get('itemId')
            item_type = data.get('itemMode') # Principalement 'event'
            action = data.get('action') # 'add' or 'remove'

            if not all([user_id, item_id, item_type, action]):
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            conn.commit()

            if action == 'add':
                cursor.execute(
                    "INSERT INTO user_participations (user_id, item_type, item_id) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_type, item_id) DO NOTHING",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'added'}), 200
            elif action == 'remove':
                cursor.execute(
                    "DELETE FROM user_participations WHERE user_id = %s AND item_type = %s AND item_id = %s",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'removed'}), 200
            else:
                return jsonify({'error': 'Invalid action'}), 400
        except Exception as e:
            logger.error(f"Erreur user_participate: {e}")
            return jsonify({'error': str(e)}), 500
```

**Ce qui se passe :**
1. ✅ L'utilisateur est créé dans la table `users` s'il n'existe pas
2. ✅ Si `action = "add"` :
   - Une entrée est créée dans la table `user_participations`
   - Le compteur `participants` de l'événement est automatiquement incrémenté (via un trigger SQL)
3. ❌ Si `action = "remove"` :
   - L'entrée est supprimée de `user_participations`
   - Le compteur `participants` est automatiquement décrémenté

---

### 4️⃣ **Dans la base de données**

La table `user_participations` stocke toutes les participations :

```sql
-- Table des participations (inscriptions aux événements)
CREATE TABLE IF NOT EXISTS user_participations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'event' principalement
    item_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_type, item_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Exemple de données :**
```
user_id | item_type | item_id | created_at
--------|-----------|---------|------------
"123"   | "event"   | 42      | 2025-12-18 10:00:00
"123"   | "event"   | 15      | 2025-12-18 11:30:00
"456"   | "event"   | 42      | 2025-12-18 12:00:00
```

---

## 📊 Affichage dans l'interface

### Dans la popup de l'événement

Le nombre de participants est affiché :

```1312:1318:public/map_logic.js
  const statsRow = `
    <div style="display:flex;gap:12px;margin:8px 0;font-size:11px;color:var(--ui-text-muted);">
      <span>❤️ ${ev.likes || 0}</span>
      <span>💬 ${ev.comments || 0}</span>
      <span>👥 ${ev.participants || 0} ${t("participants") || "participants"}</span>
    </div>
  `;
```

### Dans le profil utilisateur

Le nombre total de participations est affiché :

```4622:4622:public/map_logic.js
          <div style="font-size:24px;font-weight:700;color:#8b5cf6;">${currentUser.participating.length}</div>
```

---

## 🔄 Différence avec "Agenda"

| Fonctionnalité | "Participer" | "Agenda" |
|----------------|--------------|----------|
| **But** | S'inscrire à un événement | Sauvegarder pour plus tard |
| **Compteur** | Incrémente `participants` | Pas de compteur |
| **Automatique** | Ajoute automatiquement à l'agenda | Action manuelle |
| **Visibilité** | Visible par les autres (statistiques) | Privé (utilisateur uniquement) |

**Note importante :** Quand un utilisateur clique sur "Participer", l'événement est **automatiquement ajouté à l'agenda** aussi !

---

## ✅ Résumé

1. **Clic sur "Participer"** → L'utilisateur s'inscrit à l'événement
2. **Sauvegarde en base** → L'inscription est stockée dans `user_participations`
3. **Compteur mis à jour** → Le nombre de participants de l'événement augmente
4. **Ajout à l'agenda** → L'événement est automatiquement ajouté à l'agenda de l'utilisateur
5. **Affichage** → Le bouton change en "✅ Inscrit" et le compteur de participants est mis à jour

---

## 🚀 Prochaine étape

Une fois la route `/api/user/participate` créée dans API Gateway, vous pourrez tester cette fonctionnalité dans l'application !



