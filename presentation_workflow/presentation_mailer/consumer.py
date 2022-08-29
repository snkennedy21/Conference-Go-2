from concurrent.futures import process
import json
import pika
import django
import os
import sys
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


def process_approval(ch, method, properties, body):
  content = json.loads(body)
  send_mail(
      'Presentation Approved',
     f'Congragulations {content["name"]}! Your presentation {content["title"]} has been approved',
      'from@example.com',
      [f'{content["email"]}'],
      fail_silently=False,
  )



def process_rejection(ch, method, properties, body):
  content = json.loads(body)
  send_mail(
      'Presentation Rejected',
     f'We are sorry {content["name"]}! Your presentation {content["title"]} has been rejected',
      'from@example.com',
      [f'{content["email"]}'],
      fail_silently=False,
  )






parameters = pika.ConnectionParameters(host='rabbitmq')
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
print('hello')
channel.queue_declare(queue='presentation_approvals')
channel.basic_consume(
    queue='presentation_approvals',
    on_message_callback=process_approval,
    auto_ack=True,
)
channel.queue_declare(queue='presentation_rejections')
channel.basic_consume(
    queue='presentation_rejections',
    on_message_callback=process_rejection,
    auto_ack=True,
)
channel.start_consuming()