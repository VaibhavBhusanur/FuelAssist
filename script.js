const API_BASE = "";
let rideStarted = false;

// Helper: Show notification
function showNotification(message, type = 'info') {
  const status = document.getElementById('status');
  const statusText = document.getElementById('statusText');
  
  statusText.textContent = message;
  status.className = `p-4 rounded-xl w-full max-w-md mb-6 ${
    type === 'error' ? 'bg-red-50 border border-red-200' : 
    type === 'success' ? 'bg-green-50 border border-green-200' : 
    'bg-blue-50 border border-blue-200'
  }`;
  
  statusText.className = `font-medium text-center ${
    type === 'error' ? 'text-red-800' : 
    type === 'success' ? 'text-green-800' : 
    'text-blue-800'
  }`;
  
  status.classList.remove('hidden');
  
  // Auto hide after 5 seconds
  setTimeout(() => {
    status.classList.add('hidden');
  }, 5000);
}

// Helper: Toggle loading state
function setLoading(element, loading) {
  if (loading) {
    element.classList.add('loading');
    element.disabled = true;
  } else {
    element.classList.remove('loading');
    element.disabled = false;
  }
}

// === Vehicle Selection ===
document.getElementById("vehicle").addEventListener("change", async () => {
  const vehicle = document.getElementById("vehicle").value;
  if (!vehicle) return;
  
  try {
    const res = await fetch(`/get_vehicle_capacity?vehicle=${vehicle}`);
    if (!res.ok) throw new Error("Failed to fetch capacity.");
    const data = await res.json();
    
    const vehicleName = vehicle === 'splendor2018' ? '2018 Splendor' : '2020 Activa';
    showNotification(`${vehicleName} selected. Tank capacity: ${data.capacity}L`, 'success');
  } catch (err) {
    showNotification("Could not fetch vehicle capacity.", 'error');
  }
});

// === Start Ride ===
document.getElementById("startRide").addEventListener("click", async () => {
  const vehicle = document.getElementById("vehicle").value;
  const fuel = document.getElementById("fuelInput").value;
  const startBtn = document.getElementById("startRide");
  const endBtn = document.getElementById("endRide");
  
  if (!vehicle) {
    showNotification("Please select a vehicle first.", 'error');
    return;
  }
  
  if (!fuel || fuel <= 0) {
    showNotification("Please enter a valid fuel amount.", 'error');
    return;
  }
  
  setLoading(startBtn, true);
  
  try {
    const res = await fetch(`/start_ride`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vehicle, fuel: parseFloat(fuel) })
    });
    
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || "Failed to start ride.");
    }
    
    const data = await res.json();
    
    rideStarted = true;
    startBtn.disabled = true;
    endBtn.disabled = false;
    
    const fuelLiters = data.fuel_in_liters;
    showNotification(`Ride started! Filled ${fuelLiters}L (₹${fuel}) in your ${vehicle === 'splendor2018' ? '2018 Splendor' : '2020 Activa'}.`, 'success');
    
    // Hide results from previous ride
    document.getElementById("results").classList.add("hidden");
    
  } catch (err) {
    showNotification(err.message, 'error');
  } finally {
    setLoading(startBtn, false);
  }
});

// === End Ride ===
document.getElementById("endRide").addEventListener("click", async () => {
  const startBtn = document.getElementById("startRide");
  const endBtn = document.getElementById("endRide");
  
  if (!rideStarted) {
    showNotification("No active ride found. Please start a ride first.", 'error');
    return;
  }
  
  setLoading(endBtn, true);
  
  try {
    const res = await fetch(`/end_ride`);
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || "Failed to end ride.");
    }
    
    const data = await res.json();
    
    // Update UI
    rideStarted = false;
    startBtn.disabled = false;
    endBtn.disabled = true;
    
    // Show results
    const results = document.getElementById("results");
    results.classList.remove("hidden");
    
    const vehicleName = data.vehicle === 'splendor2018' ? '2018 Splendor' : '2020 Activa';
    
    document.getElementById("vehicleInfo").textContent = `Vehicle: ${vehicleName}`;
    document.getElementById("fuelInfo").textContent = `Fuel Filled: ${data.fuel_in_liters}L (₹${data.fuel_filled_rs})`;
    document.getElementById("mileage").textContent = `Mileage: ${data.mileage} km/L`;
    document.getElementById("fuelUsed").textContent = `Fuel Used: ${data.fuel_used}L`;
    document.getElementById("fuelLeft").textContent = `Fuel Remaining: ${data.fuel_left}L`;
    document.getElementById("fuelPercent").textContent = `Fuel Level: ${data.fuel_percent}%`;
    
    const alertElement = document.getElementById("alert");
    alertElement.textContent = data.alert;
    alertElement.className = `font-bold ${data.fuel_percent < 25 ? 'text-red-600' : 'text-green-600'}`;
    
    showNotification(`Ride completed! You traveled ${data.distance}km with ${data.mileage} km/L mileage.`, 'success');
    
  } catch (err) {
    showNotification(err.message, 'error');
  } finally {
    setLoading(endBtn, false);
  }
});

// === Chatbot ===
function addChatMessage(sender, message, isUser = false) {
  const chatbox = document.getElementById("chatbox");
  const messageDiv = document.createElement("div");
  messageDiv.className = `chat-message ${isUser ? 'user-message' : 'bot-message'}`;
  messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatbox.appendChild(messageDiv);
  chatbox.scrollTop = chatbox.scrollHeight;
}

document.getElementById("sendBtn").addEventListener("click", sendChatMessage);
document.getElementById("chatInput").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    sendChatMessage();
  }
});

async function sendChatMessage() {
  const query = document.getElementById("chatInput").value.trim();
  if (!query) return;
  
  const sendBtn = document.getElementById("sendBtn");
  const chatInput = document.getElementById("chatInput");
  
  // Add user message
  addChatMessage("You", query, true);
  chatInput.value = "";
  
  setLoading(sendBtn, true);
  
  try {
    const res = await fetch(`/chatbot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    
    if (!res.ok) throw new Error("Chatbot API failed.");
    
    const data = await res.json();
    addChatMessage("Bot", data.answer);
    
  } catch (err) {
    addChatMessage("Bot", "Sorry, I couldn't process your request right now. Please try again.");
  } finally {
    setLoading(sendBtn, false);
  }
}

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("endRide").disabled = true;
  showNotification("Welcome! Select a vehicle and add fuel to start tracking your ride.", 'info');
});