#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example gets all custom channels in an ad client.

To get ad clients, run get_all_ad_clients.py.

Tags: customchannels.list
"""

__author__ = 'sergio.gomes@google.com (Sergio Gomes)'

import sys
import gflags
from oauth2client.client import AccessTokenRefreshError
import sample_utils

MAX_PAGE_SIZE = 50

# Declare command-line flags, and set them as required.
gflags.DEFINE_string('ad_client_id', None,
                     'The ad client ID for which to get custom channels',
                     short_name='c')
gflags.MarkFlagAsRequired('ad_client_id')


def main(argv):
  # Process flags and read their values.
  sample_utils.process_flags(argv)
  ad_client_id = gflags.FLAGS.ad_client_id

  # Authenticate and construct service.
  service = sample_utils.initialize_service()

  try:
    # Retrieve custom channel list in pages and display data as we receive it.
    request = service.customchannels().list(adClientId=ad_client_id,
        maxResults=MAX_PAGE_SIZE)

    while request is not None:
      result = request.execute()
      custom_channels = result['items']
      for custom_channel in custom_channels:
        print ('Custom channel with code "%s" and name "%s" was found. '
               % (custom_channel['code'], custom_channel['name']))

        if 'targetingInfo' in custom_channel:
          print '  Targeting info:'
          targeting_info = custom_channel['targetingInfo']
          if 'adsAppearOn' in targeting_info:
            print '    Ads appear on: %s' % targeting_info['adsAppearOn']
          if 'location' in targeting_info:
            print '    Location: %s' % targeting_info['location']
          if 'description' in targeting_info:
            print '    Description: %s' % targeting_info['description']
          if 'siteLanguage' in targeting_info:
            print '    Site language: %s' % targeting_info['siteLanguage']

      request = service.customchannels().list_next(request, result)

  except AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
