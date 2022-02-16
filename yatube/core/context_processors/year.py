from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    current_year = int(timezone.now().year)
    return {
        'year': current_year
    }
