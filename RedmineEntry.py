from redmine import Redmine
from datetime import datetime
import MySQLdb
import redmine
import json
import datetime
import sys
import getpass

#Config Goes Here
#=====================
REDMINE_URL="https://redmine.com/"
IMPORT_FOR_DAYS = 7
REDMINE_USERNAME = 'udham.singh'
REDMINE_PASSWORD= '*****'
DB_SERVER = 'localhost'
DB_USERNAME = 'root'
DB_PASSWORD = '*****'
DB_DATABASENAME = 'RedmineReport'
# Variable declarations goes here.

# Open database connection
db = MySQLdb.connect(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_DATABASENAME)

# Utility methods
#=================
def ImportTimeEntries(startDate, endDate):
    OFFSET = 0
    LIMIT = 100
    condition = True

    while condition:
        print "Getting Time Entries"
        time_entries = redmine.time_entry.all(offset=OFFSET, limit=LIMIT)

        for item in time_entries:
            redmine_entry_id = item.id
            user_name = item.user.name
            project_type = GetProjectType(item.project.name)
            project_name = item.project.name
            ticket_number = item.issue.id
            issue = redmine.issue.get(item.issue.id)
            ticket_description = issue.subject
            spent_date = item.spent_on
            created_date = item.created_on
            updated_date = item.updated_on
            spent_hours = item.hours
            billing_category = item.custom_fields[0].value
            activity = item.activity
            comments = item.comments
            # Save Values in database
            Save( redmine_entry_id, user_name, project_type, project_name, \
                            ticket_number, ticket_description, spent_date, created_date, \
                            updated_date, spent_hours, billing_category, activity, comments )
        print "All values saved in Database"

        OFFSET = OFFSET + 100
        LIMIT = LIMIT + 100
        condition = time_entries[len(time_entries)-1].spent_on > endDate
    return


def GetProjectType(projectName):
    if (projectName.find('QA') > -1):
        return 'QA'
    elif (projectName.find('DevBI') > -1):
        return 'DevBI'
    elif (projectName.find('Dev/BI') > -1):
        return 'DevBI'
    elif (projectName.find('BI') > -1):
        return 'DevBI'
    elif (projectName.find('Leaves') > -1):
        return 'Leave'
    elif (projectName.find('API') > -1):
        return 'API'
    elif (projectName.find('Induction') > -1):
        return 'Induction'
    elif (projectName.find('Mobile') > -1):
        return 'Mobility'
    elif (projectName.find('Mobility') > -1):
        return 'Mobility'
    else:
        return 'Organization'



def Save( redmine_entry_id, user_name, project_type, project_name, \
                ticket_number, ticket_description, spent_date, created_date, \
                updated_date, spent_hours, billing_category, activity, comments ):

    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO redmine_entries (redmine_entry_id, user_name, project_type, project_name, \
            ticket_number, ticket_description, spent_date, created_date, updated_date,  \
            spent_hours, billing_category, activity, comments) \
            VALUES ('%d', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%d', '%s','%s','%s' ) \
    	       ON DUPLICATE KEY UPDATE \
    	          updated_date = VALUES(updated_date), \
    	             billing_category = VALUES(billing_category), \
                     activity = VALUES(activity),\
                     comments = VALUES(comments),\
                     spent_hours = VALUES(spent_hours), \
                     spent_date =  VALUES(spent_date)" % \
                     (redmine_entry_id, user_name, project_type, project_name, \
                     ticket_number, ticket_description, spent_date, created_date, updated_date, \
                     spent_hours, billing_category, activity, comments)
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()
    return


# Script execution starts here.
#================================
#USERNAME = raw_input("-->Your redmine username: ")
#PASSWORD = getpass.getpass("-->Your redmine password: ")

redmine = Redmine(REDMINE_URL, username=REDMINE_USERNAME, password=REDMINE_PASSWORD, requests={'verify': False})
startDate = datetime.datetime.now().date()
endDate = (datetime.datetime.now() - datetime.timedelta(days=IMPORT_FOR_DAYS+1)).date()

ImportTimeEntries(startDate,endDate)
# disconnect from server
db.close()
