from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    contact_person: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    volume_kg: Mapped[int] = mapped_column(Integer, nullable=False)
    textile_type: Mapped[str] = mapped_column(String, nullable=False)
    delivery_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, company='{self.company_name}', contact='{self.contact_person}')>"
