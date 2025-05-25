import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, RoomUserSeqEvent

client = TikTokLiveClient(unique_id="@bead.diy4")


@client.on(ConnectEvent)


async def on_connect(event: ConnectEvent):
    client.logger.info(f"Connected to @{event.unique_id}!")


@client.on(RoomUserSeqEvent)
async def on_room_user_seq(event: RoomUserSeqEvent):
    """
    打印当前推测的“在线人数(total)”和“累计观看(total_user)”
    """
    data = event.__dict__
    
    # 从 data 里取出
    current_viewers = data.get("total")       # 可能是当前在线
    total_viewers   = data.get("total_user")  # 可能是总观看人次

    print(
        f"[RoomUserSeqEvent] "
        f"Current viewers: {current_viewers}, "
        f"Total viewers so far: {total_viewers}"
    )


async def check_loop():
    while True:
        if not await client.is_live():
            client.logger.info("Client is currently not live. Checking again in 60 seconds.")
            await asyncio.sleep(60)
        else:
            client.logger.info("Requested client is live! Trying to connect...")
            await client.connect()
        await asyncio.sleep(5)


async def main():
    client.logger.setLevel(LogLevel.INFO.value)
    await check_loop()

if __name__ == "__main__":
    asyncio.run(main())