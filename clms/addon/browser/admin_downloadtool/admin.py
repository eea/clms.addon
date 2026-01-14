"""Admin browser views for DownloadTool database management."""

import json
import os
from datetime import datetime, timezone
from logging import getLogger

from BTrees.OOBTree import OOBTree
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite

from clms.downloadtool.utils import ANNOTATION_KEY

log = getLogger(__name__)

TABLE_NAME = "downloadtool_tasks"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS downloadtool_tasks (
    task_id TEXT PRIMARY KEY,
    payload JSONB NOT NULL,
    user_id TEXT,
    status TEXT,
    cdse_task_group_id TEXT,
    registration_datetime TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
"""

INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS downloadtool_tasks_user_id_idx "
    "ON downloadtool_tasks (user_id)",
    "CREATE INDEX IF NOT EXISTS downloadtool_tasks_status_idx "
    "ON downloadtool_tasks (status)",
    "CREATE INDEX IF NOT EXISTS downloadtool_tasks_cdse_group_idx "
    "ON downloadtool_tasks (cdse_task_group_id)",
    "CREATE INDEX IF NOT EXISTS downloadtool_tasks_reg_dt_idx "
    "ON downloadtool_tasks (registration_datetime)",
)


def _get_psycopg2():
    try:
        import psycopg2
        from psycopg2 import extras
    except ImportError as exc:
        return None, None, "psycopg2 is not available: {0}".format(exc)
    return psycopg2, extras, None


def _get_dsn():
    dsn = os.environ.get("DOWNLOADTOOL_DB_DSN", "").strip()
    if not dsn:
        return None, "DOWNLOADTOOL_DB_DSN is not set"
    return dsn, None


def _json_response(view, payload, status=200):
    view.request.response.setHeader("Content-Type", "application/json")
    view.request.response.setStatus(status)
    return json.dumps(payload, default=str, indent=2, sort_keys=True)


def _table_exists(cursor):
    cursor.execute("SELECT to_regclass(%s)", (TABLE_NAME,))
    return cursor.fetchone()[0] is not None


class CreateDownloadtoolDatabase(BrowserView):
    """Create the DownloadTool database structure."""

    def __call__(self):
        dsn, error = _get_dsn()
        if error:
            return _json_response(self, {"status": "error", "message": error}, 400)

        psycopg2, _extras, error = _get_psycopg2()
        if error:
            return _json_response(self, {"status": "error", "message": error}, 500)

        try:
            with psycopg2.connect(dsn) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(CREATE_TABLE_SQL)
                    for statement in INDEX_SQL:
                        cursor.execute(statement)
        except Exception as exc:
            log.exception("Failed to create DownloadTool table")
            return _json_response(
                self, {"status": "error", "message": str(exc)}, 500
            )

        return _json_response(self, {"status": "ok", "table": TABLE_NAME})


class DownloadtoolDatabaseDetails(BrowserView):
    """Inspect the DownloadTool database structure and status."""

    def __call__(self):
        dsn, error = _get_dsn()
        if error:
            return _json_response(self, {"status": "error", "message": error}, 400)

        psycopg2, _extras, error = _get_psycopg2()
        if error:
            return _json_response(self, {"status": "error", "message": error}, 500)

        filter_rows = self.request.form.get("filter") == "rows"
        from_param = self.request.form.get("from")
        to_param = self.request.form.get("to")

        offset = None
        limit = None
        if filter_rows:
            try:
                offset = int(from_param) if from_param is not None else 0
                limit_to = int(to_param) if to_param is not None else offset + 99
            except (TypeError, ValueError):
                return _json_response(
                    self,
                    {
                        "status": "error",
                        "message": "Invalid from/to values",
                    },
                    400,
                )
            if offset < 0 or limit_to < offset:
                return _json_response(
                    self,
                    {
                        "status": "error",
                        "message": "Invalid range",
                    },
                    400,
                )
            limit = limit_to - offset + 1

        try:
            with psycopg2.connect(dsn) as conn:
                with conn.cursor() as cursor:
                    exists = _table_exists(cursor)
                    if not exists:
                        return _json_response(
                            self,
                            {
                                "status": "ok",
                                "table": TABLE_NAME,
                                "exists": False,
                                "row_count": 0,
                                "columns": [],
                            },
                        )

                    cursor.execute(
                        """
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = %s
                        ORDER BY ordinal_position
                        """,
                        (TABLE_NAME,),
                    )
                    columns = [
                        {
                            "name": row[0],
                            "type": row[1],
                            "nullable": row[2] == "YES",
                        }
                        for row in cursor.fetchall()
                    ]

                    cursor.execute("SELECT COUNT(*) FROM downloadtool_tasks")
                    row_count = cursor.fetchone()[0]

                    rows = []
                    if filter_rows:
                        cursor.execute(
                            """
                            SELECT
                                task_id,
                                payload,
                                user_id,
                                status,
                                cdse_task_group_id,
                                registration_datetime,
                                updated_at
                            FROM downloadtool_tasks
                            ORDER BY registration_datetime NULLS LAST, task_id
                            OFFSET %s LIMIT %s
                            """,
                            (offset, limit),
                        )
                        for row in cursor.fetchall():
                            rows.append(
                                {
                                    "task_id": row[0],
                                    "payload": row[1],
                                    "user_id": row[2],
                                    "status": row[3],
                                    "cdse_task_group_id": row[4],
                                    "registration_datetime": row[5],
                                    "updated_at": row[6],
                                }
                            )
        except Exception as exc:
            log.exception("Failed to read DownloadTool table details")
            return _json_response(
                self, {"status": "error", "message": str(exc)}, 500
            )

        response = {
            "status": "ok",
            "table": TABLE_NAME,
            "exists": True,
            "row_count": row_count,
            "columns": columns,
        }

        if filter_rows:
            response["rows"] = rows
            response["from"] = offset
            response["to"] = offset + len(rows) - 1 if rows else offset - 1

        return _json_response(
            self,
            response,
        )


class MigrateDownloadtoolAnnotations(BrowserView):
    """Migrate annotation-backed tasks into the DownloadTool database."""

    def __call__(self):
        dsn, error = _get_dsn()
        if error:
            return _json_response(self, {"status": "error", "message": error}, 400)

        psycopg2, extras, error = _get_psycopg2()
        if error:
            return _json_response(self, {"status": "error", "message": error}, 500)

        site = getSite()
        annotations = IAnnotations(site)
        registry = annotations.get(ANNOTATION_KEY, OOBTree())

        if not registry:
            return _json_response(
                self,
                {
                    "status": "ok",
                    "message": "No annotation data found",
                    "migrated": 0,
                },
            )

        migrated = 0
        try:
            with psycopg2.connect(dsn) as conn:
                with conn.cursor() as cursor:
                    if not _table_exists(cursor):
                        return _json_response(
                            self,
                            {
                                "status": "error",
                                "message": "Table does not exist",
                            },
                            400,
                        )

                    for task_id, payload in registry.items():
                        user_id = payload.get("UserID")
                        status = payload.get("Status")
                        cdse_group_id = payload.get("cdse_task_group_id")
                        registration_dt = payload.get("RegistrationDateTime")
                        updated_at = datetime.now(timezone.utc)
                        cursor.execute(
                            """
                            INSERT INTO downloadtool_tasks (
                                task_id,
                                payload,
                                user_id,
                                status,
                                cdse_task_group_id,
                                registration_datetime,
                                updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (task_id) DO UPDATE SET
                                payload = EXCLUDED.payload,
                                user_id = EXCLUDED.user_id,
                                status = EXCLUDED.status,
                                cdse_task_group_id = EXCLUDED.cdse_task_group_id,
                                registration_datetime = EXCLUDED.registration_datetime,
                                updated_at = EXCLUDED.updated_at
                            """,
                            (
                                str(task_id),
                                extras.Json(payload),
                                user_id,
                                status,
                                cdse_group_id,
                                registration_dt,
                                updated_at,
                            ),
                        )
                        migrated += 1
        except Exception as exc:
            log.exception("Failed to migrate annotations to DownloadTool DB")
            return _json_response(
                self, {"status": "error", "message": str(exc)}, 500
            )

        return _json_response(
            self, {"status": "ok", "migrated": migrated, "table": TABLE_NAME}
        )


class ClearDownloadtoolDatabase(BrowserView):
    """Remove all records from the DownloadTool database."""

    def __call__(self):
        dsn, error = _get_dsn()
        if error:
            return _json_response(self, {"status": "error", "message": error}, 400)

        psycopg2, _extras, error = _get_psycopg2()
        if error:
            return _json_response(self, {"status": "error", "message": error}, 500)

        try:
            with psycopg2.connect(dsn) as conn:
                with conn.cursor() as cursor:
                    if not _table_exists(cursor):
                        return _json_response(
                            self,
                            {
                                "status": "error",
                                "message": "Table does not exist",
                            },
                            400,
                        )
                    cursor.execute("DELETE FROM downloadtool_tasks")
        except Exception as exc:
            log.exception("Failed to clear DownloadTool DB")
            return _json_response(
                self, {"status": "error", "message": str(exc)}, 500
            )

        return _json_response(
            self, {"status": "ok", "table": TABLE_NAME, "deleted": "all"}
        )
