import discord
from discord.ext import commands
from discord.ui import View, Button
from bson import ObjectId
from database import Database

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database('/storage/emulated/0/bot/MultipleFiles/mydatabase.db')

    @commands.command(name='add_product')
    @commands.has_guild_permissions(administrator=True)
    async def add_product(self, ctx, nama: str, harga: int, stock: int, deskripsi: str):
        admin_data = self.db.get_admin_data(ctx.author.id)
        if not admin_data:
            await ctx.send("Anda tidak memiliki data admin.")
            return

        product_data = {
            'admin_id': admin_data['id'],
            'nama': nama,
            'harga': harga,
            'stock': stock,
            'deskripsi': deskripsi
        }
        self.db.insert('products', product_data)
        await ctx.send(f"Produk {nama} berhasil ditambahkan.")

    @commands.command(name='remove_product')
    @commands.has_guild_permissions(administrator=True)
    async def remove_product(self, ctx, product_id: int):
        admin_data = self.db.get_admin_data(ctx.author.id)
        if not admin_data:
            await ctx.send("Anda tidak memiliki data admin.")
            return

        self.db.delete('products', {'id': product_id, 'admin_id': admin_data['id']})
        await ctx.send(f"Produk dengan ID {product_id} berhasil dihapus.")

    @commands.command(name='update_product')
    @commands.has_guild_permissions(administrator=True)
    async def update_product(self, ctx, product_id: int, nama: str = None, harga: int = None, stock: int = None, deskripsi: str = None):
        admin_data = self.db.get_admin_data(ctx.author.id)
        if not admin_data:
            await ctx.send("Anda tidak memiliki data admin.")
            return

        update_data = {}
        if nama:
            update_data['nama'] = nama
        if harga:
            update_data['harga'] = harga
        if stock:
            update_data['stock'] = stock
        if deskripsi:
            update_data['deskripsi'] = deskripsi

        self.db.update('products', {'id': product_id, 'admin_id': admin_data['id']}, update_data)
        await ctx.send(f"Produk dengan ID {product_id} berhasil diperbarui.")

    @commands.command(name='list_products')
    @commands.has_guild_permissions(administrator=True)
    async def list_products(self, ctx):
        admin_data = self.db.get_admin_data(ctx.author.id)
        if not admin_data:
            await ctx.send("Anda tidak memiliki data admin.")
            return

        products = self.db.get_all_products('products', admin_data['id'])
        if not products:
            await ctx.send("Tidak ada produk yang ditemukan.")
            return

        embed = discord.Embed(title="Daftar Produk", description="Berikut adalah daftar produk Anda:")
        for product in products:
            embed.add_field(name=product[2], value=f"Harga: {product[3]}\nStock: {product[4]}\nDeskripsi: {product[5]}", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))