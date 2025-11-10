import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app

@pytest.fixture
def app():
    """Create and configure a test instance of the app."""
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key'
    })
    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test that health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'

class TestHomePage:
    """Test home page functionality"""
    
    def test_index_page_loads(self, client):
        """Test that index page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ACEest Fitness' in response.data
    
    def test_index_contains_form(self, client):
        """Test that index page contains workout form"""
        response = client.get('/')
        assert b'workout' in response.data.lower()
        assert b'duration' in response.data.lower()

class TestAddWorkout:
    """Test add workout functionality"""
    
    def test_add_workout_success(self, client):
        """Test adding a valid workout"""
        response = client.post('/add_workout', data={
            'workout': 'Push-ups',
            'duration': '30'
        }, follow_redirects=True)
        assert response.status_code == 200
        json_data = response.json
        assert json_data['status'] == 'success'
    
    def test_add_workout_missing_fields(self, client):
        """Test adding workout with missing fields"""
        response = client.post('/add_workout', data={
            'workout': 'Push-ups'
        })
        assert response.status_code == 400
        json_data = response.json
        assert json_data['status'] == 'error'
    
    def test_add_workout_invalid_duration(self, client):
        """Test adding workout with invalid duration"""
        response = client.post('/add_workout', data={
            'workout': 'Push-ups',
            'duration': 'invalid'
        })
        assert response.status_code == 400
    
    def test_add_workout_negative_duration(self, client):
        """Test adding workout with negative duration"""
        response = client.post('/add_workout', data={
            'workout': 'Push-ups',
            'duration': '-10'
        })
        assert response.status_code == 400
    
    def test_add_workout_zero_duration(self, client):
        """Test adding workout with zero duration"""
        response = client.post('/add_workout', data={
            'workout': 'Push-ups',
            'duration': '0'
        })
        assert response.status_code == 400

class TestViewWorkouts:
    """Test view workouts functionality"""
    
    def test_view_workouts_page(self, client):
        """Test that view workouts page loads"""
        response = client.get('/view_workouts')
        assert response.status_code == 200
    
    def test_view_workouts_with_data(self, client):
        """Test viewing workouts after adding data"""
        # Add a workout first
        client.post('/add_workout', data={
            'workout': 'Squats',
            'duration': '20'
        })
        
        # View workouts
        response = client.get('/view_workouts')
        assert response.status_code == 200
        assert b'Squats' in response.data

class TestClearWorkouts:
    """Test clear workouts functionality"""
    
    def test_clear_workouts(self, client):
        """Test clearing all workouts"""
        # Add a workout
        client.post('/add_workout', data={
            'workout': 'Running',
            'duration': '45'
        })
        
        # Clear workouts
        response = client.post('/clear_workouts', follow_redirects=True)
        assert response.status_code == 200

class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self, client):
        """Test complete workflow: add, view, clear"""
        # Add multiple workouts
        workouts = [
            ('Push-ups', '30'),
            ('Squats', '25'),
            ('Running', '45')
        ]
        
        for workout, duration in workouts:
            response = client.post('/add_workout', data={
                'workout': workout,
                'duration': duration
            })
            assert response.status_code == 200
        
        # View workouts
        response = client.get('/view_workouts')
        assert response.status_code == 200
        for workout, _ in workouts:
            assert workout.encode() in response.data
        
        # Clear workouts
        response = client.post('/clear_workouts', follow_redirects=True)
        assert response.status_code == 200

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
