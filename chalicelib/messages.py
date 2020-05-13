from logging import getLogger

from chalicelib.ddb_manage import (
    get_cases,
    DDBUnknownRegion,
    DDBNoCases
)
from chalicelib.configer import (
    APP_NAME,
    DDB_TOTAL_TABLE_NAME,
    DDB_CASES_TABLE_NAME
)


lg = getLogger(f'{APP_NAME}.{__name__}')


class TGMessage():
    content = ''

    def get_message(self, content=None, header=None, footer=None):
        header = self.header() if header is None else header
        footer = self.footer() if footer is None else footer
        content = self.content if content is None else content
        return f'{header}{content}{footer}'

    def header(self):
        return ''

    def footer(self):
        return ''


class TGCaseStatsMessage(TGMessage):

    def __init__(self, region, date=None):
        self.region, self.date = region, date
        for table in (DDB_CASES_TABLE_NAME, DDB_TOTAL_TABLE_NAME):
            try:
                lg.info(f'Trying get cases for {self.region} in {table}')
                content = get_cases(self.region, table).to_dict()
            except (DDBUnknownRegion, DDBNoCases) as e:
                lg.warn(getattr(e, "message", repr(e)))
                content = {'error': f'{e}\n'}
            except Exception as e:
                lg.exception(e)
                content = {'error': 'Internal error, try again later\n'}
            finally:
                lg.debug(f'Content for message is {content}')
                self.pop_content(content, table)

    def pop_content(self, content, table):
        if table == DDB_TOTAL_TABLE_NAME:
            header = f'*Total cases*\n'
        if table == DDB_CASES_TABLE_NAME:
            header = f'*New cases*\n'
        if not content.get('error'):
            cases = int(content["cases"])
            recovered = int(content["recovered"])
            left = int(content["deaths"])
        if content.get('error'):
            content = content['error']
        else:
            content = f'On *{content["actual_date"]}*\n' \
                      f'   _Cases_: {cases:,}\n'         \
                      f'   _Recovered_: {recovered:,}\n' \
                      f'   _Left_: {left:,}\n\n'
        self.content += f'{header}{content}'

    def header(self):
        return f'*{self.region.capitalize()}*: covid-19 statistics\n\n'

    def footer(self):
        return f"Subscribe to this statistics by /subscribe\\_{self.region}"


class TGHelpMessage(TGMessage):

    def __init__(self, region=None):
        self.pop_content()

    def pop_content(self):
        content = 'Hello! I can send you statistics about COVID-19 '      \
            'cases by regions.\n'                                         \
            '*Commands*:\n'                                               \
            '/russia - Russia stats\n'                                    \
            '/subscribe\\_[country] - get a subscription to a country\n'  \
            '/unsubscribe\\_[country] - delete an existed subscription\n' \
            '/unsubscribe\\_all - delete all existed subscriptions\n'
        self.content = content


class TGSubscribeMessage(TGMessage):

    def __init__(self, region):
        self.region = region
        self.pop_content()

    def pop_content(self):
        content = "" \
            f"You've subscribed to {self.region.capitalize()}. "              \
            f"It'll notify you when the statistics will be updated. "         \
            f"Send /unsubscribe\\_{self.region}, if you do not to get it. "   \
            f"Or send /unsubscribe\\_all, to delete all subscriptions."
        self.content = content

    def header(self):
        return f'Congrats!\n'
