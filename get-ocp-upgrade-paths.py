#!/usr/bin/env python

# A tool to determine possible upgrade paths for a given openshift version
# Example usage: get-ocp-upgrade-paths 4.4.6

import json
import sys
import urllib2


def find_index(nodes, version):
    for index, node in enumerate(nodes):
        if node['version'] == version:
            return index

    return -1


def search(version, channel):
    print "\nSearching in channel: " + channel

    # Get graph in json
    url = 'https://api.openshift.com/api/upgrades_info/v1/graph?channel=' + \
        channel + '&arch=amd64'
    headers = {'Accept': 'application/json'}
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    raw = response.read()
    data = json.loads(raw)

    # Find wanted version to get its index in the node list
    index = find_index(data["nodes"], version)

    if index < 0:
        sys.exit("error: could not find version: " + version)

    print "found version:", data["nodes"][index]["version"], "at index:", index

    edge_found = False

    # Print all edges where the from version is our wanted version
    for edge in data['edges']:
        if edge[0] == index:
            print "edge: ", edge
            print "node: "
            print json.dumps(data['nodes'][edge[1]], indent=4, sort_keys=True)
            edge_found = True

    if not edge_found:
        print "==> Could not find upgrade path for: " + \
            version + " in channel: " + channel

    return edge_found


def main():
    if len(sys.argv) != 2:
        sys.exit("error: wrong number of args")

    version = sys.argv[1]

    verlist = version.split(".")
    if len(verlist) != 3:
        sys.exit("error: version argument does not look like a semantic version")

    try:
        major = int(verlist[0])
        minor = int(verlist[1])
        patch = int(verlist[2])
    except Exception as e:
        sys.exit("error: version argument does not look like a semantic version")

    found = search(version, "stable-" + str(major) + "." + str(minor))

    if not found:
        # bump minor version and try a later channel
        minor = str(minor + 1)
        channel = "stable-" + str(major) + "." + str(minor)
        search(version, channel)


if __name__ == '__main__':
    main()
