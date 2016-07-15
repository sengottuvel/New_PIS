## Employee Master Form Module Customization ##

import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import calendar
today = datetime.now()

class kg_employee(osv.osv):
	
	_name = 'hr.employee'	
	_inherit = 'hr.employee'
	#_rec_name = 'emp_code'
	
	_columns = {
	
	'emp_code': fields.char('Employee Code', size=128, required=True),	
	'join_date': fields.date('Joining Date', required=True),
	'payslip': fields.boolean('Appears On Payslip'),
	'department_id':fields.many2one('hr.department', 'Department', required=True),
	'round_off': fields.float('Current Month Balance', readonly=True),
	'last_month_bal': fields.float('Last Month Balance', readonly=True),
	'training_period': fields.selection([('one', '1 Month'),
										('two', '2 Months'),
										('three', '3 Months'),
										('four', '4 Months'),
										('five', '5 Months'),
										('six', '6 Months'),
										('seven', '7 Months'),
										('eight', '8 Months'),
										('nine', '9 Months'),
										('ten', '10 Months'),
										('ele', '11 Months'),
										('twe', '12 Months')], 'Training Period'),
										
	'probation': fields.selection([('one', '1 Month'),
										('two', '2 Months'),
										('three', '3 Months'),
										('four', '4 Months'),
										('five', '5 Months'),
										('six', '6 Months'),
										('seven', '7 Months'),
										('eight', '8 Months'),
										('nine', '9 Months'),
										('ten', '10 Months'),
										('ele', '11 Months'),
										('twe', '12 Months')], 'Probation Period'),
										
	'notice': fields.selection([('one', '1 Month'),
										('two', '2 Months'),
										('three', '3 Months'),
										('four', '4 Months'),
										('five', '5 Months'),
										('six', '6 Months'),
										('seven', '7 Months'),
										('eight', '8 Months'),
										('nine', '9 Months'),
										('ten', '10 Months'),
										('ele', '11 Months'),
										('twe', '12 Months')], 'Notice Period'),
										
	'confirm_date': fields.date('Date of Confirmation'),
	'salary_revision': fields.date('Salary Revision Due date'),
	'due_date': fields.date('Due Date'),
	'due_confirm': fields.date('Due date of Confirmation'),
	'cer_dob_date': fields.date('DOB Certificate', required=True),
	'father_name': fields.char('Father Name', size=128,required=True),
	'mother_name': fields.char('Mother Name', size=128, required=True),
	'father_occ': fields.char('Father Occupation',size=128),
	'mother_occ': fields.char('Mother Occupation', size=128),
	'ann_date': fields.date('Anniversary Date'),
	'wi_hus_name': fields.char('Wife/Husband Name', size=128),
	'present_add': fields.char('Present Address', size=256, required=True),
	'pre_city': fields.char('City', size=128, required=True),
	'pre_state': fields.many2one('res.country.state', 'State', required=True),
	'pre_country': fields.many2one('res.country', 'Country', required=True),
	'pin_code': fields.float('Postal Code', required=True),
	'pre_phone_no': fields.float('Phone Number', required=True),
	'same': fields.boolean('Same'),
	'permanent_add': fields.char('Permanent Address', size=256, required=True),
	'city': fields.char('City', size=128, required=True),
	'kg_state': fields.many2one('res.country.state', 'State', required=True),
	'country': fields.many2one('res.country', 'Country', required=True),
	'code': fields.float('Postal Code', required=True),
	'phone_no': fields.float('Phone Number', required=True),
	
	'ug_id': fields.char('Graduation/Degree', size=128),
	'ug_study': fields.char('Field Of Study', size=128),
	'ug_grade': fields.char('Grade', size=128),
	'ug_institute': fields.char('Institute', size=128),
	'ug_uni': fields.char('University', size=128),
	'ug_date': fields.date('Provision Date'),
	
	'pg_id': fields.char('Graduation/Degree', size=128),
	'study': fields.char('Field Of Study', size=128),
	'grade': fields.char('Grade', size=128),
	'institute': fields.char('Institute', size=128),
	'uni': fields.char('University', size=128),
	'pg_date': fields.date('Provision Date'),
	
	'work_exp': fields.char('Working Exp', size=128),
	'company': fields.char('Company name', size=128),
	'position': fields.char('position Title', size=128),
	'position_level': fields.char('Position Level', size=128),
	'spec': fields.char('Specialization', size=128),
	'indus': fields.char('Industry', size=128),
	'from_date': fields.date('From Date'),
	'to_date': fields.date('To Date'),
	
	'company1': fields.char('Company name', size=128),
	'position1': fields.char('position Title', size=128),
	'position_level1': fields.char('Position Level', size=128),
	'spec1': fields.char('Specialization', size=128),
	'indus1': fields.char('Industry', size=128),
	'from_date1': fields.date('From Date'),
	'to_date1': fields.date('To Date'),
	
	'pan': fields.char('Pan Card No', size=128),
	'mobile_no': fields.char('Mobile No', size=128),
	'blood': fields.char('Blood Group', size=128),
	'per_email': fields.char('Personal Email', size=128),
	'eme_contact_no': fields.char('Emergency Contact No', size=128),
	'con_person': fields.char('Contact Person', size=128),
	'relation': fields.char('Relationship', size=128),
	
	'week_off':fields.selection([('sun', 'SUNDAY'),
								('mon', 'MONDAY'),
								('tue', 'TUESDAY'),
								('wed', 'WEDNESDAY'),
								('thu', 'THURSDAY'),
								('fri', 'FRIDAY'),
								('sat', 'SATURDAY')], 'Week Off', required=True),
	'leave_type': fields.selection([('tut', 'TUTOR'),('emp', 'EMPLOYEE')], 'Leave Type', required=True),
	'location': fields.selection([('erd','ERODE'),
								('gop','GOPHI'),
								('coll','KG COLLEGE OF NURSING'),
								('kg','KGHOSPITAL'),
								('nam','NAMAKKAL'),
								('sal','SALEM'),
								('patti','SARAVANAMPATTI'),
								('thi','THIRUPUR')], 'Location', required=True),
	'shift_type': fields.many2one('kg.shift.time', 'Shift Type', required=True),
	'res_date': fields.date('Releaving Date'),
	'res_reason': fields.selection([('a', 'A'),('b', 'B'),('c', 'C'),('d','D')],'Reason for Leaving'),
	'thottam':fields.boolean('Thottam'),
		
	}
	
	_sql_constraints = [
		('code', 'unique(emp_code)', 'Employee code must be unique per Company !!'),
	]
	
	def _alldate_validation(self, cr, uid, ids, context=None):
		rec = self.browse(cr, uid, ids[0])
		print "rec...................", rec
		today = date.today()
		print "today................", type(today), today		
		join_date = datetime.strptime(rec.join_date,'%Y-%m-%d').date()
		print "rec.join_date...........", type(join_date), join_date
		if join_date > today:
			return False
		return True
		
	def _dob_validation(self, cr, uid, ids, context=None):
		rec = self.browse(cr, uid, ids[0])
		today = date.today()
		dob_date = datetime.strptime(rec.cer_dob_date,'%Y-%m-%d').date()
		if dob_date >= today:
			return False
		return True
		
		
	
	_constraints = [
        
        (_alldate_validation, 'Joining date should be less than current date !!',['join_date']),
        #(_dob_validation, 'Date of birth should be less than current date !!',['dob_date']),
        
        ]  
	
	_defaults = {
	
		'join_date' : fields.date.context_today,
		'payslip': True,

	}
	
	
kg_employee()


