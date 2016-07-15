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


class kg_gate_pass_pending_mail(osv.osv):

	_name = "kg.gate.pass.pending.mail"
	_description = "KG Gate Pass Pending"


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
			if mail_form_rec.doc_name.model == 'kg.gate.pass.pending.mail':
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
		
		
		sql = """
				select pt.name AS pro_name,
				uom.name AS uom,
				gpl.grn_pending_qty as pending_qty,
				(CURRENT_DATE - gp.date) as tat,
				(gpl.grn_pending_qty * sol.price_unit) as price,
				res.name AS su_name,
				ow.name AS outward,
				gp.name AS gp_no,
				to_char(gp.date,'dd-mm-yyyy') AS gp_date,
				gpl.qty as qty,
				(gpl.qty - gpl.grn_pending_qty) as return_qty,
				gp.note as remark
				from kg_gate_pass as gp
				JOIN kg_gate_pass_line gpl ON (gpl.gate_id=gp.id)
				JOIN product_product prd ON (prd.id=gpl.product_id)
				JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
				JOIN product_uom uom ON (uom.id=gpl.uom)
				JOIN res_partner res ON (res.id=gp.partner_id)
				left join kg_outwardmaster ow on (ow.id=gp.out_type)
				left JOIN kg_service_order_line sol on (sol.soindent_line_id=gpl.si_line_id)
				where gp.state='done' and gpl.grn_pending_qty > 0 
			order by gp.date,gp.name
			"""
		
		
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
			msg['Subject'] =  company_name.code + " : Opening Gate Pass Alert For" " " + month + "-" + year + ""
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
						
						
						<h2><font color="#0033FF" text-align="center">"""+str(company_name.code)+""" : Opening Gate Pass Alert For""" +str(month)+""" - """+ str(year) +""".</font></b></h2>
						<table border="1" style="border-collapse:collapse"> 
							<tr style="background-color:#FFB895;color:1F3399;">
							<th colspan='4'>S No</th>	
							
							<th colspan='4'>Product</th>	
							<th colspan='4'>UOM</th>	
							<th colspan='4'>Pending Qty</th>	
							<th colspan='4'>Age (in Days)</th>	
							<th colspan='4'>Value</th>	
							<th colspan='4'>Vendor</th>	
							<th colspan='4'>Reason</th>	
							<th colspan='4'>Gate Pass No</th>	
							<th colspan='4'>Date</th>	
							<th colspan='4'>Qty Send</th>	
							<th colspan='4'>Qty Returned</th>	
							<th colspan='4'>Remark</th>	
							
							</tr>
							
							"""
			ser_no =1
			for item in data:
				
				gen_part_2 += """<tr style="background-color:#FFE8DD;color:black;">
					<td colspan='4'>"""+str(ser_no)+"""</td>
					<td colspan='4'>"""+str(item['pro_name'])+"""</td>
					<td colspan='4'>"""+str(item['uom'])+"""</td>
					<td colspan='4'>"""+str(item['pending_qty'])+"""</td>
					<td colspan='4'>"""+str(item['tat'])+"""</td>
					<td colspan='4'>"""+str(item['price'])+"""</td>
					<td colspan='4'>"""+str(item['su_name'])+"""</td>
					<td colspan='4'>"""+str(item['outward'])+"""</td>
					<td colspan='4'>"""+str(item['gp_no'])+"""</td>
					<td colspan='4'>"""+str(item['gp_date'])+"""</td>
					<td colspan='4'>"""+str(item['qty'])+"""</td>
					<td colspan='4'>"""+str(item['return_qty'])+"""</td>
					<td colspan='4'>"""+str(item['remark'])+"""</td>
					
				</tr> """
				ser_no += 1	
				
					
			
					
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
	
kg_gate_pass_pending_mail()
