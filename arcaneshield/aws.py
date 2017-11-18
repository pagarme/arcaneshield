import boto3
import os
from sources.all import get_ip_list as get_upstream_ip_list
from tqdm import tqdm
import math
import re

ipset_limit = 1000

rule_condition_limit = 10

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

def get_ip_list():
    l = []

    ips = get_upstream_ip_list()

    tqdm(desc='Generating update list', total=len(ips), leave=False)
    for ip in ips:
        if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip):
            obj = {'Type': 'IPV4', 'Value': '{}'.format(ip)}
            l.append(obj)

    return l


def protect():

    iplist = get_ip_list()

    c = boto3.client('waf-regional')

    updates = []

    required_rules = math.ceil(len(iplist)/ipset_limit/rule_condition_limit)


    for ip in iplist:
        obj = {'Action': 'INSERT', 'IPSetDescriptor': ip}

        updates.append(obj)

    print('[*] Deleting Arcane Shield rules...')

    rules = []

    for r in c.list_rules()['Rules']:
        if r['Name'].startswith('Arcane Shield'):
            rules.append(r['RuleId'])

    for rule in rules:
        c.delete_rule(RuleId=rule, ChangeToken=c.get_change_token()['ChangeToken'])


    print('[*] Recreating rules...')
    print('[*] This is going to require {} rules...'.format(required_rules))

    for i in range(0, required_rules):
        print('[*] Creating rule Arcane Shield {}...'.format(i))
        rules.append(c.create_rule(Name='Arcane Shield {}'.format(i), MetricName='ArcaneShield{}'.format(i), ChangeToken=c.get_change_token()['ChangeToken'])['Rule']['RuleId'])

    '''
    print('[*] Clearing rules...')

    for arcane in rules:
        predicates = c.get_rule(RuleId=arcane)['Rule']['Predicates']

        dupdates = []

        if predicates:

            for pred in predicates:
                obj = {'Action': 'DELETE', 'Predicate': pred}
                dupdates.append(obj)


            c.update_rule(RuleId=arcane, ChangeToken=c.get_change_token()['ChangeToken'], Updates=dupdates)
    '''

    ipsetlist = []

    for ipset in c.list_ip_sets()['IPSets']:
        if ipset['Name'].startswith('Arcane Shield'):
            ipsetlist.append(ipset['IPSetId'])

    print('[*] Deleting IP Sets...')
    for ip in ipsetlist:
        desclist = c.get_ip_set(IPSetId=ip)['IPSet']['IPSetDescriptors']

        dupdates = []

        if desclist:

            for desc in desclist:
                obj = {'Action': 'DELETE', 'IPSetDescriptor': desc}
                dupdates.append(obj)

            c.update_ip_set(IPSetId=ip, ChangeToken=c.get_change_token()['ChangeToken'], Updates=dupdates)

        c.delete_ip_set(IPSetId=ip, ChangeToken=c.get_change_token()['ChangeToken'])

    print('[*] Recreating IP Sets...')

    print('[*] This is going to require {} sets...'.format(math.ceil(len(updates)/ipset_limit)))

    newipsets = []

    cnt = 0
    for chunk in chunks(updates, ipset_limit):
        cnt += 1
        ipset = c.create_ip_set(Name='Arcane Shield {}'.format(cnt), ChangeToken=c.get_change_token()['ChangeToken'])

        print('[*] Populating IP Set {} with {} IPs...'.format(ipset['IPSet']['Name'], len(chunk)))
        c.update_ip_set(IPSetId=ipset['IPSet']['IPSetId'], ChangeToken=c.get_change_token()['ChangeToken'], Updates=chunk)

        newipsets.append(ipset['IPSet']['IPSetId'])

    print('[*] Attaching IP sets to rules...')

    cnt = 0
    for chunk in chunks(newipsets, rule_condition_limit):
        updates = []
        for ipset in chunk:
            obj = {'Action': 'INSERT', 'Predicate': {'Negated': False, 'Type': 'IPMatch', 'DataId': ipset}}
            updates.append(obj)

        arcane = rules[cnt]

        print('[*] Attaching IP Sets {} to rule {}...'.format(updates, arcane))

        c.update_rule(RuleId=arcane, ChangeToken=c.get_change_token()['ChangeToken'], Updates=updates)

        cnt += 1

if __name__ == '__main__':
    protect()
