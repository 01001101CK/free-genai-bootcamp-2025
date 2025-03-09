from flask import request, jsonify
from ..agent import search_web, get_page_content, extract_vocabulary

def init_app(app):
    @app.route('/process-song', methods=['POST'])
    def process_song():
        try:
            data = request.json
            song_title = data.get('song_title')
            user_language = data.get('user_language', 'English')
            foreign_language = data.get('foreign_language', 'German')

            if not song_title:
                return jsonify({"error": "Song title is required"}), 400

            # Search for lyrics
            search_results = search_web(f"{song_title} lyrics {foreign_language}")
            
            if not search_results:
                return jsonify({"error": "No lyrics found"}), 404

            # Get the first result's content
            lyrics_url = search_results[0]["url"]
            lyrics_content = get_page_content(lyrics_url)

            # Extract vocabulary
            vocabulary = extract_vocabulary(lyrics_content)

            return jsonify({
                "song_title": song_title,
                "vocabulary": vocabulary,
                "source_url": lyrics_url
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500 