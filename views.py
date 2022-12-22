import discord
from discord.ui import View
import random

from mongodb_connection import db, user_collection

class GambleView(View):
    @discord.ui.select(
        options=[
            discord.SelectOption(label="Heads or Tails", value="0x1", description="Guess wrong, you lose. Guess right, Win 2x"),
            discord.SelectOption(label="1-10", value="0x2", description="Guess the number, Win 10x"),
        ],
    )

    async def select_callback(self, interaction, select: discord.ui.Select):
        print(f'inte: {interaction.user}')
        select.disabled = True
        if select.values[0] == "0x1":
            print("You chose Heads or Tails")
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f'You chose Heads or Tails', view=HotView())
        if select.values[0] == "0x2":
            print("You chose 1-10")
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f'You chose 1-10')

    

###########################

class HotView(View):
    @discord.ui.select(
        options=[
            discord.SelectOption(label="Heads", value="0", description="Heads"),
            discord.SelectOption(label="Tails", value="1", description="Tails"),
        ],
    )

    async def select_callback(self, interaction, select: discord.ui.Select):
        select.disabled = True
        documents = user_collection.find_one({'username': str(interaction.user)})
        hot_pick = random.randint(0, 1)
        print(f'documents {documents}')
        if select.values[0] == "0" and hot_pick == 0:
            print("You win 2x")
            new_points = (documents["points"] * 2)
            result = user_collection.update_one({'username': str(interaction.user)}, {"$set": {'points': new_points}})
            print(result)
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f'You won 2x. You now have {new_points} points.')
        elif select.values[0] == "0" and hot_pick == 1:
            print("You lost")
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f'You lost G. You now have {documents["points"]} points.')

        if select.values[0] == "1" and hot_pick == 1:
            print("You win 2x")
            new_points = (documents["points"] * 2)
            result = user_collection.update_one({'username': str(interaction.user)}, {"$set": {'points': new_points}})
            print(result)
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f'You won 2x. You now have {new_points} points.')
        elif select.values[0] == "1" and hot_pick == 0:
            print(f'You lost G')
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f'You lost G. You now have {documents["points"]} points.')


#############################################
