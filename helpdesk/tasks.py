import frappe
import pymssql

from datetime import timedelta
from utils import send_mail, create_scheduler_log
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
                    query = "SELECT * FROM employee"
                    cursor.execute(query)
                    for row in cursor:
                        # TODO save user details and roles
                        pass
    except Exception, e:
        import traceback
        error = e.message
        _traceback = traceback.print_exc()
        create_scheduler_log(error, _traceback, method="sync_db")

def ticket_escallation():
    """
        Escalate Pending Support Tickets to higher authority
    """
    query = """ SELECT * FROM `tabTicket Escalation History` WHERE status NOT IN ('Closed','Deleted') ORDER BY name"""
    records = frappe.db.sql(query, as_dict=True)

    if not records:
        return
    else:
        open_tickets = []

        # get escalation settings records
        doctype = "Ticket Escalation Settings"
        docname = frappe.db.get_value("Ticket Escalation Settings",{"is_default":1}, "name")
        
        if not docname:
            frappe.throw("Default Escalation settings not found")
        
        esc_setting = frappe.get_doc(doctype, docname)

        assigned_tickets = [record for record in records if record.get("is_assigned")]
        not_assigned_tickets = [record for record in records if not record.get("is_assigned")]

        open_tickets = check_for_open_support_tickets(not_assigned_tickets, esc_setting)

        if open_tickets:
            args = get_open_tickets_details("Administrator", open_tickets)
            send_mail(args, "[HelpDesk][Open Tickets] HelpDesk Notifications")

        check_and_escalate_assigned_tickets(assigned_tickets, esc_setting)

def get_open_tickets_details(user, tkts_list):
    """get open tickets details"""
    from utils import build_table
    args = {}

    tickets = {
        "head": ["SR", "Ticket ID", "Subject", "Department", "Opening Date", "Opening Time"],
        "total": len(tkts_list)
    }
    idx = 1
    for tkt_id in tkts_list:
        doc = frappe.get_doc("Issue", tkt_id)
        tickets.update({
            idx: [idx, doc.name, doc.subject, doc.department, str(doc.opening_date), str(doc.opening_time)]
        })
        idx += 1

    args.update({
        "user": user,
        "email": frappe.db.get_value("User", user, "email"),
        "action": "open_tickets",
        "tickets_details": build_table(tickets),
    })

    return args

def check_for_open_support_tickets(records, esc_setting):
    open_tickets = []
    time = 0

    for record in records:
        opening_date = record.get("opening_date")
        opening_time = record.get("opening_time")
        datetime_str = "{date} {time}".format(date=opening_date, time=opening_time)
        now = str(get_datetime().now())
        
        time = get_time_difference(esc_setting)
        
        if time_diff_in_hours(now, datetime_str) >= time or 2:
            open_tickets.append(record.get("ticket_id"))

    return open_tickets

def check_and_escalate_assigned_tickets(records, esc_setting):
    time = 0
    rec_cant_be_escalate = {}

    for record in records:
        datetime_str = record.get("assigned_on")
        now = str(get_datetime().now())
        time = get_time_difference(esc_setting, record.get("current_role")) or 2

        if time_diff_in_hours(now, datetime_str) >= time:
            ch_entry = esc_setting.escalation_hierarchy
            if record.current_role in [ch.role for ch in ch_entry[:2]]:
                key = frappe.db.get_value("Issue", record.get("ticket_id"), "department")
                val = rec_cant_be_escalate.get("department").append(record) if rec_cant_be_escalate.get("department") else [record]
                rec_cant_be_escalate.update({
                    key: val,
                })
            else:
                escalate_ticket_to_higher_authority(esc_setting, record)

    if rec_cant_be_escalate:
        args = get_tickets_details_that_cant_be_escalate(rec_cant_be_escalate)
        for dept_head, mail_args in args.iteritems():
            send_mail(mail_args, "[HelpDesk][Open Tickets] HelpDesk Notifications")


def get_time_difference(esc_setting, role="Administrator"):
    """checking the time limit for perticuler role"""
    roles = [ch.role for ch in esc_setting.escalation_hierarchy]
    ch_entry = esc_setting.escalation_hierarchy
    if not ch_entry:
        frappe.throw("Invalid Escalation Settings Records")
    elif role == "Administrator" and ch_entry[0].role != "Administrator":
        return 2
    elif "Administrator" and ch_entry[0].role == "Administrator":
        return ch_entry[0].time
    elif role not in [ch.role for ch in esc_setting.escalation_hierarchy]:
        frappe.throw("Invalid Role")
    else:
        time = [ch.time for ch in esc_setting.escalation_hierarchy if ch.role == role] or 2
        return time


def escalate_ticket_to_higher_authority(esc_setting, record):
    """
        TODO Escalate ticket to higher authority
    """
    from utils import get_users_email_ids

    prev_role = record.get("current_role")
    prev_owner = record.get("current_owner")

    query = """ SELECT idx, role, time, parent FROM `tabTicket Escalation Settings Record` WHERE 
                idx=(SELECT idx FROM `tabTicket Escalation Settings Record`
                WHERE parent='{parent}' AND role='{role}')-1 and parent='{parent}'""".format(
                    parent=esc_setting.name,
                    role=record.get("current_role")
                )
    higher_auth = frappe.db.sql(query, as_dict=True)[0]
        
    if not higher_auth:
        frappe.throw("could not find higher role in escalation settings")
    else:
        user = None
        next_role = higher_auth.get("role")
        time = higher_auth.get("time")
        idx = higher_auth.get("idx")

        # check if department wise escalation is enabled
        is_dept_escalation = True if esc_setting.escalation_hierarchy[idx-1].is_dept_escalation else False
        result = select_user_to_escalate_ticket(next_role, is_dept_escalation, record)
        
        user = result.get("user")
        next_role = result.get("role") if result.get("role") else next_role
        # check if todo is created for the user if yes then update else create new
        create_update_todo_for_user(user, next_role, time, record.get("ticket_id"), prev_owner)
        # notify user regarding ticket escalation
        args = {
            "user": "User",
            "email": get_users_email_ids([prev_owner, user]),
            "action": "escalate_ticket",
            "issue": frappe.get_doc("Issue", record.get("ticket_id")),
            "esc": {
                "prev_owner": prev_owner,
                "prev_role": prev_role,
                "current_owner": user,
                "current_role": next_role
            }
        }
        send_mail(args, "[HelpDesk][Ticket Escalation] HelpDesk Notifications")

