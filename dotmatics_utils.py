from config import *
from api import *
from simpleschema.models import Project, Experiment

def add_projects_to_ss():
    # customer_key = scinamic_project_pk, 
    # key = ld_project_name

    SimpleSchema_Session(SIMPLE_SCHEMA_DB_CONFIG)
    for k,v in DOTMATICS_PROJECTS_CONFIG.items():
        if str(k) != 'GLOBAL':
            try:
                mp = Project.get(key = v[0]).execute()
            except:
                try:
                    Project.register(customer_key = k, key = v[0])
                except:
                    print("error creating projects")
        else:
            i = 1
            for j in v:
                 try:
                     mp = Project.get(key = j).execute()
                 except:
                     try:
                        Project.register(customer_key = i, key = j)
                     except:
                         print("error creating projects")
                 i+=1
