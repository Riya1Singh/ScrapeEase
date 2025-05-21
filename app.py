from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, flash
from flask_login import current_user, login_required
import json
import sqlite3
import os
import sys
import asyncio
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
from auth import auth_bp, User
from models import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
import warnings
warnings.filterwarnings("ignore",module="streamlit")
from flask_mail import Mail, Message



# Import functions from the original project
sys.path.append("..")  # Add parent directory to path
from functions.scraper import scrape_urls
from functions.pagination import paginate_urls
from functions.markdown import fetch_and_store_markdowns
from services.assets import MODELS_USED
from functions.api_management import initialize_db

# Only use WindowsProactorEventLoopPolicy on Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure value in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ScrapeEase.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db.init_app(app)  # Initialize SQLAlchemy

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' 


# Initialize Flask-Mail

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
<<<<<<< HEAD
app.config['MAIL_USERNAME'] = 'scrapeease@gmail.com'
app.config['MAIL_PASSWORD'] = 'epoa qajq dyeu dadi'  # Use App Password for Gmail
=======
app.config['MAIL_USERNAME'] = 'scrapeease@gmail.com'  # Replace with your actual Gmail
app.config['MAIL_PASSWORD'] = 'jnku gdge fjak pipz'  # Replace with your actual App Password
app.config.update(
    MAIL_DEFAULT_SENDER='scrapeease@gmail.com'
)
>>>>>>> a735594a6849addef7ce6aeaa8d8c231daee0ac0
mail = Mail(app)



#Generate a password reset token

from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(app.secret_key)

def generate_reset_token(email):
    return serializer.dumps(email, salt='password-reset-salt')

def confirm_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email



