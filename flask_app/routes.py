# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
from werkzeug.security import generate_password_hash
from flask import flash
from flask import g
from . import events  # This imports our socket event handlers



db = database()

#socketio = SocketIO()

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def getUser():
    """
    Retrieve the current logged-in user's email from the session, or 'Unknown' if not logged in.
    """
    return db.reversibleEncrypt('decrypt', session['email']) if 'email' in session else 'Unknown'

def login_required(func):
    """
    Decorator to restrict access to routes for logged-in users only.
    Redirects to the login page if the user is not authenticated.
    """
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return secure_function

# @app.route('/login')
# def login():
#     """
#     Render the login page for user authentication.
#     """
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     """
#     Log the user out by clearing the session and redirecting to the home page.
#     """
#     session.pop('email', default=None)
#     return redirect(url_for('home'))

@app.route('/processlogin', methods=["POST"])
def processlogin():
    """
    Process the login form submission, authenticate the user, and set the session.
    """
    try:
        # Create a fresh database connection for this login attempt
        db_connection = database()
        
        email = request.form.get('email')
        password = request.form.get('password')

        # Authenticate user with fresh connection
        result = db_connection.authenticate(email=email, password=password)
        print(f"Authentication result: {result}")  # Debug print

        if result['success']:
            session['email'] = db_connection.reversibleEncrypt('encrypt', email)
            return jsonify({'success': 1, 'redirect': url_for('home')})
        else:
            return jsonify({'success': 0, 'message': 'Invalid email or password'})
            
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug print
        return jsonify({'success': 0, 'message': 'Authentication error'})

#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())



@socketio.on('send_message', namespace='/chat')
def handle_send_message(data):
    user = getUser()
    is_owner = user == 'owner@email.com'
    style = 'owner' if is_owner else 'guest'
    print(f"DEBUG - User: {user}, Is Owner: {is_owner}, Style: {style}")
    emit(
        'new_message',
        {'msg': f"{user}: {data['msg']}", 'style': style},
        room='main'
    )

@socketio.on('joined', namespace='/chat')
def handle_joined(data):
    user = getUser()
    join_room('main')
    is_owner = user == 'owner@email.com'
    style = 'owner' if is_owner else 'guest'
    emit('status_update', {'msg': f"{user} has entered the room.", 'style': style}, room='main')

@socketio.on('leave', namespace='/chat')
def handle_leave(data):
    user = getUser()
    leave_room('main')
    is_owner = user == 'owner@email.com'
    style = 'owner' if is_owner else 'guest'
    emit('status_update', {'msg': f"{user} has left the room.", 'style': style}, room='main')
#######################################################################################
# FEEDBACK FORM RELATED
#######################################################################################
@app.route('/processfeedback', methods=['POST'])
def processfeedback():
    """
    Process the feedback form submission and store the feedback in the database.
    """
    name = request.form.get('name')
    email = request.form.get('email')
    comment = request.form.get('comment')

    db.query(
        "INSERT INTO feedback (name, email, comment) VALUES (%s, %s, %s)",
        (name, email, comment)
    )

    feedback_data = db.query("SELECT * FROM feedback")
    return render_template('processfeedback.html', feedback=feedback_data)

#######################################################################################
# RESUME RELATED
#######################################################################################
@app.route('/resume')
def resume():
    """
    Render the resume page with data from the database.
    """
    resume_data = db.getResumeData()
    return render_template('resume.html', resume_data=resume_data, user=getUser())

