# dotmatics
Dotmatics ETL

Using the barebones api wrappers:

```python
from dotmatics_api_wrappers import *
# create a dotmatics session (will create a token and not use user or pw again)
s = Session('https://customer-url.com','user','password')
# get info from a datasource - 1000 result max (this is a default datasource)
s.get_datasource(3000,504)
# you can also use paramiters
# ex. is offset the start of the source (pagination)
s.get_datasource(3000,504,'&offset=1000')
# list projects
s.get_projects()
```
using the higher level api.py script:

```python
from api import *
from config import DOTMATICS_SOURCES

# filter=True will try and only get info from the LiveDesign specific projects and datasources. False gets all.
Basic_Project_Info(s, filter = False)
# first 1k records for compound datasources (use cycle function for next batch)
Compound_Data(s, DOTMATICS_SOURCES)
# first 1k records for study datasources
Study_Data(s, DOTMATICS_SOURCES)
```
DOTMATICS_SOURCES should look like the following, but fill in the inforation specific to your customer's dotmatics datasources. See confluence for more information:

```python
DOTMATICS_SOURCES = {
    # This requires set up of projects and datasources (sql calls) by the customer on the dotmatics side. We then just specify the datasources and projects here.

    'compounds': {'projectName':'LIVEDESIGN_REG_INT','projectID':2800,
                  'summary_datasource':{'name':'EXO_REG_DATA_SUMMARY','dsID':821},
                  'audit_datasource':{'name':'EXO_REG_DATA_AUDIT','dsID':822},
                  'compound_datasource':{'name':'EXO_COMPOUND_PROPERTIES','dsID':823},
                  'batch_datasource':{'name':'EXO_BATCH_PROPERTIES','dsID':824},
                  'reagent_datasource':{'name':'EXO_REAGENT_PROPERTIES','dsID':825},
                  },
    'studies':{'projectName':'LIVEDESIGN_STUDIES_INT', 'projectID':2900,
                'summary_datasource':{'name':'EXO_STUDIES_SUMMARY','dsID':826},
                'audit_datasource':{'name':'EXO_STUDIES_AUDIT','dsID':827},
                'study_datasource':{'name':'STUDIES_ALL_DATA_VW','dsID':839}
              }
}
```
