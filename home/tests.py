from django.test import TestCase
import requests
from datetime import date
from workalendar.america import Brazil

start = date(2023,1,1)
end = date(2023,12,31)
cal = Brazil()
workdays = cal.get_working_days_delta(start,end)

taxa_selic_diaria = 0.050788/100  # taxa diária atual (17/03/2023)
taxa_selic_anual = (1 + taxa_selic_diaria) ** workdays - 1
print(f"Taxa Selic anual: {taxa_selic_anual:.2%}")

