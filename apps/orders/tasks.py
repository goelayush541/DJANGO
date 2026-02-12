from celery import shared_task
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_order_confirmation(order_id):
    logger.info(f"Processing order confirmation for Order ID: {order_id}")
    # Simulate work
    time.sleep(2)
    logger.info(f"Order confirmation sent for Order ID: {order_id}")
    return True
