import pytest
from .. import create_app, db
from ..routes import NUMBER_OF_LATEST, PAGINATION_NUM
from ..functions import NUMBER_OF_POPULAR, \
    NUMBER_OF_POPULAR_TAGS, convert_created_time
from ..models import Posts, Tags


# commands to run tests:
# python -m pytest
# python -m pytest -v - provides verbose output about the tests run
# python -m pytest tests/unit - specific of tests can be run
# python -m pytest --last-failed - only run the failed tests from the last time pytest was run


@pytest.fixture()
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()

