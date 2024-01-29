#!/bin/bash
echo "start"
sudo su -c '
echo $(date) &>>/vol/bluebird/seurat/pro_serv/dotmatics_integration/chef/scinamic.log
source /vol/bluebird/seurat/pro_serv/dotmatics_integration/venv/bin/activate
echo "source"
echo "python start" &>>/vol/bluebird/seurat/pro_serv/livedesign-integrations/scinamic/chef/scinamic.log
python /vol/bluebird/seurat/pro_serv/livedesign-integrations/scinamic/main.py -d -f
echo "python"
echo "python finish" &>>/vol/bluebird/seurat/pro_serv/livedesign-integrations/scinamic/chef/scinamic.log
deactivate
echo "di stage start" &>>/vol/bluebird/seurat/pro_serv/livedesign-integrations/scinamic/chef/scinamic.log
di_admin staging -s /vol/bluebird/seurat/LiveDesign/DataIntegrator/scinamic_di_settings_di_formatted.json
echo "di stage finish"
echo "di main start"
di_main -s /vol/bluebird/seurat/LiveDesign/DataIntegrator/scinamic_di_settings_di_formatted.json
echo "di main finish"
echo $(date) &>>/vol/bluebird/seurat/pro_serv/livedesign-integrations/scinamic/chef/scinamic.log
'
