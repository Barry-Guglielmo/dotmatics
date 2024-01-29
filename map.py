from api import *
from simpleschema.models import *
from simpleschema.schemas import SimpleSchema
from rdkit import Chem
import re

def compound_map(dotmatics_compounds):
    ''' Take in a list of dictionaries of compounds and add them to SimpleSchema'''

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
            # create new ones if needed
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
                            )
                ld_cmpd = Compound.get(corporate_id=dot_cmpd['compoundID'])
                go = True
            except Exception as error:
                print(error)
                print('error processing:\n'+str(dot_cmpd)+'\n')
                go = False

        if 'PROJECT_NAME' in dot_cmpd and go == True:
            dot_cmpd['PROJECT_NAME'] =[i.strip() for i in dot_cmpd['PROJECT_NAME'].split(',')]
            for p in dot_cmpd['PROJECT_NAME']:
                #print(dot_cmpd['PROJECT_NAME'])
                #print(dot_cmpd['compoundID'])
                x = 0
            if DOTMATICS_PROJECTS_CONFIG['GLOBAL']:
                for i in DOTMATICS_PROJECTS_CONFIG['GLOBAL']:
                    ld_proj_pk = Project.get(key = i).id
                    CompoundObservationProject.register(compound_observation=co,
                                        project_id=ld_proj_pk)
                    CompoundProject.register(compound_id = ld_cmpd.id, project_id = ld_proj_pk)

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
    projects = list(Project_Info(s).pk_and_name.values())

    for result in results:
        try:
            compound = Compound.get(corporate_id=re.sub(REGEX_COMPOUND_ASSAY, '', result['ID']))
        except Exception as e:
            print(e)
            compound = False
        # see if assay dot['ANALYSIS_NAME'] exists or if pivot conditions are present
        if result["PROTOCOL_NAME"] in PIVOT_CONDITIONS:
            assay_key = result["PROTOCOL_NAME"]
            for piv in PIVOT_CONDITIONS[result["PROTOCOL_NAME"]]:
                assay_key += "%s%s"%(PIVOT_DELIMITER,result[piv])
        else:
            assay_key = result["PROTOCOL_NAME"]
        try:
            assay = Assay.get(key=assay_key)
        except:
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
         #   unit = result['timepoint_unit']
        #else:
         #   unit = ''

        if 'RESULT_NUMERIC' in result and compound != False:
            co = CompoundObservation.register(compound = compound,
                                                            assay = assay,
                                                            endpoint = result['ANALYSIS_NAME'],
                                                            num_value = result['RESULT_NUMERIC'],
                                                            unit = conc,
                                                            value_operator = value_operator
                                                            )
            # key for the project?? Add it here and also register to ALL or Global (put that in the config)
            CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key='ALL'))
#            for i in projects:
 #               try:
  #                  CompoundObservationProject.register(compound_observation=co,
   #                                     project=Project.get(key=i))
    #            except:
     #               x = 0 # place holder. Probably dont want to just make a project on the fly seeing as there are lots of tests
#                    Project.register(customer_key = i, key = i)
#                    CompoundObservationProject.register(compound_observation=co,
#                                        project=Project.get(key=i))
#            CompoundObservationProject.register(compound_observation=co,
#                                        project=Project.get(key=result['studyID']))
        elif compound != False:
            # need to set this logging a little differently, it will be if there is no compound or result (mostly invalidated results or High/Low standards)
            x = 0 # place holder action until logging set up

