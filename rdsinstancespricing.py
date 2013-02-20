#!/usr/bin/python
#
# Copyright (c) 2013 Evgeny Gridasov (evgeny.gridasov@gmail.com)
# Copyright (c) 2013 ITOC Australia  http://itoc.com.au
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import urllib2
import argparse
try:
	import simplejson as json
except ImportError:
	import json

RDS_REGIONS = [
	"us-east-1",
	"us-west-1",
	"us-west-2",
	"eu-west-1",
	"ap-southeast-1",
	"ap-southeast-2",
	"ap-northeast-1",
	"sa-east-1"
]

RDS_INSTANCE_TYPES = [
	"db.t1.micro",
	"db.m1.small",
	"db.m1.medium",
	"db.m1.large",
	"db.m1.xlarge",
	"db.m2.xlarge",
	"db.m2.2xlarge",
	"db.m2.4xlarge"
]

RDS_ENGINE_TYPES = [
	"mysql",
	"oracle-se1",
	"oracle",
	"sqlserver-ex",
	"sqlserver-web",
	"sqlserver-se",
	"sqlserver"
]

JSON_NAME_TO_RDS_REGIONS_API = {
	"us-east" : "us-east-1",
	"us-east-1" : "us-east-1",
	"us-west" : "us-west-1",
	"us-west-1" : "us-west-1",
	"us-west-2" : "us-west-2",
	"eu-ireland" : "eu-west-1",
	"eu-west-1" : "eu-west-1",
	"apac-sin" : "ap-southeast-1",
	"ap-southeast-1" : "ap-southeast-1",
	"ap-southeast-2" : "ap-southeast-2",
	"apac-syd" : "ap-southeast-2",
	"apac-tokyo" : "ap-northeast-1",
	"ap-northeast-1" : "ap-northeast-1",
	"sa-east-1" : "sa-east-1"
}

RDS_REGIONS_API_TO_JSON_NAME = {
	"us-east-1" : "us-east",
	"us-west-1" : "us-west",
	"us-west-2" : "us-west-2",
	"eu-west-1" : "eu-ireland",
	"ap-southeast-1" : "apac-sin",
	"ap-southeast-2" : "apac-syd",
	"ap-northeast-1" : "apac-tokyo",
	"sa-east-1" : "sa-east-1"	
}

RDS_MYSQL_STANDARD_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/mysql/pricing-standard-deployments.json"
RDS_ORACLE_LICENSED_STANDARD_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/oracle/pricing-li-standard-deployments.json"
RDS_ORACLE_BYOL_STANDARD_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/oracle/pricing-byol-standard-deployments.json"
RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/sqlserver/sqlserver-li-ex-ondemand.json"
RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/sqlserver/sqlserver-li-web-ondemand.json"
RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/sqlserver/sqlserver-li-se-ondemand.json"
RDS_MSSQL_BYOL_STANDARD_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/sqlserver/sqlserver-byol-ondemand.json"
RDS_MYSQL_MULTIAZ_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/mysql/pricing-multiAZ-deployments.json"
RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/oracle/pricing-li-multiAZ-deployments.json"
RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL = "http://aws.amazon.com/rds/pricing/oracle/pricing-byol-multiAZ-deployments.json"

RDS_MULTIAZ_TYPES = [
	"standard",
	"multiaz"
	]

RDS_ONDEMAND_STANDARD_TYPE_BY_URL = {
	RDS_MYSQL_STANDARD_ON_DEMAND_URL : ["gpl","mysql"],
	RDS_ORACLE_LICENSED_STANDARD_ON_DEMAND_URL : ["included","oracle-se1"],
	RDS_ORACLE_BYOL_STANDARD_ON_DEMAND_URL : ["byol","oracle"],
	RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL : ["included","sqlserver-ex"],
	RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL : ["included","sqlserver-web"],
	RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL : ["included","sqlserver-se"],
	RDS_MSSQL_BYOL_STANDARD_ON_DEMAND_URL : ["byol","sqlserver"]	
}

RDS_ONDEMAND_MULTIAZ_TYPE_BY_URL = {
	RDS_MYSQL_MULTIAZ_ON_DEMAND_URL : ["gpl","mysql"],
	RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL: ["included","oracle-se1"],
	RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL : ["byol","oracle"]	
}

DEFAULT_CURRENCY = "USD"

INSTANCE_TYPE_MAPPING = {
	"udbInstClass.uDBInst" : "db.t1.micro",
	"dbInstClass.uDBInst" : "db.t1.micro",
	"dbInstClass.smDBInst" : "db.m1.small",
	"dbInstClass.medDBInst" : "db.m1.medium",
	"dbInstClass.lgDBInst" : "db.m1.large",
	"dbInstClass.xlDBInst" : "db.m1.xlarge",
	"hiMemDBInstClass.xlDBInst" : "db.m2.xlarge",
	"hiMemDBInstClass.xxlDBInst" : "db.m2.2xlarge",
	"hiMemDBInstClass.xxxxDBInst" : "db.m2.4xlarge",
	
	"multiAZDBInstClass.uDBInst" : "db.t1.micro",
	"multiAZDBInstClass.smDBInst" : "db.m1.small",
	"multiAZDBInstClass.medDBInst" : "db.m1.medium",
	"multiAZDBInstClass.lgDBInst" : "db.m1.large",
	"multiAZDBInstClass.xlDBInst" : "db.m1.xlarge",
	"multiAZHiMemInstClass.xlDBInst" : "db.m2.xlarge",
	"multiAZHiMemInstClass.xxlDBInst" : "db.m2.2xlarge",
	"multiAZHiMemInstClass.xxxxDBInst" : "db.m2.4xlarge"	
}


