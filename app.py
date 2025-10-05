import inspect
import os
import uuid
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request, url_for
from torch.serialization import add_safe_globals

# Agree to Coqui CPML terms.
os.environ["COQUI_TOS_AGREED"] = "1"

# Heavy ML imports are done lazily to keep startup fast.
import whisper  # type: ignore
from TTS.api import TTS  # type: ignore
import TTS.tts.models.xtts as xtts_module
import TTS.tts.configs.xtts_config as xtts_config_module
from TTS.config import shared_configs as shared_config_module


def _register_xtts_safe_globals() -> None:
    modules = [xtts_config_module, xtts_module, shared_config_module]
    safe_objects = []
    for module in modules:
        for attr in vars(module).values():
            if inspect.isclass(attr):
                safe_objects.append(attr)
    if safe_objects:
        add_safe_globals(safe_objects)


_register_xtts_safe_globals()

app = Flask(__name__)

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
GENERATED_AUDIO_DIR = os.path.join(STATIC_DIR, "generated")
SPEAKER_REFERENCE_PATH = os.path.join(STATIC_DIR, "speaker_ref.wav")
os.makedirs(GENERATED_AUDIO_DIR, exist_ok=True)


def _speaker_reference() -> Optional[str]:
    if os.path.exists(SPEAKER_REFERENCE_PATH) and os.path.getsize(SPEAKER_REFERENCE_PATH) > 0:
        return SPEAKER_REFERENCE_PATH
    return None

# Models are loaded once at module import to serve requests quickly.
WHISPER_MODEL = whisper.load_model("base")
TTS_MODEL = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
AVAILABLE_SPEAKERS = list(TTS_MODEL.speakers or [])
DEFAULT_SPEAKER = AVAILABLE_SPEAKERS[0] if AVAILABLE_SPEAKERS else None
if DEFAULT_SPEAKER:
    app.logger.info("XTTS default speaker set to %s", DEFAULT_SPEAKER)
else:
    app.logger.info("XTTS model has no pre-defined speakers; expecting speaker_wav input")

# NOTE: Replace the placeholder speaker reference file with a real 3-5 second
# high-quality sample for optimal XTTS-v2 voice cloning performance.

