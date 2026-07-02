import enum

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, text

from db.base import BaseModel


class DataSourceTypeEnum(enum.Enum):
    pdf = "pdf"
    txt = "txt"
    url = "url"
    csv = "csv"
    api = "api"
    json = "json"
    qa = "qa"


class DataSourceStatusEnum(enum.Enum):
    pending = "pending"
    processed = "processed"
    failed = "failed"


class DataSource(BaseModel):
    __tablename__ = "DataSource"

    id = Column(Integer, primary_key=True, nullable=False)
    chatbot_id = Column(Integer, ForeignKey("Chatbot.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(DataSourceTypeEnum), nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(Enum(DataSourceStatusEnum))
