import time
from osv import fields, osv
import netsvc
import pooler
from datetime import datetime
from datetime import date
from osv.orm import browse_record, browse_null
from tools.translate import _

class closing_stock_detail_wizard(osv.osv_memory):
	_name = "closing.stock.detail.wizard"
	_description = "Closing Stock Details"
	
	_columns = {
	
				'fis_year': fields.many2one('account.fiscalyear','Fiscal year',readonly=True),
			#	'account_id': fields.many2one('account.account','Account Name',domain=[('type', '=', 'view')],required=True),
				'user_id': fields.many2one('res.users', 'User ID'),
				'location_id': fields.many2one('stock.location', 'Location',domain=[('location_type', '=', 'main')],required=True),
				'company_id': fields.many2one('res.company', 'Company Name',required=True),
				'from_date': fields.date('From Date'),
				'to_date': fields.date('Date'),
				'report_type': fields.selection([('all_product', 'All Product'),('product_wise','Product Wise')], "Report Type", required=True),
				'product_id': fields.many2one('product.product', 'Product'),
				'categ_id': fields.many2one('product.category', 'Category'),
				'type': fields.selection([('consu', 'Consumable Items'),('service','Service Items'),('cap','Capital Goods'),('assets','Assets')], 'Product Type'),
				'report_group': fields.selection([('abstract', 'Category Abstract'),('detail','Category Detail')], 'Report Group'),
       
				}
				
	
					
	
	def _get_from_date(self, cr, uid, context=None):
		today = date.today()
		fis_obj = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=',today),('date_stop','>=',today)])
		fis_id = self.pool.get('account.fiscalyear').browse(cr,uid,fis_obj[0])
		from_date = fis_id.date_start
		d2 = datetime.strptime(from_date,'%Y-%m-%d')
		res = d2.strftime('%Y-%m-%d')
		
		return res
		
	def onchange_product(self, cr, uid, ids, report_type):
		
		value = {'product':''}
		if report_type == 'all_product':
			value = {'product_id': False}
		return {'value': value}	
	
	def _get_fis(self, cr, uid, context=None):
		today = date.today()
		fis_obj = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start','<=',today),('date_stop','>=',today)])
		fis_id = self.pool.get('account.fiscalyear').browse(cr,uid,fis_obj[0])
		fisyear_id = fis_id.id
		return fisyear_id
		
	_defaults = {
	
				'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id,
				'company_id':1,
				'from_date': time.strftime('%Y-%m-%d'),
				'to_date': time.strftime('%Y-%m-%d'),
				'fis_year': _get_fis,
				
				}					

	def create_report(self, cr, uid, ids, context={}):
		data = self.read(cr,uid,ids,)[-1]
		if data['report_group']=='detail':
		
			return {
				'type'		 : 'ir.actions.report.xml',
				'report_name'   : 'jasper_closing_stock_detail_report',
				'datas': {
						'model':'closing.stock.detail.wizard',
						'id': context.get('active_ids') and context.get('active_ids')[0] or False,
						'ids': context.get('active_ids') and context.get('active_ids') or [],
						'report_type':'pdf',
						'form':data
					},
				'nodestroy': False
				}
		if data['report_group']=='abstract':
		
			return {
				'type'		 : 'ir.actions.report.xml',
				'report_name'   : 'jasper_closing_stock_abstract_report',
				'datas': {
						'model':'closing.stock.detail.wizard',
						'id': context.get('active_ids') and context.get('active_ids')[0] or False,
						'ids': context.get('active_ids') and context.get('active_ids') or [],
						'report_type':'pdf',
						'form':data
					},
				'nodestroy': False
				}
	
closing_stock_detail_wizard()

