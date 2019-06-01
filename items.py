actions = {
    'install_jenkins_key': {
        'command': 'wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | apt-key add -',
        'unless': 'apt-key list | grep "D505 82E6"',
        'cascade_skip': False
    }
}

directories = {}

if not node.has_bundle('jenkins-ssh'):
    directories['/var/lib/jenkins/.ssh'] = {
        'owner': 'jenkins',
        'group': 'jenkins',
        'mode': '0750',
        'needs': ['pkg_apt:jenkins']
    }

files = {
    '/etc/apt/sources.list.d/jenkins.list': {
        'content': 'deb https://pkg.jenkins.io/debian binary/',
        'owner': 'root',
        'group': 'root',
        'mode': '0644',
        'needs': ['action:install_jenkins_key'],
        'triggers': ['action:update_apt_cache']
    }
}

if not node.has_bundle('jenkins-ssh'):
    files['/var/lib/jenkins/.ssh/id_ed25519'] = {
        'content': repo.vault.decrypt_file('jenkins/id_ed25519'),
        'owner': 'jenkins',
        'group': 'jenkins',
        'mode': '0600',
        'needs': ['pkg_apt:jenkins']
    }

pkg_apt = {
    'jenkins': {
        'needs': [
            'file:/etc/apt/sources.list.d/jenkins.list',
            'pkg_apt:oracle-java8-installer'
        ]
    }
}

svc_systemv = {
    'jenkins': {
        'needs': ['pkg_apt:jenkins']
    }
}

if node.has_bundle('nrpe'):
    files['/etc/nagios/nrpe.d/jenkins.cfg'] = {
        'source': 'nrpe.cfg',
        'owner': 'nagios',
        'group': 'nagios',
        'mode': '0640',
        'needs': ['pkg_apt:nagios-nrpe-server'],
        'triggers': ['svc_systemv:nagios-nrpe-server:restart']
    }
