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
    return {'attachments': [newJob] }


  def do_POST(self):
    observed = json.loads(self.rfile.read(int(self.headers.getheader('content-length'))))
    desired = self.sync(observed['object'], observed['attachments'])

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(desired))

  def new_Job(self, oldJob):
    newJob = {
        'apiVersion': 'batch/v1',
        'kind': 'Job'
    }

    newJob['metadata']= {
      'name': 'job-backoff-limit-per-index-example1',
      # 'annotations': {
      #     'jax-job-label': 'jax'
      #}
    }

    newJob['spec'] ={
      'completions': 10,
      'parallelism': 3,
      'completionMode': 'Indexed',
    }

    newJob['spec']['template'] ={
      'spec': {
        'restartPolicy': 'Never',
        'containers': [
          {
            'env':[{'name':'tst', 'value':'tst'}],
            'name': 'example',
            'image': 'python',
            'command': oldJob['spec']['template']['spec']['containers'][0]['command']
          }
        ]
      }
    }
    return newJob

HTTPServer(('', 80), Controller).serve_forever()
