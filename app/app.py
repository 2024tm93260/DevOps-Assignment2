from flask import Flask, request, jsonify, render_template
from datetime import datetime

def create_app(test_config: dict | None = None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    app.workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}

    @app.get("/")
    def index():
        return jsonify(message="ACEestFitness API is running", docs=["/health", "/workouts", "/summary"]), 200

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.post("/workouts")
    def add_workout():
        if not request.is_json:
            return jsonify(error="Expected application/json"), 415

        data = request.get_json(silent=True) or {}
        category = data.get("category", "Workout")  # Default to "Workout"
        workout = (data.get("workout") or "").strip()
        duration = data.get("duration")

        if category not in app.workouts:
            return jsonify(error="Invalid category. Must be: Warm-up, Workout, or Cool-down"), 400

        if not workout:
            return jsonify(error="Field 'workout' is required"), 400

        try:
            duration = int(duration)
            if duration <= 0:
                raise ValueError
        except Exception:
            return jsonify(error="Field 'duration' must be a positive integer (minutes)"), 400

        entry = {
            "exercise": workout,
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        app.workouts[category].append(entry)
        return jsonify(message="Workout added", entry=entry, category=category), 201

    @app.get("/workouts")
    def list_workouts():
        all_workouts = []
        for category, sessions in app.workouts.items():
            for session in sessions:
                all_workouts.append({**session, "category": category})
        return jsonify(workouts=all_workouts, count=len(all_workouts), by_category=app.workouts), 200

    @app.get("/summary")
    def get_summary():
        total_time = sum(
            session['duration'] 
            for sessions in app.workouts.values() 
            for session in sessions
        )
        
        if total_time < 30:
            motivation = "Good start! Keep moving 💪"
        elif total_time < 60:
            motivation = "Nice effort! You're building consistency 🔥"
        else:
            motivation = "Excellent dedication! Keep up the great work 🏆"
        
        return jsonify(
            by_category=app.workouts,
            total_time=total_time,
            motivation=motivation
        ), 200
        
    @app.get("/ui")
    def ui():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=8000)
