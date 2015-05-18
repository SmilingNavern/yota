#!/usr/bin/env python

import requests
import ConfigParser
import argparse


TARIFF_CODES = {'320':'POS-MA6-0002', '512':'POS-MA6-0004', '768':'POS-MA6-0006', '1024':'POS-MA6-0008'}
AVAILABLE_SPEED = TARIFF_CODES.keys()

def get_settings():
    "Get login/password from config"
    cnf = ConfigParser.ConfigParser()
    cnf.readfp(open('.yota.cnf'))
    login = cnf.get('general', 'login')
    password = cnf.get('general', 'password')

    return login, password

def get_args():
    arg_parse = argparse.ArgumentParser(description='Script to change yota tariff')
    arg_parse.add_argument('speed', choices=AVAILABLE_SPEED, type=str, default='320', help='Speed to set for yota')
    args = arg_parse.parse_args()
    return args

def auth_yota(sess):
    auth_url = 'https://login.yota.ru/UI/Login'
    login, password = get_settings()

    payload = {'IDToken1' : login, 'IDToken2' : password, 
                'goto' : 'https://my.yota.ru/selfcare/loginSuccess', 
                'gotoOnFail' : 'https://my.yota.ru/selfcare/loginError',
                'old-token' : '',
                'org' : 'customer' }
    result = sess.post(auth_url, payload)
    return result

def change_offer(sess, product, speed):
    tariff_url = 'https://my.yota.ru/selfcare/devices/changeOffer'
    tariff_payload = {'product' : product, 'offerCode' : TARIFF_CODES[speed],
                      'homeOfferCode' : '', 'areOffersAvailable' : 'false',
                      'period' : '', 'status' : 'custom',
                      'autoprolong': 0, 'isSlot' : 'false', 'resourceId' : '',
                      'Device' : 1, 'username' : '', 'isDisablingAutoprolong' : 'false'}

    result = sess.post(tariff_url, tariff_payload)
    return result


def main():
    args = get_args()
    speed = args.speed

    sess = requests.Session()
    r = auth_yota(sess)
    output = r.text.split('\n')
    product = ''
    for line in output:
        if 'name="product"' in line:
            product = line.split()[3].split('=')[1]
            product = int(product.replace('"', ''))

    if product == '':
        print 'Error. Product value is empty'

    change_offer(sess, product, speed)


if __name__ == '__main__':
    main()
