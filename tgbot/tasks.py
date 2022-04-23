"""
    Celery tasks. Some of them will be launched periodically from admin panel via django-celery-beat
"""

import time
from typing import Union, List, Optional, Dict

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.models import P2p, Order, Suggestion

from dtb.celery import app
from celery.utils.log import get_task_logger
from tgbot.handlers.broadcast_message.utils import _send_message, _from_celery_entities_to_entities, \
    _from_celery_markup_to_markup

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def broadcast_message(
    user_ids: List[Union[str, int]],
    text: str,
    entities: Optional[List[Dict]] = None,
    reply_markup: Optional[List[List[Dict]]] = None,
    sleep_between: float = 0.4,
    parse_mode=telegram.ParseMode.HTML,
) -> None:
    """ It's used to broadcast message to big amount of users """
    logger.info(f"Going to send message: '{text}' to {len(user_ids)} users")

    entities_ = _from_celery_entities_to_entities(entities)
    reply_markup_ = _from_celery_markup_to_markup(reply_markup)
    for user_id in user_ids:
        try:
            _send_message(
                user_id=user_id,
                text=text,
                entities=entities_,
                parse_mode=parse_mode,
                reply_markup=reply_markup_,
            )
            logger.info(f"Broadcast message was sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}")
        time.sleep(max(sleep_between, 0.1))

    logger.info("Broadcast finished!")

    
@app.task(ignore_result=True)
def save_data_from_p2p() -> None:
    """ Получаем курсы с p2p Binance. Первая страница последние 5 записей """
    logger.info("Starting to get p2p courses")
    
    P2p.from_json(
        p2p_rub_usdt_json = P2p.get_course(pay_types = '["Tinkoff"]', trade_type = '"BUY"', fiat = '"RUB"'),
        p2p_usdt_lkr_json = P2p.get_course(pay_types = '["BANK"]', trade_type = '"SELL"', fiat = '"LKR"'),
        p2p_uah_usdt_json = P2p.get_course(pay_types = '["PrivatBank"]', trade_type = '"BUY"', fiat = '"UAH"'),
        p2p_eur_usdt_json = P2p.get_course(pay_types = '["Revolut"]', trade_type = '"BUY"', fiat = '"EUR"'),
        p2p_usd_usdt_json = P2p.get_course(pay_types = '["Tinkoff"]', trade_type = '"BUY"', fiat = '"USD"')
        )
    
    logger.info("Get p2p courses are completed!")
    
@app.task(ignore_result=True)
def change_order_status_and_mailing_suggestions(
    sleep_between: float = 0.4,
    parse_mode=telegram.ParseMode.HTML
) -> None:
    """ Меняем статус у заказов и рассылаем предложение обменников """
    logger.info("Starting checking orders")
    
    orders = Order.objects.filter(status__in=['active', 'mailing'], timestamp_execut__lte=time.time())
    for o in orders:
        if o.status == 'active':
            try:
                _send_message(
                    user_id=o.client_id.user_id,
                    text='<b>ЗАКАЗ ОТМЕНЕН!!!\n\nНА ТВОЙ ЗАКАЗ НЕБЫЛО ПРЕДЛОЖЕНИЙ, ПОПРОБУЙ ВЫБРАТЬ ГОРОД ГДЕ БОЛЬШЕ ОБМЕННИКОВ В ДАННЫЙ МОМЕНТ.</b>',
                    entities=None,
                    parse_mode=parse_mode,
                    reply_markup=_from_celery_markup_to_markup([
                        [dict(text='💸 Новый заказ', callback_data='Клиент'), dict(text='📝 Мои заказы', callback_data='Заказы_Клиент')],
                        [dict(text='⏪ Назад', callback_data='Меню')]
                    ]),
                )
                logger.info(f"Broadcast message was sent to {o.client_id}")
                o.status = 'canceled'
                o.save()
            except Exception as e:
                logger.error(f"Failed to send message to {o.client_id}, reason: {e}")
            time.sleep(max(sleep_between, 0.1))
        if o.status == 'mailing':
            suggestion = Suggestion.objects.filter(order_id=o.id)
            for s in suggestion:
                try:
                    _send_message(
                        user_id=o.client_id.user_id,
                        text='<b>Успешно выполнено \\ всего заявок: <code>{} \\ {}   {}%</code>\nПредлагаемая сумма {}</b>'.format(s.merchant_executor_id.count_merchant_order_success, s.merchant_executor_id.count_merchant_order, round(s.merchant_executor_id.count_merchant_order_success / s.merchant_executor_id.count_merchant_order * 100, 2), s.summ),
                        entities=None,
                        parse_mode=parse_mode,
                        reply_markup=_from_celery_markup_to_markup([
                            [dict(text='✅ Выбираю это предложение', callback_data='Выбираю_предложение '+str(o.id)+'_'+str(s.merchant_executor_id.user_id))]
                        ]),
                    )
                    logger.info(f"Broadcast message was sent to {o.client_id}")
                    o.status = 'waiting_client'
                    o.save()
                except Exception as e:
                    logger.error(f"Failed to send message to {o.client_id}, reason: {e}")
                time.sleep(max(sleep_between, 0.1))
        
    
    logger.info("Checking orders completed!")