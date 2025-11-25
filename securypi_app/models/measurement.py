from __future__ import annotations  # fix class forward referencing issue

from datetime import datetime
from sqlalchemy import Integer, Float, DateTime, select, text
from sqlalchemy.orm import Mapped, mapped_column

from . import db


class Measurement(db.Model):
    __tablename__ = "measurement"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement="auto"
    )
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
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

    @classmethod
    def testprintall(cls) -> None:
        measurements = db.session.execute(select(cls))
        for m in measurements.scalars():
            print(m)

    @classmethod
    def fetch_latest(cls) -> Measurement:
        stmt = (select(cls)
                .order_by(cls.time.desc())
                .limit(1)
                )
        return db.session.execute(stmt).scalar_one_or_none()

    def log(self) -> bool:
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return True

        return False
