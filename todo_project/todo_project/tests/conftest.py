# todo_project/todo_project/tests/conftest.py
import pytest
from todo_project import app as flask_app, db
from todo_project.models import User, Task

@pytest.fixture(scope="function")
def app():
    """
    Cria uma instância do Flask configurada para testes.
    - `TESTING=True` habilita o modo teste.
    - Banco em memória (`sqlite:///:memory:`) garante isolamento.
    - CSRF desativado para facilitar POSTs nos formulários.
    """
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret-key",
    )

    # Cria as tabelas antes de cada teste
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste do Flask (wrapper do Werkzeug)."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner do Flask (útil para comandos `flask` customizados)."""
    return app.test_cli_runner()

# ---------------------------------------------------------------------
# Helper fixtures for creating users and an authenticated client
# ---------------------------------------------------------------------

@pytest.fixture
def make_user(app):
    """Create a user in the test database and return the model instance.
    The fixture receives the ``app`` fixture to ensure the DB is ready.
    """
    from todo_project import bcrypt

    def _make_user(username='tester', password='secret123'):
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        return user

    return _make_user

@pytest.fixture
def auth_client(client, make_user):
    """Return a ``client`` that is already logged in as a test user.
    This uses the ``/login`` route to perform the authentication, so the
    login logic itself is also exercised.
    """
    # Create a user that will be used for authentication
    make_user(username='tester', password='secret123')
    # Perform login via POST; ``follow_redirects`` ensures we end up on the
    # page the app redirects to after a successful login.
    client.post('/login', data={
        'username': 'tester',
        'password': 'secret123'
    }, follow_redirects=True)
    return client