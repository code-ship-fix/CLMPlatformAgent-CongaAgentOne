#!/usr/bin/env python3
# Alternative entry point for cloud platforms
import web_app

if __name__ == "__main__":
    # Run the Flask app
    web_app.socketio.run(
        web_app.app,
        host='0.0.0.0',
        port=8080,
        debug=False,
        allow_unsafe_werkzeug=True
    )
