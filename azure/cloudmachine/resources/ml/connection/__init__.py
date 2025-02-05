from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required


class ConnectionParams(TypedDict, total=False):
    """"""
    category: Required[Literal['ADLSGen2', 'AIServices', 'AmazonMws', 'AmazonRdsForOracle', 'AmazonRdsForSqlServer', 'AmazonRedshift', 'AmazonS3Compatible', 'ApiKey', 'AzureBlob', 'AzureDatabricksDeltaLake', 'AzureDataExplorer', 'AzureMariaDb', 'AzureMySqlDb', 'AzureOneLake', 'AzureOpenAI', 'AzurePostgresDb', 'AzureSqlDb', 'AzureSqlMi', 'AzureSynapseAnalytics', 'AzureTableStorage', 'BingLLMSearch', 'Cassandra', 'CognitiveSearch', 'CognitiveService', 'Concur', 'ContainerRegistry', 'CosmosDb', 'CosmosDbMongoDbApi', 'Couchbase', 'CustomKeys', 'Db2', 'Drill', 'Dynamics', 'DynamicsAx', 'DynamicsCrm', 'Eloqua', 'FileServer', 'FtpServer', 'GenericContainerRegistry', 'GenericHttp', 'GenericRest', 'Git', 'GoogleAdWords', 'GoogleBigQuery', 'GoogleCloudStorage', 'Greenplum', 'Hbase', 'Hdfs', 'Hive', 'Hubspot', 'Impala', 'Informix', 'Jira', 'Magento', 'MariaDb', 'Marketo', 'MicrosoftAccess', 'MongoDbAtlas', 'MongoDbV2', 'MySql', 'Netezza', 'ODataRest', 'Odbc', 'Office365', 'OpenAI', 'Oracle', 'OracleCloudStorage', 'OracleServiceCloud', 'PayPal', 'Phoenix', 'PostgreSql', 'Presto', 'PythonFeed', 'QuickBooks', 'Redis', 'Responsys', 'S3', 'Salesforce', 'SalesforceMarketingCloud', 'SalesforceServiceCloud', 'SapBw', 'SapCloudForCustomer', 'SapEcc', 'SapHana', 'SapOpenHub', 'SapTable', 'Serp', 'Serverless', 'ServiceNow', 'Sftp', 'SharePointOnlineList', 'Shopify', 'Snowflake', 'Spark', 'SqlServer', 'Square', 'Sybase', 'Teradata', 'Vertica', 'WebTable', 'Xero', 'Zoho']]
    """Category of the connection."""
    connectionProperties: Required[Dict[str, object]]
    """The properties of the connection, specific to the auth type."""
    name: Required[str]
    """Name of the connection to create."""
    target: Required[str]
    """The target of the connection."""
    expiryTime: str
    """The expiry time of the connection."""
    isSharedToAll: bool
    """Indicates whether the connection is shared to all users in the workspace."""
    metadata: Dict[str, object]
    """User metadata for the connection."""
    sharedUserList: List[object]
    """The shared user list of the connection."""
    value: str
    """Value details of the workspace connection."""


class ConnectionKwargs(TypedDict, total=False):
    """"""
    category: Literal['ADLSGen2', 'AIServices', 'AmazonMws', 'AmazonRdsForOracle', 'AmazonRdsForSqlServer', 'AmazonRedshift', 'AmazonS3Compatible', 'ApiKey', 'AzureBlob', 'AzureDatabricksDeltaLake', 'AzureDataExplorer', 'AzureMariaDb', 'AzureMySqlDb', 'AzureOneLake', 'AzureOpenAI', 'AzurePostgresDb', 'AzureSqlDb', 'AzureSqlMi', 'AzureSynapseAnalytics', 'AzureTableStorage', 'BingLLMSearch', 'Cassandra', 'CognitiveSearch', 'CognitiveService', 'Concur', 'ContainerRegistry', 'CosmosDb', 'CosmosDbMongoDbApi', 'Couchbase', 'CustomKeys', 'Db2', 'Drill', 'Dynamics', 'DynamicsAx', 'DynamicsCrm', 'Eloqua', 'FileServer', 'FtpServer', 'GenericContainerRegistry', 'GenericHttp', 'GenericRest', 'Git', 'GoogleAdWords', 'GoogleBigQuery', 'GoogleCloudStorage', 'Greenplum', 'Hbase', 'Hdfs', 'Hive', 'Hubspot', 'Impala', 'Informix', 'Jira', 'Magento', 'MariaDb', 'Marketo', 'MicrosoftAccess', 'MongoDbAtlas', 'MongoDbV2', 'MySql', 'Netezza', 'ODataRest', 'Odbc', 'Office365', 'OpenAI', 'Oracle', 'OracleCloudStorage', 'OracleServiceCloud', 'PayPal', 'Phoenix', 'PostgreSql', 'Presto', 'PythonFeed', 'QuickBooks', 'Redis', 'Responsys', 'S3', 'Salesforce', 'SalesforceMarketingCloud', 'SalesforceServiceCloud', 'SapBw', 'SapCloudForCustomer', 'SapEcc', 'SapHana', 'SapOpenHub', 'SapTable', 'Serp', 'Serverless', 'ServiceNow', 'Sftp', 'SharePointOnlineList', 'Shopify', 'Snowflake', 'Spark', 'SqlServer', 'Square', 'Sybase', 'Teradata', 'Vertica', 'WebTable', 'Xero', 'Zoho']
    """Category of the connection."""
    connection_properties: Dict[str, object]
    """The properties of the connection, specific to the auth type."""
    target: str
    """The target of the connection."""
    expiry_time: str
    """The expiry time of the connection."""
    is_shared_to_all: bool
    """Indicates whether the connection is shared to all users in the workspace."""
    metadata: Dict[str, object]
    """User metadata for the connection."""
    shared_user_list: List[object]
    """The shared user list of the connection."""
    value: str
    """Value details of the workspace connection."""
