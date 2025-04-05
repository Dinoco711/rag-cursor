/**
 * Nexobotics Chatbot Widget
 * 
 * This script creates a customizable chatbot widget that can be added to any website.
 * It connects to the Nexobotics RAG Chatbot API to provide customer service answers.
 */

class NexoboticsChat {
    constructor(config) {
        // Default configuration
        this.config = {
            serverUrl: config.serverUrl || 'http://localhost:5000/api/chat',
            position: config.position || 'bottom-right',
            initialMessage: config.initialMessage || 'How can I assist you today?',
            logoUrl: config.logoUrl || 'https://placehold.co/200x200?text=N',
            title: config.title || 'Nexobotics Support',
            placeholder: config.placeholder || 'Type your message here...',
            primaryColor: config.primaryColor || '#0078d7',
            secondaryColor: config.secondaryColor || '#f5f5f5',
            textColor: config.textColor || '#333333',
            showStarterQuestions: config.showStarterQuestions !== undefined ? config.showStarterQuestions : true,
            starterQuestions: config.starterQuestions || [
                'What services do you offer?',
                'How can I contact support?',
                'What are your business hours?'
            ]
        };

        // Event handlers
        this.eventHandlers = {
            open: [],
            close: [],
            messageSent: [],
            responseReceived: [],
            error: []
        };

        // Chat state
        this.isOpen = false;
        this.sessionId = this._generateSessionId();
        this.messages = [];

        // Create UI
        this._createStyles();
        this._createChatWidget();

        // Add event listeners
        this._setupEventListeners();

        // Add initial message
        if (this.config.initialMessage) {
            this._addBotMessage(this.config.initialMessage);
        }
    }

    // Public methods

    /**
     * Open the chat widget
     */
    open() {
        if (!this.isOpen) {
            document.querySelector('.nexobotics-chat-container').classList.add('open');
            document.querySelector('.nexobotics-chat-button').classList.add('hidden');
            this.isOpen = true;
            this._triggerEvent('open');
            
            // Scroll to bottom
            const chatMessages = document.querySelector('.nexobotics-chat-messages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    /**
     * Close the chat widget
     */
    close() {
        if (this.isOpen) {
            document.querySelector('.nexobotics-chat-container').classList.remove('open');
            document.querySelector('.nexobotics-chat-button').classList.remove('hidden');
            this.isOpen = false;
            this._triggerEvent('close');
        }
    }

    /**
     * Send a message to the chatbot
     * @param {string} message - The message to send
     */
    sendMessage(message) {
        if (!message.trim()) return;

        // Add user message to UI
        this._addUserMessage(message);
        
        // Clear input field
        document.querySelector('.nexobotics-chat-input').value = '';
        
        // Trigger event
        this._triggerEvent('messageSent', message);
        
        // Send to API
        this._sendMessageToAPI(message);
    }

    /**
     * Register an event handler
     * @param {string} event - The event to listen for
     * @param {function} callback - The callback function
     */
    on(event, callback) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].push(callback);
        }
    }

