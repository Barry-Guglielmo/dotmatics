from config import *
from dotmatics_api_wrappers import *


class Basic_Project_Info():
    def __init__(self, session, filter = True, config_projects=['LIVEDESIGN_REG_INT','LIVEDESIGN_STUDIES_INT']):
        '''
        This will make it easier to look through different projects information
        list(.project_names)

        .datasource_names['<project>'] # example: LIVEDESIGN_REG_INT, LIVEDESIGN_STUDIES_INT

        if filter = True then only config_projects info will be displayed
        '''

        self.session = session
        self.config_projects = config_projects

        info = {}
        names = {}
        datasources = {}
        datasource_names = {}

        for i in session.get_projects():
            pi = session.get_project(i)

            if filter == True and pi['projectName'] in config_projects:
                info[i] = pi
                names[pi['projectName']] = i
                datasources[pi['projectName']] = pi['dataSources']
                datasource_names[pi['projectName']] = [[k['name'],k['dsID']] for j,k in datasources[pi['projectName']].items()]
            elif filter ==False:
                info[i] = pi
                names[pi['projectName']] = i
                datasources[pi['projectName']] = pi['dataSources']
                datasource_names[pi['projectName']] = [[k['name'],k['dsID']] for j,k in datasources[pi['projectName']].items()]

        self.project_info = info
        self.project_names = names
        self.datasources = datasources
        self.datasource_names = datasource_names

class Compound_Data():
    def __init__(self, session, dotmatics_sources, offset=0):
        self.session = session
        self.offset = offset
        self.config = dotmatics_sources['compounds']
        self.summary = session.get_datasource(self.config['projectID'], self.config['summary_datasource']['dsID'])
        self.audit = session.get_datasource(self.config['projectID'], self.config['audit_datasource']['dsID'])
        self.compound = session.get_datasource(self.config['projectID'], self.config['compound_datasource']['dsID'])
        self.batch = session.get_datasource(self.config['projectID'], self.config['batch_datasource']['dsID'])
        self.reagent = session.get_datasource(self.config['projectID'], self.config['reagent_datasource']['dsID'])
    def cycle(self):
        self.offset += 1000
        self.summary = session.get_datasource(self.config['projectID'], self.config['summary_datasource']['dsID'],params='&offset=%i'%self.offset)
        self.audit = session.get_datasource(self.config['projectID'], self.config['audit_datasource']['dsID'],params='&offset=%i'%self.offset)
        self.compound = session.get_datasource(self.config['projectID'], self.config['compound_datasource']['dsID'],params='&offset=%i'%self.offset)
        self.batch = session.get_datasource(self.config['projectID'], self.config['batch_datasource']['dsID'],params='&offset=%i'%self.offset)
        self.reagent = session.get_datasource(self.config['projectID'], self.config['reagent_datasource']['dsID'],params='&offset=%i'%self.offset)

s = Session(CDD_API_CONFIG['url'],CDD_API_CONFIG['user'],CDD_API_CONFIG['password'])
# d = Compound_Data(s, DOTMATICS_SOURCES)
