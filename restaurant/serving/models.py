import datetime

from django.db import models


SERVER_STATES = (
    'working',
    'on_break',
    'not_working',
)

TABLE_STATES = (
    'reserved',
    'empty',
    'dirty',
    'paid',
    'occupied',
)


# Create your models here.
class Server(models.Model):
    name = models.CharField(max_length=255, verbose_name='Server Name')
    state = models.CharField(max_length=11)


class Table(models.Model):
    server = models.ForeignKey(Server, related_name='table_server')
    seats = models.PositiveSmallIntegerField()
    state = models.CharField(max_length=8, verbose_name='Table State')


class Seat(models.Model):
    table = models.ForeignKey(Table, related_name='seat_table')
    number = models.PositiveSmallIntegerField()
    occupied = models.BooleanField(default=False)


class Bill(models.Model):
    table = models.ForeignKey(Table, related_name='bill_table')
    # by default a created bill is open since when you create a new bill it hasn't been paid for
    is_open = models.BooleanField(default=True)
    opened_on = models.DateTimeField(default=datetime.datetime.utcnow())
    last_server = models.ForeignKey(Server, related_name='last_server')


class BillItem(models.Model):
    seat = models.ForeignKey(Seat, related_name='bill_item_seat')
    order_item = models.ForeignKey(OrderItem, related_name='order_item')
    price = models.DecimalField(decimal_places=2, related_name='bill_item_price')
    added_on = models.DateTimeField(default=datetime.datetime.utcnow())
    bill = models.ForeignKey(Bill)
    server = models.ForeignKey(Server)


class MenuItem(models.Model):
    name = models.CharField()
    # Price can only be negative if the menu item is a modification
    price = models.DecimalField(decimal_places=2)
    added_on = models.DateTimeField(default=datetime.datetime.utcnow())
    serving = models.BooleanField(default=True)
    is_mod = models.BooleanField(default=False)


class OrderItem(models.Model):
    menu_item = models.ForeignKey(MenuItem)
    state = models.CharField()


class ModItem(models.Model):
    menu_item = models.ForeignKey(MenuItem)
    order_item = models.ForeignKey(OrderItem)
