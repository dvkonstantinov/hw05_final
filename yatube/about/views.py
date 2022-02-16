from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['temp1'] = 'Переменная из словаря номер раз'
        context['temp2'] = 'Переменная из словаря номер два'
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
