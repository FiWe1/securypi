from datetime import datetime
from sqlalchemy import Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from . import db


class Measurement(db.Model):
    __tablename__ = "measurement"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement="auto"
    )
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    temperature: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    humidity: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"Measurement(id={self.id}, time={self.time}, "
            f"temperature={self.temperature}, humidity={self.humidity})"
        )
