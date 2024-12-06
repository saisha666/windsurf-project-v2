from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import os

Base = declarative_base()

class WebsiteData(Base):
    __tablename__ = 'website_data'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, index=True)
    title = Column(String)
    content = Column(JSON)
    last_scraped = Column(DateTime, default=datetime.utcnow)
    scrape_frequency = Column(Integer, default=24)  # hours
    
class BrowserHistory(Base):
    __tablename__ = 'browser_history'
    
    id = Column(Integer, primary_key=True)
    url = Column(String)
    title = Column(String)
    visit_time = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class MLModel(Base):
    __tablename__ = 'ml_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    model_type = Column(String)
    parameters = Column(JSON)
    performance_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            app_dir = os.path.expanduser('~/AppData/Local/AI_OS')
            os.makedirs(os.path.join(app_dir, 'database'), exist_ok=True)
            db_path = os.path.join(app_dir, 'database', 'ai_os.db')
            
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def save_website_data(self, url, title, content):
        session = self.Session()
        try:
            website = WebsiteData(
                url=url,
                title=title,
                content=json.dumps(content)
            )
            session.add(website)
            session.commit()
            return website.id
        finally:
            session.close()
            
    def save_browser_history(self, url, title, metadata=None):
        session = self.Session()
        try:
            history = BrowserHistory(
                url=url,
                title=title,
                metadata=json.dumps(metadata) if metadata else None
            )
            session.add(history)
            session.commit()
            return history.id
        finally:
            session.close()
            
    def save_ml_model(self, name, model_type, parameters, metrics):
        session = self.Session()
        try:
            model = MLModel(
                name=name,
                model_type=model_type,
                parameters=json.dumps(parameters),
                performance_metrics=json.dumps(metrics)
            )
            session.add(model)
            session.commit()
            return model.id
        finally:
            session.close()
            
    def get_website_data(self, url=None, days=7):
        session = self.Session()
        try:
            query = session.query(WebsiteData)
            if url:
                return query.filter(WebsiteData.url == url).first()
            return query.all()
        finally:
            session.close()
            
    def get_browser_history(self, limit=100):
        session = self.Session()
        try:
            return session.query(BrowserHistory)\
                .order_by(BrowserHistory.visit_time.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()
            
    def get_ml_model(self, name):
        session = self.Session()
        try:
            return session.query(MLModel)\
                .filter(MLModel.name == name)\
                .first()
        finally:
            session.close()
