#!/usr/bin/python
#
# Copyright (c) 2013 Evgeny Gridasov (evgeny.gridasov@gmail.com)
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
import re
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
	"postgres",
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

RDS_MYSQL_STANDARD_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/mysql/pricing-standard-deployments.js"
RDS_POSTGRESQL_STANDARD_ON_DEMAND_URL="http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/postgresql/pricing-standard-deployments.js"
RDS_ORACLE_LICENSED_STANDARD_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-li-standard-deployments.js"
RDS_ORACLE_BYOL_STANDARD_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-byol-standard-deployments.js"
RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-ex-ondemand.js"
RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-web-ondemand.js"
RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-se-ondemand.js"
RDS_MSSQL_BYOL_STANDARD_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-byol-ondemand.js"
RDS_MYSQL_MULTIAZ_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/mysql/pricing-multiAZ-deployments.js"
RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL="http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/postgresql/pricing-multiAZ-deployments.js"
RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-li-multiAZ-deployments.js"
RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-byol-multiAZ-deployments.js"

RDS_MYSQL_RESERVED_LIGHT_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/mysql/pricing-light-utilization-reserved-instances.js"
RDS_MYSQL_RESERVED_MEDIUM_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/mysql/pricing-medium-utilization-reserved-instances.js"
RDS_MYSQL_RESERVED_HEAVY_URL= "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/mysql/pricing-heavy-utilization-reserved-instances.js"
RDS_POSTGRESQL_RESERVED_HEAVY_URL="http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/postgresql/pricing-heavy-utilization-reserved-instances.js"
RDS_ORACLE_LICENSE_RESERVED_LIGHT_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-li-light-utilization-reserved-instances.js"
RDS_ORACLE_LICENSE_RESERVED_MEDIUM_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-li-medium-utilization-reserved-instances.js"
RDS_ORACLE_LICENSE_RESERVED_HEAVY_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-li-heavy-utilization-reserved-instances.js"
RDS_ORACLE_BYOL_RESERVED_LIGHT_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-byol-light-utilization-reserved-instances.js"
RDS_ORACLE_BYOL_RESERVED_MEDIUM_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-byol-medium-utilization-reserved-instances.js"
RDS_ORACLE_BYOL_RESERVED_HEAVY_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/oracle/pricing-byol-heavy-utilization-reserved-instances.js"
RDS_SQLSERVER_BYOL_RESERVED_LIGHT_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-byol-light-ri.js"
RDS_SQLSERVER_BYOL_RESERVED_MEDIUM_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-byol-medium-ri.js"
RDS_SQLSERVER_BYOL_RESERVED_HEAVY_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-byol-heavy-ri.js"
RDS_SQLSERVER_EX_RESERVED_LIGHT_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-ex-light-ri.js"
RDS_SQLSERVER_EX_RESERVED_MEDIUM_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-ex-medium-ri.js"
RDS_SQLSERVER_EX_RESERVED_HEAVY_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-ex-heavy-ri.js"
RDS_SQLSERVER_WEB_RESERVED_LIGHT_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-web-light-ri.js"
RDS_SQLSERVER_WEB_RESERVED_MEDIUM_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-web-medium-ri.js"
RDS_SQLSERVER_WEB_RESERVED_HEAVY_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-web-heavy-ri.js"
RDS_SQLSERVER_SE_RESERVED_LIGHT_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-se-heavy-ri.js"
RDS_SQLSERVER_SE_RESERVED_MEDIUM_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-se-medium-ri.js"
RDS_SQLSERVER_SE_RESERVED_HEAVY_URL = "http://aws-assets-pricing-prod.s3.amazonaws.com/pricing/rds/sqlserver/sqlserver-li-se-light-ri.js"

RDS_MULTIAZ_TYPES = [
	"standard",
	"multiaz"
	]

RDS_MULTIAZ_MAPPING = {
	"stdDeployRes" : "standard",
	"multiAZdeployRes" : "multiaz"
}

RDS_ONDEMAND_STANDARD_TYPE_BY_URL = {
	RDS_MYSQL_STANDARD_ON_DEMAND_URL : ["gpl","mysql"],
	RDS_POSTGRESQL_STANDARD_ON_DEMAND_URL : ["postgresql","postgres"],
	RDS_ORACLE_LICENSED_STANDARD_ON_DEMAND_URL : ["included","oracle-se1"],
	RDS_ORACLE_BYOL_STANDARD_ON_DEMAND_URL : ["byol","oracle"],
	RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL : ["included","sqlserver-ex"],
	RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL : ["included","sqlserver-web"],
	RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL : ["included","sqlserver-se"],
	RDS_MSSQL_BYOL_STANDARD_ON_DEMAND_URL : ["byol","sqlserver"]	
}

