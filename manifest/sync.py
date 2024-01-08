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
import copy

logging.basicConfig(level=logging.DEBUG)

numberOfAttempts = {}

class Controller(BaseHTTPRequestHandler):
  def sync(self, job, children):
    logging.debug('Children: %s', children)
    logging.debug('Job: %s', job)
    jobName = job['metadata']['name']
   
        # Arrange observed Pods by index, and count by phase.

    (active, succeeded, failed) = (0, 0, 0)

    numberOfPods= len(children['Pod.v1'])
    numberOfAttempts.setdefault(jobName, 1)


    logging.debug('Number of pods:: %d', numberOfPods)
    spec_parallelism = job['spec']['parallelism']
    logging.debug('spec_parallelism: %d', spec_parallelism)


    for pod_name, pod in children['Pod.v1'].iteritems():
        phase = pod.get('status', {}).get('phase')

        env = pod['spec']['containers'][0].get('env', [])
        num_attempts_value = next((int(item['value']) for item in env if item['name'] == 'NUM_ATTEMPTS'), numberOfAttempts[jobName])

        logging.debug('num_attempts_value: %d', num_attempts_value)

        if phase == 'Succeeded':
            succeeded += 1
        elif phase == 'Failed' and num_attempts_value==numberOfAttempts[jobName]:
            failed += 1
        else:
            active += 1

    logging.debug('FAILED: %d', failed)

    if failed>0 :
          numberOfAttempts[jobName] += 1

    desired_pods = []
    for x in range(1, spec_parallelism + 1):
        logging.debug('NUMBER OF ATTEMPTS:: %d', numberOfAttempts[jobName])
        newPod = self.newPod(job, x, numberOfAttempts[jobName])
        desired_pods.append(newPod)
        logging.debug('podSpec: %s', newPod)
            
    
    return {'children': desired_pods }


  def newPod(self, job, index, numberOfAttemptsInt):
    
    newPod = {
      'apiVersion': 'v1',
      'kind': 'Pod',
      'metadata': {
          'name': job['metadata']['name'] +'-'+ str(index),
          

      }
    }
    newPod['spec'] = copy.deepcopy(job['spec']['template']['spec'])

    env = newPod['spec']['containers'][0].get('env', [])
    
    env.append({'name': 'NUM_ATTEMPTS', 'value': str(numberOfAttemptsInt)})    
    newPod['spec']['containers'][0]['env'] = env
    newPod['spec']['restartPolicy']= 'Never'
    return newPod


  def do_POST(self):
    observed = json.loads(self.rfile.read(int(self.headers.getheader('content-length'))))
    logging.debug('observed: %s', observed)
    desired = self.sync(observed['parent'], observed['children'])

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(desired))

HTTPServer(('', 80), Controller).serve_forever()
