rdsinstancespricing.py
======================

Written by Evgeny Gridasov     

http://itoc.com.au

http://cloudedify.com


rdsinstancespricing.py is a quick & dirty library and a command line interface (CLI)
to get a list of all Amazon Web Services RDS ondemand and reserved instances pricing.

The data is based on a set of JSON files used in the RDS page (http://aws.amazon.com/rds).

Data can be filtered by region, RDS instance type, multiaz/standard deployments and DB engine type.

Running this file will activate its CLI interface in which you can get output to your console in a CSV, JSON and table formats (default is table).

To run the command line interface, you need to install:
argparse - if you are running Python < 2.7
prettytable - to get a nice table output to your console

Both of these libraries can be installed using the 'pip install' command.

Original idea by Eran Sandler https://github.com/erans/ec2instancespricing
