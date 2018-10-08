#!/usr/bin/python
#_*_ coding:utf-8 _*_

import os
import commands
import requests
import json
import functools
import time
import sys

def add_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        response_value = func(*args, **kwargs)
        response_value.insert(0, now_time)
        return response_value
    return wrapper

def application(environ, start_response):
    response_body = get_service_status()
    status = '200 OK'
    response_heasers = [('Content-Type', 'text/plain')]
    start_response(status, response_heasers)
    return response_body

@add_time
def get_service_status():
    os.environ['OS_USERNAME'] = 'admin'
    os.environ['OS_PASSWORD'] = '123456'
    os.environ['OS_PROJECT_NAME'] = 'admin'
    os.environ['OS_USER_DOMAIN_NAME'] = 'Default'
    os.environ['OS_PROJECT_DOMAIN_NAME'] = 'Default'
    os.environ['OS_AUTH_URL'] = 'http://controller:35357/v3'
    os.environ['OS_IDENTITY_API_VERSION'] = '3'

    use = commands.getoutput("df -h | grep -w / |awk '{print int($5)}'")
    use = "The use of / is {0}%".format(use)

    free_memory = commands.getoutput("free -h | grep Mem | awk '{print $4}'")
    free_memory = "The free memory is %s" % free_memory

    mariadb_status = commands.getoutput("systemctl status mariadb.service | grep Active | awk '{print $2}'")
    mariadb_status = "The mariadb status is %s" % mariadb_status

    rabbitmq_status = commands.getoutput("systemctl status rabbitmq-server | grep Active | awk '{print $2}'")
    rabbitmq_status = "The rabbitmq status is %s" % rabbitmq_status

    httpd_status = commands.getoutput("systemctl status httpd | grep Active | awk '{print $2}'")
    httpd_status = "The http status is %s" % httpd_status

    nova_status = commands.getoutput('nova service-list')
    neutron_status = commands.getoutput('neutron agent-list')
    cinder_status = commands.getoutput('cinder service-list')
    service_status = [use, free_memory, mariadb_status, rabbitmq_status, httpd_status, nova_status, neutron_status, cinder_status]
    return service_status

