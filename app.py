from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory storage for OTPs and verified users
otp_storage = {}  # {aadhaar_number: {'otp': '1234', 'expiry': datetime_object}}
verified_users = set()  # Set of verified Aadhaar numbers

# Pre-planned Q&A Dictionary for Chatbot Responses
QA_DATABASE = {
    "hi": "Hello! Welcome to DBTSaarthi! I am your official guide from the Ministry of Social Justice & Empowerment. How can I help you avoid scholarship delays today?",
    "hello": "Hello! Welcome to DBTSaarthi! I am your official guide from the Ministry of Social Justice & Empowerment. How can I help you avoid scholarship delays today?",
    "hey": "Hello! Welcome to DBTSaarthi! I am your official guide from the Ministry of Social Justice & Empowerment. How can I help you avoid scholarship delays today?",
    
    # Aadhaar-linked account questions
    "what is aadhaar linked account": "An Aadhaar-linked account is a bank account where your Aadhaar number is linked to your account for identification purposes. This linking helps in easier KYC verification and accessing government services.",
    "aadhaar linked account": "An Aadhaar-linked account is a bank account where your Aadhaar number is linked to your account for identification purposes. This linking helps in easier KYC verification and accessing government services.",
    "linked account": "An Aadhaar-linked account is a bank account where your Aadhaar number is linked to your account for identification purposes. This linking helps in easier KYC verification and accessing government services.",
    
    # DBT-enabled Aadhaar-seeded questions
    "what is dbt enabled aadhaar seeded account": "A DBT-enabled Aadhaar-seeded bank account is specifically configured to receive Direct Benefit Transfer (DBT) payments from the government. It requires Aadhaar seeding (linking) and activation for receiving subsidies, scholarships, pensions, and other government benefits directly into your account.",
    "dbt enabled account": "A DBT-enabled Aadhaar-seeded bank account is specifically configured to receive Direct Benefit Transfer (DBT) payments from the government. It requires Aadhaar seeding (linking) and activation for receiving subsidies, scholarships, pensions, and other government benefits directly into your account.",
    "dbt account": "A DBT-enabled Aadhaar-seeded bank account is specifically configured to receive Direct Benefit Transfer (DBT) payments from the government. It requires Aadhaar seeding (linking) and activation for receiving subsidies, scholarships, pensions, and other government benefits directly into your account.",
    
    # Difference between the two
    "difference between aadhaar linked and dbt enabled": "Key Differences:\n\n1. Aadhaar-Linked Account: Simply links your Aadhaar to your bank account for identification and KYC purposes.\n\n2. DBT-Enabled Aadhaar-Seeded Account: Not only links Aadhaar but also activates your account to receive government payments through Direct Benefit Transfer.\n\nIn simple terms: All DBT-enabled accounts are Aadhaar-linked, but not all Aadhaar-linked accounts are DBT-enabled. You need to specifically enable DBT functionality to receive government benefits.",
    "difference": "Key Differences:\n\n1. Aadhaar-Linked Account: Simply links your Aadhaar to your bank account for identification and KYC purposes.\n\n2. DBT-Enabled Aadhaar-Seeded Account: Not only links Aadhaar but also activates your account to receive government payments through Direct Benefit Transfer.\n\nIn simple terms: All DBT-enabled accounts are Aadhaar-linked, but not all Aadhaar-linked accounts are DBT-enabled. You need to specifically enable DBT functionality to receive government benefits.",
    
    # How to enable DBT
    "how to enable dbt": "To enable DBT on your Aadhaar-seeded account:\n\n1. Visit your bank branch with Aadhaar card\n2. Request DBT activation on your account\n3. Bank will verify your Aadhaar seeding\n4. Once activated, you can receive government benefits\n\nYou can also check DBT status on PFMS (Public Financial Management System) website.",
    "enable dbt": "To enable DBT on your Aadhaar-seeded account:\n\n1. Visit your bank branch with Aadhaar card\n2. Request DBT activation on your account\n3. Bank will verify your Aadhaar seeding\n4. Once activated, you can receive government benefits\n\nYou can also check DBT status on PFMS (Public Financial Management System) website.",
    
    # Benefits
    "benefits of dbt": "Benefits of DBT-enabled accounts:\n\n1. Direct transfer of subsidies without middlemen\n2. Reduced corruption and leakage\n3. Faster credit of government payments\n4. Transparent tracking of benefits\n5. Access to various government schemes\n6. Elimination of duplicate/fake beneficiaries",
    "why dbt": "Benefits of DBT-enabled accounts:\n\n1. Direct transfer of subsidies without middlemen\n2. Reduced corruption and leakage\n3. Faster credit of government payments\n4. Transparent tracking of benefits\n5. Access to various government schemes\n6. Elimination of duplicate/fake beneficiaries",
    
    # Scholarship payment questions
    "will i get my scholarship if my account is only linked": "No, your scholarship payment will be rejected. The central system needs your account mapped to the NPCI Mapper. If it's just 'linked,' the money has no route to your account. You must be seeded to get paid.",
    "scholarship payment rejected": "No, your scholarship payment will be rejected. The central system needs your account mapped to the NPCI Mapper. If it's just 'linked,' the money has no route to your account. You must be seeded to get paid.",
    "scholarship not received": "Your scholarship payment will be rejected if your account is only linked but not seeded. The central system needs your account mapped to the NPCI Mapper. If it's just 'linked,' the money has no route to your account. You must be seeded to get paid.",
    "payment rejected": "If your payment is rejected, it's likely because your account is only linked but not seeded. The central system needs your account mapped to the NPCI Mapper. If it's just 'linked,' the money has no route to your account. You must be seeded to get paid.",
    
    # Help and other queries
    "help": "I'm DBTSaarthi, your guide from the Ministry of Social Justice & Empowerment. You can ask me about:\n\n• What is Aadhaar-linked account?\n• What is DBT-enabled Aadhaar-seeded account?\n• Difference between them\n• How to enable DBT?\n• Benefits of DBT\n• Will I get scholarship if account is only linked?\n• Why was my scholarship payment rejected?\n• How to avoid scholarship delays\n\nJust type your question!",
    "menu": "I'm DBTSaarthi, your guide from the Ministry of Social Justice & Empowerment. You can ask me about:\n\n• What is Aadhaar-linked account?\n• What is DBT-enabled Aadhaar-seeded account?\n• Difference between them\n• How to enable DBT?\n• Benefits of DBT\n• Will I get scholarship if account is only linked?\n• Why was my scholarship payment rejected?\n• How to avoid scholarship delays\n\nJust type your question!",
    
    # Default response
    "default": "I'm DBTSaarthi from the Ministry of Social Justice & Empowerment. I'm sorry, I didn't understand that. Type 'help' to see what I can answer. I can help you with Aadhaar-linked accounts, DBT-enabled accounts, and how to avoid scholarship delays."
}


