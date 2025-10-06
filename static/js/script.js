// Global variables
let currentAadhaar = '';
let isVerified = false;

// DOM Elements
let verificationSection, chatSection, aadhaarInput, sendOtpBtn, aadhaarInputGroup, otpInputGroup, otpInput, 
    verifyOtpBtn, statusMessage, resendLink, resendOtpLink, chatMessages, messageInput, sendMessageBtn, statusText, loadingOverlay;

// Function to get DOM elements
function getDOMElements() {
    verificationSection = document.getElementById('verificationSection');
    chatSection = document.getElementById('chatSection');
    aadhaarInput = document.getElementById('aadhaarInput');
    sendOtpBtn = document.getElementById('sendOtpBtn');
    aadhaarInputGroup = document.getElementById('aadhaarInputGroup');
    otpInputGroup = document.getElementById('otpInputGroup');
    otpInput = document.getElementById('otpInput');
    verifyOtpBtn = document.getElementById('verifyOtpBtn');
    statusMessage = document.getElementById('statusMessage');
    resendLink = document.getElementById('resendLink');
    resendOtpLink = document.getElementById('resendOtpLink');
    chatMessages = document.getElementById('chatMessages');
    messageInput = document.getElementById('messageInput');
    sendMessageBtn = document.getElementById('sendMessageBtn');
    statusText = document.getElementById('statusText');
    loadingOverlay = document.getElementById('loadingOverlay');
}

// Function to initialize the script
function init() {
    getDOMElements();
    
    // Add event listeners
    sendOtpBtn.addEventListener('click', handleSendOtp);
    verifyOtpBtn.addEventListener('click', handleVerifyOtp);
    resendLink.addEventListener('click', handleResendOtp);
    sendMessageBtn.addEventListener('click', handleSendMessage);
    
    // Add keyboard event listeners
    aadhaarInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSendOtp();
        }
    });
    
    otpInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleVerifyOtp();
        }
    });
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });
    
    // Show loading overlay initially
    showLoading(true);
    
    // Add window resize listener for responsive scrolling
    window.addEventListener('resize', () => {
        if (chatSection && !chatSection.classList.contains('hidden')) {
            resizeChatArea();
        }
    });
    
    // Check if user is already verified
    checkIfVerified();
}

