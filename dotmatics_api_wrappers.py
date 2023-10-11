import requests
import json
from aiohttp import BasicAuth

# curl -H X-CDD-Token:$TOKEN 'https://app.collaborativedrug.com/api/v1/vaults/23/protocols?async=true'
class Session:

    def get(self, endpoint):
        response = requests.get(url=endpoint)
        return response

    def __init__(self,url, user = '', password = '', token = False, expire = 86400):
        '''
        For authentication, you are required to provide valid isid (username) and password parameters, or a
        security token, with every request:
        '''

        self.url = url
        self.user = user
        self.password = password
        self.expire = expire
        self._auth = BasicAuth(self.user, self.password)

        if token != False:
            self.creds = '?token=%s'%token
        else:
            self.plain_creds = '?isid=%s&password=%s'%(user, password)
            self.token =  self.get(self.url+'/browser/api/authenticate/requestToken%s&expiration=%i'%(self.plain_creds,self.expire)).text.strip('"')
            self.creds = '?token=%s'%self.token
    def get_collection(self, collection):
        '''/browser/api/<collection>'''
        return self.get(self.url+'/browser/api/%s%s'%(str(collection), self.creds))

    def get_users(self):
        '''/browser/api/users'''
        return self.get(self.url+'/browser/api/users')

    def get_datasources(self, project = 'all'):
        '''
        Get list of all datasources or all datasources from a project
        /datasources/project/<projectid>
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
        /data/<isid>/<projectid>/<dskeys>/<ids>
        A wildcard “*” may be specified to retrieve data for
        all of the IDs from the project’s summary datasource
        params can be offset=<number> or limit=<number>
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
        '''/projects/<projectid>
        Returns dictionary of project info

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
