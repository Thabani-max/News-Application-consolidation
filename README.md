---

# News_app Django Project

This is a Django web application project that includes two main apps:

* **grabsomore**: Handles user authentication, registration, password reset, and user sessions.
* **eNews**: Basic eCommerce functionality with journalists, articles, newsletters, and subscrption to journalists or publishers and journalists associate with a publisher.

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Prerequisites](#prerequisites)
- [Installation For Virtual Environment](#installation-for-venv)
- [Database Setup (Virtual environment)](#database-setup-for-venv)
- [Running the Project using virtual environment](#running-the-project-for-venv)
- [Installation For Docker Desktop/Playground](#installation-for-docker)
- [Database Setup (Docker)](#database-setup-for-docker)
- [Running the Project using Docker](#running-the-project-for-docker)
- [Accessing the application(For both, Docker and Virtual environment use case)](#accesing-the-app)
- [Usage](#usage)
- [Password Reset Testing](#password-reset-testing)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## Prerequisites

Before you begin, ensure you have met the following requirements:

* Python 3.9 or later installed. [Download Python](https://www.python.org/downloads/)
* MySQL installed and running on your machine.
* Basic knowledge of using the command line / terminal.
* Git installed to clone the repository (optional but recommended).
* Docker desktop(if using docker to run the application)/ Docker playground
[Download Docker desktop](https://www.docker.com/products/docker-desktop/)
[Using Docker Playground](https://labs.play-with-docker.com/)

---

## Installation For Virtual Environment 

1. **Clone the repository** (or download the ZIP and extract):

   ```bash
   https://github.com/Thabani-max/News-Application-consolidation.git
   cd News-Application-consolidation
   ```

---

2. **Create and activate a virtual environment** (recommended):

   * On Windows:

     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * On macOS/Linux:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the required Python packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Email Settings:**

   For sending emails (like password resets), update your email credentials in `News_app/settings.py` under the email section:

   ```python
   EMAIL_HOST_USER = 'your-email@example.com'
   EMAIL_HOST_PASSWORD = 'your-email-password-or-app-password'
   ```

   > **Note:** For Gmail, you might need to create an App Password and enable "Less secure app access".

---

## Database Setup (Virtual environment)

1. **Create MariaDB database:**

   Login to your MariaDB server and create the database:

   ```sql
   CREATE DATABASE news_app;
   ```

2. **Update database credentials in `News_app/settings.py`** if your MariaDB username or password differ:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'news_app',
           'USER': 'root',
           'PASSWORD': 'your_mariadb_password',
           'HOST': 'localhost',
           'PORT': '',
       }
   }
   ```

3. **Install MySQL Python adapter** if not already installed:

   ```bash
   pip install mysqlclient
   ```

---

## Running the Project using virtual environment

1. **Apply migrations:**

   Run the following commands to create the necessary database tables:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create a superuser** (for admin access):

   ```bash
   python manage.py createsuperuser
   ```

   Follow the prompts to create a user with admin privileges.

3. **Run the development server in venv:**

   ```bash
   python manage.py runserver
   ```

---

## Installation For Docker

1. **Clone the repository** (or download the ZIP and extract):

   ```bash
   https://github.com/Thabani-max/News-Application-consolidation.git
   cd News-Application-consolidation
   ```

---

## Database Setup (Docker)

1. **Create MariaDB database:**

   Login to your MariaDB server and create the database:

   ```sql
   CREATE DATABASE news_app;
   ```

2. **Update database credentials in `News_app/settings.py`** if your MariaDB username or password differ:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'news_app',
           'USER': 'root',
           'PASSWORD': 'your_mariadb_password',
           'HOST': 'host.docker.internal',
           'PORT': '',
       }
   }
   ```

---

## Running the project using Docker

1. **Login to docker Desktop and Start Engine** (recommended):

   To build docker container and image and running both use Docker desktop as docker
   playground is currently unavailable. To perform the actions mentioned on o 2., 3.,
   and 4, on your Docker terminal run the commands below that follow. first change
   directory to your projact directory.

2. **Build the web service:**

   ```
   docker-compose build web
   ```

3. **Start the web service**

   ```
   docker-compose up
   ```

4. **Applying migrations**

   ```
   docker compose run web python manage.py migrate
   ```

5. **Configure Email Settings:**

   For sending emails (like password resets), update your email credentials in `News_app/settings.py` under the email section:

   ```python
   EMAIL_HOST_USER = 'your-email@example.com'
   EMAIL_HOST_PASSWORD = 'your-email-password-or-app-password'
   ```

   > **Note:** For Gmail, you might need to create an App Password and enable "Less secure app access".

---

## Accessing the application(For both, Docker and Virtual environment use case)

   * Open your browser and go to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   * For superuser go to:[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
   * You can login, register new users, browse publishers, journalists, newsletters and articles, and test password reset functionality.

---

## Usage

* **Authentication (`grabsomore` app):**

  * Login at `/` (root URL)
  * Register at `/register/`
  * Request password reset at `/request-password-reset/`
  * Reset password via emailed token link

* **eNews (`eNews` app):**
  * View all AJournalists/Publishers at `/` (root URL, depending on project URL setup)
  * View all Newsletters/Articles at `/` (root URL, depending on project URL setup)
  * View articles/newseletter details, update articles/newsletters (if editor/journalist),    subscribe to journalists/publishers (if reader), associate with publishers (if editor/journalist), publish independent articles/newsletters (if journalist), can publish newsletters(if journalist), and can approve articles for publishng (if editor).

---

## Password Reset Testing

If you want to test password reset functionality without sending real emails:

1. Change email backend in `News_app/settings.py` to console:

   ```python
   EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
   ```

2. When you submit a password reset request, the reset link will print in your console/terminal.

3. Copy and paste the link into your browser to reset the password.

---

## Troubleshooting

* **MySQL Client Missing Error:**

  If you get `ModuleNotFoundError: No module named 'mysqlclient'`, install it with:

  ```bash
  pip install mysqlclient
  ```

* **SMTP Authentication Error:**

  Make sure you use correct email and password. For Gmail, you might need to use App Passwords instead of your regular password.

* **Static files not loading:**

  During development, Django serves static files automatically. For production, you need to configure static files properly.

---

## Documentation

* **documentation (sphinx_maths/docs/_build/html/index.py app):**
  * To view the html file's complete documentaion of the eNews app open the index.html
  * file in your web browser, and navigate to the eNews package.

---

## Project Structure

```
News_app/
├── eNews/               # eNews_app
│   ├── models.py
│   ├── views.py
│   ├── templates/
│   └── urls.py
├── grabsomore/              # Authentication app
│   ├── models.py
│   ├── views.py
│   ├── templates/
│   ├── urls.py
│   └── ...
├── News_app/
│   ├── settings.py          # Project settings (DB, email, apps)
│   ├── urls.py              # Root URL routing
│   └── wsgi.py
├── manage.py                # Django CLI utility
└── requirements.txt         # Python dependencies
```

---