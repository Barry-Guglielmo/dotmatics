from config import *
from dotmatics_api_wrappers import *
from simpleschema.schemas import SimpleSchema

def SimpleSchema_Session(SIMPLE_SCHEMA_DB_CONFIG):
    '''Just a Wrapper to Make it easy to look at in the main.py'''
    return SimpleSchema(SIMPLE_SCHEMA_DB_CONFIG["database"],
                        user=SIMPLE_SCHEMA_DB_CONFIG["user"],
                        password=SIMPLE_SCHEMA_DB_CONFIG["password"],
                        port=SIMPLE_SCHEMA_DB_CONFIG["port"],
                        host=SIMPLE_SCHEMA_DB_CONFIG["host"])

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
        self.compounds = session.get_datasource(self.config['projectID'], self.config['compound_datasource']['dsID'])
        self.batch = session.get_datasource(self.config['projectID'], self.config['batch_datasource']['dsID'])
        self.reagent = session.get_datasource(self.config['projectID'], self.config['reagent_datasource']['dsID'])
    def cycle(self, datasource = 'compounds'):
        self.offset += 1000
        if datasource == 'compounds':
            self.compounds = self.session.get_datasource(self.config['projectID'], self.config['compound_datasource']['dsID'],params='&offset=%i'%self.offset)
    def clean_data(self):
        # study, dictionary
        lst = []
        for k,v in self.compounds.items():
            # dataSource, dictionary
            for i,j in v['dataSources'].items():
                # flatten the data structure and make it easy to use
                # assumes only one compound information returned per ID
                cmpd = j[next(iter(j))]
                cmpd['compoundID']=k
                cmpd['dataSource']=i
                lst.append(cmpd)
        self.compounds = lst

class Study_Data():
    def __init__(self, session, dotmatics_sources, offset=0):
        self.session = session
        self.offset = offset
        self.config = dotmatics_sources['studies']
        #self.summary = session.get_datasource(self.config['projectID'], self.config['summary_datasource']['dsID'])
        #self.audit = session.get_datasource(self.config['projectID'], self.config['audit_datasource']['dsID'])
        self.study = session.get_datasource(self.config['projectID'], self.config['study_datasource']['dsID'])
        self.protocols = {}

    def cycle(self):
        self.offset += 1000
        #self.summary = session.get_datasource(self.config['projectID'], self.config['summary_datasource']['dsID'],params='&offset=%i'%self.offset)
        #self.audit = session.get_datasource(self.config['projectID'], self.config['audit_datasource']['dsID'],params='&offset=%i'%self.offset)
        self.study = session.get_datasource(self.config['projectID'], self.config['study_datasource']['dsID'],params='&offset=%i'%self.offset)

    def clean_data(self):
        # study, dictionary
        lst = []
        for k,v in self.study.items():
            # dataSource, dictionary
            for i,j in v['dataSources'].items():
                # flatten the data structure and make it easy to use
                # results is a dictionary of someID and a dictionary
                # still not sure how to relate the outcome with the sample
#                lst.append({'studyID':k, 'dataSource':i, 'results':j})
                for o,p in j.items():
                    r = p
                    r['studyID'] =k
                    r['dataSource']=i
                    # check for protocol (this is only because allProtocols endpoint not permissioned)
                    if r['PROTOCOL_ID'] in self.protocols:
                        r['PROTOCOL_NAME']=self.protocols[r['PROTOCOL_ID']]
                    else:
                        try:
                            r['PROTOCOL_NAME']=self.session.get_protocol(r['PROTOCOL_ID'])['name']
                            self.protocols[r['PROTOCOL_ID']] = r['PROTOCOL_NAME']
                        except:
                            self.protocols[r['PROTOCOL_ID']] = 'N/A'
                            print('Could Not Find: '+r['PROTOCOL_ID'])
                            r['PROTOCOL_NAME'] = 'N/A'
                    lst.append(r)
        self.data = lst
        # self.study['141892']['dataSources']['939']['4953']['ANALYSIS_NAME']

# s = Session(DOTMATICS_API_CONFIG['url'],DOTMATICS_API_CONFIG['user'],DOTMATICS_API_CONFIG['password'])
# d = Compound_Data(s, DOTMATICS_SOURCES)
