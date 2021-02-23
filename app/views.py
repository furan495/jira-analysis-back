import json
import random
from jira import JIRA
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

jira = None


@csrf_exempt
def login(request):
    global jira
    params = json.loads(request.body)
    try:
        jira = JIRA(params['server'], auth=(
            params['username'], params['password']))
        name = jira.user(params['username']).displayName
        avatar = jira.user_avatars(params['username'])[
            'custom'][0]['urls']['48x48']
        return JsonResponse({'res': 'succ', 'name': name, 'avatar': avatar})
    except Exception as e:
        print(e)
        return JsonResponse({'res': 'fail'})


@csrf_exempt
def projects(request):

    def avatar(pro):
        try:
            return list(filter(lambda obj: obj['isSelected'], jira.project_avatars(jira.project(pro.key))['system']))[0]['urls']['48x48']
        except:
            return jira.project_avatars(jira.project(pro.key))['system'][random.randint(0, 25)]['urls']['48x48']

    projects = map(lambda pro: {
        'key': pro.key,
        'name': pro.name,
        'avatar': avatar(pro),
        'lead': jira.project(pro.key).lead.displayName,
        'issueTypes': list(map(lambda obj: obj.name.strip(), jira.issue_types())),
        'issue': jira.search_issues(
            'project = %s and created >= startOfYear()' % pro.id, fields="summary, priority, status,issuetype,description,assignee,reporter,resolution,created,updated,comments", maxResults=-1, json_result='true')['issues']
    }, jira.projects())
    return JsonResponse({'data': list(projects)})
