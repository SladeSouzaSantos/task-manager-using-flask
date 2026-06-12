import pytest
from todo_project.forms import (
    RegistrationForm,
    LoginForm,
    UpdateUserInfoForm,
    UpdateUserPassword,
    TaskForm,
    UpdateTaskForm,
)
from wtforms import ValidationError

# ---------------------------------------------------------------------
# RegistrationForm
# ---------------------------------------------------------------------

def test_registration_form_duplicate_username(make_user, app):
    # cria usuário existente
    make_user(username='existing', password='pwd')
    form = RegistrationForm(data={
        'username': 'existing',
        'password': 'any',
        'confirm_password': 'any',
    })
    # a validação customizada deve lançar ValidationError
    with pytest.raises(ValidationError):
        form.validate_username(form.username)

def test_registration_form_success(app):
    form = RegistrationForm(data={
        'username': 'newuser',
        'password': 'Secret123',
        'confirm_password': 'Secret123',
    })
    assert form.validate()

# ---------------------------------------------------------------------
# LoginForm
# ---------------------------------------------------------------------

def test_login_form_valid(app):
    form = LoginForm(data={
        'username': 'anyuser',
        'password': 'anypwd',
    })
    assert form.validate()

# ---------------------------------------------------------------------
# UpdateUserInfoForm – conflict with another user
# ---------------------------------------------------------------------

def test_update_user_info_conflict(make_user, auth_client, app):
    # cria outro usuário que será usado como conflito
    make_user(username='conflict', password='pwd')
    # usuário autenticado já está criado pelo fixture auth_client (username='tester')
    form = UpdateUserInfoForm(data={'username': 'conflict'})
    # a validação customizada deve lançar ValidationError
    with pytest.raises(ValidationError):
        form.validate_username(form.username)

def test_update_user_info_success(make_user, auth_client, app):
    # usuário autenticado é 'tester'
    form = UpdateUserInfoForm(data={'username': 'newname'})
    # como o nome ainda não existe, a validação deve passar
    assert form.validate()

# ---------------------------------------------------------------------
# UpdateUserPassword – only field validation (DataRequired)
# ---------------------------------------------------------------------

def test_update_user_password_fields(app):
    form = UpdateUserPassword(data={
        'old_password': 'oldpwd',
        'new_password': 'newpwd',
    })
    assert form.validate()

# ---------------------------------------------------------------------
# TaskForm and UpdateTaskForm – basic validation
# ---------------------------------------------------------------------

def test_task_form_valid(app):
    form = TaskForm(data={'task_name': 'Minha tarefa'})
    assert form.validate()

def test_update_task_form_valid(app):
    form = UpdateTaskForm(data={'task_name': 'Tarefa atualizada'})
    assert form.validate()
