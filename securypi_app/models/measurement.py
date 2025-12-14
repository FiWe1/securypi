from __future__ import annotations  # fix class forward referencing issue

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from sqlalchemy import Integer, Float, DateTime, select, text
from sqlalchemy.orm import Mapped, mapped_column

from . import db


# @TODO move to json config
TIMEZONE_ZONEINFO = "Europe/Prague"


class Measurement(db.Model):
    __tablename__ = "measurement"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement="auto"
    )
    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # hadnling only UTC time
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP") # is UTC
    )
    temperature: Mapped[float] = mapped_column(
        Float, nullable=True
    )
    humidity: Mapped[float] = mapped_column(
        Float, nullable=True
    )
    pressure: Mapped[float] = mapped_column(
        Float, nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"Measurement(id={self.id}, time={self.time}, "
            f"temperature={self.temperature}, humidity={self.humidity}, "
            f"pressure={self.pressure})"
        )
    
    def to_local_timezone(self, local_timezone: ZoneInfo = None) -> Measurement:
        """
        Converts Measurement to local time zone. (implicitly from config)
        """
        if local_timezone is None:
            # @TODO fetch from json config
            local_timezone = ZoneInfo(TIMEZONE_ZONEINFO)
        
        tm = self.time.replace(tzinfo=timezone.utc)
        self.time = tm.astimezone(local_timezone)
        return self

    def log(self) -> bool:
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return True

        return False

    @classmethod
    def fetch_latest(cls) -> Measurement | None:
        stmt = (select(cls)
                .order_by(cls.time.desc())
                .limit(1)
                )
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def fetch_previous_range(cls,
                             target_datetime_timezone: datetime = None,
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
        return db.session.execute(stmt).scalars().all()
    
    @classmethod
    def testprintall(cls) -> None:
        measurements = db.session.execute(select(cls))
        for m in measurements.scalars():
            print(m)
