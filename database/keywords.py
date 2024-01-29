import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text, func, or_
from source.general_functions import read_file
from database.models import Base, Keywords
import pandas as pd

ENGINE = create_engine("sqlite:///database/keywords_data.db", echo=True)


class TechKeywords:
    """
    :Title: Class with function to extract data from 3gpp database.
    """

    def __init__(self):
        create_session = sessionmaker(bind=ENGINE)
        self.session = create_session()

    def add_keyword(self, keyword_: str, tech_words: str):
        try:
            record = Keywords(keyword=keyword_, tech_words=tech_words, inserted_at=None, updated_at=None)
            self.session.add(record)
            self.session.commit()
        except Exception as e:
            import pdb;pdb.set_trace()
            self.session.rollback()
        finally:
            self.session.close()

    def find(self, keyword_: str):
        result = self.session.query(Keywords.keyword, Keywords.tech_words).filter(or_(Keywords.keyword.like(f"%{keyword_}%"), Keywords.tech_words.like(f"%{keyword_}%"))).all()
        return [{'keyword': keyword, 'tech_words': tech_words} for keyword, tech_words in result]

    def get_data(self):
        try:
            keywords_ = self.session.query(Keywords.keyword, Keywords.tech_words).all()
            return [{'keyword': keyword, 'tech_words': tech_words} for keyword, tech_words in keywords_]
        except sqlalchemy.exc.OperationalError:
            return []

    def update(self, keyword_: str, tech_words: str):
        try:
            record = self.session.query(Keywords).filter(Keywords.keyword == keyword_.lower()).first()
            if record:
                record.tech_words = tech_words
                record.updated_at = None
            self.session.commit()
        except Exception as e:
            import pdb;
            pdb.set_trace()
            self.session.rollback()
        finally:
            self.session.close()

    def delete(self, keyword_: str):
        try:
            record = self.session.query(Keywords).filter(Keywords.keyword == keyword_.lower()).first()
            if record:
                self.session.delete(record)
            self.session.commit()
        except Exception as e:
            import pdb;
            pdb.set_trace()
            self.session.rollback()
        finally:
            self.session.close()

    def delete_keywords(self, keywords: str):
        keywords = [key.strip().lower() for key in keywords]
        records = self.session.query(Keywords).filter(Keywords.keyword.in_(keywords)).all()
        if len(records):
            try:
                for record in records:
                    self.session.delete(record)
                    self.session.commit()
            except Exception as e:
                import pdb;
                pdb.set_trace()
                self.session.rollback()
            finally:
                self.session.close()


    def get_existing_keywords(self, keyword_list: list):
        records = self.session.query(Keywords.keyword, Keywords.tech_words).filter(Keywords.keyword.in_(keyword_list)).all()
        return [{'keyword': keyword, 'tech_words': tech_words} for keyword, tech_words in records]


    def searched_data(self, filter=None):
        if len(filter):
            conditions = []
            for key in filter.keys():
                temp = f"{key} like '%{filter[key]}%'"
                conditions.append(temp)
            condition = ' and '.join(conditions)
            return self.get_data(condition)
        else:
            return self.get_data()

    def create_db(self) -> str:
        """
        :Title Function to create data base
        :return:
        """
        try:
            Base.metadata.create_all(bind=ENGINE, checkfirst=True)
            self.session.commit()
            return "<h1> Database created</h1>"
        except Exception as e:
            return f'Failed due to {e}'


    def __del__(self):
        self.session.close()
