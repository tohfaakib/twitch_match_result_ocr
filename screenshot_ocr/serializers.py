from rest_framework import serializers


class TriggerSerializer(serializers.Serializer):
    """Your data serializer, define your fields here."""
    twitch_match_url = serializers.CharField(max_length=250, required=False)
    match_id = serializers.CharField(max_length=250, required=False)


class ResultSerializer(serializers.Serializer):
    """Your data serializer, define your fields here."""
    match_id = serializers.CharField(max_length=250, required=False)
    time = serializers.CharField(max_length=250, required=False)
    home_team = serializers.CharField(max_length=250, required=False)
    home_result = serializers.CharField(max_length=250, required=False)
    away_team = serializers.CharField(max_length=250, required=False)
    away_result = serializers.CharField(max_length=250, required=False)