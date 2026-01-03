// public/js/api.js

const API_BASE_URL = "/api"; // à adapter si nécessaire

// --------- UTILS GÉNÉRIQUES ---------

async function apiPost(path, payload) {
  const url = `${API_BASE_URL}${path}`;
  console.log("[API POST]", url, payload);

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status} - ${text}`);
    }

    return await res.json();
  } catch (err) {
    console.error("[API ERROR]", err);
    alert("Erreur lors de l'envoi des données. Réessaie plus tard.");
    return null;
  }
}

async function apiGet(path) {
  const url = `${API_BASE_URL}${path}`;
  console.log("[API GET]", url);

  try {
    const res = await fetch(url);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status} - ${text}`);
    }
    return await res.json();
  } catch (err) {
    console.error("[API ERROR]", err);
    alert("Erreur lors du chargement des données. Réessaie plus tard.");
    return null;
  }
}

// --------- EVENTS ---------

async function publishEvent(eventData) {
  return apiPost("/events/publish", eventData);
}

async function fetchEvents() {
  return apiGet("/events");
}

// --------- BOOKINGS ---------

async function publishBooking(bookingData) {
  return apiPost("/bookings/publish", bookingData);
}

async function fetchBookings() {
  return apiGet("/bookings");
}

// --------- SERVICES ---------

async function publishService(serviceData) {
  return apiPost("/services/publish", serviceData);
}

async function fetchServices() {
  return apiGet("/services");
}