@app.route('/')
def index():
    """Render the main chatbot page"""
    return render_template('index.html')


@app.route('/send_otp', methods=['POST'])
def send_otp():
    """
    Send constant OTP to the provided Aadhaar number.
    In production, integrate with SMS API (Twilio, AWS SNS, etc.)
    """
    try:
        data = request.get_json()
        aadhaar_number = data.get('aadhaar_number', '').strip()
        
        # Validate Aadhaar number (12 digits)
        if not aadhaar_number or len(aadhaar_number) != 12 or not aadhaar_number.isdigit():
            return jsonify({
                'success': False,
                'message': 'Invalid Aadhaar number. Please enter a 12-digit number.'
            }), 400
        
        # Use constant OTP for testing
        otp = "5422"
        
        # Store OTP with 5-minute expiry
        expiry_time = datetime.now() + timedelta(minutes=5)
        otp_storage[aadhaar_number] = {
            'otp': otp,
            'expiry': expiry_time
        }
        
        # Mock SMS sending (print to console for testing)
        print(f"\n{'='*50}")
        print(f"📱 SMS SENT TO AADHAAR: {aadhaar_number}")
        print(f"🔐 OTP: {otp} (CONSTANT FOR TESTING)")
        print(f"⏰ Valid until: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # In production, uncomment below and add your SMS API credentials
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=f"Your Aadhaar Chatbot OTP is: {otp}. Valid for 5 minutes.",
        #     from_='+1234567890',
        #     to='+91' + aadhaar_number[-10:]  # Assuming last 10 digits as mobile
        # )
        
        return jsonify({
            'success': True,
            'message': f'OTP sent successfully to Aadhaar number ending with {aadhaar_number[-4:]}.'
        })
        
    except Exception as e:
        print(f"Error in send_otp: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send OTP. Please try again.'
        }), 500


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    """
    Verify the OTP entered by the user
    """
    try:
        data = request.get_json()
        aadhaar_number = data.get('aadhaar_number', '').strip()
        entered_otp = data.get('otp', '').strip()
        
        # Check if OTP exists for this Aadhaar number
        if aadhaar_number not in otp_storage:
            return jsonify({
                'success': False,
                'message': 'No OTP request found. Please request OTP first.'
            }), 400
        
        stored_data = otp_storage[aadhaar_number]
        
        # Check if OTP has expired
        if datetime.now() > stored_data['expiry']:
            del otp_storage[aadhaar_number]
            return jsonify({
                'success': False,
                'message': 'OTP has expired. Please request a new OTP.'
            }), 400
        
        # Verify OTP
        if entered_otp == stored_data['otp']:
            # Add to verified users
            verified_users.add(aadhaar_number)
            # Clean up OTP storage
            del otp_storage[aadhaar_number]
            
            print(f"✅ User verified: {aadhaar_number}")
            
            return jsonify({
                'success': True,
                'message': 'OTP verified successfully! You can now start chatting.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid OTP. Please try again.'
            }), 400
            
    except Exception as e:
        print(f"Error in verify_otp: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Verification failed. Please try again.'
        }), 500


