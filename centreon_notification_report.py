#!/usr/bin/python3
#
# Copyright (c) 2017 Lydia Sevelt <LydiaSevelt@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

import pymysql
import getopt
import sys

DBPASSWD=""

def print_help():
	"""Print help"""
	print("-h = display help")
	print("-H = host report in csv format")
	print("-S = service report in csv format")
	print("no options = print out hosts and services in a human readable format")

# basic getopts
try:
	opts, args = getopt.getopt(sys.argv[1:], "hHS", [])
except getopt.GetoptError as err:
	print(err)
	print_help()
	sys.exit(1)

hosts_csv = False
services_csv = False
for option, arg in opts:
	if option == "-h":
		print_help()
		sys.exit()
	elif option == "-H":
		hosts_csv = True
	elif option == "-S":
		services_csv = True
	else:
		assert False, "unhandled option"

# query data
db = pymysql.connect(host='localhost', port=3306, user='centreon', passwd=DBPASSWD, db='centreon')
query = db.cursor()
# get all hosts with contacts, contact groups, templates, and inheritance
# +---------+----------------+--------------------+---------+------------------------------+-------------------------+-------------+---------------+
# | host_id | host_name      | contact_name       | cg_name | contact_additive_inheritance | cg_additive_inheritance | host_tpl_id | host_register |
# +---------+----------------+--------------------+---------+------------------------------+-------------------------+-------------+---------------+
# |      36 | Centreon-Sever | Lydia_Sevelt_Admin | NULL    |                            0 |                       0 |          81 | 1             |
# +---------+----------------+--------------------+---------+------------------------------+-------------------------+-------------+---------------+
query.execute("select h.host_id, h.host_name, con.contact_name, cong.cg_name, contact_additive_inheritance, cg_additive_inheritance, htr.host_tpl_id, h.host_register from host h left join host_template_relation htr on htr.host_host_id = h.host_id left join contact_host_relation ctr ON htr.host_host_id = ctr.host_host_id left join contact con on ctr.contact_id = con.contact_id left join contactgroup_host_relation ctr2 ON htr.host_host_id = ctr2.host_host_id left join contactgroup cong on contactgroup_cg_id = cong.cg_id where h.host_register = '1'")
hosts = {}
for row in query:
	if not row[0] in hosts:
		hosts[row[0]] = [ (row[1], row[2], row[3], row[4], row[5], row[6], row[7] ) ]
	else:
		hosts[row[0]].append( (row[1], row[2], row[3], row[4], row[5], row[6], row[7] ) )

# get all hosts templates with contacts, contact groups, templates, and inheritance
# +---------+--------------+--------------+---------+------------------------------+-------------------------+-------------+---------------+
# | host_id | host_name    | contact_name | cg_name | contact_additive_inheritance | cg_additive_inheritance | host_tpl_id | host_register |
# +---------+--------------+--------------+---------+------------------------------+-------------------------+-------------+---------------+
# |       2 | generic-host | NULL         | NULL    |                            0 |                       0 |        NULL | 0             |
# +---------+--------------+--------------+---------+------------------------------+-------------------------+-------------+---------------+
query.execute("select h.host_id, h.host_name, con.contact_name, cong.cg_name, contact_additive_inheritance, cg_additive_inheritance, htr.host_tpl_id, h.host_register from host h left join host_template_relation htr on htr.host_host_id = h.host_id left join contact_host_relation ctr ON htr.host_host_id = ctr.host_host_id left join contact con on ctr.contact_id = con.contact_id left join contactgroup_host_relation ctr2 ON htr.host_host_id = ctr2.host_host_id left join contactgroup cong on contactgroup_cg_id = cong.cg_id where h.host_register = '0'")
hosts_templates = {}
for row in query:
	if not row[0] in hosts_templates:
		hosts_templates[row[0]] = [ (row[1], row[2], row[3], row[4], row[5], row[6], row[7] ) ]
	else:
		hosts_templates[row[0]].append( (row[1], row[2], row[3], row[4], row[5], row[6], row[7] ) )


# All services with contacts, contact groups, templates, and inheritance
# +---------+----------------+---------------------+------------+-------------------------------+------------------------------+-------------------------+--------------+---------+------------------+---------------+
# | host_id | host_name      | service_description | service_id | service_template_model_stm_id | contact_additive_inheritance | cg_additive_inheritance | contact_name | cg_name | service_register | host_register |
# +---------+----------------+---------------------+------------+-------------------------------+------------------------------+-------------------------+--------------+---------+------------------+---------------+
# |      36 | Centreon-Sever | Disk /              |         28 |                             5 |                            0 |                       0 | NULL         | NULL    | 1                | 1             |
# +---------+----------------+---------------------+------------+-------------------------------+------------------------------+-------------------------+--------------+---------+------------------+---------------+
query.execute("select h.host_id, h.host_name, s.service_description, s.service_id, s.service_template_model_stm_id, s.contact_additive_inheritance, s.cg_additive_inheritance, c.contact_name, cong.cg_name, s.service_register, h.host_register from host h left join host_service_relation hsr on hsr.host_host_id = h.host_id left join service s on hsr.service_service_id = s.service_id left join contact_service_relation csr on csr.service_service_id = s.service_id left join contact c on c.contact_id = csr.contact_id left join contactgroup_service_relation cgsr on cgsr.service_service_id = s.service_id left join contactgroup cong on cgsr.contactgroup_cg_id = cong.cg_id where h.host_register = '1'")
services = {}
for row in query:
	if not row[0] in services:
		services[row[0]] = [ (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]) ]
	else:
		services[row[0]].append( (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]) )

