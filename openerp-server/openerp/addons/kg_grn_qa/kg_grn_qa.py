from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
import datetime
from datetime import date
class kg_grn_qa(osv.osv):

	_name = "kg.grn.qa"
	_description = "KG GRN qa"
	_order = "date desc"

	
	_columns = {
	
		'date': fields.datetime('Creation Date', readonly=True)	,
		'user_id': fields.many2one('res.users','Created By', readonly=True),		
		'name': fields.char('QA No', size=128,select=True,readonly=True),
		'qa_date': fields.date('QA Date', readonly=True, states={'draft':[('readonly',False)]},select=True, required=True),						
		'partner_id': fields.many2one('res.partner', 'Supplier', select=True,
					domain=[('customer', '=', True)], readonly=True, states={'draft':[('readonly',False)]}),
		'company_id': fields.many2one('res.company', 'Company Name',readonly=True),		
		'line_ids':fields.one2many('kg.grn.qa.line', 'grn_line_id', 'Grn QA Line',readonly=True, states={'draft':[('readonly',False)]}),
		'remark': fields.text('Remarks', readonly=True, states={'draft':[('readonly',False)]}),		
		'state': fields.selection([('draft','Draft'),('confirm','Waiting for approval'),('approved','Approved'),
				('reject','Rejected'),('cancel','Cancelled')],'Status', readonly=True,track_visibility='onchange',select=True),
		'approve_date': fields.datetime('Approved Date', readonly=True),
		'app_user_id': fields.many2one('res.users', 'Apprved By', readonly=True),
		'confirm_date': fields.datetime('Confirm Date', readonly=True),
		'conf_user_id': fields.many2one('res.users', 'Confirmed By', readonly=True),
		
		'cancel_date': fields.datetime('Cancel Date', readonly=True),
		'can_user_id': fields.many2one('res.users', 'Cancelled By', readonly=True),
		
		'active': fields.boolean('Active'),
		'gen_grn_no':fields.many2one('kg.general.grn','GRN NO',readonly=True,states={'draft': [('readonly', False)]}),
		'po_grn_no':fields.many2one('kg.po.grn','GRN NO',readonly=True,states={'draft': [('readonly', False)]}),
		'gen_grn_date':fields.datetime('GRN Date',readonly=True,states={'draft': [('readonly', False)]}),
		'po_grn_date':fields.datetime('GRN Date',readonly=True,states={'draft': [('readonly', False)]}),
		'grn_type': fields.selection([('from_po_grn', 'PO/SO GRN'), ('from_general_grn', 'General GRN'), ('others', 'Others')], 'GRN Type',readonly=True, states={'draft':[('readonly',False)]}),
		
	}
	_defaults={
	
	'date': fields.date.context_today,
	'name':'',
	'state':'draft',
	'active':True,
	'qa_date':fields.date.context_today,
	'user_id': lambda obj, cr, uid, context: uid,
	}
	
	
	def confirm(self,cr,uid,ids,context=None):
		rec  = self.browse(cr,uid,ids[0])
		date = datetime.date.today()
		print "date",date
		if rec.grn_type == 'from_general_grn':
			for element in rec.gen_grn_no.grn_line:
				for line in rec.line_ids:
					if element.product_id == line.product_id:
						
						if line.accepted_qty > 0:
							rej_qty = line.quantity - line.accepted_qty
							element.write({'grn_qty':line.accepted_qty})
							line.write({'rejected_qty':rej_qty})
						else:
							raise osv.except_osv(_('Invalid Action!'), _('You can not confirm a product with zero quantity'))
		else:
			for element in rec.po_grn_no.line_ids:
				for line in rec.line_ids:
					if element.product_id == line.product_id:
						
						if line.accepted_qty > 0:
							rej_qty = line.quantity - line.accepted_qty
							element.write({'po_grn_qty':line.accepted_qty})
							line.write({'rejected_qty':rej_qty})
						else:
							raise osv.except_osv(_('Invalid Action!'), _('You can not confirm a product with zero quantity'))						
		
		self.write(cr,uid,ids[0],{'state':'confirm','conf_user_id':uid,'confirm_date':date,
				'name':self.pool.get('ir.sequence').get(cr, uid, 'kg.grn.qa'),
				})	
		
	def approve(self,cr,uid,ids,context=None):
		rec  = self.browse(cr,uid,ids[0])
		po_line = self.pool.get('purchase.order.line')
		so_line = self.pool.get('kg.service.order.line')
		date = datetime.date.today()
		if rec.conf_user_id.id == uid:
			raise osv.except_osv(
					_('Warning'),
					_('Approve cannot be done by Confirmed user'))
		else:
			if rec.grn_type == 'from_general_grn':
				self.pool.get('kg.general.grn').kg_grn_approve(cr,uid,rec.gen_grn_no.id,context = None)	
			else:
				
				if rec.po_grn_no.grn_type == 'from_po':
					for line in rec.line_ids:
						if line.po_line_id.id: 
							po_line_rec  = po_line.browse(cr,uid,line.po_line_id.id)
							pending_qty = po_line_rec.pending_qty + line.rejected_qty
							
						else:
							pass	
				else:
					for line in rec.line_ids:
						if line.so_line_id.id: 
							so_line_rec  = so_line.browse(cr,uid,line.so_line_id.id)
							pending_qty = so_line_rec.pending_qty + line.rejected_qty
							
						else:
							pass
				self.pool.get('kg.po.grn').kg_po_grn_approve(cr,uid,rec.po_grn_no.id,context = None)								
			rec.write({'app_user_id':uid})
			rec.write({'approve_date':date})
			rec.write({'state':'approved'})
			
	def approve_GP(self,cr,uid,ids,context=None):
		rec  = self.browse(cr,uid,ids[0])
		po_line = self.pool.get('purchase.order.line')
		so_line = self.pool.get('kg.service.order.line')
		gp_obj = self.pool.get('kg.gate.pass')
		gp_line_obj = self.pool.get('kg.gate.pass.line')
		date = datetime.date.today()
		if rec.conf_user_id.id == uid:
			raise osv.except_osv(
					_('Warning'),
					_('Approve cannot be done by Confirmed user'))
		else:
			if rec.grn_type == 'from_general_grn':
				self.pool.get('kg.general.grn').kg_grn_approve(cr,uid,rec.gen_grn_no.id,context = None)	
			else:
				form_vals = {
					
					
					'partner_id':rec.partner_id.id,
					'gp_type':'direct',
					'creation_date':date,
					'user_id':uid,
					'indent_flag': True,
										}   
		
				gp_id = gp_obj.create(cr,uid,form_vals)
				if rec.po_grn_no.grn_type == 'from_po':
					for line in rec.line_ids:
						if line.po_line_id.id: 
							po_line_rec  = po_line.browse(cr,uid,line.po_line_id.id)
							pending_qty = po_line_rec.pending_qty + line.rejected_qty

							if line.rejected_qty > 0:
								gp_line_obj.create(cr,uid,
											{
											
											'gate_id':gp_id,
											
											'product_id':line.product_id.id,
											'uom':line.uom_id.id,
											'qty':line.rejected_qty,
											'grn_pending_qty':line.rejected_qty,
											
											
											
											})	
						else:
							pass	
				else:
					for line in rec.line_ids:
						if line.so_line_id.id: 
							so_line_rec  = so_line.browse(cr,uid,line.so_line_id.id)
							pending_qty = so_line_rec.pending_qty + line.rejected_qty
							
							if line.rejected_qty > 0:
								gp_line_obj.create(cr,uid,
											{
											
											'gate_id':gp_id,
											
											'product_id':line.product_id.id,
											'uom':line.uom_id.id,
											'qty':line.rejected_qty,
											'grn_pending_qty':line.rejected_qty,
											'si_line_id':line.si_line_id.id,
											
											
											
											})	
						else:
							pass
				self.pool.get('kg.po.grn').kg_po_grn_approve(cr,uid,rec.po_grn_no.id,context = None)								
			rec.write({'app_user_id':uid})
			rec.write({'approve_date':date})
			rec.write({'state':'approved'})
							
		
			
	def unlink(self, cr, uid, ids, context=None):
		grn_qa = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for s in grn_qa:
			if s['state'] in ['draft', 'cancel']:
				unlink_ids.append(s['id'])
			else:
				raise osv.except_osv(_('Invalid Action!'), _('You can not delete the confirmed QA'))
		return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
