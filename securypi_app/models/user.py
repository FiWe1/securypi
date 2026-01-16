from __future__ import annotations # fix class forward referencing issue

from sqlalchemy import Integer, String, Boolean, select, Row
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass
from werkzeug.security import generate_password_hash
from securypi_app.services.app_config import AppConfig

from . import db


class User(MappedAsDataclass, db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, init=False, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String, nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    email: Mapped[str | None] = mapped_column(
        String, default=None, nullable=True
    )
        
    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, username={self.username}, "
            f"is_admin={self.is_admin}, email={self.email})"
        )
    
    @classmethod
    def get_hash_method(cls) -> str:
        """ Fetches hash method from app configuration. """
        config = AppConfig.get()
        return config.authentication.password.hash_method

    @classmethod
    def get_by_id(cls, user_id: int) -> User | None:
        stmt = select(cls).where(cls.id == user_id)
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def get_by_username(cls, username: str) -> User | None:
        stmt = select(cls).where(cls.username == username)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @classmethod
    def is_username_free(cls, username) -> bool:
        """ Chcecks if username is not taken. """
        try:
            return cls.get_by_username(username) is None
        except Exception as e:
            print(e)
            raise RuntimeError("Error while checking username. "
                               "Is the database initialized?")

    @classmethod
    def get_meta_by_id(cls, user_id: int) -> Row | None:
        """ 
        Returns Row object of the user attributes - without password
        for better data manipulation.
        (Row._mapping -> dict of attributes)
        """
        stmt = select(cls.id, cls.username, cls.is_admin, cls.email).where(
            cls.id == user_id
        )
        return db.session.execute(stmt).first()

    @classmethod
    def register(cls,
                 username,
                 password,
                 is_admin=False) -> tuple[bool, str]:
        """
        Registers a new user. 
        -> (True, "succes message")
        -> (False, "error message")
        """
        hashed = generate_password_hash(password, method=cls.get_hash_method())

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
                "There was a database error. Please, check logs."
            )
            print(e)
            return False, message

        user_type = "administrator" if is_admin else "standard user"
        return True, f"Successfully registered {username} as {user_type}."
    
    def change_password(self,
                        new_password: str) -> tuple[bool, str]:
        """
        Changes the password for an existing user.
        -> (True, "success message")
        -> (False, "error message")
        """
        
        # hash new password
        self.hashed_password = generate_password_hash(
            new_password,
            method=self.get_hash_method()
        )
        
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False, "Failed to update password due to a database error."

        return True, f"Password successfully updated for user '{self.username}'."
