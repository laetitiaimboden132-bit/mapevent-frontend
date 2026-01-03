# 🔔 Système de Notifications pour Alarmes

## 📋 Logique Implémentée

### 1. **Limites SMS**
- **Gratuit** : 0 SMS
- **events-explorer** : 10 SMS/mois
- **events-alerts-pro** : 10 SMS/mois
- **full-premium (25.-)** : **Illimité**

### 2. **Limites Email**
- **Tous les abonnements** : **Illimité**

### 3. **Méthodes de Notification**
L'utilisateur peut choisir :
- ✅ Email uniquement
- ✅ SMS uniquement
- ✅ Email + SMS (les deux)

### 4. **Compteur SMS Mensuel**
- Le compteur `currentUser.smsNotifications` doit être réinitialisé chaque mois
- Vérification avant chaque envoi SMS : `canSendSMS()`

### 5. **Déclenchement des Alarmes**
- Les alarmes se déclenchent selon le `timeBefore` configuré
- Si SMS : Vérifier `canSendSMS()` avant d'envoyer
- Si Email : Toujours autorisé (illimité)

---

## 🔧 Fonctions à Implémenter

### `sendAlarmNotification(alarm, method)`
Envoie une notification (SMS ou Email) pour une alarme.

### `checkAndTriggerAlarms()`
Vérifie toutes les alarmes et déclenche celles qui doivent être envoyées.

### `resetMonthlySMSCounter()`
Réinitialise le compteur SMS au début de chaque mois.

---

## 📝 Structure des Alarmes

```javascript
{
  id: "alarm-123",
  alertId: "alert-456",
  eventId: "789",
  favoriteId: "123",
  favoriteName: "Nom du favori",
  favoriteMode: "event",
  timeBefore: {
    value: 1,
    unit: "days" // "hours", "days", "weeks"
  },
  notificationMethod: "email" | "sms" | "both",
  createdAt: "2025-01-15T10:00:00Z",
  triggered: false
}
```

---

## ⚠️ Important

- Les alarmes ne fonctionnent **QUE** pour les alertes **non floutées**
- Si une alerte devient floue, son alarme est automatiquement supprimée
- Les alarmes sont vérifiées périodiquement (ex: toutes les heures)



