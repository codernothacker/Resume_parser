# Resume Parser Project

This project provides a tool for parsing and analyzing resumes in PDF and DOCX formats. It includes a command-line interface and a Streamlit web application for easy use.

## Features

- Parse resumes in PDF and DOCX formats
- Extract key information such as name, email, phone, skills, education, experience, and languages
- Dynamically handle additional fields found in resumes
- Generate an analysis report with insights about the parsed resumes
- Streamlit web interface for easy upload and analysis of resumes

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/resume-parser-project.git
   cd resume-parser-project
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Download the spaCy English model:
   ```
   python -m spacy download en_core_web_sm
   ```

## Usage

### Command-line Interface

To use the resume parser from the command line:

```
python enhanced_resume_parser.py /path/to/resume/directory output.csv
```

This will parse all resumes in the specified directory and save the results to `output.csv`.

### Streamlit Web Application

To run the Streamlit web application:

```
streamlit run app.py
```

This will start the web application. Open the provided URL in your web browser to use the application.
