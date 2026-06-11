"""Entry point for the Flask Task Manager application.

When the application is started directly via ``python run.py`` we ensure that
the SQLite database and all tables defined in ``todo_project.models`` exist.
If the tables are missing (e.g. after cloning the repository), ``db.create_all()``
will create them automatically. This prevents the ``OperationalError: no such
table: user`` that occurs when the registration or login forms try to query the
``User`` model before the schema has been created.
"""

import os

from todo_project import app, db
# Import models so that SQLAlchemy is aware of them before ``create_all`` is called.
from todo_project.models import User, Task  # noqa: F401

def _initialize_database():
    """Create database tables if they do not exist.

    The function is idempotent – calling ``create_all`` on an existing schema
    is safe and does nothing. It is executed only when the script is run as the
    main module.
    """
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    _initialize_database()
    
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0') # nosec B104
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(host=host, debug=debug)
