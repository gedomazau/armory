#!/usr/bin/python

from included.ModuleTemplate import ModuleTemplate
import re
from utilities.get_urls import run as geturls
from database.repositories import ServiceRepository
import requests
import time
import os
import sys
import pdb
from multiprocessing import Pool as ThreadPool

class Module(ModuleTemplate):
    
    name = "HeaderScanner"

    def __init__(self, db):
        self.db = db
        self.Service = ServiceRepository(db, self.name)

    def set_options(self):
        super(Module, self).set_options()

        self.options.add_argument('-t', '--timeout', help='Connection timeout (default 5)', default="5")
        self.options.add_argument('-u', '--url', help="URL to get headers")
        self.options.add_argument('-i', '--import_db', help="Import URLs from the database", action="store_true")
        self.options.add_argument('-th', '--threads', help="Number of threads to run", default="10")

    def run(self, args):
        
        if args.import_db:
            

            svc = self.Service.all(name='http')
            svc += self.Service.all(name='https')

            data = []

            for s in svc:

                urls = ["%s://%s:%s" % (s.name, s.port.ipaddress.ip_address, s.port.port_number)]

                for d in s.port.ipaddress.domains:
                    urls.append("%s://%s:%s" % (s.name, d.domain, s.port.port_number))

                data.append([s.id, urls, args.timeout])                
            
            pool = ThreadPool(int(args.threads))

            results = pool.map(process_urls, data)
            print("Adding data to the database")
            for i, headers in results:
                created, svc = self.Service.find_or_create(id=i)
                svc.meta['headers'] = headers
                svc.update()

            
            self.Service.commit()


            

            
def process_urls(data):

    i, urls, timeout = data
    blacklist = ['Date', 'Connection', 'Content-Type', 'Content-Length', 'Keep-Alive', 'Content-Encoding', 'Vary']
    new_headers = {}

    for u in urls:
        print("Processing %s" % u)
        try:
            res = requests.get(u, timeout=int(timeout), verify=False)

            for k in res.headers.keys():
                if k not in blacklist:
                    if not new_headers.get(u, False):
                        new_headers[u] = []

                    new_headers[u].append("%s: %s" % (k, res.headers[k]))
            

        except KeyboardInterrupt:
            print("Got Ctrl+C, exiting")
            sys.exit(1)
        except Exception as e:
            print("%s no good, skipping: %s" % (u, e))
    return (i, new_headers)