from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
import PyPDF2
from google import genai

app = Flask(__name__)

# =====================================================
# GLOBAL STORAGE
# =====================================================

document_text = ""
chat_history = []
uploaded_filename = ""

# =====================================================
# DATABASE CONFIGURATION
# =====================================================

app.config['SQLALCHEMY_DATABASE_URI'] = \
'mysql+pymysql://root:yourpassword@localhost/ai_research_assistant'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =====================================================
# GEMINI CONFIGURATION
# =====================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key= "AIzaSyBTjwHukS3lzmkp4HpQozIHZflVN6_6dP0"
)

# =====================================================
# UPLOAD FOLDER
# =====================================================

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):

    os.makedirs(UPLOAD_FOLDER)

# =====================================================
# DATABASE MODEL
# =====================================================

class Document(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(255))

    summary = db.Column(db.Text)

# =====================================================
# HOME PAGE
# =====================================================

@app.route('/')

def home():

    return render_template(

        'index.html',

        chat_history=[],

        filename=None
    )

# =====================================================
# CHAT PAGE
# =====================================================

@app.route('/chat')

def chat():

    global chat_history
    global uploaded_filename

    return render_template(

        'index.html',

        chat_history=chat_history,

        filename=uploaded_filename
    )

# =====================================================
# ANALYZE PDF + INITIAL PROMPT
# =====================================================

@app.route('/analyze', methods=['POST'])

def analyze():

    global document_text
    global chat_history
    global uploaded_filename

    # RESET CHAT

    chat_history = []

    # =====================================================
    # GET FILE + USER PROMPT
    # =====================================================

    file = request.files['pdf_file']

    user_prompt = request.form['user_prompt']

    # =====================================================
    # VALIDATION
    # =====================================================

    if not file:

        return "Please upload a PDF."

    if not file.filename.endswith('.pdf'):

        return "Only PDF files are allowed."

    # =====================================================
    # SAVE FILE
    # =====================================================

    filepath = os.path.join(

        app.config['UPLOAD_FOLDER'],

        file.filename
    )

    file.save(filepath)

    uploaded_filename = file.filename

    # =====================================================
    # EXTRACT PDF TEXT
    # =====================================================

    text = ""

    try:

        with open(filepath, 'rb') as pdf_file:

            reader = PyPDF2.PdfReader(pdf_file)

            for page in reader.pages:

                extracted = page.extract_text()

                if extracted:

                    text += extracted

    except Exception as e:

        return f"PDF Extraction Error: {str(e)}"

    # =====================================================
    # CLEAN TEXT
    # =====================================================

    text = text.strip()

    text = text.replace("\n", " ")

    text = " ".join(text.split())

    # LIMIT HUGE PDFs

    if len(text) > 50000:

        text = text[:50000]

    # STORE DOCUMENT

    document_text = text

    # =====================================================
    # AI PROMPT
    # =====================================================

    prompt = f"""
You are a smart conversational AI assistant like ChatGPT.

The uploaded PDF is additional context.

Use the PDF whenever relevant.

If the user's request is unrelated to the PDF,
answer naturally using your own knowledge.

PDF CONTENT:
{text[:50000]}

USER REQUEST:
{user_prompt}

Rules:
- Be conversational
- Explain clearly
- Use simple language
- Use bullet points when useful
- Keep responses structured
"""

    # =====================================================
    # GEMINI RESPONSE
    # =====================================================

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )

        ai_output = response.text

        # CLEAN OUTPUT

        ai_output = ai_output.replace("**", "")
        ai_output = ai_output.replace("*", "•")
        ai_output = ai_output.replace("##", "")
        ai_output = ai_output.replace("#", "")

    except Exception as e:

        print("Gemini Error:", e)

        ai_output = f"""
AI Service Temporarily Unavailable.

Error Details:
{str(e)}
"""

    # =====================================================
    # SAVE TO DATABASE
    # =====================================================

    try:

        new_doc = Document(

            filename=file.filename,

            summary=ai_output
        )

        db.session.add(new_doc)

        db.session.commit()

    except Exception as e:

        print("Database Error:", e)

    # =====================================================
    # STORE CHAT
    # =====================================================

    chat_history.append({

        "question": user_prompt,

        "answer": ai_output
    })

    # =====================================================
    # RETURN PAGE
    # =====================================================

    return render_template(

        'index.html',

        chat_history=chat_history,

        filename=uploaded_filename
    )

