from app import app, User
from flask_login import login_user

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

with app.test_client() as client:
    with app.app_context():
        # Authenticate as student
        response = client.post('/', data={'uid': 'EST-01', 'password': '123456'}, follow_redirects=True)
        print("Status code:", response.status_code)
        print("Content-Length:", len(response.data))
        text = response.data.decode('utf-8')
        if "Progreso Académico" in text:
            print("Student dashboard loaded successfully with 'Progreso Académico'.")
        elif "Internal Server Error" in text:
            print("Internal Server Error found!")
            print(text)
        else:
            print("Something else loaded:")
            print(text[:1000]) # Print excerpt
