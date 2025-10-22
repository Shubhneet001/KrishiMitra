document.addEventListener('DOMContentLoaded', () => {
    // API Configuration
    const API_BASE_URL = 'http://localhost:8000';

    // Navbar Functionality
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Weather Functionality
    const locationInput = document.getElementById('locationInput');
    const updateLocationBtn = document.getElementById('updateLocationBtn');
    const weatherDisplay = document.getElementById('weatherDisplay');

    const fetchWeather = async (location = null) => {
        try {
            const url = location ? `${API_BASE_URL}/weather/${location}` : `${API_BASE_URL}/weather/`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Weather data not available.');
            }
            
            const data = await response.json();

            // Get today's icon from the forecast data (index 0)
            let iconHTML = '';
            if (data.forecast && data.forecast.length > 0) {
                const todayIconUrl = `https:${data.forecast[0].day.condition.icon}`;
                const todayConditions = data.forecast[0].day.condition.text;
                iconHTML = `<img src="${todayIconUrl}" alt="${todayConditions}" style="width: 60px; height: 60px;">`;
            }

            // Set Main Weather Display
            weatherDisplay.innerHTML = `
                <div class="weather-current">
                    ${iconHTML}
                    <div class="weather-info">
                        <h3>${data.temperature}°C</h3>
                        <p>${data.conditions} in ${data.location}</p>
                    </div>
                </div>
                
                <div class="weather-details-grid">
                    <div class="detail-item">
                        <span>Humidity</span>
                        <strong>${data.humidity}%</strong>
                    </div>
                    <div class="detail-item">
                        <span>Rainfall</span>
                        <strong>${data.rainfall} mm</strong>
                    </div>
                    <div class="detail-item">
                        <span>Wind</span>
                        <strong>${data.wind_speed} kph</strong>
                    </div>
                    <div class="detail-item">
                        <span>UV Index</span>
                        <strong>${data.uv_index}</strong>
                    </div>
                </div>
            `;
            
            // Save last successful location
            localStorage.setItem('userLocation', data.location);

        } catch (error) {
            console.error('Weather fetch error:', error);
            weatherDisplay.innerHTML = `<p>Could not fetch weather data. Please update your location.</p>`;
        }
    };


    updateLocationBtn.addEventListener('click', async () => {
        const location = locationInput.value.trim();
        if (!location) {
            alert('Please enter a location.');
            return;
        }
        updateLocationBtn.disabled = true;
        updateLocationBtn.textContent = 'Updating...';
        
        try {
            // Update location on backend
            await fetch(`${API_BASE_URL}/set-location/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ location: location })
            });
            // Fetch new weather data
            await fetchWeather(location);
        } catch (error) {
            console.error('Location update error:', error);
        } finally {
            updateLocationBtn.disabled = false;
            updateLocationBtn.textContent = 'Update Location';
            locationInput.value = '';
        }
    });

    // Fetch weather on page load with stored location
    fetchWeather(localStorage.getItem('userLocation'));

    // Tab Functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Universal Image Upload Handler
    const setupUploadArea = (type) => {
        const uploadArea = document.getElementById(`${type}Upload`);
        const input = document.getElementById(`${type}Input`);
        const preview = document.getElementById(`${type}Preview`);
        const image = document.getElementById(`${type}Image`);
        const analyzeBtn = document.getElementById(`${type}Analyze`);
        const result = document.getElementById(`${type}Result`);
        const resultContent = document.getElementById(`${type}ResultContent`);
        let file = null;

        const handleFile = (uploadedFile) => {
            if (!uploadedFile.type.startsWith('image/')) {
                alert('Please upload an image file.');
                return;
            }
            if (uploadedFile.size > 5 * 1024 * 1024) {
                alert('File size must be less than 5MB.');
                return;
            }
            file = uploadedFile;
            const reader = new FileReader();
            reader.onload = (e) => {
                image.src = e.target.result;
                preview.classList.add('active');
                result.style.display = 'none';
            };
            reader.readAsDataURL(file);
        };

        uploadArea.addEventListener('click', () => input.click());
        input.addEventListener('change', (e) => e.target.files.length > 0 && handleFile(e.target.files[0]));
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            e.dataTransfer.files.length > 0 && handleFile(e.dataTransfer.files[0]);
        });
        
        analyzeBtn.addEventListener('click', async () => {
            if (!file) return;

            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="loader"></span> Analyzing...';
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch(`${API_BASE_URL}/${type}-prediction/`, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.success) {
                    if (type === 'disease') {
                        resultContent.innerHTML = `
                            <p><strong>Plant:</strong> ${data.plant}</p>
                            <p><strong>Disease:</strong> ${data.disease}</p>
                            <p><strong>Status:</strong> ${data.is_healthy ? '<span style="color: green;">✓ Healthy</span>' : '<span style="color: red;">⚠ Disease Detected</span>'}</p>
                            <p><strong>Confidence:</strong> ${data.confidence}%</p>
                            <div class="confidence-bar"><div class="confidence-fill" style="width: ${data.confidence}%"></div></div>
                            ${!data.is_healthy ? `<button class="btn get-solution-btn" data-problem="${data.disease}">Get Solution</button>` : ''}
                        `;
                    } else if (type === 'pest') {
                        resultContent.innerHTML = `
                            <p><strong>Detected Pest:</strong> ${data.predicted_pest}</p>
                            <p><strong>Confidence:</strong> ${data.confidence}%</p>
                            <div class="confidence-bar"><div class="confidence-fill" style="width: ${data.confidence}%"></div></div>
                            <button class="btn get-solution-btn" data-problem="${data.predicted_pest}">Get Solution</button>
                        `;
                    }
                } else {
                    resultContent.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }
            } catch (error) {
                console.error(`${type} prediction error:`, error);
                resultContent.innerHTML = `<p style="color: red;">Error connecting to server. Please try again.</p>`;
            }
            result.style.display = 'block';
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/></svg> Analyze Image`;
        });
    };

    setupUploadArea('disease');
    setupUploadArea('pest');

    // Get Solution Button Functionality
    document.querySelector('.upload-container').addEventListener('click', (e) => {
        if (e.target && e.target.matches('.get-solution-btn')) {
            const problem = e.target.getAttribute('data-problem');
            const query = `What are the treatment and control methods for ${problem}?`;
            
            // Open chatbot and send message
            chatbotContainer.classList.add('active');
            chatbotToggle.style.display = 'none';
            chatInput.value = query;
            sendMessage();
        }
    });

    // Chatbot Functionality
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotContainer = document.getElementById('chatbotContainer');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatbotClear = document.getElementById('chatbotClear');
    const chatbotMessages = document.getElementById('chatbotMessages');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');

    chatbotToggle.addEventListener('click', () => {
        chatbotContainer.classList.add('active');
        chatbotToggle.style.display = 'none';
        chatInput.focus();
    });

    chatbotClose.addEventListener('click', () => {
        chatbotContainer.classList.remove('active');
        chatbotToggle.style.display = 'flex';
    });

    const addMessage = (message, isUser = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        messageDiv.innerHTML = isUser ? `<p>${message}</p>` : message;
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    };

    const addTypingIndicator = () => {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatbotMessages.appendChild(typingDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    };

    const removeTypingIndicator = () => {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) typingIndicator.remove();
    };

    const sendMessage = async () => {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        chatInput.value = '';
        chatSend.disabled = true;
        addTypingIndicator();

        try {
            const response = await fetch(`${API_BASE_URL}/chatbot/?query=${encodeURIComponent(message)}`);
            const data = await response.json();
            removeTypingIndicator();
            if (data.response) {
                addMessage(data.response);
            } else {
                addMessage('<p>Sorry, I couldn\'t process your request.</p>');
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            removeTypingIndicator();
            addMessage(`<p style="color: red;">Could not connect to the AI assistant.</p>`);
        }
        chatSend.disabled = false;
        chatInput.focus();
    };

    const clearChat = async () => {
        try {
            await fetch(`${API_BASE_URL}/clear-memory/`, { method: 'POST' });
        } catch (error) {
            console.error("Failed to clear backend memory:", error);
        }
        chatbotMessages.innerHTML = `<div class="message bot"><p>Hello! I'm Krishi Mitra. How can I help you today?</p></div>`;
    };

    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage()));
    chatbotClear.addEventListener('click', clearChat);
});