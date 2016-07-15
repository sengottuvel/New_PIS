##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'SO Advance',
    'version': '0.1',
    'author': 'Sangeetha',
    'category': 'PO Advance',
    'images': ['images/purchase_requisitions.jpeg'],
    'website': 'http://www.openerp.com',
    'description': """ This module is used to track advance details against PO and SO """,
    'depends' : ['base','kg_po_grn','kg_general_grn','account','kg_service_order'],
    'depends' : ['base','kg_po_grn','kg_general_grn','account','kg_service_order'],
    'data': ['kg_so_advance_view.xml'],
    'auto_install': False,
    'installable': True,
}

