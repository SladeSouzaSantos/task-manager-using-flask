import pytest
from todo_project import db
from todo_project.models import User, Task

def test_user_password_hash(make_user):
    # cria usuário usando fixture make_user
    user = make_user(username='alice', password='s3cr3t')
    # a senha armazenada deve ser hash e não o texto puro
    assert user.password != 's3cr3t'
    # bcrypt pode validar a senha
    from todo_project import bcrypt
    assert bcrypt.check_password_hash(user.password, 's3cr3t')

def test_task_relationship(make_user, app):
    # cria usuário e tarefa associada
    user = make_user(username='bob', password='pwd')
    task = Task(content='Minha tarefa', author=user)
    db.session.add(task)
    db.session.commit()
    # a tarefa deve estar vinculada ao usuário
    assert task.user_id == user.id
    assert task.author == user
    # o usuário deve ter a tarefa na relação backref
    assert task in user.tasks