    /**
     * Clear the chat session
     */
    clearSession() {
        this.messages = [];
        document.querySelector('.nexobotics-chat-messages').innerHTML = '';
        
        // Add initial message
        if (this.config.initialMessage) {
            this._addBotMessage(this.config.initialMessage);
        }
        
        // Clear session on server
        fetch(`${this.config.serverUrl.replace('/chat', '/clear-session')}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: this.sessionId })
        }).catch(error => {
            console.error('Error clearing session:', error);
        });
    }

    // Private methods

    _createStyles() {
        const styleEl = document.createElement('style');
        styleEl.textContent = `
            .nexobotics-chat-button {
                position: fixed;
                ${this.config.position === 'bottom-right' ? 'right: 20px; bottom: 20px;' : 'left: 20px; bottom: 20px;'}
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background-color: ${this.config.primaryColor};
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                cursor: pointer;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }
            
            .nexobotics-chat-button:hover {
                transform: scale(1.05);
            }
            
            .nexobotics-chat-button.hidden {
                display: none;
            }
            
            .nexobotics-chat-button-icon {
                width: 30px;
                height: 30px;
                fill: white;
            }
            
            .nexobotics-chat-container {
                position: fixed;
                ${this.config.position === 'bottom-right' ? 'right: 20px; bottom: 20px;' : 'left: 20px; bottom: 20px;'}
                width: 370px;
                height: 500px;
                max-height: calc(100vh - 40px);
                border-radius: 10px;
                background-color: white;
                box-shadow: 0 5px 40px rgba(0, 0, 0, 0.16);
                z-index: 10000;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                transition: all 0.3s ease;
                transform: scale(0.9);
                opacity: 0;
                pointer-events: none;
            }
            
            .nexobotics-chat-container.open {
                transform: scale(1);
                opacity: 1;
                pointer-events: all;
            }
            
            .nexobotics-chat-header {
                background-color: ${this.config.primaryColor};
                color: white;
                padding: 15px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .nexobotics-chat-header-title {
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: bold;
                font-size: 16px;
            }
            
            .nexobotics-chat-logo {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                background-color: white;
                object-fit: cover;
            }
            
            .nexobotics-chat-close {
                cursor: pointer;
                padding: 5px;
            }
            
            .nexobotics-chat-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 10px;
                background-color: ${this.config.secondaryColor};
            }
            
            .nexobotics-chat-message {
                max-width: 80%;
                padding: 10px 15px;
                border-radius: 18px;
                word-break: break-word;
                animation: fade-in 0.3s ease;
            }
            
            .nexobotics-chat-message.user {
                align-self: flex-end;
                background-color: ${this.config.primaryColor};
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .nexobotics-chat-message.bot {
                align-self: flex-start;
                background-color: white;
                color: ${this.config.textColor};
                border-bottom-left-radius: 5px;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            }
            
            .nexobotics-chat-input-container {
                display: flex;
                padding: 10px;
                border-top: 1px solid #eee;
                background-color: white;
            }
            
            .nexobotics-chat-input {
                flex: 1;
                padding: 12px 15px;
                border: 1px solid #ddd;
                border-radius: 25px;
                outline: none;
                font-size: 14px;
                resize: none;
                height: 45px;
                max-height: 100px;
                overflow-y: auto;
            }
            
            .nexobotics-chat-input:focus {
                border-color: ${this.config.primaryColor};
            }
            
            .nexobotics-chat-send {
                background-color: ${this.config.primaryColor};
                color: white;
                border: none;
                border-radius: 50%;
                width: 45px;
                height: 45px;
                margin-left: 10px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .nexobotics-chat-send:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .nexobotics-chat-loader {
                display: inline-block;
                width: 15px;
                height: 15px;
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-top-color: ${this.config.primaryColor};
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            
            .nexobotics-starter-questions {
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin-top: 10px;
                margin-bottom: 5px;
            }
            
            .nexobotics-starter-question {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 18px;
                padding: 8px 15px;
                font-size: 13px;
                cursor: pointer;
                transition: background-color 0.2s;
                text-align: left;
                color: ${this.config.textColor};
            }
            
            .nexobotics-starter-question:hover {
                background-color: #f0f0f0;
            }
            
            @keyframes fade-in {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Mobile responsive styles */
            @media (max-width: 480px) {
                .nexobotics-chat-container {
                    width: calc(100% - 20px);
                    height: calc(100% - 80px);
                    ${this.config.position === 'bottom-right' ? 'right: 10px; bottom: 10px;' : 'left: 10px; bottom: 10px;'}
                }
            }
        `;
        document.head.appendChild(styleEl);
    }

    _createChatWidget() {
        // Chat button
        const button = document.createElement('div');
        button.className = 'nexobotics-chat-button';
        button.innerHTML = `
            <svg class="nexobotics-chat-button-icon" viewBox="0 0 24 24">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"></path>
                <path d="M7 9h10M7 13h7" stroke="white" stroke-width="1.5" stroke-linecap="round"></path>
            </svg>
        `;
        document.body.appendChild(button);

        // Chat container
        const container = document.createElement('div');
        container.className = 'nexobotics-chat-container';
        container.innerHTML = `
            <div class="nexobotics-chat-header">
                <div class="nexobotics-chat-header-title">
                    <img class="nexobotics-chat-logo" src="${this.config.logoUrl}" alt="Logo">
                    <span>${this.config.title}</span>
                </div>
                <div class="nexobotics-chat-close">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </div>
            </div>
            <div class="nexobotics-chat-messages"></div>
            <div class="nexobotics-chat-input-container">
                <textarea class="nexobotics-chat-input" placeholder="${this.config.placeholder}" rows="1"></textarea>
                <button class="nexobotics-chat-send" disabled>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 2L11 13"></path>
                        <path d="M22 2L15 22L11 13L2 9L22 2Z"></path>
                    </svg>
                </button>
            </div>
        `;
        document.body.appendChild(container);

        // Add starter questions if enabled
        if (this.config.showStarterQuestions && this.config.starterQuestions.length > 0) {
            const starterQuestionContainer = document.createElement('div');
            starterQuestionContainer.className = 'nexobotics-starter-questions';
            
            this.config.starterQuestions.forEach(question => {
                const questionButton = document.createElement('button');
                questionButton.className = 'nexobotics-starter-question';
                questionButton.textContent = question;
                questionButton.addEventListener('click', () => this.sendMessage(question));
                starterQuestionContainer.appendChild(questionButton);
            });
            
            const messagesContainer = document.querySelector('.nexobotics-chat-messages');
            messagesContainer.appendChild(starterQuestionContainer);
        }
    }

    _setupEventListeners() {
        // Open chat
        document.querySelector('.nexobotics-chat-button').addEventListener('click', () => {
            this.open();
        });

        // Close chat
        document.querySelector('.nexobotics-chat-close').addEventListener('click', () => {
            this.close();
        });

        // Send message on button click
        document.querySelector('.nexobotics-chat-send').addEventListener('click', () => {
            const inputEl = document.querySelector('.nexobotics-chat-input');
            const message = inputEl.value.trim();
            if (message) {
                this.sendMessage(message);
            }
        });

        // Send message on Enter (but new line on Shift+Enter)
        const inputEl = document.querySelector('.nexobotics-chat-input');
        inputEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const message = inputEl.value.trim();
                if (message) {
                    this.sendMessage(message);
                }
            }
        });

        // Enable/disable send button based on input
        inputEl.addEventListener('input', () => {
            document.querySelector('.nexobotics-chat-send').disabled = !inputEl.value.trim();
            
            // Auto-adjust textarea height
            inputEl.style.height = 'auto';
            inputEl.style.height = (inputEl.scrollHeight < 100) ? `${inputEl.scrollHeight}px` : '100px';
        });
    }

    _addUserMessage(message) {
        const messagesContainer = document.querySelector('.nexobotics-chat-messages');
        const messageEl = document.createElement('div');
        messageEl.className = 'nexobotics-chat-message user';
        messageEl.textContent = message;
        messagesContainer.appendChild(messageEl);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Add to messages array
        this.messages.push({ role: 'user', content: message });
        
        // Add typing indicator
        this._addTypingIndicator();
        
        // Hide starter questions if they exist
        const starterQuestions = document.querySelector('.nexobotics-starter-questions');
        if (starterQuestions) {
            starterQuestions.style.display = 'none';
        }
    }

    _addBotMessage(message) {
        // Remove typing indicator if exists
        this._removeTypingIndicator();
        
        const messagesContainer = document.querySelector('.nexobotics-chat-messages');
        const messageEl = document.createElement('div');
        messageEl.className = 'nexobotics-chat-message bot';
        
        // Process markdown-like formatting
        message = this._formatMessage(message);
        
        messageEl.innerHTML = message;
        messagesContainer.appendChild(messageEl);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Add to messages array
        this.messages.push({ role: 'bot', content: message });
    }

    _addTypingIndicator() {
        const messagesContainer = document.querySelector('.nexobotics-chat-messages');
        let typingIndicator = messagesContainer.querySelector('.nexobotics-chat-typing');
        
        if (!typingIndicator) {
            typingIndicator = document.createElement('div');
            typingIndicator.className = 'nexobotics-chat-message bot nexobotics-chat-typing';
            typingIndicator.innerHTML = '<div class="nexobotics-chat-loader"></div>Typing...';
            messagesContainer.appendChild(typingIndicator);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    _removeTypingIndicator() {
        const typingIndicator = document.querySelector('.nexobotics-chat-typing');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    _formatMessage(message) {
        // Basic markdown formatting
        return message
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Bullet points
            .replace(/^- (.*?)$/gm, '<li>$1</li>')
            .replace(/<li>(.*?)<\/li>/g, '<ul style="margin: 0; padding-left: 20px;"><li>$1</li></ul>')
            // Preserve line breaks
            .replace(/\n/g, '<br>');
    }

    _sendMessageToAPI(message) {
        fetch(this.config.serverUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            this._removeTypingIndicator();
            if (data.response) {
                this._addBotMessage(data.response);
                this._triggerEvent('responseReceived', data.response);
            } else {
                this._addBotMessage('I apologize, but I encountered an issue processing your request.');
                this._triggerEvent('error', 'Empty response from server');
            }
        })
        .catch(error => {
            this._removeTypingIndicator();
            this._addBotMessage('I apologize, but I\'m having trouble connecting to our servers. Please try again later.');
            this._triggerEvent('error', error);
            console.error('Error:', error);
        });
    }

    _generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    _triggerEvent(event, data) {
        if (this.eventHandlers[event]) {
            for (const handler of this.eventHandlers[event]) {
                handler(data);
            }
        }
    }
}

// If the script is loaded in a browser environment, make it globally available
if (typeof window !== 'undefined') {
    window.NexoboticsChat = NexoboticsChat;
} 