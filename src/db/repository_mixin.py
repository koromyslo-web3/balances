from datetime import timedelta, datetime

from pydantic import TypeAdapter
from sqlalchemy import delete, select, update, func
from sqlalchemy.exc import IntegrityError

from .engine import Session


class RepositoryMixin:
    
    async def db_create(self):
        try:
            ignore_fields = self.Meta.ignore_fields if hasattr(self.Meta, 'ignore_fields') else {}
            obj = self.Meta.orm_model(**self.model_dump(exclude=ignore_fields))
            async with Session() as session:
                session.add(obj)
                await session.commit()
                return obj
        except IntegrityError as e:
            detail = str(e.orig.args[0])
            raise ValueError(detail.split("\n")[1])

    async def update(self) -> None:
        try:
            orm_cls = self.Meta.orm_model
            ignore_fields = self.Meta.ignore_fields if hasattr(self.Meta, 'ignore_fields') else {}
            stmt = (
                update(orm_cls)
                .where(orm_cls.id == self.id)
                .values(**self.model_dump(exclude=ignore_fields))
            )
            async with Session() as session:
                await session.execute(stmt)
                await session.commit()
                return
        except IntegrityError as e:
            detail = str(e.orig.args[0])
            raise ValueError(detail.split("\n")[1])

    async def db_update_fields(self, **kwargs):
        try:
            orm_model = self.Meta.orm_model
            async with Session() as session:
                stmt = update(orm_model).where(orm_model.id == self.id).values(**kwargs)
                await session.execute(stmt)
                await session.commit()

        except IntegrityError as e:
            detail = str(e.orig.args[0])
            raise ValueError(detail.split("\n")[1])
        
    @classmethod
    async def db_update_fields_by_id(cls, id_, **kwargs):
        try:
            orm_model = cls.Meta.orm_model
            async with Session() as session:
                stmt = update(orm_model).where(orm_model.id == id_).values(**kwargs)
                await session.execute(stmt)
                await session.commit()

        except IntegrityError as e:
            detail = str(e.orig.args[0])
            raise ValueError(detail.split("\n")[1])

    @classmethod
    async def db_delete(cls, id: int) -> None:
        try:
            orm_cls = cls.Meta.orm_model
            if getattr(orm_cls, 'is_deleted'):
                stmt = update(orm_cls).where(orm_cls.id == id).values(is_deleted=True)
            else:
                stmt = delete(orm_cls).where(orm_cls.id == id)
            async with Session() as session:
                await session.execute(stmt)
                await session.commit()
        except IntegrityError as e:
            detail = str(e.orig.args[0])
            raise ValueError(detail.split("\n")[1])

    @classmethod
    async def _db_get(cls, limit=None, **kwargs):
        orm_cls = cls.Meta.orm_model
        stmt = select(orm_cls).filter_by(**kwargs)
        if limit:
            stmt = stmt.limit(limit)
        async with Session() as session:
            return await session.execute(stmt.order_by(orm_cls.created_at.desc()))

    @classmethod
    async def db_get_or_none(cls, **kwargs):
        q = await cls._db_get(limit=1, **kwargs)
        q_first = q.scalars().first()
        if q_first:
            return TypeAdapter(cls).validate_python(q_first)
        return None

    @classmethod
    async def db_get_many(cls, **kwargs):
        q = await cls._db_get(**kwargs)
        q_all = q.scalars().all()
        return TypeAdapter(list[cls]).validate_python(q_all)
    
    @classmethod
    async def db_get_amount_of_recent_created(cls, period: timedelta, **kwargs) -> int:
        orm_cls = cls.Meta.orm_model
        stmt = (
            select(func.count(orm_cls.id))
            .where(orm_cls.created_at > datetime.now() - period)
            .filter_by(**kwargs)
            .select_from(orm_cls)
        )
        async with Session() as session:
            q = await session.execute(stmt)
            return q.scalars().first()
        
    @classmethod
    async def db_get_ensure(cls, **kwargs):
        obj = await cls.db_get_or_none(**kwargs)
        if obj:
            return obj
        raise ValueError(f"Cannot find object ({kwargs})")
    
    @classmethod
    async def db_exists(cls, **kwargs):
        q = await cls._db_get(**kwargs)
        q_first = q.scalars().first()
        if q_first:
            return True
        return False
        
