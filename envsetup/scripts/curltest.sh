#!/bin/bash
curl --header "Content-Type: application/json" -X POST -k https://napps.kytos.io/api/napps/ --data '{'author': 'lmarinve', 'username': 'lmarinve', 'name': 'myfirst_napp', 'description': 'Insert\ your\ NApp\ description\ here', 'version': '1.0', 'napp_dependencies': [], 'license': '', 'tags': [], 'url': '', 'readme': 'Overview\nInsert\ your\ NApp\ description\ here\n\nRequirements\n', 'OpenAPI_Spec': '{'openapi': '3.0.0', 'info': {'title': 'lmarinve/myfirst\_napp', 'version': 1.0, 'description': ''}, 'paths': ''}', 'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImxtYXJpbnZlIiwiaXNzIjoiS3l0b3MgTkFwcHMgU2VydmVyIiwiZXhwIjoxNjMwNTE0MzAyfQ.thLcH532eqSQZHA1BSgJL712ggHzh9cQDlGBm95ur8k'}'