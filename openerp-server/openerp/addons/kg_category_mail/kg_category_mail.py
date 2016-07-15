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
from collections import Counter

class kg_category_mail(osv.osv):

	_name = "kg.category.mail"
	_description = "Category Count"


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
			
			if mail_form_rec.doc_name.model == 'kg.category.mail':
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
		
		sql = cr.execute("""select res.id as user_id,res.login as name from res_users res where active='t' and res.id != 1""")
		
		data=cr.dictfetchall()
		
		cat_list = []
		row_list = []
		col_list = []
		sql1 = cr.execute("""SELECT   
							pc.name as category,
							pc.id as cat_id,
							res.login as user,
							res.id as user_id,
							sum(pol.product_qty * pol.price_unit) as quantity,
							count(pc.name) as cat_count
								  
							FROM  purchase_order_line pol 

							JOIN purchase_order po ON (po.id = pol.order_id)
							JOIN res_users res ON (res.id = pol.create_uid)
							JOIN product_product prd ON (prd.id=pol.product_id)
							JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
							JOIN product_category pc ON (pc.id=pt.categ_id)
							where po.date_order >='%s' and po.date_order <='%s' 
							group by 1,2,3,4

							union

							SELECT  
							pc.name as category,
							pc.id as cat_id,
							res.login as user,
							res.id as user_id,
							sum(sol.product_qty * sol.price_unit) as quantity,
							count(pc.name) as cat_count
								  
							FROM  kg_service_order_line sol 

							JOIN kg_service_order so ON (so.id = sol.service_id)
							JOIN res_users res ON (res.id = sol.create_uid)
							JOIN product_product prd ON (prd.id=sol.product_id)
							JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
							JOIN product_category pc ON (pc.id=pt.categ_id)
							where so.date >='%s' and so.date <='%s'
							group by 1,2,3,4

							union

							SELECT  
							pc.name as category,
							pc.id as cat_id,
							res.login as user,
							res.id as user_id,
							sum(ggl.grn_qty * ggl.price_unit) as quantity,
							count(pc.name) as cat_count
								  
							FROM  kg_general_grn_line ggl 

							JOIN kg_general_grn gg ON (gg.id = ggl.grn_id)
							JOIN res_users res ON (res.id = ggl.create_uid)
							JOIN product_product prd ON (prd.id=ggl.product_id)
							JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
							JOIN product_category pc ON (pc.id=pt.categ_id)
							where gg.grn_date >='%s' and gg.grn_date <='%s'
							group by 1,2,3,4"""%(first_day,last_day,first_day,last_day,first_day,last_day))
		
		data1=cr.dictfetchall()
		
		for item1 in data1:
			if item1['cat_id'] not in cat_list and item1['cat_count'] > 0:
				cat_list.append(item1['cat_id'])
				
		for cat in cat_list:
			category_dict = {}
			user_cot = []   
			other_cot = 0.0 
			sum_col = 0
			sum_qty = 0
		   
			user_qty = []   
			other_qty = 0.0 
			cat_rec = self.pool.get('product.category').browse(cr,uid, cat)
			category_dict['cat_name'] = cat_rec.name
			
			for item in data:
				sql2 = cr.execute("""SELECT	  
					pc.name as category,
					pc.id as cat_id,
					res.login as user,
					res.id as user_id,
					sum(pol.product_qty * pol.price_unit) as quantity,
					count(pc.name) as cat_count
						  
					FROM  purchase_order_line pol 

					JOIN purchase_order po ON (po.id = pol.order_id)
					JOIN res_users res ON (res.id = pol.create_uid)
					JOIN product_product prd ON (prd.id=pol.product_id)
					JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
					JOIN product_category pc ON (pc.id=pt.categ_id)
					where po.date_order >='%s' and po.date_order <='%s' and pc.id = %s and res.id = %s
					group by 1,2,3,4

					union

					SELECT	
					pc.name as category,
					pc.id as cat_id,
					res.login as user,
					res.id as user_id,
					sum(sol.product_qty * sol.price_unit) as quantity,
					count(pc.name) as cat_count
						  
					FROM  kg_service_order_line sol 

					JOIN kg_service_order so ON (so.id = sol.service_id)
					JOIN res_users res ON (res.id = sol.create_uid)
					JOIN product_product prd ON (prd.id=sol.product_id)
					JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
					JOIN product_category pc ON (pc.id=pt.categ_id)
					where so.date >='%s' and so.date <='%s' and pc.id = %s and res.id = %s
					group by 1,2,3,4

					union

					SELECT	
					pc.name as category,
					pc.id as cat_id,
					res.login as user,
					res.id as user_id,
					sum(ggl.grn_qty * ggl.price_unit) as quantity,
					count(pc.name) as cat_count
						  
					FROM  kg_general_grn_line ggl 

					JOIN kg_general_grn gg ON (gg.id = ggl.grn_id)
					JOIN res_users res ON (res.id = ggl.create_uid)
					JOIN product_product prd ON (prd.id=ggl.product_id)
					JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
					JOIN product_category pc ON (pc.id=pt.categ_id)
					where gg.grn_date >='%s' and gg.grn_date <='%s' and pc.id = %s and res.id = %s
					group by 1,2,3,4"""%(first_day,last_day,cat,item['user_id'],first_day,last_day,cat,item['user_id'],first_day,last_day,cat,item['user_id'])) 
				data2=cr.dictfetchall()
				if data2:
					count = data2[0]['cat_count']
					qty = data2[0]['quantity']
				else:
					count = 0
					qty = 0
						
				user_cot.append(count)
				category_dict[item['user_id']] = count
				user_qty.append(qty)
				category_dict[item['name']] = qty
			category_dict['tot_count'] = sum(user_cot)	  
			category_dict['tot_qty'] = sum(user_qty)	  
			if sum(user_cot) > 0:
				row_list.append(category_dict)	
				
		c = Counter()
		for d in row_list:
			c.update(d)
					
		col_list = [{key: value} for key, value in c.items()]
		print "-----------",col_list
		
		col_key = []
		for col in col_list:
			for key, value in col.iteritems():
				if isinstance(key, int) and value > 0:
					col_key.append(key)
					
		col_dict = dict((k,v) for d in col_list for (k,v) in d.items())			
					 
		print "---------------------------->",col_key			 
		print "---------------------------->",col_dict			 
		
			
		gen_part_1 = ""
		gen_part_2 = ""
		gen_part_3 = ""
		gen_part_4 = ""
		gen_part_5 = ""
		gen_part_6 = ""
		gen_part_7 = ""
		gen_part_8 = ""
		gen_part_9 = ""
		gen_part_10 = ""
		gen_part_11 = ""
		
		gr_tot = 0.0
		
			
		if data:
			
			msg = ''
			msg = MIMEMultipart('alternative')
			msg['Subject'] = company_name.code + " : Product Category Wise Count Report For " " " + month + "-" + year + ""
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
						
						
						<h2><font color="#0033FF" text-align="center">"""+str(company_name.code)+""" : Product Category Wise Count Report For """ +str(month)+""" - """+ str(year) +""".</font></b></h2>
						<table border="1" style="border-collapse:collapse"> 
						 <tr style="background-color:#FFB895;color:1F3399;">
						 
						 <th>S.No</th>
						 <th>Category</th>"""
						 
			for col in col_key:
				user_browse = self.pool.get('res.users').browse(cr,uid,col)			 
				
				gen_part_2 += """<th>"""+str(user_browse.login)+"""</th>"""			 
			
			gen_part_3 = """<th>Total Count</th>
							</tr>"""
			ser_no =1
			for row in row_list:
				gen_part_5 = ""
				gen_part_6 = ""
				gen_part_7 = ""
				
				gen_part_5 = """<tr style="background-color:#FFE8DD;color:black;">
								<td>"""+str(str(ser_no))+ """</td>
								<td>"""+str(row['cat_name'])+ """</td>"""
			
				for col in col_key:
					user_browse = self.pool.get('res.users').browse(cr,uid,col)
					
					gen_part_6 += """
								<td>"""+str(row[col]) + str("/") + str(row[user_browse.login])+ """</td>"""
					
				gen_part_7 = """
							<th>"""+str(row['tot_count'])+ str("/") + str(row['tot_qty'])+ """</th>			
							</tr>"""	
							
				gen_part_8 += gen_part_5 + 	gen_part_6 + gen_part_7
				ser_no += 1		
			
			print "----------------------------------->",gen_part_8							
			gen_part_9 = """
							<tr style="background-color:#FFE8DD;color:black;">
							
			                <td> </td>
			                <th> Total Count</th>"""
			
			for col in col_key:
					user_browse = self.pool.get('res.users').browse(cr,uid,col)
					
					
						
					gen_part_10 += """
								<th>"""+str(col_dict[col]) + str("/") + str(col_dict[user_browse.login])+ """</th>"""
			
			gen_part_11 = """<th>"""+str(col_dict['tot_count'])+ str("/") + str(col_dict['tot_qty'])+"""</th></tr>"""
								
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
				
		

			html = gen_part_1 + gen_part_2 + gen_part_3 + gen_part_8 + gen_part_9 + gen_part_10 + gen_part_11 + gen_part_4 
		
		
			part2 = MIMEText(html, 'html')
			msg.attach(part2)
			
			# Check Server Connection
			try:
				print "server checking..............."
				server = smtplib.SMTP('10.100.1.209')
			#   server.sendmail(from_mailid,party_rec.email,msg.as_string())
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
			#   server.sendmail(from_mailid,party_rec.email,msg.as_string())
				server.sendmail(email_from,email_to+email_cc,msg.as_string())
				print " Message............................",msg.as_string()
				print "Successfully sent email ---------------------To.........>>" 
			except Exception:
				pass
				return True
	
kg_category_mail()
