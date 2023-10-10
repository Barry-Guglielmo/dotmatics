from config import *
from dotmatics_api_wrappers import *

def basic_project_info(session, name_only=True):
    if name_only == False:
        d = {}
        for i in session.get_projects():
            d[i] = s.get_project(i)
        return d
    else:
        d = {}
        for i in session.get_projects():
            try:
                d[session.get_project(i)['projectName']] = i
            except:
                print(i)
        return d
