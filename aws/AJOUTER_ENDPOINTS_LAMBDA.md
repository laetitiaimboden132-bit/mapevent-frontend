# 🔧 Ajouter les Endpoints Utilisateur au Backend Lambda

## ⚠️ Problème

**Le backend Lambda (`lambda-package/backend/main.py`) n'a PAS les endpoints :**
- `/api/user/likes`
- `/api/user/participate`
- `/api/user/favorites` (peut-être)
- `/api/user/agenda` (peut-être)

**Ces endpoints sont nécessaires pour que le frontend puisse appeler l'API.**

---

## 📋 Solution : Ajouter les Endpoints

### Étape 1 : Ajouter les Endpoints dans `lambda-package/backend/main.py`

**Ajoutez ces routes AVANT la ligne `return app` (vers la ligne 374) :**

```python
    # Routes utilisateur
    @app.route('/api/user/likes', methods=['POST'])
    def user_likes():
        """Gère les likes des utilisateurs pour les événements, bookings et services."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_id = data.get('itemId')
            item_type = data.get('itemMode')
            action = data.get('action') # 'add' or 'remove'

            if not all([user_id, item_id, item_type, action]):
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            # Assurer que l'utilisateur existe (ou le créer si c'est la première action)
            cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            conn.commit()

            if action == 'add':
                cursor.execute(
                    "INSERT INTO user_likes (user_id, item_type, item_id) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_type, item_id) DO NOTHING",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'added'}), 200
            elif action == 'remove':
                cursor.execute(
                    "DELETE FROM user_likes WHERE user_id = %s AND item_type = %s AND item_id = %s",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'removed'}), 200
            else:
                return jsonify({'error': 'Invalid action'}), 400
        except Exception as e:
            logger.error(f"Erreur user_likes: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/favorites', methods=['POST'])
    def user_favorites():
        """Gère les favoris des utilisateurs."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_id = data.get('itemId')
            item_type = data.get('itemMode')
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
                    "INSERT INTO user_favorites (user_id, item_type, item_id) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_type, item_id) DO NOTHING",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'added'}), 200
            elif action == 'remove':
                cursor.execute(
                    "DELETE FROM user_favorites WHERE user_id = %s AND item_type = %s AND item_id = %s",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'removed'}), 200
            else:
                return jsonify({'error': 'Invalid action'}), 400
        except Exception as e:
            logger.error(f"Erreur user_favorites: {e}")
            return jsonify({'error': str(e)}), 500

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

    @app.route('/api/user/agenda', methods=['POST'])
    def user_agenda():
        """Gère l'ajout/retrait d'éléments à l'agenda de l'utilisateur."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_id = data.get('itemId')
            item_type = data.get('itemMode')
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
                    "INSERT INTO user_agenda (user_id, item_type, item_id) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_type, item_id) DO NOTHING",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'added'}), 200
            elif action == 'remove':
                cursor.execute(
                    "DELETE FROM user_agenda WHERE user_id = %s AND item_type = %s AND item_id = %s",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'removed'}), 200
            else:
                return jsonify({'error': 'Invalid action'}), 400
        except Exception as e:
            logger.error(f"Erreur user_agenda: {e}")
            return jsonify({'error': str(e)}), 500
```

---

### Étape 2 : Créer le Nouveau Package Lambda

**Utilisez le script PowerShell :**

```powershell
cd C:\MapEventAI_NEW\frontend
.\aws\creer_package_lambda.ps1
```

**Ou manuellement :**

1. **Allez dans `lambda-package`**
2. **Créez un ZIP** avec tous les fichiers
3. **Nommez-le `lambda-deployment.zip`**

---

### Étape 3 : Uploader le Nouveau Package dans Lambda

1. **AWS Console** → **Lambda** → **mapevent-backend**
2. **Code** → **Upload from** → **.zip file**
3. **Sélectionnez `lambda-deployment.zip`**
4. **Cliquez sur Save**

---

### Étape 4 : Tester

1. **Rafraîchissez `test_api.html` (F5)**
2. **Cliquez sur "Test Likes"**
3. **Ça devrait fonctionner !**

---

## ✅ Vérification

**Après avoir ajouté les endpoints, vérifiez que :**
- ✅ Les routes sont dans `lambda-package/backend/main.py`
- ✅ Le package Lambda a été créé
- ✅ Le package a été uploadé dans Lambda
- ✅ L'API Gateway a les routes `/api/user/likes`, etc.
- ✅ L'API Gateway est déployée

---

## 🚨 Important

**Les tables de base de données doivent exister :**
- `users`
- `user_likes`
- `user_favorites`
- `user_participations`
- `user_agenda`

**Vérifiez dans `lambda-package/backend/database/schema.sql` qu'elles existent !**



