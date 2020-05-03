from logging import getLogger

from chalice import Chalice

from chalicelib.views import mgmt, sources, tgbot
from chalicelib.configer import APP_NAME, DEBUG


lg = getLogger(f'{APP_NAME}.{__name__}')
app = Chalice(app_name=APP_NAME, debug=DEBUG)
app.experimental_feature_flags.update([
    'BLUEPRINTS'
])

# registration blueprints
app.register_blueprint(mgmt.bp, url_prefix='/mgmt')
app.register_blueprint(sources.bp, url_prefix='/sources')
app.register_blueprint(tgbot.bp, url_prefix='/tgbot')
