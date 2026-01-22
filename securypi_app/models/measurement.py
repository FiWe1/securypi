from __future__ import annotations  # fix class forward referencing issue

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from sqlalchemy import Integer, Float, DateTime, select, text
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass

from . import db
from securypi_app.services.app_config import AppConfig


class Measurement(MappedAsDataclass, db.Model):
    __tablename__ = "measurement"

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, autoincrement=True
    )
    temperature: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    humidity: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    pressure: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    time: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0),
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"Measurement(id={self.id}, time={self.time}, "
            f"temperature={self.temperature}, humidity={self.humidity}, "
            f"pressure={self.pressure})"
        )
    
    def time_local_timezone(self, local_timezone: ZoneInfo | None = None) -> datetime:
        """
        Returns measurement's time: DateTime in local time zone.
        (implicitly fetches from config)
        """
        if local_timezone is None:
            config = AppConfig.get()
            local_timezone = ZoneInfo(config.measurements.weather_station.timezone)
        
        tm = self.time.replace(tzinfo=timezone.utc)
        return tm.astimezone(local_timezone)

    def log(self) -> bool:
        """ Write measurement (self) to the database, returns True on success. """
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return False

        return True

    @classmethod
    def fetch_latest(cls) -> Measurement | None:
        stmt = (select(cls)
                .order_by(cls.time.desc())
                .limit(1)
                )
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def fetch_previous_range(cls,
                             target_datetime_timezone: datetime | None = None,
                             days_before: int = 0,
                             hours_before: int = 0,
                             minutes_before: int = 0) -> list[Measurement]:
        """
        explicit 'target_datetime_timezone' must have a timezone information!
        (datetime.now(timezone.utc))
        
        Retrieves list of measurements in interval:
        <(target_datetime - ..._before); target_datetime>
        By default returns measurements from last 24 hours.
        """
        # input check:
        if target_datetime_timezone is not None and (
           target_datetime_timezone.utcoffset() is None):
            raise ValueError("Naive datetime is not allowed; timezone required")
        
        # safe default:
        if target_datetime_timezone is None:
            target_datetime_timezone = datetime.now(timezone.utc)
        if days_before == 0 and hours_before == 0 and minutes_before == 0:
            hours_before = 24

        delta = timedelta(
            days=days_before,
            hours=hours_before,
            minutes=minutes_before
        )
        datetime_from = target_datetime_timezone - delta
        
        stmt = (select(cls)
                .where(cls.time >= datetime_from)
                .where(cls.time <= target_datetime_timezone)
                .order_by(cls.time.asc())
                )
        return list(db.session.execute(stmt).scalars().all())
    
    @classmethod
    def testprintall(cls) -> None:
        measurements = db.session.execute(select(cls))
        for m in measurements.scalars():
            print(m)
