import frappe
import pymssql

from utils import send_mail
from frappe.utils import get_datetime, time_diff_in_hours

def sync_db():
    """
        Sync Data from MS-SQL database to MariaDB
    """
    try:
        from helpdesk.doctype.mssql_configuration.mssql_configuration import get_mssql_config

        config = get_mssql_config()
        server = config.get("server")
        port = config.get("port")
        user = config.get("user")
        password = config.get("password")
        database = config.get("database")

        if not (server and port and user and password and database):
            raise Exception("Please Configure MS-SQL Configuration First")
        else:
            with pymssql.connect(server, user, password, database) as cn:
                with cn.cursor(as_dict) as cursor:
                    query = ""
                    cursor.execute(query)
                    for row in cursor:
                        # save user details and roles
                        pass
    except Exception, e:
        # create scheduler log
        print e
        pass

def ticket_escallation():
    """
        Escalate Pending Support Tickets to higher authority
    """
    query = """ SELECT * FROM `tabTicket Escalation History` WHERE status<>'closed' ORDER BY name"""
    records = frappe.db.sql(query, as_dict=True)

    not_assigned = []

    for record in records:
        # check if ticket is assigned or not
        if not record.get("is_assigned"):
            # send reminder mail to administrator after certain intervals
            opening_date = record.get("opening_date")
            opening_time = record.get("opening_time")
            datetime_str = "{date} {time}".format(date=opening_date, time=opening_time)
            now = str(get_datetime().now())

            if time_diff_in_hours(now, datetime_str) >= 2:
                not_assigned.append(record.get("ticket_id"))
            # notify administrator regarding open tickets
            if not_assigned:
                args = get_open_tickets_details("Administrator", not_assigned)
                send_mail(args, "[HelpDesk][Open Tickets] HelpDesk Notifications")
        else:
            # escalate ticket to higher authority
            # escalate_ticket()
            pass

# idx, ticket id, subject, department, opening date, opening time
def get_open_tickets_details(user, tkts_list):
    """get open tickets details"""
    args = {}

    tickets = {
        "head": ["SR", "Ticket ID", "Subject", "Department", "Opening Date", "Opening Time"],
        "total": len(tkts_list)
    }
    idx = 1
    for tkt_id in tkts_list:
        doc = frappe.get_doc("Issue", tkt_id)
        tickets.update({
            idx: [doc.name, doc.subject, doc.department, str(doc.opening_date), str(doc.opening_time)]
        })

    args.update({
        "user": user,
        "email": frappe.db.get_value("User", user, "email"),
        "action": "open_tickets",
        "tickets_details": build_table(tickets),
    })

    return args

def build_table(data):
    """
    build html table
    inupt: data:dict
    format: {
                "head":["SR","HEADER1", "HEADET2"],
                total: 5                            #total number of rows
                1: [1, "col1", "col2"]              # first row
                2: [2, "col1", "col2"]              # second row
            }
    """
    # building table head
    th = "".join(["<th>%s</th>"%(th) for th in data.get("head")])
    thead = "<thead><tr align='center'>{th}</tr><thead>".format(th=th)
    records = ""

    order = data.get("order")
    for idx in xrange(1, data.get("total") + 1):
        td = "<td align='center' >%s</td>"%(idx)
        td += "".join(["<td align='center'>%s</td>"%(td) for td in data.get(idx)])
        tr = "<tr>%s</tr>"%(td)
        records += tr

    tbody = "<tbody>%s<tbody>"%(records)
    table = """<table border="1px" style="border-collapse: collapse;">{thead}{tbody}</table>""".format(thead=thead, tbody=tbody)
    
    return table