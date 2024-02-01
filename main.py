from api import *
from etl import *
from map import *
from dotmatics_utils import *

# add the argparse...
# most code here will move to etl.py soon, but this is for easy testing right now

# This session carries a token that will be used. We can then deactivate this token at the end of the etl run
dotmatics_session = Session(DOTMATICS_API_CONFIG['url'],DOTMATICS_API_CONFIG['user'],DOTMATICS_API_CONFIG['password'])
# doesnt need to be called again. Now all pewee SS calls go to the configured DB. We close it at the end.
simpleschema_session = SimpleSchema_Session(SIMPLE_SCHEMA_DB_CONFIG)
simpleschema_session.clear_all()
add_projects_to_ss()
# this will move to etl.py, but for quick testing we can put it here
compounds = Compound_Data(dotmatics_session, DOTMATICS_SOURCES)
# This cleaning step makes the information returned from Dotmatics much easier to work with (takes less than a second to run). Suggested for SA usage and required for this code base.
compounds.clean_data()
while 'status' not in compounds.compounds:
    # map the compounds into SS
    compound_map(compounds.compounds)
    compounds.cycle()
    try:
        compounds.clean_data()
    except:
        print(compounds.compounds)
# Do the same as above but for Results/Studies/Protocols/Assays** Whatever you wanna call them
results = Study_Data(dotmatics_session, DOTMATICS_SOURCES)
results.clean_data()
while 'status' not in results.study:
    # map the compounds into SS
    assay_map(results.data)
    results.cycle()
    try:
        results.clean_data()
    except:
        print(results.study)

print('Complete')
