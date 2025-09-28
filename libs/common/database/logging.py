from contextvars import ContextVar
import time
from typing import Any
import warnings

from common.logger import get_logger
from common.sentry.config import sentry_config
from sqlalchemy import ClauseElement, Compiled, Connection, event
from sqlalchemy.dialects.postgresql.asyncpg import PGExecutionContext_asyncpg
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SAWarning
import sqlparse  # type: ignore[import-untyped]


__all__ = ["setup_alchemy_logging"]


logger = get_logger(__name__)


alchemy_query_start_time = ContextVar("alchemy_query_start_time", default=0.0)


def setup_alchemy_logging() -> None:
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(*_: Any) -> None:
        query_start_time = time.time()
        alchemy_query_start_time.set(query_start_time)

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(
        _conn: Connection,
        _cursor: Any,
        statement: str,
        _parameters: Any,
        context: PGExecutionContext_asyncpg,
        _executemany: Any,
    ) -> None:
        query_start_time = alchemy_query_start_time.get()
        query_duration = time.time() - query_start_time

        # В момент компиляции запроса объект ещё не имеет значения id, оно ещё не подтянуто из базы
        warnings.filterwarnings("ignore", category=SAWarning, message=".*NULL.*")

        compiled = context.compiled
        if isinstance(compiled, Compiled) and isinstance(compiled.statement, ClauseElement):
            compiled_sql = compiled.statement.compile(dialect=compiled.dialect, compile_kwargs={"literal_binds": True})
            formatted_sql = sqlparse.format(str(compiled_sql), reindent=True, keyword_case="upper")
        else:
            formatted_sql = sqlparse.format(statement, reindent=True, keyword_case="upper")

        logger.debug("%s\nQuery Time: %.5fs", query_duration, formatted_sql)
        if query_duration > sentry_config.slow_sql_threshold:
            logger.warning("Slow SQL query", extra={"query": formatted_sql, "duration": query_duration})
