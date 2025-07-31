from cogs._pterodapi import API
from json import loads
from config import ISSUEBOT_URL
from requests import post

api = API(
    address="https://fissionhost.dpdns.org",
    application_token=(
        "ptla_4fB6pnehpUVKDEUY6L3IkFbKNfFuzFT4PXl9Gd6iBqp"
    ),  # Flake8's fault
    user_token="ptlc_1qcXqvxqhFdQyBDk4UvvF0sw6IM2TDTd5UTFFc6BHUO",
    debug=True,
)


async def send_messages(messages: list[list[str]]):
    print(messages)
    if len(messages) != 1:
        data = {
            "embeds": [
                {
                    "title": "Some tests failed",
                    "color": 15158332,
                    "description": "The bot will not start until these issues are fixed!",  # noqa: E501
                    "fields": [
                        {"name": f"Test {i+1}", "value": str(msg), "inline": False}  # noqa: E501
                        for i, msg in enumerate(messages)
                    ]
                }
            ]
        }
        print(data)

        response = post(ISSUEBOT_URL, json=data)
        if response.status_code != 204:
            print(f'Failed to send message: {response.status_code}')
        return response.status_code
        # return 400
    else:
        return 0


async def test_nodes():
    messages = []
    tests_for = ['public', 'no_maintenance', 'memory', 'disk', 'fake_test']
    tests_passed = []

    warning_msg = {
        'public': 'There are no public nodes!',
        'no_maintenance': 'All nodes are in maintenance!',
        'memory': 'A node is running out of available memory!',
        'disk': 'A node is running out of available disk space!',
        'fake_test': 'This is just a fake test!'
    }

    response = loads(await api.Nodes.list_nodes())
    nodes = response["data"]
    if len(nodes) == 0:
        return messages.append("There are no nodes!")

    for node in nodes:
        attribs = node["attributes"]
        max_memory = attribs['memory']
        max_disk = attribs['disk']
        used_memory = attribs['allocated_resources']['memory']
        used_disk = attribs['allocated_resources']['disk']

        if attribs['public'] and 'public' not in tests_passed:
            tests_passed.append('public')

        if not attribs['maintenance_mode'] and 'maintenance_mode' not in tests_passed:  # noqa: E501
            tests_passed.append('maintenance_mode')

        if used_memory <= max_memory - 15000 and 'memory' not in tests_passed:
            tests_passed.append('memory')

        if used_disk <= max_disk - 15000 and 'disk' not in tests_passed:
            tests_passed.append('disk')

    for test in tests_for:
        if test not in tests_passed:
            print(test, 'test failed!')
            print(attribs['maintenance_mode'])
            messages.append(warning_msg[test])

    return messages


async def Tester():
    messages = []
    messages.append(await test_nodes())

    response = await send_messages(messages)

    return response
