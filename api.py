from config import *
from dotmatics_api_wrappers import *


class Basic_Project_Info():
    def __init__(self, session, filter = False, config_projects=['LIVEDESIGN_REG_INT','LIVEDESIGN_STUDIES_INT']):
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
