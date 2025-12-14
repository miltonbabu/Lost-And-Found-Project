"""
Lost and Found Management System
A beginner-friendly Flask application for managing lost and found items.
"""

import sqlite3
from datetime import datetime
from functools import wraps
import os
import uuid
import difflib
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database configuration
DATABASE = 'lost_and_found.db'

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    with app.app_context():
        db = get_db()
        # Read and execute schema file
        with open('schema.sql', 'r') as f:
            schema = f.read()
        db.executescript(schema)
        db.commit()


def find_similar_items(item_type, item_data):
    """Find similar items based on category, name, location, and date proximity.
    
    Args:
        item_type: 'lost' or 'found' - the type of item being reported
        item_data: dict with item details (item_name, category, location, lost_date/found_date)
    
    Returns:
        List of similar items sorted by similarity score
    """
    db = get_db()
    
    # Determine which tables and columns to use based on item type
    if item_type == 'lost':
        # For lost items, look for similar found items
        compare_table = 'found_items'
        compare_date_col = 'found_date'
        target_status = 'unclaimed'  # Only match with unclaimed found items
    else:
        # For found items, look for similar lost items
        compare_table = 'lost_items'
        compare_date_col = 'lost_date'
        target_status = 'unclaimed'  # Only match with unclaimed lost items
    
    # Get all relevant unclaimed items from the comparison table
    compare_items = db.execute(
        f'SELECT * FROM {compare_table} WHERE status = ? ORDER BY created_at DESC',
        (target_status,)
    ).fetchall()
    
    if not compare_items:
        return []
    
    # Extract item data
    item_name = item_data.get('item_name', '').lower()
    item_category = item_data.get('category', '').lower()
    item_location = item_data.get('location', '').lower()
    
    # Parse date
    item_date_str = item_data.get('lost_date' if item_type == 'lost' else 'found_date', '')
    try:
        item_date = datetime.strptime(item_date_str, '%Y-%m-%d')
    except ValueError:
        item_date = None
    
    similar_items = []
    
    for compare_item in compare_items:
        # Calculate similarity scores
        score = 0
        reasons = []
        
        # Compare categories (exact match gives high score)
        compare_category = compare_item['category'].lower()
        if item_category == compare_category:
            score += 40
            reasons.append(f"Same category: {item_category}")
        
        # Compare item names (using difflib for similarity)
        compare_name = compare_item['item_name'].lower()
        name_similarity = difflib.SequenceMatcher(None, item_name, compare_name).ratio()
        if name_similarity > 0.6:
            score += int(name_similarity * 30)
            reasons.append(f"Similar name ({int(name_similarity * 100)}% match)")
        
        # Compare locations (using difflib for similarity)
        compare_location = compare_item['location'].lower()
        location_similarity = difflib.SequenceMatcher(None, item_location, compare_location).ratio()
        if location_similarity > 0.5:
            score += int(location_similarity * 20)
            reasons.append(f"Similar location ({int(location_similarity * 100)}% match)")
        
        # Compare dates (proximity gives score)
        if item_date:
            try:
                compare_date = datetime.strptime(compare_item[compare_date_col], '%Y-%m-%d')
                date_diff = abs((item_date - compare_date).days)
                if date_diff <= 7:
                    score += max(0, 10 - date_diff)  # 10 points for same day, decreasing by 1 per day
                    reasons.append(f"Reported {date_diff} days apart")
            except ValueError:
                pass
        
        # Only consider items with meaningful similarity score
        if score >= 30:
            similar_items.append({
                'item': compare_item,
                'score': score,
                'reasons': reasons,
                'item_type': 'found' if compare_table == 'found_items' else 'lost'
            })
    
    # Sort by score descending
    similar_items.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top 5 matches
    return similar_items[:5]

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with admin and user options"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        # Check if user exists and verify password
        if user:
            stored_password = user['password']
            
            # For demo users, check against common passwords
            if username in ['admin', 'user'] and password in ['admin123', 'user123']:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_role'] = user['role']
                session['full_name'] = user['full_name']
                
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return redirect(url_for('index'))
            
            # For other users, check if password matches stored format
            elif stored_password.endswith('_hash'):
                # Remove _hash suffix and compare with actual password
                expected_password = stored_password[:-5]  # Remove '_hash'
                if password == expected_password:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['user_role'] = user['role']
                    session['full_name'] = user['full_name']
                    
                    flash(f'Welcome back, {user["full_name"]}!', 'success')
                    return redirect(url_for('index'))
        
        flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration page"""
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Basic validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters long')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if username already exists
        db = get_db()
        existing_user = db.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if existing_user:
            errors.append('Username already exists. Please choose another.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('signup.html')
        
        # Create new user
        db.execute(
            '''INSERT INTO users (username, password, email, full_name, role)
               VALUES (?, ?, ?, ?, ?)''',
            (username, password + '_hash', email, full_name, 'user')
        )
        db.commit()
        
        flash('Registration successful! Please login with your new account.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

# Routes

@app.route('/')
@login_required
def index():
    """Home page - show overview of lost and found items"""
    db = get_db()
    
    # Get recent lost items
    lost_items = db.execute(
        'SELECT * FROM lost_items WHERE status = "unclaimed" ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    
    # Get recent found items
    found_items = db.execute(
        'SELECT * FROM found_items WHERE status = "unclaimed" ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    
    # Get statistics
    lost_count = db.execute('SELECT COUNT(*) FROM lost_items WHERE status = "unclaimed"').fetchone()[0]
    found_count = db.execute('SELECT COUNT(*) FROM found_items WHERE status = "unclaimed"').fetchone()[0]
    claimed_count = db.execute(
        'SELECT COUNT(*) FROM lost_items WHERE status = "claimed" UNION '
        'SELECT COUNT(*) FROM found_items WHERE status = "claimed"'
    ).fetchall()
    total_claimed = sum(row[0] for row in claimed_count)
    
    return render_template('index.html', 
                         lost_items=lost_items, 
                         found_items=found_items,
                         lost_count=lost_count,
                         found_count=found_count,
                         claimed_count=total_claimed)

@app.route('/lost')
@login_required
def list_lost():
    """List all lost items"""
    db = get_db()
    items = db.execute(
        'SELECT * FROM lost_items ORDER BY created_at DESC'
    ).fetchall()
    return render_template('lost_items.html', items=items, title='Lost Items')

@app.route('/found')
@login_required
def list_found():
    """List all found items"""
    db = get_db()
    items = db.execute(
        'SELECT * FROM found_items ORDER BY created_at DESC'
    ).fetchall()
    return render_template('found_items.html', items=items, title='Found Items')

@app.route('/report/lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    """Report a lost item"""
    if request.method == 'POST':
        # Get form data
        item_name = request.form['item_name']
        category = request.form['category']
        description = request.form.get('description', '')
        lost_date = request.form['lost_date']
        location = request.form['location']
        contact_name = request.form['contact_name']
        contact_email = request.form.get('contact_email', '')
        contact_phone = request.form.get('contact_phone', '')
        
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        # Insert into database
        db = get_db()
        db.execute(
            '''INSERT INTO lost_items 
               (item_name, category, description, lost_date, location, 
                contact_name, contact_email, contact_phone, image_filename, user_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (item_name, category, description, lost_date, location, 
             contact_name, contact_email, contact_phone, image_filename, session['user_id'])
        )
        db.commit()
        
        # Check for similar found items after reporting
        item_data = {
            'item_name': item_name,
            'category': category,
            'location': location,
            'lost_date': lost_date
        }
        similar_items = find_similar_items('lost', item_data)
        
        if similar_items:
            flash('Lost item reported successfully! We found some similar unclaimed found items that might be yours.', 'success')
            return render_template('similar_items.html', 
                                original_item_type='lost',
                                original_item_name=item_name,
                                similar_items=similar_items,
                                title='Similar Found Items')
        else:
            flash('Lost item reported successfully!', 'success')
            return redirect(url_for('list_lost'))
    
    return render_template('report_lost.html')

@app.route('/report/found', methods=['GET', 'POST'])
@login_required
def report_found():
    """Report a found item"""
    if request.method == 'POST':
        # Get form data
        item_name = request.form['item_name']
        category = request.form['category']
        description = request.form.get('description', '')
        found_date = request.form['found_date']
        location = request.form['location']
        contact_name = request.form['contact_name']
        contact_email = request.form.get('contact_email', '')
        contact_phone = request.form.get('contact_phone', '')
        
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        # Insert into database
        db = get_db()
        db.execute(
            '''INSERT INTO found_items 
               (item_name, category, description, found_date, location, 
                contact_name, contact_email, contact_phone, image_filename, user_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (item_name, category, description, found_date, location, 
             contact_name, contact_email, contact_phone, image_filename, session['user_id'])
        )
        db.commit()
        
        # Check for similar lost items after reporting
        item_data = {
            'item_name': item_name,
            'category': category,
            'location': location,
            'found_date': found_date
        }
        similar_items = find_similar_items('found', item_data)
        
        if similar_items:
            flash('Found item reported successfully! We found some similar unclaimed lost items that might match what you found.', 'success')
            return render_template('similar_items.html', 
                                original_item_type='found',
                                original_item_name=item_name,
                                similar_items=similar_items,
                                title='Similar Lost Items')
        else:
            flash('Found item reported successfully!', 'success')
            return redirect(url_for('list_found'))
    
    return render_template('report_found.html')

@app.route('/item/lost/<int:item_id>')
@login_required
def view_lost_item(item_id):
    """View details of a specific lost item"""
    db = get_db()
    item = db.execute(
        'SELECT * FROM lost_items WHERE id = ?', (item_id,)
    ).fetchone()
    
    if item is None:
        flash('Item not found!', 'error')
        return redirect(url_for('list_lost'))
    
    return render_template('view_lost_item.html', item=item)

@app.route('/item/found/<int:item_id>')
@login_required
def view_found_item(item_id):
    """View details of a specific found item"""
    db = get_db()
    item = db.execute(
        'SELECT * FROM found_items WHERE id = ?', (item_id,)
    ).fetchone()
    
    if item is None:
        flash('Item not found!', 'error')
        return redirect(url_for('list_found'))
    
    return render_template('view_found_item.html', item=item)

@app.route('/claim/lost/<int:item_id>', methods=['GET', 'POST'])
@login_required
def claim_lost_item(item_id):
    """Claim a lost item"""
    db = get_db()
    item = db.execute(
        'SELECT * FROM lost_items WHERE id = ?', (item_id,)
    ).fetchone()
    
    if item is None:
        flash('Item not found!', 'error')
        return redirect(url_for('list_lost'))
    
    if request.method == 'POST':
        claimant_name = request.form['claimant_name']
        claimant_email = request.form.get('claimant_email', '')
        claimant_phone = request.form.get('claimant_phone', '')
        claim_description = request.form.get('claim_description', '')
        
        # Insert claim record
        db.execute(
            '''INSERT INTO claims 
               (item_type, item_id, claimant_name, claimant_email, 
                claimant_phone, claim_description)
               VALUES (?, ?, ?, ?, ?, ?)''',
            ('lost', item_id, claimant_name, claimant_email, 
             claimant_phone, claim_description)
        )
        
        # Update item status
        db.execute(
            'UPDATE lost_items SET status = "claimed", updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (item_id,)
        )
        db.commit()
        
        flash('Item claimed successfully! We will contact you soon.', 'success')
        return redirect(url_for('list_lost'))
    
    return render_template('claim_item.html', item=item, item_type='lost')

@app.route('/claim/found/<int:item_id>', methods=['GET', 'POST'])
@login_required
def claim_found_item(item_id):
    """Claim a found item"""
    db = get_db()
    item = db.execute(
        'SELECT * FROM found_items WHERE id = ?', (item_id,)
    ).fetchone()
    
    if item is None:
        flash('Item not found!', 'error')
        return redirect(url_for('list_found'))
    
    if request.method == 'POST':
        claimant_name = request.form['claimant_name']
        claimant_email = request.form.get('claimant_email', '')
        claimant_phone = request.form.get('claimant_phone', '')
        claim_description = request.form.get('claim_description', '')
        
        # Insert claim record
        db.execute(
            '''INSERT INTO claims 
               (item_type, item_id, claimant_name, claimant_email, 
                claimant_phone, claim_description)
               VALUES (?, ?, ?, ?, ?, ?)''',
            ('found', item_id, claimant_name, claimant_email, 
             claimant_phone, claim_description)
        )
        
        # Update item status
        db.execute(
            'UPDATE found_items SET status = "claimed", updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (item_id,)
        )
        db.commit()
        
        flash('Item claimed successfully! We will contact you soon.', 'success')
        return redirect(url_for('list_found'))
    
    return render_template('claim_item.html', item=item, item_type='found')

@app.route('/delete/lost/<int:item_id>', methods=['POST'])
@login_required
def delete_lost(item_id):
    """Delete a lost item (only admin or item reporter can delete)"""
    db = get_db()
    
    # Get the item to check ownership
    item = db.execute('SELECT * FROM lost_items WHERE id = ?', (item_id,)).fetchone()
    
    if not item:
        flash('Item not found!', 'error')
        return redirect(url_for('list_lost'))
    
    # Check if user is admin or the one who reported it
    if session['user_role'] != 'admin' and session['user_id'] != item['user_id']:
        flash('You do not have permission to delete this item.', 'error')
        return redirect(url_for('list_lost'))
    
    # Delete the item
    db.execute('DELETE FROM lost_items WHERE id = ?', (item_id,))
    db.commit()
    
    flash('Lost item deleted successfully!', 'success')
    return redirect(url_for('list_lost'))

@app.route('/delete/found/<int:item_id>', methods=['POST'])
@login_required
def delete_found(item_id):
    """Delete a found item (only admin or item reporter can delete)"""
    db = get_db()
    
    # Get the item to check ownership
    item = db.execute('SELECT * FROM found_items WHERE id = ?', (item_id,)).fetchone()
    
    if not item:
        flash('Item not found!', 'error')
        return redirect(url_for('list_found'))
    
    # Check if user is admin or the one who reported it
    if session['user_role'] != 'admin' and session['user_id'] != item['user_id']:
        flash('You do not have permission to delete this item.', 'error')
        return redirect(url_for('list_found'))
    
    # Delete the item
    db.execute('DELETE FROM found_items WHERE id = ?', (item_id,))
    db.commit()
    
    flash('Found item deleted successfully!', 'success')
    return redirect(url_for('list_found'))

@app.route('/admin')
@admin_required
def admin():
    """Admin dashboard - view all items and claims"""
    db = get_db()
    
    # Get all items with their status
    lost_items = db.execute('SELECT * FROM lost_items ORDER BY created_at DESC').fetchall()
    found_items = db.execute('SELECT * FROM found_items ORDER BY created_at DESC').fetchall()
    
    # Get detailed claims information
    claims = db.execute('''
        SELECT c.*, 
               CASE 
                   WHEN c.item_type = 'lost' THEN l.item_name
                   ELSE f.item_name
               END as item_name,
               CASE 
                   WHEN c.item_type = 'lost' THEN l.contact_name
                   ELSE f.contact_name
               END as original_contact,
               CASE 
                   WHEN c.item_type = 'lost' THEN 'Lost Item'
                   ELSE 'Found Item'
               END as item_type_desc
        FROM claims c
        LEFT JOIN lost_items l ON c.item_id = l.id AND c.item_type = 'lost'
        LEFT JOIN found_items f ON c.item_id = f.id AND c.item_type = 'found'
        ORDER BY c.created_at DESC
    ''').fetchall()
    
    # Get detailed item information with claims
    detailed_lost_items = []
    for item in lost_items:
        item_info = dict(item)
        # Get claim information for this item
        claim_info = db.execute('''
            SELECT claimant_name, claimant_email, claimant_phone, claim_description, status, created_at
            FROM claims 
            WHERE item_type = 'lost' AND item_id = ?
            ORDER BY created_at DESC
        ''', (item['id'],)).fetchone()
        
        item_info['claim_info'] = claim_info
        detailed_lost_items.append(item_info)
    
    detailed_found_items = []
    for item in found_items:
        item_info = dict(item)
        # Get claim information for this item
        claim_info = db.execute('''
            SELECT claimant_name, claimant_email, claimant_phone, claim_description, status, created_at
            FROM claims 
            WHERE item_type = 'found' AND item_id = ?
            ORDER BY created_at DESC
        ''', (item['id'],)).fetchone()
        
        item_info['claim_info'] = claim_info
        detailed_found_items.append(item_info)
    
    return render_template('admin.html', 
                         lost_items=detailed_lost_items, 
                         found_items=detailed_found_items, 
                         claims=claims)

@app.route('/admin/update_status', methods=['POST'])
@admin_required
def update_status():
    """Update item status (admin only)"""
    item_type = request.form['item_type']
    item_id = request.form['item_id']
    new_status = request.form['status']
    
    db = get_db()
    
    if item_type == 'lost':
        db.execute(
            'UPDATE lost_items SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (new_status, item_id)
        )
    elif item_type == 'found':
        db.execute(
            'UPDATE found_items SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (new_status, item_id)
        )
    
    db.commit()
    flash('Item status updated successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/edit/lost/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_lost_item(item_id):
    """Edit a lost item (admin only)"""
    db = get_db()
    
    if request.method == 'POST':
        # Get form data
        item_name = request.form['item_name']
        category = request.form['category']
        description = request.form.get('description', '')
        lost_date = request.form['lost_date']
        location = request.form['location']
        contact_name = request.form['contact_name']
        contact_email = request.form.get('contact_email', '')
        contact_phone = request.form.get('contact_phone', '')
        
        # Update database
        db.execute(
            '''UPDATE lost_items 
               SET item_name = ?, category = ?, description = ?, lost_date = ?, 
                   location = ?, contact_name = ?, contact_email = ?, contact_phone = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (item_name, category, description, lost_date, location, 
             contact_name, contact_email, contact_phone, item_id)
        )
        db.commit()
        
        flash('Lost item updated successfully!', 'success')
        return redirect(url_for('admin'))
    
    # Get item data for form
    item = db.execute(
        'SELECT * FROM lost_items WHERE id = ?', (item_id,)
    ).fetchone()
    
    if item is None:
        flash('Item not found!', 'error')
        return redirect(url_for('admin'))
    
    return render_template('edit_lost_item.html', item=item)

@app.route('/admin/edit/found/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_found_item(item_id):
    """Edit a found item (admin only)"""
    db = get_db()
    
    if request.method == 'POST':
        # Get form data
        item_name = request.form['item_name']
        category = request.form['category']
        description = request.form.get('description', '')
        found_date = request.form['found_date']
        location = request.form['location']
        contact_name = request.form['contact_name']
        contact_email = request.form.get('contact_email', '')
        contact_phone = request.form.get('contact_phone', '')
        
        # Update database
        db.execute(
            '''UPDATE found_items 
               SET item_name = ?, category = ?, description = ?, found_date = ?, 
                   location = ?, contact_name = ?, contact_email = ?, contact_phone = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (item_name, category, description, found_date, location, 
             contact_name, contact_email, contact_phone, item_id)
        )
        db.commit()
        
        flash('Found item updated successfully!', 'success')
        return redirect(url_for('admin'))
    
    # Get item data for form
    item = db.execute(
        'SELECT * FROM found_items WHERE id = ?', (item_id,)
    ).fetchone()
    
    if item is None:
        flash('Item not found!', 'error')
        return redirect(url_for('admin'))
    
    return render_template('edit_found_item.html', item=item)

@app.route('/admin/delete/lost/<int:item_id>', methods=['POST'])
@admin_required
def delete_lost_item(item_id):
    """Delete a lost item (admin only)"""
    db = get_db()
    
    # Delete associated claims first
    db.execute('DELETE FROM claims WHERE item_type = "lost" AND item_id = ?', (item_id,))
    
    # Delete the item
    db.execute('DELETE FROM lost_items WHERE id = ?', (item_id,))
    db.commit()
    
    flash('Lost item deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete/found/<int:item_id>', methods=['POST'])
@admin_required
def delete_found_item(item_id):
    """Delete a found item (admin only)"""
    db = get_db()
    
    # Delete associated claims first
    db.execute('DELETE FROM claims WHERE item_type = "found" AND item_id = ?', (item_id,))
    
    # Delete the item
    db.execute('DELETE FROM found_items WHERE id = ?', (item_id,))
    db.commit()
    
    flash('Found item deleted successfully!', 'success')
    return redirect(url_for('admin'))


@app.route('/custom_404')
def custom_404():
    """Custom 404 page with Easter egg - shows MILTON when clicked twice"""
    # Track click count in session
    if '404_clicks' not in session:
        session['404_clicks'] = 0
    
    session['404_clicks'] += 1
    click_count = session['404_clicks']
    
    # Check if it's the second click
    if click_count >= 2:
        # Reset click count
        session['404_clicks'] = 0
        return render_template('404_milton.html', title='MILTON')
    
    return render_template('404.html', title='404 Not Found')


@app.errorhandler(404)
def page_not_found(e):
    """Handle regular 404 errors"""
    return render_template('404.html', title='404 Not Found'), 404

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    init_db()
    app.run(debug=True)