# Simple multilingual response bank keyed by language code.
# Each entry is an ordered list of tuples (keywords, response_text).
KNOWLEDGE_BASE: Dict[str, List[Dict[str, List[str]]]] = {
    "en": [
        {"keywords": ["help", "hello"], "responses": [
            "Hello! I'm your multilingual voice assistant. Ask about direct benefit transfer services."
        ]},
        {"keywords": ["aadhaar", "aadhar"], "responses": [
            "An Aadhaar-linked account ensures your benefits reach you directly via DBT."
        ]},
        {"keywords": ["scholarship", "payment"], "responses": [
            "Scholarship payments are processed within 7-10 days once the Aadhaar linkage is verified."
        ]},
        {"keywords": ["default"], "responses": [
            "I'm here to help with DBT-related questions! Try asking about Aadhaar linkage or scholarship timelines."
        ]},
    ],
    "hi": [
        {"keywords": ["help", "namaste", "madad"], "responses": [
            "नमस्ते! मैं आपकी बहुभाषी सहायक हूं। डीबीटी सेवाओं से जुड़े प्रश्न पूछें।"
        ]},
        {"keywords": ["aadhaar", "आधार"], "responses": [
            "आधार से लिंक्ड खाता होने से आपकी डीबीटी राशि सीधे खाते में आती है।"
        ]},
        {"keywords": ["scholarship", "वृत्ति", "payment", "छात्रवृत्ति"], "responses": [
            "आधार सत्यापन पूरा होने के बाद छात्रवृत्ति भुगतान 7-10 दिनों में संसाधित होता है।"
        ]},
        {"keywords": ["default"], "responses": [
            "मैं डीबीटी संबंधी प्रश्नों में सहायता के लिए तैयार हूँ! आधार या छात्रवृत्ति के बारे में पूछें।"
        ]},
    ],
    "ta": [
        {"keywords": ["help", "vanakkam", "உதவி"], "responses": [
            "வணக்கம்! நான் உங்கள் பன்மொழி உதவியாளர். டிபிடி சேவை குறித்து கேள்விகள் கேளுங்கள்."
        ]},
        {"keywords": ["aadhaar", "ஆதார்"], "responses": [
            "ஆதார் இணைக்கப்பட்ட கணக்கு டிபிடி நன்மைகள் நேரடியாக உங்களுக்கு வரும் வகையில் செய்கிறது."
        ]},
        {"keywords": ["scholarship", "கல்வியுதவி", "payment"], "responses": [
            "ஆதார் சரிபார்ப்புக்குப் பிறகு கல்வி உதவி 7-10 நாட்களில் செயலாக்கப்படும்."
        ]},
        {"keywords": ["default"], "responses": [
            "டிபிடி அல்லது கல்வி உதவி தொடர்பான கேள்விகளுக்கு நான் தயாராக இருக்கிறேன். கேளுங்கள்!"
        ]},
    ],
    "te": [
        {"keywords": ["help", "namaste", "సహాయం"], "responses": [
            "నమస్తే! నేను మీ బహుభాషా సహాయకురాలు. డీబీటీ సేవల గురించి అడగండి."
        ]},
        {"keywords": ["aadhaar", "ఆధార్"], "responses": [
            "ఆధార్ లింక్ చేసిన ఖాతాతో డీబీటీ ప్రయోజనాలు నేరుగా మీకు చేరుతాయి." ]},
        {"keywords": ["scholarship", "విద్యావేతనం", "payment"], "responses": [
            "ఆధార్ ధృవీకరణ పూర్తయిన తర్వాత విద్యావేతన చెల్లింపులు 7-10 రోజుల్లో జరుగుతాయి."
        ]},
        {"keywords": ["default"], "responses": [
            "డీబీటీ లేదా విద్యావేతనం గురించి ఏ ప్రశ్న ఉన్నా అడగండి, నేను సహయపడతాను." ]},
    ],
    "mr": [
        {"keywords": ["help", "namaskar", "मदत"], "responses": [
            "नमस्कार! मी तुमची बहुभाषिक सहाय्यक आहे. डीबीटी सेवांबद्दल प्रश्न विचारा." ]},
        {"keywords": ["aadhaar", "आधार"], "responses": [
            "आधार लिंक केलेले खाते असल्यास डीबीटीचे लाभ थेट तुमच्यापर्यंत पोहोचतात." ]},
        {"keywords": ["scholarship", "शिष्यवृत्ती", "payment"], "responses": [
            "आधार पडताळणीनंतर शिष्यवृत्तीचे पेमेंट ७-१० दिवसांत प्रक्रिया होते." ]},
        {"keywords": ["default"], "responses": [
            "डीबीटी किंवा शिष्यवृत्ती संदर्भातील प्रश्न विचारण्यासाठी मी सज्ज आहे." ]},
    ],
    "kn": [
        {"keywords": ["help", "namaskara", "ಸಹಾಯ"], "responses": [
            "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಬಹುಭಾಷಾ ಸಹಾಯಕ. ಡಿಬಿಟಿ ಸೇವೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ." ]},
        {"keywords": ["aadhaar", "ಆಧಾರ್"], "responses": [
            "ಆಧಾರ್ ಲಿಂಕ್ ಮಾಡಿದ ಖಾತೆಯ ಮೂಲಕ ಡಿಬಿಟಿ ಸೌಲಭ್ಯಗಳು ನೇರವಾಗಿ ನಿಮಗೆ ಬರುತ್ತವೆ." ]},
        {"keywords": ["scholarship", "ವಿದ್ಯಾರ್ಥಿವೇತನ", "payment"], "responses": [
            "ಆಧಾರ್ ಪರಿಶೀಲನೆಯ ನಂತರ ವಿದ್ಯಾರ್ಥಿವೇತನ ಪಾವತಿಗಳು 7-10 ದಿನಗಳಲ್ಲಿ ಕಾರ್ಯಗತಗೊಳ್ಳುತ್ತವೆ." ]},
        {"keywords": ["default"], "responses": [
            "ಡಿಬಿಟಿ ಅಥವಾ ವಿದ್ಯಾರ್ಥಿವೇತನ ಕುರಿತು ಪ್ರಶ್ನೆಗಳಿದ್ದರೆ ಕೇಳಿ, ನಾನು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ." ]},
    ],
    "ml": [
        {"keywords": ["help", "സഹായം", "namaskaram"], "responses": [
            "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ ബഹുഭാഷ സഹായി. ഡിബി.ടി സേവനങ്ങളെ കുറിച്ച് ചോദിക്കൂ."
        ]},
        {"keywords": ["aadhaar", "ആധാർ"], "responses": [
            "ആധാർ ലിങ്ക് ചെയ്ത അക്കൗണ്ട് ഉണ്ടെങ്കിൽ ഡിബി.ടി ഗുണങ്ങൾ നേരിട്ട് നിങ്ങൾക്ക് ലഭിക്കും."
        ]},
        {"keywords": ["scholarship", "സ്കോളർഷിപ്പ്", "payment"], "responses": [
            "ആധാർ പരിശോധനയ്ക്ക് ശേഷം സ്കോളർഷിപ്പ് പണമടയ്ക്കൽ 7-10 ദിവസങ്ങളിൽ നടക്കും."
        ]},
        {"keywords": ["default"], "responses": [
            "ഡിബി.ടി അല്ലെങ്കിൽ സ്കോളർഷിപ്പ് സംബന്ധിച്ച ചോദ്യങ്ങൾ ഉണ്ടെങ്കിൽ ചോദിക്കൂ, ഞാൻ സഹായിക്കും."
        ]},
    ],
    "gu": [
        {"keywords": ["help", "madad", "નમસ્તે"], "responses": [
            "નમસ્તે! હું તમારો બહુભાષી સહાયક છું. ડીબિટી સેવાઓ વિશે પ્રશ્નો પૂછો."
        ]},
        {"keywords": ["aadhaar", "આધાર"], "responses": [
            "આધારથી જોડાયેલ ખાતું હોય તો ડીબિટી લાભો સીધા તમારા ખાતામાં પહોંચે છે."
        ]},
        {"keywords": ["scholarship", "સ્કોલરશિપ", "payment"], "responses": [
            "આધાર ચકાસણી પછી સ્કોલરશિપ ચુકવણીઓ 7-10 દિવસમાં પ્રક્રિયા થાય છે."
        ]},
        {"keywords": ["default"], "responses": [
            "ડીબિટી અથવા સ્કોલરશિપ અંગે કંઈ પૂછવું હોય તો પૂછો, હું મદદ કરીશ."
        ]},
    ],
    "pa": [
        {"keywords": ["help", "sat sri akal", "ਮਦਦ"], "responses": [
            "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡੀ ਬਹੁਭਾਸ਼ੀ ਸਹਾਇਕ ਹਾਂ। ਡੀਬੀਟੀ ਸੇਵਾਵਾਂ ਬਾਰੇ ਪੁੱਛੋ।"
        ]},
        {"keywords": ["aadhaar", "ਆਧਾਰ"], "responses": [
            "ਆਧਾਰ ਨਾਲ ਜੁੜਿਆ ਖਾਤਾ ਹੋਣ ਨਾਲ ਡੀਬੀਟੀ ਲਾਭ ਸਿੱਧੇ ਤੁਹਾਨੂੰ ਮਿਲਦੇ ਹਨ।"
        ]},
        {"keywords": ["scholarship", "ਵਜ਼ੀਫ਼ਾ", "payment"], "responses": [
            "ਆਧਾਰ ਤਸਦੀਕ ਤੋਂ ਬਾਅਦ ਵਜ਼ੀਫ਼ੇ ਦੀ ਭੁਗਤਾਨੀ 7-10 ਦਿਨਾਂ ਵਿੱਚ ਹੋ ਜਾਂਦੀ ਹੈ।"
        ]},
        {"keywords": ["default"], "responses": [
            "ਡੀਬੀਟੀ ਜਾਂ ਵਜ਼ੀਫ਼ੇ ਬਾਰੇ ਸਵਾਲ ਹੋਣ ਤੇ ਮੈਨੂੰ ਪੁੱਛੋ, ਮੈਂ ਮਦਦ ਕਰਾਂਗਾ।"
        ]},
    ],
    "or": [
        {"keywords": ["help", "ସହାୟତା", "namaskar"], "responses": [
            "ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କର ବହୁଭାଷୀ ସହାୟକ। ଡିବିଟି ସେବା ସମ୍ବନ୍ଧୀୟ ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ।"
        ]},
        {"keywords": ["aadhaar", "ଆଧାର"], "responses": [
            "ଆଧାର ସଂଯୁକ୍ତ ଖାତା ଥିଲେ ଡିବିଟି ଲାଭ ସିଧାସଳଖ ଆପଣଙ୍କୁ ପହଞ୍ଚେ।"
        ]},
        {"keywords": ["scholarship", "ବୃତ୍ତି", "payment"], "responses": [
            "ଆଧାର ସତ୍ୟପାୟନ ପରେ ବୃତ୍ତି ପରିଶୋଧନ 7-10 ଦିନ ମଧ୍ୟରେ ହୁଏ।"
        ]},
        {"keywords": ["default"], "responses": [
            "ଡିବିଟି କିମ୍ବା ବୃତ୍ତି ନେଇ ପ୍ରଶ୍ନ ଥାକିଲେ ପଚାରନ୍ତୁ, ମୁଁ ସହାୟତା କରିବି।"
        ]},
    ],
}