#route to request password reset
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            email = request.form['email']
            user = User.query.filter_by(email=email).first()
            if user:
                token = generate_reset_token(email)
                reset_url = url_for('reset_password', token=token, _external=True)
                msg = Message(
                    'Password Reset Request - ScrapeEase',
                    recipients=[email],
                    html=render_template(
                        'email/reset_password.html',
                        reset_url=reset_url,
                        username=user.username
                    )
                )
                mail.send(msg)
                flash('Password reset link has been sent to your email.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('No user found with that email address.', 'error')
        except Exception as e:
            flash('An error occurred. Please try again later.', 'error')
            print(f"Password reset error: {str(e)}")  # For debugging
    return render_template('forgot_password.html')


#route to handle reset link and update password
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = confirm_token(token)
        if not email:
            flash('The password reset link is invalid or has expired.', 'error')
            return redirect(url_for('forgot_password'))

        if request.method == 'POST':
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('reset_password.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return render_template('reset_password.html')

            user = User.query.filter_by(email=email).first()
            if user:
                from bcrypt import hashpw, gensalt
                hashed_password = hashpw(password.encode('utf-8'), gensalt())
                user.password = hashed_password.decode('utf-8')
                db.session.commit()
                flash('Your password has been updated successfully.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('User not found.', 'error')
                return redirect(url_for('forgot_password'))
                
        return render_template('reset_password.html')
    except Exception as e:
        flash('An error occurred. Please try again.', 'error')
        print(f"Password reset error: {str(e)}")  # For debugging
        return redirect(url_for('forgot_password'))

    return render_template('reset_password.html')


#feedback form route
@app.route('/feedback')
def feedback_form():
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    username = request.form.get('username')
    reviews = request.form.get('review')
    fun_meter = request.form.get('fun_meter')

    # Connect to database
    conn = sqlite3.connect('instance/ScrapeEase.db')
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            review TEXT,
            fun_meter INTEGER
        )
    ''')

    # Insert the feedback
    cursor.execute("INSERT INTO feedback (username, review, fun_meter) VALUES (?, ?, ?)", 
                   (username, reviews, fun_meter))

    conn.commit()
    conn.close()

    return redirect('/thank_you')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')




@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Make sure the database is initialized
db_initialized = False

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(auth_bp)
# Add custom filters to Jinja environment
@app.template_filter('fromjson')
def fromjson(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}

@app.template_filter('get_item')
def get_item(obj, key):
    """Get an item from an object safely"""
    if isinstance(obj, dict):
        return obj.get(key, '')
    return ''

# Add now() function to Jinja environment
@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    return dict(now=now, models=MODELS_USED)

@app.route('/main', methods=['GET'])
@login_required
def main():
    global db_initialized
    
    if not db_initialized:
        db_initialized = initialize_db()
    
    # Pass the complete models dictionary to the template
    return render_template('main.html', models=MODELS_USED)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
@login_required
def scrape():
    # Get form data
    urls = request.form.getlist('urls[]')
    fields = request.form.getlist('fields[]')
    model_selection = request.form.get('model_selection', 'gemini')  # Default model changed to gemini
    use_pagination = request.form.get('use_pagination') == 'true'
    pagination_details = request.form.get('pagination_details', '')
    max_output_tokens = int(request.form.get('max_output_tokens', 8192))  # Increased to 8192 to handle more data
    
    # Store in session
    session['urls'] = urls
    session['fields'] = fields
    session['model_selection'] = model_selection
    session['use_pagination'] = use_pagination
    session['pagination_details'] = pagination_details
    session['max_output_tokens'] = max_output_tokens
    
    # Process data
    try:
        print(f"Starting scraping process for {len(urls)} URLs with fields: {fields}")
        
        if not urls:
            raise ValueError("No URLs provided")
            
        # Fetch or reuse the markdown for each URL
        unique_names = fetch_and_store_markdowns(urls)
        if not unique_names:
            raise ValueError("Failed to process URLs")
            
        session['unique_names'] = unique_names
        
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0
        all_data = []
        pagination_info = None
        
        print(f"Successfully processed {len(unique_names)} unique URLs")
        
        # 1) Scraping logic
        if fields:
            in_tokens_s, out_tokens_s, cost_s, parsed_data = scrape_urls(
                unique_names,
                fields,
                model_selection,
                max_output_tokens=max_output_tokens
            )
            total_input_tokens += in_tokens_s
            total_output_tokens += out_tokens_s
            total_cost += cost_s
            
            # Process the parsed data
            processed_data = []
            for item in parsed_data:
                if isinstance(item, dict):
                    # If it's already a dictionary, keep it as is
                    parsed = json.loads(item["parsed_data"]) if isinstance(item["parsed_data"], str) else item["parsed_data"]
                    if "listings" in parsed:
                        item["parsed_data"] = parsed
                        processed_item = item
                    else:
                        processed_item = {"parsed_data": {"listings": [parsed]}}
                elif isinstance(item, str):
                    # If it's a string, try to parse it as JSON
                    try:
                        parsed = json.loads(item)
                        if "listings" in parsed:
                            processed_item = {"parsed_data": parsed}
                        else:
                            processed_item = {"parsed_data": {"listings": [parsed]}}
                        print(f"Successfully parsed JSON string: {type(processed_item)}")
                    except json.JSONDecodeError:
                        processed_item = {"parsed_data": {"listings": [{"content": item}]}}
                        print(f"Failed to parse as JSON, keeping as string")
                else:
                    processed_item = {"parsed_data": {"listings": [{"content": str(item)}]}}
                    print(f"Non-string, non-dict item: {type(item)}")
                
                processed_data.append(processed_item)
            
            # Debug print to see the structure and concatenate listings from all URLs
            total_listings = 0
            for pd in processed_data:
                if "listings" in pd["parsed_data"]:
                    total_listings += len(pd["parsed_data"]["listings"])
            print(f"PROCESSED DATA STRUCTURE: Total listings across all URLs: {total_listings}")
            all_data = processed_data
            print(all_data)
            session['in_tokens_s'] = in_tokens_s
            session['out_tokens_s'] = out_tokens_s
            session['cost_s'] = cost_s
        
        # 2) Pagination logic
        if use_pagination:
            in_tokens_p, out_tokens_p, cost_p, page_results = paginate_urls(
                unique_names,
                model_selection,
                pagination_details,
                urls,
                max_output_tokens=max_output_tokens
            )
            total_input_tokens += in_tokens_p
            total_output_tokens += out_tokens_p
            total_cost += cost_p
            pagination_info = page_results
            pagination_info[0]["pagination_data"] = json.loads(pagination_info[0]["pagination_data"]) if isinstance(pagination_info[0]["pagination_data"], str) else pagination_info[0]["pagination_data"]
            
            
            print("Pagination results:", pagination_info)
            
            session['in_tokens_p'] = in_tokens_p
            session['out_tokens_p'] = out_tokens_p
            session['cost_p'] = cost_p
        
        # Save results to session
        try:
            # parsed_data = json.loads(all_data) if isinstance(all_data, str) else all_data
            session['results'] = {
                'data': all_data,
                'input_tokens': total_input_tokens,
                'output_tokens': total_output_tokens,
                'total_cost': total_cost,
                'pagination_info': pagination_info
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing scraped data: {str(e)}")
            session['results'] = {
                'data': [],
                'input_tokens': total_input_tokens,
                'output_tokens': total_output_tokens,
                'total_cost': total_cost,
                'pagination_info': pagination_info.get('page_urls', []) if isinstance(pagination_info, dict) else []
            }
        
        return jsonify({'status': 'success', 'message': 'Scraping completed successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An error occurred during scraping: {str(e)}'})

@app.route('/results', methods=['GET'])
@login_required
def results():
    # Get results from session
    results = session.get('results', None)
    
    if not results:
        return redirect(url_for('index'))
    
    return render_template('results.html', results=results)

@app.route('/download_json', methods=['GET'])
@login_required
def download_json():
    results = session.get('results', None)
    
    if not results or not results.get('data'):
        print("No results data found for JSON download")
        return redirect(url_for('index'))
    
    try:
        print(f"Preparing JSON download with {len(results['data'])} items")
        json_data = json.dumps(
            results['data'],
            default=lambda o: o.dict() if hasattr(o, 'dict') else str(o),
            indent=4
        )
        
        # Create a BytesIO object
        bytes_io = BytesIO(json_data.encode('utf-8'))
        bytes_io.seek(0)  # Ensure cursor is at the beginning
        
        # Return the file
        return send_file(
            bytes_io,
            mimetype='application/json',
            as_attachment=True,
            download_name='scraped_data.json'
        )
    except Exception as e:
        print(f"Error downloading JSON: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_csv', methods=['GET'])
@login_required
def download_csv():
    results = session.get('results', None)
    
    if not results or not results.get('data'):
        print("No results data found for CSV download")
        return redirect(url_for('index'))
    
    try:
        # Convert all data to a single DataFrame
        all_listings = []
        print(f"Processing {len(results['data'])} items for CSV download")
        
        for data in results['data']:
            if isinstance(data, dict) and "parsed_data" in data:
                # Extract parsed_data if it exists
                parsed_data = data["parsed_data"]
                if isinstance(parsed_data, dict) and "listings" in parsed_data:
                    all_listings.extend(parsed_data["listings"])
                else:
                    all_listings.append(parsed_data)
            elif isinstance(data, dict) and "listings" in data:
                all_listings.extend(data["listings"])
            elif isinstance(data, str):
                try:
                    parsed = json.loads(data)
                    if isinstance(parsed, dict) and "listings" in parsed:
                        all_listings.extend(parsed["listings"])
                    else:
                        all_listings.append(parsed)
                except json.JSONDecodeError:
                    all_listings.append({"content": data})
            else:
                all_listings.append(data)
        
        print(f"Generated {len(all_listings)} listings for CSV")
        
        # Handle empty listings
        if not all_listings:
            all_listings = [{"empty": "No data available"}]
        
        # Convert to DataFrame
        combined_df = pd.DataFrame(all_listings)
        csv_data = combined_df.to_csv(index=False).encode('utf-8')
        
        # Create a BytesIO object
        bytes_io = BytesIO(csv_data)
        bytes_io.seek(0)  # Ensure cursor is at the beginning
        
        return send_file(
            bytes_io,
            mimetype='text/csv',
            as_attachment=True,
            download_name='scraped_data.csv'
        )
    except Exception as e:
        print(f"Error downloading CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_pagination_csv', methods=['GET'])
def download_pagination_csv():
    results = session.get('results', None)
    
    if not results or not results.get('pagination_info'):
        print("No pagination info found for CSV download")
        return redirect(url_for('index'))
    
    try:
        # Process pagination info
        all_page_rows = []
        print(f"Processing {len(results['pagination_info'])} pagination items for CSV")
        
        for item in results['pagination_info']:
            if not isinstance(item, dict):
                continue
                
            if "pagination_data" in item:
                pag_obj = item["pagination_data"]
                
                # Convert if it's a Pydantic model
                if hasattr(pag_obj, "dict"):
                    pag_obj = pag_obj.model_dump()
                elif isinstance(pag_obj, str):
                    try:
                        pag_obj = json.loads(pag_obj)
                    except json.JSONDecodeError:
                        pass
                        
                item["pagination_data"] = pag_obj
            
            pd_obj = item["pagination_data"]
            
            if (
                isinstance(pd_obj, dict)
                and "page_urls" in pd_obj
                and isinstance(pd_obj["page_urls"], list)
            ):
                for page_url in pd_obj["page_urls"]:
                    row_dict = {"page_url": page_url}
                    all_page_rows.append(row_dict)
            else:
                row_dict = dict(item)
                all_page_rows.append(row_dict)
        
        print(f"Generated {len(all_page_rows)} page URLs for CSV")
        
        # Handle empty data
        if not all_page_rows:
            all_page_rows = [{"empty": "No pagination URLs available"}]
        
        pagination_df = pd.DataFrame(all_page_rows)
        csv_data = pagination_df.to_csv(index=False).encode('utf-8')
        
        # Create a BytesIO object
        bytes_io = BytesIO(csv_data)
        bytes_io.seek(0)  # Ensure cursor is at the beginning
        
        return send_file(
            bytes_io,
            mimetype='text/csv',
            as_attachment=True,
            download_name='pagination_urls.csv'
        )
    except Exception as e:
        print(f"Error downloading pagination CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_pagination_json', methods=['GET'])
def download_pagination_json():
    results = session.get('results', None)
    
    if not results or not results.get('pagination_info'):
        print("No pagination info found for JSON download")
        return redirect(url_for('index'))
    
    try:
        # Process pagination info
        all_page_rows = []
        print(f"Processing {len(results['pagination_info'])} pagination items for JSON")
        
        for item in results['pagination_info']:
            if not isinstance(item, dict):
                continue
                
            if "pagination_data" in item:
                pag_obj = item["pagination_data"]
                
                # Convert if it's a Pydantic model
                if hasattr(pag_obj, "dict"):
                    pag_obj = pag_obj.model_dump()
                elif isinstance(pag_obj, str):
                    try:
                        pag_obj = json.loads(pag_obj)
                    except json.JSONDecodeError:
                        pass
                        
                item["pagination_data"] = pag_obj
            
            pd_obj = item["pagination_data"]
            
            if (
                isinstance(pd_obj, dict)
                and "page_urls" in pd_obj
                and isinstance(pd_obj["page_urls"], list)
            ):
                for page_url in pd_obj["page_urls"]:
                    row_dict = {"page_url": page_url}
                    all_page_rows.append(row_dict)
            else:
                row_dict = dict(item)
                all_page_rows.append(row_dict)
        
        print(f"Generated {len(all_page_rows)} page URLs for JSON")
        
        # Handle empty data
        if not all_page_rows:
            all_page_rows = [{"empty": "No pagination URLs available"}]
        
        json_data = json.dumps(all_page_rows, indent=4)
        
        # Create a BytesIO object
        bytes_io = BytesIO(json_data.encode('utf-8'))
        bytes_io.seek(0)  # Ensure cursor is at the beginning
        
        return send_file(
            bytes_io,
            mimetype='application/json',
            as_attachment=True,
            download_name='pagination_urls.json'
        )
    except Exception as e:
        print(f"Error downloading pagination JSON: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_results', methods=['POST'])
def clear_results():
    # Clear session data
    session.pop('results', None)
    session.pop('in_tokens_s', None)
    session.pop('out_tokens_s', None)
    session.pop('cost_s', None)
    session.pop('in_tokens_p', None)
    session.pop('out_tokens_p', None)
    session.pop('cost_p', None)
    
    return jsonify({'status': 'success'})

@app.route('/api_keys', methods=['POST'])
def update_api_keys():
    for model, required_keys in MODELS_USED.items():
        for key_name in required_keys:
            key_value = request.form.get(key_name)
            if key_value:
                os.environ[key_name] = key_value
    
    # Update DATABASE_URL if provided
    database_url = request.form.get('DATABASE_URL')
    if database_url:
        os.environ['DATABASE_URL'] = database_url
    
    return jsonify({'status': 'success', 'message': 'API keys updated successfully!'})


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=False,host='0.0.0.0') 