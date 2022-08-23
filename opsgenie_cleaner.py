#!/usr/bin/python3
# -*- coding: utf-8 -*-
from time import sleep
import json
import requests
import re
import csv
import argparse

# Empty Opsgenie Api Key variable that we introduce using argparse.
opsgenie_api_key = ''

# Time to Sleep.
nap_time = 30

# Set to 0 the number of items in the list.
number_of_items_inside_list = 0

"""
  Function: handler()
  Input: API_KEY from Opsgenie.
  Output: A file called --> all_ids_backup_temp.txt that contains all IDs of the alerts to be deleted.
  Descr: Small Python code to remove all alerts closed from Opsgenie.
"""

# Waiting 30 seconds for every requests... due a 409 Too Many Requests response from Opsgenie API. # https://docs.opsgenie.com/docs/api-rate-limiting
def take_a_nap_30_seconds(nap_time):
  print("Waiting 30 seconds... due a 409 Too Many Requests")
  sleep(nap_time)

# Check the number of alerts closed.
def get_number_alerts_opsgenie(opsgenie_query_get_number_of_alerts_closed, headers):
  opsgenie_response_alerts_counts_closed = requests.get(opsgenie_query_get_number_of_alerts_closed, headers=headers)
  jsonResponse_count = json.loads(opsgenie_response_alerts_counts_closed.text)
  return jsonResponse_count

# We use LIST-ALERTS method -->  https://docs.opsgenie.com/docs/alert-api#list-alerts
def get_list_alerts_opsgenie(opsgenie_query_list_all_alerts_closed, headers):
  opsgenie_response_list_all_alerts = requests.get(opsgenie_query_list_all_alerts_closed, headers=headers)
  return opsgenie_response_list_all_alerts

# Load JSON response and iterate/loop to Parse JSON with id.
def create_list_of_ids_opsgenie(get_list_alerts_opsgenie_response):
  list_of_ids = []
  jsonResponse = json.loads(get_list_alerts_opsgenie_response.text)
  for every_alert in jsonResponse['data']:
    list_of_ids.append(every_alert['id'])
  return list_of_ids

# We are going to READ one by one the LIST that we created before with all IDs and DELETE it.
def delete_alerts_opsgenie(create_list_of_ids_opsgenie_response, headers, region_to_use):
  if region_to_use == 'EU':
    for id in create_list_of_ids_opsgenie_response:
      print(id)
      deleting_id = requests.delete(f'https://api.eu.opsgenie.com/v2/alerts/{(id)}?identifierType=id', headers=headers)
      print(deleting_id.text)
  else:
    for id in create_list_of_ids_opsgenie_response:
      print(id)
      deleting_id = requests.delete(f'https://api.opsgenie.com/v2/alerts/{(id)}?identifierType=id', headers=headers)
      print(deleting_id.text)


####################################
####### OPSGENIE_CLEANER.PY ########
####################################

# Initialize argparse put a welcome message and define the arguments.
parser = argparse.ArgumentParser(description='Welcome to Opsgenie Cleaner!')
parser.add_argument("-k", "--key", dest='key', required=True, help="To run this script provide token from your Opsgenie account")
parser.add_argument("-r", "--region", dest='region', required=True, help="Choose EU or GLOBAL if you are using --> api.eu.opsgenie.com or api.opsgenie.com")
args = parser.parse_args()

# Define URL to later do a request type GET. There is a limitation from the Opsgenie API. Is limited to return only max 100 alerts --> https://docs.opsgenie.com/docs/alert-api#list-alerts

# EU
if args.region == 'EU':
  opsgenie_query_list_all_alerts_closed = 'https://api.eu.opsgenie.com/v2/alerts?query=status%3Aclosed&limit=100&order=asc' # https://www.w3schools.com/tags/ref_urlencode.asp  (%3A)
  opsgenie_query_get_number_of_alerts_closed = 'https://api.eu.opsgenie.com/v2/alerts/count?query=status%3Aclosed' #  (%3A)
  region_to_use = args.region
  print("------------------------------------------------------------------------------------------------------------------------------------")
  print("You selected EU region, using URLs")
  print("------------------------------------------------------------------------------------------------------------------------------------")
else:
  # GLOBAL.
  opsgenie_query_list_all_alerts_closed = 'https://api.opsgenie.com/v2/alerts?query=status%3Aclosed&limit=100&order=asc' # https://www.w3schools.com/tags/ref_urlencode.asp  (%3A)
  opsgenie_query_get_number_of_alerts_closed = 'https://api.opsgenie.com/v2/alerts/count?query=status%3Aclosed' #  (%3A)
  region_to_use = args.region
  print("------------------------------------------------------------------------------------------------------------------------------------")
  print("You selected GLOBAL region, using URLs")
  print("------------------------------------------------------------------------------------------------------------------------------------")


# Define Opsgenie Api Key variable.
opsgenie_api_key = args.key
print("------------------------------------------------------------------------------------------------------------------------------------")
print(f"You set the following api-key --> {opsgenie_api_key}")
print("------------------------------------------------------------------------------------------------------------------------------------")

