// Simple voice input component
class VoiceInput {
    constructor(inputElement) {
        this.inputElement = inputElement;
        this.recognition = new webkitSpeechRecognition();
        this.setupRecognition();
        this.createMicButton();
    }

    setupRecognition() {
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            this.inputElement.value = text;
            this.micButton.classList.remove('listening');
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.micButton.classList.remove('listening');
        };
    }

    createMicButton() {
        this.micButton = document.createElement('button');
        this.micButton.innerHTML = '🎤'; // Microphone emoji
        this.micButton.className = 'mic-button';
        this.micButton.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            transition: background-color 0.3s;
        `;

        this.micButton.addEventListener('click', () => this.toggleRecognition());
        
        // Insert mic button next to input
        this.inputElement.parentElement.style.position = 'relative';
        this.inputElement.style.paddingRight = '40px';
        this.inputElement.parentElement.appendChild(this.micButton);
    }

    toggleRecognition() {
        if (this.micButton.classList.contains('listening')) {
            this.recognition.stop();
            this.micButton.classList.remove('listening');
        } else {
            this.recognition.start();
            this.micButton.classList.add('listening');
        }
    }
}

// Add styles
const style = document.createElement('style');
style.textContent = `
    .mic-button:hover {
        background-color: rgba(0,0,0,0.1);
    }
    .mic-button.listening {
        background-color: #ff4444;
        color: white;
    }
`;
document.head.appendChild(style);

// Initialize voice input on chat input field
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.querySelector('.chat-input');
    if (chatInput) {
        new VoiceInput(chatInput);
    }
});
