from flask import render_template, url_for, flash, redirect, request

from todo_project import app, db, bcrypt
# Central logger for activity logging
from todo_project.logger import logger

# Import the forms
from todo_project.forms import (LoginForm, RegistrationForm, UpdateUserInfoForm, 
                                UpdateUserPassword, TaskForm, UpdateTaskForm)

# Import the Models
from todo_project.models import User, Task

# Import 
from flask_login import login_required, current_user, login_user, logout_user


@app.errorhandler(404)
def error_404(error):
    return (render_template('errors/404.html'), 404)

@app.errorhandler(403)
def error_403(error):
    return (render_template('errors/403.html'), 403)

@app.errorhandler(500)
def error_500(error):
    return (render_template('errors/500.html'), 500)


@app.route("/")
@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('all_tasks'))

    form = LoginForm()
    # After you submit the form
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Check if the user exists and the password is valid
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            # Log successful login
            logger.info(f"User '{user.username}' logged in successfully")
            task_form = TaskForm()
            flash('Login Successfull', 'success')
            return redirect(url_for('all_tasks'))
        else:
            # Log failed login attempt (do not log password)
            logger.warning(f"Failed login attempt for username '{form.username.data}'")
            flash('Login Unsuccessful. Please check Username Or Password', 'danger')
    
    return render_template('login.html', title='Login', form=form)
    

@app.route("/logout")
def logout():
    # Log logout before clearing the user session
    if current_user.is_authenticated:
        logger.info(f"User '{current_user.username}' logged out")
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('all_tasks'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # Log new user registration
        logger.info(f"New user registered: '{user.username}'")
        flash(f'Account Created For {form.username.data}', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/all_tasks")
@login_required
def all_tasks():
    """List all tasks for the logged‑in user.

    If a ``q`` query parameter is supplied, the tasks are filtered by the
    keyword (case‑insensitive) using ``ilike``. This implements the *search
    tasks* feature (Task‑03).
    """
    # Base query – tasks belonging to the current user
    user = User.query.filter_by(username=current_user.username).first()
    query = Task.query.filter_by(user_id=user.id)

    # Optional search term
    search_term = request.args.get('q', type=str)
    if search_term:
        # ``ilike`` provides case‑insensitive LIKE for SQLite and other DBs
        query = query.filter(Task.content.ilike(f"%{search_term}%"))

    tasks = query.all()
    return render_template('all_tasks.html', title='All Tasks', tasks=tasks, search_term=search_term)


@app.route("/add_task", methods=['POST', 'GET'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(content=form.task_name.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        # Log task creation
        logger.info(f"Task created by '{current_user.username}': '{task.content}' (id={task.id})")
        flash('Task Created', 'success')
        return redirect(url_for('add_task'))
    return render_template('add_task.html', form=form, title='Add Task')


@app.route("/all_tasks/<int:task_id>/update_task", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = UpdateTaskForm()
    if form.validate_on_submit():
        if form.task_name.data != task.content:
            old_content = task.content
            task.content = form.task_name.data
            db.session.commit()
            # Log task update with old and new content
            logger.info(f"Task id={task.id} updated by '{current_user.username}' from '{old_content}' to '{task.content}'")
            flash('Task Updated', 'success')
            return redirect(url_for('all_tasks'))
        else:
            flash('No Changes Made', 'warning')
            return redirect(url_for('all_tasks'))
    elif request.method == 'GET':
        form.task_name.data = task.content
    return render_template('add_task.html', title='Update Task', form=form)


@app.route("/all_tasks/<int:task_id>/delete_task")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    # Log task deletion
    logger.info(f"Task id={task.id} deleted by '{current_user.username}'")
    flash('Task Deleted', 'info')
    return redirect(url_for('all_tasks'))


@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateUserInfoForm()
    if form.validate_on_submit():
        if form.username.data != current_user.username:
            old_username = current_user.username
            current_user.username = form.username.data
            db.session.commit()
            # Log username change
            logger.info(f"User id={current_user.id} changed username from '{old_username}' to '{current_user.username}'")
            flash('Username Updated Successfully', 'success')
            return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username 

    return render_template('account.html', title='Account Settings', form=form)


@app.route("/account/change_password", methods=['POST', 'GET'])
@login_required
def change_password():
    form = UpdateUserPassword()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            # Log password change event (do not log the password itself)
            logger.info(f"User '{current_user.username}' changed password")
            flash('Password Changed Successfully', 'success')
            redirect(url_for('account'))
        else:
            flash('Please Enter Correct Password', 'danger') 

    return render_template('change_password.html', title='Change Password', form=form)