# HTTPS HEADERS.
headers = {
  'Content-Type':'application/json',
  'Authorization':f'GenieKey {(opsgenie_api_key)}'
}

# Check the number of alerts closed.
try:
  get_number_alerts_opsgenie_response = get_number_alerts_opsgenie(opsgenie_query_get_number_of_alerts_closed, headers)
  print("------------------------------------------------------------------------------------------------------------------------------------")
  print(f"You have {(get_number_alerts_opsgenie_response['data']['count'])} closed alerts")
  print("------------------------------------------------------------------------------------------------------------------------------------")

  # Waiting 30 seconds for every requests... due a 409 Too Many Requests response from Opsgenie API. # https://docs.opsgenie.com/docs/api-rate-limiting
  take_a_nap_30_seconds(nap_time)
  print("------------------------------------------------------------------------------------------------------------------------------------")
  print("INFO --> https://community.atlassian.com/t5/Opsgenie-questions/Error-429-Too-Many-Requests-to-Opsgenie-Integration-API/qaq-p/1966186")
  print("------------------------------------------------------------------------------------------------------------------------------------")
  print("------------------------------------------------------------------------------------------------------------------------------------")
  print("INFO --> Opsgenie API GET to obtain 100 alerts (max) and save the header called X-Paging-Next to know next pages with offset")
  print("------------------------------------------------------------------------------------------------------------------------------------")
except:
  print("------------------------------------------------------------------------------------------------------------------------------------")
  print("INFO --> Please check your api-key something is wrong ... cannot connect to Opsgenie")
  print("------------------------------------------------------------------------------------------------------------------------------------")
  exit()

# We are going to GET the alerts using LIST-ALERTS method -->  https://docs.opsgenie.com/docs/alert-api#list-alert
get_list_alerts_opsgenie_response = get_list_alerts_opsgenie(opsgenie_query_list_all_alerts_closed, headers)

# Load JSON response and iterate/loop to create a LIST with IDS of the alerts.
create_list_of_ids_opsgenie_response = create_list_of_ids_opsgenie(get_list_alerts_opsgenie_response)

# Retrieve the HTTPS response to get the 'X-Paging-Next' header to know offset and use it for next requests, if we don't receive nothing the return is "None".
nextUrl = get_list_alerts_opsgenie_response.headers.get("X-Paging-Next", None)

# While nextUrl variable exists and it has the header called "X-Paging-Next". If is "None" only delete this first 100 alerts.
while nextUrl is not None:
  while number_of_items_inside_list < 19900 and nextUrl is not None:
    take_a_nap_30_seconds(nap_time)
    get_list_alerts_opsgenie_response = get_list_alerts_opsgenie(nextUrl, headers)

    # += adds another value with the variable's value and assigns the new value to the variable --> https://stackoverflow.com/questions/4841436/what-exactly-does-do
    create_list_of_ids_opsgenie_response += create_list_of_ids_opsgenie(get_list_alerts_opsgenie_response)

    # Set the new nextUrl with the new offset to next request.
    nextUrl = get_list_alerts_opsgenie_response.headers.get("X-Paging-Next", None)
    print(f"The next URL to check is --> {nextUrl}")

    # Check number of IDs to be deleted only in this iteration.
    number_of_items_inside_list = len(create_list_of_ids_opsgenie_response)
    print(f"The number of Alerts/IDs in this list is --> {(number_of_items_inside_list)}")

  # Writing the data TEMP with the first 1000 IDs into the file called all_ids_backup_temp.txt --> https://stackoverflow.com/questions/899103/writing-a-list-to-a-file-with-python-with-newlines
  print("------------------------------------------------------------------------------------------------------------------------------------")
  print("Writing data of ids in temporal file called --> all_ids_backup_temp.txt ")
  print("------------------------------------------------------------------------------------------------------------------------------------")
  with open('all_ids_backup_temp.txt', 'a') as f:
    for item in create_list_of_ids_opsgenie_response:
        f.write("%s\n" % item)

  # Empty the LIST and set the number of items to 0 again, print the result.
  create_list_of_ids_opsgenie_response = []
  number_of_items_inside_list = 0

# Writing the data into the file. # https://stackoverflow.com/questions/899103/writing-a-list-to-a-file-with-python-with-newlines
with open('all_ids_backup_temp.txt', 'a') as f:
  for item in create_list_of_ids_opsgenie_response:
      f.write("%s\n" % item)

# Delete all Alerts with all IDS reading the file instead of using the list of ids in memory --> Max 20.000 records. Is a HARD limit described here --> https://community.atlassian.com/t5/Opsgenie-questions/Opsgenie-Alert-API-422-Sum-of-offset-and-limit-should-be-lower/qaq-p/1576684
# print("Starting to delete all ids , reading from all_ids_backup_temp.txt file ... ")
# with open('all_ids_backup_temp.txt') as fp:
#   items = fp.readlines()
#   for item in items:
#     delete_alerts_opsgenie([item], headers, region_to_use)
