import boto3
import os
from sources.all import get_ip_list as get_upstream_ip_list
from tqdm import tqdm
import math

ipset_limit = 10000

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

def get_ip_list():
    l = []

    ips = get_upstream_ip_list()

    tqdm(desc='Generating update list', total=len(ips), leave=False)
    for ip in ips:
        obj = {'Type': 'IPV4', 'Value': '{}/32'.format(ip)}
        l.append(obj)

    return l


def protect():

    iplist = get_ip_list()

    c = boto3.client('waf-regional')

    updates = []


    for ip in iplist:
        obj = {'Action': 'INSERT', 'IPSetDescriptor': ip}

        updates.append(obj)

    print('[*] Getting Arcane Shield rule...')

    arcane = None

    for r in c.list_rules()['Rules']:
        if r['Name'] == 'Arcane Shield':
            arcane = r['RuleId']

    if not arcane:
        arcane = c.create_rule(Name='Arcane Shield', MetricName='ArcaneShield', ChangeToken=c.get_change_token()['ChangeToken'])['Rule']['RuleId']

    print('[*] Clearing rule')

    predicates = c.get_rule(RuleId=arcane)['Rule']['Predicates']

    dupdates = []

    if predicates:

        for pred in predicates:
            obj = {'Action': 'DELETE', 'Predicate': pred}
            dupdates.append(obj)


        c.update_rule(RuleId=arcane, ChangeToken=c.get_change_token()['ChangeToken'], Updates=dupdates)

    ipsetlist = []

    for ipset in c.list_ip_sets()['IPSets']:
        if ipset['Name'].startswith('Arcane Shield'):
            ipsetlist.append(ipset['IPSetId'])

    print('[*] Deleting IP Sets')
    for ip in ipsetlist:
        desclist = c.get_ip_set(IPSetId=ip)['IPSet']['IPSetDescriptors']

        dupdates = []

        if desclist:

            for desc in desclist:
                obj = {'Action': 'DELETE', 'IPSetDescriptor': desc}
                dupdates.append(obj)

            c.update_ip_set(IPSetId=ip, ChangeToken=c.get_change_token()['ChangeToken'], Updates=dupdates)

        c.delete_ip_set(IPSetId=ip, ChangeToken=c.get_change_token()['ChangeToken'])

    print('[*] Recreating IP Sets')

    print('[*] This is going to require {} sets'.format(math.ceil(len(updates)/ipset_limit)))


    updates = updates[:1000]

    newipsets = []

    cnt = 0
    for chunk in chunks(updates, ipset_limit):
        cnt += 1
        ipset = c.create_ip_set(Name='Arcane Shield {}'.format(cnt), ChangeToken=c.get_change_token()['ChangeToken'])

        print('[*] Populating IP Set {} with {} IPs'.format(ipset['IPSet']['Name'], len(chunk)))
        c.update_ip_set(IPSetId=ipset['IPSet']['IPSetId'], ChangeToken=c.get_change_token()['ChangeToken'], Updates=chunk)

        newipsets.append(ipset['IPSet']['IPSetId'])

    print('[*] Attaching IP sets to rule')

    updates = []

    for ipset in newipsets:
        obj = {'Action': 'INSERT', 'Predicate': {'Negated': False, 'Type': 'IPMatch', 'DataId': ipset}}
        updates.append(obj)

    c.update_rule(RuleId=arcane, ChangeToken=c.get_change_token()['ChangeToken'], Updates=updates)

if __name__ == '__main__':
    protect()
