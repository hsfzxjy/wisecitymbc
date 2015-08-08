from articles.signals import status_posted
from .signals import finance_year_changed
from django.dispatch import receiver
from .serializers import PlayerDataLogSerializer
from .models import PlayerDataLog

@receiver(finance_year_changed)
def finance_year_changed_receiver(sender, post_year, current_year, **kwargs):
    PlayerDataLog.summary(post_year)

@receiver(status_posted)
def status_posted_receiver(sender, data, **kwargs):
    cleaned_data = {}

    for key, value in data.iteritems():
        if not key.startswith("data__"):
            continue

        _, field_name, player_id = key.split('__')
        value = value or 0
        
        if player_id in cleaned_data:
            cleaned_data[player_id][field_name] = value 
            cleaned_data[player_id]["not_empty"] = cleaned_data[player_id]["not_empty"] or bool(float(value))
        else:
            cleaned_data[player_id] = {
                "user": player_id,
                field_name: value,
                "not_empty": bool(float(value)),
                "status": sender.id,
            }

    serializer = PlayerDataLogSerializer(
        data = filter(lambda x: x["not_empty"], cleaned_data.itervalues()),
        many = True
    )

    if serializer.is_valid():
        serializer.save()
    else:
        from rest_framework.exceptions import ParseError
        raise ParseError(serializer.errors)
