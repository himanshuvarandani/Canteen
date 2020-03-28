# Canteen
Canteen orders application

# Clone
    git clone https://github.com/himanshuvarandani/Canteen.git
It creates a new "canteen" folder.

# Create Virtual Environment
 Create virtual environment in canteen folder.
    
    For Windows:    virtualenv venv
    For Linux:      python3 -m venv venv

Activate Virtual Environment

    For windows:  venv\Scripts\activate
    For linux:  source venv/bin/activate

# Install Requirements:
    pip3 install -r requirements.txt

# Mail Section
To send mail direct to user email

    export MAIL_SERVER=smtp.googlemail.com
    export MAIL_PORT=587
    export MAIL_USE_TLS=1
    export MAIL_USERNAME=<your-gmail-username>
    export MAIL_PASSWORD=<your-gmail-password>
        
To test mail on local server (debug mode should be off)

    export MAIL_SERVER=localhost
    export MAIL_PORT=8025
        
    For local server use a new terminal
        python -m smtpd -n -c DebuggingServer localhost:8025
    
For Windows, use "set" instead of "export".

# Debug Mode
    export FLASK_DEBUG=1

# Run Project
    flask run

# Login Section
    Credentials for the admin are:
    Username:   admin
    Password:   admin123
