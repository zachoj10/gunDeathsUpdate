# gunDeaths.py

from BeautifulSoup import BeautifulSoup
import requests
import time
from datetime import date, timedelta, datetime	
import psycopg2
import sys
import os
import pytz

yesterdayTotal = 0
todayTotal = 0
weeklyTotal = 0
yearlyTotal = 0

URL = 'http://www.gunviolencearchive.org/reports/number-of-gun-deaths'



DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASS = os.environ.get('DATABASE_PASS')
DATABASE_NAME = os.environ.get('DATABASE_NAME')

LOCAL_TIME = os.environ.get('LOCAL_TIME')
LOCAL = pytz.timezone('{0}'.format(LOCAL_TIME))
TZ=pytz.timezone('America/New_York')


def connectToDB(dbname, user, password, host='localhost'):
	#try:
		conn = psycopg2.connect("dbname={0} user={1} host={2} password={3}".format(dbname, user, host, password))
		print ('Connection successful!')
		return conn
	# except:
	# 	print ('Unable to connect to database {0}'.format(dbname))
	# 	sys.exit(0)


def insertToDB(conn, cur, incident):
	try:
		cur.execute("INSERT INTO incidents VALUES (%(date)s, %(state)s, %(city)s, %(address)s, %(killed)s, %(injured)s, %(incidentURL)s) ", incident)
		conn.commit()
		return True
	
	except:
		conn.rollback()

def getToday(conn, cur):
	todayDate = datetime.now()
	todayDate = LOCAL.localize(todayDate)
	todayDate = todayDate.astimezone(TZ).date()
	print(todayDate)
	cur.execute("SELECT * FROM incidents WHERE date = '{0}';".format(todayDate))
	
	dailyKilled = 0
	dailyTotal = 0
	for incident in cur.fetchall():
		dailyKilled += incident[4]
		dailyTotal += 1

	print('Today\'s Incident Total: {0}'.format(dailyTotal))
	print('Today\'s Death Total: {0}'.format(dailyKilled))

def getYesterday(conn, cur):
	todayDate = datetime.now()
	todayDate = LOCAL.localize(todayDate)
	todayDate = todayDate.astimezone(TZ).date()
	yesterdayDate = todayDate - timedelta(1)
	cur.execute("SELECT * FROM incidents WHERE date = '{0}';".format(yesterdayDate))
	
	dailyKilled = 0
	dailyTotal = 0
	for incident in cur.fetchall():
		dailyKilled += incident[4]
		dailyTotal += 1

	print('Yesterday\'s Incident Total: {0}'.format(dailyTotal))
	print('Yesterday\'s Death Total: {0}'.format(dailyKilled))

def getWTD(conn, cur):
	todayDate = datetime.now()
	todayDate = LOCAL.localize(todayDate)
	todayDate = todayDate.astimezone(TZ).date()
	weekday = todayDate.weekday()
	weekStart = todayDate - timedelta(weekday)
	cur.execute("SELECT * FROM incidents WHERE date >= '{0}';".format(weekStart))
	
	dailyKilled = 0
	dailyTotal = 0
	for incident in cur.fetchall():
		dailyKilled += incident[4]
		dailyTotal += 1

	print('Week\'s Incident Total: {0}'.format(dailyTotal))
	print('Week\'s Death Total: {0}'.format(dailyKilled))

def getMTD(conn, cur):
	todayDate = datetime.now()
	todayDate = LOCAL.localize(todayDate)
	todayDate = todayDate.astimezone(TZ).date()
	monthDay = todayDate.day
	monthStart = todayDate - timedelta(monthDay)

	cur.execute("SELECT * FROM incidents WHERE date > '{0}';".format(monthStart))
	
	dailyKilled = 0
	dailyTotal = 0
	for incident in cur.fetchall():
		dailyKilled += incident[4]
		dailyTotal += 1

	print('Months\'s Incident Total: {0}'.format(dailyTotal))
	print('Months\'s Death Total: {0}'.format(dailyKilled))


def getYTD(conn, cur):
	todayDate = datetime.now()
	todayDate = LOCAL.localize(todayDate)
	todayDate = todayDate.astimezone(TZ).date()
	year = todayDate.year
	newYear = date(year, 1, 1)

	cur.execute("SELECT * FROM incidents WHERE date >= '{0}';".format(newYear))
	
	dailyKilled = 0
	dailyTotal = 0
	for incident in cur.fetchall():
		dailyKilled += incident[4]
		dailyTotal += 1

	print('Year\'s Incident Total: {0}'.format(dailyTotal))
	print('Year\'s Death Total: {0}'.format(dailyKilled))

def populateDB(conn, cur, numpages):
	urllist = ['http://www.gunviolencearchive.org/reports/number-of-gun-deaths']
	for i in range(1, numpages + 1):
		urllist.append('http://www.gunviolencearchive.org/reports/number-of-gun-deaths?page={0}'.format(i))

	printed = False
	existingPrinted = False
	
	for url in urllist:
		page = requests.get(url)
		soup = BeautifulSoup(page.text)

		rows = soup.findAll('tr')

		for row in rows[1:]:
				date = time.strptime(row.contents[0].text, "%B %d, %Y")
				date = time.strftime("%Y-%m-%d", date)
				date = datetime.strptime(date, "%Y-%m-%d")

				try:
					url = row.find('li', {'class' : '0 first'})
					url = url.find('a').get('href')
				except: 
					url = row.find('li', {'class' : '0 first last'})
					url = url.find('a').get('href')

				incident = {'date': date,
							'state': row.contents[1].text,
							'city': row.contents[2].text,
							'address': row.contents[3].text, 
							'killed': int(row.contents[4].text),
							'injured': int(row.contents[5].text),
							'incidentURL':url}

				cur = conn.cursor()
				result = insertToDB(conn, cur, incident)
				if result and not printed:
					printed = True
					print('Added record to database')
				elif not result and not existingPrinted:
					existingPrinted = True
					print('Already in database')



def main():

	#conn = connectToDB('gunincidents', 'Zach', 'Zach9125', 'gunincidents.ctj67xhqvtly.us-west-2.rds.amazonaws.com:5432')
	conn = connectToDB(DATABASE_NAME, DATABASE_USER, DATABASE_PASS, DATABASE_HOST)

	cur = conn.cursor()
	populateDB(conn, cur, 11)
	

	getToday(conn, cur)
	getYesterday(conn, cur)
	getWTD(conn, cur)
	getMTD(conn, cur)
	# getYTD(conn, cur)

if __name__ == "__main__":
	main()


