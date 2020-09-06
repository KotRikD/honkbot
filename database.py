import peewee, peewee_async
import time, datetime

from decimal import Decimal

db_host = "postgres"
db_port = 5432
db_username = "user"
db_password = "pass"
db_name = "db"
custom_driver = "PostgreSQL"

if custom_driver == "PostgreSQL":
    driver = peewee_async.PostgresqlDatabase
    if db_port is None: db_port = 5432

elif custom_driver == "MySQL":
    driver = peewee_async.MySQLDatabase
    if db_port is None: db_port = 3306

database = driver(db_name, user=db_username, password=db_password, host=db_host, port=db_port)

manager = peewee_async.Manager(database)

async def get_or_none(model, *args, **kwargs):
    try:
        return await manager.get(model, *args, **kwargs)

    except peewee.DoesNotExist:
        return None

class BaseModel(peewee.Model):
    class Meta:
        database = manager.database

class Role(BaseModel):
    user_id = peewee.BigIntegerField()
    role = peewee.TextField()

    reason = peewee.TextField(default=None)

class Priviliges(BaseModel):
    user_id = peewee.BigIntegerField()
    priv = peewee.IntegerField()

    last_update_reason = peewee.TextField(default=None)

class Bank(BaseModel):
    user_id = peewee.BigIntegerField(unique=True)
    balance = peewee.BigIntegerField(default=500)

class PxUser(BaseModel):
    iduser = peewee.CharField()
    messcount = peewee.IntegerField(default=1)
    xpcount = peewee.IntegerField(default=0)
    rank = peewee.IntegerField(default=0)
    personal = peewee.CharField(default="")

class Donate(BaseModel):
    user_id = peewee.BigIntegerField(unique=True)
    amout = peewee.IntegerField(default=0)
    last_trans_id = peewee.BigIntegerField(default=0)

class shopcenter(BaseModel):
    name = peewee.TextField()
    slot = peewee.TextField()
    price = peewee.BigIntegerField()
    moneymin = peewee.IntegerField(default=0)

class MoneySendLimit(BaseModel):
    user_id = peewee.BigIntegerField(default=0)
    pay_amount = peewee.IntegerField(default=0)
    gived_money = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
    pay = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))

class jobs(BaseModel):
    name = peewee.TextField()
    need_days = peewee.IntegerField()
    pay = peewee.IntegerField(default=0)
    type_name = peewee.TextField()

class business(BaseModel):
    level = peewee.IntegerField()
    level1_name = peewee.TextField()
    level2_name = peewee.TextField()
    level3_name = peewee.TextField()
    up_price = peewee.BigIntegerField()
    price = peewee.BigIntegerField()
    smile = peewee.TextField()
    max_works = peewee.IntegerField()
    pay = peewee.IntegerField()

class clan_members(BaseModel):
    user_id = peewee.BigIntegerField(default=0)
    is_accepted = peewee.IntegerField(default=1)
    join_date = peewee.TextField(default=datetime.date.today())
    rank = peewee.IntegerField(default=1)
    clan_tag = peewee.TextField(default="")

class clan_invites(BaseModel):
    whom_id = peewee.BigIntegerField(default=0)
    clan_tag = peewee.TextField(default=0)

class clans(BaseModel):
    header_id = peewee.BigIntegerField(default=0)
    register_date = peewee.TextField(default=datetime.date.today())
    name = peewee.TextField(default="")
    shortname = peewee.TextField(default="")
    treasury = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
    clan_type = peewee.IntegerField(default=0)
    raiting = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
    tag = peewee.TextField(default="")

