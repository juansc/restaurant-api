import datetime

from django.db import models

DEFAULT_MAX_CHAR_COLUMN_LENGTH = 255
# Decimal fields will represent decimal numbers having up to 6 digits (including those after the decimal)
DEFAULT_DECIMAL_PLACES = 2
DEFAULT_MAX_DIGITS = 6

SERVER_WORKING = 'working'
SERVER_ON_BREAK = 'on_break'
SERVER_NOT_WORKING = 'not_working'

SERVER_STATES = (
    SERVER_WORKING,
    SERVER_ON_BREAK,
    SERVER_NOT_WORKING,
)

TABLE_RESERVED = 'reserved'
TABLE_EMPTY = 'empty'
TABLE_DIRTY = 'dirty'
TABLE_PAID = 'paid'
TABLE_OCCUPIED = 'occupied'

TABLE_STATES = (
    TABLE_RESERVED,
    TABLE_EMPTY,
    TABLE_DIRTY,
    TABLE_PAID,
    TABLE_OCCUPIED,
)


class ServerManager(models.Manager):
    @staticmethod
    def assert_server_employed(server):
        assert server.employed, 'Could not complete operation: server is no longer employed.'

    def update_server(self, server_id, state):
        if state not in SERVER_STATES:
            raise ValueError('Encountered unsupported state: {}'.format(state))
        server = self.get(server_id=server_id)
        if state == SERVER_ON_BREAK:
            server.go_on_break()
        elif state == SERVER_WORKING:
            server.start_working()
        elif state == SERVER_WORKING:
            server.stop_working()

    def servers_working(self):
        return self.filter(state=SERVER_WORKING)

    def servers_on_break(self):
        return self.filter(state=SERVER_ON_BREAK)

    def servers_not_working(self):
        return self.filter(state=SERVER_NOT_WORKING)


# Create your models here.
class Server(models.Model):
    server_id = models.CharField(max_length=16)
    name = models.CharField(max_length=DEFAULT_MAX_CHAR_COLUMN_LENGTH, verbose_name='Server Name')
    state = models.CharField(max_length=11, default=SERVER_NOT_WORKING)
    employed = models.BooleanField(default=True)

    objects = ServerManager()

    def assert_currently_in_valid_state(self):
        assert self.state in SERVER_STATES, 'Encountered unknown server state: {}'.format(self.state)

    def go_on_break(self):
        """
        Change state of server so they go on break. A server can only go on break if they are currently working.
        """
        self.assert_currently_in_valid_state()
        assert self.state != SERVER_ON_BREAK, 'Server cannot go on break because they are already on break.'
        assert self.state != SERVER_NOT_WORKING, 'Server cannot go on break because they are not working.'
        self.state = SERVER_ON_BREAK
        self.save()

    def stop_working(self):
        """
        Change state of server so they not working anymore. A server can stop working as long as they are not already
        not working.
        """
        self.assert_currently_in_valid_state()
        assert self.state != SERVER_NOT_WORKING, 'Cannot stop working because server is already not working.'
        self.state = SERVER_NOT_WORKING
        self.save()

    def start_working(self):
        """
        Change state of server so they start working. A server can start working as long as they are not already
        working.
        """
        self.assert_currently_in_valid_state()
        assert self.state != SERVER_WORKING, 'Cannot start working because server is already working.'
        self.state = SERVER_WORKING
        self.save()


class Table(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='table_server')
    seats = models.PositiveSmallIntegerField()
    state = models.CharField(max_length=8, verbose_name='Table State')


class Seat(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='seat_table')
    number = models.PositiveSmallIntegerField()
    occupied = models.BooleanField(default=False)


class Bill(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bill_table')
    # by default a created bill is open since when you create a new bill it hasn't been paid for
    is_open = models.BooleanField(default=True)
    opened_on = models.DateTimeField(default=datetime.datetime.utcnow)
    last_server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='last_server')


class MenuItem(models.Model):
    name = models.CharField(max_length=DEFAULT_MAX_CHAR_COLUMN_LENGTH)
    # Price can only be negative if the menu item is a modification
    price = models.DecimalField(max_digits=DEFAULT_MAX_DIGITS, decimal_places=DEFAULT_DECIMAL_PLACES)
    added_on = models.DateTimeField(default=datetime.datetime.utcnow)
    serving = models.BooleanField(default=True)
    is_mod = models.BooleanField(default=False)


class OrderItem(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    state = models.CharField(max_length=DEFAULT_MAX_CHAR_COLUMN_LENGTH)


class ModItem(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)


class BillItem(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='bill_item_seat')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='order_item')
    price = models.DecimalField(max_digits=DEFAULT_MAX_DIGITS, decimal_places=DEFAULT_DECIMAL_PLACES)
    added_on = models.DateTimeField(default=datetime.datetime.utcnow)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