@app.route('/check_if_verified', methods=['GET'])
def check_if_verified():
    """
    Check if any user is currently verified (for session persistence)
    """
    try:
        # For this simple implementation, we'll return that no user is verified
        # In a real application, you might store session info in cookies or similar
        return jsonify({
            'success': False,
            'message': 'No verified session found. Please verify your Aadhaar number.'
        })
    except Exception as e:
        print(f"Error in check_if_verified: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Session check failed.'
        }), 500


@app.route('/get_response', methods=['POST'])
def get_response():
    """
    Get chatbot response based on user message using if-else logic
    """
    try:
        data = request.get_json()
        aadhaar_number = data.get('aadhaar_number', '').strip()
        user_message = data.get('message', '').strip().lower()
        
        # Check if user is verified
        if aadhaar_number not in verified_users:
            return jsonify({
                'success': False,
                'message': 'Please complete OTP verification first.'
            }), 401
        
        # Find appropriate response using if-else logic
        bot_response = None
        
        # Check for exact matches first
        if user_message in QA_DATABASE:
            bot_response = QA_DATABASE[user_message]
        else:
            # Check for partial matches using if-else
            if "aadhaar linked" in user_message or "linked account" in user_message:
                if "dbt" in user_message or "difference" in user_message:
                    bot_response = QA_DATABASE["difference between aadhaar linked and dbt enabled"]
                else:
                    bot_response = QA_DATABASE["aadhaar linked account"]
            
            elif "dbt" in user_message:
                if "enable" in user_message or "activate" in user_message or "how" in user_message:
                    bot_response = QA_DATABASE["how to enable dbt"]
                elif "benefit" in user_message or "why" in user_message or "advantage" in user_message:
                    bot_response = QA_DATABASE["benefits of dbt"]
                elif "difference" in user_message:
                    bot_response = QA_DATABASE["difference between aadhaar linked and dbt enabled"]
                else:
                    bot_response = QA_DATABASE["dbt enabled account"]
            
            elif "difference" in user_message:
                bot_response = QA_DATABASE["difference between aadhaar linked and dbt enabled"]
            
            elif "scholarship" in user_message:
                if "rejected" in user_message or "not received" in user_message:
                    bot_response = QA_DATABASE["scholarship payment rejected"]
                elif "linked" in user_message or "only linked" in user_message:
                    bot_response = QA_DATABASE["will i get my scholarship if my account is only linked"]
                else:
                    bot_response = QA_DATABASE["scholarship payment rejected"]
            
            elif "payment" in user_message and ("rejected" in user_message or "failed" in user_message):
                bot_response = QA_DATABASE["payment rejected"]
            
            elif "help" in user_message or "menu" in user_message or "options" in user_message:
                bot_response = QA_DATABASE["help"]
            
            elif "hi" in user_message or "hello" in user_message or "hey" in user_message:
                bot_response = QA_DATABASE["hi"]
            
            else:
                # Default response if no match found
                bot_response = QA_DATABASE["default"]
        
        return jsonify({
            'success': True,
            'response': bot_response
        })
        
    except Exception as e:
        print(f"Error in get_response: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get response. Please try again.'
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 DBTSaarthi Server Starting...")
    print("🏛️  Ministry of Social Justice & Empowerment")
    print("="*60)
    print("📱 Access the chatbot at: http://127.0.0.1:5000")
    print("🔐 CONSTANT OTP FOR TESTING: 5422")
    print("💡 Use any 12-digit Aadhaar number + OTP: 5422")
    print("🎓 Helping students avoid scholarship delays")
    print("="*60 + "\n")
    
    # Run Flask app in debug mode
    app.run(debug=True, host='0.0.0.0', port=5000)