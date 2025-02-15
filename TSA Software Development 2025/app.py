import os
import uuid
import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import text_generation  # Must be configured to generate agriculture-specific prompts
import interview_ai

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "PATHFINDER_KEY"

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///career_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# In-Memory User Storage for Authentication
users = {
    "admin": "admin",
    "yuvaraj": "yuvaraj",
    "thomas": "thomas"
}

# -------------------- Authentication Utilities -------------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# -------------------- Database Model -------------------- #
class MentorRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    agriculture_field = db.Column(db.String(120), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    mentor_suggestion = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<MentorRequest {self.username} - {self.agriculture_field}>"

# Create database tables if not present
with app.app_context():
    db.create_all()

# -------------------- Authentication Routes -------------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username in users and users[username] == password:
            session["username"] = username
            flash("Logged in successfully.", "success")
            return redirect(url_for("mentorship_hub"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username in users:
            flash("Username already exists. Please choose another.", "error")
        else:
            users[username] = {"username": username, "password": password}
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))

# -------------------- Main Application Routes -------------------- #

INTERVIEW_HISTORY = []

@app.route("/")
def home():
    current_year = datetime.datetime.now().year
    return render_template("index.html", year=current_year)

# 1) Email Assistance
@app.route("/email-assistance", methods=["GET", "POST"])
def email_assistance():
    """
    Helps craft a short, polite email to potential agriculture employers, 
    farming associations, or sustainability networks.
    """
    ai_suggestion = None
    if request.method == "POST":
        context_info = request.form.get('context_info', '')
        ai_suggestion = text_generation.generate_email_draft(context_info)
    return render_template("email_assistance.html", ai_suggestion=ai_suggestion)

# 2) Resume Builder
@app.route("/resume-builder", methods=["GET", "POST"])
def resume_builder():
    """
    Generates a resume snippet tailored for agriculture or sustainability roles,
    emphasizing relevant farming, crop management, or eco-friendly accomplishments.
    """
    suggestions = None
    if request.method == "POST":
        full_name = request.form.get('fullname', '')
        professional_summary = request.form.get('professional_summary', '')
        experience = request.form.get('experience', '')
        education = request.form.get('education', '')
        skills = request.form.get('skills', '')
        certifications = request.form.get('certifications', '')
        suggestions = text_generation.generate_resume_snippet(
            full_name, professional_summary, experience, education, skills, certifications, additional_advice=True
        )
    return render_template("resume_builder.html", suggestions=suggestions)

# 3) Cover Letter
@app.route("/cover-letter", methods=["GET", "POST"])
def cover_letter():
    """
    Drafts a cover letter focusing on agriculture experience, 
    environmental stewardship, or farm-related qualifications.
    """
    cover_letter_text = None
    if request.method == "POST":
        user_details = request.form.get('user_details', '')
        job_desc = request.form.get('job_desc', '')
        cover_letter_text = text_generation.generate_cover_letter(user_details, job_desc)
    return render_template("cover_letter.html", cover_letter_text=cover_letter_text)

# 4) Interview
@app.route("/interview")
def interview_page():
    """
    Page to record and upload a video interview for feedback.
    """
    return render_template("interview.html")

@app.route("/upload_interview", methods=["POST"])
def upload_interview():
    """
    Uploads a video interview and uses 'interview_ai' for analysis.
    """
    if "videoFile" not in request.files:
        return "No video file part", 400
    file = request.files["videoFile"]
    if file.filename == "":
        return "Empty filename", 400
    ext = os.path.splitext(file.filename)[1]
    if not ext:
        ext = ".webm"
    unique_name = f"interview_{uuid.uuid4().hex}{ext}"
    os.makedirs("uploads", exist_ok=True)
    save_path = os.path.join("uploads", unique_name)
    file.save(save_path)

    feedback = interview_ai.get_interview_feedback(save_path)
    INTERVIEW_HISTORY.append({
        "filename": unique_name,
        "feedback": feedback
    })
    return redirect(url_for("interview_results"))

@app.route("/interview_results")
def interview_results():
    """
    Shows feedback from past interviews.
    """
    return render_template("interview_results.html", history=INTERVIEW_HISTORY)

# 5) Networking Assistant
@app.route("/networking-assistant", methods=["GET", "POST"])
def networking_assistant():
    """
    Assists with finding agriculture professionals or eco-friendly organizations,
    plus drafting personalized icebreaker messages relevant to sustainable farming 
    or green job opportunities.
    """
    connection_recommendations = None
    icebreaker_message = None

    if request.method == "POST":
        # For agriculture-related networking recommendations
        if "recommendations" in request.form:
            agriculture_focus = request.form.get("agriculture_focus", "")
            connection_recommendations = text_generation.generate_connection_recommendations(
                agriculture_focus  # Agriculture-specific focus
            )
        # For an agriculture-themed icebreaker message
        elif "icebreaker" in request.form:
            context_info = request.form.get("icebreaker_context", "")
            icebreaker_message = text_generation.generate_icebreaker_message(context_info)

    return render_template(
        "networking_assistant.html",
        connection_recommendations=connection_recommendations,
        icebreaker_message=icebreaker_message
    )

# 6) Community & Mentorship
@app.route("/mentorship-hub", methods=["GET", "POST"])
@login_required
def mentorship_hub():
    """
    Allows users to request mentor suggestions specifically in agriculture, 
    sustainability, or eco-friendly fields. Saves requests to the MentorRequest model.
    """
    matched_mentor = None
    if request.method == "POST":
        agriculture_field = request.form.get("agriculture_field", "")
        experience_level = request.form.get("experience_level", "")

        prompt = (
            f"Suggest a detailed agriculture mentor for someone working in '{agriculture_field}' "
            f"with '{experience_level}' experience. Include the mentor's background, name, and why "
            f"they are a good match. Provide tips on reaching out, preparing for the conversation, and "
            f"offer any relevant agriculture conferences, job fairs, or local meetups they might attend together."
        )
        matched_mentor = text_generation.generate_text(prompt, max_tokens=250, temperature=0.7)

        # Save to database
        new_request = MentorRequest(
            username=session["username"],
            agriculture_field=agriculture_field,
            experience_level=experience_level,
            mentor_suggestion=matched_mentor
        )
        db.session.add(new_request)
        db.session.commit()

    # Example agriculture-focused communities
    groups = [
        {"name": "Organic Farming Innovators", "description": "Exchanging best practices in soil health and regenerative farming."},
        {"name": "Urban Agriculture Network", "description": "Connecting rooftop gardeners and hydroponic enthusiasts."},
        {"name": "Renewable Energy & Agriculture", "description": "Discussions on integrating solar, wind, and farm operations."}
    ]

    past_requests = MentorRequest.query.filter_by(username=session["username"]).order_by(MentorRequest.created_at.desc()).all()

    return render_template("mentorship_hub.html", groups=groups, matched_mentor=matched_mentor, past_requests=past_requests)

# 7) Agriculture Updates (Events & News)
@app.route("/agriculture-updates")
def agriculture_updates():
    """
    Displays upcoming agriculture events and the latest agriculture news.
    In a real application, these details could be dynamically fetched from a database or external API.
    """
    events = [
        {
            "title": "Organic Farming Conference 2025",
            "date": "2025-03-20",
            "location": "Iowa, USA",
            "description": "A conference on the latest organic farming techniques and sustainable practices."
        },
        {
            "title": "Sustainable Agriculture Workshop",
            "date": "2025-04-10",
            "location": "California, USA",
            "description": "Hands-on training in sustainable farming and regenerative land management."
        },
        {
            "title": "Urban Agriculture Expo",
            "date": "2025-05-15",
            "location": "New York, USA",
            "description": "Showcasing innovations and success stories in urban farming."
        }
    ]
    news = [
        {
            "headline": "New Advances in Crop Management",
            "date": "2025-02-14",
            "summary": "Researchers unveil innovative methods for crop rotation and soil enrichment."
        },
        {
            "headline": "Government Grants for Sustainable Farms",
            "date": "2025-02-15",
            "summary": "New funding opportunities announced for small and medium sustainable farms."
        }
    ]
    return render_template("agriculture_updates.html", events=events, news=news)

# 8) Agriculture Certifications & Skills
@app.route("/agriculture-certifications", methods=["GET", "POST"])
def agriculture_certifications():
    """
    Provides resources and recommended certifications for agriculture professionals,
    including courses and training to enhance farm management and sustainability skills.
    """
    certifications = [
        {
            "name": "Permaculture Design Certificate",
            "provider": "Permaculture Institute",
            "description": "Learn sustainable land-use design and regenerative farming practices."
        },
        {
            "name": "LEED Green Building",
            "provider": "USGBC",
            "description": "Understand green building practices applicable to sustainable agricultural structures."
        },
        {
            "name": "Climate Literacy Certification",
            "provider": "Climate Reality Project",
            "description": "Gain a comprehensive understanding of climate science and its impact on agriculture."
        }
    ]
    
    # Handle requests for more information
    if request.method == "POST":
        user_email = request.form.get("email", "")
        flash(f"Thank you! More information on agriculture certifications will be sent to {user_email}.", "success")
        # Here you could also store the email in a database for future outreach.
    
    return render_template("agriculture_certifications.html", certifications=certifications)

# -------------------- Main App Runner -------------------- #
if __name__ == "__main__":
    text_generation.initialize_text_gen_model("gpt-3.5-turbo")
    interview_ai.load_interview_model()
    app.run(debug=True)