RDS_ONDEMAND_MULTIAZ_TYPE_BY_URL = {
	RDS_MYSQL_MULTIAZ_ON_DEMAND_URL : ["gpl","mysql"],
	RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL : ["postgresql","postgres"],
	RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL: ["included","oracle-se1"],
	RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL : ["byol","oracle"]	
}

RDS_RESERVED_TYPE_BY_URL = {
	RDS_MYSQL_RESERVED_LIGHT_URL : ["gpl","mysql","light"],
	RDS_MYSQL_RESERVED_MEDIUM_URL : ["gpl","mysql","medium"],
	RDS_MYSQL_RESERVED_HEAVY_URL : ["gpl","mysql","heavy"],
	RDS_POSTGRESQL_RESERVED_HEAVY_URL : ["postgresql","postgres","heavy"],
	RDS_ORACLE_LICENSE_RESERVED_LIGHT_URL : ["included","oracle-se1","light"],
	RDS_ORACLE_LICENSE_RESERVED_MEDIUM_URL : ["included","oracle-se1","medium"],
	RDS_ORACLE_LICENSE_RESERVED_HEAVY_URL : ["included","oracle-se1","heavy"],
	RDS_ORACLE_BYOL_RESERVED_LIGHT_URL : ["byol","oracle","light"],
	RDS_ORACLE_BYOL_RESERVED_MEDIUM_URL : ["byol","oracle","medium"],
	RDS_ORACLE_BYOL_RESERVED_HEAVY_URL : ["byol","oracle","heavy"],
	RDS_SQLSERVER_BYOL_RESERVED_LIGHT_URL : ["byol","sqlserver","light"],
	RDS_SQLSERVER_BYOL_RESERVED_MEDIUM_URL : ["byol","sqlserver","medium"],
	RDS_SQLSERVER_BYOL_RESERVED_HEAVY_URL : ["byol","sqlserver","heavy"],
	RDS_SQLSERVER_EX_RESERVED_LIGHT_URL : ["included","sqlserver-ex","light"],
	RDS_SQLSERVER_EX_RESERVED_MEDIUM_URL : ["included","sqlserver-ex","medium"],
	RDS_SQLSERVER_EX_RESERVED_HEAVY_URL : ["included","sqlserver-ex","heavy"],
	RDS_SQLSERVER_WEB_RESERVED_LIGHT_URL : ["included","sqlserver-web","light"],
	RDS_SQLSERVER_WEB_RESERVED_MEDIUM_URL : ["included","sqlserver-web","medium"],
	RDS_SQLSERVER_WEB_RESERVED_HEAVY_URL : ["included","sqlserver-web","heavy"],
	RDS_SQLSERVER_SE_RESERVED_LIGHT_URL : ["included","sqlserver-se","light"],
	RDS_SQLSERVER_SE_RESERVED_MEDIUM_URL : ["included","sqlserver-se","medium"],
	RDS_SQLSERVER_SE_RESERVED_HEAVY_URL : ["included","sqlserver-se","heavy"]
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
	"clusterHiMemDB.xxxxxxxxl" : "db.cr1.8xlarge",
	
	# Multiaz instances
	"multiAZDBInstClass.uDBInst" : "db.t1.micro",
	"multiAZDBInstClass.smDBInst" : "db.m1.small",
	"multiAZDBInstClass.medDBInst" : "db.m1.medium",
	"multiAZDBInstClass.lgDBInst" : "db.m1.large",
	"multiAZDBInstClass.xlDBInst" : "db.m1.xlarge",
	"multiAZHiMemInstClass.xlDBInst" : "db.m2.xlarge",
	"multiAZHiMemInstClass.xxlDBInst" : "db.m2.2xlarge",
	"multiAZHiMemInstClass.xxxxDBInst" : "db.m2.4xlarge",
	"multiAZClusterHiMemDB.xxxxxxxxl" : "db.cr1.8xlarge",
	
	#Reserved
	"stdDeployRes.u" : "db.t1.micro",
	"stdDeployRes.micro" : "db.t1.micro",
	"stdDeployRes.sm" : "db.m1.small",
	"stdDeployRes.med" : "db.m1.medium",
	"stdDeployRes.lg" : "db.m1.large",
	"stdDeployRes.xl" : "db.m1.xlarge",
	"stdDeployRes.xlHiMem" : "db.m2.xlarge",
	"stdDeployRes.xxlHiMem" : "db.m2.2xlarge",
	"stdDeployRes.xxxxlHiMem" : "db.m2.4xlarge",
	"stdDeployRes.xxxxxxxxl" : "db.cr1.8xlarge",
	
	#Reserved multi az
	"multiAZdeployRes.u" : "db.t1.micro",
	"multiAZdeployRes.sm" : "db.m1.small",
	"multiAZdeployRes.med" : "db.m1.medium",
	"multiAZdeployRes.lg" : "db.m1.large",
	"multiAZdeployRes.xl" : "db.m1.xlarge",
	"multiAZdeployRes.xlHiMem" : "db.m2.xlarge",
	"multiAZdeployRes.xxlHiMem" : "db.m2.2xlarge",
	"multiAZdeployRes.xxxxlHiMem" : "db.m2.4xlarge",
	"multiAZdeployRes.xxxxxxxxl" : "db.cr1.8xlarge"

}