# all service templates with contacts, contact groups, templates, and inheritance
# +------------+---------------------+-------------------------------+------------------------------+-------------------------+--------------+-------------+------------------+
# | service_id | service_description | service_template_model_stm_id | contact_additive_inheritance | cg_additive_inheritance | contact_name | cg_name     | service_register |
# +------------+---------------------+-------------------------------+------------------------------+-------------------------+--------------+-------------+------------------+
# |          1 | generic-service     |                          NULL |                            0 |                       1 | NULL         | Supervisors | 0                |
# +------------+---------------------+-------------------------------+------------------------------+-------------------------+--------------+-------------+------------------+
query.execute("select s.service_id, s.service_description, s.service_template_model_stm_id, s.contact_additive_inheritance, s.cg_additive_inheritance, c.contact_name, cong.cg_name, s.service_register from service s left join contact_service_relation csr on csr.service_service_id = s.service_id left join contact c on c.contact_id = csr.contact_id left join contactgroup_service_relation cgsr on cgsr.service_service_id = s.service_id left join contactgroup cong on cgsr.contactgroup_cg_id = cong.cg_id where s.service_register = '0'")
services_templates = {}
for row in query:
	if not row[0] in services_templates:
		services_templates[row[0]] = [ (row[1], row[2], row[3], row[4], row[5], row[6], row[7]) ]
	else:
		services_templates[row[0]].append( (row[1], row[2], row[3], row[4], row[5], row[6], row[7]) )


def host_template_check(contact_inherit, cg_inherit, host_tpl_id):
	"""Return contacts from template if inheritence"""
	contacts = []
	contact_groups = []
	# ignore inheritance for now
	c_inhert = hosts_templates[host_tpl_id][0][3]
	cg_inhert = hosts_templates[host_tpl_id][0][4]
	template = hosts_templates[host_tpl_id][0][5]
	for line in hosts_templates[host_tpl_id]:
		contacts.append(line[1])
		contact_groups.append(line[2])
	return(c_inhert, cg_inhert, template, set(contacts), set(contact_groups))

def service_template_check(contact_inherit, cg_inherit, service_tpl_id):
	"""Return contacts from template if inheritence"""
	contacts = []
	contact_groups = []
	# ignore inheritance for now
	c_inhert = services_templates[service_tpl_id][0][2]
	cg_inhert = services_templates[service_tpl_id][0][3]
	template = services_templates[service_tpl_id][0][1]
	for line in services_templates[service_tpl_id]:
		contacts.append(line[4])
		contact_groups.append(line[5])
	return(c_inhert, cg_inhert, template, set(contacts), set(contact_groups))



for host in hosts:
	contacts = []
	contact_groups = []
	h_name = hosts[host][0][0]
	c_inhert = hosts[host][0][3]
	cg_inhert = hosts[host][0][4]
	template = hosts[host][0][5]
	for entry in hosts[host]:
		contacts.append(entry[1])
		contact_groups.append(entry[2])
	while True:
		if not template:
			# no template
			break
		c_inhert, cg_inhert, template, t_contacts, t_contact_groups = host_template_check(c_inhert, cg_inhert, template)
		for i in t_contacts:
			contacts.append(i)
		for i in t_contact_groups:
			contact_groups.append(i)
		
	if hosts_csv:
		spacer_string = "   "
	else:
		spacer_string = " "
	c_string = ""
	cg_string = ""
	for i in set(contacts):
		if i:
			c_string = c_string + i + spacer_string
	for i in set(contact_groups):
		if i:
			cg_string = cg_string + i + spacer_string
	if hosts_csv:
		print(h_name + "," + c_string + "," + cg_string)
		continue
	elif services_csv:
		pass
	else:
		print(h_name + " - contacts: " + c_string + " - contact groups: " + cg_string)

	h_services = {}
	for entry in services[host]:
		if not entry[2] in h_services:
			h_services[entry[2]] = [ (entry[1], entry[6], entry[7], entry[3], entry[4], entry[5]) ]
		else:
			h_services[entry[2]].append( (entry[1], entry[6], entry[7], entry[3], entry[4], entry[5]) )

	for entry in h_services:
		contacts = []
		contact_groups = []
		s_name = h_services[entry][0][0]
		c_inhert = h_services[entry][0][4]
		cg_inhert = h_services[entry][0][5]
		template = h_services[entry][0][3]
		for line in h_services[entry]:
			contacts.append(line[1])
			contact_groups.append(line[2])
		while True:
			if not template:
				# no template
				break
			c_inhert, cg_inhert, template, t_contacts, t_contact_groups = service_template_check(c_inhert, cg_inhert, template)
			for i in t_contacts:
				contacts.append(i)
			for i in t_contact_groups:
				contact_groups.append(i)
		if services_csv:
			spacer_string = "   "
		else:
			spacer_string = " "
		c_string = ""
		cg_string = ""
		for i in set(contacts):
			if i:
				c_string = c_string + i + spacer_string
		for i in set(contact_groups):
			if i:
				cg_string = cg_string + i + spacer_string
		if h_services[entry][0][0]:
			if services_csv:
				print(h_name + "," + h_services[entry][0][0] + "," + c_string + "," + cg_string)
			else:
				print("        " + h_services[entry][0][0] + " - contacts: " + c_string + " - contact groups: " + cg_string)
	print(" ")

