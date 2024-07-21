import pytz

# 獲取並列印所有可用的時區
timezones = pytz.all_timezones
for timezone in timezones:
    print(timezone)

