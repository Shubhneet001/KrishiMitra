const backendBaseURL = 'http://127.0.0.1:8000'

function showSection(sectionId) {
    document.querySelectorAll('section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}

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

async function predictDisease() {
    const fileInput = document.getElementById('diseaseImage');
    const file = fileInput.files[0];
    if (!file) return alert("Please upload an image!");

    const formData = new FormData();
    formData.append('file', file);

    try {
        document.getElementById("disease-name").innerText = "Processing...";
        document.getElementById("disease-confidence-score").innerText = "--";
        
        const res = await fetch(`${backendBaseURL}/disease-prediction/`, {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        const plant_name = data.disease.replace(/__+/, ',').replace(/_/g, ' ').split(',')[0].trim();
        const disease_name = data.disease.replace(/__+/, ',').replace(/_/g, ' ').split(',')[1].trim();
        document.getElementById("plant-name").innerText = plant_name || "Unknown";
        document.getElementById("disease-name").innerText = disease_name || "Unknown";
        document.getElementById("disease-confidence-score").innerText = data.confidence;
    } catch (error) {
        console.error("Disease prediction failed:", error);
        document.getElementById("disease-name").innerText = "Error";
        document.getElementById("disease-confidence-score").innerText = "--";
        alert("Error predicting disease. Please try again.");
    }
}

async function predictPest() {
    const fileInput = document.getElementById('pestImage');
    const file = fileInput.files[0];
    if (!file) return alert("Please upload an image!");

    const formData = new FormData();
    formData.append('file', file);

    try {
        document.getElementById("pest-name").innerText = "Processing...";
        document.getElementById("pest-confidence-score").innerText = "--";
        
        const res = await fetch(`${backendBaseURL}/pest-prediction/`, {
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

function getSolution(type) {
    let query = "";
    
    if (type === 'disease') {
        const plantName = document.getElementById("plant-name").innerText;
        const diseaseName = document.getElementById("disease-name").innerText;
        if (diseaseName === "--" || diseaseName === "Unknown" || diseaseName === "Processing..." || diseaseName === "Error") {
            alert("Please predict a disease first!");
            return;
        }
        query = `My ${plantName} plant has ${diseaseName} disease, what's the solution?`;
    } else if (type === 'pest') {
        const pestName = document.getElementById("pest-name").innerText;
        if (pestName === "--" || pestName === "Unknown" || pestName === "Processing..." || pestName === "Error") {
            alert("Please predict a pest first!");
            return;
        }
        query = `How to control ${pestName} pest in crops?`;
    }
    
    const chatbox = document.getElementById("chatbot-container");
    if (!chatbox.classList.contains("open")) {
        toggleChatbot();
    }
    
    document.getElementById("chatbot-input").value = query;
    sendChat();
}

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

function appendMessage(message, sender = "bot") {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");

    if (sender === "bot") {
        const cleanedMessage = message.slice(7, -3);
        messageDiv.innerHTML = cleanedMessage;
    } else {
        messageDiv.textContent = message;
    }

    document.getElementById("chatbot-messages").appendChild(messageDiv);
    document.getElementById("chatbot-messages").scrollTop = document.getElementById("chatbot-messages").scrollHeight;
}

async function sendChat() {
    const input = document.getElementById("chatbot-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    input.value = "";

    try {
        const typingDiv = document.createElement("div");
        typingDiv.classList.add("message", "bot-message", "typing-indicator");
        typingDiv.textContent = "Thinking...";
        document.getElementById("chatbot-messages").appendChild(typingDiv);
        
        const res = await fetch(`${backendBaseURL}/chatbot/?query=${encodeURIComponent(message)}`);
        const data = await res.json();
        
        document.getElementById("chatbot-messages").removeChild(typingDiv);
        
        appendMessage(data.response, "bot");
    } catch (error) {
        console.error("Chat error:", error);
        appendMessage("Sorry, I couldn't process that request. Please try again later.", "bot");
    }
}

let userLocation = null;
function openLocationModal() {
    document.getElementById("location-modal").style.display = "block";
}

function closeLocationModal() {
    document.getElementById("location-modal").style.display = "none";
}

async function submitLocation() {
    const location = document.getElementById("modal-location-input").value.trim();
    if (!location) {
        alert("Please enter a location.");
        return;
    }

    try {
        const res = await fetch(`${backendBaseURL}/set-location/?location=${encodeURIComponent(location)}`, {
            method: "PUT"
        });
        const data = await res.json();
        
        userLocation = location;
        alert(data.message || `Location set to ${location}!`);
        closeLocationModal();
    } catch (err) {
        console.error("Location error:", err);
        alert("Failed to set location. Please try again.");
    }
}

window.onclick = function(event) {
    const modal = document.getElementById("location-modal");
    if (event.target === modal) {
        closeLocationModal();
    }
};

document.getElementById("chatbot-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendChat();
    }
});

function showLogin() {
    alert("Login feature coming soon!");
}

function showSignup() {
    alert("Signup feature coming soon!");
}

document.addEventListener('DOMContentLoaded', function() {
    showSection('home');
});