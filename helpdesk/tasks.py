import frappe
import pymssql

def sync_db():
    """
        Sync Data from MS-SQL database to MariaDB
    """
    try:
        from helpdesk.helpdesk.doctype.mssql_configuration import get_mssql_config

        config = get_mssql_config()
        server = config.get("server")
        port = config.get("port")
        username = config.get("user")
        password = config.get("password")

        if not (server and port and user and password):
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
        pass
