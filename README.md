# mailbox-app
#### Video Demo:  <https://www.youtube.com/watch?v=ntUQt5VSqKQ>
#### Description:
**CS50 Mailbox** is a full-stack web email client created with Python, Flask, and SQLite. With a simple, user-friendly interface, it enables users to create accounts, send and receive emails, and manage their inbox. A thorough explanation of its features, design decisions, and technical execution can be found below.

---

## Features
### Essential Features
1. **User Authentication**
   - Password hashing for secure registration (through Werkzeug).
   - Session-based login/logout with `session` in Flask.
   - Validation of input to avoid submissions that are empty.

2. **Email Management**
   - **Compose**: Include recipient, subject, and body fields in emails.
   - **Inbox/Sent Folders**: View sent and received messages along with their timestamps.
   - **Email Details**: To view and respond to any email, click on it.

3. **Reply System**
   - One-click responses (such as "Re: Original Subject") pre-fill the subject and recipient fields.

## Technical Implementation
### Backend (`app.py`)
- **Flask Routes**:
  - `/register`: Validates and hashes passwords before storing in SQLite.
  - `/compose`: Handles email creation with server-side checks for empty fields.
  - `/sent` and `/inbox`: Query database for user-specific emails.

#### Core Flask Configuration:
```python
# Initialize Flask app
app = Flask(__name__)

# Configure sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database setup
db = SQL("sqlite:///project.db")

# Security headers
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
```
1. **Authentication Routes:**
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate existing users"""
    # Verifies password hashes using Werkzeug
    if not check_password_hash(rows[0]["hash"], request.form.get("password")):
        return apology("invalid credentials", 403)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new users with password hashing"""
    hash = generate_password_hash(password)
    db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", email, hash)

@app.route("/logout")
def logout():
    """Clear user session"""
    session.clear()
```

2. **Email Management Routes:**
```python
@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    """Handle email creation"""
    if not sender or not recipient or not subject or not body:
        return apology("All fields required")
    db.execute("INSERT INTO emails VALUES (?, ?, ?, ?)",
              sender, recipient, subject, body)

@app.route("/inbox")
@login_required
def inbox():
    """Retrieve received emails"""
    emails = db.execute("SELECT * FROM emails WHERE recipient = ?", username)

@app.route("/sent")
@login_required
def sent():
    """Retrieve sent emails"""
    emails = db.execute("SELECT * FROM emails WHERE sender = ?", username)
```
3. **Email Operations:**
```python
@app.route("/email", methods=["POST"])
@login_required
def email():
    """Display full email content"""
    emailDetail = db.execute("SELECT * FROM emails WHERE id = ?", emailId)[0]

@app.route("/reply", methods=["POST"])
@login_required
def reply():
    """Pre-fill reply form"""
    original = db.execute("SELECT * FROM emails WHERE id = ?", emailId)[0]
```

### Security Features:

 - Password Hashing: Uses Werkzeug's generate_password_hash and check_password_hash
 - Session Protection: @login_required decorator on sensitive routes
 - Input Validation: Checks for empty fields in forms
 - CSRF Protection: Flask sessions prevent cross-site requests

### Error Handling:

 - Custom apology() function displays user-friendly errors
 - Try/except blocks for database operations
 - HTTP status codes (403 for auth failures)

## Database Architecture

### Schema Overview
The application uses SQLite3 with two core tables, managed via phpLiteAdmin v1.9.9:

  ```sql
  -- Users table (stores account credentials)
  CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      username TEXT NOT NULL UNIQUE,
      hash TEXT NOT NULL
  );

  -- Emails table (stores all message data)
  CREATE TABLE emails (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sender TEXT NOT NULL,
      recipient TEXT NOT NULL,
      subject TEXT NOT NULL,
      body TEXT NOT NULL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  );
```

### Key Design Decisions

   - User Authentication
   - UNIQUE constraint on usernames prevents duplicate accounts
   - Password hashes stored as TEXT (compatible with Werkzeug's output)
   - Auto-incrementing IDs for relational integrity

### Email Management
   - Denormalized design stores raw usernames instead of foreign keys
   - Automatic CURRENT_TIMESTAMP for message ordering
   - No size limits on body text (simplicity over optimization)


## Frontend Integration

### Structure of Templates (`/templates/`)

For responsive design, the frontend makes use of Bootstrap 5 and Jinja2 templating:

- **`layout.html`**
includes the following:
  - A navigation bar with links to send, compose, and inbox
  - Bootstrap CSS/JS imports
  - Flash message display area
  - Consistent footer across all pages

- **`compose.html`**
  Email composition form featuring:
  - Responsive textarea with dynamic sizing
  - Client-side form validation
  - Clean field labels and send button

- **`index.html`**
  Displays email lists with:
  - Clickable list items showing sender/recipient, subject, and timestamp
  - Visual hover effects
  - Pagination-ready structure (for future implementation)

## Styling (`/static/styles.css`)

### Navigation Branding (`navbar-brand`)
```css
nav .navbar-brand {
    font-size: xx-large;  /* Large, prominent logo text */
}

/* Color variants for brand personality */
nav .navbar-brand .blue { color: #537fbe; }  /* Calming blue */
nav .navbar-brand .red { color: #ea433b; }   /* Attention-grabbing red */
nav .navbar-brand .yellow { color: #f5b82e; }/* Friendly yellow */
nav .navbar-brand .green { color: #2e944b; }  /* Success-associated green */
```
### Email Composition Interface
```css
textarea {
    width: 200px;
    height: 100px;
    border: 1px solid lightgray;
    border-radius: 10px;  /* Softened edges for modern look */
}
```
### Email List Items
```css
.list-group-item {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;  /* Perfect vertical centering */
}

.view-email {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    width: 300px;  /* Constrained width for better scanability */
}
```
### Centered Content Blocks
```css
.center-div {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;  /* Stacked vertical layout */
}
```

## Project Structure
/project
│
├── /flask_session/ # Flask session storage
│ ├── 202924076d1128be8... # Session data files
│ └── f9bc6829a24e1be5d1... # Session data files
│
├── /static/ # Static assets
│ ├── favicon.ico # Browser tab icon
│ ├── L_heart_validator.png # Validation icon
│ └── styles.css # Custom CSS styles
│
├── /templates/ # Jinja2 templates
│ ├── apology.html # Error page template
│ ├── compose.html # Email composition
│ ├── email.html # Email detail view
│ ├── index.html # Inbox/Sent view
│ ├── layout.html # Base template
│ ├── login.html # Login page
│ ├── register.html # Registration page
│ └── reply.html # Reply page
│
├── app.py # Main Flask application
├── helpers.py # Custom helper functions
├── project.db # SQLite database
├── README.md # Project documentation
└── requirements.txt # Python dependencies

### Key Files Explained:

1. **Core Application Files**:
   - `app.py`: Contains all Flask routes and application logic
   - `helpers.py`: Includes custom functions (`login_required`, `apology`)
   - `project.db`: SQLite database storing users and emails

2. **Templates**:
   - `layout.html`: Base template with navigation and Bootstrap setup
   - Authentication: `login.html`, `register.html`
   - Email Views: `compose.html`, `email.html`, `reply.html`
   - `index.html`: Displays inbox/sent emails
   - `apology.html`: Error page template

3. **Static Assets**:
   - `styles.css`: Custom CSS overrides
   - Image assets for UI elements

4. **Configuration**:
   - `requirements.txt`: Lists all Python dependencies
   - `flask_session/`: Stores user session data