kg_grn_qa()



class kg_grn_qa_line(osv.osv):
	_name = "kg.grn.qa.line"
	_description = "KG GRN QA line"
	
	_columns = {
	  'product_id':fields.many2one('product.product','Item Name'),
	  'quantity':fields.float('Quantity'),
	  'accepted_qty':fields.float('Accepted Qty'),
	  'rejected_qty':fields.float('Rejected Qty'),
	  'grn_line_id':fields.many2one('kg.grn.qa','GRN QA'),
	  'po_line_id':fields.many2one('purchase.order.line','PO Line'),
	  'so_line_id':fields.many2one('kg.service.order.line','SO Line'),
	  'pi_line_id':fields.many2one('purchase.requisition.line','PI Line'),
	  'si_line_id':fields.many2one('kg.service.indent.line','SI Line'),
	  'gen_grn_line_id':fields.many2one('kg.general.grn.line','SI Line'),
	  'po_grn_line_id':fields.many2one('po.grn.line','SI Line'),

	  'remarks':fields.char('Remarks'),
	  'uom_id':fields.many2one('product.uom','UOM',readonly=True),
		
	}
	_defaults={
	
		'rejected_qty':0.00,
	}

	
	def onchange_reject_qty(self,cr,uid,ids,quantity,accepted_qty,rejected_qty):
		value = {'rejected_qty':''}
		reject = quantity - accepted_qty
		value = {'rejected_qty':reject}
		return {'value':value}
		
kg_grn_qa_line()


