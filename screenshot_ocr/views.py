from django.shortcuts import HttpResponse
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from .serializers import TriggerSerializer, ResultSerializer
from screenshot_ocr.task import sleepy, start_tracking



def index(request):
    sleepy.delay(30)
    return HttpResponse("<h1>hi</h1>")


class Entry(object):
    def __init__(self, **kwargs):
        for field in ('twitch_match_url', 'match_id',):
            setattr(self, field, kwargs.get(field, None))


class EntryResult(object):
    def __init__(self, **kwargs):
        for field in ('match_id', 'time', 'home_team', 'home_result', 'away_team', 'away_result'):
            setattr(self, field, kwargs.get(field, None))


class TriggerProcess(viewsets.ViewSet):
    serializer_class = TriggerSerializer

    def list(self, request):
        twitch_match_url = str(request.data['twitch_match_url'])
        match_id = str(request.data['match_id'])

        print(twitch_match_url)
        print(match_id)
        if twitch_match_url and match_id:
            print("calling..")
            start_tracking.delay(twitch_match_url, match_id)
            # start_tracking(twitch_match_url, match_id)

        entries = {
            1: Entry(twitch_match_url=twitch_match_url, match_id=match_id),
        }
        serializer = TriggerSerializer(instance=entries.values(), many=True)
        return Response({'success': True, 'message': 'tracking started successfully.'})



# class Result(viewsets.ViewSet):
#     serializer_class = ResultSerializer
#
#     def list(self, request):
#         match_id = str(request.data['match_id'])
#         time, home_team, home_result, away_team, away_result = [] * 5
#
#
#         print(match_id)
#         if match_id:
#             with open(f'output/{match_id}.txt', 'r') as f:
#                 lines = f.readlines()
#             # start_tracking(twitch_match_url, match_id)
#             for line in lines:
#                 if 'time' in line:
#                     time = line.split(':')[1].strip()
#                 if 'home_team' in line:
#                     home_team = line.split(':')[1].strip()
#                 if 'home_result' in line:
#                     home_result = line.split(':')[1].strip()
#                 if 'away_team' in line:
#                     away_team = line.split(':')[1].strip()
#                 if 'away_result' in line:
#                     away_result = line.split(':')[1].strip()
#
#         entries = {
#             1: Entry(match_id=match_id, time=time, home_team=home_team, home_result=home_result, away_team=away_team, away_result=away_result),
#         }
#         serializer = TriggerSerializer(instance=entries.values(), many=True)
#         return Response({'success': True, 'data': serializer.data})



class Result(APIView):
    def get(self, request, match_id):
        print('match id:', match_id)
        data = {}
        time, home_team, home_result, away_team, away_result, lines = [''] * 6
        if match_id:
            try:
                with open(f'output/{match_id}.txt', 'r') as f:
                    lines = f.readlines()
            except:
                return Response({'success': False, 'message': f'Match with id {match_id} does not exist!'}, status=status.HTTP_404_NOT_FOUND)

            for line in lines:
                if 'time' in line:
                    print(line)
                    time = line.split('=')[1].strip()
                if 'home_team' in line:
                    home_team = line.split('=')[1].strip()
                if 'home_result' in line:
                    home_result = line.split('=')[1].strip()
                if 'away_team' in line:
                    away_team = line.split('=')[1].strip()
                if 'away_result' in line:
                    away_result = line.split('=')[1].strip()

            data = {
                'match_id': match_id,
                'time': time,
                'home_team': home_team,
                'home_result': home_result,
                'away_team': away_team,
                'away_result': away_result
            }

        return Response({'success': True, 'data': data}, status=HTTP_200_OK)
