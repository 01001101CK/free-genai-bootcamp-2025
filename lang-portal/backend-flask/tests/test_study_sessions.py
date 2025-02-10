def test_create_study_session():
    # Setup: Insert test group and activity
    with app.db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO groups (name) VALUES (?)", 
            ("Test Group",)
        )
        group_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO study_activities (name, url, preview_url) VALUES (?, ?, ?)", 
            ("Test Activity", "http://test.com", "http://test.com/preview")
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