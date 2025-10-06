# 🇮🇳 Aadhaar Awareness Chatbot

A WhatsApp-style web chatbot that explains the difference between Aadhaar-linked accounts and DBT-enabled Aadhaar-seeded bank accounts, with OTP verification.

## 📋 Features

✅ WhatsApp-style chat interface  
🔐 Aadhaar number verification with OTP  
💬 Pre-planned Q&A about Aadhaar and DBT accounts  
📱 Mobile-responsive design  
🚀 Simple Flask backend with no database  
⚡ Real-time chat experience

🗂️ Project Structure
AadhaarChatBot/
│
├── static/
│   ├── css/
│   │   └── style.css          # WhatsApp-style UI
│   ├── js/
│       └── script.js          # Frontend logic
├── templates/
│   └── index.html             # Main HTML page
├── app.py                     # Flask backend
├── requirements.txt           # Python dependencies
└── README.md                  # This file
🚀 Quick Start
Prerequisites

Python 3.11 or higher
pip (Python package manager)

Installation

Clone or download this project
Navigate to the project directory

bash   cd AadhaarChatBot

Create a virtual environment (recommended)

bash   python -m venv venv

Activate the virtual environment

On Windows:



bash     venv\Scripts\activate

On macOS/Linux:

bash     source venv/bin/activate

Install dependencies

bash   pip install -r requirements.txt

Run the application

bash   python app.py

Open your browser
Navigate to: http://127.0.0.1:5000

📖 Usage Guide
Step 1: Aadhaar Verification

Enter your 12-digit Aadhaar number
Click "Send OTP"
Check the console/terminal for the OTP (in testing mode)
Enter the 4-digit OTP
Click "Verify OTP"

Step 2: Chat with the Bot
Once verified, you can ask questions like:

"What is Aadhaar-linked account?"
"What is DBT-enabled Aadhaar-seeded account?"
"Difference between Aadhaar linked and DBT enabled"
"How to enable DBT?"
"Benefits of DBT"
"Help" (to see all options)

💡 Testing OTP
For easy testing, the chatbot uses a **constant OTP: 5422**
- Enter any 12-digit Aadhaar number (e.g., 123456789012)
- Always use OTP: **5422**
- This makes testing much simpler!

Console output will show:
==================================================
📱 SMS SENT TO AADHAAR: 123456789012
🔐 OTP: 5422 (CONSTANT FOR TESTING)
⏰ Valid until: 2025-10-05 15:30:00
==================================================
🔧 Customization
Adding More Q&A
Edit the QA_DATABASE dictionary in app.py:
pythonQA_DATABASE = {
    "your question": "Your answer here",
    "another question": "Another answer",
    # Add more Q&A pairs
}
Enabling Real SMS (Optional)
To send real SMS instead of console output:

Install Twilio

bash   pip install twilio

Get Twilio credentials from https://www.twilio.com
Uncomment and configure the SMS code in app.py:

python   from twilio.rest import Client
   
   account_sid = 'your_account_sid'
   auth_token = 'your_auth_token'
   
   client = Client(account_sid, auth_token)
   message = client.messages.create(
       body=f"Your Aadhaar Chatbot OTP is: {otp}",
       from_='+1234567890',  # Your Twilio number
       to='+91' + aadhaar_number[-10:]
   )
🎨 UI Customization
Changing Colors
Edit static/css/style.css:
css/* Change header color */
.chat-header {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}

/* Change user bubble color */
.message.user .message-bubble {
    background: #YOUR_COLOR;
}
📝 API Endpoints
EndpointMethodDescription/GETServes the main HTML page/send_otpPOSTGenerates and sends OTP/verify_otpPOSTVerifies the entered OTP/get_responsePOSTReturns chatbot response
🔒 Security Notes
Important: This is a demonstration project. For production use:

✅ Use a proper database (PostgreSQL, MongoDB)
✅ Implement rate limiting
✅ Add HTTPS/SSL
✅ Use environment variables for sensitive data
✅ Implement proper session management
✅ Add input sanitization and validation
✅ Use real OTP service (Twilio, AWS SNS)

🐛 Troubleshooting
Port Already in Use
If port 5000 is already in use, change it in app.py:
pythonapp.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
OTP Not Appearing

Check the console/terminal where you ran python app.py
The OTP is printed there in testing mode

Styles Not Loading

Make sure the folder structure is correct
Clear browser cache (Ctrl+F5 or Cmd+Shift+R)

Messages Not Sending

Check browser console for errors (F12)
Verify the Flask server is running
Check network tab in browser DevTools

📦 Dependencies

Flask 3.0.0: Web framework
Werkzeug 3.0.1: WSGI utility library

🤝 Contributing
Feel free to:

Add more Q&A pairs
Improve the UI/UX
Add new features
Fix bugs

📄 License
This project is for educational purposes. Feel free to use and modify as needed.
👨‍💻 Development
Running in Debug Mode
Debug mode is enabled by default. To disable:
pythonapp.run(debug=False, host='0.0.0.0', port=5000)
Adding Logging
Add to app.py:
pythonimport logging
logging.basicConfig(level=logging.INFO)
📞 Support
For issues or questions:

Check the troubleshooting section
Review the code comments
Check Flask documentation: https://flask.palletsprojects.com/

✨ Future Enhancements
Possible improvements:

 Multi-language support
 Voice messages
 File upload support
 Chat history export
 Admin dashboard
 Analytics and metrics
 Integration with actual Aadhaar API (if available)


Made with ❤️ for Aadhaar awareness