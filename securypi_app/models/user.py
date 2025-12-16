from __future__ import annotations # fix class forward referencing issue

from sqlalchemy import Integer, String, Boolean, select, Row
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash

from . import db


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement="auto"
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column( # @TODO rename to hashed_password
        String, nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, server_default="0", nullable=False
    )
    email: Mapped[str | None] = mapped_column(
        String, nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, username={self.username}, "
            f"is_admin={self.is_admin}, email={self.email})"
        )

    @classmethod
    def get_by_id(cls, user_id: int) -> User:
        stmt = select(cls).where(cls.id == user_id)
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def get_by_username(cls, username: str) -> User:
        stmt = select(cls).where(cls.username == username)
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def get_meta_by_id(cls, user_id: int) -> Row:
        """ 
        Returns Row for better data manipulation.
        (Row._mapping -> dict)
        """
        stmt = select(cls.id, cls.username, cls.is_admin, cls.email).where(
            cls.id == user_id
        )
        return db.session.execute(stmt).first()

    @classmethod
    def register(cls,
                 username,
                 password,
                 is_admin=False,
                 hash_method="pbkdf2:sha256") -> tuple[bool, str]:
        """ @TODO check hash method: soft
        Registers a new user. 
        -> (True, "succes message")
        -> (False, "error message")
        """
        hashed = generate_password_hash(password, method=hash_method)

        new_user = cls(
            username=username,
            hashed_password=hashed,
            is_admin=is_admin,
        )
        db.session.add(new_user)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            message = (
                f"Failed to register user with username: '{username}',\n"
                "it is already taken."
            )
            print(message)
            return False, message

        user_type = "admin" if is_admin else "standard user"
        return True, f"Successfully registered {username} as {user_type}."
