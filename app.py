import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie
import requests
import time
import google.generativeai as genai
from google.generativeai.types import SafetySettingDict
import io
from pypdf import PdfReader

# Set page configuration
st.set_page_config(page_title="Career Guidance", page_icon="logo.png", layout="wide")

# Custom CSS for button styles and smooth animations
st.markdown("""
<style>
    /* Color palette */
    :root {
        --primary-color: #4A90E2;
        --secondary-color: #50E3C2;
        --accent-color: #F5A623;
        --background-color: #F0F4F8;
        --text-color: #333333;
        --button-color: #000000;
        --button-hover-gradient: linear-gradient(135deg, #00C9A0, #00D084);
    }

    /* Apply colors */
    body {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    .stButton > button {
        background-color: var(--button-color);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: var(--button-hover-gradient);
        color: white;
        transform: scale(1.05);
    }

    /* Input and select styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-color: var(--secondary-color);
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 0.2rem rgba(245, 166, 35, 0.25);
    }

    /* Smooth animations */
    .stTab, .stMarkdown, .stForm {
        animation: fadeIn 0.5s ease-in-out;
    }

    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Load job data (you should replace this with your own data)
@st.cache_data
def load_job_data():
    return pd.DataFrame({
        'job': ['Software Developer', 'Data Scientist', 'UX Designer', 'Project Manager', 'Marketing Specialist'],
        'skills': ['programming', 'analytics', 'design', 'leadership', 'communication'],
        'education': ['Computer Science', 'Statistics', 'Design', 'Business', 'Marketing'],
        'personality': ['analytical', 'curious', 'creative', 'organized', 'outgoing']
    })

# Load Lottie animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Simple authentication (replace with a more secure method in production)
def authenticate(username, password):
    # This is a placeholder. In a real application, you'd check against a secure database.
    return username == "" and password == ""

# Initialize Gemini API
def initialize_gemini():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
    return model

# Generate career advice using Gemini
def generate_career_advice(model, user_input):
    prompt = f"""
    Based on the following user information, provide detailed career advice and job suggestions:
    
    Education: {user_input['education']}
    Skills: {', '.join(user_input['skills'])}
    Personality: {user_input['personality']}
    Work Experience: {user_input['work_experience']}
    Work Environment Preference: {user_input['work_environment']}
    Career Interests: {user_input['career_interests']}
    Preferred Industry: {user_input['preferred_industry']}
    Preferred Work Style: {user_input['preferred_work_style']}
    Work Location: {user_input['work_location']}
    Desired Work Schedule: {user_input['work_schedule']}
    
    Please provide:
    1. A list of 3-5 suitable job roles
    2. Brief explanations of why each role is a good fit
    3. Suggestions for skills to develop or improve
    4. Advice on how to pursue these career paths
    """
    
    safety_settings = [
        SafetySettingDict(category="HARM_CATEGORY_DANGEROUS", threshold="BLOCK_NONE"),
        SafetySettingDict(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
        SafetySettingDict(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
        SafetySettingDict(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
        SafetySettingDict(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
    ]
    
    response = model.generate_content(prompt, safety_settings=safety_settings)
    return response.text

# New function to generate a tailored resume
def generate_tailored_resume(model, resume_content, job_objective):
    prompt = f"""
    Based on the following resume content and Job Description, create a tailored resume:

    Original Resume:
    {resume_content}

    Job Description:
    {job_objective}

    Please provide a tailored resume that:
    1. Highlights relevant skills and experiences for the Job Description
    2. Adjusts the summary or objective statement to match the Job Description
    3. Reorganizes and emphasizes relevant achievements
    4. Suggests any additional skills or experiences that could be beneficial to include

    Format the resume in a clear, professional structure using Markdown.
    """

    safety_settings = [
        SafetySettingDict(category="HARM_CATEGORY_DANGEROUS", threshold="BLOCK_NONE"),
        SafetySettingDict(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
        SafetySettingDict(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
        SafetySettingDict(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
        SafetySettingDict(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
    ]

    response = model.generate_content(prompt, safety_settings=safety_settings)
    return response.text

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Main application
def main():
    # Load Lottie animation
    lottie_hello = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_M9p23l.json")

    # Session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("Career Guidance Project")
        st_lottie(lottie_hello, height=200, key="hello")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if authenticate(username, password):
                    st.session_state.authenticated = True
                else:
                    st.error("Invalid username or password")
    else:
        job_data = load_job_data()
        model = initialize_gemini()

        # Create tabs for different functionalities
        tab1, tab2 = st.tabs(["Career Advice", "Resume Builder"])

        with tab1:
            # Add h1 for Career Guidance and set color to #F3FEB8
            st.markdown("<h1 style='color:#F3FEB8;'>Career Guidance</h1>", unsafe_allow_html=True)

            # Existing career advice functionality
            education = st.radio("What's your field of study?", job_data['education'].unique())
            skills = st.multiselect("Select your top skills:", job_data['skills'].unique())
            personality = st.radio("How would you describe your personality?", job_data['personality'].unique())
            
            work_experience = st.slider("How many years of work experience do you have?", 
                min_value=0, max_value=20, step=1, value=0)
            
            work_environment = st.radio("What type of work environment do you prefer?", 
                ["Remote", "In-office", "Hybrid (a mix of remote and in-office)"])
            
            career_interests = st.radio("What areas are you most interested in pursuing?", 
                ["Technology and Development", "Marketing and Sales", "Design and Creative", 
                "Operations and Management", "Finance and Analytics"])
            
            preferred_industry = st.radio("What industry are you interested in working in?", 
                ["Technology", "Healthcare", "Finance", "Education", "Retail", "Other (please specify)"])
            
            preferred_work_style = st.radio("Do you prefer working in a team or independently?", 
                ["Team-based", "Independent", "Both"])
            
            work_location = st.selectbox("Select your country", 
                ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", 
                "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", 
                "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", 
                "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", 
                "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", 
                "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", 
                "Colombia", "Comoros", "Congo, Democratic Republic of the", "Congo, Republic of the", 
                "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czechia", "Denmark", "Djibouti", 
                "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", 
                "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", 
                "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", 
                "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", 
                "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", 
                "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", 
                "Kiribati", "Korea, North", "Korea, South", "Kosovo", "Kuwait", "Kyrgyzstan", 
                "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", 
                "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", 
                "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", 
                "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", 
                "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", 
                "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", 
                "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", 
                "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", 
                "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", 
                "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", 
                "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", 
                "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", 
                "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", 
                "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Turkey", 
                "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", 
                "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", 
                "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"])
                        
            work_schedule = st.radio("What type of work schedule do you prefer?", 
                ["9-to-5", "Flexible hours", "Part-time", "Shift work"])
            
            if st.button("Get Career Advice"):
                with st.spinner("Generating career advice..."):
                    user_input = {
                        'education': education,
                        'skills': skills,
                        'personality': personality,
                        'work_experience': work_experience,
                        'work_environment': work_environment,
                        'career_interests': career_interests,
                        'preferred_industry': preferred_industry,
                        'preferred_work_style': preferred_work_style,
                        'work_location': work_location,
                        'work_schedule': work_schedule
                    }
                    career_advice = generate_career_advice(model, user_input)
                    st.success("Here's your personalized career advice:")
                    st.markdown(career_advice)

        with tab2:
        # Resume Builder
            st.markdown("<h1 style='color:#F3FEB8;'>Resume Builder</h1>", unsafe_allow_html=True)
            st.write("Generate a tailored resume based on a given job description!")

            resume_file = st.file_uploader("Upload your resume (PDF format only):", type=["pdf"])
            job_objective = st.text_area("Paste the job description or job objective here:")
            submit_resume = st.button("Generate Tailored Resume")
            
            if submit_resume and resume_file and job_objective:
                with st.spinner("Generating tailored resume..."):
                    resume_content = extract_text_from_pdf(resume_file)
                    tailored_resume = generate_tailored_resume(model, resume_content, job_objective)
                    st.success("Here's your tailored resume:")
                    st.markdown(tailored_resume)
                    
                    # Add download button for the tailored resume
                    resume_download = tailored_resume.encode()
                    st.download_button(
                        label="Download Tailored Resume",
                        data=resume_download,
                        file_name="tailored_resume.txt",
                        mime="text/markdown"
                    )
            elif submit_resume:
                st.error("Please upload your resume and provide the job description.")

if __name__ == "__main__":
    main()