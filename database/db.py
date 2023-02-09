from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from  database import  models

class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def create_post(self, grade_data):
        session = self.maker()

        post = models.Post(**grade_data)
        session.add(post)
        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()