from api import *
from simpleschema.models import *
from simpleschema.schemas import SimpleSchema
from rdkit import Chem
import re

def compound_map(dotmatics_compounds):
    '''
    Take in a list of dictionaries of compounds and add them to SimpleSchema
    This will be looped in batches of 1K which is the max number of compounds the API allows.
    The process is relatively quick, future improvements for speed would be adding to SS in bulk instead of individual calls.

    1K compounds loaded into SS in x seconds (this time includes the API call, data processing, and putting into SS)
    '''

    for dot_cmpd in dotmatics_compounds:
        # update if it exists
        try:
            ld_cmpd = Compound.get(corporate_id=dot_cmpd['compoundID'])
            ld_cmpd.canonical_smiles = dot_cmpd['SMILES']
            ld_cmpd.mol_file = dot_cmpd['MOLFILE']
            ld_cmpd.created_at = dot_cmpd['DATE_CREATED']
            ld_cmpd.person = dot_cmpd['USER_NAME']
            ld_cmpd.save()
        except:
            # create new compounds if none found above
            try:
                if 'DATE_CREATED' in dot_cmpd:
                    date = dot_cmpd['DATE_CREATED']
                elif 'REG_DATE' in dot_cmpd:
                    date = dot_cmpd['REG_DATE']
                    date = re.match(r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}:\d{2})', date)
                    day, month, year = date.group(1).split('/') 
                    date = f"{year}-{month}-{day}"
                Compound.register(
                            corporate_id = dot_cmpd['compoundID'],
                            # customer_key=dot_cmpd['pk'],
                            canonical_smiles = dot_cmpd['SMILES'],
                            mol_file = dot_cmpd['MOLFILE'],
                            created_at = date,
                            person = dot_cmpd['USER_NAME'],
                            # Add Source?
                            )
                ld_cmpd = Compound.get(corporate_id=dot_cmpd['compoundID'])
                go = True
            except Exception as error:
                #print(error)
                #print('error processing:\n'+str(dot_cmpd)+'\n')
                go = False

        if 'PROJECT_NAME' in dot_cmpd and go == True:

            '''
            This if statement is where we ensure there is a project to be put into.
            It also has the go == True statment because we want to ensure that the compound (ld_cmpd) was created and loaded apporpriately.
            '''

            dot_cmpd['PROJECT_NAME'] =[i.strip() for i in dot_cmpd['PROJECT_NAME'].split(',')]
            for p in dot_cmpd['PROJECT_NAME']:
                '''
                This is where we use the rest of the DOTMATICS_PROJECTS_CONFIG dictionary from config.py to give compound permissions.
                We get the SimpleSchema project PK (ss_proj_pk) from the project name (p). These projects are added to SS in a seperate function.
                In order to keep things clean, we are explicit about which projects to bring in. See config.py
                '''
                # check if project in DOTMATICS_PROJECTS_CONFIG
                if p in DOTMATICS_PROJECTS_CONFIG:
                    ss_proj_pk = Project.get(key = p).id
                    CompoundProject.register(compound_id = ld_cmpd.id, project_id = ss_proj_pk)
            '''
            Here we add compounds to 'GLOBAL' projects or projects that are in the config.py DOTMATICS_PROJECTS_CONFIG['GLOBAL'] list.
            You may add any project that all compounds go to to that list and all compounds will get permissions in that project.
            '''
            if DOTMATICS_PROJECTS_CONFIG['GLOBAL']:
                for i in DOTMATICS_PROJECTS_CONFIG['GLOBAL']:
                    ss_proj_pk = Project.get(key = i).id
                   # CompoundObservationProject.register(compound_observation=co,
                    #                    project_id=ld_proj_pk)
                    CompoundProject.register(compound_id = ld_cmpd.id, project_id = ss_proj_pk)
        # Add batch logic here...

def assay_map(results):
    '''
    Map Assay data (results from Studies) back to compounds. There is no project Level info here. I am looking for a workaround.

    This function takes in a list of dictionary objects. This list is created using the Study_Data() class found in api.py
    Once you have recieved the data from dotmatics we use a function built into  Study_Data called clean_data() which provides
    a nice flat list of dicts to use in this process. The raw retrun from dotmatics is a little hard to use and this makes it easier to read and debug.

    Attributes
    ----------
    results : list
        A list of dictionaries to itterate through and load into simple schema.
    '''
    s = Session(DOTMATICS_API_CONFIG['url'],DOTMATICS_API_CONFIG['user'],DOTMATICS_API_CONFIG['password'])
    projects = [project.key for project in Project.select()]
    for result in results:
        try:
            compound = Compound.get(corporate_id=re.sub(REGEX_COMPOUND_ASSAY, '', result['ID']))
        except Exception as e:
            #print(e)
            compound = False
        # see if assay e.g. result['PROTOCOL_NAME'] exists and if pivot conditions are present
        if result["PROTOCOL_NAME"] in PIVOT_CONDITIONS:
            assay_key = result["PROTOCOL_NAME"]
            for piv in PIVOT_CONDITIONS[result["PROTOCOL_NAME"]]:
                assay_key += "%s%s"%(PIVOT_DELIMITER,result[piv])
        else:
            assay_key = result["PROTOCOL_NAME"]
        try:
            # Check to see if Assay in SS and get the assay object
            assay = Assay.get(key=assay_key)
        except:
            # If not register it then retrieve it as an object
            Assay.register(key=assay_key)
            assay = Assay.get(key=assay_key)
        # handle value operator...needs to be parsed out of RESULT_ALPHA
        if 'RESULT_ALPHA' in result:
            value_operator = result['RESULT_ALPHA'][0]
        else:
            value_operator = ''
        if 'CONC_UNITS' in result:
            conc = result['CONC_UNITS']
        else:
            conc = ''
        # handle the timepoint unit
        #if 'timepoint_unit' in result:
        #    unit = result['timepoint_unit']
        #else:
        #   unit = ''

        if 'RESULT_NUMERIC' in result and compound != False:
            # Register the compound observation
            co = CompoundObservation.register(compound = compound,
                                                            assay = assay,
                                                            endpoint = result['ANALYSIS_NAME'],
                                                            num_value = result['RESULT_NUMERIC'],
                                                            unit = conc,
                                                            value_operator = value_operator
                                                            )
            # Add the observation to global projects (can have many)
            for i in DOTMATICS_PROJECTS_CONFIG['GLOBAL']:
                CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key='ALL'))
            '''
            Currently the assay data view does not contain project level information, however the workaround is that you can only see assay data for a compound
            if that compound is permissioned in the project. Therfore, we can make all assay results permissioned for all projects.
            Note: this is not the most time or memory efficient way to do things. We will improve this system by adding a project field to the all data view (datasource) on the dotmatics side
            '''
            for project in projects:
                CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key=project))
        elif compound != False:
            x = 0 # place holder action until logging set up

