import os
from io import BytesIO

from flask import Flask, g

from cloudmachine.ext.flask import CloudMachine
from cloudmachine.resources import CloudMachineDeployment, StorageAccount, Sku, ResourceGroup


# deployment = CloudMachineDeployment(
#     name="testfoo",
#     #host="local" | "appService" | "container",
#     storage=StorageAccount(
#         sku=Sku(name='Premium_ZRS'),
#         kind='StorageV2'
#     )
# )

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    #cm = CloudMachine(deployment=deployment)
    cm = CloudMachine(name="testfoo")

    cm.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    # a simple page that says hello
    @app.route('/hello')
    def hello():
        g.cloudmachine.storage.upload("testblob", BytesIO(b"Hello, World!"))

        return 'Hello, World!'


    return app