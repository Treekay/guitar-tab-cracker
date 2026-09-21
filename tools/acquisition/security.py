"""Public HTTP(S) policy, enforced again at every Python socket connection."""
import ipaddress
import socket
import sys
from urllib.parse import urlsplit

class AcquisitionError(Exception):
    def __init__(self,reason,message):self.reason=reason;super().__init__(message)

def public_ip(value):
    try:ip=ipaddress.ip_address(value.split('%')[0])
    except ValueError:return False
    if getattr(ip,'ipv4_mapped',None):ip=ip.ipv4_mapped
    return ip.is_global and not (ip.is_multicast or ip.is_reserved or ip.is_unspecified)

def host_policy(host):
    if not host or any(c in host for c in '\\%\r\n\t /'):
        raise AcquisitionError('unsupported_url','Invalid host')
    host=host.rstrip('.').lower()
    try:ipaddress.ip_address(host)
    except ValueError:
        if '.' not in host or host.endswith(('.localhost','.local','.internal','.lan','.home','.test','.invalid')) or host=='localhost':
            raise AcquisitionError('unsupported_url','Internal-only host is not allowed')
    else:
        if not public_ip(host):raise AcquisitionError('unsupported_url','Non-public IP is not allowed')
    return host

def validate_url(url,resolve=True):
    if not isinstance(url,str) or any(ord(c)<33 for c in url) or '\\' in url:
        raise AcquisitionError('unsupported_url','Malformed URL')
    try:
        u=urlsplit(url);host=host_policy(u.hostname);port=u.port or (443 if u.scheme=='https' else 80)
    except ValueError as e:raise AcquisitionError('unsupported_url','Malformed URL') from e
    if u.scheme not in ('http','https') or u.username is not None or u.password is not None or port not in (80,443):
        raise AcquisitionError('unsupported_url','Only public HTTP(S) URLs on ports 80/443, without credentials, are supported')
    if resolve:
        try:addresses=socket.getaddrinfo(host,port,type=socket.SOCK_STREAM)
        except OSError as e:raise AcquisitionError('network_error','DNS resolution failed') from e
        if not addresses or any(not public_ip(a[4][0]) for a in addresses):
            raise AcquisitionError('unsupported_url','Host resolves to a non-public address')
    return url

def audit_network(event,args):
    if event=='socket.getaddrinfo':
        host,port=args[:2];host_policy(host.decode() if isinstance(host,bytes) else host)
        if port not in (80,443,'80','443'):raise AcquisitionError('unsupported_url','Non-web destination port blocked')
    elif event=='socket.connect':
        address=args[1]
        # Reject hostnames here: connection must use the numeric address resolved
        # by the HTTP stack. This rechecks DNS rebinding and redirect targets.
        if not isinstance(address,tuple) or len(address)<2 or address[1] not in (80,443) or not public_ip(address[0]):
            raise AcquisitionError('unsupported_url','Non-public socket destination blocked')
    elif event in ('subprocess.Popen','os.system','os.posix_spawn'):
        raise AcquisitionError('unsupported_url','External downloader/runtime execution disabled in acquisition worker')

def install_network_guard():sys.addaudithook(audit_network)
