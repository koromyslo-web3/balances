from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import DB_URL

engine = create_async_engine(DB_URL)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency
async def get_session() -> AsyncSession:  # type: ignore
    async with Session() as session:
        yield session


class UnitOfWork:
    def __init__(self, autocommit=False, session_factory=Session):
        self.session_factory = session_factory
        self.autocommit = autocommit

    async def __aenter__(self):
        self.session = self.session_factory()
        return self.session

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None and self.autocommit:
                await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            detail = str(e.orig.args[0])
            raise ValueError(detail.split("\n")[1])
        finally:
            await self.session.close()


class DbException(Exception):
    pass