#######################################################################################
# OTHER ROUTES
#######################################################################################
@app.route('/')
def root():
    """
    Landing page with options to sign in or sign up
    """
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation
        if not email or not password:
            flash('All fields are required', 'error')
            return redirect('/signup')
            
        # Check if user already exists
        cursor = db.query("SELECT * FROM users WHERE email = %s", (email,))
        if cursor:  # If the query returns any results
            flash('Email already registered. Please login or use a different email.', 'error')
            return redirect('/signup')
            
        # If email is not taken, create new user
        result = db.createUser(email=email, password=password, role='guest')
        
        if result['success']:
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')
        else:
            flash(result['message'], 'error')
            return redirect('/signup')
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation
        if not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('login'))
            
        # Use the existing authenticate method from your database class
        result = db.authenticate(email=email, password=password)
        print(f"Authentication result: {result}")  # Debug print
        
        if result['success']:
            session['email'] = db.reversibleEncrypt('encrypt', email)
            return redirect(url_for('home'))
        else:
            flash(result['message'], 'error')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Log the user out by clearing the session and redirecting to the home page.
    """
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('root'))

@app.route('/home')
def home():
    """
    Display the home page with board options after login
    """
    if 'email' not in session:
        return redirect('/login')
        
    user_email = getUser()
    
    # Fetch boards where user is a member
    user_boards = db.query("""
        SELECT b.board_id, b.name 
        FROM boards b 
        JOIN board_members bm ON b.board_id = bm.board_id 
        WHERE bm.user_email = %s
    """, (user_email,))
    
    print(f"Fetched boards for {user_email}: {user_boards}")  # Debug print
    
    return render_template('home.html', user_email=user_email, boards=user_boards)

@app.context_processor
def inject_user():
    """
    Make user information available to all templates
    """
    if 'email' in session:
        user_email = getUser()
    else:
        user_email = None
    return dict(user_email=user_email)

@app.route('/create-board', methods=['POST'])
def create_board():
    if 'email' not in session:
        return redirect(url_for('login'))
        
    project_name = request.form.get('projectName')
    member_emails = request.form.get('memberEmails').split('\n')
    member_emails = [email.strip() for email in member_emails if email.strip()]
    
    creator_email = getUser()
    
    try:
        # Create the board
        cursor = db.query(
            "INSERT INTO boards (name, created_by) VALUES (%s, %s)",
            (project_name, creator_email)
        )
        
        # Get the board ID
        board_id = cursor[0]['LAST_INSERT_ID()']
        
        # Create default lists
        db.create_default_lists(board_id)
        
        # Add the creator as a board member
        db.query(
            "INSERT INTO board_members (board_id, user_email) VALUES (%s, %s)",
            (board_id, creator_email)
        )
        
        # Add other members
        for email in member_emails:
            user_exists = db.query("SELECT email FROM users WHERE email = %s", (email,))
            if user_exists:
                db.query(
                    "INSERT INTO board_members (board_id, user_email) VALUES (%s, %s)",
                    (board_id, email)
                )
        
        flash('Board created successfully!', 'success')
        return redirect(url_for('home'))
        
    except Exception as e:
        print(f"Error creating board: {e}")
        flash('Error creating board. Please try again.', 'error')
        return redirect(url_for('home'))

@app.route('/board/<int:board_id>')
def view_board(board_id):
    if 'email' not in session:
        return redirect(url_for('login'))
        
    user_email = getUser()
    
    # Check if user is a member of this board
    is_member = db.query("""
        SELECT 1 FROM board_members 
        WHERE board_id = %s AND user_email = %s
    """, (board_id, user_email))
    
    if not is_member:
        flash('You do not have access to this board', 'error')
        return redirect(url_for('home'))
    
    # Get board details
    board = db.query("SELECT * FROM boards WHERE board_id = %s", (board_id,))[0]
    
    # Get lists with their cards for this board
    lists = db.query("""
        SELECT l.list_id, l.name, l.position,
               c.card_id, c.content, c.position as card_position
        FROM lists l
        LEFT JOIN cards c ON l.list_id = c.list_id
        WHERE l.board_id = %s
        ORDER BY l.position, c.position
    """, (board_id,))
    
    # Organize cards by list
    organized_lists = {}
    for row in lists:
        list_id = row['list_id']
        if list_id not in organized_lists:
            organized_lists[list_id] = {
                'list_id': list_id,
                'name': row['name'],
                'position': row['position'],
                'cards': []
            }
        if row['card_id']:  # If there's a card
            organized_lists[list_id]['cards'].append({
                'card_id': row['card_id'],
                'content': row['content'],
                'position': row['card_position']
            })
    
    # Convert to list and sort by position
    final_lists = list(organized_lists.values())
    final_lists.sort(key=lambda x: x['position'])
    
    print(f"Fetched lists and cards for board {board_id}: {final_lists}")  # Debug print
    
    return render_template('board_view.html', board=board, lists=final_lists)

@app.route('/create-card', methods=['POST'])
def create_card():
    if 'email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    list_id = request.form.get('listId')
    content = request.form.get('cardContent')
    
    try:
        # Get the current highest position in the list
        position_result = db.query("""
            SELECT COALESCE(MAX(position), -1) + 1 as next_pos 
            FROM cards 
            WHERE list_id = %s
        """, (list_id,))
        next_position = position_result[0]['next_pos']
        
        # Insert the new card
        db.query("""
            INSERT INTO cards (list_id, content, position) 
            VALUES (%s, %s, %s)
        """, (list_id, content, next_position))
        
        # Get the ID of the card we just inserted
        card_id = db.query("""
            SELECT card_id 
            FROM cards 
            WHERE list_id = %s AND content = %s AND position = %s
            ORDER BY card_id DESC LIMIT 1
        """, (list_id, content, next_position))
        
        return jsonify({'success': True, 'cardId': card_id[0]['card_id']}), 200
        
    except Exception as e:
        print(f"Error creating card: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update-card', methods=['POST'])
def update_card():
    if 'email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    card_id = data.get('cardId')
    content = data.get('content')
    
    try:
        db.query("""
            UPDATE cards 
            SET content = %s 
            WHERE card_id = %s
        """, (content, card_id))
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error updating card: {e}")
        return jsonify({'error': 'Failed to update card'}), 500

@app.route('/delete-card', methods=['POST'])
def delete_card():
    if 'email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    card_id = data.get('cardId')
    
    try:
        db.query("DELETE FROM cards WHERE card_id = %s", (card_id,))
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error deleting card: {e}")
        return jsonify({'error': 'Failed to delete card'}), 500

@app.route('/update-card-position', methods=['POST'])
def update_card_position():
    if 'email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    card_id = data.get('cardId')
    new_list_id = data.get('listId')
    new_position = data.get('position')
    
    try:
        # Update positions of other cards
        db.query("""
            UPDATE cards 
            SET position = position + 1 
            WHERE list_id = %s 
            AND position >= %s
        """, (new_list_id, new_position))
        
        # Update the moved card
        db.query("""
            UPDATE cards 
            SET list_id = %s, position = %s 
            WHERE card_id = %s
        """, (new_list_id, new_position, card_id))
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error updating card position: {e}")
        return jsonify({'error': 'Failed to update card position'}), 500