# Map alternate Whisper language codes to our KB keys if necessary.
LANGUAGE_ALIASES = {
    "en-in": "en",
    "hi-in": "hi",
    "te-in": "te",
    "ta-in": "ta",
    "kn-in": "kn",
    "ml-in": "ml",
    "gu-in": "gu",
    "pa-in": "pa",
    "mr-in": "mr",
    "or-in": "or",
}

FALLBACK_LANGUAGE = "en"


def choose_response(language: str, transcript: str) -> str:
    transcript_lower = transcript.lower()
    language_key = LANGUAGE_ALIASES.get(language, language)
    entries = KNOWLEDGE_BASE.get(language_key, KNOWLEDGE_BASE[FALLBACK_LANGUAGE])

    # Search for the first matching keyword-based response.
    for entry in entries:
        for keyword in entry["keywords"]:
            if keyword != "default" and keyword in transcript_lower:
                return entry["responses"][0]

    # Fallback to the default response for the language.
    for entry in entries:
        if "default" in entry["keywords"]:
            return entry["responses"][0]

    # Absolute fallback to English.
    return KNOWLEDGE_BASE[FALLBACK_LANGUAGE][-1]["responses"][0]


@app.route("/")
def home():
    return render_template("index.html")


@app.post("/api/voice_process")
def process_voice():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded."}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    temp_input_path = os.path.join(GENERATED_AUDIO_DIR, f"input_{uuid.uuid4().hex}.webm")
    audio_file.save(temp_input_path)

    try:
        whisper_result = WHISPER_MODEL.transcribe(temp_input_path)
        transcript_text = whisper_result.get("text", "").strip()
        language_code = whisper_result.get("language", FALLBACK_LANGUAGE)
        language_for_response = LANGUAGE_ALIASES.get(language_code, language_code)
        if language_for_response not in KNOWLEDGE_BASE:
            language_for_response = FALLBACK_LANGUAGE

        if not transcript_text:
            transcript_text = ""

        bot_response = choose_response(language_for_response, transcript_text or "")

        output_filename = f"response_{uuid.uuid4().hex}.wav"
        output_path = os.path.join(GENERATED_AUDIO_DIR, output_filename)

        # Generate TTS audio using Coqui XTTS-v2.
        speaker_wav = _speaker_reference()
        speaker_id = None
        if not speaker_wav:
            speaker_id = DEFAULT_SPEAKER

        if speaker_wav:
            bot_response = "This is a cloned voice response. " + bot_response
        elif speaker_id:
            bot_response = f"This is the default XTTS voice '{speaker_id}'. " + bot_response

        TTS_MODEL.tts_to_file(
            text=bot_response,
            file_path=output_path,
            speaker_wav=speaker_wav,
            speaker=speaker_id,
            language=language_for_response,
        )

        audio_url = url_for("static", filename=f"generated/{output_filename}")

        return jsonify(
            {
                "user_text": transcript_text,
                "language": language_code,
                "bot_text": bot_response,
                "audio_url": audio_url,
            }
        )
    except Exception as exc:  # pragma: no cover - logging placeholder
        app.logger.exception("Error processing voice request")
        return jsonify({"error": str(exc)}), 500
    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)


if __name__ == "__main__":
    port = int(os.environ.get("FLASK_RUN_PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
