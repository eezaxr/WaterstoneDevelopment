import aiohttp
import config


class BloxlinkHandler:
    """Handler for Bloxlink API requests"""
    
    BASE_URL = "https://api.blox.link/v4"
    
    def __init__(self):
        self.api_key = config.BLOXLINK_API_KEY
        self.headers = {
            "Authorization": self.api_key
        }
    
    async def get_roblox_user_info(self, roblox_id: str) -> dict:
        """Fetch Roblox user info directly from Roblox API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get username
                async with session.get(f"https://users.roblox.com/v1/users/{roblox_id}") as resp:
                    if resp.status == 200:
                        user_data = await resp.json()
                        
                        # Get group roles
                        async with session.get(f"https://groups.roblox.com/v1/users/{roblox_id}/groups/roles") as group_resp:
                            groups = []
                            if group_resp.status == 200:
                                group_data = await group_resp.json()
                                groups = group_data.get('data', [])
                            
                            return {
                                "name": user_data.get("name"),
                                "displayName": user_data.get("displayName"),
                                "groups": groups
                            }
        except Exception:
            pass
        return {}
    
    async def get_user(self, discord_id: str) -> dict:
        """
        Get Roblox user data linked to a Discord ID via Bloxlink
        
        Returns dict with keys:
        - robloxID: str
        - resolved: dict with user details
        - success: bool
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/public/guilds/{config.GUILD_ID}/discord-to-roblox/{discord_id}"
                
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        roblox_id = data.get("robloxID")
                        
                        # If resolved is empty, fetch from Roblox API directly
                        resolved = data.get("resolved", {})
                        if not resolved and roblox_id:
                            roblox_info = await self.get_roblox_user_info(roblox_id)
                            resolved = {"roblox": roblox_info}
                        
                        return {
                            "success": True,
                            "robloxID": roblox_id,
                            "resolved": resolved,
                            "raw_data": data
                        }
                    elif resp.status == 404:
                        return {
                            "success": False,
                            "error": "User not linked"
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API returned status {resp.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_roblox_username(self, discord_id: str) -> str:
        """Get Roblox username from Discord ID"""
        data = await self.get_user(discord_id)
        if data.get("success"):
            resolved = data.get("resolved", {})
            
            # Check resolved.roblox.name
            if "roblox" in resolved:
                name = resolved["roblox"].get("name")
                if name:
                    return name
            
            # Check direct robloxUsername field
            if "robloxUsername" in data.get("raw_data", {}):
                return data["raw_data"]["robloxUsername"]
        
        return "N/A"
    
    async def get_roblox_id(self, discord_id: str) -> str:
        """Get Roblox ID from Discord ID"""
        data = await self.get_user(discord_id)
        if data.get("success"):
            return data.get("robloxID")
        return None
    
    async def get_primary_group(self, discord_id: str) -> dict:
        """
        Get user's primary group information
        
        Returns dict with:
        - id: int
        - name: str
        - role: dict with rank info
        """
        data = await self.get_user(discord_id)
        if data.get("success"):
            resolved = data.get("resolved", {})
            
            # Try to find groups in the response
            groups = None
            if "roblox" in resolved and "groups" in resolved["roblox"]:
                groups = resolved["roblox"]["groups"]
            elif "groups" in resolved:
                groups = resolved["groups"]
            
            if groups:
                # Find the matching group
                for group_data in groups:
                    # Handle Roblox API format
                    group = group_data.get("group", group_data)
                    if str(group.get("id")) == str(config.ROBLOX_GROUP_ID):
                        # Return with role info
                        return {
                            "id": group.get("id"),
                            "name": group.get("name"),
                            "role": group_data.get("role", {})
                        }
        
        return None
    
    async def get_roblox_rank(self, discord_id: str) -> str:
        """Get user's rank name in the configured Roblox group"""
        group = await self.get_primary_group(discord_id)
        if group:
            role = group.get("role", {})
            if isinstance(role, dict):
                return role.get("name", "N/A")
            else:
                return str(role)
        
        return "N/A"
    
    async def update_user(self, discord_id: str) -> bool:
        """
        Trigger a Bloxlink update for a user
        Forces Bloxlink to refresh their data
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/public/guilds/{config.GUILD_ID}/update-user/{discord_id}"
                async with session.patch(url, headers=self.headers) as resp:
                    return resp.status == 200
        except Exception:
            return False


# Create a singleton instance
bloxlink = BloxlinkHandler()