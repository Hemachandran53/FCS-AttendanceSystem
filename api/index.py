from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Attendance System</title>
            <style>
                body { font-family: Arial; padding: 50px; text-align: center; }
                .container { max-width: 600px; margin: 0 auto; }
                .error { background: #fee; padding: 20px; border-radius: 5px; }
                .info { background: #e3f2fd; padding: 20px; border-radius: 5px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>FCS Attendance System</h1>
                <div class="error">
                    <h2>⚠️ Database Configuration Required</h2>
                    <p>This Flask app requires a persistent database which is not supported on Vercel's serverless platform.</p>
                </div>
                <div class="info">
                    <h3>Recommended Deployment Options:</h3>
                    <ul style="text-align: left;">
                        <li><strong>Render.com</strong> - Free tier with PostgreSQL</li>
                        <li><strong>Railway.app</strong> - Simple deployment with database</li>
                        <li><strong>Heroku</strong> - Professional hosting</li>
                    </ul>
                    <p>Or run locally with: <code>python app.py</code></p>
                </div>
            </div>
        </body>
    </html>
    '''

# This is required for Vercel
app = app