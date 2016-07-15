from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import date
import openerp.addons.decimal_precision as dp
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import re
import smtplib
import netsvc
import time, datetime
from datetime import *
import calendar
import datetime
from dateutil.relativedelta import relativedelta 


class kg_po_pending_mail(osv.osv):

	_name = "kg.po.pending.mail"
	_description = "KG PO Pending"


	def notification_to_user(self,cr,uid,ids=0,context=None):
		company_name = self.pool.get('res.company').browse(cr,uid,1)
		email_from = []
		email_to = []
		email_cc = []
		ir_model = self.pool.get('kg.mail.settings').search(cr,uid,[('active','=',True)])
		#to_mails = []
		#hr_mail_id = '' 
		mail_form_ids = self.pool.get('kg.mail.settings').search(cr,uid,[('active','=',True)])
		for ids in mail_form_ids:
			mail_form_rec = self.pool.get('kg.mail.settings').browse(cr,uid,ids)
			print "kjsjsddsd .........",mail_form_rec.doc_name.model
			if mail_form_rec.doc_name.model == 'kg.po.pending.mail':
				email_from.append(mail_form_rec.name)
				mail_line_id = self.pool.get('kg.mail.settings.line').search(cr,uid,[('line_entry','=',ids)])
				for mail_id in mail_line_id:
					mail_line_rec = self.pool.get('kg.mail.settings.line').browse(cr,uid,mail_id)
					if mail_line_rec.to_address:
						email_to.append(mail_line_rec.mail_id)
					if mail_line_rec.cc_address:
						email_cc.append(mail_line_rec.mail_id)
		
		today = date.today()
		d = today - relativedelta(months=1)
		

		first_day=date(d.year, d.month, 1)
		
		month = first_day.strftime("%B")
		year = first_day.strftime("%Y")
		first_day = first_day.strftime("%Y-%m-%d")
		last_day=date(today.year, today.month, 1) - relativedelta(days=1)
		last_day = last_day.strftime("%Y-%m-%d")
		
		
		sql = """SELECT
			po.id AS po_id,
			po.name AS po_no,
			to_char(po.date_order,'dd/mm/yyyy') AS po_date,
			po.date_order AS date,
			(CURRENT_DATE - po.date_order) as tat,
			po.note AS remark,
			po.amount_total as total,
			po.add_text as address,
			po.amount_tax as taxamt,
			pol.id as pol_id,
			pol.product_qty AS qty,
			pol.pending_qty AS pending_qty,
			pol.price_unit as rate,
			pol.kg_discount_per as disc1,
			pol.kg_disc_amt_per as disc2,			  
			po_ad.advance_amt as po_ad_amt,			  
			uom.name AS uom,
			pt.name AS pro_name,
			res.name AS su_name,
			res.street AS str1,
			res.zip as zip,
			city.name as city,
			state.name as state,
			brand.name as brand_name,
			po.quot_ref_no as quot_ref_no
				  
					  
			FROM  purchase_order po
					  
			JOIN res_partner res ON (res.id=po.partner_id)
			left join res_city city on(city.id=res.city)
			left join res_country_state state on(state.id=res.state_id)
			JOIN purchase_order_line pol ON (pol.order_id=po.id)
			JOIN product_product prd ON (prd.id=pol.product_id)
			JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
			JOIN product_uom uom ON (uom.id=pol.product_uom)
			left JOIN kg_brand_master brand ON (pol.brand_id = brand.id)
			left JOIN kg_po_advance_line po_ad ON (po_ad.po_id = po.id)

			where po.state='approved' and pol.pending_qty > 0 and po.date_order >= '%s' and po.date_order <= '%s'
			order by po.date_order,po.name
			"""%(first_day,last_day)
		
		
		gen_part_1 = ""
		gen_part_2 = ""
		gen_part_3 = ""
		gen_part_4 = ""
		po_list = []
		gr_tot = 0.0
		cr.execute(sql)
		data = cr.dictfetchall()
		print "buyer_data...................", data
			
		if data:
			
			msg = ''
			msg = MIMEMultipart('alternative')
			msg['Subject'] =  company_name.code + " : Pending PO Register For " " " + month + "-" + year + ""
			msg['From'] = ','.join(email_from)
			msg['To'] = ','.join(email_to)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>to address>>>>>>>>>>>>>>>>>>>>>>>>>>",msg['To']
			msg['Cc'] = ','.join(email_cc)   
			print ">>>>>>>>>>>>>>>>>>>>>>>>>cc address>>>>>>>>>>>>>>>>>>>>>>>>>>",msg['Cc']   
			
			gen_part_1 = """\
				<html>
				<head>
				<style>
				table, th, td {
				border: 1px solid white;
				border-collapse: collapse;
				}
				th, td {
				padding: 5px;
				}
				body {
				background-image: url("");
				}
				</style>
				</head>
					<body>
						
						
						<h2><font color="#0033FF" text-align="center">"""+str(company_name.code)+""" : Pending PO Register For """ +str(month)+""" - """+ str(year) +""".</font></b></h2>
						<table border="1" style="border-collapse:collapse"> 
							<tr style="background-color:#FFB895;color:1F3399;">
							<th colspan='4'>S No</th>	
							
							<th colspan='4'>PO NO</th>	
							<th colspan='4'>PO Date</th>	
							<th colspan='4'>Supplier</th>	
							<th colspan='4'>Product</th>	
							<th colspan='4'>UOM</th>	
							<th colspan='4'>Price</th>	
							<th colspan='4'>PO Qty </th>	
							<th colspan='4'>Pending Qty</th>	
							<th colspan='4'>TAT</th>	
							
							</tr>
							
							"""
			ser_no =1
			for item in data:
				if item['po_no'] not in po_list:
					po_list.append(item['po_no'])
					item['po_no']= item['po_no']
					item['po_date']= item['po_date']
					item['su_name']= item['su_name']
					item['tat']= item['tat']
				else:
					item['po_no']= ''
					item['po_date']= ''
					item['su_name']= ''
					item['tat']= ''	
				gen_part_2 += """<tr style="background-color:#FFE8DD;color:black;">
					<td colspan='4'>"""+str(ser_no)+"""</td>
					<td colspan='4'>"""+str(item['po_no'])+"""</td>
					<td colspan='4'>"""+str(item['po_date'])+"""</td>
					<td colspan='4'>"""+str(item['su_name'])+"""</td>
					<td colspan='4'>"""+str(item['pro_name'])+"""</td>
					<td colspan='4'>"""+str(item['uom'])+"""</td>
					<td colspan='4'>"""+str(item['rate'])+"""</td>
					<td colspan='4'>"""+str(item['qty'])+"""</td>
					<td colspan='4'>"""+str(item['pending_qty'])+"""</td>
					<td colspan='4'>"""+str(item['tat'])+"""</td>
					
				</tr> """
				ser_no += 1	
				gr_tot += item['pending_qty']
					
			
					
			gen_part_4 = """	
			 </table>
			 
			 </br>
			 <br/>
			 
			 <p> 
			 </br>
			 <font size="2" color="0033FF">** This mail is auto generated from ERP system.</font>
			 </p>
			 </body>
			 </html>"""
				
		

			html = gen_part_1 + gen_part_2 + gen_part_4
		
		
			part2 = MIMEText(html, 'html')
			msg.attach(part2)
			
			# Check Server Connection
			try:
				print "server checking..............."
				server = smtplib.SMTP('10.100.1.209')
			#	server.sendmail(from_mailid,party_rec.email,msg.as_string())
				server.sendmail(email_from,email_to+email_cc,msg.as_string())
				print " Message............................",msg.as_string()
				print "Successfully sent email ---------------------To.........>>" 
			except Exception:
				pass
				return True
				
		else:
			
			msg = ''
			msg = MIMEMultipart('alternative')
			msg['Subject'] = "Monthly PO Count Report"
			msg['From'] = email_from
			msg['To'] = ','.join(email_to)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>to address>>>>>>>>>>>>>>>>>>>>>>>>>>",msg['To']
			msg['Cc'] = ','.join(email_cc)   
			print ">>>>>>>>>>>>>>>>>>>>>>>>>cc address>>>>>>>>>>>>>>>>>>>>>>>>>>",msg['Cc']   
			
			gen_part_1 = """\
				<html>
				<head>
				<style>
				table, th, td {
				border: 1px solid black;
				border-collapse: collapse;
				}
				th, td {
				padding: 5px;
				}
				body {
				background-image: url("");
				}
				</style>
				</head>
					<body>
						<p>
							
							<p> <b><font size="3" color="blue">Dear Sir,<br /></font></b></p>
							<p>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp <font size="3">There is no Purchase Order for <b><font size="3" color="brown">""" +str(month)+"""</font></b> Month.<br /></font></p></p><br/>
							
						</p>
						
			 <p> <b><font size="3" color="003366">Thanks & Regards,<br /></font></b>
			
			 <font size="3">KGiSL-IAS</font>
			 </p>"""

			html = gen_part_1 
		
		
			part2 = MIMEText(html, 'html')
			msg.attach(part2)
			
			# Check Server Connection
			try:
				print "server checking..............."
				server = smtplib.SMTP('10.100.1.209')
			#	server.sendmail(from_mailid,party_rec.email,msg.as_string())
				server.sendmail(email_from,email_to+email_cc,msg.as_string())
				print " Message............................",msg.as_string()
				print "Successfully sent email ---------------------To.........>>" 
			except Exception:
				pass
				return True
	
kg_po_pending_mail()
