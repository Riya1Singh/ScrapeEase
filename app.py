from flask import Flask, render_template,request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from auth import auth_bp, User
from models import db
from Scrape import (
     scrape_website,
     extract_body_content,
     clean_body_content,
     split_dom_content
)
from parse import parse_with_ollama

#store DOM content in session
dom_content_storage = {}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ScrapeEase.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications
app.secret_key = 'your_secret_key'  # replace with asecure key

db.init_app(app)  # Initialize SQLAlchemy

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Where to redirect if not logged in

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return render_template('index.html')


# @app.route('/scraper')
# def scraper():
#     return render_template('scraper.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/main')

def main():
    return render_template('main.html')


@app.route('/scrape', methods=['GET','POST'])
def scrape():
    url = request.form.get('url')
    prompt = request.form.get('prompt')

    if not url or not prompt:
        return jsonify({'success': False, 'error': 'URL and Prompt are required.'})
    
    try:  
            # Scrape the website
            dom_content = scrape_website(url)
            body_content = extract_body_content(dom_content)
            cleaned_content = clean_body_content(body_content)

             # Store the DOM content
            dom_content_storage['content'] = cleaned_content
            
            return jsonify({
                'success': True,
                'content': cleaned_content
            })
    except Exception as e:
            return jsonify({'success': False,'error': str(e)
            })
    

@app.route('/parse', methods=['GET','POST'])
def parse():
    parse_description = request.form.get('parse_description')
    if not parse_description:
        return jsonify({
            'success': False,
            'error': 'No parse description provided'
        })
    
    if 'content' not in dom_content_storage:
        return jsonify({
            'success': False,
            'error': 'Please scrape a website first'
        })
    
    try:
        # Parse the content with Ollama
        dom_chunks = split_dom_content(dom_content_storage['content'])
        parsed_result = parse_with_ollama(dom_chunks, parse_description)
        return jsonify({
            'success': True,
            'result': parsed_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True,host='0.0.0.0')
   
    


   

