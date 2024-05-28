# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class GroupAccountTable(models.Model):
    group_account_id = models.AutoField(primary_key=True)
    item = models.CharField(max_length=200, blank=True, null=True)
    account_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    payment = models.IntegerField(blank=True, null=True)
    flag = models.IntegerField()
    group = models.ForeignKey('GroupTable', models.DO_NOTHING)
    category = models.ForeignKey('GroupCategoryTable', models.DO_NOTHING)
    payment_person = models.ForeignKey('PersonalTable', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'group_account_table'
        unique_together = (('group_account_id', 'group', 'category', 'payment_person'),)


class GroupCategoryTable(models.Model):
    group_category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=45, blank=True, null=True)
    category_description = models.CharField(max_length=200, blank=True, null=True)
    group = models.ForeignKey('GroupTable', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'group_category_table'
        unique_together = (('group_category_id', 'group'),)


class GroupTable(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=200)
    group_code = models.CharField(unique=True, max_length=200)

    class Meta:
        managed = False
        db_table = 'group_table'


class PersonalAccountTable(models.Model):
    personal_account_id = models.AutoField(primary_key=True)
    item = models.CharField(max_length=200, blank=True, null=True)
    account_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    payment = models.IntegerField(blank=True, null=True)
    flag = models.IntegerField()
    personal = models.ForeignKey('PersonalTable', models.DO_NOTHING)
    category = models.ForeignKey('PersonalCategoryTable', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'personal_account_table'
        unique_together = (('personal_account_id', 'personal', 'category'),)


class PersonalCategoryTable(models.Model):
    personal_category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=45)
    transaction_type = models.CharField(max_length=200, blank=True, null=True)
    category_description = models.CharField(max_length=200, blank=True, null=True)
    personal = models.ForeignKey('PersonalTable', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'personal_category_table'
        unique_together = (('personal_category_id', 'personal'),)


class PersonalGroupLinkingTable(models.Model):
    personal = models.OneToOneField('PersonalTable', models.DO_NOTHING, primary_key=True)
    group = models.ForeignKey(GroupTable, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'personal_group_linking_table'
        unique_together = (('personal', 'group'),)


class PersonalTable(models.Model):
    personal_id = models.CharField(primary_key=True, max_length=200)
    user_name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'personal_table'


class SplitTable(models.Model):
    split_id = models.AutoField(primary_key=True)
    payment = models.IntegerField(blank=True, null=True)
    advance_payment = models.IntegerField(blank=True, null=True)
    group_account = models.ForeignKey(GroupAccountTable, models.DO_NOTHING)
    spliter = models.ForeignKey(PersonalTable, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'split_table'
        unique_together = (('split_id', 'group_account', 'spliter'),)
