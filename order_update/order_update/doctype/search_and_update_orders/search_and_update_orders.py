# Copyright (c) 2023, Hardik Gadesha and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import msgprint , _
from frappe.utils import cint, flt, nowdate, add_days, getdate, fmt_money, add_to_date, DATE_FORMAT, date_diff, cstr, get_datetime_str, formatdate
from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file, read_xls_file_from_attached_file
from frappe.utils.csvutils import UnicodeWriter
import frappe, csv, os
from datetime import date
from datetime import datetime
import base64
from six import string_types
import json

STATUS_COLOR = {
		"Draft": "red",
		"On Hold": "blue",
		"To Bill": "orange",
		"To Deliver and Bill": "green",
		"To Deliver": "orange",
		"Cancelled": "red",
		"Completed": "green",
		"Closed": "blue"
		}

class SearchandUpdateOrders(Document):
	@frappe.whitelist()
	def get_excel_record(self):
		data = read_xlsx_file_from_attached_file(self.import_file)
		if not len(data[1:]):
			frappe.throw(_("Excel Sheet must contains records to update"))

		else:
			order_data = []
			for f in data[1:]:
				if f[0] and frappe.db.exists("Sales Order", str(f[0])):
					so_status = frappe.db.get_value('Sales Order', f[0], 'status')
					return_data = {}
					return_data['order_no'] = f[0]
					return_data['date'] = frappe.db.get_value('Sales Order', f[0], 'transaction_date')
					return_data['status'] = "<span class=\"indicator-pill whitespace-nowrap {color}\"> <span>{status}</span></span>".format(
					color = STATUS_COLOR[so_status],status = so_status) 
					return_data['shipping_status'] = frappe.db.get_value('Sales Order', f[0], 'shipping_status')
					return_data['tracking_number'] = frappe.db.get_value('Sales Order', f[0], 'tracking_number')
					order_data.append(return_data)
		
			return order_data

	@frappe.whitelist()
	def get_order_data(self):
		filters = []
		if self.company :
			filters.append(['company', '=', self.company])
		if self.customer :
			filters.append(['customer', '=', self.customer])
		if self.order_type :
			filters.append(['order_type', '=', self.order_type])
		if self.status :
			filters.append(['status', '=', self.status])
		if self.from_date :
			filters.append(['transaction_date', '>=', self.from_date])
		if self.to_date :
			filters.append(['transaction_date', '<=', self.to_date])

		sales_order_records = frappe.db.get_list('Sales Order',filters=filters , 
		fields = ['name','transaction_date','status','shipping_status','tracking_number'])
		return sales_order_records if filters else []

	@frappe.whitelist()
	def process_update(self):
		data = read_xlsx_file_from_attached_file(self.import_file)
		fields = ["Sales Order"]
		if data[0] != fields:
			frappe.throw(_("Column in Excel Sheet are not matched with default column"))

		for f in self.searched_order_list:
			if frappe.db.exists("Sales Order", f.order_no):
				frappe.db.set_value('Sales Order', f.order_no, 'shipping_status', f.shipping_status)
				frappe.db.set_value('Sales Order', f.order_no, 'tracking_number', f.tracking_number)

		return True

# Privously Used Code

# def update_searched_orders(doc, data, publish_progress =True):
# 	order_data = []

# 	for f in data[1:]:
# 		if f[0] and frappe.db.exists("Sales Order", str(f[0])):
# 			return_data = {}
# 			return_data['order_no'] = f[0]
# 			return_data['date'] = frappe.db.get_value('Sales Order', f[0], 'transaction_date')
# 			return_data['status'] = frappe.db.get_value('Sales Order', f[0], 'status')
# 			return_data['shipping_status'] = frappe.db.get_value('Sales Order', f[0], 'shipping_status')
# 			return_data['tracking_number'] = frappe.db.get_value('Sales Order', f[0], 'tracking_number')
# 			order_data.append(return_data)
		
# 	return order_data

@frappe.whitelist()
def download_template():
	data = frappe._dict(frappe.local.form_dict)
	writer = get_template()
	build_response_as_excel(writer)

def get_template():
	import json
	fields = []

	fields = ["Sales Order"]
	writer = UnicodeWriter()
	writer.writerow(fields)
	# writer = get_sample_template(writer=writer,company = None,customer = customer,order_type = order_type,status = status,from_date = from_date,to_date=to_date)

	return writer

# def get_sample_template(writer,company,customer,order_type,status,from_date,to_date):
# 	row = []

# 	filters = []
# 	if company :
# 		filters.append(['company', '=', company])
# 	if customer :
# 		filters.append(['customer', '=', customer])
# 	if order_type :
# 		filters.append(['order_type', '=', order_type])
# 	if status :
# 		filters.append(['status', '=', status])
# 	if from_date :
# 		filters.append(['transaction_date', '>=', from_date])
# 	if to_date :
# 		filters.append(['transaction_date', '<=', to_date])

# 	sales_order_records = frappe.db.get_list('Sales Order',filters=filters , fields = ['name','shipping_status','tracking_number'])
# 	for so in sales_order_records:
# 		row = [so.name,so.shipping_status,so.tracking_number]
# 		writer.writerow(row)
# 	return writer	

def build_response_as_excel(writer):
	filename = frappe.generate_hash("", 10)
	with open(filename, 'wb') as f:
		f.write(cstr(writer.getvalue()).encode('utf-8'))
	f = open(filename)
	reader = csv.reader(f)

	from frappe.utils.xlsxutils import make_xlsx
	xlsx_file = make_xlsx(reader, "Orders to be Updated")

	f.close()
	os.remove(filename)

	# write out response as a xlsx type
	frappe.response['filename'] = 'searched_orders_list.xlsx'
	frappe.response['filecontent'] = xlsx_file.getvalue()
	frappe.response['type'] = 'binary'