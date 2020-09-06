import math
import datetime
import time

def calculateDebt(startYear,startMonth,startDay,baseDebt,perSecondDebt,yearPop,monthPop,dayPop,basePop,perSecondPop):
    startdate = datetime.date(startYear, startMonth-1 if startMonth > 1 else 1, startDay)
    startPopdate = datetime.date(yearPop, monthPop-1 if monthPop > 1 else 1, dayPop)

    startdate = int(time.mktime(startdate.timetuple()))
    startPopdate = int(time.mktime(startPopdate.timetuple()))


    perTenthDebt = perSecondDebt/10
    today = int(time.time())
    elapsedTenths=math.ceil((today-startdate)/100)

    currentDebt=(elapsedTenths*perTenthDebt)+baseDebt

    elapsedTenths=math.ceil((today-startPopdate)/100)

    return currentDebt

class DebtCalc:

    def __init__(self):
      a = datetime.datetime.now().date()
      self.debt = calculateDebt(a.year,a.month,a.day,21599377345082.36,31610.2,2011,6,6,311496761,0.076923076923077) 
