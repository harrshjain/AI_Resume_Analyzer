from flask import Flask, jsonify, request
from openai import OpenAI
import configparser, PyPDF2, io, textwrap


app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

API_KEY = config["OPENAI_API"]["API_KEY"]

client = OpenAI(api_key=API_KEY)

def extract_text_from_pdf(resume):
    pdf_reader = PyPDF2.PdfReader(resume)
    text_extracted = ""
    for page in pdf_reader.pages:
        text_extracted += page.extract_text() + "\n"
    
    return text_extracted

def extract_text_from_file(resume, file_type):
    if file_type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(resume.read()))
    
    return resume.read().decode("utf-8")



@app.route("/api/v1/resume_parser", methods=["POST"])
def resume_analyzer():
    """
    Analyses Resume PDF file and give inputs

    input: PDF file

    output: summary of the resume
    """
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No file in the request"}), 400
        
        resume = request.files["resume"]

        if resume.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400
        
        if not resume.filename.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        job_role = request.form.get("job_role", "")
        
        file_content = extract_text_from_file(resume, resume.content_type)
        
        
        prompt = f"""Please analyze this resume and provide constructive feedback. 
            Focus on the following aspects:
            1. Content clarity and impact
            2. Skills presentation
            3. Experience descriptions
            4. Specific improvements for {job_role if job_role else 'general job applications'}
            
            Resume content:
            {file_content}
            
            Please provide your analysis in a clear, structured format with specific recommendations."""


        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume reviewer with years of experience in HR and recruitment."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )

        final_response = response.choices[0].message.content
        
        return jsonify({"analysis": final_response}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