def _load_data(url):
	f = urllib2.urlopen(url)
	return json.loads(f.read())

def get_rds_ondemand_instances_prices(filter_region=None, filter_instance_type=None, filter_multiaz=None, filter_db=None):
	""" Get RDS on-demand instances prices. Results can be filtered by region """

	get_specific_region = (filter_region is not None)
	if get_specific_region:
		filter_region = RDS_REGIONS_API_TO_JSON_NAME[filter_region]

	get_specific_instance_type = (filter_instance_type is not None)
	get_specific_multiaz = (filter_multiaz is not None)
	get_specific_db = (filter_db is not None)

	currency = DEFAULT_CURRENCY

	result_regions = []
	result = {
		"config" : {
			"currency" : currency,
			"unit" : "perhr"
		},
		"regions" : result_regions
	}
	
	urls = [
	RDS_MYSQL_STANDARD_ON_DEMAND_URL,
	RDS_ORACLE_LICENSED_STANDARD_ON_DEMAND_URL,
	RDS_ORACLE_BYOL_STANDARD_ON_DEMAND_URL,
	RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL,
	RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL,
	RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL,
	RDS_MSSQL_BYOL_STANDARD_ON_DEMAND_URL,
	RDS_MYSQL_MULTIAZ_ON_DEMAND_URL,
	RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL,
	RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL				
	]

	for u in urls:
		print u
		if u in RDS_ONDEMAND_STANDARD_TYPE_BY_URL:
			licensedb = RDS_ONDEMAND_STANDARD_TYPE_BY_URL[u]
			multiaz = "standard";
		else:
			licensedb = RDS_ONDEMAND_MULTIAZ_TYPE_BY_URL[u];
			multiaz = "multiaz";
		if get_specific_multiaz and multiaz != filter_multiaz:
			continue
		if get_specific_db and licensedb[1] != filter_db:
			continue
		data = _load_data(u)
		if "config" in data and data["config"] and "regions" in data["config"] and data["config"]["regions"]:
			for r in data["config"]["regions"]:
				if "region" in r and r["region"]:
					if get_specific_region and filter_region != r["region"]:
						continue
	
					region_name = JSON_NAME_TO_RDS_REGIONS_API[r["region"]]
					instance_types = []
					if "types" in r:
						for it in r["types"]:
							instance_name = it["name"]
							if "tiers" in it:
								for s in it["tiers"]:
									_type = INSTANCE_TYPE_MAPPING[instance_name + "." + s["name"] ]
	
									if get_specific_instance_type and _type != filter_instance_type:
										continue
									
									price = None
									try:
										price = float(s["prices"][currency])
									except ValueError:
										price = None
									
									instance_types.append({
										"type" : _type,
										"multiaz" : multiaz,
										"license" : licensedb[0],
										"db" : licensedb[1], 
										"price" : price
									})
	
						result_regions.append({
							"region" : region_name,
							"instanceTypes" : instance_types
						})
	return result

if __name__ == "__main__":
	def none_as_string(v):
		if not v:
			return ""
		else:
			return v

	try:
		import argparse 
	except ImportError:
		print "ERROR: You are running Python < 2.7. Please use pip to install argparse:   pip install argparse"


	parser = argparse.ArgumentParser(add_help=True, description="Print out the current prices of RDS instances")
	parser.add_argument("--type", "-t", help="Show ondemand or reserved instances", choices=["ondemand", "reserved"], required=True)
	parser.add_argument("--filter-region", "-fr", help="Filter results to a specific region", choices=RDS_REGIONS, default=None)
	parser.add_argument("--filter-type", "-ft", help="Filter results to a specific instance type", choices=RDS_INSTANCE_TYPES, default=None)
	parser.add_argument("--filter-multiaz", "-fz", help="Filter results to a specific db license", choices=RDS_MULTIAZ_TYPES, default=None)
	parser.add_argument("--filter-db", "-fd", help="Filter results to a specific db type", choices=RDS_ENGINE_TYPES, default=None)
	parser.add_argument("--format", "-f", choices=["json", "table", "csv"], help="Output format", default="table")

	args = parser.parse_args()

	if args.format == "table":
		try:
			from prettytable import PrettyTable
		except ImportError:
			print "ERROR: Please install 'prettytable' using pip:    pip install prettytable"

	data = None
	if args.type == "ondemand":
		data = get_rds_ondemand_instances_prices(args.filter_region, args.filter_type, args.filter_multiaz, args.filter_db)
	elif args.type == "reserved":
		print "reserved instances are not supported"
		exit()

	if data == None:
		print "filter produced no results"
		exit()
		
	if args.format == "json":
		print json.dumps(data)
	elif args.format == "table":
		x = PrettyTable()

		if args.type == "ondemand":
			try:			
				x.set_field_names(["region", "type", "multiaz", "license", "db", "price"])
			except AttributeError:
				x.field_names = ["region", "type", "multiaz", "license", "db", "price"]

			try:
				x.aligns[-1] = "l"
			except AttributeError:
				x.align["price"] = "l"

			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					x.add_row([region_name, it["type"], it["multiaz"], it["license"], it["db"], none_as_string(it["price"])])
		
		print x
	elif args.format == "csv":
		if args.type == "ondemand":
			print "region,type,multiaz,license,db,price"
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					print "%s,%s,%s,%s,%s,%s" % (region_name, it["type"], it["multiaz"], it["license"], it["db"], none_as_string(it["price"]))
		