// Copyright (c) 2023, Hardik Gadesha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Search and Update Orders', {
	onload: function(frm) {
		frm.set_value("customer", "");
		frm.set_value("order_type", "");
		frm.set_value("status", ""); 
		frm.set_value("from_date", "");
		frm.set_value("to_date", "");
		frm.set_value("import_file", "");
	},
	refresh: function(frm) {
		frm.add_custom_button(__("Order List"), function() {
			frappe.set_route("List", "Sales Order");
		});
		frm.disable_save();
		frm.page.set_primary_action(__('Process'), () => {
			if(frm.doc.import_file){
				process_import(frm);
			}
			else{
				frappe.throw(__('Please attach file to import'));
			}
		});
	},
	download_template(frm) {
		open_url_post(
			'/api/method/order_update.order_update.doctype.search_and_update_orders.search_and_update_orders.download_template',
			{
				company : frm.doc.company,
				customer : frm.doc.customer,
				order_type : frm.doc.order_type,
				status :frm.doc.status,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date
			}
		);
	}
});

function process_import(frm) {
	frm.page.page_actions.find(".primary-action").addClass("hide");
	frm.page.set_indicator(__('In Progress'), 'green');
		frappe.call({
			method: "process_data_excel",
			doc:frm.doc,
			freeze: true,
			freeze_message: __("Updating Data..."),
		callback: function(r) {
			frm.page.set_indicator(__('Records Updated'), 'green');
		}
	});
}