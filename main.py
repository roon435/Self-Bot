import discord
from discord.ext import commands
from discord.utils import get

class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.command()
    async def tictactoe(self, ctx, opponent: discord.User):
        if ctx.author.id in self.games or opponent.id in self.games:
            await ctx.send("One of you is already in a game!")
            return

        self.games[ctx.author.id] = {
            'opponent': opponent,
            'board': [' ' for _ in range(9)],
            'current_player': ctx.author,
            'messages': []
        }

        await self.send_board(ctx)

    async def send_board(self, ctx):
        game = self.games[ctx.author.id]
        board = game['board']
        message = "\n".join([f"{board[i]} | {board[i+1]} | {board[i+2]}" for i in range(0, 9, 3)])
        embed = discord.Embed(title="Tic-Tac-Toe", description=message, color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        game['messages'].append(msg)

        for i in range(9):
            await msg.add_reaction(str(i+1))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        game = next((g for g in self.games.values() if user.id in [g['opponent'].id, g['current_player'].id]), None)
        if not game:
            return

        if reaction.message.id not in [m.id for m in game['messages']]:
            return

        index = int(reaction.emoji) - 1
        if game['board'][index] != ' ':
            await reaction.remove(user)
            return

        game['board'][index] = 'X' if game['current_player'] == user else 'O'
        game['current_player'] = game['opponent'] if game['current_player'] == user else game['current_player']

        await self.check_winner(game, reaction.message)

    async def check_winner(self, game, message):
        board = game['board']
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]             # Diagonals
        ]

        for combo in winning_combinations:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
                winner = game['current_player'] if game['current_player'] != game['opponent'] else game['opponent']
                await message.channel.send(f"Congratulations {winner.mention}, you won!")
                del self.games[game['current_player'].id]
                return

        if ' ' not in board:
            await message.channel.send("It's a tie!")
            del self.games[game['current_player'].id]
            return

        await self.send_board(message.channel)

def setup(bot):
    bot.add_cog(TicTacToe(bot))
