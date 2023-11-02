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
                    print(date)
                elif 'REG_DATE' in dot_cmpd:
                    date = dot_cmpd['REG_DATE']
                    date = re.match(r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}:\d{2})', date)
                    day, month, year = date.group(1).split('/') 
                    date = f"{year}-{month}-{day}"
                    print('lets see:')
                    print(date)

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
                    co = CompoundObservation.register(compound = ld_cmpd,
                                                            assay = Assay.get(key='dotmatics_upgrade_source'),
                                                            endpoint = 'From Upgrade',
                                                            text_value = 'Upgrade In Progress',
                                                            )
                    ld_proj_pk = Project.get(key = i).id
                    CompoundObservationProject.register(compound_observation=co,
                                        project_id=ld_proj_pk)
                    CompoundProject.register(compound_id = ld_cmpd.id, project_id = ld_proj_pk)

def assay_map(results):
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
            CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key='ALL'))
        elif compound != False:
            print(result)
            '''
                co = CompoundObservation.register(compound = compound,
                                                            assay = assay,
                                                            endpoint = result['ANALYSIS_NAME'],
                                                            text_value = result['value_text'],
                                                            unit = unit,
                                                            value_operator = value_operator
                                                            )
               '''
        '''  # handle the project ACLs
                    if ',' in i['project']:
                        ps = i['project'].split(',')
                        for p in ps + SCINAMIC_PROJECTS_CONFIG['GLOBAL']:
                            CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key=p))
                    else:
                        CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key=i['project']))
                        for i in SCINAMIC_PROJECTS_CONFIG['GLOBAL']:
                            CompoundObservationProject.register(compound_observation=co,
                                        project=Project.get(key=i))
'''
        # now, there may be batch data that needs tweeking!!