// Function to check if user is already verified
async function checkIfVerified() {
    try {
        // Call backend API to check if user is already verified
        const response = await fetch('/check_if_verified', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mark as verified
            isVerified = true;
            
            // Show success message briefly
            showStatusMessage(data.message, 'success');
            
            // Update status
            statusText.textContent = 'Online';
            statusText.style.color = '#4CAF50';
            
            // Switch to chat interface after a short delay
            setTimeout(() => {
                verificationSection.classList.add('hidden');
                chatSection.classList.remove('hidden');
                
                // Ensure chat area is properly sized
                setTimeout(() => {
                    resizeChatArea();
                }, 100);
                
                // Show welcome message
                showWelcomeMessage();
                
                // Focus on message input
                messageInput.focus();
            }, 1500);
        } else {
            showStatusMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Error checking if user is already verified:', error);
        showStatusMessage('Network error. Please check your connection and try again.', 'error');
    } finally {
        // Hide loading overlay
        showLoading(false);
    }
}

// Function to handle Send OTP button click
async function handleSendOtp() {
    const aadhaarNumber = aadhaarInput.value.trim();
    
    // Validate Aadhaar number
    if (!aadhaarNumber) {
        showStatusMessage('Please enter your Aadhaar number', 'error');
        return;
    }
    
    if (aadhaarNumber.length !== 12) {
        showStatusMessage('Aadhaar number must be exactly 12 digits', 'error');
        return;
    }
    
    // Disable button and show loading
    sendOtpBtn.disabled = true;
    sendOtpBtn.textContent = 'Sending...';
    showLoading(true);
    
    try {
        // Call backend API to send OTP
        const response = await fetch('/send_otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                aadhaar_number: aadhaarNumber
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store Aadhaar number
            currentAadhaar = aadhaarNumber;
            
            // Show success message
            showStatusMessage(data.message, 'success');
            
            // Hide Aadhaar input, show OTP input
            aadhaarInputGroup.classList.add('hidden');
            otpInputGroup.classList.remove('hidden');
            resendLink.classList.remove('hidden');
            
            // Focus on OTP input
            otpInput.focus();
        } else {
            showStatusMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Error sending OTP:', error);
        showStatusMessage('Network error. Please check your connection and try again.', 'error');
    } finally {
        sendOtpBtn.disabled = false;
        sendOtpBtn.textContent = 'Send OTP';
        showLoading(false);
    }
}

/**
 * Handle Verify OTP button click
 */
async function handleVerifyOtp() {
    const otp = otpInput.value.trim();
    
    // Validate OTP
    if (!otp) {
        showStatusMessage('Please enter the OTP', 'error');
        return;
    }
    
    if (otp.length !== 4) {
        showStatusMessage('OTP must be exactly 4 digits', 'error');
        return;
    }
    
    // Disable button and show loading
    verifyOtpBtn.disabled = true;
    verifyOtpBtn.textContent = 'Verifying...';
    showLoading(true);
    
    try {
        // Call backend API to verify OTP
        const response = await fetch('/verify_otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                aadhaar_number: currentAadhaar,
                otp: otp
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mark as verified
            isVerified = true;
            
            // Show success message briefly
            showStatusMessage(data.message, 'success');
            
            // Update status
            statusText.textContent = 'Online';
            statusText.style.color = '#4CAF50';
            
            // Switch to chat interface after a short delay
            setTimeout(() => {
                verificationSection.classList.add('hidden');
                chatSection.classList.remove('hidden');
                
                // Ensure chat area is properly sized
                setTimeout(() => {
                    resizeChatArea();
                }, 100);
                
                // Show welcome message
                showWelcomeMessage();
                
                // Focus on message input
                messageInput.focus();
            }, 1500);
        } else {
            showStatusMessage(data.message, 'error');
            // Clear OTP input for retry
            otpInput.value = '';
            otpInput.focus();
        }
    } catch (error) {
        console.error('Error verifying OTP:', error);
        showStatusMessage('Network error. Please check your connection and try again.', 'error');
    } finally {
        verifyOtpBtn.disabled = false;
        verifyOtpBtn.textContent = 'Verify OTP';
        showLoading(false);
    }
}

/**
 * Handle Resend OTP link click
 */
async function handleResendOtp(e) {
    e.preventDefault();
    
    // Clear OTP input
    otpInput.value = '';
    
    // Show info message
    showStatusMessage('Resending OTP...', 'info');
    
    // Call send OTP function again
    await handleSendOtp();
}

/**
 * Show welcome message when user enters chat
 */
function showWelcomeMessage() {
    const welcomeMessages = [
        'Welcome to DBTSaarthi! I am your official guide from the Ministry of Social Justice & Empowerment. My purpose is to help you avoid scholarship delays by clarifying the difference between Aadhaar-Linked and DBT-Enabled accounts.',
        'Type "help" to see what questions you can ask me, or just ask your question directly!'
    ];
    
    welcomeMessages.forEach((msg, index) => {
        setTimeout(() => {
            addMessage(msg, 'bot');
        }, index * 800);
    });
}

/**
 * Handle Send Message button click
 */
async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    // Validate message
    if (!message) {
        return;
    }
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Call backend API to get response
        const response = await fetch('/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                aadhaar_number: currentAadhaar,
                message: message
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (data.success) {
            // Add bot response to chat
            addMessage(data.response, 'bot');
        } else {
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error getting response:', error);
        removeTypingIndicator();
        addMessage('Network error. Please check your connection and try again.', 'bot');
    }
}

/**
 * Add message to chat
 * @param {string} text - Message text
 * @param {string} sender - 'user' or 'bot'
 */
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    
    // Preserve line breaks in bot messages
    if (sender === 'bot') {
        bubbleDiv.innerHTML = text.replace(/\n/g, '<br>');
    } else {
        bubbleDiv.textContent = text;
    }
    
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom with a slight delay to ensure DOM is updated
    setTimeout(() => {
        scrollToBottom();
    }, 50);
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble typing-indicator';
    bubbleDiv.innerHTML = '<span></span><span></span><span></span>';
    
    typingDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(typingDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    // Use requestAnimationFrame to ensure DOM is updated
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
    
    // Also try smooth scrolling as fallback
    setTimeout(() => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

/**
 * Show status message in verification section
 * @param {string} message - Message to display
 * @param {string} type - 'success', 'error', or 'info'
 */
function showStatusMessage(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    
    // Auto-hide success and info messages after 5 seconds
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            statusMessage.className = 'status-message';
        }, 5000);
    }
}

/**
 * Show/hide loading overlay
 * @param {boolean} show - Whether to show or hide
 */
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

/**
 * Resize chat area to ensure proper scrolling
 */
function resizeChatArea() {
    if (chatMessages) {
        // Force a reflow to ensure proper sizing
        chatMessages.style.height = 'auto';
        setTimeout(() => {
            // Ensure the chat messages area has the correct height
            const chatSectionHeight = chatSection.offsetHeight;
            const headerHeight = document.querySelector('.chat-header').offsetHeight;
            const inputHeight = document.querySelector('.chat-input').offsetHeight;
            const availableHeight = chatSectionHeight - inputHeight - 40; // 40px for padding
            
            chatMessages.style.maxHeight = `${availableHeight}px`;
            chatMessages.style.height = `${availableHeight}px`;
            
            // Scroll to bottom after resizing
            scrollToBottom();
        }, 50);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);