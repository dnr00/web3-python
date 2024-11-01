class Watchlist:
    def __init__(self):
        self.watchlists = {}
    
    async def add_token(self, user_id: int, token: str):
        if user_id not in self.watchlists:
            self.watchlists[user_id] = []
        if token not in self.watchlists[user_id]:
            self.watchlists[user_id].append(token)
            return True
        return False
    
    async def remove_token(self, user_id: int, token: str):
        if user_id in self.watchlists and token in self.watchlists[user_id]:
            self.watchlists[user_id].remove(token)
            return True
        return False
    
    async def get_watchlist(self, user_id: int):
        return self.watchlists.get(user_id, [])

watchlist_manager = Watchlist()