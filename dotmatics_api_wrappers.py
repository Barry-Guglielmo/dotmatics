import requests
import json
from aiohttp import BasicAuth

# curl -H X-CDD-Token:$TOKEN 'https://app.collaborativedrug.com/api/v1/vaults/23/protocols?async=true'
class Session:
    """
    Create a Session for interacting with Dotmatics

    A Session will require a url, a user, and a password. The other params have defaults that we typically wont change.
    Creating a session will request a token over https. This token will then be used through the ETL process.
    Dfault expiration of token is 86400 seconds.

    Attributes
    ----------
    url : str
        url for the site you want to reach (be sure to whitelist LD server/Resources on Dotmatics Side)
    user : str
        user created by Dotmatics team (Typically called LDADMIN)
    password : str
        password created by Dotmatics team (Dotmatics is required to maintain this) This password will be used to generate a token.
    """

    def get(self, endpoint):
        """
        This is a simple get function that uses requests library. It simply takes an endpoint and returns the results as json.
        You can use this for testing endpoints. It is used in the higher level functions that actually generate endpoints then feed them in.

        Parameters
        ----------
        endpoint : str
            an endpoint to request information from Dotmatics.
        """
        response = requests.get(url=endpoint)
        return response

    def __init__(self,url, user = '', password = '',  token = False, port='443', expire = 86400):
        """
        Initialize a Session so that you can easily make requests to Dotmatics API

        Parameters
        ----------
        url : str
            url for the site you want to reach (be sure to whitelist LD server/Resources on Dotmatics Side)
        user : str
            user created by Dotmatics team (Typically called LDADMIN)
        password : str
            password created by Dotmatics team (Dotmatics is required to maintain this) This password will be used to generate a token.
        """

        self.url = '%s:%s'%(url,port)
        self.port = port
        self.user = user
        self.password = password
        self.expire = expire
        self._auth = BasicAuth(self.user, self.password)

        if token != False:
            self.creds = '/?token=%s'%(token)
        else:
            self.plain_creds = '/?isid=%s&password=%s'%(user, password)
            self.token_request_url=self.url+'/browser/api/authenticate/requestToken%s&expiration=%i'%(self.plain_creds,self.expire)
            self.token =  self.get(self.url+'/browser/api/authenticate/requestToken%s&expiration=%i'%(self.plain_creds,self.expire)).text.strip('"')
            self.creds = '?token=%s'%(self.token)

    def get_datasource(self, project, data_source, ids = '*',params=''):
        '''
        This is the main driver for the ETL and in api.py the rest of these functions are very useful for SA usage.
        The endpoint is /data/<isid>/<projectid>/<dskeys>/<ids>
        The only input you need to provide is the project id and the data_source id (see readme for more on datasources)

        Parameters
        ----------
        project : int
            REQUIRED project id as int that you want to pull from in the data source
        data_source : int
            REQUIRED the data source as int to pull from (Data sources are really just out put of sql statments run on Dotmatics servers and data)
        user : str
            PREFILLED self.user of the session class
        ids : str
            OPTIONAL ids to pull (we use wild card *)
        credentials : str
            PREFILLED credentials typically as a token
        params : str
            OPTIONAL other paramiters for your query
        '''
        d = self.get(self.url+'/browser/api/data/%s/%i/%i/%s%s&%s'%(self.user, project, data_source, ids, self.creds, params)).text
        return json.loads(d)
    def get_collection(self, collection):
        '''/browser/api/<collection>'''
        return self.get(self.url+'/browser/api/%s%s'%(str(collection), self.creds))

    def get_users(self):
        '''/browser/api/users'''
        return self.get(self.url+'/browser/api/users')

    def get_protocol(self, protocol):
        return json.loads(self.get(self.url+'/browser/api/studies/protocol/%s%s'%(str(protocol),self.creds)).text)

    def get_datasources(self, project = 'all'):
        '''
        Get list of all datasources or all datasources from a project
        /browser/api/datasources/project/<projectid>
        '''
        if project == 'all':
            # returns list of ds [514,234,...]
            return self.get(self.url+'/browser/api/datasources%s'%(self.creds))
        else:
            return self.get(self.url+'/browser/api/datasources/project/%s%s'%(project, self.creds))

    def get_datasource_info(self, datasource):
        d = self.get(self.url+'/browser/api/datasources/%s%s'%(datasource, self.creds)).text
        return json.loads(d)

    def get_datasource(self, project, data_source, ids = '*',params=''):
        '''
        This is the main driver for api.py the rest of these functions are very useful for SA usage.
        endpoint is /data/<isid>/<projectid>/<dskeys>/<ids>

        Parameters
        ----------
        project : int
            REQUIRED project id as int that you want to pull from in the data source
        data_source : int
            REQUIRED the data source as int to pull from (Data sources are really just out put of sql statments run on Dotmatics servers and data)
        user : str
            PREFILLED self.user of the session class
        ids : str
            OPTIONAL ids to pull (we use wild card *)
        credentials : str
            PREFILLED credentials typically as a token
        params : str
            OPTIONAL other paramiters for your query
        '''
        d = self.get(self.url+'/browser/api/data/%s/%i/%i/%s%s&%s'%(self.user, project, data_source, ids, self.creds, params)).text
        return json.loads(d)

    def get_structures(self, project):
        '''/structure/<isid>/<projectid>/<ids>'''
        return self.get(self.url+'/browser/api/structure/*/%s%s'%(project, self.creds))

    def get_projects(self):
        '''/projects/

           Returns project pks
        '''
        projs = self.get(self.url+'/browser/api/projects%s'%(self.creds)).text.strip('][').split(',')
        return [int(i.strip('"')) for i in projs]

    def get_project(self, project):
        '''
        This will query the /browser/api/projects/<projectid>
        Returns dictionary of project info

        Parameters
        ----------
        int
           Project ID

        Returns
        -------
        dict
            Returns a dictionary with the following keys:
            ['projectID', 'projectName', 'projectType', 'projectTypeDescr',
            'projectCategory', 'description', 'defaultJoinColumn',
            'JOIN_FORMAT', 'defaultDateColumn', 'primaryRegExp', 'primaryLength',
            'dateFormatOracle', 'dateFormatJava', 'projectForms', 'dataSources',
            'throttle', 'autoButtons', 'custom_img_size', 'isEditable', 'isHidden',
            'dynamicStructures', 'orderby', 'latest_date', 'count', 'POPULATE_PROJECT_NAME_YN',
            'AUDIT_YN', 'run_after_query', 'exclusive', 'numberFormats', 'excel_img_size',
            'listBindings', 'autorun', 'productonly', 'BROWSEMODEEDITING', 'autofetchRestful']
        '''
        d = self.get(self.url+'/browser/api/projects/%i%s'%(project, self.creds)).text
        return json.loads(d)

    def get_query(self, endpoint):
        '''/query/<isid>/<projectID>/<dsid>/<dskeys>/<operator>/<parameter>'''
        return 0
