// Show selected section
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('section').forEach(section => {
        section.classList.remove('active');
    });
    // Show the selected section
    document.getElementById(sectionId).classList.add('active');
}

// Preview the selected image
function previewImage(inputId, previewId) {
    const fileInput = document.getElementById(inputId);
    const previewDiv = document.getElementById(previewId);
    
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewDiv.innerHTML = '';
            const img = document.createElement('img');
            img.src = e.target.result;
            previewDiv.appendChild(img);
        }
        
        reader.readAsDataURL(fileInput.files[0]);
    }
}

// Call disease prediction API
async function predictDisease() {
    const fileInput = document.getElementById('diseaseImage');
    const file = fileInput.files[0];
    if (!file) return alert("Please upload an image!");

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Show loading state
        document.getElementById("disease-name").innerText = "Processing...";
        document.getElementById("disease-confidence-score").innerText = "--";
        
        const res = await fetch('http://127.0.0.1:8000/disease-prediction/', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        document.getElementById("disease-name").innerText = data.disease || "Unknown";
        document.getElementById("disease-confidence-score").innerText = data.confidence;
    } catch (error) {
        console.error("Disease prediction failed:", error);
        document.getElementById("disease-name").innerText = "Error";
        document.getElementById("disease-confidence-score").innerText = "--";
        alert("Error predicting disease. Please try again.");
    }
}

// Call pest prediction API
async function predictPest() {
    const fileInput = document.getElementById('pestImage');
    const file = fileInput.files[0];
    if (!file) return alert("Please upload an image!");

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Show loading state
        document.getElementById("pest-name").innerText = "Processing...";
        document.getElementById("pest-confidence-score").innerText = "--";
        
        const res = await fetch('http://127.0.0.1:8000/pest-prediction/', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        document.getElementById("pest-name").innerText = data.pest || "Unknown";
        document.getElementById("pest-confidence-score").innerText = data.confidence + "%";
    } catch (error) {
        console.error("Pest prediction failed:", error);
        document.getElementById("pest-name").innerText = "Error";
        document.getElementById("pest-confidence-score").innerText = "--";
        alert("Error predicting pest. Please try again.");
    }
}

// Get solution for detected issues by opening chatbot and sending query
function getSolution(type) {
    let query = "";
    
    if (type === 'disease') {
        const diseaseName = document.getElementById("disease-name").innerText;
        if (diseaseName === "--" || diseaseName === "Unknown" || diseaseName === "Processing..." || diseaseName === "Error") {
            alert("Please predict a disease first!");
            return;
        }
        query = `What is the solution for ${diseaseName} disease in plants?`;
    } else if (type === 'pest') {
        const pestName = document.getElementById("pest-name").innerText;
        if (pestName === "--" || pestName === "Unknown" || pestName === "Processing..." || pestName === "Error") {
            alert("Please predict a pest first!");
            return;
        }
        query = `How to control ${pestName} pest in crops?`;
    }
    
    // Open chatbot if it's not already open
    const chatbox = document.getElementById("chatbot-container");
    if (!chatbox.classList.contains("open")) {
        toggleChatbot();
    }
    
    // Set the query in the input field and send it
    document.getElementById("chatbot-input").value = query;
    sendChat();
}

// Toggle chatbot visibility
function toggleChatbot() {
    const chatbox = document.getElementById("chatbot-container");
    const toggleBtn = document.getElementById("chatbot-toggle");

    if (chatbox.classList.contains("open")) {
        chatbox.classList.remove("open");
        chatbox.style.display = "none";
        toggleBtn.style.display = "flex";
    } else {
        chatbox.classList.add("open");
        chatbox.style.display = "flex";
        toggleBtn.style.display = "none";
    }
}

// Append message to chatbot
function appendMessage(message, sender = "bot") {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");

    if (sender === "bot") {
        // Clean message if it has HTML tags
        const cleanedMessage = message.slice(7, -3);
        messageDiv.innerHTML = cleanedMessage;
    } else {
        messageDiv.textContent = message;
    }

    document.getElementById("chatbot-messages").appendChild(messageDiv);
    document.getElementById("chatbot-messages").scrollTop = document.getElementById("chatbot-messages").scrollHeight;
}

// Send chat to FastAPI
async function sendChat() {
    const input = document.getElementById("chatbot-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    input.value = "";

    try {
        // Show typing indicator
        const typingDiv = document.createElement("div");
        typingDiv.classList.add("message", "bot-message", "typing-indicator");
        typingDiv.textContent = "Thinking...";
        document.getElementById("chatbot-messages").appendChild(typingDiv);
        
        const res = await fetch(`http://127.0.0.1:8000/chatbot/?query=${encodeURIComponent(message)}`);
        const data = await res.json();
        
        // Remove typing indicator
        document.getElementById("chatbot-messages").removeChild(typingDiv);
        
        appendMessage(data.response, "bot");
    } catch (error) {
        console.error("Chat error:", error);
        appendMessage("Sorry, I couldn't process that request. Please try again later.", "bot");
    }
}

// Location handling
let userLocation = null;

// Show the location modal
function openLocationModal() {
    document.getElementById("location-modal").style.display = "block";
}

// Hide the location modal
function closeLocationModal() {
    document.getElementById("location-modal").style.display = "none";
}

// Submit location to API
async function submitLocation() {
    const location = document.getElementById("modal-location-input").value.trim();
    if (!location) {
        alert("Please enter a location.");
        return;
    }

    try {
        const res = await fetch(`http://127.0.0.1:8000/set-location/?location=${encodeURIComponent(location)}`, {
            method: "PUT"
        });
        const data = await res.json();
        
        // Update user location and show confirmation
        userLocation = location;
        alert(data.message || `Location set to ${location}!`);
        closeLocationModal();
    } catch (err) {
        console.error("Location error:", err);
        alert("Failed to set location. Please try again.");
    }
}

// Close modal if user clicks outside the modal box
window.onclick = function(event) {
    const modal = document.getElementById("location-modal");
    if (event.target === modal) {
        closeLocationModal();
    }
};

// Add event listener for Enter key in chatbot input
document.getElementById("chatbot-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendChat();
    }
});

// Handle login/signup placeholders
function showLogin() {
    alert("Login feature coming soon!");
}

function showSignup() {
    alert("Signup feature coming soon!");
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Make sure home section is shown by default
    showSection('home');
});