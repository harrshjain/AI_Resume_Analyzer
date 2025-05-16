import streamlit as st
import PyPDF2, configparser, io
from openai import OpenAI

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📃", layout="centered")
st.title("AI Resume Analyzer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")


config = configparser.ConfigParser()
config.read("config.ini")

API_KEY = config["OPENAI_API"]["API_KEY"]

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
job_role = st.text_input("Enter the job role you're targeting (optional)")
analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if analyze and not uploaded_file:
    st.error("Please upload your resume!!", icon="❗")

elif analyze and uploaded_file:
    with st.spinner("Analyzing your resume..."):
        try:
            uploaded_file.seek(0)
            file_content = extract_text_from_file(uploaded_file)
            
            if not file_content.strip():
                st.error("File does not have any content...")
                st.stop()
            
            if not API_KEY:
                st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
                st.stop()
            
            prompt = f"""Please analyze this resume and provide constructive feedback. 
            Focus on the following aspects:
            1. Content clarity and impact
            2. Skills presentation
            3. Experience descriptions
            4. Specific improvements for {job_role if job_role else 'general job applications'}
            
            Resume content:
            {file_content}
            
            Please provide your analysis in a clear, structured format with specific recommendations."""
            
            client = OpenAI(api_key=API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            st.success("Analysis complete!")
            st.markdown("### Resume Analysis Results")
            
            analysis_text = response.choices[0].message.content
            st.markdown(analysis_text)
            
            st.download_button(
                label="Download Analysis",
                data=analysis_text,
                file_name="resume_analysis.txt",
                mime="text/plain"
            )
        
        except PyPDF2.errors.PdfReadError:
            st.error("Error reading PDF file. Please ensure it's a valid PDF document.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            

st.markdown("---")
st.markdown("""
**How to use this app:**
1. Upload your resume in PDF or TXT format
2. Optionally enter your target job role for more tailored feedback
3. Click "Analyze Resume" to get AI-powered feedback
""")