from flask import Flask, render_template, request, send_from_directory
import google.generativeai as genai
from datetime import datetime
import os
import markdown
from bs4 import BeautifulSoup

# Configure Gemini AI
genai.configure(api_key='AIzaSyDgyy6G-qmsH8bO6UWHzptRoQHX8YLaG8U')
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'IamGood'

def format_response(text):
    """Convert markdown to HTML and add syntax highlighting"""
    html = markdown.markdown(text)
    
    # Add Tailwind classes for better formatting
    soup = BeautifulSoup(html, 'html.parser')
    
    # Style code blocks
    for pre in soup.find_all('pre'):
        pre['class'] = 'bg-gray-800 text-gray-100 p-4 rounded-md overflow-x-auto'
    
    # Style code elements
    for code in soup.find_all('code'):
        if not code.parent.name == 'pre':  # Inline code
            code['class'] = 'bg-gray-200 text-gray-800 px-1 rounded'
    
    # Style headers
    for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        h['class'] = 'font-bold my-2'
        if h.name == 'h1':
            h['class'] += ' text-2xl'
        elif h.name == 'h2':
            h['class'] += ' text-xl'
        elif h.name == 'h3':
            h['class'] += ' text-lg'
    
    # Style lists
    for ul in soup.find_all('ul'):
        ul['class'] = 'list-disc pl-5 my-2'
    for ol in soup.find_all('ol'):
        ol['class'] = 'list-decimal pl-5 my-2'
    
    # Style blockquotes
    for blockquote in soup.find_all('blockquote'):
        blockquote['class'] = 'border-l-4 border-gray-400 pl-4 my-2 italic'
    
    return str(soup)

# ... [rest of the backend code remains the same until the index route]

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'chat_history' not in app.config:
        app.config['chat_history'] = []
    
    if request.method == 'POST':
        question = request.form.get('new_string', '').strip()
        if question:
            try:
                response = model.generate_content(question)
                response_text = format_response(response.text)
                timestamp = datetime.now().strftime("%H:%M")
                app.config['chat_history'].append({
                    'question': question,
                    'response': response_text,
                    'timestamp': timestamp
                })
                if len(app.config['chat_history']) > 20:
                    app.config['chat_history'] = app.config['chat_history'][-20:]
            except Exception as e:
                print(f"Error generating response: {e}")
                app.config['chat_history'].append({
                    'question': question,
                    'response': "Sorry, I encountered an error processing your request.",
                    'timestamp': datetime.now().strftime("%H:%M")
                })
    
    return render_template('chat.html', chat_history=app.config['chat_history'])

# ... [rest of the file remains the same]

if __name__ == '__main__':
    app.run(debug=True, port=5000)