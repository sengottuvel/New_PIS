import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import datetime
import calendar
from datetime import date
import re
import urllib
import urllib2
import logging
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import calendar
today = datetime.now()
a = datetime.now()
dt_time = a.strftime('%m/%d/%Y %H:%M:%S')

class kg_direct_expense_entry(osv.osv):
	
	_name = 'direct.entry.expense'
	_description = "This form is to add the direct expense"
	_order = "expense_date desc"
	
	
	def _amount_line_tax(self, cr, uid, line, context=None):
		val = 0.0
		amt_to_per = (line.dis_amt / (1 * line.total_amt or 1.0 )) * 100
		print "---------------------------------",line.header_id.supplier_id
		for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id,
			line.total_amt * (1-(amt_to_per or 0.0)/100.0), 1, 4099,
			 line.header_id.supplier_id)['taxes']:			 
			val += c.get('amount', 0.0)
		return val
	
	
	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		cur_obj=self.pool.get('res.currency')
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
				'discount' : 0.0,
				'other_charge': 0.0,
			}
			val = val1 = val3 = line_total = 0.0
			for line in order.line_ids:
				per_to_amt = line.total_amt
				tot_discount = line.dis_amt
				
				line_total += line.total_amt 
				val += self._amount_line_tax(cr, uid, line, context=context)
				val3 += tot_discount	
			res[order.id]['amount_tax']=(round(val,0))
			res[order.id]['amount_untaxed']=(round(line_total,0))
			res[order.id]['discount']=(round(val3,0))   
			res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] - res[order.id]['discount']
		return res
	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('direct.entry.expense.line').browse(cr, uid, ids, context=context):
			result[line.header_id.id] = True
		return result.keys()
	
	_columns = {
	
		'name':fields.char('Entry No'),
		'invoice_no':fields.char('Supplier Invoice No'),
		'expense_date':fields.date('Expense Date'),
		'invoice_date':fields.date('Supplier Invoice Date'),
		'supplier_id':fields.many2one('res.partner','Supplier'),
		'project_id':fields.many2one('kg.project.master','Project Name'),
		'Supplier_add':fields.text('Supplier Address'),
		'state': fields.selection([('draft','Draft'),('confirm','Waiting for approval'),('approved','Approved'),('reject','Rejected')],'Status', readonly=True),
		'active':fields.boolean('Active'),'user_id': fields.many2one('res.users', 'Created By', readonly=True),
		'currency_id': fields.many2one('res.currency', 'Currency', readonly=True),
		'line_ids':fields.one2many('direct.entry.expense.line','header_id','Line Entry'),	
		'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Taxes',
			store={
				'direct.entry.expense': (lambda self, cr, uid, ids, c={}: ids, ['line_ids'], 10),
				'direct.entry.expense.line': (_get_order, ['total_amt', 'tax_id', 'dis_amt',1], 10),
			}, multi="sums", help="The tax amount"),
		'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
			store=True,multi="sums",help="The total amount"),
		'discount': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total Discount(-)',
			store={
				'direct.entry.expense': (lambda self, cr, uid, ids, c={}: ids, ['line_ids'], 10),
				'direct.entry.expense.line': (_get_order, ['total_amt', 'tax_id', 'dis_amt',1], 10),
			}, multi="sums", help="The amount without tax", track_visibility='always'),
			
		'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
			store={
				'direct.entry.expense': (lambda self, cr, uid, ids, c={}: ids, ['line_ids'], 10),
				'direct.entry.expense.line': (_get_order, ['total_amt', 'tax_id', 'dis_amt',1], 10),
			}, multi="sums", help="The amount without tax", track_visibility='always'),
		'remark':fields.text('Remarks'),
			
			
			### Entry Info ###
		'crt_date': fields.datetime('Creation Date',readonly=True),
		'user_id': fields.many2one('res.users', 'Created By', readonly=True),
		'confirm_date': fields.datetime('Confirmed Date', readonly=True),
		'confirm_user_id': fields.many2one('res.users', 'Confirmed By', readonly=True),
		'approve_date': fields.datetime('Approved Date', readonly=True),
		'app_user_id': fields.many2one('res.users', 'Approved By', readonly=True),	
		'reject_date': fields.datetime('Rejected Date', readonly=True),
		'rej_user_id': fields.many2one('res.users', 'Rejected By', readonly=True),
		'payment_type': fields.selection([('cash', 'Cash'), ('credit', 'Credit')], 'Payment Type'),
			
	
	}
	
	_defaults = {
	
		'active': True,
		'state': 'draft',
		'payment_type': 'credit',
		'user_id': lambda obj, cr, uid, context: uid,
		'crt_date':fields.datetime.now,
	}
	
	_sql_constraints = [
		('invoice_no', 'unique(invoice_no)', 'Invoice No must be unique !!'),
		 ]
	
	def entry_draft(self,cr,uid,ids,context=None):
		self.write(cr, uid, ids, {'state': 'draft'})
		return True

	def entry_confirm(self,cr,uid,ids,context=None):
		self.write(cr, uid, ids, {'state': 'confirm','confirm_user_id': uid, 'confirm_date': dt_time,'name':self.pool.get('ir.sequence').get(cr, uid,'direct.entry.expense')})
		return True

	def entry_approve(self,cr,uid,ids,context=None):
		obj = self.browse(cr, uid, ids[0])
		if obj.confirm_user_id.id == uid:
			raise osv.except_osv(
                    _('Warning'),
                    _('Approve cannot be done by Confirmed user'))
		self.write(cr, uid, ids, {'state': 'approved','app_user_id': uid, 'approve_date': dt_time})
		return True

	def entry_reject(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		if rec.remark:
			self.write(cr, uid, ids, {'state': 'reject','rej_user_id': uid, 'reject_date': dt_time})
		else:
			raise osv.except_osv(_('Rejection remark is must !!'),
				_('Enter the remarks in rejection remark field !!'))
		return True
		
		
	def onchange_supplier(self,cr,uid,ids,supplier_id):
		val = []
		sup_add = self.pool.get('res.partner').browse(cr,uid,supplier_id)
		tot_add = (sup_add.street or '')+ ',' + (sup_add.street2 or '') + ','+(sup_add.city.name or '')+ ',' +(sup_add.state_id.name or '') + '-' +(sup_add.zip or '') + 'Ph:' + (sup_add.phone or '')+ ',' +(sup_add.mobile or '')		
		
		return {'value': {'Supplier_add': tot_add}}
		return True
		
		
		
	def check_date(self,cr,uid,ids,context=None):
		read_date = self.read(cr,uid,ids,['invoice_date','expense_date'],context=context)
		for t in read_date:
			if t['invoice_date']>t['expense_date']:
				return False
			else:
				return True
		return True	
		
	def _check_lineitem(self, cr, uid, ids, context=None):
		print "called liteitem ___ function"
		indent = self.browse(cr,uid,ids[0])
		if not indent.line_ids:
			return False
												
		return True
		
	def unlink(self,cr,uid,ids,context=None):
		if context is None:
			context={}
		indent = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for t in indent:
			if t['state'] in ('draft'):
				unlink_ids.append(t['id'])
			else:
				raise osv.except_osv(('Invalid action !'),('System not allow to delete a UN-DRAFT state !!'))
		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return True
	
	_constraints = [(check_date,'The invoice date should not be greater the expense date',['']),
					(_check_lineitem,'Please enter the Expense Details',['']),
					]
	
	

kg_direct_expense_entry()



class ch_direct_expense_entry(osv.osv):
	_name='direct.entry.expense.line'
	_description='This is used to add notes about the company and some remarks'
	
	
	_columns={
	
		'header_id':fields.many2one('direct.entry.expense','Entry'),
		'entry_id':fields.many2one('direct.entry.expense','Entry'),
		'exp_des':fields.text('Expense Description',size=200),
		'dis_amt':fields.float('Discount Amount'),
		'tax_id': fields.many2many('account.tax', 'sol_taxes', 'sol_id', 'tax_id', 'Taxes'),
		'total_amt':fields.float('Amount'),
		
		
		
	
	}	
	
	_defaults = {
	
		
	
	}
	
	def _amount_line(self, cr, uid, ids, prop, arg, context=None):
		cur_obj=self.pool.get('res.currency')
		tax_obj = self.pool.get('account.tax')
		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			amt_to_per = (line.dis_amt / (1 * line.total_amt or 1.0 )) * 100
			price = line.total_amt * (1 - (amt_to_per or 0.0) / 100.0)
			taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, 1, 4099, line.header_id.supplier_id)
			cur = line.header_id.supplier_id.property_product_pricelist_purchase.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, taxes['total_included'])
		return res  
		
ch_direct_expense_entry()
