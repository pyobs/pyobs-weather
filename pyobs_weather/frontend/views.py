from django.views.generic import TemplateView

#from pyobs_weather.weather.models import Station, Weather


class OverView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        return {}
        #return {'stations': Station.objects.all(), 'weather': Weather.objects.filter(station_id=3).all()}
