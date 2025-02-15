from openai import OpenAI
import os

# Set OpenAI API key as an environment variable
client = OpenAI(api_key=os.environ.get("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"))


def initialize_text_gen_model(model_name="gpt-3.5-turbo"):
    print(f"Using ChatGPT model: {model_name}")


def generate_text(prompt, max_tokens=150, temperature=0.7):
    try:
        messages = [
            {"role": "system", "content": "You are ChatGPT, a helpful assistant specialized in green careers and sustainable agriculture."},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9,
            n=1,
            stream=False
        )
        generated_text = response.choices[0].message.content.strip()
        return generated_text
    except Exception as e:
        return f"Error generating text: {e}"


def generate_email_draft(context_info):
    """
    Generates a short, polite email suitable for a professional setting,
    specifically in the context of green jobs or sustainable agriculture.
    """
    prompt = (
        "Write a short, professional email introducing the sender’s interest in a green or sustainable agriculture role. "
        "Ensure it's polite, concise, and clearly states how the sender can contribute to environmental objectives.\n\n"
        f"Context: {context_info}\n\n"
        "Email:"
    )
    return generate_text(prompt, max_tokens=150, temperature=0.7)


def generate_resume_snippet(
    full_name,
    professional_summary,
    experience,
    education,
    skills,
    certifications,
    additional_advice=True
):
    """
    Creates a resume snippet emphasizing green job experience, eco-friendly initiatives,
    or sustainable agriculture projects.
    """
    advice_section = ""
    if additional_advice:
        advice_section = (
            "Additionally, provide actionable advice on how to make this resume stand out for green or sustainable roles. "
            "Include tips on highlighting eco-friendly projects, relevant volunteer work, and demonstrating impact (e.g., "
            "reduced waste, improved resource management)."
        )

    prompt = (
        "Create a professional resume snippet tailored for green jobs or sustainable agriculture positions. "
        "Highlight environmental and sustainability-focused initiatives, achievements, or certifications.\n\n"
        "Sections to include:\n"
        "1. Professional Summary\n"
        "2. Experience (Emphasize any projects related to renewable energy, organic farming, or eco-friendly practices)\n"
        "3. Education (Include relevant coursework, workshops, or certifications)\n"
        "4. Skills (Technical and soft skills, especially those relevant to green industries)\n"
        "5. Certifications (Permaculture Design, LEED, Climate Literacy, etc.)\n\n"
        f"Full Name: {full_name}\n"
        f"Professional Summary: {professional_summary}\n"
        f"Experience: {experience}\n"
        f"Education: {education}\n"
        f"Skills: {skills}\n"
        f"Certifications: {certifications}\n\n"
        f"{advice_section}\n\n"
        "Output:"
    )
    return generate_text(prompt, max_tokens=300, temperature=0.7)


def generate_cover_letter(user_details, job_desc):
    """
    Drafts a concise and compelling cover letter for a green job or sustainable agriculture role.
    """
    prompt = (
        "Write a concise, compelling cover letter tailored to a green job or sustainable agriculture position. "
        "Highlight the applicant's passion for environmental stewardship, relevant eco-skills, and dedication "
        "to sustainability.\n\n"
        f"Applicant Details: {user_details}\n"
        f"Job Description: {job_desc}\n\n"
        "Cover Letter:"
    )
    return generate_text(prompt, max_tokens=250, temperature=0.7)


def generate_connection_recommendations(target_company, industry):
    """
    Suggests three potential LinkedIn contacts for someone looking to grow their network in
    green industries, focusing on sustainable agriculture, conservation, or similar fields.
    """
    prompt = (
        f"Suggest three potential LinkedIn contacts for a professional seeking to expand their network in the green job market, "
        f"particularly around {industry}. Focus on individuals at {target_company} or involved in sustainable agriculture, "
        f"renewable energy, or eco-friendly initiatives. Provide each contact's role and why they would be valuable connections."
    )
    return generate_text(prompt, max_tokens=200, temperature=0.7)


def generate_icebreaker_message(context_info):
    """
    Crafts a personalized LinkedIn icebreaker message with a green career focus,
    ideal for networking or requesting informational interviews in eco-friendly industries.
    """
    prompt = (
        "Craft a friendly, professional LinkedIn icebreaker message for someone interested in connecting about sustainable agriculture, "
        "conservation, or green job opportunities. Mention shared values or environmental interests.\n\n"
        f"Context: {context_info}\n"
        "Message:"
    )
    return generate_text(prompt, max_tokens=150, temperature=0.7)
