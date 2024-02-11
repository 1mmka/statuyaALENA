from django.core.management import call_command # при migrate автоматический срабатывает
call_command('update_database',verbosity=0)  