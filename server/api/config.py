
import os, random, string
from datetime import timedelta
from typing import Optional

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = BASE_DIR+'/static/uploads'
UPLOAD_PICTURE = BASE_DIR+'/static/profile'

class BaseConfig():
    
    SECRET_KEY: Optional[str | None] = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY: str = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 64 ))

    UPLOAD_EXTENSIONS: list = ['.jpg', '.png', '.gif']

    JWT_SECRET_KEY: Optional[str | None] = os.getenv('JWT_SECRET_KEY', None)
    if not JWT_SECRET_KEY:
        JWT_SECRET_KEY: str = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))
    
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    DB_ENGINE: Optional[str | None]   = os.getenv('DB_ENGINE'   , None)
    DB_USERNAME: Optional[str | None] = os.getenv('DB_USERNAME' , None)
    DB_PASS: Optional[str | None]     = os.getenv('DB_PASS'     , None)
    DB_HOST: Optional[str | None]     = os.getenv('DB_HOST'     , None)
    DB_PORT: Optional[int| None]     = os.getenv('DB_PORT'     , None)
    DB_NAME: Optional[str | None]     = os.getenv('DB_NAME'     , None)

    USE_SQLITE: bool  = True 

    # try to set up a Relational DBMS
    if DB_ENGINE and DB_NAME and DB_USERNAME:

        try:
            
            # Relational DBMS: PostgreSQL, MySQL
            SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
                DB_ENGINE,
                DB_USERNAME,
                DB_PASS,
                DB_HOST,
                DB_PORT,
                DB_NAME
            ) 

            USE_SQLITE  = False

        except Exception as e:
            # add logs
            print('> Error: DBMS Exception: ' + str(e) )
            print('> Fallback to SQLite ')    

    if USE_SQLITE:

        # This will create a file in <app> FOLDER
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'apidata.sqlite3')

    UPLOAD_FOLDER: str = UPLOAD_FOLDER
    UPLOAD_PICTURE: str = UPLOAD_PICTURE
    # MAX_CONTENT_LENGTH: int = 6 * 1000 * 1000
    SECURITY_PASSWORD_SALT: Optional[str | None] = os.environ.get('SECURITY_PASSWORD_SALT')


    