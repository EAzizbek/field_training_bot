import aiocron


@aiocron.crontab('* * * * *', tz='Asia/Tashkent')
async def test_cron():
    print("🕒 Cron ishladi")
