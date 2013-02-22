import json
import requests
import sys
import getpass
from xml.dom import minidom


def getComment(bug):
    comments = bug.getElementsByTagName('long_desc') 
    commentList = []
    for c in comments:
        text = c.getElementsByTagName('thetext')[0].firstChild.nodeValue
        when = c.getElementsByTagName('bug_when')[0].firstChild.nodeValue
        who = c.getElementsByTagName('who')[0].getAttribute('name')
        who_mail = c.getElementsByTagName('who')[0].firstChild.nodeValue
    
        commentList.append({"text": text, "when": when, "who": who, "mail": who_mail})

    return commentList


print "Enter github username: "
user = sys.stdin.readline().strip()
pwd = getpass.getpass()
print "Which repo (username/repo): "
repo = sys.stdin.readline().strip()
print "Enter xmlfile:"
xmlfile = sys.stdin.readline().strip()


urlbase="https://api.github.com/repos/" + repo
xmldoc = minidom.parse(xmlfile)

itemlist = xmldoc.getElementsByTagName('bug') 
print len(itemlist)
for bug in itemlist :
    bug_id = bug.getElementsByTagName('bug_id')[0].firstChild.nodeValue
    bug_product = bug.getElementsByTagName('product')[0].firstChild.nodeValue
    bug_status = bug.getElementsByTagName('bug_status')[0].firstChild.nodeValue
    bug_title = "%(title)s (Bugzilla #%(id)s)" % {"title": bug.getElementsByTagName('short_desc')[0].firstChild.nodeValue, "id": bug_id}
    bug_version = bug.getElementsByTagName('version')[0].firstChild.nodeValue
    bug_platform = bug.getElementsByTagName('rep_platform')[0].firstChild.nodeValue
    bug_severity = bug.getElementsByTagName('bug_severity')[0].firstChild.nodeValue
    bug_component = bug.getElementsByTagName('component')[0].firstChild.nodeValue

    if bug_severity == "Feature request":
        bug_severity = "enhancement"

    # print "################"
    # print bug_id
    # print bug_product
    # print bug_status
    # print bug_title
    # print bug_version
    # print bug_platform
    # print bug_severity

    url = "%s/issues" % (urlbase)
    bbody = "%s bug in component %s\n" % (bug_severity, bug_component)
    bbody += "Reported in version %s on platform %s\n" % (bug_version, bug_platform);
    labels = [bug_version, bug_severity, bug_component]
    params = {"title":bug_title, "body": bbody, "labels":labels}
    r = requests.post(url, data=json.dumps(params), auth=(user, pwd))
    if not r.ok:
        print "Error:", r.json()
        print "URL:", url
        print "Parameters:", params
    else:
        comments = getComment(bug)
        url = r.json()['comments_url']
        for c in comments:
            cbody = "On %s, '%s (%s) wrote:\n%s" % (c['when'], c['who'], c['mail'], c['text'])
            r = requests.post(url, data=json.dumps({"body": cbody}), auth=(user, pwd))
            if not r.ok:
                print "Error:", r.json()
                print "URL:", url
                print "Parameters:", params


