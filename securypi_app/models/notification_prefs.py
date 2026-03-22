from __future__ import annotations

from datetime import datetime, timezone, timedelta
from sqlalchemy import Integer, Float, Boolean, DateTime, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass

from . import db


class NotificationPrefs(MappedAsDataclass, db.Model):
    __tablename__ = "notification_prefs"

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, unique=True
    )

    # motion capture
    motion_capture_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # sensor threshold toggles
    temp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    humidity_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pressure_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # sensor thresholds (None = no alert)
    temp_lower: Mapped[float | None] = mapped_column(Float, default=None, nullable=True)
    temp_upper: Mapped[float | None] = mapped_column(Float, default=None, nullable=True)
    humidity_lower: Mapped[float | None] = mapped_column(Float, default=None, nullable=True)
    humidity_upper: Mapped[float | None] = mapped_column(Float, default=None, nullable=True)
    pressure_lower: Mapped[float | None] = mapped_column(Float, default=None, nullable=True)
    pressure_upper: Mapped[float | None] = mapped_column(Float, default=None, nullable=True)

    # cooldown
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)

    # last sent timestamps (UTC)
    last_sent_motion: Mapped[datetime | None] = mapped_column(DateTime, default=None, nullable=True)
    last_sent_temp: Mapped[datetime | None] = mapped_column(DateTime, default=None, nullable=True)
    last_sent_humidity: Mapped[datetime | None] = mapped_column(DateTime, default=None, nullable=True)
    last_sent_pressure: Mapped[datetime | None] = mapped_column(DateTime, default=None, nullable=True)

    def __repr__(self) -> str:
        return f"NotificationPrefs(user_id={self.user_id})"

    @classmethod
    def get_by_user_id(cls, user_id) -> NotificationPrefs | None:
        stmt = select(cls).where(cls.user_id == user_id)
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def get_or_create(cls, user_id) -> NotificationPrefs:
        prefs = cls.get_by_user_id(user_id)
        if prefs is None:
            prefs = cls(user_id=user_id)
            db.session.add(prefs)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
        return prefs

    @classmethod
    def get_all_motion_enabled(cls) -> list[NotificationPrefs]:
        stmt = select(cls).where(cls.motion_capture_enabled == True)  # noqa: E712
        return list(db.session.execute(stmt).scalars().all())

    @classmethod
    def fetch_all(cls) -> list[NotificationPrefs]:
        stmt = select(cls)
        return list(db.session.execute(stmt).scalars().all())

    def is_cooldown_expired(self, metric) -> bool:
        """
        Returns True if the cooldown has expired for the given metric,
        or if no alert has been sent yet.
        metric: "motion" | "temp" | "humidity" | "pressure"
        """
        last_sent_map = {
            "motion": self.last_sent_motion,
            "temp": self.last_sent_temp,
            "humidity": self.last_sent_humidity,
            "pressure": self.last_sent_pressure,
        }
        last_sent = last_sent_map.get(metric)
        if last_sent is None:
            return True
        now = datetime.now(timezone.utc)
        last_sent_aware = last_sent.replace(tzinfo=timezone.utc)
        return (now - last_sent_aware) >= timedelta(minutes=self.cooldown_minutes)

    def update_last_sent(self, metric):
        """
        Sets last_sent_{metric} to now (UTC) and commits.
        metric: "motion" | "temp" | "humidity" | "pressure"
        """
        now = datetime.now(timezone.utc).replace(microsecond=0)
        if metric == "motion":
            self.last_sent_motion = now
        elif metric == "temp":
            self.last_sent_temp = now
        elif metric == "humidity":
            self.last_sent_humidity = now
        elif metric == "pressure":
            self.last_sent_pressure = now
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
