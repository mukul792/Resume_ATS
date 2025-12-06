import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_repsonse(input_prompt_text):
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(input_prompt_text)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() if page.extract_text() else ""
    return text

input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving thr resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

st.title("Smart ATS: Resume Evaluator")
st.markdown("Improve Your Resume for Application Tracking Systems (ATS)")

jd = st.text_area("✍️ Paste the Job Description Here")
uploaded_file = st.file_uploader("⬆️ Upload Your Resume (PDF)", type="pdf", help="Please upload your resume in PDF format.")

submit = st.button("Submit & Evaluate Resume")

if submit:
    if uploaded_file is not None:
        with st.spinner('Evaluating your resume...'):
            resume_text = input_pdf_text(uploaded_file)
            full_prompt = input_prompt.format(text=resume_text, jd=jd)
            json_response_string = get_gemini_repsonse(full_prompt)
            
            try:
                data = json.loads(json_response_string)
                
                st.markdown("---")
                st.subheader("✅ ATS Evaluation Results")
                
                match_percent = data.get("JD Match", "N/A")
                if match_percent != "N/A":
                    st.metric(label="Job Description Match Score", value=match_percent)
                
                st.subheader("🔑 Missing Keywords")
                missing_keywords = data.get("MissingKeywords", [])
                if missing_keywords:
                    st.warning("⚠️ **To increase your score, consider adding these keywords to your resume:**")
                    st.markdown(f"> **{', '.join(missing_keywords)}**")
                else:
                    st.success("Great job! Your resume appears to cover all key terms.")
                
                st.subheader("📝 Profile Summary & Improvement Suggestions")
                profile_summary = data.get("Profile Summary", "No detailed summary provided.")
                st.info(profile_summary)
                st.markdown("---")
                
            except json.JSONDecodeError:
                st.error("🚨 Error: Could not parse the response from the AI. The output might not be in the expected JSON format.")
                st.text("Raw Response:")
                st.code(json_response_string)
    
    else:
        st.error("Please upload a PDF file to proceed with the evaluation.")