def _load_data(url):
	f = urllib2.urlopen(url).read()
	def callback(json):
		return json
	data = eval(f, {"__builtins__" : None}, {"callback" : callback} )
	return data


def get_rds_reserved_instances_prices(filter_region=None, filter_instance_type=None, filter_multiaz=None, filter_db=None):
	""" Get RDS reserved instances prices. Results can be filtered by region """

	get_specific_region = (filter_region is not None)
	get_specific_instance_type = (filter_instance_type is not None)
	get_specific_multiaz = (filter_multiaz is not None)
	get_specific_db = (filter_db is not None)

	currency = DEFAULT_CURRENCY

	urls = [
		RDS_MYSQL_RESERVED_LIGHT_URL,
		RDS_MYSQL_RESERVED_MEDIUM_URL,
		RDS_MYSQL_RESERVED_HEAVY_URL,
		RDS_POSTGRESQL_RESERVED_HEAVY_URL,
		RDS_ORACLE_LICENSE_RESERVED_LIGHT_URL,
		RDS_ORACLE_LICENSE_RESERVED_MEDIUM_URL,
		RDS_ORACLE_LICENSE_RESERVED_HEAVY_URL,
		RDS_ORACLE_BYOL_RESERVED_LIGHT_URL,
		RDS_ORACLE_BYOL_RESERVED_MEDIUM_URL,
		RDS_ORACLE_BYOL_RESERVED_HEAVY_URL,
		RDS_SQLSERVER_BYOL_RESERVED_LIGHT_URL,
		RDS_SQLSERVER_BYOL_RESERVED_MEDIUM_URL,
		RDS_SQLSERVER_BYOL_RESERVED_HEAVY_URL,
		RDS_SQLSERVER_EX_RESERVED_LIGHT_URL,
		RDS_SQLSERVER_EX_RESERVED_MEDIUM_URL,
		RDS_SQLSERVER_EX_RESERVED_HEAVY_URL,
		RDS_SQLSERVER_WEB_RESERVED_LIGHT_URL,
		RDS_SQLSERVER_WEB_RESERVED_MEDIUM_URL,
		RDS_SQLSERVER_WEB_RESERVED_HEAVY_URL,
		RDS_SQLSERVER_SE_RESERVED_LIGHT_URL,
		RDS_SQLSERVER_SE_RESERVED_MEDIUM_URL,
		RDS_SQLSERVER_SE_RESERVED_HEAVY_URL					
	]

	result_regions = []
	result_regions_index = {}
	result = {
		"config" : {
			"currency" : currency,
		},
		"regions" : result_regions
	}

	for u in urls:
		info = RDS_RESERVED_TYPE_BY_URL[u]
		license = info[0]
		db = info[1]
		utilization_type = info[2]
		
		if get_specific_db and db != filter_db:
			continue
		data = _load_data(u)
		if "config" in data and data["config"] and "regions" in data["config"] and data["config"]["regions"]:
			for r in data["config"]["regions"]:
				if "region" in r and r["region"]:
					region_name = JSON_NAME_TO_RDS_REGIONS_API[r["region"]]
					if get_specific_region and filter_region != region_name:
						continue
					if region_name in result_regions_index:
						instance_types = result_regions_index[region_name]["instanceTypes"]
					else:
						instance_types = []
						result_regions.append({
							"region" : region_name,
							"instanceTypes" : instance_types
						})
						result_regions_index[region_name] = result_regions[-1]
						
					if "instanceTypes" in r:
						for it in r["instanceTypes"]:
							multiaz = RDS_MULTIAZ_MAPPING[it["type"]]
							if get_specific_multiaz and multiaz != filter_multiaz:
								continue
							instance_class = it["type"]
							if "tiers" in it:
								for s in it["tiers"]:
									_type = INSTANCE_TYPE_MAPPING[instance_class + "." + s["size"] ]
	
									if get_specific_instance_type and _type != filter_instance_type:
										continue
									
									prices = {
										"1year" : {
											"hourly" : None,
											"upfront" : None
										},
										"3year" : {
											"hourly" : None,
											"upfront" : None
										}
									}
	
									instance_types.append({
										"type" : _type,
										"multiaz" : multiaz,
										"license" : license,
										"db" : db,
										"utilization" : utilization_type,
										"prices" : prices
									})
	
									for price_data in s["valueColumns"]:
										price = None
										try:
											price = float(re.sub("[^0-9\.]", "", price_data["prices"][currency]))
										except ValueError:
											price = None
	
										if price_data["name"] == "yrTerm1":
											prices["1year"]["upfront"] = price
										elif price_data["name"] == "yrTerm1Hourly":
											prices["1year"]["hourly"] = price
										elif price_data["name"] == "yearTerm1Hourly":
											prices["1year"]["hourly"] = price
										elif price_data["name"] == "yrTerm3":
											prices["3year"]["upfront"] = price
										elif price_data["name"] == "yrTerm3Hourly":
											prices["3year"]["hourly"] = price
										elif price_data["name"] == "yearTerm3Hourly":
											prices["3year"]["hourly"] = price			

	return result



