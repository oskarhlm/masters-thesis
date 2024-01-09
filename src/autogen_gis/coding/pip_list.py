# filename: pip_list.py

import pkg_resources

def print_installed_packages():
    packages = pkg_resources.working_set
    packages_list = sorted(["%s==%s" % (i.key, i.version)
       for i in packages])
    for i in packages_list:
        print(i)

print_installed_packages()