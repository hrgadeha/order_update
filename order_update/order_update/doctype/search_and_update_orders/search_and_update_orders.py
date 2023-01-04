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

class SearchandUpdateOrders(Document):
	@frappe.whitelist()
	def process_data_excel(self):
		data = read_xlsx_file_from_attached_file(self.import_file)
		if not len(data[1:]):
			frappe.throw(_("Excel Sheet must contains records to update"))

		else:
			frappe.enqueue(update_searched_orders,timeout=6000,is_async=True,now=True,doc=self, data=data)

def update_searched_orders(doc, data, publish_progress =True):
	fields = ["Sales Order","Shipping Status","Tracking Number"]

	if data[0] != fields:
		frappe.throw(_("Column in Excel Sheet are not matched with default column"))

	rownum = 0
	for f in data[1:]:
		rownum +=1
		if frappe.db.exists("Sales Order", str(f[0])) and (f[1] or f[2]):
			frappe.db.set_value('Sales Order', f[0], 'shipping_status', f[1])
			frappe.db.set_value('Sales Order', f[0], 'tracking_number', f[2])

@frappe.whitelist()
def download_template(company = None, customer = None,order_type = None,status = None,from_date = None,to_date = None):
	data = frappe._dict(frappe.local.form_dict)
	writer = get_template(company = None, customer = customer,order_type = order_type,status = status,from_date = from_date,to_date=to_date)
	build_response_as_excel(writer)

def get_template(company,customer,order_type,status,from_date,to_date):
	import json
	fields = []

	fields = ["Sales Order","Shipping Status","Tracking Number"]
	writer = UnicodeWriter()
	writer.writerow(fields)
	writer = get_sample_template(writer=writer,company = None,customer = customer,order_type = order_type,status = status,from_date = from_date,to_date=to_date)

	return writer

def get_sample_template(writer,company,customer,order_type,status,from_date,to_date):
	row = []

	filters = []
	if company :
		filters.append(['company', '=', company])
	if customer :
		filters.append(['customer', '=', customer])
	if order_type :
		filters.append(['order_type', '=', order_type])
	if status :
		filters.append(['status', '=', status])
	if from_date :
		filters.append(['transaction_date', '>=', from_date])
	if to_date :
		filters.append(['transaction_date', '<=', to_date])

	sales_order_records = frappe.db.get_list('Sales Order',filters=filters , fields = ['name','shipping_status','tracking_number'])
	for so in sales_order_records:
		row = [so.name,so.shipping_status,so.tracking_number]
		writer.writerow(row)
	return writer	

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