def get_rds_ondemand_instances_prices(filter_region=None, filter_instance_type=None, filter_multiaz=None, filter_db=None):
	""" Get RDS on-demand instances prices. Results can be filtered by region """

	get_specific_region = (filter_region is not None)
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
	RDS_POSTGRESQL_STANDARD_ON_DEMAND_URL,
	RDS_ORACLE_LICENSED_STANDARD_ON_DEMAND_URL,
	RDS_ORACLE_BYOL_STANDARD_ON_DEMAND_URL,
	RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL,
	RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL,
	RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL,
	RDS_MSSQL_BYOL_STANDARD_ON_DEMAND_URL,
	RDS_MYSQL_MULTIAZ_ON_DEMAND_URL,
	RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL,
	RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL,
	RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL
	]

	for u in urls:
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
					region_name = JSON_NAME_TO_RDS_REGIONS_API[r["region"]]
					if get_specific_region and filter_region != region_name:
						continue	
					
					instance_types = []
					if "types" in r:
						for it in r["types"]:
							instance_class = it["name"]
							if "tiers" in it:
								for s in it["tiers"]:
									_type = INSTANCE_TYPE_MAPPING[instance_class + "." + s["name"] ]
	
									if get_specific_instance_type and _type != filter_instance_type:
										continue
									
									price = None
									try:
										price = float(re.sub("[^0-9\.]", "", s["prices"][currency]))
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
	parser.add_argument("--type", "-t", help="Show ondemand or reserved(may be slow) instances", choices=["ondemand", "reserved"], required=True)
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
		data = get_rds_reserved_instances_prices(args.filter_region, args.filter_type, args.filter_multiaz, args.filter_db)

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
		elif args.type == "reserved":
			try:
				x.set_field_names(["region", "type", "multiaz", "license", "db", "utilization", "term", "price", "upfront"])
			except AttributeError:
				x.field_names = ["region", "type", "multiaz", "license", "db", "utilization", "term", "price", "upfront"]

			try:
				x.aligns[-1] = "l"
				x.aligns[-2] = "l"
			except AttributeError:
				x.align["price"] = "l"
				x.align["upfront"] = "l"
			
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					for term in it["prices"]:
						x.add_row([region_name, it["type"],  it["multiaz"], it["license"], it["db"], it["utilization"], term, none_as_string(it["prices"][term]["hourly"]), none_as_string(it["prices"][term]["upfront"])])
		
		print x
	elif args.format == "csv":
		if args.type == "ondemand":
			print "region,type,multiaz,license,db,price"
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					print "%s,%s,%s,%s,%s,%s" % (region_name, it["type"], it["multiaz"], it["license"], it["db"], none_as_string(it["price"]))
		elif args.type == "reserved":
					print "region,type,multiaz,license,db,utilization,term,price,upfront"
					for r in data["regions"]:
						region_name = r["region"]
						for it in r["instanceTypes"]:
							for term in it["prices"]:
								print "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (region_name, it["type"], it["multiaz"], it["license"], it["db"], it["utilization"], term, none_as_string(it["prices"][term]["hourly"]), none_as_string(it["prices"][term]["upfront"]))
