import motor.motor_asyncio
from config import DB_URL, DB_NAME

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.user  # Collection for users
        self.channels = self.db.channels  # Collection for channels

    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.users.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.users.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.users.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.users.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.users.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, id, file_id):
        await self.users.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.users.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.users.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.users.find_one({'_id': int(id)})
        return user.get('caption', None)

    # Store the broadcast message ID
    async def add_broadcast_message(self, user_id, message_id):
        await self.users.update_one(
            {"_id": user_id}, {"$set": {"last_broadcast_msg": message_id}}, upsert=True
        )

    # Retrieve the last broadcast message ID
    async def get_broadcast_message(self, user_id):
        user = await self.users.find_one({"_id": user_id})
        return user.get("last_broadcast_msg") if user else None

    # Delete the stored broadcast message ID
    async def delete_broadcast_message(self, user_id):
        await self.users.update_one({"_id": user_id}, {"$unset": {"last_broadcast_msg": ""}})

    # =================== CHANNEL SYSTEM ===================

    # Add a channel to the database
    async def add_channel(self, channel_id):
        if not await self.channels.find_one({"_id": channel_id}):
            await self.channels.insert_one({"_id": channel_id})
            return True  # New channel added
        return False  # Channel already exists

    # Remove a channel from the database
    async def remove_channel(self, channel_id):
        await self.channels.delete_one({"_id": channel_id})

    # Check if a channel exists
    async def is_channel_exist(self, channel_id):
        channel = await self.channels.find_one({"_id": channel_id})
        return bool(channel)

    # Get all stored channels
    async def get_all_channels(self):
        channels_cursor = self.channels.find({})
        return [channel["_id"] async for channel in channels_cursor]


# Initialize Database
db = Database(DB_URL, DB_NAME)
