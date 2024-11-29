import re
import csv
import os
from docx import Document
from pdfminer.high_level import extract_text as extract_pdf_text
import spacy
import pandas as pd
from datetime import datetime

class EnhancedResumeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.base_fields = ["name", "email", "phone", "skills", "education", "experience", "languages"]
        self.all_fields = set(self.base_fields)

    def extract_text_from_docx(self, file_path):
        doc = Document(file_path)
        return " ".join([para.text for para in doc.paragraphs])

    def extract_text(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_extension.lower() == '.pdf':
            return extract_pdf_text(file_path)
        else:
            raise ValueError("Unsupported file format")

    def extract_name(self, text):
        doc = self.nlp(text[:200])  # Assume name is at the beginning
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None

    def extract_email(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def extract_phone(self, text):
        phone_pattern = r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None

    def extract_skills(self, text):
        skill_keywords = ["python", "java", "c++", "javascript", "sql", "machine learning", "data analysis"]
        skills = []
        for skill in skill_keywords:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                skills.append(skill)
        return skills

    def extract_education(self, text):
        education_pattern = r'(?i)(?:bachelor|master|phd|associate)(?:\s+of\s+|\s+in\s+|\s+)(?:science|arts|engineering|business|[a-z]+)'
        matches = re.findall(education_pattern, text)
        return list(set(matches))  # Remove duplicates

    def extract_experience(self, text):
        experience_pattern = r'(?i)(?:(\d+)\+?\s+years?\s+(?:of\s+)?experience|experience:\s*(\d+)\+?\s+years?)'
        match = re.search(experience_pattern, text)
        if match:
            years = match.group(1) or match.group(2)
            return f"{years} years"
        return None

    def extract_languages(self, text):
        language_pattern = r'(?i)languages?(?:\s+spoken)?:\s*((?:[a-z]+(?:,\s*|(?:\s+and\s+))?)+)'
        match = re.search(language_pattern, text)
        if match:
            languages = re.findall(r'([a-z]+)', match.group(1), re.IGNORECASE)
            return list(set(languages))  # Remove duplicates
        return []

    def extract_additional_fields(self, text):
        additional_fields = {}
        pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):\s*(.+)$'
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            field = match.group(1).lower().replace(' ', '_')
            value = match.group(2).strip()
            if field not in self.base_fields:
                additional_fields[field] = value
        return additional_fields

    def parse_resume(self, file_path):
        text = self.extract_text(file_path)
        parsed_data = {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": ", ".join(self.extract_skills(text)),
            "education": ", ".join(self.extract_education(text)),
            "experience": self.extract_experience(text),
            "languages": ", ".join(self.extract_languages(text)),
        }
        
        additional_fields = self.extract_additional_fields(text)
        parsed_data.update(additional_fields)
        
        self.all_fields.update(additional_fields.keys())
        
        return parsed_data

    def parse_resumes_to_csv(self, input_directory, output_file):
        parsed_resumes = []
        for filename in os.listdir(input_directory):
            if filename.endswith(('.docx', '.pdf')):
                file_path = os.path.join(input_directory, filename)
                try:
                    parsed_resume = self.parse_resume(file_path)
                    parsed_resume['file_name'] = filename
                    parsed_resumes.append(parsed_resume)
                except Exception as e:
                    print(f"Error parsing {filename}: {str(e)}")

        for resume in parsed_resumes:
            for field in self.all_fields:
                if field not in resume:
                    resume[field] = "NA"

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['file_name'] + list(self.all_fields)
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for resume in parsed_resumes:
                writer.writerow(resume)

    def analyze_resumes(self, csv_file):
        df = pd.read_csv(csv_file)
        
        all_skills = ', '.join(df['skills'].dropna()).split(', ')
        skill_counts = pd.Series(all_skills).value_counts()

        df['exp_years'] = df['experience'].apply(self.extract_years_of_experience)
        avg_experience = df['exp_years'].mean()

        all_education = ', '.join(df['education'].dropna()).split(', ')
        education_counts = pd.Series(all_education).value_counts()

        report = f"""
        Resume Analysis Report
        Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        Total Resumes Analyzed: {len(df)}

        Top 5 Skills:
        {skill_counts.head().to_string()}

        Average Years of Experience: {avg_experience:.2f}

        Top 3 Education Levels:
        {education_counts.head(3).to_string()}

        Additional Fields Found:
        {', '.join(set(df.columns) - set(self.base_fields) - {'file_name', 'exp_years'})}
        
        Fields with NA values:
        {', '.join(df.columns[df.eq("NA").any()].tolist())}
        """
        return report

    def extract_years_of_experience(self, experience_string):
        if pd.isna(experience_string) or experience_string == "NA":
            return 0
        match = re.search(r'(\d+)', str(experience_string))
        return int(match.group(1)) if match else 0