# =====================================================
# FOLLOW-UP QUESTIONS
# =====================================================

@app.route('/ask', methods=['POST'])

def ask_question():

    global document_text
    global chat_history
    global uploaded_filename

    question = request.form['question']

    # =====================================================
    # VALIDATION
    # =====================================================

    if document_text.strip() == "":

        return "Please upload a PDF first."

    # =====================================================
    # REAL-TIME QUESTION DETECTION
    # =====================================================

    question_lower = question.lower()

    realtime_keywords = [

        "weather",
        "temperature",
        "news",
        "today",
        "current time"

    ]

    if any(word in question_lower for word in realtime_keywords):

        answer = """
I currently do not have live internet access
for real-time information like weather or news.

Future Improvement:
Integrate APIs for live responses.
"""

        chat_history.append({

            "question": question,

            "answer": answer
        })

        return render_template(

            'index.html',

            chat_history=chat_history,

            filename=uploaded_filename
        )

    # =====================================================
    # AI QUESTION PROMPT
    # =====================================================

    prompt = f"""
You are a smart conversational AI assistant like ChatGPT.

The uploaded PDF is additional context.

Use the PDF whenever relevant.

If the user's question is unrelated to the PDF,
answer naturally using your own knowledge.

PDF CONTENT:
{document_text[:50000]}

QUESTION:
{question}

Rules:
- Be conversational
- Explain clearly
- Use simple language
- Use bullet points when useful
"""

    # =====================================================
    # GEMINI RESPONSE
    # =====================================================

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )

        answer = response.text

        # CLEAN OUTPUT

        answer = answer.replace("**", "")
        answer = answer.replace("*", "•")
        answer = answer.replace("##", "")
        answer = answer.replace("#", "")

    except Exception as e:

        print("Question Error:", e)

        answer = f"""
AI Service Temporarily Unavailable.

Error Details:
{str(e)}
"""

    # =====================================================
    # STORE CHAT
    # =====================================================

    chat_history.append({

        "question": question,

        "answer": answer
    })

    # =====================================================
    # RETURN PAGE
    # =====================================================

    return render_template(

        'index.html',

        chat_history=chat_history,

        filename=uploaded_filename
    )

# =====================================================
# GENERATE ACADEMIC QUIZ
# =====================================================

@app.route('/academic_quiz', methods=['POST'])

def academic_quiz():

    global document_text
    global uploaded_filename

    if document_text.strip() == "":

        return "Please upload a PDF first."

    prompt = f"""
You are an AI academic quiz generator.

Generate 20 academically focused questions
from the uploaded PDF.

Requirements:
- Focus on concepts
- Include theory questions
- Mix short and long questions
- Clear formatting
- Number all questions
- Do not label questions as beginner, intermediate, or advanced

PDF CONTENT:
{document_text[:50000]}
"""
    
    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )

        quiz = response.text

        quiz = quiz.replace("**", "")
        quiz = quiz.replace("*", "•")
        quiz = quiz.replace("##", "")
        quiz = quiz.replace("#", "")

    except Exception as e:

        quiz = f"""
Quiz Generation Error:

{str(e)}
"""

    return render_template(

        'quiz.html',

        quiz=quiz,

        filename=uploaded_filename
    )

# =====================================================
# GENERATE INTERVIEW QUESTIONS
# =====================================================

@app.route('/interview_questions', methods=['POST'])

def interview_questions():

    global document_text
    global uploaded_filename

    if document_text.strip() == "":

        return "Please upload a PDF first."

    prompt = f"""
You are an AI academic quiz generator.

Generate 20 academically focused questions
from the uploaded PDF.

Requirements:
- Focus on concepts
- Include theory questions
- Mix short and long questions
- Clear formatting
- Number all questions
- Do not label questions as beginner, intermediate, or advanced

PDF CONTENT:
{document_text[:50000]}
"""

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )

        interview_questions = response.text

        interview_questions = interview_questions.replace("**", "")
        interview_questions = interview_questions.replace("*", "•")
        interview_questions = interview_questions.replace("##", "")
        interview_questions = interview_questions.replace("#", "")

    except Exception as e:

        interview_questions = f"""
Interview Question Generation Error:

{str(e)}
"""

    return render_template(

        'interview.html',

        interview_questions=interview_questions,

        filename=uploaded_filename
    )

# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(debug=True)