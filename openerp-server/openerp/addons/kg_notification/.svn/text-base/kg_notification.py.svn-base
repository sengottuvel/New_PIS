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


class kg_notification(osv.osv):

	_name = "kg.notification"
	_description = "KG Notification"


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
			if mail_form_rec.doc_name.model == 'kg.notification':
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
		
		
		sql = """select id,INITCAP(login) as user 
				from res_users 
				 where active='t' and id != 1 order by login"""
		
		
		gen_part_1 = ""
		gen_part_2 = ""
		gen_part_3 = ""
		gen_part_4 = ""
		di_tot = 0
		pi_tot = 0
		po_tot = 0
		grn1_tot = 0
		issue_tot = 0
		si_tot = 0
		gp_tot = 0
		total = 0
		so_tot = 0
		inv_tot = 0
		col_tot = 0
		cr.execute(sql)
		data = cr.dictfetchall()
		print "buyer_data...................", data
			
		if data:
			
			msg = ''
			msg = MIMEMultipart('alternative')
			msg['Subject'] = company_name.code + " : User Wise Entry Count For " " " + month + "-" + year + ""
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
						
						
						<h2><font color="#0033FF" text-align="center">"""+str(company_name.code)+""" : User Wise Entry Count For """ +str(month)+""" - """+ str(year) +""".</font></b></h2>
						<table border="1" style="border-collapse:collapse"> 
							<tr style="background-color:#FFB895;color:1F3399;">
							<th colspan='4'>S No</th>	
							
							<th colspan='4'>User</th>	
							<th colspan='4'>DI</th>	
							<th colspan='4'>PI</th>	
							<th colspan='4'>PO</th>	
							<th colspan='4'>GRN</th>	
							<th colspan='4'>Issue</th>	
							<th colspan='4'>SI</th>	
							<th colspan='4'>GP</th>	
							<th colspan='4'>SO</th>	
							<th colspan='4'>Invoice</th>	
							<th colspan='4'>Total</th>	
							
							
							</tr>
							
							"""
			ser_no =1
			for item in data:
				sql1 = """select count(*) as di_count from kg_depindent where state = 'approved' and create_uid=%s and ind_date >= '%s' and ind_date <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql1)
				data1 = cr.dictfetchall()
				a1 = data1[0]['di_count']
				di_tot +=a1
				
				sql2 = """select count(*) as pi_count from purchase_requisition where state = 'approved' and create_uid=%s and date_start >= '%s' and date_start <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql2)
				data2 = cr.dictfetchall()
				a2 = data2[0]['pi_count']
				pi_tot +=a2
				
				sql3 = """select count(*) as po_count from purchase_order where  (state = 'approved' or state = 'inv') and create_uid=%s and date_approve >= '%s' and date_approve <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql3)
				data3 = cr.dictfetchall()
				a3 = data3[0]['po_count']
				po_tot +=a3
				 
				sql4 = """select count(*) as po_grn_count from kg_po_grn where  (state = 'done' or state = 'inv') and create_uid=%s and grn_date >= '%s' and grn_date <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql4)
				data4 = cr.dictfetchall()
				po_grn = data4[0]['po_grn_count']
				
				sql5 = """select count(*) as gen_grn_count from kg_general_grn where  (state = 'done' or state = 'inv') and create_uid=%s and grn_date >= '%s' and grn_date <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql5)
				data5 = cr.dictfetchall()
				gen_grn = data5[0]['gen_grn_count']
				
				tot_grn = po_grn + gen_grn
				grn1_tot += tot_grn
				
				sql6 = """select count(*) as issue_count from kg_department_issue where state = 'done' and create_uid=%s and issue_date >= '%s' and issue_date <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql6)
				data6 = cr.dictfetchall()
				a6 = data6[0]['issue_count']
				issue_tot +=a6
				
				sql7 = """select count(*) as si_count from kg_service_indent where (state = 'done' or state='approved') and create_uid=%s and date >= '%s' and date <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql7)
				data7 = cr.dictfetchall()
				a7 = data7[0]['si_count']
				si_tot += a7
				
				sql10 = """select count(*) as gp_count from kg_gate_pass where (state = 'done') and create_uid=%s and date >= '%s' and date <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql10)
				data10 = cr.dictfetchall()
				a10 = data10[0]['gp_count']
				gp_tot += a10
				
				sql8 = """select count(*) as so_count from kg_service_order where (state = 'inv' or state='approved') and create_uid=%s and date >= '%s' and date <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql8)
				data8 = cr.dictfetchall()
				a8 = data8[0]['so_count']
				so_tot += a8
				
				sql9 = """select count(*) as pb_count from kg_purchase_invoice where state='approved' and create_uid=%s and invoice_date >= '%s' and invoice_date <= '%s'"""%(item['id'],first_day,last_day)
				cr.execute(sql9)
				data9 = cr.dictfetchall()
				a9 = data9[0]['pb_count']
				inv_tot += a9
				
				a11 = a1+a2+a3+tot_grn+a6+a7+a10+a8+a9
				col_tot += a11
				if a11 > 0:
					gen_part_2 += """<tr style="background-color:#FFE8DD;color:black;">
						<td colspan='4'>"""+str(ser_no)+"""</td>
						<td colspan='4'>"""+str(item['user'])+"""</td>
						<td colspan='4'>"""+str(a1)+"""</td>
						<td colspan='4'>"""+str(a2)+"""</td>
						<td colspan='4'>"""+str(a3)+"""</td>
						<td colspan='4'>"""+str(tot_grn)+"""</td>
						<td colspan='4'>"""+str(a6)+"""</td>
						<td colspan='4'>"""+str(a7)+"""</td>
						<td colspan='4'>"""+str(a10)+"""</td>
						<td colspan='4'>"""+str(a8)+"""</td>
						<td colspan='4'>"""+str(a9)+"""</td>
						<td colspan='4'><b>"""+str(a11)+"""</b></td>
					</tr> """
					ser_no += 1	
				else:
					pass	
			total = (col_tot)		
			gen_part_3 += """<tr style="background-color:#FFE8DD;color:black;">
					<td colspan='4' style="border-right: 1px solid #ffffff !important;">"""+str('')+"""</td>
					<td colspan='4'><b><font size="3" color="1F3399">"""+str('Grand Total')+"""</font></b></td>
					<td colspan='4'><b>"""+str(di_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(pi_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(po_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(grn1_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(issue_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(si_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(gp_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(so_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(inv_tot)+"""</b></td>
					<td colspan='4'><b>"""+str(total)+"""</b></td>
				</tr> """	
					
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
				
		

			html = gen_part_1 + gen_part_2 + gen_part_3 + gen_part_4
		
		
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
				
		
kg_notification()
