import requests
import json

# curl -H X-CDD-Token:$TOKEN 'https://app.collaborativedrug.com/api/v1/vaults/23/protocols?async=true'
class Session:
    def __init__(self,url, user = '', password = '', token = False):
        '''
        For authentication, you are required to provide valid isid (username) and password parameters, or a
        security token, with every request:
        '''

        self.url = url
        self.user = user
        self.password = password
        if token != False:
            self.creds = '?token=%s'%token
        else:
            # PROBABLY SHOULD REQUEST A TOKEN HERE
            # /authenticate/requestToken?expiration=<seconds>
            self.creds = '?isid=%s&password=%s'%(user, password)

    def get(self, endpoint):
        response = requests.get(url=endpoint)
        return json.loads(response.text)

    def get_collection(self, collection):
        '''/browser/api/<collection>'''
        return self.get(self.url+'/browser/api/%s%s'%(str(collection), self.creds))
    
    def get_users(self):
        '''/browser/api/users'''
        return self.get(self.url+'/browser/api/users')
    
    def get_datasources(self, project = 'all'):
        '''
        Get all datasources or all datasources from a project
        /datasources/project/<projectid>
        '''
        if project == 'all':
            # returns list of ds [514,234,...]
            return self.get(self.url+'/datasources%s'%(self.creds))
        else:
            return self.get(self.url+'/datasources/project/%s%s'%(project, self.creds))

    def get_datasource_data(self, project, data_source):
        '''
        /data/<isid>/<projectid>/<dskeys>/<ids>
        
        A wildcard “*” may be specified to retrieve data for 
        all of the IDs from the project’s summary datasource.
        '''

        return self.get(self.url+'/data/*/')
    
    def get_structures(self, project):
        '''/structure/<isid>/<projectid>/<ids>'''
        return self.get(self.url+'/structure/*/%s%s'%(project, self.creds))

    def get_projects(self):
        '''/projects/'''
        return self.get(self.url+'/projects/*/%s%s'%(project, self.creds))

    def get_project(self, project):
        '''/projects/<projectid>'''
        return self.get(self.url+'/projects/*/%s%s'%(project, self.creds))
    
    def get_query(self, endpoint):
        '''/query/<isid>/<projectID>/<dsid>/<dskeys>/<operator>/<parameter>'''
        return 0