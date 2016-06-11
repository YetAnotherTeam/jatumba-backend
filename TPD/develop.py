import json
import logging

from TPD.settings import *  # noqa

DEBUG = True
SQL_DEBUG = True


class NonHtmlDebugToolbarMiddleware(object):
    """
    The Django Debug Toolbar usually only works for views that return HTML.
    This middleware wraps any non-HTML response in HTML if the request
    has a 'debug' query parameter (e.g. http://localhost/foo?debug)
    Special handling for json (pretty printing) and
    binary data (only show data length)
    """

    @staticmethod
    def process_response(request, response):
        if request.GET.get('debug') == '':
            if response['Content-Type'] == 'application/octet-stream':
                new_content = ('<html><body>Binary Data, Length: {}</body></html>'
                               .format(len(response.content)))
                response = HttpResponse(new_content)
            elif response['Content-Type'] != 'text/html':
                content = response.content
                try:
                    json_ = json.loads(content)
                    content = json.dumps(json_, sort_keys=True, indent=2)
                except ValueError:
                    pass
                response = HttpResponse('<html><body><pre>{}</pre></body></html>'.format(content))

        return response


class SQLFormatter(logging.Formatter):
    def format(self, record):
        # Check if Pygments is available for coloring
        try:
            import pygments
            from pygments.lexers import SqlLexer
            from pygments.formatters import Terminal256Formatter
        except ImportError:
            pygments = None

        # Check if sqlparse is available for indentation
        try:
            import sqlparse
        except ImportError:
            sqlparse = None

        # Remove leading and trailing whitespacespip
        sql = record.sql.strip()

        if sqlparse:
            # Indent the SQL query
            sql = sqlparse.format(sql, reindent=True)

        if pygments:
            # Highlight the SQL query
            sql = pygments.highlight(
                sql,
                SqlLexer(),
                Terminal256Formatter(style='monokai')
            )

        # Set the record's statement to the formatted query
        record.statement = sql
        return super(SQLFormatter, self).format(record)


if SQL_DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
    )

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'TPD.develop.NonHtmlDebugToolbarMiddleware',
    )

    LOGGING = {
        'version': 1,
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['sql'],
                'propagate': False,
            }
        },
        'handlers': {
            'sql': {
                'class': 'logging.StreamHandler',
                'formatter': 'sql',
                'level': 'DEBUG',
            }
        },
        'formatters': {
            'sql': {
                '()': SQLFormatter,
                'format': '[%(duration).3f] %(statement)s',
            }
        }
    }
