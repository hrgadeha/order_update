// Copyright (c) 2023, Hardik Gadesha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Search and Update Orders', {
	onload: function(frm) {
		frm.set_value("company", "");
		frm.set_value("customer", "");
		frm.set_value("order_type", "");
		frm.set_value("status", ""); 
		frm.set_value("from_date", "");
		frm.set_value("to_date", "");
		frm.set_value("import_file", "");
		frm.clear_table('searched_order_list');
		frm.refresh_field('searched_order_list');
	},
	refresh: function(frm) {
		if (frm.$wrapper.find(".layout-side-section").css("display") == "block") {
			frm.$wrapper.find(".layout-side-section").css("display", "none");
		}
		frm.fields_dict['searched_order_list'].grid.wrapper.find('.grid-add-row').hide();
		frm.get_field('searched_order_list').grid.df.cannot_delete_rows = true;
		frm.get_field('searched_order_list').grid.df.cannot_add_rows = true;

		frm.add_custom_button(__("Order List"), function() {
			frappe.set_route("List", "Sales Order");
		});
		frm.disable_save();
		frm.page.set_primary_action(__('Process'), () => {
			if(frm.doc.searched_order_list && frm.doc.searched_order_list.length > 0){
				process_update(frm);
			}
		});
	},
	company: function(frm) {
		set_orders_list(frm);
	},
	customer: function(frm) {
		set_orders_list(frm);
	},
	order_type: function(frm) {
		set_orders_list(frm);
	},
	status: function(frm) {
		set_orders_list(frm);
	},
	from_date: function(frm) {
		set_orders_list(frm);
	},
	to_date: function(frm) {
		set_orders_list(frm);
	},
	download_template(frm) {
		open_url_post(
			'/api/method/order_update.order_update.doctype.search_and_update_orders.search_and_update_orders.download_template',
			{}
		);
	},
	after_save: function(frm) {
		if(frm.doc.import_file){
			set_excel_records(frm);
		}
	}
});

function set_orders_list(frm) {
	if(!frm.doc.import_file){
		frm.clear_table('searched_order_list');
		frm.refresh_field('searched_order_list');
		frappe.call({
			method: "get_order_data",
			doc:frm.doc,
			freeze: true,
			freeze_message: __("Fetching Data..."),
			callback: function(r) {
				$.each(r.message, function(index, row){
					let d = frm.add_child('searched_order_list');
						d.order_no = row.name;
						d.date = row.transaction_date;
						d.status = row.status;
						d.shipping_status = row.shipping_status;
						d.tracking_number = row.tracking_number;
					frm.refresh_field('searched_order_list');
				});
			}
		});
	}
}

function set_excel_records(frm) {
	frm.clear_table('searched_order_list');
	frm.refresh_field('searched_order_list');
	frappe.call({
		method: "get_excel_record",
		doc:frm.doc,
		freeze: true,
		freeze_message: __("Updating Data..."),
	callback: function(r) {
		$.each(r.message, function(index, row){
			let d = frm.add_child('searched_order_list');
				d.order_no = row.order_no;
				d.date = row.date;
				d.status = row.status;
				d.shipping_status = row.shipping_status;
				d.tracking_number = row.tracking_number;
			frm.refresh_field('searched_order_list');
		});
	}
});
}

function process_update(frm) {
	frappe.call({
		method: "process_update",
		doc:frm.doc,
		freeze: true,
		freeze_message: __("Updating Data..."),
	callback: function(r) {
		if(r.message == true){
			frappe.show_alert('Records Updated')
			frm.reload_doc();
		}
	}
});
}