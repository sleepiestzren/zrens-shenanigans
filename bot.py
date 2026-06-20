import discord
from discord.ext import commands
import aiohttp
import io
import json
import os
import time

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # REQUIRED for join detection

bot = commands.Bot(command_prefix=",", intents=intents)

CONFIG_FILE = "config.json"
AFK_FILE = "afk.json"

jSON.

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

config = load_json(CONFIG_FILE)
afk_users = load_json(AFK_FILE)

mod check.

def is_mod(ctx):
    guild_id = str(ctx.guild.id)
    mod_role_id = config.get(guild_id, {}).get("mod_role")

    has_perm = ctx.author.guild_permissions.manage_messages

    has_role = False
    if mod_role_id:
        role = ctx.guild.get_role(mod_role_id)
        if role in ctx.author.roles:
            has_role = True

    return has_perm or has_role

time.

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)

    if hours:
        return f"{hours}h {mins}m"
    elif mins:
        return f"{mins}m {secs}s"
    else:
        return f"{secs}s"

config.

@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    config.setdefault(guild_id, {})["log_channel"] = channel.id
    save_json(CONFIG_FILE, config)
    await ctx.send(f"✅ Log channel set to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setmodrole(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)
    config.setdefault(guild_id, {})["mod_role"] = role.id
    save_json(CONFIG_FILE, config)
    await ctx.send(f"✅ Mod role set to {role.name}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setminage(ctx, days: int):
    guild_id = str(ctx.guild.id)
    config.setdefault(guild_id, {})["min_account_age"] = days
    save_json(CONFIG_FILE, config)
    await ctx.send(f"✅ Minimum account age set to {days} days")

copy emojis and stickers.

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def copy(ctx):
    if not is_mod(ctx):
        await ctx.send("❌ You need to be a mod.")
        return

    if not ctx.message.reference:
        await ctx.send("Reply to a message with a sticker.")
        return

    ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)

    if not ref.stickers:
        await ctx.send("No stickers found.")
        return

    success = failed = skipped = 0

    guild_id = str(ctx.guild.id)
    log_channel = bot.get_channel(config.get(guild_id, {}).get("log_channel", 0))
    existing = [s.name for s in ctx.guild.stickers]

    for sticker in ref.stickers:
        if sticker.name in existing:
            skipped += 1
            continue

        async with aiohttp.ClientSession() as session:
            async with session.get(sticker.url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    file = discord.File(io.BytesIO(data), filename=f"{sticker.name}.png")

                    try:
                        await ctx.guild.create_sticker(
                            name=sticker.name,
                            description="Copied sticker",
                            emoji="😀",
                            file=file
                        )
                        success += 1

                        if log_channel:
                            embed = discord.Embed(title="Sticker Copied", color=discord.Color.green())
                            embed.add_field(name="User", value=ctx.author.mention)
                            embed.add_field(name="Sticker", value=sticker.name)
                            embed.set_thumbnail(url=sticker.url)
                            await log_channel.send(embed=embed)

                    except:
                        failed += 1
                else:
                    failed += 1

    await ctx.send(f"✅ Done!\n✔ {success} | ❌ {failed} | ⏭ {skipped}")

clear.

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def clear(ctx, amount: int = 5):
    if not is_mod(ctx):
        await ctx.send("❌ You need to be a mod.")
        return

    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Cleared {amount}")
    await msg.delete(delay=3)

afk.

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def afk(ctx, *, reason="AFK"):
    afk_users[str(ctx.author.id)] = {
        "reason": reason,
        "time": time.time()
    }
    save_json(AFK_FILE, afk_users)
    await ctx.send(f"🌙 {ctx.author.mention} is now AFK: {reason}")

events.

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)

    # Remove AFK
    if user_id in afk_users:
        data = afk_users.pop(user_id)
        save_json(AFK_FILE, afk_users)

        duration = format_time(time.time() - data["time"])
        await message.channel.send(
            f"👋 Welcome back {message.author.mention}, you were AFK for {duration}"
        )

    # Mention AFK users
    for user in message.mentions:
        uid = str(user.id)
        if uid in afk_users:
            data = afk_users[uid]
            duration = format_time(time.time() - data["time"])

            await message.channel.send(
                f"💤 {user.name} is AFK ({duration}): {data['reason']}"
            )

    await bot.process_commands(message)

new account.

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)

    min_days = config.get(guild_id, {}).get("min_account_age")
    if not min_days:
        return

    account_age = (discord.utils.utcnow() - member.created_at).days

    if account_age < min_days:
        try:
            await member.kick(reason=f"Account too new ({account_age}d < {min_days}d)")

            log_channel = member.guild.get_channel(
                config.get(guild_id, {}).get("log_channel", 0)
            )

            if log_channel:
                embed = discord.Embed(
                    title="🚨 Auto Kick: New Account",
                    color=discord.Color.red()
                )
                embed.add_field(name="User", value=member.mention)
                embed.add_field(name="Account Age", value=f"{account_age} days")
                embed.add_field(name="Required", value=f"{min_days} days")

                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Kick failed: {e}")

cooldown stuff.

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Try again in {round(error.retry_after, 1)}s")

run.

bot.run("put token here")
