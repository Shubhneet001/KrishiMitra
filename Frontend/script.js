// Show selected section
function showSection(sectionId) {
    document.querySelectorAll('section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}

// Call disease prediction API
async function predictDisease() {
    const fileInput = document.getElementById('plantImage');
    const file = fileInput.files[0];
    if (!file) return alert("Please upload an image!");

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('http://127.0.0.1:8000/disease-prediction/', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        document.getElementById("disease-name").innerText = data.disease || "Unknown";
        document.getElementById("confidence-score").innerText = data.confidence + "%";
    } catch (error) {
        console.error("Prediction failed:", error);
        alert("Error predicting disease.");
    }
}

// Dummy feature
function consultExpert() {
    alert("Consulting an expert... (Feature coming soon)");
}

function toggleChatbot() {
    const chatbox = document.getElementById("chatbot-container");
    const toggleBtn = document.getElementById("chatbot-toggle");

    const isOpen = chatbox.classList.contains("open");

    if (isOpen) {
        chatbox.classList.remove("open");
        toggleBtn.style.display = "block";
    } else {
        chatbox.classList.add("open");
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


// Send chat to FastAPI
async function sendChat() {
    const input = document.getElementById("chatbot-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    input.value = "";

    try {
        const res = await fetch(`http://127.0.0.1:8000/chatbot/?query=${encodeURIComponent(message)}`);
        const data = await res.json();
        appendMessage(data.response, "bot");
    } catch (error) {
        appendMessage("Sorry, I couldn’t process that.", "bot");
    }
}

let userLocation = null;

// Show the modal
function openLocationModal() {
    document.getElementById("location-modal").style.display = "block";
}

// Hide the modal
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
        alert(data.message || "Location updated!");
        closeLocationModal();
    } catch (err) {
        console.error(err);
        alert("Failed to set location.");
    }
}

// Close modal if user clicks outside the modal box
window.onclick = function (event) {
    const modal = document.getElementById("location-modal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
};


// Dummy login/signup
function showLogin() {
    alert("Login feature coming soon!");
}
function showSignup() {
    alert("Signup feature coming soon!");
}
