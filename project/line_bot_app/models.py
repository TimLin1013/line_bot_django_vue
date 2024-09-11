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
    account_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    payment = models.IntegerField(blank=True, null=True)
    info_complete_flag = models.IntegerField()
    group = models.ForeignKey('GroupTable', on_delete=models.CASCADE)
    category = models.ForeignKey('GroupCategoryTable', on_delete=models.CASCADE)
    personal = models.ForeignKey('PersonalTable', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'group_account_table'
        unique_together = (('group_account_id', 'group', 'category', 'personal'),)


class GroupCategoryTable(models.Model):
    group_category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=45, blank=True, null=True)
    category_description = models.CharField(max_length=200, blank=True, null=True)
    group = models.ForeignKey('GroupTable', on_delete=models.CASCADE)

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
    account_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    payment = models.IntegerField(blank=True, null=True)
    info_complete_flag = models.IntegerField()
    personal = models.ForeignKey('PersonalTable', on_delete=models.CASCADE)
    category = models.ForeignKey('PersonalCategoryTable', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'personal_account_table'
        unique_together = (('personal_account_id', 'personal', 'category'),)
        ordering = ['account_date']


class PersonalCategoryTable(models.Model):
    personal_category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=45)
    transaction_type = models.CharField(max_length=200, blank=True, null=True)
    category_description = models.CharField(max_length=200, blank=True, null=True)
    personal = models.ForeignKey('PersonalTable', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'personal_category_table'
        unique_together = (('personal_category_id', 'personal'),)


class PersonalGroupLinkingTable(models.Model):
    personal = models.ForeignKey('PersonalTable', on_delete=models.CASCADE)
    group = models.ForeignKey(GroupTable, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'personal_group_linking_table'
        unique_together = (('id', 'personal', 'group'),)


class PersonalTable(models.Model):
    personal_id = models.CharField(primary_key=True, max_length=200)
    user_name = models.CharField(max_length=200)
    line_id = models.CharField(unique=True, max_length=45)
    input_status = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'personal_table'


class ReturnTable(models.Model):
    return_id = models.AutoField(primary_key=True)
    return_payment = models.CharField(max_length=45)
    payer = models.CharField(max_length=45)
    receiver = models.CharField(max_length=45)
    return_flag = models.CharField(max_length=1)
    split = models.ForeignKey('SplitTable', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'return_table'
        unique_together = (('return_id', 'split'),)


class SplitTable(models.Model):
    split_id = models.AutoField(primary_key=True)
    payment = models.IntegerField(blank=True, null=True)
    advance_payment = models.IntegerField(blank=True, null=True)
    group_account = models.ForeignKey(GroupAccountTable, on_delete=models.CASCADE)
    personal = models.ForeignKey(PersonalTable, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'split_table'
        unique_together = (('split_id', 'group_account', 'personal'),)
