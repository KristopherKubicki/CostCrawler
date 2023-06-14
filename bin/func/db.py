
import sqlalchemy as sa
import sqlalchemy.orm
from func import config

_engine = sa.create_engine(config.config['database'], pool_size=100)  # type: Any

sessionmaker = sa.orm.sessionmaker(bind=_engine, autoflush=False)  # type: Any
session = sa.orm.scoped_session(sessionmaker)

