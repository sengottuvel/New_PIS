from kg_purchase_order import JasperDataParser
from jasper_reports import jasper_report
import pooler
from datetime import date
from datetime import datetime
from datetime import timedelta
import base64
import netsvc
from osv import osv, fields
from tools.translate import _
from osv.orm import browse_record, browse_null
import os
import re
from HTMLParser import HTMLParser

class kg_stock_ledger_report(JasperDataParser.JasperDataParser):
	def __init__(self, cr, uid, ids, data, context):
		super(kg_stock_ledger_report, self).__init__(cr, uid, ids, data, context)

	def generate_data_source(self, cr, uid, ids, data, context):
		return 'records'

	def generate_ids(self, cr, uid, ids, data, context):
		return {}

	def generate_properties(self, cr, uid, ids, data, context):
		return {}
		
	def generate_parameters(self, cr, uid, ids, data, context):
		val={}
	
		user_obj = self.pool.get('res.users').search(self.cr, self.uid, [('id','=',uid)])
		user_id = self.pool.get('res.users').browse(self.cr,self.uid,user_obj[0])
		user_rec = user_id.login
		
		val['from_date']=''
		val['to_date']=''
		val['t_date']=''
		val['account_id']=0
		val['company_name']=1
		val['company_add']=''
		frm_rec = data['form']['from_date']
		print "------------------------------------>",frm_rec
		user_name = user_rec
		current_time = datetime.now()
		ist_time = current_time + timedelta(minutes = 330)
		crt_time = ist_time.strftime('%d/%m/%Y %H:%M:%S')	
		t_rec = data['form']['to_date']
		to_date =  t_rec.encode('utf-8')
		from_date =  frm_rec.encode('utf-8')
		t_d1 = datetime.strptime(to_date,'%Y-%m-%d')
		t_d2 = datetime.strftime(t_d1, '%Y-%m-%d')
		t_d5 = datetime.strftime(t_d1, '%d/%m/%Y')
		t_d3 = datetime.strptime(from_date,'%Y-%m-%d')
		t_d4 = datetime.strftime(t_d3, '%Y-%m-%d')
		t_d6 = datetime.strftime(t_d3, '%d/%m/%Y')
		
		print "------------------------------------>",t_d2
		print "------------------------------------>",type(t_d2)
		
		
		location_id = data['form']['location_id']
		location_id = location_id[0]

		report_type = data['form']['report_type']
		report_type = report_type.encode('utf-8')
		if report_type == 'all_product':
			report_type_name = 'All Product'
		else:
			report_type_name = 'Product Wise'	
		
		

		company_id = data['form']['company_id']
		company_rec = self.pool.get('res.company').browse(self.cr,self.uid,company_id[0])
		company_name = company_rec.name
		
		
	#	account_rec = data['form']['account_id']
		
		val['m_from_date'] = t_d4
		val['m_to_date'] = t_d2
		val['p_from_date'] = t_d6
		val['p_to_date'] = t_d5
		val['account_id'] = 2
		val['user_name'] = user_name
		val['user_id'] = uid
		val['current_time'] = crt_time
		val['t_date'] = t_d2
		val['company_name'] = company_name
		
		val['location_id'] = location_id
	
		val['report_type'] = report_type
		val['report_type_name'] = report_type_name
		
		
		if data['form']['product_id']:
			product_id = data['form']['product_id']
			product_id = product_id[0]
			val['product_id'] = product_id
			
		if data['form']['type']:
			type1 = data['form']['type']
			type1 = type1.encode('utf-8')
			
			val['type'] = type1	
			
			
		if data['form']['categ_id']:
			categ_id = data['form']['categ_id']
			categ_id = categ_id[0]
			val['categ_id'] = categ_id	
			print "-------------------------categ_id----------------",categ_id
		print "vals ------",val
		return val


	def generate_records(self, cr, uid, ids, data, context):
		pool= pooler.get_pool(cr.dbname)
		return {}

jasper_report.report_jasper('report.jasper_kg_stock_ledger_report', 'res.users', parser=kg_stock_ledger_report)
