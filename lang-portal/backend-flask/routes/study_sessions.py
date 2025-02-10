from flask import request, jsonify, g
from flask_cors import cross_origin
from datetime import datetime
import math

def load(app):
  def validate_request(cursor, data):
    """Validate the study session request data"""
    if not data:
      return False, "No JSON data provided"
    
    # Check required fields
    required_fields = ['group_id', 'study_activity_id']
    for field in required_fields:
      if field not in data:
        return False, f"Missing required field: {field}"
      if not isinstance(data[field], int):
        return False, f"{field} must be an integer"
    
    # Verify group exists
    cursor.execute('SELECT id FROM groups WHERE id = ?', (data['group_id'],))
    if not cursor.fetchone():
      return False, f"Group with id {data['group_id']} does not exist"
    
    # Verify study activity exists
    cursor.execute('SELECT id FROM study_activities WHERE id = ?', 
                  (data['study_activity_id'],))
    if not cursor.fetchone():
      return False, f"Study activity with id {data['study_activity_id']} does not exist"
    
    return True, None

  def insert_study_session(cursor, data):
    """Insert a new study session into the database"""
    cursor.execute('''
      INSERT INTO study_sessions (
        group_id,
        study_activity_id,
        created_at
      ) VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (data['group_id'], data['study_activity_id']))
    return cursor.lastrowid

  @app.route('/api/study-sessions', methods=['POST'])
  @cross_origin()
  def create_study_session():
    """Create a new study session"""
    try:
      cursor = app.db.cursor()
      data = request.get_json()
      
      # Validate request
      is_valid, error_message = validate_request(cursor, data)
      if not is_valid:
        return jsonify({"error": error_message}), 400
      
      # Create session
      session_id = insert_study_session(cursor, data)
      
      # Get the created session details
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          ss.study_activity_id,
          sa.name as activity_name,
          ss.created_at
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        WHERE ss.id = ?
      ''', (session_id,))
      
      session = cursor.fetchone()
      app.db.commit()
      
      return jsonify({
        "message": "Study session created successfully",
        "session": {
          "id": session['id'],
          "group_id": session['group_id'],
          "group_name": session['group_name'],
          "activity_id": session['study_activity_id'],
          "activity_name": session['activity_name'],
          "created_at": session['created_at']
        }
      }), 201
            
    except Exception as e:
      app.db.rollback()
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions', methods=['GET'])
  @cross_origin()
  def get_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get total count
      cursor.execute('''
        SELECT COUNT(*) as count 
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
      ''')
      total_count = cursor.fetchone()['count']

      # Get paginated sessions
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        GROUP BY ss.id
        ORDER BY ss.created_at DESC
        LIMIT ? OFFSET ?
      ''', (per_page, offset))
      sessions = cursor.fetchall()

      return jsonify({
        'items': [{
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time since we don't track end time
          'review_items_count': session['review_items_count']
        } for session in sessions],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/<id>', methods=['GET'])
  @cross_origin()
  def get_study_session(id):
    try:
      cursor = app.db.cursor()
      
      # Get session details
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        WHERE ss.id = ?
        GROUP BY ss.id
      ''', (id,))
      
      session = cursor.fetchone()
      if not session:
        return jsonify({"error": "Study session not found"}), 404

      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get the words reviewed in this session with their review status
      cursor.execute('''
        SELECT 
          w.*,
          COALESCE(SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END), 0) as session_correct_count,
          COALESCE(SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END), 0) as session_wrong_count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
        GROUP BY w.id
        ORDER BY w.kanji
        LIMIT ? OFFSET ?
      ''', (id, per_page, offset))
      
      words = cursor.fetchall()

      # Get total count of words
      cursor.execute('''
        SELECT COUNT(DISTINCT w.id) as count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
      ''', (id,))
      
      total_count = cursor.fetchone()['count']

      return jsonify({
        'session': {
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time
          'review_items_count': session['review_items_count']
        },
        'words': [{
          'id': word['id'],
          'kanji': word['kanji'],
          'romaji': word['romaji'],
          'english': word['english'],
          'correct_count': word['session_correct_count'],
          'wrong_count': word['session_wrong_count']
        } for word in words],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  def validate_review_request(cursor, session_id, data):
    """Validate the review request data"""
    if not data:
      return False, "No JSON data provided"
    
    # Check required fields
    required_fields = ['word_id', 'correct']
    for field in required_fields:
      if field not in data:
        return False, f"Missing required field: {field}"
    
    # Validate types
    if not isinstance(data['word_id'], int):
      return False, "word_id must be an integer"
    if not isinstance(data['correct'], bool):
      return False, "correct must be a boolean"
    
    # Verify session exists
    cursor.execute('SELECT id FROM study_sessions WHERE id = ?', (session_id,))
    if not cursor.fetchone():
      return False, f"Study session with id {session_id} does not exist"
    
    # Verify word exists
    cursor.execute('SELECT id FROM words WHERE id = ?', (data['word_id'],))
    if not cursor.fetchone():
      return False, f"Word with id {data['word_id']} does not exist"
    
    return True, None

  def insert_review_item(cursor, session_id, data):
    """Insert a new review item into the database"""
    cursor.execute('''
      INSERT INTO word_review_items (
        word_id,
        study_session_id,
        correct,
        created_at
      ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (data['word_id'], session_id, data['correct']))
    
    # Update word_reviews table
    cursor.execute('''
      INSERT INTO word_reviews (word_id, correct_count, wrong_count)
      VALUES (?, ?, ?)
      ON CONFLICT(word_id) DO UPDATE SET
        correct_count = correct_count + ?,
        wrong_count = wrong_count + ?,
        last_reviewed = CURRENT_TIMESTAMP
    ''', (
      data['word_id'],
      1 if data['correct'] else 0,
      0 if data['correct'] else 1,
      1 if data['correct'] else 0,
      0 if data['correct'] else 1
    ))
    
    return cursor.lastrowid

  @app.route('/api/study-sessions/<int:session_id>/review', methods=['POST'])
  @cross_origin()
  def create_session_review(session_id):
    """Create a review for a study session"""
    try:
      cursor = app.db.cursor()
      data = request.get_json()
      
      # Validate request
      is_valid, error_message = validate_review_request(cursor, session_id, data)
      if not is_valid:
        return jsonify({"error": error_message}), 400
      
      # Create review item
      review_id = insert_review_item(cursor, session_id, data)
      
      # Get the updated review stats
      cursor.execute('''
        SELECT 
          w.id,
          w.kanji,
          w.romaji,
          w.english,
          COUNT(CASE WHEN wri.correct = 1 THEN 1 END) as correct_count,
          COUNT(CASE WHEN wri.correct = 0 THEN 1 END) as wrong_count
        FROM words w
        LEFT JOIN word_review_items wri ON wri.word_id = w.id
        WHERE w.id = ? AND wri.study_session_id = ?
        GROUP BY w.id
      ''', (data['word_id'], session_id))
      
      word_stats = cursor.fetchone()
      app.db.commit()
      
      return jsonify({
        "message": "Review recorded successfully",
        "review": {
          "id": review_id,
          "session_id": session_id,
          "word": {
            "id": word_stats['id'],
            "kanji": word_stats['kanji'],
            "romaji": word_stats['romaji'],
            "english": word_stats['english'],
            "session_stats": {
              "correct_count": word_stats['correct_count'],
              "wrong_count": word_stats['wrong_count']
            }
          }
        }
      }), 201
            
    except Exception as e:
      app.db.rollback()
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/reset', methods=['POST'])
  @cross_origin()
  def reset_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # First delete all word review items since they have foreign key constraints
      cursor.execute('DELETE FROM word_review_items')
      
      # Then delete all study sessions
      cursor.execute('DELETE FROM study_sessions')
      
      app.db.commit()
      
      return jsonify({"message": "Study history cleared successfully"}), 200
    except Exception as e:
      return jsonify({"error": str(e)}), 500