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
from email.Utils import COMMASPACE, formatdate
import re
import smtplib
import netsvc
import time, datetime
from datetime import *
import calendar
import datetime
import unicodedata
from dateutil.relativedelta import relativedelta 


class daily_scheduler_mail(osv.osv):

	_name = "daily.scheduler.mail"
	_description = "Daily Scheduler"

	def daily_scheduler_alert(self,cr,uid,ids=0,context=None):
				
		cr.execute('select id,sch_name,name,subject from kg_mail_settings where sch_type=%s and active=%s and state=%s and sch_interval=%s',('scheduler',True,'validate','daily'))
		sch_list = cr.fetchall()
		if sch_list:			
			for item in sch_list:
				
				email_from = []
				email_to = []
				email_cc = []
				msg = ''
				body_data = ''
				msg = MIMEMultipart('alternative')	
				sch_name = item[1]
				
				## Mail Body Part
				
				unicodedata.normalize('NFKD', sch_name).encode('ascii','ignore')
				print "Scheduler Name ----------->> ", sch_name
				cr.execute('select all_daily_auto_scheduler_mails(%s)',(sch_name,))
				body_data = cr.fetchall()
				body_data = body_data[0][0]

				if body_data:
									
					## Prepare Mail Details - Start
									
					msg['Subject'] = item[3]				
					email_from = item[2]				
					unicodedata.normalize('NFKD', email_from).encode('ascii','ignore')
					mail_line_id = self.pool.get('kg.mail.settings.line').search(cr,uid,[('line_entry','=',item[0])])
					for mail_id in mail_line_id:
						mail_line_rec = self.pool.get('kg.mail.settings.line').browse(cr,uid,mail_id)
						if mail_line_rec.to_address:
							email_to.append(mail_line_rec.mail_id)
						if mail_line_rec.cc_address:
							email_cc.append(mail_line_rec.mail_id)
					if email_to:
						msg['To'] = ','.join(email_to)
						msg['From'] = email_from
					if email_cc:
						msg['Cc'] = ','.join(email_cc)				
								
					part2 = MIMEText(body_data, 'html')
					msg.attach(part2)
				
					# Check Server Connection					
					try:
						server = smtplib.SMTP('10.100.1.209')
						server.sendmail(email_from,email_to+email_cc,msg.as_string())
						print "Successfully sent email ---------------------To.........>>" 
					except Exception:
						print "Unable to sent email --------------------->>" 
						return True
				else:
					print "No body content"
				
		else:
			print "No Scheduler List"

		return True
		
daily_scheduler_mail()
