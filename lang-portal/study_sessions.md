Updated Plan: Implementing POST /study_sessions Endpoint
🎯 Objective
Create an endpoint to start a new study session based on the study_sessions table schema.

## 📊 Database Schema Reference
```sql
CREATE TABLE study_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  group_id INTEGER NOT NULL,
  study_activity_id INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (group_id) REFERENCES groups(id),
  FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
);
```

## 📋 Implementation Steps

### 1. Basic Route Setup

- [ ] Create the route with proper decorators
```python
@app.route('/api/study-sessions', methods=['POST'])
@cross_origin()
def create_study_session():
    pass
```
2. Request Validation

- [ ] Validate required fields and their types
```python
def validate_request(cursor, data):
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
```

### 3. Database Operations

- [ ] Create SQL insert statement respecting schema
```python
def insert_study_session(cursor, data):
    cursor.execute('''
        INSERT INTO study_sessions (
            group_id,
            study_activity_id,
            created_at
        ) VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (data['group_id'], data['study_activity_id']))
    return cursor.lastrowid
```

### 4. Complete Route Implementation

- [ ] Implement the full route with error handling
```python
@app.route('/api/study-sessions', methods=['POST'])
@cross_origin()
def create_study_session():
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
```

### 5. Testing

- [ ] Create test cases with curl
```bash
# Test 1: Valid Request
curl -X POST http://localhost:5000/api/study-sessions \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "study_activity_id": 1
  }'

# Test 2: Missing Field
curl -X POST http://localhost:5000/api/study-sessions \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1
  }'

# Test 3: Invalid Group ID
curl -X POST http://localhost:5000/api/study-sessions \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 999,
    "study_activity_id": 1
  }'
```

### 6. Python Test Cases

- [ ] Create unit tests
```python
def test_create_study_session():
    # Setup: Insert test group and activity
    with app.db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO groups (name) VALUES (?)", 
            ("Test Group",)
        )
        group_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO study_activities (name) VALUES (?)", 
            ("Test Activity",)
        )
        activity_id = cursor.lastrowid
        
        app.db.commit()
    
    # Test cases
    def run_tests():
        # Test valid creation
        response = client.post('/api/study-sessions', json={
            'group_id': group_id,
            'study_activity_id': activity_id
        })
        assert response.status_code == 201
        assert 'session' in response.json
        
        # Test missing field
        response = client.post('/api/study-sessions', json={
            'group_id': group_id
        })
        assert response.status_code == 400
        
        # Test invalid group_id
        response = client.post('/api/study-sessions', json={
            'group_id': 999,
            'study_activity_id': activity_id
        })
        assert response.status_code == 400
    
    try:
        run_tests()
    finally:
        # Cleanup: Remove test data
        with app.db.cursor() as cursor:
            cursor.execute("DELETE FROM study_sessions")
            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            cursor.execute("DELETE FROM study_activities WHERE id = ?", (activity_id,))
            app.db.commit()
```

## 📝 Expected Response Format
```json
// Success Response (201)
{
    "message": "Study session created successfully",
    "session": {
        "id": 123,
        "group_id": 1,
        "group_name": "JLPT N5",
        "activity_id": 1,
        "activity_name": "Flashcards",
        "created_at": "2024-03-14T12:00:00Z"
    }
}

// Error Response (400)
{
    "error": "Group with id 999 does not exist"
}
```

## 🧪 Testing Checklist
🧪 Testing Checklist
[ ] Test with valid group_id and study_activity_id
[ ] Test with missing fields
[ ] Test with non-existent group_id
[ ] Test with non-existent study_activity_id
[ ] Test with non-integer IDs
[ ] Verify foreign key constraints work
[ ] Verify created_at timestamp is set correctly
[ ] Verify response includes all required session details
[ ] Test transaction rollback on error
Remember to:
Test foreign key constraints
Verify timestamps are handled correctly
Check that all fields from the schema are properly used
Ensure proper error handling for database constraints