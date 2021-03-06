# encoding: utf-8
import re

from sqlalchemy import engine_from_config, orm

from ..defaults import get_default_db_uri
from .tables import Language, metadata
from .multilang import MultilangSession, MultilangScopedSession

ENGLISH_ID = 9


def connect(uri=None, session_args={}, engine_args={}, engine_prefix=''):
    """Connects to the requested URI.  Returns a session object.

    With the URI omitted, attempts to connect to a default SQLite database
    contained within the package directory.

    Calling this function also binds the metadata object to the created engine.
    """

    # If we didn't get a uri, fall back to the default
    if uri is None:
        uri = engine_args.get(engine_prefix + 'url', None)
    if uri is None:
        uri = get_default_db_uri()

    ### Do some fixery for MySQL
    if uri.startswith('mysql:'):
        # MySQL uses latin1 for connections by default even if the server is
        # otherwise oozing with utf8; charset fixes this
        if 'charset' not in uri:
            uri += '?charset=utf8'

        # Tables should be InnoDB, in the event that we're creating them, and
        # use UTF-8 goddammit!
        for table in list(metadata.tables.values()):
            table.kwargs['mysql_engine'] = 'InnoDB'
            table.kwargs['mysql_charset'] = 'utf8'

    ### Connect
    engine_args[engine_prefix + 'url'] = uri
    engine = engine_from_config(engine_args, prefix=engine_prefix)
    conn = engine.connect()
    metadata.bind = engine

    all_session_args = dict(autoflush=True, autocommit=False, bind=engine)
    all_session_args.update(session_args)
    sm = orm.sessionmaker(class_=MultilangSession,
        default_language_id=ENGLISH_ID, **all_session_args)
    session = MultilangScopedSession(sm)

    return session

def identifier_from_name(name):
    """Make a string safe to use as an identifier.

    Valid characters are lowercase alphanumerics and "-". This function may
    raise ValueError if it can't come up with a suitable identifier.

    This function is useful for scripts which add things with names.
    """
    if isinstance(name, str):
        identifier = name.decode('utf-8')
    else:
        identifier = name
    identifier = identifier.lower()
    identifier = identifier.replace('+', ' plus ')
    identifier = re.sub('[ _–]+', '-', identifier)
    identifier = re.sub("['./;’(),:]", '', identifier)
    identifier = identifier.replace('é', 'e')
    identifier = identifier.replace('♀', '-f')
    identifier = identifier.replace('♂', '-m')
    if identifier in ('???', '????'):
        identifier = 'unknown'
    elif identifier == '!':
        identifier = 'exclamation'
    elif identifier == '?':
        identifier = 'question'

    if not identifier.replace("-", "").isalnum():
        raise ValueError(identifier)
    return identifier
