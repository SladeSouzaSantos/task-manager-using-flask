import pytest
from flask import url_for

# ---------------------------------------------------------------------
# Auth routes (register, login, logout)
# ---------------------------------------------------------------------

def test_register_success(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'StrongPass123',
        'confirm_password': 'StrongPass123'
    }, follow_redirects=True)
    # After successful registration the app redirects to login page
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_success(auth_client):
    # auth_client fixture already logged in as 'tester'
    response = auth_client.get('/')
    # after login the user is redirected to the task list (all_tasks)
    assert response.status_code == 200
    assert b'All Tasks' in response.data or b'Tasks' in response.data

def test_logout(auth_client):
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    # after logout the login page should be shown again
    assert b'Login' in response.data

# ---------------------------------------------------------------------
# Task CRUD routes
# ---------------------------------------------------------------------

def test_add_task(auth_client):
    response = auth_client.post('/add_task', data={
        'task_name': 'Minha tarefa de teste'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Minha tarefa de teste' in response.data

def test_list_tasks(auth_client):
    # assume at least one task exists (added by previous test)
    response = auth_client.get('/all_tasks')
    assert response.status_code == 200
    # the page should contain the table of tasks
    assert b'Tasks' in response.data or b'All Tasks' in response.data

def test_search_task(auth_client):
    # create a unique task first
    auth_client.post('/add_task', data={'task_name': 'BuscaUnicaXYZ'}, follow_redirects=True)
    response = auth_client.get('/all_tasks?q=BuscaUnicaXYZ')
    assert response.status_code == 200
    assert b'BuscaUnicaXYZ' in response.data

def test_update_task(auth_client, make_user, app):
    # create a task to be updated
    user = make_user(username='upduser', password='pwd')
    from todo_project.models import Task
    from todo_project import db
    task = Task(content='Texto antigo', author=user)
    db.session.add(task)
    db.session.commit()
    # perform update via POST
    response = auth_client.post(f'/all_tasks/{task.id}/update_task', data={
        'task_name': 'Texto atualizado'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Texto atualizado' in response.data

def test_delete_task(auth_client, make_user, app):
    user = make_user(username='deluser', password='pwd')
    from todo_project.models import Task
    from todo_project import db
    task = Task(content='Para excluir', author=user)
    db.session.add(task)
    db.session.commit()
    # delete the task
    response = auth_client.get(f'/all_tasks/{task.id}/delete_task', follow_redirects=True)
    assert response.status_code == 200
    # after deletion the task text must not appear anymore
    assert b'Para excluir' not in response.data
