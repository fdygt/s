import discord
from discord.ext import commands
from discord.ui import View, Button
from bson import ObjectId
from database import Database
from config import load_config

# Inisialisasi intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Inisialisasi bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Membaca konfigurasi dari file config.txt
config = load_config('/storage/emulated/0/bot/MultipleFiles/config.txt')

# Inisialisasi database dengan konfigurasi
    db = Database(config['LINK_DATABASE'])

# World command
@bot.command(name='world')
async def world(ctx):
    admin_data = db.get_admin_data(ctx.author.id)
    if admin_data:
        world_name = admin_data.get('world_name')
        owner = admin_data.get('owner')
        bot_name = admin_data.get('bot_name')
        await ctx.send(f'World: {world_name}\nOwner: {owner}\nBot: {bot_name}')
    else:
        await ctx.send('Data world tidak ditemukan.')

# Stock command
@bot.command(name='stock')
async def stock(ctx):
    if ctx.author.guild_permissions.administrator:
        produk_data = db.get_all_products("products", ctx.guild.owner_id)
        user_balance = db.get_user_balance(ctx.author.id)
        embed = discord.Embed(title='Live Stock', description=f'Saldo Anda: :WL: {user_balance}')
        for produk in produk_data:
            embed.add_field(name=produk['nama'], value=f'Harga: {produk["harga"]}\nStock: {produk["stock"]}', inline=False)
        view = View()
        for produk in produk_data:
            button = Button(label=produk['nama'], style=discord.ButtonStyle.green)
            button.custom_id = f'beli_{produk["_id"]}'
            view.add_item(button)
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send('Anda tidak memiliki akses untuk menjalankan command ini!')

# Event on interaction
@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data.custom_id.startswith('beli_'):
            produk_id = interaction.data.custom_id.split('_')[1]
            produk_data = db.find_product("products", {"_id": ObjectId(produk_id), "admin_id": interaction.guild.owner_id})
            if produk_data is None:
                await interaction.response.send_message('Produk tidak ditemukan!', ephemeral=True)
                return
            produk_data = produk_data[0]
            harga = produk_data['harga']
            
            await interaction.response.send_message(f'Anda ingin membeli {produk_data["nama"]} dengan harga {harga} per unit. Berapa jumlah yang ingin Anda beli?', ephemeral=True)

            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel

            msg = await bot.wait_for('message', check=check)
            try:
                jumlah = int(msg.content)
                if jumlah <= 0:
                    raise ValueError("Jumlah harus lebih dari 0")
            except ValueError:
                await interaction.followup.send('Jumlah yang Anda masukkan tidak valid. Silakan coba lagi.', ephemeral=True)
                return

            total_harga = harga * jumlah
            user_balance = db.get_user_balance(interaction.user.id)
            if user_balance < total_harga:
                await interaction.followup.send('Saldo tidak cukup!', ephemeral=True)
                return
            
            if produk_data['stock'] < jumlah:
                await interaction.followup.send('Stok tidak mencukupi!', ephemeral=True)
                return

            db.update_user_balance(interaction.user.id, -total_harga)
            db.update_product_stock(produk_id, -jumlah)
            await interaction.followup.send(f'Anda telah membeli {jumlah} {produk_data["nama"]} dengan total harga {total_harga}!', ephemeral=True)

            # Kirimkan barang ke buyer
            buyer = interaction.user
            with open(f"results_{buyer.name}.txt", "w") as f:
                f.write(produk_data["deskripsi"])
            await buyer.send(file=discord.File(f"results_{buyer.name}.txt"))

            # Update stock embed
            produk_data = db.get_all_products("products", interaction.guild.owner_id)
            user_balance = db.get_user_balance(interaction.user.id)
            embed = discord.Embed(title='Live Stock', description=f'Saldo Anda: :WL: {user_balance}')
            for produk in produk_data:
                embed.add_field(name=produk['nama'], value=f'Harga: {produk["harga"]}\nStock: {produk["stock"]}', inline=False)
            view = View()
            for produk in produk_data:
                button = Button(label=produk['nama'], style=discord.ButtonStyle.green)
                button.custom_id = f'beli_{produk["_id"]}'
                view.add_item(button)
            channel_id = db.get_channel_id(interaction.guild.id)
            channel = bot.get_channel(channel_id)
            await channel.send(embed=embed, view=view)

async def update_live_stock():
    for guild in bot.guilds:
        # Logika untuk memperbarui stok secara live
        pass

# Menjalankan bot
bot.run(config['DISCORD_TOKEN'])