#!/usr/bin/env python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import logging

logging.basicConfig(level=logging.DEBUG, filename='sample.log')



class Controller(BaseHTTPRequestHandler):
  def sync(self, job, children):
    logging.debug('Children: %s', children)
    newJob = self.new_Job(job)
    return {'children': [newJob] }


  def new_Job(self, oldJob):
    newJob = {
      'apiVersion': 'apps/v1',
      'kind': 'Deployment',
      'metadata': {
          'name': 'jax-deployment1',
          'labels': {
              'app': 'jax'
          },
      },
      'spec': {
          'replicas': oldJob['spec']['replicas'],
          'selector': {
              'matchLabels': {
                  'app': 'jax'
              }
          },
          'template': {
              'metadata': {
                  'labels': {
                      'app': 'jax'
                  }
              },
              'spec': {
                  'containers': [
                      {
                          'name': 'busybox',
                          'image': 'busybox',
                          'command':oldJob['spec']['template']['spec']['containers'][0]['command'],
                          'env':[{'name':'tst', 'value':'tst'}],
                          'ports': [
                              {
                                  'containerPort': 80
                              }
                          ]
                      }
                  ]
              }
          }
      }
  }

    return newJob


  def do_POST(self):
    observed = json.loads(self.rfile.read(int(self.headers.getheader('content-length'))))
    desired = self.sync(observed['parent'], observed['children'])

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(desired))

HTTPServer(('', 80), Controller).serve_forever()
