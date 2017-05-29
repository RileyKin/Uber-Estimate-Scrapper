# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of` the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from utils import create_uber_client
from utils import import_oauth2_credentials
from utils import import_start_end_points
from utils import fail_print
from utils import success_print
from utils import response_print
from utils import paragraph_print
from uber_rides.errors import ClientError
from uber_rides.errors import ServerError
import datetime
import time
import csv

'Definitions'
""""""""""""""""""
# uber pool "POOL"
SF_POOL_PRODUCT_ID = '26546650-e557-4a7b-86e7-6a3942445247'
OAKLAND_POOL_PRODUCT_ID = 'ee3ab307-e340-4406-b5ec-9f8c3b43075a'
# uberx "UberX"
SF_UBERX_PRODUCT_ID = 'a1111c8c-c720-46c3-8534-2fcdd730040d'
OAKLAND_UBERX_PRODUCT_ID = '04a497f5-380d-47f2-bf1b-ad4cfdcb51f2'
# define locations privately using seperate yaml file
locations = import_start_end_points()
START_LAT = locations.get('start_lat')
START_LNG = locations.get('start_lng')
END_LAT = locations.get('end_lat')
END_LNG = locations.get('end_lng')
# instantiate empty global objects
display_fare_start_to_end = ''
display_fare_end_to_start = ''
master_data = []
starttime=time.time()


'Defined Functions'
""""""""""""""""""
def request_available_products(api_client):
    try:
        request_products = api_client.get_products(
            latitude=START_LAT,
            longitude=START_LNG,
        )
    except (ClientError, ServerError) as error:
        fail_print(error)
        return
    else:
#        success_print(request_products.json) #See the raw estimate printed in green
        product_step1 = (request_products.json.get("products"))
        find_pool = next((item for item in product_step1 if item['display_name'] == 'POOL'), None)
        response_print(find_pool.get("display_name"))
        response_print(find_pool.get("product_id"))


def request_ufp_ride_start_to_end(api_client):
    global display_fare_start_to_end
    try:
        estimate_start_to_end = api_client.estimate_ride(
            product_id=SF_POOL_PRODUCT_ID,
            start_latitude=START_LAT,
            start_longitude=START_LNG,
            end_latitude=END_LAT,
            end_longitude=END_LNG,
            seat_count=1
        )
    except (ClientError, ServerError) as error:
        fail_print(error)
        return
    else:
#        success_print(estimate_start_to_end.json) #See the raw estimate printed in green
        display_fare_start_to_end = str((estimate_start_to_end.json.get("fare")).get("display"))


def request_ufp_ride_end_to_start(api_client):
    global display_fare_end_to_start
    try:
        estimate_end_to_start = api_client.estimate_ride(
            product_id=OAKLAND_POOL_PRODUCT_ID,
            start_latitude=END_LAT,
            start_longitude=END_LNG,
            end_latitude=START_LAT,
            end_longitude=START_LNG,
            seat_count=1
        )
    except (ClientError, ServerError) as error:
        fail_print(error)
        return
    else:
#        success_print(estimate_end_to_start.json) #See the raw estimate printed in green
        display_fare_end_to_start = str((estimate_end_to_start.json.get("fare")).get("display"))


def write_to_file ():
    global master_data
    global display_fare_start_to_end
    global display_fare_end_to_start
    time_stamp = str(datetime.datetime.now())
    master_data = [[time_stamp, display_fare_start_to_end, display_fare_end_to_start]]
    print(master_data)  # See the data in list form """""""""""""""""""""""""""""""""
    with open("attempt_4.csv", 'ab') as uber_data:
        writing_appending = csv.writer(uber_data)
        writing_appending.writerows(master_data)


'Script'
""""""""""""""""""
if __name__ == '__main__':
    credentials = import_oauth2_credentials()
    api_client = create_uber_client(credentials)

#    Requesting a ride estimate.
# request_available_products(api_client)

while True:
   request_ufp_ride_start_to_end(api_client)
   request_ufp_ride_end_to_start(api_client)
   write_to_file()
   time.sleep(120.0 - ((time.time() - starttime) % 120.0))