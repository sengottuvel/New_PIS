from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from datetime import datetime

a = datetime.now()
dt_time = a.strftime('%m/%d/%Y %H:%M:%S')

### All many2one field should end with _id. Ex : user_id, partner_id, employee_id
### All one2many fields name should line_ids
### All many2many field should end with _ids. EX : tax_ids, user_ids
### All date fields should end with date
### Parent table id in child table should be in "header_id"

class kg_selling_cost_details(osv.osv):

	_name = "kg.selling.cost.details"
	_description = "Selling Cost Details Module"
	_order = "date desc"
	
	_columns = {

		'date': fields.datetime('Creation Date', readonly=True)	,
		'user_id': fields.many2one('res.users','Created By', readonly=True),		
		'name': fields.char('No', size=128,select=True,readonly=True),
		'trans_date': fields.date('Date', readonly=True, states={'draft':[('readonly',False)]},
											select=True, required=True),						
		'partner_id': fields.many2one('res.partner', 'Buyer Name', select=True,
					domain=[('customer', '=', True)], readonly=True, states={'draft':[('readonly',False)]}),
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),		
		'line_ids':fields.one2many('kg.selling.cost.details.line', 'header_id', 'Selling Cost Details Line',readonly=True, states={'draft':[('readonly',False)]}),
		'remark': fields.text('Remarks', readonly=True, states={'draft':[('readonly',False)]}),		
		'state': fields.selection([('load','Load'),('draft','Draft'),('confirm','Waiting for approval'),('approved','Approved'),
				('reject','Rejected'),('cancel','Cancelled'),('inactive','Inactive')],'Status', readonly=True,track_visibility='onchange',select=True),
		'approve_date': fields.datetime('Approved Date', readonly=True),
		'app_user_id': fields.many2one('res.users', 'Apprved By', readonly=True),
		'confirm_date': fields.datetime('Confirm Date', readonly=True),
		'conf_user_id': fields.many2one('res.users', 'Confirmed By', readonly=True),
		'reject_date': fields.datetime('Reject Date', readonly=True),
		'rej_user_id': fields.many2one('res.users', 'Rejected By', readonly=True),
		'cancel_date': fields.datetime('Cancel Date', readonly=True),
		'can_user_id': fields.many2one('res.users', 'Cancelled By', readonly=True),
		'orderby_no': fields.integer('Order By',readonly=True),
		'active': fields.boolean('Active'),
		'load': fields.boolean('Load'),
		'total': fields.float('Total Amount', readonly=True),
		
		
	}
	
	_defaults = {
	
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg_selling_cost_details', context=c),			
		'trans_date' : fields.date.context_today,
		'date':fields.datetime.now,		
		'state': 'load',		
		'active': True,
		'load': False,
		'user_id': lambda obj, cr, uid, context: uid,
		
	}
	
	def load_stock(self, cr, uid, ids = 0,context=None):
		rec  = self.browse(cr,uid,ids[0])
		sale_line = self.pool.get('sale.order.line')
		#sql = """delete from kg_physical_stock where state='load'"""
		#cr.execute(sql)		
				
		"""
		draft_amends=self.search(cr,uid,[('date','=',rec.date)])
		if len(draft_amends) > 1:
			raise osv.except_osv(
				_('Physical stock has been already done'),
				_('for this Date')) 
		"""
		
		#vals={
			#'stock_type':'main',
			#'state':'draft',
			
			#}
		
		#stock = self.pool.get('kg.physical.stock').create(cr,uid,vals,context=None)		
		sql="""select pt.id as product,
			
			spl.product_uom as uom,
			(sum(price_tax) / count(product_id)) as price 
			from product_template pt
			join stock_production_lot spl on(pt.id = spl.product_id)
			where pt.sale_ok='t' 
			group by pt.id,spl.product_uom

			"""
		cr.execute(sql)
		data = cr.dictfetchall()		
		data.sort(key=lambda data: data['product'])
		
		for item in data:
			sale_search = sale_line.search(cr, uid, [('state','=','confirmed'),('product_id','=',item['product'])])
			print  "----------------------------------------------",sale_search		
			if sale_search:
				sale_browse = sale_line.browse(cr, uid, sale_search[-1])
				price = sale_browse.price_unit	
			else:
				price = item['price']		
				
			line_vals = {
			'product_id':item['product'],
		
			'uom_id':item['uom'],
			'purchase_price':item['price'],
			'sale_price':price,
			'header_id':rec.id,
			
			}
			if line_vals:
				common_line = self.pool.get('kg.selling.cost.details.line').create(cr,uid,line_vals,context=None)
				
		self.write(cr,uid,ids[0],{'load':True,'state':'draft'})		
		return True	
	

	def _future_date_check(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		today = date.today()
		today = str(today)
		today = datetime.strptime(today, '%Y-%m-%d')
		trans_date = rec.trans_date
		trans_date = str(trans_date)
		trans_date = datetime.strptime(trans_date, '%Y-%m-%d')
		if trans_date > today:
			return False
		return True		
	
	def _check_line_entry(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.line_ids:
			return False
		else:
			for line in entry.line_ids:
				if line.unit_price == 0 or line.quantity == 0:
					return False
		return True
	
	_constraints = [        
              
        #(_check_line_entry, 'System not allow to save empty transaction and zero qty .!!',['price']),
        (_future_date_check, 'System not allow to save with future date. !!',['price']),
        
       ]

	def entry_confirm(self,cr,uid,ids,context=None):		
		cr.execute(''' select count(*) from kg_selling_cost_details where state !='draft' ''')
		data = cr.fetchone()
		order_by = data[0] + 1		
		rec = self.browse(cr,uid,ids[0])
		for element in rec.line_ids:
			if (round(element.sale_price,2)) >= (round(element.purchase_price,2)):
				pass
			else:
				raise osv.except_osv(
					_('Warning'),
					_('Sale cost must be greater than Purchase cost. Please check - %s' %(element.product_id.name)))
		self.write(cr, uid, ids, {
					'state': 'confirm',
					'conf_user_id': uid,
					'confirm_date': dt_time,
					'name' : self.pool.get('ir.sequence').get(cr, uid, 'kg.selling.cost.details'),
					'orderby_no':order_by,
					})
		return True

	def entry_approve(self,cr,uid,ids,context=None):
		user_id = self.pool.get('res.users').browse(cr, uid, uid)
		rec = self.browse(cr,uid,ids[0])
		line_obj = self.pool.get('kg.selling.cost.details.line')
		"""
		if rec.conf_user_id.id == uid:
			raise osv.except_osv(
					_('Warning'),
					_('Approve cannot be done by Confirmed user'))
		
		"""
		cr.execute('''update kg_selling_cost_details set state ='inactive' where state ='approved' ''')	
		cr.execute('''update kg_selling_cost_details_line set state ='inactive' where state ='approved' ''')	
		for element in rec.line_ids:
			if (round(element.sale_price,2)) >= (round(element.purchase_price,2)):
				pass
			else:
				raise osv.except_osv(
					_('Warning'),
					_('Sale cost must be greater than Purchase cost. Please check - %s' %(element.product_id.name)))
			line_obj.write(cr,uid,element.id,{'state':'approved'})
			
			
		self.write(cr, uid, ids, {
				'state': 'approved',
				'app_user_id': uid,
				'approve_date': dt_time})

		return True

	def entry_reject(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		if rec.remark:
			self.write(cr, uid, ids, {
						'state': 'reject',
						'rej_user_id': uid,
						'reject_date': dt_time})
		else:
			raise osv.except_osv(_('Rejection remark is must !!'),
				_('Enter rejection remark in remark field !!'))
		return True

	def entry_cancel(self,cr,uid,ids,context=None):
		## Don't allow to cancel if this id linked with other transaction or master
		self.write(cr, uid, ids, {'state': 'cancel','can_user_id': uid,
				'cancel_date': dt_time})
		return True

	def entry_draft(self,cr,uid,ids,context=None):
		# While change state corresponding back updated to be done
		self.write(cr, uid, ids, {'state': 'draft'})
		return True

	def unlink(self,cr,uid,ids,context=None):
		unlink_ids = []		
		for rec in self.browse(cr,uid,ids):	
			if rec.state != 'draft':			
				raise osv.except_osv(_('Warning!'),
						_('You can not delete this entry !!'))
			else:
				unlink_ids.append(rec.id)
		return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)	
	
kg_selling_cost_details()


class kg_selling_cost_details_line(osv.osv):
	
	_name = "kg.selling.cost.details.line"
	_description = "Selling Cost Details Line"
	
	_columns = {
		
		'header_id': fields.many2one('kg.selling.cost.details','Selling Cost Details',ondelete='cascade',select=True),
		'product_id': fields.many2one('product.product', 'Item Name', required=True),
		'brand_id': fields.many2one('kg.brand.master', 'Brand'),
		'uom_id': fields.many2one('product.uom', 'UOM', required=False),
		'purchase_price': fields.float('Purchase Cost', required=True),
		'sale_price': fields.float('Selling Cost', required=True),
	
		'total': fields.float('Total'),
		'remark': fields.text('Remark'),
		'discount': fields.float('Discount(%)'),
		'state': fields.selection([('load','Load'),('draft','Draft'),('confirm','Waiting for approval'),('approved','Approved'),
				('reject','Rejected'),('cancel','Cancelled'),('inactive','Inactive')],'Status', readonly=True,track_visibility='onchange',select=True),
	}	
	
kg_selling_cost_details_line()
