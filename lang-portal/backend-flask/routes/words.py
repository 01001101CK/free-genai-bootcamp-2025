from flask import request, jsonify, g
from flask_cors import cross_origin
import json

def load(app):
  # Endpoint: GET /words with pagination (50 words per page)
  @app.route('/groups/<int:id>/words/raw', methods=['GET'])
  @cross_origin()
  def get_group_words_raw(id):
    try:
      cursor = app.db.cursor()
      # First, check if the group exists
      cursor.execute('SELECT name FROM groups WHERE id = ?', (id,))
      group = cursor.fetchone()
      if not group:
        return jsonify({"error": "Group not found"}), 404
      # SQL query to fetch words along with group information
      cursor.execute('''
        SELECT g.id as group_id, g.name as group_name, w.*
        FROM groups g
        JOIN word_groups wg ON g.id = wg.group_id
        JOIN words w ON w.id = wg.word_id
        WHERE g.id = ?;
      ''', (id,))
      
      data = cursor.fetchall()
      
      # Format the response
      result = {
        "group_id": id,
        "group_name": data[0]["group_name"] if data else group["name"],
        "words": []
      }
      
      for row in data:
        word = {
          "id": row["id"],
          "kanji": row["kanji"],
          "romaji": row["romaji"],
          "english": row["english"],
          "parts": json.loads(row["parts"])  # Deserialize 'parts' field
        }
        result["words"].append(word)
      
      return jsonify(result)
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  # Endpoint: GET /words/:id to get a single word with its details
  @app.route('/words/<int:word_id>', methods=['GET'])
  @cross_origin()
  def get_word(word_id):
    try:
      cursor = app.db.cursor()
      
      # Query to fetch the word and its details
      cursor.execute('''
        SELECT w.id, w.kanji, w.romaji, w.english,
               COALESCE(r.correct_count, 0) AS correct_count,
               COALESCE(r.wrong_count, 0) AS wrong_count,
               GROUP_CONCAT(DISTINCT g.id || '::' || g.name) as groups
        FROM words w
        LEFT JOIN word_reviews r ON w.id = r.word_id
        LEFT JOIN word_groups wg ON w.id = wg.word_id
        LEFT JOIN groups g ON wg.group_id = g.id
        WHERE w.id = ?
        GROUP BY w.id
      ''', (word_id,))
      
      word = cursor.fetchone()
      
      if not word:
        return jsonify({"error": "Word not found"}), 404
      
      # Parse the groups string into a list of group objects
      groups = []
      if word["groups"]:
        for group_str in word["groups"].split(','):
          group_id, group_name = group_str.split('::')
          groups.append({
            "id": int(group_id),
            "name": group_name
          })
      
      return jsonify({
        "word": {
          "id": word["id"],
          "kanji": word["kanji"],
          "romaji": word["romaji"],
          "english": word["english"],
          "correct_count": word["correct_count"],
          "wrong_count": word["wrong_count"],
          "groups": groups
        }
      })
      
    except Exception as e:
      return jsonify({"error": str(e)}), 500