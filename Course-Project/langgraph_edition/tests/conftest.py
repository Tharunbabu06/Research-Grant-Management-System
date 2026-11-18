import os,tempfile
os.environ['GRANT_DATA_DIR']=tempfile.mkdtemp(prefix='grant-tests-v2-')
os.environ['GRANT_LLM']='template'
import pytest
from fastapi.testclient import TestClient
from app import store
from app.main import app
@pytest.fixture(scope='session',autouse=True)
def accounts():
 for username,role,dep in [('f','faculty','SOCSE'),('h','hod','SOCSE'),('x','faculty','SOECE'),('o','research_office','R&D')]:
  with store.connect() as c:c.execute('INSERT INTO users VALUES(?,?,?,?,?)',(username,username,role,dep,store.password_hash('test-only-password')))
@pytest.fixture
def client():return TestClient(app)