class Profile(peewee.Model):
  user_id = peewee.BigIntegerField(default=0)
  clan = peewee.IntegerField(default=None, null=True)
  last_payout = peewee.DateTimeField(default=datetime.datetime.now() - datetime.timedelta(days=1))
  last_btc_payout = peewee.DateTimeField(default=datetime.datetime.now())
  minercheck = peewee.IntegerField(default=0)
  last_bank_payout = peewee.DateTimeField(default=datetime.datetime.now())
  last_job_end = peewee.DateTimeField(default=datetime.datetime.now())
  last_bonus = peewee.DateTimeField(default=datetime.datetime.now())
  last_pay_send = peewee.DateTimeField(default=datetime.datetime.now())
  bankmoney = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  datareg = peewee.TextField(default=datetime.date.today())
  money = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("5000"))
  rg = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  house = peewee.ForeignKeyField(shopcenter, on_delete='SET NULL', null=True, related_name="housed")
  car = peewee.ForeignKeyField(shopcenter, on_delete='SET NULL', null=True, related_name="cared")
  airplane = peewee.ForeignKeyField(shopcenter, on_delete='SET NULL', null=True, related_name="airplaned")
  yacht = peewee.ForeignKeyField(shopcenter, on_delete='SET NULL', null=True, related_name="yachted")
  btc = peewee.BigIntegerField(default=0)
  energy_days = peewee.IntegerField(default=10)
  last_energy_end = peewee.DateTimeField(default=datetime.datetime.now())
  energy_worked = peewee.BigIntegerField(default=0)
  iron = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  gold = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  diamond = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  btc_amount = peewee.BigIntegerField(default=0)
  business1 = peewee.ForeignKeyField(business, on_delete='SET NULL', null=True, related_name="businessed")
  business2 = peewee.ForeignKeyField(business, on_delete='SET NULL', null=True, related_name="businessed2")
  business1_money = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  business2_money = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  business1_level = peewee.IntegerField(default=1)
  business2_level = peewee.IntegerField(default=1)
  last_bus1_pay = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  last_bus2_pay = peewee.DecimalField(max_digits=65, decimal_places=2, default=Decimal("0"))
  business1_works = peewee.IntegerField(default=1)
  business2_works = peewee.IntegerField(default=1)
  business1_run = peewee.DateTimeField(default=datetime.datetime.now())
  business2_run = peewee.DateTimeField(default=datetime.datetime.now())
  helicopter = peewee.ForeignKeyField(shopcenter, on_delete='SET NULL', null=True, related_name="helicoptered")
  apartment = peewee.ForeignKeyField(shopcenter, on_delete='SET NULL', null=True, related_name="apartmented")
  mobile = peewee.ForeignKeyField(shopcenter, on_delete='SET NULL', null=True, related_name="mobiled")
  other = peewee.ForeignKeyField(shopcenter, on_delete='SET NULL', null=True, related_name="othered")
  job = peewee.ForeignKeyField(jobs, on_delete='SET NULL', null=True, related_name="jobed")
  job_days = peewee.IntegerField(default=3)
  job_worked = peewee.IntegerField(default=0)
  reg = peewee.IntegerField(default=0)
  class Meta:
        database = database
        indexes = (
            (('user_id',), True),
        )

class Log(BaseModel):
    type = peewee.CharField()
    from_id = peewee.BigIntegerField(default=0)
    to_id = peewee.BigIntegerField(default=0)
    time = peewee.BigIntegerField(default=int(time.time()))
    body = peewee.CharField(default="")

class nicknames(BaseModel):
    user_id = peewee.BigIntegerField(default=0)
    is_accepted = peewee.IntegerField(default=0)
    nickname = peewee.TextField(default="")

class Mutes(BaseModel):
    user_id = peewee.BigIntegerField()
    time_to = peewee.BigIntegerField()

    reason = peewee.TextField(default=None)

    class Meta:
        database = manager.database

class Relations(BaseModel):
    user1 = peewee.BigIntegerField()
    user2 = peewee.BigIntegerField()
    datetime = peewee.IntegerField()

class DonateQiwi(BaseModel):
    txnId = peewee.BigIntegerField()

class DynamicSettings(BaseModel):
    key = peewee.CharField()
    value = peewee.CharField()

class OsuProfile(BaseModel):
    vk_id = peewee.BigIntegerField()
    
    osu_name = peewee.CharField(null=True, default=None)
    osu_mode = peewee.CharField(null=True, default=None)

    kurikku_name = peewee.CharField(null=True, default=None)
    kurikku_mode = peewee.CharField(null=True, default=None)

    gatari_name = peewee.CharField(null=True, default=None)
    gatari_mode = peewee.CharField(null=True, default=None)

    akatsuki_name = peewee.CharField(null=True, default=None)
    akatsuki_mode = peewee.CharField(null=True, default=None)

    ripple_name = peewee.CharField(null=True, default=None)
    ripple_mode = peewee.CharField(null=True, default=None)

class OsuStats(BaseModel):
    nickname = peewee.CharField()
    server = peewee.CharField()
    mode = peewee.CharField()
    stat = peewee.CharField(default="[0,0,0,0,0,0,0,0,0,0,0]")

with manager.allow_sync():
    Bank.create_table(True)
    PxUser.create_table(True)
    business.create_table(True)
    jobs.create_table(True)
    Donate.create_table(True)
    shopcenter.create_table(True)
    clans.create_table(True)
    clan_invites.create_table(True)
    clan_members.create_table(True)
    Profile.create_table(True)
    Mutes.create_table(True)
    Relations.create_table(True)
    DonateQiwi.create_table(True)
    Priviliges.create_table(True)
    Log.create_table(True)
    DynamicSettings.create_table(True)
    OsuProfile.create_table(True)
    OsuStats.create_table(True)

class SmallProfile(peewee.Model):
    user_id = peewee.BigIntegerField()
    bankmoney = peewee.BigIntegerField(default=0)
    money = peewee.DecimalField(max_digits=64, decimal_places=2, default=Decimal("5000"))

    class Meta:
        database = manager.database
        db_table = 'profile'