def get_tickets_details_that_cant_be_escalate(records):
    """get tickets details that cant be escalate"""
    from utils import build_table, get_dept_head_user

    args = {}
    for dept,record in records.iteritems():
        tickets = {
            "head": ["SR", "Ticket ID", "Subject", "Department", "Opening Date & Time", "Assigned To", "Assigned On", "Ticket Status"],
            "total": len(record)
        }
       
        idx = 1

        for tkt in record:
            doc = frappe.get_doc("Issue", tkt.get("ticket_id"))
            datetime_str = "{date} {time}".format(date=doc.opening_date, time=doc.opening_time)
            tickets.update({
                idx: [idx, doc.name, doc.subject, doc.department, datetime_str, tkt.get("current_owner"), tkt.get("assigned_on"), doc.status]
            })

        dept_head = get_dept_head_user(dept)

        args.update({
            dept_head:{
                "user": dept_head,
                "email": frappe.db.get_value("User", dept_head, "email"),
                "action": "cant_escalate_tickets",
                "tickets_details": build_table(tickets),
            }
        })
    return args


def get_department_head_user(dept):
    query = """ SELECT name FROM `tabUser` WHERE name IN (SELECT parent FROM tabUserRole 
                WHERE role='Department Head') AND department='%s'"""%(dept)
    user = frappe.db.sql(query, as_dict=True)[0]
    return user.get("name")

def create_update_todo_for_user(user, role, time, issue, prev_owner):
    desc = "[Escalated][Support Ticket]\n"
    desc += "Support Ticket : %s has been escalated to you"%(issue)

    todo = None
    filters = {
        "reference_type": "Issue",
        "reference_name": issue,
        "owner": user
    }
    docname = frappe.db.get_value("ToDo", filters, "name")
    is_new = False
    if not todo:
        todo = frappe.new_doc("ToDo")
        is_new = True
    else:
        todo = frappe.get_doc("ToDo", docname)

    filters.update({"owner":prev_owner})
    dn = frappe.db.get_value("ToDo", filters, "name")
    if dn:
        prev_todo = frappe.get_doc("ToDo", dn)
        prev_todo.status = "Closed"
        prev_todo.description = "Ticket Escalated to {0}\n{1}".format(role, prev_todo.description)
        prev_todo.save(ignore_permissions=True)

    todo.description = "%s\n\n%s"%(desc, todo.description) if todo.description else desc
    todo.status = "Open"
    todo.owner = user
    todo.reference_type = "Issue"
    todo.reference_name = issue
    todo.role = role
    todo.assigned_by = "Administrator"
    # TODO check-> assign due date, priority
    due_date = get_datetime().now() + timedelta(hours=time)
    todo.date = due_date.date()
    todo.due_time = due_date.time().strftime("%H:%M:%S")
    todo.save(ignore_permissions=True)

def select_user_to_escalate_ticket(next_role, is_dept_escalation, record):
    """
        select the user to whom the ticket should be escalated
        1:  check the current_owner todo get assigned_by and check the role
            if roles of todo assigned by and role of next_role are same assign ticket to 
            assigned_by user
        2:  if not then search the user from role if is_dept_escalation enabled get only those
            user which belongs to said department if is_dept_escalation is disabled then get any
            user belonging to next_role

    """
    current_owner = record.get("current_owner")
    current_role = record.get("current_role")
    issue = record.get("ticket_id")
    department = frappe.db.get_value("Issue", record.get("ticket_id"), "department")

    filters = {
        "owner": current_owner,
        "reference_type": "Issue",
        "reference_name": issue
    }

    todo = frappe.db.get_value("ToDo", filters, ["assigned_by", "role"], as_dict=True)
    # TODO handle multiple todos
    if todo and todo.get("role") == next_role:
        return { "user":todo.get("assigned_by") }
    else:
        # return get_user_from_role(next_role, department=department, is_department=is_dept_escalation)
        user = get_user_from_role(next_role, department=department, is_department=is_dept_escalation)
        if not user:
            return {
                    "user": todo.assigned_by,
                    "role": todo.role
                }
        return { "user":user }

def get_user_from_role(role, department=None, is_department=False):
    query = """ SELECT
                    usr.name
                FROM
                    tabUser AS usr
                LEFT JOIN
                    tabUserRole AS urole
                ON
                    usr.name=urole.parent
                WHERE
                    urole.role='%s'
                AND urole.role<>'Administrator'
            """%(role)
    
    if is_department:
       query = "{query} AND usr.department='{dept}'".format(query=query, dept=department)

    users = frappe.db.sql(query, as_dict=True)
    if not users:
        frappe.throw("Can not find any users to whom ticket can be escalate")
    elif len(users) == 1:
        return users[0].get("name")
    else:
        #TODO multiple user how to select ?
        return None